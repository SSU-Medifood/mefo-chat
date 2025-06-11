from dotenv import load_dotenv
load_dotenv()

import os
import json
from datetime import datetime, date, time, timedelta

import aioredis
import random
from langchain_core.tracers.context import tracing_v2_enabled
from fastapi.concurrency import run_in_threadpool
from langchain.schema import AIMessage
from app.services.chat_service import generate_response
from app.services.user_service import fetch_user_info, fetch_user_id

REDIS_URL       = os.getenv("REDIS_URL")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

def _seconds_until_midnight() -> int:
    now      = datetime.now()
    tomorrow = datetime.combine(now.date() + timedelta(days=1), time.min)
    return int((tomorrow - now).total_seconds())

async def _call_deepseek(prompt: str) -> list[str]:
    with tracing_v2_enabled():
        ai_msg = await run_in_threadpool(generate_response, prompt)

    if isinstance(ai_msg, AIMessage):
        text = ai_msg.content
    else:
        text = str(ai_msg)

    return [
        line.strip(" -0123456789. ")
        for line in text.splitlines()
        if line.strip()
    ]

async def _generate_food_list(token: str, user_id: int, mode: str) -> list[str]:
    """
    1) fetch_user_info(token) 로 프로필 조회
    2) 프로필을 읽기 좋게 포맷
    3) 프롬프트 생성 (black/white 분기)
    4) DeepSeek 호출
    """
    # 1) 사용자 프로필 가져오기
    profile = await run_in_threadpool(fetch_user_info, token)
    seed = random.random()

    # 2) 필요한 필드 파싱
    allergies = [d["allergyDrug"] for d in profile.get("allergyDrugList", [])]
    diseases  = [d["disease"]      for d in profile.get("diseaseList", [])]

    allergy_str = ", ".join(allergies) if allergies else "없음"
    disease_str = ", ".join(diseases)  if diseases  else "없음"

    if mode == "black":
        instruction = "섭취를 권장하지 않는 음식 5가지를 한국어로 이름만, 부가 설명 없이, 목록 형태로 나열해줘."
    else:
        instruction = "섭취를 권장하는, 건강에 도움이 되는 음식 5가지를 한국어로 이름만, 부가 설명 없이, 목록 형태로 나열해줘."

    prompt = (
        "사용자의 건강정보를 참고하여 "
        f"{instruction}\n\n"
        f"- 성별: {profile.get('userSex')}\n"
        f"- 키/몸무게: {profile.get('height')}cm / {profile.get('weight')}kg\n"
        f"- 흡연 여부: {profile.get('userSmoke')}\n"
        f"- 음주 빈도: {profile.get('userDrink')}\n"
        f"- 질병 이력: {disease_str}\n"
        f"- 알레르기 약물: {allergy_str}\n"
        f"\n# 시드: {seed}"
    )

    return await _call_deepseek(prompt)

async def get_foods(token: str, mode: str) -> list[str]:
    """
    캐시가 있으면 반환
    없으면 _generate_food_list 호출 및 Redis 저장 후 반환
    """
    
    user_id   = await run_in_threadpool(fetch_user_id, token)

    today     = date.today().isoformat()
    cache_key = f"foods:{mode}:{user_id}:{today}"

    if (cached := await redis.get(cache_key)) is not None:
        return json.loads(cached)

    items = await _generate_food_list(token, user_id, mode)

    await redis.set(cache_key, json.dumps(items), ex=_seconds_until_midnight())
    return items
