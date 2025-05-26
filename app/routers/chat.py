from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from app.services.rag.rag_service import generate_rag_response

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    question: str

#배포 시 대체 예정
'''
@router.post("/")
async def chat(request: ChatRequest, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization 헤더가 필요합니다.")
    
    token = authorization.replace("Bearer ", "")
    answer = generate_rag_response(request.question, token)
    return {"answer": answer}
'''

@router.post("/")
async def chat(request: ChatRequest, authorization: str = Header(default=None)):
    # [임시] Authorization이 없으면 하드코딩된 토큰 사용
    if authorization:
        token = authorization.replace("Bearer ", "")
    else:
        # 로컬 테스트용 임시 토큰
        token = "eyJhbGciOiJIUzI1NiJ9.eyJsb2dpbklkIjoiMDQwOGtzeUBnbWFpbC5jb20iLCJyb2xlIjoiUk9MRV9VU0VSIiwiaWF0IjoxNzQ4MjUyOTUzLCJleHAiOjE3NDgyNTY1NTN9.WJqfwNE8eNXx3DjwNRYsinEExCGwMi3q8JAGlkLCx4c"
        print("[디버그] Authorization 헤더 없음 → 임시 토큰 사용")

    answer = generate_rag_response(request.question, token)
    return {"answer": answer}