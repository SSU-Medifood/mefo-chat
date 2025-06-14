import pandas as pd
import numpy as np
import json
from datetime import datetime
from fastapi.concurrency import run_in_threadpool
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.user_service import fetch_user_id, fetch_liked_recipes
from app.recipe.content_utils import add_content_string_column
from app.recipe.recipes_loader import load_recipe_df, load_ingredient_df
from app.utils.redis import redis


def recommend_random(df: pd.DataFrame, n: int = 6) -> list[dict]:
    return df.sample(n=min(n, len(df)))[["id", "menu", "imageSmall"]].rename(columns={
        "id": "recipeId",
        "menu": "name"
    }).to_dict(orient="records")


async def get_content_based_recommendations(token: str, filtered_df: pd.DataFrame, ingredient_df: pd.DataFrame) -> list[dict]:
    user_id = await run_in_threadpool(fetch_user_id, token)
    now_minute = int(datetime.now().timestamp() // 600)
    cache_key = f"main_recommend:{user_id}:{now_minute}"

    if (cached := await redis.get(cache_key)) is not None:
        print("[CACHE] main recipe recommendation hit")
        return json.loads(cached)

    if filtered_df.empty:
        print("[WARN] 규칙 기반 필터링 결과 없음 → 전체 레시피 중 랜덤 추천")
        fallback_df = load_recipe_df()
        result = recommend_random(fallback_df, 6)
        await redis.set(cache_key, json.dumps(result, ensure_ascii=False), ex=600)
        return result

    liked = fetch_liked_recipes(token)
    liked_ids = [r['recipeId'] for r in liked]

    if not liked_ids:
        print("[INFO] 사용자가 찜한 레시피가 없어 랜덤 추천 실행")
        result = recommend_random(filtered_df, 6)
        await redis.set(cache_key, json.dumps(result, ensure_ascii=False), ex=600)
        return result

    filtered_df = add_content_string_column(filtered_df, ingredient_df).reset_index(drop=True)

    if filtered_df['content_string'].isnull().all() or filtered_df['content_string'].str.strip().eq("").all():
        print("[WARN] content_string 비어 있음 → 랜덤 추천")
        result = recommend_random(filtered_df, 6)
        await redis.set(cache_key, json.dumps(result, ensure_ascii=False), ex=600)
        return result

    try:
        tfidf = TfidfVectorizer()
        tfidf_matrix = tfidf.fit_transform(filtered_df['content_string'])
    except Exception as e:
        print(f"[ERROR] TF-IDF 벡터화 실패: {e}")
        result = recommend_random(filtered_df, 6)
        await redis.set(cache_key, json.dumps(result, ensure_ascii=False), ex=600)
        return result

    liked_indexes = [
        idx for idx in filtered_df[filtered_df['id'].isin(liked_ids)].index
        if idx < tfidf_matrix.shape[0]
    ]

    if not liked_indexes:
        print("[INFO] 찜한 레시피가 규칙 필터링 결과에 없음 → 랜덤 추천 실행")
        result = recommend_random(filtered_df, 6)
        await redis.set(cache_key, json.dumps(result, ensure_ascii=False), ex=600)
        return result

    user_vector = tfidf_matrix[liked_indexes].mean(axis=0)
    user_vector = np.asarray(user_vector).reshape(1, -1)

    similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()
    filtered_df['similarity'] = similarities

    top_20 = filtered_df.sort_values(by='similarity', ascending=False).head(20)

    if len(top_20) < 6:
        needed = 6 - len(top_20)
        exclude_ids = top_20['id'].tolist()
        candidates = filtered_df[~filtered_df['id'].isin(exclude_ids)]
        if not candidates.empty:
            extra = candidates.sample(n=min(needed, len(candidates)))
            top_20 = pd.concat([top_20, extra])

    recommend_recipes = top_20.sample(n=min(6, len(top_20)))
    recommend_recipes = recommend_recipes.rename(columns={"id": "recipeId", "menu": "name"})

    result = recommend_recipes[["recipeId", "name", "imageSmall"]].to_dict(orient="records")

    await redis.set(cache_key, json.dumps(result, ensure_ascii=False), ex=600)

    return result


def get_more_recipes(recipe_id: int, top_k: int = 20, return_n: int = 6):
    recipe_df = load_recipe_df()
    ingredient_df = load_ingredient_df()

    full_df = add_content_string_column(recipe_df, ingredient_df)

    if recipe_id not in full_df['id'].values:
        raise ValueError("해당 recipeId가 존재하지 않습니다.")

    full_df = full_df[["id", "menu", "imageSmall", "content_string"]].reset_index(drop=True)
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(full_df['content_string'])

    target_index = full_df[full_df['id'] == recipe_id].index[0]
    target_vector = tfidf_matrix[target_index]

    # 콘텐츠 기반 유사도 계산
    similarities = cosine_similarity(target_vector, tfidf_matrix).flatten()
    full_df['similarity'] = similarities

    candidates = full_df[full_df['id'] != recipe_id].sort_values(by='similarity', ascending=False).head(top_k)

    sampled = recommend_random(candidates, n=return_n)
    print("[DEBUG] sampled:", sampled)

    return sampled
