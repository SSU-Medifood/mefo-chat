"""
인코딩 관련 오류때문에 추후 추가.
"""

from datetime import datetime
from fastapi import HTTPException
from app.services.user_service import fetch_user_info

def calculate_daily_targets(token: str) -> dict:
    """
    로그인된 사용자의 신체 정보로 하루 권장 섭취량 계산
    - 기준: Mifflin-St Jeor 공식 + 활동계수 1.375
    """

    try:
        user_info = fetch_user_info(token)
        
        print("[DEBUG] user_info:", user_info)

        # 필수 값 확인
        weight = float(user_info.get("weight", 0))
        height = float(user_info.get("height", 0))
        birth = str(user_info.get("birth", ""))
        sex = user_info.get("userSex", "")

        if not weight or not height or not birth or not sex:
            raise HTTPException(status_code=400, detail="Missing required user profile data.")

        if len(birth) < 4:
            raise HTTPException(status_code=400, detail="Invalid birth year format.")

        birth_year = int(birth[:4])
        current_year = datetime.now().year
        age = current_year - birth_year

        # BMR 계산
        if sex == "남성":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        elif sex == "여성":
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        else:
            raise HTTPException(status_code=400, detail="Invalid gender value.")

        # 활동계수 적용
        tdee = bmr * 1.375

        return {
            "calories": round(tdee),
            "carbohydrate": round(tdee * 0.5 / 4),    # 50%
            "protein": round(tdee * 0.25 / 4),        # 25%
            "fat": round(tdee * 0.25 / 9),            # 25%
            "sodium": 2000  # WHO 기준 권장량
        }

    except HTTPException:
        raise

    except Exception as e:
        error_msg = str(e).encode('ascii', errors='ignore').decode()
        print(f"[ERROR] Failed to calculate daily targets: {error_msg}")
        raise HTTPException(status_code=500, detail="Failed to calculate daily nutrition targets.")