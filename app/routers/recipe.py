from fastapi import APIRouter, Depends, HTTPException
from app.auth.security import get_token
from app.recipe.rule_based import get_rule_based_recommendations
from app.recipe.content_based import get_content_based_recommendations, get_more_recipes
from app.recipe.daily_meal import get_daily_meal_plan
from app.recipe.recipes_loader import load_ingredient_df

router = APIRouter(
    prefix="/api/recipe",
    tags=["Recipe"]
)


@router.get(
    "/daily", 
    summary="오늘의 식단 추천",
    description="""
    메인 화면의 `오늘의 식단`에서 사용  
    하루 단위로 업데이트
    """
)
async def recommend_daily_meal(token: str = Depends(get_token)):
    try:
        result = await get_daily_meal_plan(token)
        return {
            "success": True,
            "count": len(result),
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/recommend", 
    summary="메인 화면에서 레시피 추천",
    description="""
    메인 화면의 `(사용자)님에게 좋은 음식을 알려드릴게요.`에서 사용  
    규칙 + 콘텐츠 기반으로 레시피 6개 추천  
    10분마다 업데이트
    """
)
async def recommend_total(token: str = Depends(get_token)):
    try:
        filtered_df = get_rule_based_recommendations(token)
        if filtered_df.empty:
            return {
                "success": True,
                "count": 0,
                "data": []
            }
            
        ingredient_df = load_ingredient_df()
        recommended = await get_content_based_recommendations(
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
    
    
@router.get(
    "/more/{recipeId}", 
    summary="더 많은 레시피",
    description="""
    레시피 페이지 하단 `더 많은 레시피`에 사용  
    선택한 레시피 기반 유사도 높은 6개의 레시피를 출력
    """
)
def recommend_more_recipes(recipeId: int):
    try:
        recommended = get_more_recipes(recipeId)
        return {
            "success": True,
            "count": len(recommended),
            "data": recommended
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))