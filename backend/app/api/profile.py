"""User profile API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import date, datetime

from app.db.session import get_db
from app.db.models import User, UserProfile
from app.auth.dependencies import get_current_user

router = APIRouter()


class ProfileBase(BaseModel):
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    age_years: Optional[int] = None
    sex: Optional[str] = None
    dietary_preference: str = "NON_VEGETARIAN"
    allergies: List[str] = []
    ingredient_exclusions: List[str] = []
    cuisine_preferences: List[str] = []
    cuisine_exclusions: List[str] = []
    disliked_ingredients: List[str] = []
    religious_restrictions: List[str] = []
    medical_conditions: List[str] = []
    target_energy_kcal: Optional[float] = None
    target_protein_g: Optional[float] = None
    target_carbohydrate_g: Optional[float] = None
    target_fat_g: Optional[float] = None
    target_fibre_g: Optional[float] = None
    target_sodium_mg: Optional[float] = None
    weight_goal: str = "MAINTAIN"
    weight_change_rate_kg_per_week: float = 0.5
    activity_level: str = "SEDENTARY"
    meal_frequency: int = 3
    preferred_meal_times: dict = {}
    cooking_skill: str = "INTERMEDIATE"
    budget_constraint: Optional[str] = None
    time_constraint_minutes: Optional[int] = None

    @validator("sex")
    def validate_sex(cls, v):
        if v and v not in ["MALE", "FEMALE"]:
            raise ValueError("Sex must be MALE or FEMALE")
        return v

    @validator("dietary_preference")
    def validate_dietary_preference(cls, v):
        valid = ["VEGETARIAN", "VEGAN", "EGGETARIAN", "NON_VEGETARIAN"]
        if v not in valid:
            raise ValueError(f"Dietary preference must be one of: {valid}")
        return v

    @validator("weight_goal")
    def validate_weight_goal(cls, v):
        valid = ["MAINTAIN", "LOSE", "GAIN"]
        if v not in valid:
            raise ValueError(f"Weight goal must be one of: {valid}")
        return v

    @validator("activity_level")
    def validate_activity_level(cls, v):
        valid = ["SEDENTARY", "LIGHTLY_ACTIVE", "MODERATELY_ACTIVE", "VERY_ACTIVE", "EXTREMELY_ACTIVE"]
        if v not in valid:
            raise ValueError(f"Activity level must be one of: {valid}")
        return v

    @validator("cooking_skill")
    def validate_cooking_skill(cls, v):
        valid = ["BEGINNER", "INTERMEDIATE", "ADVANCED"]
        if v not in valid:
            raise ValueError(f"Cooking skill must be one of: {valid}")
        return v

    @validator("weight_change_rate_kg_per_week")
    def validate_weight_change_rate(cls, v):
        if v < -1 or v > 1:
            raise ValueError("Weight change rate must be between -1 and 1 kg/week")
        return v


class ProfileUpdate(ProfileBase):
    pass


class ProfileResponse(ProfileBase):
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's profile."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        # Create default profile if doesn't exist
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.patch("", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    # Update fields
    update_data = profile_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile