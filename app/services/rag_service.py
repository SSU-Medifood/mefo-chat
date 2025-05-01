from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_upstage import UpstageEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from app.services.chat_service import llm
import os
from dotenv import load_dotenv

load_dotenv()

query_embedding = UpstageEmbeddings(model="solar-embedding-1-large-query")
passage_embedding = UpstageEmbeddings(model="solar-embedding-1-large-passage")

def initialize_chroma_from_file(pdf_path: str):
    if os.path.exists("./chroma_db/index"):
        #이미 존재하는 문서일 경우
        return
    
    loader = UnstructuredPDFLoader(pdf_path)
    docs = loader.load()

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)

    db = Chroma.from_documents(split_docs, passage_embedding, persist_directory="./chroma_db")
    db.persist()
    
def generate_rag_response(question: str) -> str:
    db = Chroma(persist_directory="./chroma_db", embedding_function=query_embedding)
    retriever = db.as_retriever()

    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff"
    )

    return rag_chain.run(question)