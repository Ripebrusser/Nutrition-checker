"""Meal history API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

from app.db.session import get_db
from app.db.models import User, MealHistory, Recipe
from app.auth.dependencies import get_current_user

router = APIRouter()


class MealHistoryResponse(BaseModel):
    id: int
    user_id: int
    meal_plan_id: Optional[int]
    recipe_id: Optional[int]
    meal_slot: str
    consumed_at: datetime
    servings: float
    recipe: Optional[dict] = None

    class Config:
        from_attributes = True


@router.get("", response_model=List[MealHistoryResponse])
async def get_meal_history(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get meal history for current user."""
    history = db.query(MealHistory).filter(
        MealHistory.user_id == current_user.id
    ).order_by(desc(MealHistory.consumed_at)).limit(limit).all()

    result = []
    for h in history:
        recipe = db.query(Recipe).filter(Recipe.id == h.recipe_id).first() if h.recipe_id else None
        result.append(MealHistoryResponse(
            id=h.id,
            user_id=h.user_id,
            meal_plan_id=h.meal_plan_id,
            recipe_id=h.recipe_id,
            meal_slot=h.meal_slot.value,
            consumed_at=h.consumed_at,
            servings=h.servings,
            recipe={
                "id": recipe.id,
                "recipe_id": recipe.recipe_id,
                "recipe_name": recipe.recipe_name,
                "cuisine": recipe.cuisine,
                "course": recipe.course,
                "recipe_type": recipe.recipe_type,
                "total_time_min": recipe.total_time_min,
                "servings": recipe.servings,
                "image_url": recipe.image_url,
                "diet_labels": recipe.diet_labels,
                "nutrition_per_serving": recipe.nutrition_per_serving if hasattr(recipe, 'nutrition_per_serving') else None,
            } if recipe else None
        ))
    return result


@router.get("/range", response_model=List[MealHistoryResponse])
async def get_meal_history_by_range(
    start: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end: date = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get meal history for a date range."""
    start_dt = datetime.combine(start, datetime.min.time())
    end_dt = datetime.combine(end, datetime.max.time())

    history = db.query(MealHistory).filter(
        MealHistory.user_id == current_user.id,
        MealHistory.consumed_at >= start_dt,
        MealHistory.consumed_at <= end_dt
    ).order_by(desc(MealHistory.consumed_at)).all()

    result = []
    for h in history:
        recipe = db.query(Recipe).filter(Recipe.id == h.recipe_id).first() if h.recipe_id else None
        result.append(MealHistoryResponse(
            id=h.id,
            user_id=h.user_id,
            meal_plan_id=h.meal_plan_id,
            recipe_id=h.recipe_id,
            meal_slot=h.meal_slot.value,
            consumed_at=h.consumed_at,
            servings=h.servings,
            recipe={
                "id": recipe.id,
                "recipe_id": recipe.recipe_id,
                "recipe_name": recipe.recipe_name,
                "cuisine": recipe.cuisine,
                "course": recipe.course,
                "recipe_type": recipe.recipe_type,
                "total_time_min": recipe.total_time_min,
                "servings": recipe.servings,
                "image_url": recipe.image_url,
                "diet_labels": recipe.diet_labels,
            } if recipe else None
        ))
    return result