from fastapi import APIRouter, Depends, HTTPException
from app.auth.security import get_token
from app.recipe.rule_based import get_rule_based_recommendations
from app.recipe.content_based import get_content_based_recommendations
from app.recipe.recipes_loader import load_ingredient_df

router = APIRouter(
    prefix="/api/recipe",
    tags=["Recipe"]
)

@router.get("/recommend", summary="규칙 + 콘텐츠 기반 통합 추천")
def recommend_total(token: str = Depends(get_token)):
    try:
        # 1. 규칙 기반 필터링 적용
        filtered_df = get_rule_based_recommendations(token)
        if filtered_df.empty:
            return {
                "success": True,
                "count": 0,
                "recipes": []
            }

        # 2. 콘텐츠 기반 정렬 및 상위 6개 추천
        ingredient_df = load_ingredient_df()
        recommended = get_content_based_recommendations(
            token=token,
            filtered_df=filtered_df,
            ingredient_df=ingredient_df
        )

        return {
            "success": True,
            "count": len(recommended),
            "data": recommended
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))