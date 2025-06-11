from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat, recommend

app = FastAPI()

#CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mefoweb.com",
        "https://api.mefoweb.com",
        "https://care.mefoweb.com",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(recommend.router)

@app.get("/")
def root():
    return {"message": "FastAPI + LangChain 서버 실행 중"}