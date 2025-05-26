from langchain_community.document_loaders import UnstructuredPDFLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_upstage import UpstageEmbeddings
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from app.services.chat_service import llm
from dotenv import load_dotenv
import os
from app.services.user_service import fetch_user_info

load_dotenv()

query_embedding = UpstageEmbeddings(model="solar-embedding-1-large-query")
passage_embedding = UpstageEmbeddings(model="solar-embedding-1-large-passage")

#pdf용 임베딩 함수
def initialize_chroma_from_file(pdf_path: str):
    #이미 존재하는 문서일 경우
    persist_dir = f"./chroma_db/{os.path.splitext(os.path.basename(pdf_path))[0]}"
    if os.path.exists(os.path.join(persist_dir, "index")):
        return
    
    loader = UnstructuredPDFLoader(pdf_path)
    docs = loader.load()

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)

    db = Chroma.from_documents(split_docs, passage_embedding, persist_directory=persist_dir)
    db.persist()
    
#markdown용 임베딩 함수
def initialize_chroma_from_markdown(md_path: str):
    persist_dir = f"./chroma_db/{os.path.splitext(os.path.basename(md_path))[0]}"
    if os.path.exists(os.path.join(persist_dir, "index")):
        return

    loader = TextLoader(md_path, encoding='utf-8')
    docs = loader.load()

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)

    db = Chroma.from_documents(split_docs, passage_embedding, persist_directory=persist_dir)
    db.persist()
    
def get_retriever():
    persist_dir = "./chroma_db"
    db = Chroma(persist_directory=persist_dir, embedding_function=query_embedding)
    return db.as_retriever()

#개인화 프롬포트
def build_user_prompt(user_info: dict) -> str:
    allergies = [item["allergyDrug"] for item in user_info.get("allergyDrugList", [])]
    diseases = user_info.get("diseaseList", [])

    prompt = f"""
당신은 헬스 케어 상담 전문가입니다. 아래는 사용자의 건강 정보입니다. 이 정보를 기반으로 문서를 검색하고 가장 알맞은 조언을 제공하세요.

- 성별: {user_info['userSex']}
- 키/몸무게: {user_info['height']}cm / {user_info['weight']}kg
- 흡연 여부: {user_info['userSmoke']}
- 음주 빈도: {user_info['userDrink']}
- 질병 이력: {', '.join(diseases) if diseases else '없음'}
- 알레르기 약물: {', '.join(allergies) if allergies else '없음'}

이 정보를 고려하여 사용자의 건강 상태에 맞는 문서 기반 맞춤 응답을 생성하세요.
"""
    return prompt.strip()

def generate_rag_response(question: str, token: str) -> str:
    user_info = fetch_user_info(token)
    user_prompt = build_user_prompt(user_info)
    retriever = get_retriever()

    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template=f"""{user_prompt}

다음은 관련 문서입니다:
{{context}}

질문: {{question}}
답변:"""
    )

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt_template}
    )

    response = qa.invoke({"query": question})
    return {"result": response["result"]}