"""Recommendation service for personalized recommendations."""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.recommendation import ContentBasedRecipeRecommender, create_recommender
from app.personalization.recipe_profile import build_recipe_profiles, RecipeProfileCollection
from app.personalization.personalized_recommender import (
    PersonalizedRecommender,
    PersonalizedRecommenderConfig,
    create_personalized_recommender,
)
from app.personalization.dietary_constraints import DietaryConstraintEngine
from app.personalization.nutrition_targets import NutritionTargetCalculator
from app.database.models import Recipe
from app.database.session import get_db
import pandas as pd

class RecommendationService:
    """Service for generating personalized recommendations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.recipe_collection = None
        self.base_recommender = None
        self.personalized_recommender = None
        self.dietary_engine = DietaryConstraintEngine()
        self.nutrition_calculator = None
        self._initialized = False
    
    def initialize(self, nutrition_calculator=None):
        """Initialize the recommendation system."""
        if self._initialized:
            return
        
        # Load recipe data
        self._load_recipe_data()
        
        # Create base recommender (Phase 5)
        self.base_recommender = create_recommender()
        self.base_recommender.fit(
            recipe_ingredients=self.recipe_ingredients,
            recipe_metadata=self.recipe_metadata,
        )
        
        # Build recipe profiles with nutrition
        if nutrition_calculator:
            self.nutrition_calculator = nutrition_calculator
            builder = build_recipe_profiles(nutrition_calculator)
            self.recipe_collection = builder.build_all_profiles()
        else:
            # Build without nutrition
            self.recipe_collection = RecipeProfileCollection()
            for recipe_id in self.recipe_ids:
                # Build basic profile without nutrition
                pass
        
        # Create dietary engine
        self.dietary_engine = DietaryConstraintEngine()
        
        # Create personalized recommender
        config = PersonalizedRecommenderConfig(
            require_dietary_compliance=True,
            min_nutrition_completeness=0.0,
            exclude_unverified_dietary=True,
        )
        
        self.personalized_recommender = create_personalized_recommender(
            recipe_profile_collection=self.recipe_collection,
            base_recommender=self.base_recommender,
            dietary_engine=self.dietary_engine,
            config=PersonalizedRecommenderConfig()
        )
        
        self._initialized = True
    
    def _load_recipe_data(self):
        """Load recipe data for recommender."""
        # Get recipe ingredients
        self.recipe_ingredients = {}
        self.recipe_metadata = {}
        
        recipes = self.db.query(Recipe).all()
        for recipe in recipes:
            # Get ingredients from parsed data
            # For now, use the recipe's ingredients_en
            ingredients = []
            if recipe.ingredients_en:
                ingredients = [i.strip() for i in recipe.ingredients_en.split(',') if i.strip()]
            
            self.recipe_ingredients[recipe.recipe_id] = ingredients
            self.recipe_metadata[recipe.recipe_id] = {
                "recipe_name": recipe.recipe_name,
                "cuisine": recipe.cuisine,
                "course": recipe.course,
                "diet_labels": recipe.diet_labels,
                "prep_time_min": recipe.prep_time_min,
                "cook_time_min": recipe.cook_time_min,
                "total_time_min": recipe.total_time_min,
                "servings": recipe.servings,
            }
        
        self.recipe_ids = list(self.recipe_ingredients.keys())
    
    def get_recommendations(
        self,
        user_profile,
        nutrition_targets=None,
        query_recipe_id=None,
        query_ingredients=None,
        meal_slot=None,
        k=10,
        filters=None,
    ):
        """Get personalized recommendations."""
        if not self._initialized:
            self.initialize()
        
        # Ensure recommender is initialized
        if not self.personalized_recommender:
            self.initialize()
        
        # Get recommendations
        return self.personalized_recommender.recommend(
            user_profile=user_profile,
            nutrition_targets=nutrition_targets,
            query_recipe_id=query_recipe_id,
            query_ingredients=query_ingredients,
            meal_slot=meal_slot,
            k=k,
            filters=filters,
        )
    
    def recommend_by_ingredients(
        self,
        ingredients: List[str],
        k: int = 10,
        filters: Dict = None,
    ) -> List[Dict]:
        """Get recommendations based on ingredients."""
        if not self._initialized:
            self.initialize()
        
        # Use base recommender
        return self.base_recommender.recommend_by_ingredients(
            ingredients=ingredients,
            k=k,
            filters=filters,
        )
    
    def recommend_for_meal_slot(
        self,
        user_profile,
        nutrition_targets,
        meal_slot: str,
        k: int = 5,
    ):
        """Get recommendations for a specific meal slot."""
        if not self._initialized:
            self.initialize()
        
        return self.personalized_recommender.recommend_for_meal_slot(
            user_profile=user_profile,
            nutrition_targets=nutrition_targets,
            meal_slot=meal_slot,
            k=k,
        )
    
    def get_recipe_details(self, recipe_id: int) -> Optional[dict]:
        """Get detailed recipe information."""
        recipe = self.db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            return None
        
        return {
            "id": recipe.id,
            "recipe_id": recipe.recipe_id,
            "recipe_name": recipe.recipe_name,
            "cuisine": recipe.cuisine,
            "course": recipe.course,
            "diet_labels": recipe.diet_labels,
            "recipe_type": recipe.recipe_type,
            "prep_time_min": recipe.prep_time_min,
            "cook_time_min": recipe.cook_time_min,
            "total_time_min": recipe.total_time_min,
            "servings": recipe.servings,
            "ingredients_raw": recipe.ingredients_raw,
            "ingredients_en": recipe.ingredients_en,
            "instructions_raw": recipe.instructions_raw,
            "instructions_en": recipe.instructions_en,
            "nutrition_status": recipe.nutrition_status,
            "per_serving_nutrients": recipe.per_serving_nutrients,
            "nutrition_completeness": recipe.nutrient_completeness,
        }
    
    def get_recipe_candidates(
        self,
        filters: Dict = None,
        limit: int = 50,
    ) -> List[Dict]:
        """Get recipe candidates for recommendation."""
        from app.services.recipe_service import RecipeService
        
        recipe_service = RecipeService(get_db())
        recipes = recipe_service.search_recipes(
            cuisine=filters.get("cuisine") if filters else None,
            course=filters.get("course") if filters else None,
            diet_type=filters.get("diet_type") if filters else None,
            max_time=filters.get("max_time") if filters else None,
            limit=limit,
        )
        
        return [
            {
                "id": r.id,
                "recipe_id": r.recipe_id,
                "recipe_name": r.recipe_name,
                "cuisine": r.cuisine,
                "course": r.course,
                "diet_labels": r.diet_labels,
                "recipe_type": r.recipe_type,
                "total_time_min": r.total_time_min,
            }
            for r in recipes
        ]