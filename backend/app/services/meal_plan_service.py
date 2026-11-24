"""Meal plan service.

Database-backed meal plans (create / add meals / complete meals) are fully
functional here. The Phase 4 optimiser and validator require a fitted
recommender + recipe-profile collection that this backend does not build, so
those two operations report that they are unavailable instead of pretending to
optimise a plan. See reports/phase9 for the honest capability matrix.
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import date

from app.db.models import MealPlan, MealPlanItem, MealPlanStatus, Recipe, UserProfile


class OptimizationUnavailable(RuntimeError):
    """Raised when the Phase 4 optimiser cannot run in this deployment."""


class MealPlanService:
    """Service for meal plan operations."""

    def __init__(self, db: Session):
        self.db = db

    def optimize_meal_plan(self, meal_plan_id: int) -> MealPlan:
        """Phase 4 optimisation is not wired into this backend.

        MealPlanOptimizer needs a MealPlanner + recipe collection + fitted
        recommender. Running it without those would silently do nothing, so we
        surface the limitation instead.
        """
        meal_plan = self.db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
        if not meal_plan:
            raise ValueError("Meal plan not found")

        raise OptimizationUnavailable(
            "Automatic meal-plan optimisation is not available in this build. "
            "It requires the Phase 4 recommender stack (fitted TF-IDF recommender + "
            "recipe profile collection), which is not initialised by the backend. "
            "Meals can still be added, edited and completed manually."
        )

    def generate_meal_plan(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
        name: Optional[str] = None,
    ) -> MealPlan:
        """Create a new (empty) active meal plan for the user.

        Recipes are chosen by the user; automatic plan generation needs the
        same Phase 4 stack as the optimiser and is therefore not performed.
        """
        self.db.query(MealPlan).filter(
            MealPlan.user_id == user_id,
            MealPlan.status == MealPlanStatus.ACTIVE,
        ).update({"status": MealPlanStatus.DRAFT})

        meal_plan = MealPlan(
            user_id=user_id,
            name=name or f"Meal Plan {start_date.strftime('%b %d')} - {end_date.strftime('%b %d')}",
            start_date=start_date,
            end_date=end_date,
            status=MealPlanStatus.ACTIVE,
        )
        self.db.add(meal_plan)
        self.db.commit()
        self.db.refresh(meal_plan)
        return meal_plan

    def validate_meal_plan(self, meal_plan_id: int) -> Dict[str, Any]:
        """Report that Phase 4 validation is unavailable (not that the plan is valid)."""
        meal_plan = self.db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
        if not meal_plan:
            raise ValueError("Meal plan not found")

        return {
            "is_valid": None,
            "warnings": [],
            "errors": [
                "Phase 4 meal-plan validation is not available in this build "
                "(requires a fitted recommender and recipe profile collection)."
            ],
            "nutrient_adequacy": {},
            "variety_score": None,
            "validation_available": False,
        }

    def _profile_to_dict(self, profile: UserProfile) -> Dict[str, Any]:
        """Convert UserProfile to a dictionary (used by callers/tests)."""
        return {
            "user_id": profile.user_id,
            "dietary_preference": profile.dietary_preference,
            "allergies": profile.allergies or [],
            "ingredient_exclusions": profile.ingredient_exclusions or [],
            "cuisine_preferences": profile.cuisine_preferences or [],
            "cuisine_exclusions": profile.cuisine_exclusions or [],
            "disliked_ingredients": profile.disliked_ingredients or [],
            "religious_restrictions": profile.religious_restrictions or [],
            "medical_conditions": profile.medical_conditions or [],
            "target_energy_kcal": profile.target_energy_kcal,
            "meal_frequency": profile.meal_frequency,
            "preferred_meal_times": profile.preferred_meal_times or {},
        }
