import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BACKEND_API_BASE_URL")

def fetch_user_info(token: str) -> dict:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    url = f"{BASE_URL}/api/userInfo/get"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"유저 정보 요청 실패: {response.status_code}")
    return response.json()["data"]