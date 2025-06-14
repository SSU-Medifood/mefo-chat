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


def fetch_user_id(token: str) -> int:
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/api/user/loginCheck"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["data"]["userId"]
    raise Exception("userId 조회 실패")


def fetch_liked_recipes(token: str) -> list[dict]:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    url = f"{BASE_URL}/api/storage/getAll"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"찜한 레시피 요청 실패: {response.status_code}")

    result = response.json()
    if not result.get("success"):
        raise Exception("찜한 레시피 응답 실패")

    return result.get("data", [])