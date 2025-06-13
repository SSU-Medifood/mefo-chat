from fastapi import APIRouter, Depends, HTTPException
from app.auth.security import get_token
from app.recipe.rule_based import get_rule_based_recommendations

router = APIRouter(
    prefix="/api/recipe",
    tags=["Recipe"]
)

@router.get("/recommend", summary="규칙 기반 추천 레시피 6개")
def recommend_by_disease(token: str = Depends(get_token)):
    try:
        recommendations = get_rule_based_recommendations(token)
        return {
            "success": True,
            "data": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
