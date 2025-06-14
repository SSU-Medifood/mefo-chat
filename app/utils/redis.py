import os
import aioredis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL       = os.getenv("REDIS_URL")

redis = aioredis.from_url(
    REDIS_URL,
    encoding="utf-8",
    decode_responses=True
)
