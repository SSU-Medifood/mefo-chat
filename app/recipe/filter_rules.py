DISEASE_FILTER_RULES = {
    "고혈압": {
        "sodium": lambda val: float(val) <= 600
    },
    "당뇨병": {
        "carbohydrate": lambda val: float(val) <= 50
    },
    "이상지질혈증": {
        "fat": lambda val: float(val) <= 15
    },
    "비만": {
        "calories": lambda val: float(val) <= 600
    },
    "공복혈당장애": {
        "carbohydrate": lambda val: float(val) <= 40
    },
    "비알코올성 지방간": {
        "fat": lambda val: float(val) <= 10,
        "sodium": lambda val: float(val) <= 700
    },
    "심근경색": {
        "fat": lambda val: float(val) <= 12,
        "sodium": lambda val: float(val) <= 600
    },
    "심부전": {
        "sodium": lambda val: float(val) <= 500,
        "ingredient_name": lambda name: not any(x in name for x in ["소금", "간장"])
    },
    "고지혈증": {
        "fat": lambda val: float(val) <= 15
    },
    "갑상선 기능 항진증": {
        "ingredient_name": lambda name: not any(x in name for x in ["김", "미역", "다시마"])
    },
    "갑상선 기능 저하증": {
        "ingredient_name": lambda name: not any(x in name for x in ["대두", "콩", "브로콜리"])
    },
    "빈혈": {
        "ingredient_name": lambda name: any(x in name for x in ["간", "시금치", "소고기", "돼지고기", "말고기", "염소고기" "건포도"])
    },
    "백혈병": {
        "ingredient_name": lambda name: not any(x in name for x in ["날생선", "육회", "생달걀"])
    },
    "구루병": {
        "ingredient_name": lambda name: any(x in name for x in ["우유", "달걀", "연어", "버섯"])
    },
    "결핵": {
        "ingredient_name": lambda name: not any(x in name for x in ["튀김", "베이컨", "햄", "소시지"])
    },
    "통풍": {
        "ingredient_name": lambda name: not any(x in name for x in ["내장", "멸치", "고등어", "꽁치", "참치", "삼치", "연어", "육수", "황태"])
    },
    "유당 불내증": {
        "ingredient_name": lambda name: not any(x in name for x in ["우유", "치즈", "버터", "요거트"])
    },
    "식도암": {
        "ingredient_name": lambda name: not any(x in name for x in ["햄", "소시지", "베이컨", "장아찌"])
    },
    "후두암": {
        "ingredient_name": lambda name: not any(x in name for x in ["술", "훈제", "햄", "소시지", "베이컨"])
    },
    "난소암": {
        "ingredient_name": lambda name: not any(x in name for x in ["마가린", "버터", "튀김"])
    },
    "직장암": {
        "ingredient_name": lambda name: not any(x in name for x in ["소고기", "돼지고기", "햄", "소시지", "베이컨", "지방"])
    },
    "자궁암": {
        "ingredient_name": lambda name: not any(x in name for x in ["설탕", "튀김"])
    },
    "피부암": {
        "ingredient_name": lambda name: not any(x in name for x in [ "설탕", "튀김"])
    },
    "전립선암": {
        "ingredient_name": lambda name: not any(x in name for x in ["유제품", "소고기", "돼지고기", "버터"])
    },
    "요도암": {
        "ingredient_name": lambda name: not any(x in name for x in ["알코올"])
    },
    "협심증": {
        "fat": lambda val: float(val) <= 12,
        "sodium": lambda val: float(val) <= 500
    },
    "위암": {
        "ingredient_name": lambda name: not any(x in name for x in ["절임", "소금", "장아찌", "훈제"])
    },
    "간암": {
        "ingredient_name": lambda name: not any(x in name for x in ["햄", "소시지", "베이컨", "와인"])
    },
    "대장암": {
        "ingredient_name": lambda name: not any(x in name for x in ["소고기", "돼지고기", "햄", "소시지", "베이컨", "튀김"])
    },
    "유방암": {
        "ingredient_name": lambda name: not any(x in name for x in ["지방", "버터", "마가린"])
    },
    "자궁경부암": {
        "ingredient_name": lambda name: not any(x in name for x in ["고지방", "햄", "소시지", "베이컨", "설탕"])
    },
    "폐암": {
        "ingredient_name": lambda name: not any(x in name for x in [ "훈제", "햄", "소시지", "베이컨"])
    },
    "갑상선암": {
        "ingredient_name": lambda name: not any(x in name for x in ["미역", "다시마", "김"])
    },
    "췌장암": {
        "ingredient_name": lambda name: not any(x in name for x in ["고지방", "육류", "기름진 음식", "설탕"])
    },
    "뇌졸중": {
        "sodium": lambda val: float(val) <= 500,
        "fat": lambda val: float(val) <= 12
    },
    "뇌경색": {
        "sodium": lambda val: float(val) <= 500,
        "fat": lambda val: float(val) <= 10
    },
    "뇌출혈": {
        "sodium": lambda val: float(val) <= 500,
        "fat": lambda val: float(val) <= 10
    },
    "간염": {
        "ingredient_name": lambda name: not any(x in name for x in [ "햄", "소시지", "베이컨"]),
        "fat": lambda val: float(val) <= 10
    },
    "간경변증": {
        "sodium": lambda val: float(val) <= 500,
        "fat": lambda val: float(val) <= 10,
        "ingredient_name": lambda name: not any(x in name for x in ["소금", "간장"])
    },
    "위염": {
        "ingredient_name": lambda name: not any(x in name for x in ["매운", "산성", "튀김"])
    },
    "장염": {
        "ingredient_name": lambda name: not any(x in name for x in ["우유", "버터", "요거트", "치즈", "튀김"])
    },
    "위궤양": {
        "ingredient_name": lambda name: not any(x in name for x in ["매운"])
    },
    "식도염": {
        "ingredient_name": lambda name: not any(x in name for x in ["초콜릿", "커피", "탄산"])
    },
    "과민성 대장 증후군": {
        "ingredient_name": lambda name: not any(x in name for x in ["우유", "버터", "요거트", "치즈", "밀가루", "양파", "마늘", "콩"])
    },
    "크론병": {
        "ingredient_name": lambda name: not any(x in name for x in ["튀김", "우유", "버터", "치즈", "요거트"])
    },
    "담낭염": {
        "fat": lambda val: float(val) <= 10,
        "ingredient_name": lambda name: not any(x in name for x in ["기름", "노른자", "치즈", "버터"])
    },
    "폐렴": {
        "ingredient_name": lambda name: not any(x in name for x in ["튀김"])
    },
    "천식": {
        "ingredient_name": lambda name: not any(x in name for x in ["우유", "치즈", "계란", "튀김"])
    },
    "만성폐쇄성폐질환": {
        "fat": lambda val: float(val) <= 15,
        "ingredient_name": lambda name: not any(x in name for x in ["햄", "소시지", "베이컨", "알코올", "카페인"])
    },
    "기관지염": {
        "ingredient_name": lambda name: not any(x in name for x in ["기름", "튀김", "가공육"])
    },
}


ALLERGY_FILTER_RULES = {
    "알류(가금류에 한함)": {
        "ingredient_name": lambda name: not any(x in name for x in ["달걀", "계란", "유정란", "알", "노른자", "흰자"])
    },
    "우유": {
        "ingredient_name": lambda name: not any(x in name for x in ["우유", "치즈", "버터", "요거트", "연유", "크림"])
    },
    "메밀": {
        "ingredient_name": lambda name: "메밀" not in name
    },
    "땅콩": {
        "ingredient_name": lambda name: "땅콩" not in name
    },
    "대두": {
        "ingredient_name": lambda name: any(x not in name for x in ["두유", "콩", "대두", "된장", "간장", "청국장"])
    },
    "밀": {
        "ingredient_name": lambda name: not any(x in name for x in ["밀가루", "빵", "국수", "파스타", "밀"])
    },
    "잣": {
        "ingredient_name": lambda name: "잣" not in name
    },
    "호두": {
        "ingredient_name": lambda name: "호두" not in name
    },
    "게": {
        "ingredient_name": lambda name: "게" not in name
    },
    "새우": {
        "ingredient_name": lambda name: "새우" not in name
    },
    "오징어": {
        "ingredient_name": lambda name: "오징어" not in name
    },
    "고등어": {
        "ingredient_name": lambda name: "고등어" not in name
    },
    "조개류(굴, 전복, 홍합)": {
        "ingredient_name": lambda name: not any(x in name for x in ["조개", "굴", "전복", "홍합"])
    },
    "복숭아": {
        "ingredient_name": lambda name: "복숭아" not in name
    },
    "토마토": {
        "ingredient_name": lambda name: "토마토" not in name
    },
    "닭고기": {
        "ingredient_name": lambda name: not any(x in name for x in ["닭", "치킨", "닭가슴살"])
    },
    "돼지고기": {
        "ingredient_name": lambda name: not any(x in name for x in ["돼지", "삼겹살", "목살", "돼지고기"])
    },
    "쇠고기": {
        "ingredient_name": lambda name: not any(x in name for x in ["소고기", "쇠고기", "불고기", "우둔살"])
    },
    "아황산류": {
        "ingredient_name": lambda name: "아황산" not in name
    },
}
