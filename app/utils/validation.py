"""Validation utilities."""

import re
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import date

def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_positive_number(value: Union[int, float], field_name: str = "value") -> bool:
    """Validate that a number is positive."""
    if value is None:
        return False
    return value > 0

def validate_range(value: Union[int, float], min_val: float, max_val: float, field_name: str = "value") -> bool:
    """Validate that a number is within range."""
    if value is None:
        return False
    return min_val <= value <= max_val

def validate_meal_frequency(freq: int) -> bool:
    """Validate meal frequency."""
    return freq in [3, 4, 5, 6]

def validate_cooking_skill(skill: str) -> bool:
    """Validate cooking skill level."""
    return skill in ["BEGINNER", "INTERMEDIATE", "ADVANCED"]

def validate_dietary_preference(pref: str) -> bool:
    """Validate dietary preference."""
    valid = ["OMNIVORE", "VEGETARIAN", "VEGAN", "EGGETARIAN", "JAIN", "PESCATARIAN", "FLEXITARIAN"]
    return pref in valid

def validate_activity_level(level: str) -> bool:
    """Validate activity level."""
    valid = ["SEDENTARY", "LIGHTLY_ACTIVE", "MODERATELY_ACTIVE", "VERY_ACTIVE", "EXTREMELY_ACTIVE"]
    return level in valid

def validate_sex(sex: str) -> bool:
    """Validate sex."""
    return sex in ["MALE", "FEMALE"]

def validate_weight_goal(goal: str) -> bool:
    """Validate weight goal."""
    return goal in ["MAINTAIN", "LOSE", "GAIN"]

def validate_weight_change_rate(rate: float) -> bool:
    """Validate weight change rate."""
    return 0.1 <= rate <= 1.0

def validate_meal_frequency(freq: int) -> bool:
    """Validate meal frequency."""
    return freq in [3, 4, 5, 6]

def validate_time_constraint(minutes: int) -> bool:
    """Validate time constraint."""
    return 5 <= minutes <= 180

# Pydantic models for request validation
class ProfileCreate(BaseModel):
    height_cm: Optional[float] = Field(None, ge=50, le=250)
    weight_kg: Optional[float] = Field(None, ge=2, le=300)
    age_years: Optional[int] = Field(None, ge=1, le=120)
    sex: Optional[str] = Field(None, pattern="^(MALE|FEMALE)$")
    dietary_preference: str = Field(default="OMNIVORE")
    allergies: List[str] = Field(default_factory=list)
    ingredient_exclusions: List[str] = Field(default_factory=list)
    cuisine_preferences: List[str] = Field(default_factory=list)
    cuisine_exclusions: List[str] = Field(default_factory=list)
    disliked_ingredients: List[str] = Field(default_factory=list)
    religious_restrictions: List[str] = Field(default_factory=list)
    medical_conditions: List[str] = Field(default_factory=list)
    weight_goal: str = Field(default="MAINTAIN")
    weight_change_rate_kg_per_week: float = Field(default=0.5, ge=0.1, le=1.0)
    activity_level: str = Field(default="SEDENTARY")
    meal_frequency: int = Field(default=3, ge=3, le=6)
    cooking_skill: str = Field(default="INTERMEDIATE")
    budget_constraint: Optional[str] = None
    time_constraint_minutes: Optional[int] = Field(None, ge=5, le=180)

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=255)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ProfileUpdate(BaseModel):
    height_cm: Optional[float] = Field(None, ge=50, le=250)
    weight_kg: Optional[float] = Field(None, ge=2, le=300)
    age_years: Optional[int] = Field(None, ge=1, le=120)
    sex: Optional[str] = Field(None, pattern="^(MALE|FEMALE)$")
    dietary_preference: Optional[str] = None
    allergies: Optional[List[str]] = None
    ingredient_exclusions: Optional[List[str]] = None
    cuisine_preferences: Optional[List[str]] = None
    cuisine_exclusions: Optional[List[str]] = None
    disliked_ingredients: Optional[List[str]] = None
    religious_restrictions: Optional[List[str]] = None
    medical_conditions: Optional[List[str]] = None
    target_energy_kcal: Optional[float] = Field(None, ge=500, le=5000)
    target_protein_g: Optional[float] = Field(None, ge=10, le=300)
    target_carbohydrate_g: Optional[float] = Field(None, ge=20, le=500)
    target_fat_g: Optional[float] = Field(None, ge=10, le=200)
    target_fibre_g: Optional[float] = Field(None, ge=5, le=100)
    target_sodium_mg: Optional[float] = Field(None, ge=500, le=5000)
    weight_goal: Optional[str] = None
    weight_change_rate_kg_per_week: Optional[float] = Field(None, ge=0.1, le=1.0)
    activity_level: Optional[str] = None
    meal_frequency: Optional[int] = Field(None, ge=3, le=6)
    cooking_skill: Optional[str] = None
    budget_constraint: Optional[str] = None
    time_constraint_minutes: Optional[int] = Field(None, ge=5, le=180)

class MealPlanCreate(BaseModel):
    start_date: date
    days: int = Field(default=7, ge=1, le=14)
    meal_frequency: int = Field(default=4, ge=3, le=6)
    name: Optional[str] = None

class RecipeSearch(BaseModel):
    query: Optional[str] = None
    cuisine: Optional[str] = None
    course: Optional[str] = None
    diet_type: Optional[str] = None
    max_time: Optional[int] = Field(None, ge=0, le=300)
    min_nutrition_completeness: float = Field(default=0.0, ge=0.0, le=1.0)
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

class RecommendationRequest(BaseModel):
    user_id: int
    query_recipe_id: Optional[int] = None
    query_ingredients: Optional[List[str]] = None
    meal_slot: Optional[str] = None
    k: int = Field(default=10, ge=1, le=20)
    filters: Optional[dict] = None

class MealPlanRequest(BaseModel):
    user_id: int
    start_date: date
    days: int = Field(default=7, ge=1, le=14)
    meal_frequency: int = Field(default=4, ge=3, le=6)
    config: Optional[dict] = None