"""Nutrition service integrating with Phase 3 nutrition engine."""

from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from datetime import date

from app.db.models import UserProfile, Recipe, MealPlan, MealPlanItem

# Import Phase 4 nutrition modules. The ML packages live under src/ and are
# imported as `src.<package>` (the same way the project's tests import them).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.personalization.energy_requirements import calculate_energy_requirements
from src.personalization.macro_targets import calculate_nutrition_targets
from src.personalization.profile_models import Anthropometrics, Sex, WeightGoal

# Display units for the nutrients reported by MicronutrientTargets.
MICRONUTRIENT_META = {
    "sodium_mg": ("Sodium", "mg"),
    "potassium_mg": ("Potassium", "mg"),
    "calcium_mg": ("Calcium", "mg"),
    "iron_mg": ("Iron", "mg"),
    "zinc_mg": ("Zinc", "mg"),
    "vitamin_a_mcg": ("Vitamin A", "mcg"),
    "vitamin_d_iu": ("Vitamin D", "IU"),
    "vitamin_b12_mcg": ("Vitamin B12", "mcg"),
    "folate_mcg": ("Folate", "mcg"),
    "vitamin_c_mg": ("Vitamin C", "mg"),
}


class NutritionService:
    """Service for nutrition calculations using Phase 3/4 engines."""

    def __init__(self, db: Session):
        self.db = db

    def calculate_targets(self, profile: UserProfile) -> Dict[str, Any]:
        """Calculate nutrition targets using Phase 4 nutrition target engine."""
        # Validate required profile fields
        required_fields = ['age_years', 'sex', 'height_cm', 'weight_kg', 'activity_level']
        missing = [f for f in required_fields if getattr(profile, f, None) is None]
        
        if missing:
            # Return default targets with warning
            return self._get_default_targets(missing)

        # Phase 4 engine: BMR (Mifflin-St Jeor) -> TDEE (PAL) -> goal adjustment
        energy = calculate_energy_requirements(
            height_cm=profile.height_cm,
            weight_kg=profile.weight_kg,
            age_years=profile.age_years,
            sex=profile.sex,
            activity_level=profile.activity_level,
            weight_goal=profile.weight_goal or "MAINTAIN",
            weight_change_kg_per_week=profile.weight_change_rate_kg_per_week or 0.0,
        )

        try:
            sex = Sex(profile.sex)
        except (ValueError, AttributeError, TypeError):
            sex = Sex.MALE

        anthropometrics = Anthropometrics(
            height_cm=profile.height_cm,
            weight_kg=profile.weight_kg,
            age_years=profile.age_years,
            sex=sex,
        )
        try:
            weight_goal = WeightGoal(profile.weight_goal or "MAINTAIN")
        except ValueError:
            weight_goal = WeightGoal.MAINTAIN

        # Phase 4 engine: macro + micronutrient targets from ICMR 2020
        targets = calculate_nutrition_targets(energy, anthropometrics, weight_goal)
        macros = targets.macros
        micros = targets.micros

        micronutrients = self._format_micronutrients(micros)

        # Compile limitations (honest reporting of the methodology)
        limitations = [
            "Calculations based on ICMR 2020 RDA and Mifflin-St Jeor equations",
            "Individual requirements may vary based on genetics, health conditions, and metabolic factors",
            "Consult a registered dietitian or healthcare provider for personalized advice",
        ]
        for warning in getattr(energy, "warnings", []) or []:
            limitations.append(warning)
        for warning in getattr(macros, "warnings", []) or []:
            limitations.append(warning)

        return {
            "bmr_kcal": round(energy.bmr_kcal, 1),
            "tdee_kcal": round(energy.tdee_kcal, 1),
            "target_energy_kcal": round(energy.target_energy_kcal, 1),
            "protein_g": round(macros.protein_g, 1),
            "fat_g": round(macros.fat_g, 1),
            "carbohydrate_g": round(macros.carbohydrate_g, 1),
            "fibre_g": round(macros.fibre_g, 1),
            "sodium_mg": round(micros.sodium_mg, 1) if micros.sodium_mg else None,
            "micronutrients": micronutrients,
            "calculation_method": "Mifflin-St Jeor BMR × PAL (ICMR 2020) + Macro distribution (ICMR 2020)",
            "limitations": limitations,
        }

    def _get_default_targets(self, missing_fields: List[str]) -> Dict[str, Any]:
        """Return default targets when profile is incomplete."""
        return {
            "bmr_kcal": 1500.0,
            "tdee_kcal": 2000.0,
            "target_energy_kcal": 2000.0,
            "protein_g": 60.0,
            "fat_g": 67.0,
            "carbohydrate_g": 250.0,
            "fibre_g": 25.0,
            "sodium_mg": 2000.0,
            "micronutrients": {},
            "calculation_method": "Default values (profile incomplete)",
            "limitations": [
                f"Profile incomplete - missing: {', '.join(missing_fields)}",
                "Using population average defaults",
                "Complete your profile for personalized targets",
            ],
        }

    def _format_micronutrients(self, micros) -> Dict[str, Dict[str, Any]]:
        """Shape the Phase 4 micronutrient targets for the API response.

        Nutrients the engine leaves unknown stay None rather than becoming zero.
        """
        micronutrients: Dict[str, Dict[str, Any]] = {}
        for key, (name, unit) in MICRONUTRIENT_META.items():
            value = getattr(micros, key, None)
            micronutrients[key] = {
                "target": round(value, 1) if isinstance(value, (int, float)) else None,
                "unit": unit,
                "name": name,
            }
        return micronutrients

    def get_recipe_breakdown(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed nutrition breakdown for a recipe using Phase 3 engine."""
        # This would integrate with the Phase 3 nutrition calculator
        # For now, return unavailable since no approved mappings exist
        recipe = self.db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            return None

        return {
            "recipe_id": recipe_id,
            "per_serving": {
                "energy_kcal": None,
                "protein_g": None,
                "fat_g": None,
                "carbohydrate_g": None,
                "fibre_g": None,
                "sodium_mg": None,
                "calculation_status": "UNAVAILABLE",
                "missing_nutrients": ["All - zero approved IFCT mappings"],
                "provenance": "Zero approved IFCT mappings available. Gate C authorization pending.",
            },
            "per_100g": None,
            "ingredients": [],
            "completeness": "UNAVAILABLE",
            "notes": [
                "Nutrition analysis unavailable: zero approved IFCT mappings",
                "1.4% gram weight coverage for ingredients",
                "42% of IFCT foods missing fibre/carbohydrate data",
                "Gate C authorization pending for ingredient mappings",
            ],
        }

    def get_meal_plan_nutrition(self, meal_plan_id: int) -> Optional[Dict[str, Any]]:
        """Get nutrition summary for a meal plan."""
        meal_plan = self.db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
        if not meal_plan:
            return None

        items = self.db.query(MealPlanItem).filter(
            MealPlanItem.meal_plan_id == meal_plan_id,
            MealPlanItem.recipe_id.isnot(None)
        ).all()

        # Nutrition values stay None (unknown), never 0, while zero IFCT mappings
        # are approved. Callers must display them as unavailable.
        total_nutrients = {
            "energy_kcal": None,
            "protein_g": None,
            "fat_g": None,
            "carbohydrate_g": None,
            "fibre_g": None,
            "sodium_mg": None,
        }

        daily_average = {k: None for k in total_nutrients}
        completion_rate = 0
        if items:
            completed = sum(1 for i in items if i.is_completed)
            completion_rate = (completed / len(items)) * 100

        # Get user targets if available
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == meal_plan.user_id).first()
        targets = None
        if profile:
            targets = self.calculate_targets(profile)

        return {
            "meal_plan_id": meal_plan_id,
            "total_nutrients": total_nutrients,
            "daily_average": daily_average,
            "targets": targets,
            "completion_rate": completion_rate,
            "nutrition_status": "UNAVAILABLE",
            "notes": [
                "Recipe nutrient totals are unavailable: zero approved IFCT ingredient mappings (Gate C pending).",
                "Values are reported as null rather than 0 so they are not mistaken for measurements.",
            ],
        }