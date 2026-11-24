"""Meal Plan Models - Data models for meal planning."""

# Re-export from meal_planner for convenience
from .meal_planner import (
    MealPlanStatus,
    MealSlotPlan,
    DailyMealPlan,
    WeeklyMealPlan,
    MealPlanConfig,
)

from .meal_plan_validation import (
    ValidationSeverity,
    ValidationIssue,
    ValidationResult,
)

__all__ = [
    # Meal plan models
    "MealPlanStatus",
    "MealSlotPlan",
    "DailyMealPlan",
    "WeeklyMealPlan",
    "MealPlanConfig",
    
    # Validation models
    "ValidationSeverity",
    "ValidationIssue",
    "ValidationResult",
]