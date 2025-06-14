import pandas as pd

def preprocess_text_columns(recipe_df: pd.DataFrame, ingredient_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    recipe_df = recipe_df.copy()
    ingredient_df = ingredient_df.copy()

    recipe_df['menu'] = recipe_df['menu'].str.strip().str.lower()
    recipe_df['food_type'] = recipe_df['food_type'].str.strip().str.lower()
    recipe_df['cooking_type'] = recipe_df['cooking_type'].str.strip().str.lower()
    ingredient_df['ingredient_name'] = ingredient_df['ingredient_name'].str.strip().str.lower()

    return recipe_df, ingredient_df


def make_content_string(recipe_row: pd.Series, ingredient_df: pd.DataFrame) -> str:
    recipe_id = recipe_row['id']
    ingredients = ingredient_df[
        ingredient_df['recipe_id'] == recipe_id
    ]['ingredient_name'].tolist()

    return (
        f"{recipe_row['menu']} "
        f"{recipe_row['food_type']} "
        f"{recipe_row['cooking_type']} "
        + " ".join(ingredients)
    )


def add_content_string_column(recipe_df: pd.DataFrame, ingredient_df: pd.DataFrame) -> pd.DataFrame:
    recipe_df, ingredient_df = preprocess_text_columns(recipe_df, ingredient_df)
    
    recipe_df['content_string'] = recipe_df.apply(
        lambda row: make_content_string(row, ingredient_df),
        axis=1
    )
    
    return recipe_df
