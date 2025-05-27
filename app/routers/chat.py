from fastapi import APIRouter, Header, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.rag.rag_service import generate_rag_response, stream_rag_response
from app.auth.security import get_token

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    question: str


@router.post("/")
async def chat(
    request: ChatRequest,
    token: str = Depends(get_token)
):
    answer = generate_rag_response(request.question, token)
    return {"answer": answer}


@router.post("/stream")
async def chat_stream(
    request: ChatRequest, 
    token: str = Depends(get_token)
):
    stream = stream_rag_response(request.question, token)
    return StreamingResponse(
        stream,
        media_type="text/event-stream"
    )