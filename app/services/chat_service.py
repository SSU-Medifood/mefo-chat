from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# LangChain LLM setting
llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com", 
    model="deepseek-chat",
    temperature=0.7 #답변 창의성/ 1에 가까울수록 창의적
)

def generate_response(question: str) -> str:
    response = llm.invoke(question)
    return response