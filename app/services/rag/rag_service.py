from langchain_community.document_loaders import  TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_upstage import UpstageEmbeddings
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA, create_retrieval_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from app.history.chat_history import get_chat_history
from app.services.chat_service import llm
from dotenv import load_dotenv
import os
from app.services.user_service import fetch_user_info, fetch_user_id

load_dotenv()

query_embedding = UpstageEmbeddings(model="solar-embedding-1-large-query")
passage_embedding = UpstageEmbeddings(model="solar-embedding-1-large-passage")

system_message = """
당신은 헬스케어 상담 전문가입니다.
- 답변은 최대 600자 내외로 간결하게 작성하세요.
- 사용자 정보는 주요한 핵심 키워드만 언급합니다.
- 마크다운 헤더(예: ###)는 사용하지 않습니다. **(굵은 글씨)는 사용해도 좋습니다.
- 리스트 앞에는 ‘-’ 또는 ‘1.’ 등을 쓰고, 각 항목 끝에 스페이스 두 칸를 추가한 뒤 엔터로 줄바꿈하세요.  
- 단락 구분이 필요할 땐 빈 줄(엔터 두 번)로 구분하세요.
""".strip()

# 문서 활용 가이드
doc_guide = """
관련 문서에서 필요한 정보만 뽑아 답변에 참고하세요.
""".strip()

# 공통 PromptTemplate 정의 (유저 프롬프트 포함)
tuned_template = PromptTemplate(
    input_variables=["user_prompt", "context", "question"],
    template=f"""{system_message}

<USER PROFILE>
{{user_prompt}}

이전 대화:
{{chat_history}}

<DOC GUIDE>
{doc_guide}

<RELEVANT DOCUMENTS>
{{context}}

<INPUT>
{{input}}
"""
)

#markdown용 임베딩 함수
def initialize_chroma_from_markdown(md_path: str):
    persist_dir = "./chroma_db"
    if os.path.exists(os.path.join(persist_dir, "index")):
        return

    loader = TextLoader(md_path, encoding='utf-8')
    docs = loader.load()

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)

    db = Chroma.from_documents(split_docs, passage_embedding, persist_directory=persist_dir)
    
def get_retriever(k: int = 6):
    persist_dir = "./chroma_db/2025_merged"
    db = Chroma(persist_directory=persist_dir, embedding_function=query_embedding)
    return db.as_retriever(
        search_type="mmr", 
        search_kwargs={"k": k}
    )

#개인화 프롬포트
def build_user_prompt(user_info: dict) -> str:
    disease_names    = [ d["disease"]   for d in user_info.get("diseaseList", []) ]
    allergy_drugs    = [ a["allergyDrug"] for a in user_info.get("allergyDrugList", []) ]
    allergy_etc      = [ e["allergyEtc"]  for e in user_info.get("allergyEtcList", []) ]
    
    disease_str      = ", ".join(disease_names)    if disease_names    else "없음"
    allergy_drug_str = ", ".join(allergy_drugs)    if allergy_drugs    else "없음"
    allergy_etc_str  = ", ".join(allergy_etc)      if allergy_etc      else "없음"
    prompt = f"""
당신은 헬스 케어 상담 전문가입니다. 아래는 사용자의 건강 정보입니다. 

- 성별: {user_info['userSex']}
- 키/몸무게: {user_info['height']}cm / {user_info['weight']}kg
- 흡연 여부: {user_info['userSmoke']}
- 음주 빈도: {user_info['userDrink']}
- 질병 이력: {disease_str}
- 알레르기 약물: {allergy_drug_str}
- 알레르기 기타: {allergy_etc_str}

이 정보를 고려하여 사용자의 건강 상태에 맞는 문서 기반 맞춤 응답을 생성하세요.
"""
    return prompt.strip()

def generate_rag_response(question: str, token: str) -> dict:
    user_info = fetch_user_info(token)
    user_prompt = build_user_prompt(user_info)
    retriever = get_retriever()

    prompt_template = tuned_template

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt_template}
    )

    response = qa.invoke({"query": question})
    response = qa.invoke({
        "query": question,
        "user_prompt": user_prompt,
    })
    return {"result": response["result"]}


async def stream_rag_response(question: str, token: str):
    user_info = fetch_user_info(token)
    user_id = fetch_user_id(token)
    user_prompt = build_user_prompt(user_info)

    prompt_template = PromptTemplate(
        input_variables=["user_prompt", "context", "input",  "chat_history"],
        template=tuned_template.template
    )

    rag_chain = prompt_template | llm

    qa_chain = create_retrieval_chain(
        retriever=get_retriever(),
        combine_docs_chain=rag_chain
    )
    
    from langchain_core.runnables.history import RunnableWithMessageHistory

    chat_chain = RunnableWithMessageHistory(
        qa_chain,
        get_session_history=lambda session_id: get_chat_history(session_id),
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer"
    )

    async for chunk in chat_chain.astream(
        {
            "input": question,
            "user_prompt": user_prompt,
            },
        config={"configurable": {"session_id": str(user_id)}}
    ):
        
        if isinstance(chunk, dict) and "answer" in chunk:
            content = chunk["answer"].content
            yield f"data: {content}\n\n"