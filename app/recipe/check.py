import requests

url = 'http://openapi.foodsafetykorea.go.kr/api/abba144c850845ff9e10/COOKRCP01/json/162/162'
response = requests.get(url)
data = response.json()

# 레시피 리스트 추출
recipes = data['COOKRCP01']['row']

# 각 레시피에서 재료 정보 및 조리 순서 출력
for r in recipes:
    print(f"레시피 ID: {r['RCP_SEQ']}")
    print(f"레시피명: {r['RCP_NM']}")
    print("재료정보:", r.get('RCP_PARTS_DTLS', '없음'))
    print("조리순서:")
    for i in range(1, 21):
        step = r.get(f'MANUAL{str(i).zfill(2)}')
        if step and step.strip():
            print(f"{i:02d}: {step.strip()}")
    print("-" * 60)