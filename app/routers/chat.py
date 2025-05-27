from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from app.services.rag.rag_service import generate_rag_response, stream_rag_response
from app.utils.response import ApiResponse
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
    

@router.get("/examples", response_class=JSONResponse)
async def get_example_questions():
    try:
        example_questions = [
            {"id": 1, "question": "아침을 상쾌하게 시작하는 스트레칭 추천해 줘"},
            {"id": 2, "question": "오늘 점심 뭐 먹지?"},
            {"id": 3, "question": "요즘따라 위장이 아픈데 주의해야할 점 있을까?"}
        ]
        return ApiResponse.success(data=example_questions)
    except Exception as e:
        return ApiResponse.error(message="예시 질문 조회 실패", code=1501)