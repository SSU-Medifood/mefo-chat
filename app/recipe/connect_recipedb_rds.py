import pymysql
import requests
from datetime import datetime
import re

# 안전한 정수 변환 함수
def safe_int(val):
    try:
        return int(float(val))
    except:
        return 0

# 재료 파싱 함수
import re

def split_ingredient(raw_text):
    # \r\n → \n 통일
    raw_text = raw_text.replace('\r\n', '\n')

    # 1. 괄호 안 쉼표 보존을 위해 임시 토큰으로 치환
    raw_text = re.sub(r'\(([^)]+)\)', lambda m: '(' + m.group(1).replace(',', '[[COMMA]]') + ')', raw_text)

    # 2. 쉼표 또는 줄바꿈 기준으로 분할
    items = re.split(r'[,\n]+', raw_text)

    results = []
    for item in items:
        item = item.strip()
        if not item:
            continue

        # ● 또는 : 같은 prefix 제거
        if ':' in item:
            item = item.split(':', 1)[1].strip()
        item = re.sub(r'^●+', '', item).strip()

        # 3. "재료", "소스" 또는 "소스명 + 재료" 제거
        item = re.sub(r'^(재료|[\w가-힣]*소스|양념)\s+', '', item).strip()

        # 4. 괄호 있는 경우: 이름 / 용량 추출
        match = re.match(r'^(.+?)\((.+?)\)$', item)
        if match:
            name = match.group(1).strip()
            capacity = match.group(2).replace('[[COMMA]]', ',').strip()
        else:
            # fallback: 공백 기준 분할
            parts = item.split(' ', 1)
            name = parts[0].strip()
            capacity = parts[1].strip() if len(parts) > 1 else ''

        results.append((name, capacity))

    return results


# 조리설명 앞 숫자 제거
def clean_instruction(text):
    return re.sub(r'^\d+\.\s*', '', text).strip()

# 1. DB 연결
conn = pymysql.connect(
    host='mefo.c9qco6s0sre8.ap-northeast-2.rds.amazonaws.com',
    user='root',
    password='mefo1234!',
    db='mefo',
    charset='utf8mb4'
)
cursor = conn.cursor()

# 2. API 요청
url = 'http://openapi.foodsafetykorea.go.kr/api/abba144c850845ff9e10/COOKRCP01/json/172/203'
response = requests.get(url)
data = response.json()
recipes = data['COOKRCP01']['row']

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 3. DB 저장
for r in recipes:
    # recipe 테이블
    cursor.execute("""
        INSERT INTO recipe (
            created_at, updated_at, menu, food_type, cooking_type,
            amount, calories, carbohydrate, protein, fat, sodium
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        now,
        now,
        r.get('RCP_NM'),
        r.get('RCP_PAT2'),
        r.get('RCP_WAY2'),
        1,
        safe_int(r.get('INFO_ENG')),
        safe_int(r.get('INFO_CAR')),
        safe_int(r.get('INFO_PRO')),
        safe_int(r.get('INFO_FAT')),
        safe_int(r.get('INFO_NA'))
    ))
    recipe_id = cursor.lastrowid

    # ingredient 테이블
    ingredients_raw = r.get('RCP_PARTS_DTLS', '')
    parsed_ingredients = split_ingredient(ingredients_raw)
    for name, capacity in parsed_ingredients:
        cursor.execute("""
            INSERT INTO ingredient (recipe_id, created_at, updated_at, ingredient_name, capacity)
            VALUES (%s, %s, %s, %s, %s)
        """, (recipe_id, now, now, name, capacity))

    # instruction 테이블
    for i in range(1, 21):
        step = r.get(f'MANUAL{str(i).zfill(2)}')
        if step and step.strip():
            cleaned_step = clean_instruction(step)
            cursor.execute("""
                INSERT INTO instruction (recipe_id, created_at, updated_at, step_number, description)
                VALUES (%s, %s, %s, %s, %s)
            """, (recipe_id, now, now, i, cleaned_step))

    # recipe_image 테이블
    image_small = r.get('ATT_FILE_NO_MAIN')
    image_large = r.get('ATT_FILE_NO_MK')
    if image_small or image_large:
        cursor.execute("""
            INSERT INTO recipe_image (recipe_id, created_at, updated_at, image_small, image_large)
            VALUES (%s, %s, %s, %s, %s)
        """, (recipe_id, now, now, image_small, image_large))

# 4. 커밋 및 종료
conn.commit()
cursor.close()
conn.close()