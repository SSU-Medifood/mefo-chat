import pandas as pd
from app.services.user_service import fetch_user_info
from app.recipe.filter_rules import DISEASE_FILTER_RULES
from app.recipe.recipes_loader import load_recipe_df, load_ingredient_df

def get_rule_based_recommendations(token: str):
    user_info = fetch_user_info(token)
    disease_names = [d['disease'] for d in user_info.get("diseaseList", [])]
    allergy_items = [a['allergyEtc'] for a in user_info.get("allergyEtcList", [])]

    recipe_df = load_recipe_df()
    ingredient_df = load_ingredient_df()
    ingredient_df['ingredient_name'] = ingredient_df['ingredient_name'].str.strip().str.lower()
    recipes_filtered = recipe_df.copy()

    # 질병 기반 필터링
    for disease in disease_names:
        rules = DISEASE_FILTER_RULES.get(disease)
        if not rules:
            continue
        for field, condition in rules.items():
            if field == "ingredient_name":
                block_ids = ingredient_df[
                    ingredient_df['ingredient_name'].apply(lambda name: not condition(name))
                ]['recipe_id'].unique()
                recipes_filtered = recipes_filtered[~recipes_filtered['id'].isin(block_ids)]
            else:
                if field in recipes_filtered.columns:
                    recipes_filtered = recipes_filtered[recipes_filtered[field].apply(condition)]

    # 알레르기 필터링
    for allergy in allergy_items:
        allergy = allergy.strip().lower()
        block_ids = ingredient_df[
            ingredient_df['ingredient_name'].str.contains(allergy)
        ]['recipe_id'].unique()
        recipes_filtered = recipes_filtered[~recipes_filtered['id'].isin(block_ids)]

    if len(recipes_filtered) == 0:
        return []

    result_df = recipes_filtered.sample(n=min(6, len(recipes_filtered)))
    return result_df[["id", "menu"]].to_dict(orient="records")
