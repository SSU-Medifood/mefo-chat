import requests
import os
from dotenv import load_dotenv
import time
import json
import re
from bs4 import BeautifulSoup

load_dotenv()
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")

def get_requestId(pdf_path: str) -> str:
    url = "https://api.upstage.ai/v1/document-digitization/async"
    headers = {
        "Authorization": f"Bearer {UPSTAGE_API_KEY}"
    }
    files = {
        "document": open(pdf_path, "rb")
    }
    data = {
        "model": "document-parse" 
    }

    response = requests.post(url, headers=headers, files=files, data=data)
    
    if response.status_code == 202:
        request_id = response.json()["request_id"]
        print(f"업로드 성공 request_id: {request_id}")
        return request_id
    else:
        print("업로드 실패:", response.text)
        raise Exception("Upstage 비동기 업로드 실패")
    
def clean_markdown(text: str) -> str:
    # 날짜 형식 (예: 2025. 1. 22. 오후 10:59 등)
    text = re.sub(r'\d{4}\.\s?\d{1,2}\.\s?\d{1,2}\.\s?(오전|오후)?\s?\d{1,2}:\d{2}', '', text)

    # 단독 연도/월 (예: "2024", "2025", "1", "22" 등만 존재하는 줄)
    text = re.sub(r'^\s*\d{1,4}\s*$', '', text, flags=re.MULTILINE)

    # indesign 흔적 제거 (예: "건강 실천 안내서.indd", "실천 안내서.indd" 등)
    text = re.sub(r'.*\.indd.*', '', text)

    # 불필요한 개행 제거 (연속 개행을 한 줄로)
    text = re.sub(r'\n{2,}', '\n', text)

    # 양쪽 공백 정리
    return text.strip()
    
    
def save_markdown(request_id: str, output_path: str, polling_interval=5):
    status_url = f"https://api.upstage.ai/v1/document-digitization/requests/{request_id}"
    headers = {
        "Authorization": f"Bearer {UPSTAGE_API_KEY}"
    }

    # 1. 상태 완료될 때까지 대기
    while True:
        response = requests.get(status_url, headers=headers)
        data = response.json()

        status = data.get("status", "")
        if status == "completed":
            print("문서 분석 완료")
            break
        elif status in ["submitted", "scheduled", "started"]:
            print(f"현재 상태: {status}... 다시 확인 중")
            time.sleep(polling_interval)
        else:
            raise Exception(f"변환 실패: 상태={status}")

    # 2. batch 다운로드
    all_markdown_chunks = []

    for batch in data["batches"]:
        download_url = batch["download_url"]
        print(f"다운로드 중: {download_url}")

        batch_response = requests.get(download_url)
        batch_data = batch_response.json()

        for element in batch_data["elements"]:
            content = element.get("content", {})
            print("[디버그] content keys:", content.keys())

            html = content.get("html", "")
            if html:
                soup = BeautifulSoup(html, "html.parser")
                text = soup.get_text(separator=" ", strip=True)
                
                #불필요한 텍스트 필터링
                cleaned_text = clean_markdown(text)
                if cleaned_text:
                    all_markdown_chunks.append(cleaned_text)
                else:
                    print("[경고] HTML 파싱 결과가 비어 있음:", html)
            else:
                print("[경고] HTML 필드 없음:", content)

    # 3. Markdown 파일로 저장
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_markdown_chunks))

    print(f"Markdown 저장 완료: {output_path}")
