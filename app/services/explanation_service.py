"""Explanation service for generating traceable explanations."""

from typing import Optional, List, Dict, Any
from app.personalization.explanation_engine import (
    ExplanationEngine,
    ExplanationEngine as EE,
    ExplanationType,
    ExplanationSegment,
    RecommendationExplanation,
    MealPlanExplanation,
    generate_recommendation_explanation,
    generate_meal_plan_explanation,
)
from app.personalization.personalized_recommender import PersonalizedRecommendationResult
from app.personalization.meal_planner import WeeklyMealPlan, DailyMealPlan
from app.nutrition_targets import CompleteNutritionTargets
from app.personalization.recipe_profile import RecipeProfileCollection

class ExplanationService:
    """Service for generating explanations."""
    
    def __init__(self):
        self.engine = ExplanationEngine()
    
    def explain_recommendation(
        self,
        recommendation: Any,  # PersonalizedRecommendationResult
        user_profile=None,
        nutrition_targets=None,
    ) -> Dict:
        """Generate explanation for a recommendation."""
        explanation = self.engine.explain_recommendation(
            rec=recommendation,
            user_profile=user_profile,
            nutrition_targets=nutrition_targets,
        )
        return explanation.to_dict()
    
    def explain_meal_plan(
        self,
        plan,  # WeeklyMealPlan
        user_profile=None,
        nutrition_targets=None,
        recipe_collection=None,
    ) -> Dict:
        """Generate explanation for a meal plan."""
        explanation = self.engine.explain_meal_plan(
            plan=plan,
            user_profile=user_profile,
            nutrition_targets=nutrition_targets,
            recipe_collection=recipe_collection,
        )
        return explanation.to_dict()
    
    def generate_recommendation_explanation_text(self, explanation: Dict) -> str:
        """Generate human-readable text explanation."""
        from app.personalization.explanation_engine import RecommendationExplanation
        rec_exp = RecommendationExplanation(**explanation)
        return rec_exp.to_text()
    
    def generate_meal_plan_explanation_text(self, explanation: Dict) -> str:
        """Generate human-readable meal plan explanation."""
        from app.personalization.explanation_engine import MealPlanExplanation
        mp_exp = MealPlanExplanation(**explanation)
        return mp_exp.to_text()
    
    def get_explanation_segments(self, explanation: Dict) -> List[Dict]:
        """Extract explanation segments."""
        return explanation.get("segments", [])
    
    def get_limitations(self, explanation: Dict) -> List[str]:
        """Get limitations from explanation."""
        return explanation.get("limitations", [])