"""Meal plan service for generating and managing meal plans."""

from typing import Optional, List, Dict, Any
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.database.models import MealPlan, MealPlanItem, Recipe, MealPlanStatus, MealSlot
from app.database.session import get_db
from app.personalization.recommendation_service import RecommendationService
from app.personalization.nutrition_targets import CompleteNutritionTargets
from app.personalization.meal_planner import MealPlanner, MealPlanConfig
from app.personalization.meal_plan_optimizer import MealPlanOptimizer, OptimizationConfig
from app.database.session import get_db

class MealPlanService:
    """Service for meal plan generation and management."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_meal_plan(
        self,
        user_id: int,
        start_date: date,
        days: int = 7,
        meal_frequency: int = 4,
        name: str = None,
        nutrition_targets: Optional[object] = None,
    ) -> Optional[object]:
        """Create a new meal plan."""
        from app.personalization.meal_planner import MealPlanner, MealPlanConfig
        from app.personalization.personalized_recommender import create_personalized_recommender
        from app.personalization.recipe_profile import build_recipe_profiles
        from app.personalization.dietary_constraints import DietaryConstraintEngine
        from app.personalization.nutrition_targets import NutritionTargetCalculator
        from app.database.models import User, UserProfile
        
        # Get user profile
        from app.database.models import User, UserProfile
        db = get_db()
        user = db.query(User).filter(User.id == user_id).first()
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        if not user or not profile:
            return None
        
        # Build nutrition targets if not provided
        if nutrition_targets is None:
            from app.personalization.nutrition_targets import NutritionTargetCalculator
            calc = NutritionTargetCalculator()
            from app.profile_models import Anthropometrics, Sex, ActivityLevel, WeightGoal, MealFrequency
            anthro = Anthropometrics(
                height_cm=profile.height_cm,
                weight_kg=profile.weight_kg,
                age_years=profile.age_years,
                sex=profile.sex
            )
            nutrition_targets = NutritionTargetCalculator().calculate(
                anthropometrics=anthro,
                activity_level=profile.activity_level,
                weight_goal=profile.weight_goal,
                weight_change_kg_per_week=profile.weight_change_rate_kg_per_week
            )
        
        # Create meal plan
        plan = MealPlan(
            user_id=user_id,
            start_date=start_date,
            end_date=start_date + timedelta(days=days - 1),
            status="ACTIVE",
        )
        
        return plan
    
    def get_meal_plan(self, plan_id: int) -> Optional[object]:
        from app.database.models import MealPlan
        db = get_db()
        return db.query(MealPlan).filter(MealPlan.id == plan_id).first()
    
    def get_user_meal_plans(self, user_id: int, status: str = None) -> List[object]:
        from app.database.models import MealPlan
        db = get_db()
        query = db.query(MealPlan).filter(MealPlan.user_id == user_id)
        if status:
            query = query.filter(MealPlan.status == status)
        return query.order_by(MealPlan.created_at.desc()).all()
    
    def update_meal_plan(self, plan_id: int, updates: dict) -> bool:
        from app.database.models import MealPlan
        db = get_db()
        plan = db.query(MealPlan).filter(MealPlan.id == plan_id).first()
        if not plan:
            return False
        for key, value in updates.items():
            if hasattr(plan, key):
                setattr(plan, key, value)
        db.commit()
        return True
    
    def delete_meal_plan(self, plan_id: int) -> bool:
        from app.database.models import MealPlan
        db = get_db()
        plan = db.query(MealPlan).filter(MealPlan.id == plan_id).first()
        if not plan:
            return False
        db.delete(plan)
        db.commit()
        return True
    
    def add_meal_item(self, plan_id: int, day_index: int, meal_slot: str, recipe_id: int, servings: float = 1.0) -> bool:
        from app.database.models import MealPlanItem
        db = get_db()
        item = MealPlanItem(
            meal_plan_id=plan_id,
            day_index=day_index,
            meal_slot=meal_slot,
            recipe_id=recipe_id,
            servings=servings,
        )
        db.add(item)
        db.commit()
        return True
    
    def remove_meal_item(self, item_id: int) -> bool:
        from app.database.models import MealPlanItem
        db = get_db()
        item = db.query(MealPlanItem).filter(MealPlanItem.id == item_id).first()
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True
    
    def update_meal_item(self, item_id: int, updates: dict) -> bool:
        from app.database.models import MealPlanItem
        db = get_db()
        item = db.query(MealPlanItem).filter(MealPlanItem.id == item_id).first()
        if not item:
            return False
        for key, value in updates.items():
            if hasattr(item, key):
                setattr(item, key, value)
        db.commit()
        return True
    
    def complete_meal(self, item_id: int) -> bool:
        from app.database.models import MealPlanItem
        from datetime import datetime
        db = get_db()
        item = db.query(MealPlanItem).filter(MealPlanItem.id == item_id).first()
        if not item:
            return False
        item.is_completed = True
        item.completed_at = datetime.utcnow()
        db.commit()
        return True
    
    def get_daily_plan(self, plan_id: int, day_index: int) -> List[object]:
        from app.database.models import MealPlanItem
        db = get_db()
        return db.query(MealPlanItem).filter(
            MealPlanItem.meal_plan_id == plan_id,
            MealPlanItem.day_index == day_index
        ).order_by(MealPlanItem.meal_slot).all()
    
    def get_weekly_summary(self, plan_id: int) -> dict:
        from app.database.models import MealPlanItem, Recipe
        db = get_db()
        items = db.query(MealPlanItem).filter(
            MealPlanItem.meal_plan_id == plan_id
        ).all()
        
        total_slots = 0
        filled_slots = 0
        completed_slots = 0
        recipes_used = set()
        cuisines = set()
        
        for item in items:
            if item.recipe_id:
                filled_slots += 1
                recipes_used.add(item.recipe_id)
                recipe = db.query(Recipe).filter(Recipe.id == item.recipe_id).first()
                if recipe:
                    cuisines.add(recipe.cuisine)
                if item.is_completed:
                    completed_slots += 1
            total_slots = len([i for i in items if i.recipe_id])  # Approximate
        
        return {
            "total_slots": total_slots,
            "filled_slots": filled_slots,
            "completed_slots": completed_slots,
            "unique_recipes": len(recipes_used),
            "cuisines": list(cuisines),
        }
    
    def get_daily_nutrition(self, plan_id: int, day_index: int) -> dict:
        """Get nutrition totals for a specific day."""
        from app.database.models import MealPlanItem, Recipe
        db = get_db()
        
        items = db.query(MealPlanItem).filter(
            MealPlanItem.meal_plan_id == plan_id,
            MealPlanItem.day_index == day_index
        ).all()
        
        totals = {}
        for item in items:
            if item.recipe_id and item.per_serving_nutrients:
                for nutrient, value in item.per_serving_nutrients.items():
                    totals[nutrient] = totals.get(nutrient, 0) + value * item.servings
        
        return totals