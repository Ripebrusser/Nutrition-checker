"""Personalized recommendations API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.db.session import get_db
from app.db.models import User, UserProfile
from app.auth.dependencies import get_current_user
from app.services.recommendation_service import RecommendationService

router = APIRouter()


class RecommendationRequest(BaseModel):
    meal_slot: Optional[str] = None
    cuisine: Optional[str] = None
    diet_labels: List[str] = []
    exclude_allergens: List[str] = []
    exclude_ingredients: List[str] = []
    max_prep_time: Optional[int] = None
    max_cook_time: Optional[int] = None
    k: int = 10


class RecommendationResult(BaseModel):
    recipe_id: int
    score: float
    explanation: str
    component_scores: Dict[str, float]
    shared_ingredients: List[str]


class RecommendationsResponse(BaseModel):
    recommendations: List[RecommendationResult]
    query_info: Dict[str, Any]


@router.post("", response_model=RecommendationsResponse)
async def get_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get personalized recipe recommendations."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please complete your profile first to get personalized recommendations.",
        )

    service = RecommendationService(db)
    result = service.get_recommendations(
        user_profile=profile,
        meal_slot=request.meal_slot,
        cuisine=request.cuisine,
        diet_labels=request.diet_labels,
        exclude_allergens=request.exclude_allergens,
        exclude_ingredients=request.exclude_ingredients,
        max_prep_time=request.max_prep_time,
        max_cook_time=request.max_cook_time,
        k=request.k,
    )
    return result


@router.get("/similar/{recipe_id}", response_model=RecommendationsResponse)
async def get_similar_recipes(
    recipe_id: int,
    k: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get recipes similar to a given recipe."""
    service = RecommendationService(db)
    result = service.get_similar_recipes(recipe_id, k)
    return result