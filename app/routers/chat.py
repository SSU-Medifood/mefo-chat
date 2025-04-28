from fastapi import APIRouter
from pydantic import BaseModel
from app.services.chat_service import generate_response

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    question: str

@router.post("/")
async def chat(request: ChatRequest):
    answer = generate_response(request.question)
    return {"answer": answer}