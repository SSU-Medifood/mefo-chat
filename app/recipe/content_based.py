import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.user_service import fetch_liked_recipes
from app.recipe.content_utils import add_content_string_column
from app.recipe.recipes_loader import load_recipe_df


def recommend_random(df: pd.DataFrame, n: int = 6) -> list[dict]:
    return df.sample(n=min(n, len(df)))[["id", "menu", "imageSmall"]].to_dict(orient="records")


def get_content_based_recommendations(token: str, filtered_df: pd.DataFrame, ingredient_df: pd.DataFrame) -> list[dict]:
    """
    콘텐츠 기반 추천 시스템
    - 사용자 찜 레시피로부터 콘텐츠 벡터 생성
    - 규칙 기반 필터링을 통과한 레시피 중 유사한 레시피 상위 20개에서 6개 랜덤 추천
    """
    
    # ✅ 예외 1: 규칙 기반 필터링 결과 없음
    if filtered_df.empty:
        print("[WARN] 규칙 기반 필터링 결과 없음 → 전체 레시피 중 랜덤 추천")
        fallback_df = load_recipe_df()
        return recommend_random(fallback_df, 6)

    # 1. 사용자 찜 목록 로딩
    liked = fetch_liked_recipes(token)
    liked_ids = [r['recipeId'] for r in liked]

    if not liked_ids:
        print("[INFO] 사용자가 찜한 레시피가 없어 랜덤 추천 실행")
        return recommend_random(filtered_df, 6)

    # 2. content_string 생성
    filtered_df = add_content_string_column(filtered_df, ingredient_df).reset_index(drop=True)
    
    # ✅ 예외 2: content_string 비어 있음
    if filtered_df['content_string'].isnull().all() or filtered_df['content_string'].str.strip().eq("").all():
        print("[WARN] content_string 비어 있음 → 랜덤 추천")
        return recommend_random(filtered_df, 6)

    # 4. TF-IDF 벡터화
    try:
        tfidf = TfidfVectorizer()
        tfidf_matrix = tfidf.fit_transform(filtered_df['content_string'])
    except Exception as e:
        print(f"[ERROR] TF-IDF 벡터화 실패: {e}")
        return recommend_random(filtered_df, 6)
    
    liked_indexes = [
        idx for idx in filtered_df[filtered_df['id'].isin(liked_ids)].index
        if idx < tfidf_matrix.shape[0]
    ]

    if not liked_indexes:
        print("[INFO] 찜한 레시피가 규칙 필터링 결과에 없음 → 랜덤 추천 실행")
        return recommend_random(filtered_df, 6)

    # 6. 사용자 벡터 생성
    user_vector = tfidf_matrix[liked_indexes].mean(axis=0)
    user_vector = np.asarray(user_vector).reshape(1, -1)

    # 7. 코사인 유사도 계산
    similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()
    filtered_df['similarity'] = similarities

    # 8. 상위 20개 중 랜덤 6개 추천
    top_20 = filtered_df.sort_values(by='similarity', ascending=False).head(20)
    
    # ✅ 예외 4: 추천이 6개 미만일 경우 보충
    if len(top_20) < 6:
        needed = 6 - len(top_20)
        exclude_ids = top_20['id'].tolist()
        candidates = filtered_df[~filtered_df['id'].isin(exclude_ids)]
        if not candidates.empty:
            extra = candidates.sample(n=min(needed, len(candidates)))
            top_20 = pd.concat([top_20, extra])
            
    recommend_recipes = top_20.sample(n=min(6, len(top_20)))
    recommend_recipes = recommend_recipes.rename(columns={
        "id": "recipeId",
        "menu": "name"
    })

    return recommend_recipes[["recipeId", "name", "imageSmall"]].to_dict(orient="records")