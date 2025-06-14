import pandas as pd
import random
import itertools
import json
import numpy as np
from datetime import date, datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi.concurrency import run_in_threadpool

from app.recipe.recipes_loader import load_recipe_df, load_ingredient_df
from app.recipe.content_utils import add_content_string_column
from app.recipe.rule_based import get_rule_based_recommendations
from app.recipe.nutrition_calculator import calculate_daily_targets
from app.services.user_service import fetch_user_info,  fetch_user_id, fetch_liked_recipes
from app.utils.redis import redis


# food types 중복 방지
def is_diverse_combo(recipes: list[dict]) -> bool:
    food_types = set()
    cooking_types = set()
    for r in recipes:
        food_types.add(r["food_type"])
        cooking_types.add(r["cooking_type"])
    return len(food_types) == len(recipes) and len(cooking_types) == len(recipes)


# calorie 제한 및 영양 성분 합계
def is_under_calorie_limit(recipes: list[dict], max_calories=1500) -> bool:
    total = sum(float(r.get("calories", 0)) for r in recipes)
    return total <= max_calories


# 콘텐츠 기반 필터링
def get_content_top_n(token: str, df: pd.DataFrame, ingredient_df: pd.DataFrame, top_k: int = 20) -> pd.DataFrame:
    liked = fetch_liked_recipes(token)
    liked_ids = [r['recipeId'] for r in liked]
    
    df = add_content_string_column(df, ingredient_df)
    df = df.reset_index(drop=True)

    if df.empty or not liked_ids:
        return df.sample(n=min(top_k, len(df)))

    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(df['content_string'])

    liked_indexes = df[df['id'].isin(liked_ids)].index.tolist()
    if not liked_indexes:
        return df.sample(n=min(top_k, len(df)))

    user_vector = tfidf_matrix[liked_indexes].mean(axis=0)
    user_vector = np.asarray(user_vector).reshape(1, -1)
    similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()
    df['similarity'] = similarities

    return df.sort_values(by='similarity', ascending=False).head(top_k)


# 레시피 중복 없이 3개 선택
def select_balanced_combination(df: pd.DataFrame, max_calories=1500) -> list[dict]:
    records = df.to_dict(orient="records")
    random.shuffle(records)

    for combo in itertools.combinations(records, 3):
        if is_diverse_combo(combo) and is_under_calorie_limit(combo, max_calories):
            return format_recipe_output(combo)

    return format_recipe_output(records[:3])


def format_recipe_output(recipes: list[dict]) -> dict:
    time_tags = ["breakfast", "lunch", "dinner"]
    output = {}

    for i, r in enumerate(recipes):
        output[time_tags[i]] = {
            "recipeId": r["id"],
            "name": r["menu"],
            "imageSmall": r.get("imageSmall"),
            "carbohydrate": r.get("carbohydrate"),
            "protein": r.get("protein"),
            "fat": r.get("fat"),
            "sodium": r.get("sodium"),
            "calories": r.get("calories"),
        }
    return output


def _seconds_until_midnight() -> int:
    now = datetime.now()
    midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
    return int((midnight - now).total_seconds())


async def get_daily_meal_plan(token: str) -> dict:
    user_id = await run_in_threadpool(fetch_user_id, token)
    today = date.today().isoformat()
    cache_key = f"daily_meal:{user_id}:{today}"

    cached = await redis.get(cache_key)
    if cached:
        print("[CACHE] daily meal cache hit")
        return json.loads(cached)

    rule_filtered_df = get_rule_based_recommendations(token)
    if rule_filtered_df.empty:
        rule_filtered_df = load_recipe_df()

    ingredient_df = load_ingredient_df()
    content_top_n = get_content_top_n(token, rule_filtered_df, ingredient_df, top_k=30)
    result = select_balanced_combination(content_top_n)

    await redis.set(cache_key, json.dumps(result, ensure_ascii=False), ex=_seconds_until_midnight())

    return result