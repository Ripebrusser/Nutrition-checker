"""Nutrition breakdown API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, List, Any

from app.db.session import get_db
from app.db.models import User, Recipe
from app.auth.dependencies import get_current_user
from app.services.nutrition_service import NutritionService

router = APIRouter()


class NutritionBreakdownResponse(BaseModel):
    recipe_id: int
    per_serving: Dict[str, Any]
    per_100g: Optional[Dict[str, Any]]
    ingredients: List[Dict[str, Any]]
    completeness: str
    notes: List[str]


@router.get("/breakdown/{recipe_id}", response_model=NutritionBreakdownResponse)
async def get_nutrition_breakdown(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed nutrition breakdown for a recipe."""
    # Verify recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    service = NutritionService(db)
    breakdown = service.get_recipe_breakdown(recipe_id)
    if not breakdown:
        # Return unavailable status instead of 404
        return NutritionBreakdownResponse(
            recipe_id=recipe_id,
            per_serving={
                "calculation_status": "UNAVAILABLE",
                "missing_nutrients": ["All - no approved IFCT mappings"],
                "provenance": "Zero approved IFCT mappings available"
            },
            per_100g=None,
            ingredients=[],
            completeness="UNAVAILABLE",
            notes=["Nutrition analysis unavailable: zero approved IFCT mappings"]
        )
    return breakdown