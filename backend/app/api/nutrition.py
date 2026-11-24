"""Nutrition targets and breakdown API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import date

from app.db.session import get_db
from app.db.models import User, UserProfile, MealPlan
from app.auth.dependencies import get_current_user
from app.services.nutrition_service import NutritionService

router = APIRouter()


class NutritionTargetsResponse(BaseModel):
    bmr_kcal: float
    tdee_kcal: float
    target_energy_kcal: float
    protein_g: float
    fat_g: float
    carbohydrate_g: float
    fibre_g: float
    sodium_mg: float
    micronutrients: Dict[str, Dict[str, Any]]
    calculation_method: str
    limitations: List[str]


class NutritionBreakdownResponse(BaseModel):
    recipe_id: int
    per_serving: Dict[str, Any]
    per_100g: Optional[Dict[str, Any]]
    ingredients: List[Dict[str, Any]]
    completeness: str
    notes: List[str]


class MealPlanNutritionResponse(BaseModel):
    meal_plan_id: int
    total_nutrients: Dict[str, Any]
    daily_average: Dict[str, Any]
    targets: Optional[Dict[str, Any]]
    completion_rate: float
    nutrition_status: Optional[str] = None
    notes: List[str] = []


@router.get("/targets", response_model=NutritionTargetsResponse)
async def get_nutrition_targets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get nutrition targets for current user."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please complete your profile first.",
        )

    service = NutritionService(db)
    targets = service.calculate_targets(profile)
    return targets


@router.post("/calculate", response_model=NutritionTargetsResponse)
async def calculate_nutrition_targets(
    profile_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Calculate nutrition targets from provided profile data."""
    # Create a temporary profile object
    from types import SimpleNamespace
    temp_profile = SimpleNamespace(**profile_data)
    
    service = NutritionService(db)
    targets = service.calculate_targets(temp_profile)
    return targets


@router.get("/breakdown/{recipe_id}", response_model=NutritionBreakdownResponse)
async def get_nutrition_breakdown(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed nutrition breakdown for a recipe."""
    service = NutritionService(db)
    breakdown = service.get_recipe_breakdown(recipe_id)
    if not breakdown:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found or nutrition data unavailable",
        )
    return breakdown


@router.get("/meal-plan/{meal_plan_id}", response_model=MealPlanNutritionResponse)
async def get_meal_plan_nutrition(
    meal_plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get nutrition summary for a meal plan."""
    # Verify meal plan belongs to user
    meal_plan = db.query(MealPlan).filter(
        MealPlan.id == meal_plan_id,
        MealPlan.user_id == current_user.id
    ).first()
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )

    service = NutritionService(db)
    nutrition = service.get_meal_plan_nutrition(meal_plan_id)
    return nutrition