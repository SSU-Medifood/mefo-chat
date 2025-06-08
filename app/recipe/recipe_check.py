import requests

url = 'http://openapi.foodsafetykorea.go.kr/api/abba144c850845ff9e10/COOKRCP01/json/10/15'

try:
    response = requests.get(url, timeout=10)  # 10초 이상 기다리지 않도록 설정
    print("응답 상태 코드:", response.status_code)
    print("응답 본문 (일부):", response.text[:500])  # 본문이 너무 길면 일부만 출력

    if response.status_code == 200:
        data = response.json()
        if 'COOKRCP01' in data and 'row' in data['COOKRCP01']:
            print("✅ API 응답 정상 + 데이터 존재함")
        else:
            print("⚠️ API는 응답했지만 데이터 없음 ('row' 키 없음)")
    else:
        print("❌ 응답 실패: 상태 코드가 200이 아님")

except requests.exceptions.Timeout:
    print("⏱️ 요청 시간 초과 (Timeout)")
except requests.exceptions.RequestException as e:
    print("❌ 요청 에러:", e)