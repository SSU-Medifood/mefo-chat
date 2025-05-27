from fastapi.responses import JSONResponse
from typing import Any

class ApiResponse:
    @staticmethod
    def success(data: Any = None, code: int = 0) -> JSONResponse:
        return JSONResponse(
            content={
                "success": True,
                "code": code,
                "data": data
            }
        )

    @staticmethod
    def error(message: str = "오류가 발생했습니다.", code: int = 1000) -> JSONResponse:
        return JSONResponse(
            content={
                "success": False,
                "code": code,
                "data": None,
                "message": message
            },
            status_code=400
        )