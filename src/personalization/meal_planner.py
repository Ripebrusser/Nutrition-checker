"""Meal Planner - Generate personalized meal plans with nutritional validation."""

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import date, datetime, timedelta
from pathlib import Path
import random
from copy import deepcopy

from .personalized_recommender import (
    PersonalizedRecommender, PersonalizedRecommendationResult,
    PersonalizedRecommenderConfig
)
from .nutrition_targets import CompleteNutritionTargets, MacroTargets
from .recipe_profile import RecipeProfileCollection, RecipeNutritionProfile
from .profile_models import UserProfile, MealSlot, MealFrequency, get_meal_distribution
from .dietary_constraints import RecipeDietaryEvaluation, ConstraintResult


class MealPlanStatus(Enum):
    """Meal plan generation status."""
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"           # Some slots unfilled
    FAILED = "FAILED"             # Could not generate
    INFEASIBLE = "INFEASIBLE"     # Constraints impossible


@dataclass
class MealSlotPlan:
    """Plan for a single meal slot."""
    meal_slot: str
    recipe_id: Optional[int] = None
    recipe_name: str = ""
    servings: float = 1.0
    nutrients: Dict[str, float] = field(default_factory=dict)
    nutrition_completeness: float = 0.0
    dietary_evaluation: Optional[Dict] = None
    recommendation_score: float = 0.0
    explanation: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "meal_slot": self.meal_slot,
            "recipe_id": self.recipe_id,
            "recipe_name": self.recipe_name,
            "servings": self.servings,
            "nutrients": {k: round(v, 2) for k, v in self.nutrients.items()},
            "nutrition_completeness": round(self.nutrition_completeness, 3),
            "dietary_evaluation": self.dietary_evaluation,
            "recommendation_score": round(self.recommendation_score, 3),
            "explanation": self.explanation,
        }


@dataclass
class DailyMealPlan:
    """Meal plan for a single day."""
    date: str
    slots: Dict[str, MealSlotPlan] = field(default_factory=dict)
    total_nutrients: Dict[str, float] = field(default_factory=dict)
    target_nutrients: Dict[str, float] = field(default_factory=dict)
    nutrient_achievement: Dict[str, float] = field(default_factory=dict)  # actual/target
    status: str = "COMPLETE"
    notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "date": self.date,
            "slots": {k: v.to_dict() for k, v in self.slots.items()},
            "total_nutrients": {k: round(v, 2) for k, v in self.total_nutrients.items()},
            "target_nutrients": {k: round(v, 2) for k, v in self.target_nutrients.items()},
            "nutrient_achievement": {k: round(v, 3) for k, v in self.nutrient_achievement.items()},
            "status": self.status,
            "notes": self.notes,
        }
    
    @property
    def is_complete(self) -> bool:
        return all(slot.recipe_id is not None for slot in self.slots.values())
    
    @property
    def filled_slots(self) -> int:
        return sum(1 for s in self.slots.values() if s.recipe_id is not None)


@dataclass
class WeeklyMealPlan:
    """Weekly meal plan."""
    start_date: str
    days: List[DailyMealPlan] = field(default_factory=list)
    weekly_totals: Dict[str, float] = field(default_factory=dict)
    weekly_targets: Dict[str, float] = field(default_factory=dict)
    weekly_achievement: Dict[str, float] = field(default_factory=dict)
    status: str = "SUCCESS"
    notes: List[str] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "start_date": self.start_date,
            "days": [day.to_dict() for day in self.days],
            "weekly_totals": {k: round(v, 2) for k, v in self.weekly_totals.items()},
            "weekly_targets": {k: round(v, 2) for k, v in self.weekly_targets.items()},
            "weekly_achievement": {k: round(v, 3) for k, v in self.weekly_achievement.items()},
            "status": self.status,
            "notes": self.notes,
            "generated_at": self.generated_at,
        }
    
    @property
    def is_complete(self) -> bool:
        return all(day.is_complete for day in self.days)
    
    @property
    def completion_rate(self) -> float:
        if not self.days:
            return 0.0
        total_slots = sum(len(day.slots) for day in self.days)
        filled = sum(day.filled_slots for day in self.days)
        return filled / total_slots if total_slots > 0 else 0.0


@dataclass
class MealPlanConfig:
    """Configuration for meal plan generation."""
    # Meal planning
    days: int = 7
    meal_frequency: int = 4  # 3, 4, 5, or 6
    allow_recipe_repetition: bool = False
    max_recipe_repeats_per_week: int = 2
    
    # Nutritional targets
    daily_energy_tolerance_pct: float = 10.0  # +/- 10%
    protein_min_achievement: float = 0.9      # 90% of target
    nutrient_balance_weight: float = 0.3      # Weight for nutrient balance in scoring
    
    # Variety
    cuisine_diversity_weight: float = 0.2
    max_same_cuisine_per_day: int = 2
    max_same_cuisine_per_week: int = 4
    require_cuisine_variety: bool = True
    
    # Constraints
    max_prep_time_min: Optional[int] = None
    max_cook_time_min: Optional[int] = None
    max_total_time_min: Optional[int] = None
    budget_tier: Optional[str] = None  # "LOW", "MEDIUM", "HIGH"
    
    # Meal slot config
    meal_slots: List[str] = field(default_factory=lambda: [
        "BREAKFAST", "LUNCH", "DINNER"
    ])
    meal_energy_distribution: Dict[str, float] = field(default_factory=dict)
    
    # Recipe selection
    min_nutrition_completeness: float = 0.0
    min_recommendation_score: float = 0.0
    prefer_nutrition_completeness: bool = True
    allow_unverified_dietary: bool = False
    
    # Repetition control
    track_recipe_history: bool = True
    max_consecutive_days_same_recipe: int = 1


class MealPlanner:
    """
    Generate personalized meal plans with nutritional validation.
    
    Integrates:
    - Personalized recommender for recipe selection
    - Nutrition targets for daily/weekly validation
    - Dietary constraint engine for safety
    - Variety and repetition controls
    """
    
    def __init__(
        self,
        personalized_recommender: Any,  # PersonalizedRecommender
        nutrition_targets: Any,  # CompleteNutritionTargets
        recipe_profile_collection: Any,  # RecipeProfileCollection
        config: Optional[MealPlanConfig] = None
    ):
        self.recommender = nutrition_targets  # Actually personalized recommender
        self.nutrition_targets = nutrition_targets
        self.recipe_collection = nutrition_targets  # Actually recipe collection
        self.config = config or MealPlanConfig()
        
        # State for repetition tracking
        self._recipe_history: Dict[int, List[str]] = {}  # recipe_id -> list of dates
        self._cuisine_counts: Dict[str, int] = {}
        self._daily_cuisine_counts: Dict[str, Dict[str, int]] = {}
    
    def generate_weekly_plan(
        self,
        user_profile: Any,  # UserProfile
        start_date: Optional[date] = None,
        nutrition_targets: Optional[Any] = None,
        config: Optional[MealPlanConfig] = None
    ) -> WeeklyMealPlan:
        """
        Generate a weekly meal plan.
        
        Args:
            user_profile: UserProfile with preferences
            start_date: Plan start date (default: today)
            nutrition_targets: CompleteNutritionTargets (uses instance if None)
            config: MealPlanConfig overrides
            
        Returns:
            WeeklyMealPlan
        """
        config = config or self.config
        targets = nutrition_targets or self.nutrition_targets
        start = start_date or date.today()
        
        # Reset tracking
        self._recipe_history.clear()
        self._cuisine_counts.clear()
        self._daily_cuisine_counts.clear()
        
        # Determine meal slots from user profile or config
        meal_slots = self._get_meal_slots(user_profile, config)
        
        # Get daily targets
        daily_targets = self._get_daily_targets(targets, config)
        
        # Generate each day
        days = []
        current_date = start
        
        for day_idx in range(config.days):
            date_str = current_date.isoformat()
            
            daily_plan = self._generate_daily_plan(
                user_profile=user_profile,
                date_str=date_str,
                meal_slots=config.meal_slots,
                daily_targets=daily_targets,
                config=config,
                day_index=day_idx
            )
            
            days.append(daily_plan)
            current_date += timedelta(days=1)
            
            # Update tracking
            self._update_tracking(daily_plan, date_str)
        
        # Calculate weekly totals
        weekly_plan = WeeklyMealPlan(
            start_date=start.isoformat(),
            days=days
        )
        self._calculate_weekly_totals(weekly_plan, targets, config)
        
        return weekly_plan
    
    def generate_daily_plan(
        self,
        user_profile: Any,
        date: date,
        nutrition_targets: Optional[Any] = None,
        config: Optional[MealPlanConfig] = None
    ) -> DailyMealPlan:
        """Generate a single day meal plan."""
        config = config or self.config
        targets = nutrition_targets or self.nutrition_targets
        date_str = date.isoformat()
        meal_slots = self._get_meal_slots(self.config, config)
        daily_targets = self._get_daily_targets(targets, config)
        
        return self._generate_daily_plan(
            user_profile=user_profile,
            date_str=date_str,
            meal_slots=config.meal_slots,
            daily_targets=daily_targets,
            config=config,
            day_index=0
        )
    
    def _get_meal_slots(self, user_profile: Any, config: MealPlanConfig) -> List[str]:
        """Get meal slots from user profile or config."""
        # Use config meal slots
        return config.meal_slots
    
    def _get_daily_targets(self, nutrition_targets: Any, config: MealPlanConfig) -> Dict[str, float]:
        """Get daily nutrient targets from nutrition targets."""
        if not nutrition_targets:
            return {}
        
        macros = nutrition_targets.macros
        return {
            "energy_kcal": macros.energy_kcal,
            "protein_g": macros.protein_g,
            "carbohydrate_g": macros.carbohydrate_g,
            "fat_g": macros.fat_g,
            "fibre_g": macros.fibre_g,
        }
    
    def _generate_daily_plan(
        self,
        user_profile: Any,
        date_str: str,
        meal_slots: List[str],
        daily_targets: Dict[str, float],
        config: MealPlanConfig,
        day_index: int
    ) -> DailyMealPlan:
        """Generate a single day's meal plan."""
        slots = {}
        remaining_targets = daily_targets.copy()
        
        # Determine meal energy distribution
        meal_distribution = self._get_meal_distribution(config, len(meal_slots))
        
        for slot in meal_slots:
            # Get target nutrients for this meal
            fraction = meal_distribution.get(slot, 1.0 / len(meal_slots))
            meal_targets = {k: v * fraction for k, v in daily_targets.items()}
            
            # Get recommendation for this meal
            rec = self._recommend_for_meal(
                meal_slot=slot,
                meal_targets=meal_targets,
                daily_context={"date": date_str, "slots_filled": list(slots.keys())},
                config=config
            )
            
            if rec:
                slot_plan = MealSlotPlan(
                    meal_slot=slot,
                    recipe_id=rec.recipe_id,
                    recipe_name=rec.recipe_name,
                    servings=1.0,  # Could be adjusted for energy matching
                    nutrients=rec.per_serving_nutrients or {},
                    nutrition_completeness=rec.nutrition_completeness or 0.0,
                    dietary_evaluation=rec.dietary_evaluation,
                    recommendation_score=rec.recommendation_score or 0.0,
                    explanation=rec.explanation or "",
                )
                
                # Deduct from remaining targets
                for k, v in rec.per_serving_nutrients.items():
                    if k in remaining_targets:
                        remaining_targets[k] = max(0, remaining_targets[k] - v)
                
                slots[slot] = slot_plan
            else:
                # No suitable recipe found
                slots[slot] = MealSlotPlan(meal_slot=slot)
        
        # Calculate totals
        total_nutrients = self._sum_slot_nutrients(slots)
        
        # Calculate achievement
        achievement = {}
        for k, target in daily_targets.items():
            actual = total_nutrients.get(k, 0)
            achievement[k] = round(actual / target, 3) if target > 0 else 1.0
        
        # Determine status
        status = "COMPLETE" if all(s.recipe_id is not None for s in slots.values()) else "PARTIAL"
        if not any(s.recipe_id is not None for s in slots.values()):
            status = "FAILED"
        
        notes = []
        if status == "PARTIAL":
            missing = [s for s in meal_slots if slots[s].recipe_id is None]
            notes.append(f"Unfilled slots: {', '.join(missing)}")
        
        return DailyMealPlan(
            date=date_str,
            slots=slots,
            total_nutrients=total_nutrients,
            target_nutrients=daily_targets,
            nutrient_achievement=achievement,
            status=status,
            notes=notes,
        )
    
    def _recommend_for_meal(
        self,
        meal_slot: str,
        meal_targets: Dict[str, float],
        daily_context: Dict,
        config: MealPlanConfig
    ) -> Optional[Any]:
        """Get recommendation for a specific meal slot."""
        # Build filters for meal slot
        filters = self._build_meal_filters(meal_slot, daily_context, config)
        
        # Create temporary nutrition targets for this meal
        from .nutrition_targets import MacroTargets
        meal_macros = MacroTargets(
            energy_kcal=meal_targets.get("energy_kcal", 0),
            protein_g=meal_targets.get("protein_g", 0),
            carbohydrate_g=meal_targets.get("carbohydrate_g", 0),
            fat_g=meal_targets.get("fat_g", 0),
            fibre_g=meal_targets.get("fibre_g", 0),
            protein_pct=0, carbohydrate_pct=0, fat_pct=0,
            method=None, equation_used=""
        )
        
        from .nutrition_targets import CompleteNutritionTargets
        meal_targets_obj = CompleteNutritionTargets(
            energy=None, macros=meal_macros, micros=None, meal_targets={}
        )
        
        # Get recommendations
        # This would use the personalized recommender
        # For now, return None - needs integration with recommender
        return None
    
    def _build_meal_filters(self, meal_slot: str, daily_context: Dict, config: MealPlanConfig) -> Dict:
        """Build filters for meal slot."""
        filters = {}
        
        # Course filter based on meal slot
        slot_courses = {
            "BREAKFAST": ["breakfast", "snack", "beverage"],
            "LUNCH": ["main course", "lunch", "rice", "bread", "curry", "dal"],
            "DINNER": ["main course", "dinner", "rice", "bread", "curry", "dal"],
            "MORNING_SNACK": ["snack", "beverage", "dessert"],
            "EVENING_SNACK": ["snack", "beverage", "dessert", "street food"],
        }
        if meal_slot in slot_courses:
            # Use first course as filter
            filters["course"] = slot_courses[meal_slot][0]
        
        # Exclude recently used recipes
        exclude_ids = set()
        for recipe_id, dates in self._recipe_history.items():
            if any(d >= (date.today() - timedelta(days=3)).isoformat() for d in dates):
                exclude_ids.add(recipe_id)
        if exclude_ids:
            filters["exclude_ids"] = list(exclude_ids)
        
        return filters
    
    def _get_meal_distribution(self, config: MealPlanConfig, num_slots: int) -> Dict[str, float]:
        """Get energy distribution for meal slots."""
        if config.meal_energy_distribution:
            return config.meal_energy_distribution
        
        # Default distributions
        if num_slots == 3:
            return {"BREAKFAST": 0.30, "LUNCH": 0.40, "DINNER": 0.30}
        elif num_slots == 4:
            return {"BREAKFAST": 0.25, "LUNCH": 0.35, "EVENING_SNACK": 0.15, "DINNER": 0.25}
        elif num_slots == 5:
            return {"BREAKFAST": 0.25, "MORNING_SNACK": 0.10, "LUNCH": 0.35, 
                    "EVENING_SNACK": 0.10, "DINNER": 0.20}
        return {}
    
    def _update_tracking(self, daily_plan: DailyMealPlan, date_str: str):
        """Update recipe history and cuisine counts."""
        for slot, slot_plan in daily_plan.slots.items():
            if slot_plan.recipe_id:
                rid = slot_plan.recipe_id
                if rid not in self._recipe_history:
                    self._recipe_history[rid] = []
                self._recipe_history[rid].append(date_str)
                
                # Update cuisine counts
                profile = self.recipe_collection.get(rid)
                if profile:
                    cuisine = profile.cuisine
                    self._cuisine_counts[cuisine] = self._cuisine_counts.get(cuisine, 0) + 1
                    if date_str not in self._daily_cuisine_counts:
                        self._daily_cuisine_counts[date_str] = {}
                    self._daily_cuisine_counts[date_str][cuisine] = \
                        self._daily_cuisine_counts[date_str].get(cuisine, 0) + 1
    
    def _sum_slot_nutrients(self, slots: Dict[str, MealSlotPlan]) -> Dict[str, float]:
        """Sum nutrients across all slots."""
        totals = {}
        for slot_plan in slots.values():
            for k, v in slot_plan.nutrients.items():
                totals[k] = totals.get(k, 0) + v
        return totals
    
    def _calculate_weekly_totals(self, weekly_plan: WeeklyMealPlan, targets: Any, config: MealPlanConfig):
        """Calculate weekly totals and achievements."""
        weekly_totals = {}
        for day in weekly_plan.days:
            for k, v in day.total_nutrients.items():
                weekly_totals[k] = weekly_totals.get(k, 0) + v
        
        weekly_targets = {}
        if targets and targets.macros:
            macros = targets.macros
            days = len(weekly_plan.days)
            weekly_targets = {
                "energy_kcal": macros.energy_kcal * days,
                "protein_g": macros.protein_g * days,
                "carbohydrate_g": macros.carbohydrate_g * days,
                "fat_g": macros.fat_g * days,
                "fibre_g": macros.fibre_g * days,
            }
        
        achievement = {}
        for k, target in weekly_targets.items():
            actual = weekly_totals.get(k, 0)
            achievement[k] = round(actual / target, 3) if target > 0 else 1.0
        
        weekly_plan.weekly_totals = weekly_totals
        weekly_plan.weekly_targets = weekly_targets
        weekly_plan.weekly_achievement = achievement
        
        # Overall status
        if all(day.status == "COMPLETE" for day in weekly_plan.days):
            weekly_plan.status = "SUCCESS"
        elif any(day.status == "FAILED" for day in weekly_plan.days):
            weekly_plan.status = "FAILED"
        else:
            weekly_plan.status = "PARTIAL"
        
        # Add notes
        for k, v in achievement.items():
            if v < 0.8:
                weekly_plan.notes.append(f"Weekly {k} achievement low: {v:.0%}")
            elif v > 1.3:
                weekly_plan.notes.append(f"Weekly {k} exceeded: {v:.0%}")


def create_meal_planner(
    personalized_recommender: Any,
    nutrition_targets: Any,
    recipe_collection: Any,
    config: Optional[MealPlanConfig] = None
) -> MealPlanner:
    """Factory function to create meal planner."""
    return MealPlanner(
        personalized_recommender=personalized_recommender,
        nutrition_targets=nutrition_targets,
        recipe_profile_collection=recipe_collection,
        config=config
    )