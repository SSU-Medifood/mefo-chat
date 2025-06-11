from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from app.auth.security import get_token
from app.services.recommend.bw_service import get_foods

router = APIRouter(prefix="/api/recommend", tags=["Recommend"])
security = HTTPBearer(auto_error=False)

class FoodsResponse(BaseModel):
    success: bool = True
    code:    int  = 0
    data:    List[str]

@router.get(
    "/black",
    response_model=FoodsResponse,
    summary="흑색(권장하지 않는) 음식 조회",
    description="""
      llm 통해서 흑색 음식 5개 호출  
      첫 호출 이후 하루 동안 응답 지속되고, 자정 지나면 리셋
    """,
    responses={
        401: {"description": "유효하지 않은 토큰"},
        500: {"description": "서버 내부 오류"},
    },
)
async def black_foods(token: str = Depends(get_token)):
    try:
        black = await get_foods(token, "black")
        return {"success": True, "code": 0, "data": black}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/white",
    response_model=FoodsResponse,
    summary="백색(권장하는) 음식 조회",
    description="""
      llm 통해서 백색 음식 5개 호출  
      첫 호출 이후 하루 동안 응답 지속되고, 자정 지나면 리셋
    """,
    responses={
        401: {"description": "유효하지 않은 토큰"},
        500: {"description": "서버 내부 오류"},
    },
)
async def white_foods(token: str = Depends(get_token)):
    try:
        white = await get_foods(token, "white")
        return {"success": True, "code": 0, "data": white}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))