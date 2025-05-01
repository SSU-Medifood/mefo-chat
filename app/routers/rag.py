from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_service import generate_rag_response

router = APIRouter(prefix="/rag", tags=["RAG"])

class RAGRequest(BaseModel):
    question: str

@router.post("/")
async def rag_endpoint(request: RAGRequest):
    answer = generate_rag_response(request.question)
    return {"answer": answer}