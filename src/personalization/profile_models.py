"""User Profile Models - Structured user profile with validation."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Literal
from enum import Enum
from datetime import datetime
import json
import enum


class Sex(Enum):
    """Biological sex for nutritional calculations."""
    MALE = "MALE"
    FEMALE = "FEMALE"


class ActivityLevel(Enum):
    """Physical activity level for energy expenditure estimation."""
    SEDENTARY = "SEDENTARY"           # Little or no exercise
    LIGHTLY_ACTIVE = "LIGHTLY_ACTIVE" # Light exercise 1-3 days/week
    MODERATELY_ACTIVE = "MODERATELY_ACTIVE"  # Moderate exercise 3-5 days/week
    VERY_ACTIVE = "VERY_ACTIVE"       # Hard exercise 6-7 days/week
    EXTREMELY_ACTIVE = "EXTREMELY_ACTIVE"  # Very hard exercise, physical job


class DietaryPreference(Enum):
    """Dietary preference classification."""
    VEGETARIAN = "VEGETARIAN"
    VEGAN = "VEGAN"
    EGGETARIAN = "EGGETARIAN"         # Vegetarian + eggs
    NON_VEGETARIAN = "NON_VEGETARIAN"
    JAIN = "JAIN"                     # Jain dietary restrictions
    PESCATARIAN = "PESCATARIAN"       # Vegetarian + fish
    FLEXITARIAN = "FLEXITARIAN"       # Mostly vegetarian, occasional meat
    OMNIVORE = "OMNIVORE"             # No restrictions


class WeightGoal(Enum):
    """Weight management goal."""
    MAINTAIN = "MAINTAIN"
    LOSE = "LOSE"
    GAIN = "GAIN"


class MealFrequency(Enum):
    """Number of meals per day."""
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6


@dataclass
class Anthropometrics:
    """Physical measurements with units."""
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    age_years: Optional[int] = None
    sex: Optional[Sex] = None

    def validate(self) -> List[str]:
        """Validate anthropometric values. Returns list of error messages."""
        errors = []
        if self.height_cm is not None:
            if self.height_cm < 50 or self.height_cm > 250:
                errors.append(f"height_cm must be between 50 and 250, got {self.height_cm}")
        if self.weight_kg is not None:
            if self.weight_kg < 2 or self.weight_kg > 300:
                errors.append(f"weight_kg must be between 2 and 300, got {self.weight_kg}")
        if self.age_years is not None:
            if self.age_years < 1 or self.age_years > 120:
                errors.append(f"age_years must be between 1 and 120, got {self.age_years}")
        return errors

    def has_required_for_bmr(self) -> bool:
        """Check if all required fields for BMR calculation are present."""
        return all(v is not None for v in [self.height_cm, self.weight_kg, self.age_years, self.sex])


@dataclass
class DietaryProfile:
    """Dietary preferences and restrictions."""
    preference: DietaryPreference = DietaryPreference.OMNIVORE
    allergies: List[str] = field(default_factory=list)           # e.g., ["peanut", "shellfish"]
    ingredient_exclusions: List[str] = field(default_factory=list)  # e.g., ["onion", "garlic"]
    cuisine_preferences: List[str] = field(default_factory=list)    # preferred cuisines
    cuisine_exclusions: List[str] = field(default_factory=list)     # excluded cuisines
    disliked_ingredients: List[str] = field(default_factory=list)
    religious_restrictions: List[str] = field(default_factory=list)  # e.g., ["halal", "kosher", "jain"]
    medical_conditions: List[str] = field(default_factory=list)     # e.g., ["diabetes", "hypertension"]


@dataclass
class NutritionalGoals:
    """Optional nutritional targets (override calculated defaults)."""
    target_energy_kcal: Optional[float] = None
    target_protein_g: Optional[float] = None
    target_carbohydrate_g: Optional[float] = None
    target_fat_g: Optional[float] = None
    target_fibre_g: Optional[float] = None
    target_sodium_mg: Optional[float] = None
    weight_goal: WeightGoal = WeightGoal.MAINTAIN
    weight_change_rate_kg_per_week: float = 0.5  # Conservative default


@dataclass
class LifestyleProfile:
    """Lifestyle and eating patterns."""
    activity_level: ActivityLevel = ActivityLevel.SEDENTARY
    meal_frequency: MealFrequency = MealFrequency.THREE
    preferred_meal_times: Dict[str, str] = field(default_factory=dict)  # meal_name -> "HH:MM"
    cooking_skill: Literal["BEGINNER", "INTERMEDIATE", "ADVANCED"] = "INTERMEDIATE"
    budget_constraint: Optional[Literal["LOW", "MEDIUM", "HIGH"]] = None
    time_constraint_minutes: Optional[int] = None  # Max prep+cook time per meal


@dataclass
class UserProfile:
    """Complete user profile for personalization."""
    user_id: str
    anthropometrics: Anthropometrics = field(default_factory=Anthropometrics)
    dietary_profile: DietaryProfile = field(default_factory=DietaryProfile)
    nutritional_goals: NutritionalGoals = field(default_factory=NutritionalGoals)
    lifestyle: LifestyleProfile = field(default_factory=LifestyleProfile)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        """Validate entire profile. Returns list of error messages."""
        errors = []
        errors.extend(self.anthropometrics.validate())
        
        # Check for conflicting preferences
        if self.dietary_profile.preference == DietaryPreference.VEGAN:
            if any(ing in self.dietary_profile.ingredient_exclusions for ing in ["tofu", "tempeh", "legumes"]):
                pass  # Not an error, just a note
        
        # Validate weight change rate
        if self.nutritional_goals.weight_change_rate_kg_per_week > 1.0:
            errors.append("weight_change_rate_kg_per_week should not exceed 1.0 kg/week for safety")
        if self.nutritional_goals.weight_change_rate_kg_per_week < 0:
            errors.append("weight_change_rate_kg_per_week must be positive")
        
        return errors

    def has_minimum_for_nutrition_calculation(self) -> bool:
        """Check if profile has minimum data for nutrition target calculation."""
        return self.anthropometrics.has_required_for_bmr()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        # Handle both enum and string values
        sex_val = self.anthropometrics.sex
        if hasattr(sex_val, 'value'):
            sex_str = sex_val.value
        else:
            sex_str = sex_val
            
        pref_val = self.dietary_profile.preference
        if hasattr(pref_val, 'value'):
            pref_str = pref_val.value
        else:
            pref_str = pref_val
            
        goal_val = self.nutritional_goals.weight_goal
        if hasattr(goal_val, 'value'):
            goal_str = goal_val.value
        else:
            goal_str = goal_val
            
        act_val = self.lifestyle.activity_level
        if hasattr(act_val, 'value'):
            act_str = act_val.value
        else:
            act_str = act_val
            
        freq_val = self.lifestyle.meal_frequency
        if hasattr(freq_val, 'value'):
            freq_str = freq_val.value
        else:
            freq_str = freq_val
        
        return {
            "user_id": self.user_id,
            "anthropometrics": {
                "height_cm": self.anthropometrics.height_cm,
                "weight_kg": self.anthropometrics.weight_kg,
                "age_years": self.anthropometrics.age_years,
                "sex": sex_str,
            },
            "dietary_profile": {
                "preference": pref_str,
                "allergies": self.dietary_profile.allergies,
                "ingredient_exclusions": self.dietary_profile.ingredient_exclusions,
                "cuisine_preferences": self.dietary_profile.cuisine_preferences,
                "cuisine_exclusions": self.dietary_profile.cuisine_exclusions,
                "disliked_ingredients": self.dietary_profile.disliked_ingredients,
                "religious_restrictions": self.dietary_profile.religious_restrictions,
                "medical_conditions": self.dietary_profile.medical_conditions,
            },
            "nutritional_goals": {
                "target_energy_kcal": self.nutritional_goals.target_energy_kcal,
                "target_protein_g": self.nutritional_goals.target_protein_g,
                "target_carbohydrate_g": self.nutritional_goals.target_carbohydrate_g,
                "target_fat_g": self.nutritional_goals.target_fat_g,
                "target_fibre_g": self.nutritional_goals.target_fibre_g,
                "target_sodium_mg": self.nutritional_goals.target_sodium_mg,
                "weight_goal": goal_str,
                "weight_change_rate_kg_per_week": self.nutritional_goals.weight_change_rate_kg_per_week,
            },
            "lifestyle": {
                "activity_level": act_str,
                "meal_frequency": freq_str,
                "preferred_meal_times": self.lifestyle.preferred_meal_times,
                "cooking_skill": self.lifestyle.cooking_skill,
                "budget_constraint": self.lifestyle.budget_constraint,
                "time_constraint_minutes": self.lifestyle.time_constraint_minutes,
            },
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserProfile":
        """Deserialize from dictionary."""
        anthro = data.get("anthropometrics", {})
        dietary = data.get("dietary_profile", {})
        goals = data.get("nutritional_goals", {})
        lifestyle = data.get("lifestyle", {})
        
        # Helper to convert string to enum, handling both string and enum
        def to_enum(enum_cls, value, default):
            if value is None:
                return default
            if isinstance(value, enum_cls):
                return value
            try:
                return enum_cls(value)
            except (ValueError, KeyError):
                return default
        
        return cls(
            user_id=data["user_id"],
            anthropometrics=Anthropometrics(
                height_cm=anthro.get("height_cm"),
                weight_kg=anthro.get("weight_kg"),
                age_years=anthro.get("age_years"),
                sex=to_enum(Sex, anthro.get("sex"), None),
            ),
            dietary_profile=DietaryProfile(
                preference=to_enum(DietaryPreference, dietary.get("preference"), DietaryPreference.OMNIVORE),
                allergies=dietary.get("allergies", []),
                ingredient_exclusions=dietary.get("ingredient_exclusions", []),
                cuisine_preferences=dietary.get("cuisine_preferences", []),
                cuisine_exclusions=dietary.get("cuisine_exclusions", []),
                disliked_ingredients=dietary.get("disliked_ingredients", []),
                religious_restrictions=dietary.get("religious_restrictions", []),
                medical_conditions=dietary.get("medical_conditions", []),
            ),
            nutritional_goals=NutritionalGoals(
                target_energy_kcal=goals.get("target_energy_kcal"),
                target_protein_g=goals.get("target_protein_g"),
                target_carbohydrate_g=goals.get("target_carbohydrate_g"),
                target_fat_g=goals.get("target_fat_g"),
                target_fibre_g=goals.get("target_fibre_g"),
                target_sodium_mg=goals.get("target_sodium_mg"),
                weight_goal=to_enum(WeightGoal, goals.get("weight_goal"), WeightGoal.MAINTAIN),
                weight_change_rate_kg_per_week=goals.get("weight_change_rate_kg_per_week", 0.5),
            ),
            lifestyle=LifestyleProfile(
                activity_level=to_enum(ActivityLevel, lifestyle.get("activity_level"), ActivityLevel.SEDENTARY),
                meal_frequency=to_enum(MealFrequency, lifestyle.get("meal_frequency"), MealFrequency.THREE),
                preferred_meal_times=lifestyle.get("preferred_meal_times", {}),
                cooking_skill=lifestyle.get("cooking_skill", "INTERMEDIATE"),
                budget_constraint=lifestyle.get("budget_constraint"),
                time_constraint_minutes=lifestyle.get("time_constraint_minutes"),
            ),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            version=data.get("version", 1),
            metadata=data.get("metadata", {}),
        )


# --- Meal Slot Definitions ---

class MealSlot(Enum):
    """Standard meal slots."""
    BREAKFAST = "BREAKFAST"
    MORNING_SNACK = "MORNING_SNACK"
    LUNCH = "LUNCH"
    EVENING_SNACK = "EVENING_SNACK"
    DINNER = "DINNER"


DEFAULT_MEAL_SLOTS = [
    MealSlot.BREAKFAST,
    MealSlot.MORNING_SNACK,
    MealSlot.LUNCH,
    MealSlot.EVENING_SNACK,
    MealSlot.DINNER,
]

# Energy distribution across meals (fractions of daily total)
DEFAULT_MEAL_ENERGY_DISTRIBUTION = {
    MealSlot.BREAKFAST: 0.25,
    MealSlot.MORNING_SNACK: 0.10,
    MealSlot.LUNCH: 0.35,
    MealSlot.EVENING_SNACK: 0.10,
    MealSlot.DINNER: 0.20,
}

# For 3-meal frequency (no snacks)
THREE_MEAL_DISTRIBUTION = {
    MealSlot.BREAKFAST: 0.30,
    MealSlot.LUNCH: 0.40,
    MealSlot.DINNER: 0.30,
}

# For 4-meal frequency (one snack)
FOUR_MEAL_DISTRIBUTION = {
    MealSlot.BREAKFAST: 0.25,
    MealSlot.LUNCH: 0.35,
    MealSlot.EVENING_SNACK: 0.15,
    MealSlot.DINNER: 0.25,
}


def get_meal_distribution(meal_frequency: MealFrequency) -> Dict[MealSlot, float]:
    """Get energy distribution for a meal frequency."""
    if meal_frequency == MealFrequency.THREE:
        return THREE_MEAL_DISTRIBUTION
    elif meal_frequency == MealFrequency.FOUR:
        return FOUR_MEAL_DISTRIBUTION
    elif meal_frequency in (MealFrequency.FIVE, MealFrequency.SIX):
        return DEFAULT_MEAL_ENERGY_DISTRIBUTION
    return DEFAULT_MEAL_ENERGY_DISTRIBUTION