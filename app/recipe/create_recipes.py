import requests

url = 'http://openapi.foodsafetykorea.go.kr/api/abba144c850845ff9e10/COOKRCP01/json/1/5'

response = requests.get(url)
data = response.json()

recipes = data['COOKRCP01']['row']

for r in recipes:
    print("레시피ID:", r['RCP_SEQ'])
    print("이름:", r['RCP_NM'])
    print("칼로리:", r['INFO_ENG'])
    print("탄수화물:", r['INFO_CAR'])
    print("단백질:", r['INFO_PRO'])
    print("지방:", r['INFO_FAT'])
    print("나트륨:", r['INFO_NA'])
    print("분량:", r['INFO_WGT'])
    print("요리종류:", r['RCP_PAT2'])
    print("조리방법:", r['RCP_WAY2'])
    print("이미지:", r['ATT_FILE_NO_MAIN'])
    print("재료:", r['RCP_PARTS_DTLS'])
    print("-" * 50)