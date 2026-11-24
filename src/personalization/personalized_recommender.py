"""Personalized Recommender - Integrates Phase 5 content-based recommender with Phase 4 personalization."""

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import pandas as pd
import numpy as np

from ..recommendation import (
    ContentBasedRecipeRecommender, RecipePreprocessor,
    get_recipe_ingredient_mapping, get_recipe_metadata_mapping,
    PipelineConfig, RecommendationResult
)
from .recipe_profile import RecipeProfileBuilder, RecipeProfileCollection, RecipeNutritionProfile
from .dietary_constraints import (
    DietaryConstraintEngine, RecipeDietaryEvaluation, ConstraintResult
)
from .nutrition_targets import CompleteNutritionTargets, MacroTargets
from .profile_models import UserProfile, MealSlot


class RecommendationFilter(Enum):
    """Filter types for personalized recommendations."""
    DIETARY = "DIETARY"                    # Hard dietary constraints
    NUTRITIONAL = "NUTRITIONAL"            # Nutritional target matching
    PREFERENCE = "PREFERENCE"              # Cuisine, ingredient preferences
    MEAL_SLOT = "MEAL_SLOT"                # Meal-type appropriateness
    NUTRITION_COMPLETENESS = "NUTRITION_COMPLETENESS"  # Filter by nutrition data availability


@dataclass
class PersonalizedRecommendationResult:
    """Enhanced recommendation result with personalization details."""
    recipe_id: int
    recipe_name: str
    similarity_score: float
    cuisine: str
    course: str
    diet_labels: List[str]
    shared_ingredients: List[str]
    explanation: str
    component_scores: Dict[str, float] = field(default_factory=dict)
    
    # Personalization additions
    dietary_evaluation: Optional[Dict] = None
    nutrition_match_score: Optional[float] = None
    per_serving_nutrients: Optional[Dict[str, float]] = None
    nutrition_completeness: Optional[float] = None
    meets_nutritional_targets: Optional[Dict[str, bool]] = None
    personalization_notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "recipe_id": self.recipe_id,
            "recipe_name": self.recipe_name,
            "similarity_score": round(self.similarity_score, 4),
            "cuisine": self.cuisine,
            "course": self.course,
            "diet_labels": self.diet_labels,
            "shared_ingredients": self.shared_ingredients,
            "explanation": self.explanation,
            "component_scores": {k: round(v, 4) for k, v in self.component_scores.items()},
            "dietary_evaluation": self.dietary_evaluation,
            "nutrition_match_score": round(self.nutrition_match_score, 4) if self.nutrition_match_score else None,
            "per_serving_nutrients": {k: round(v, 2) for k, v in self.per_serving_nutrients.items()} if self.per_serving_nutrients else None,
            "nutrition_completeness": round(self.nutrition_completeness, 3) if self.nutrition_completeness else None,
            "meets_nutritional_targets": self.meets_nutritional_targets,
            "personalization_notes": self.personalization_notes,
        }


@dataclass
class PersonalizedRecommenderConfig:
    """Configuration for personalized recommender."""
    # Base recommender weights
    ingredient_weight: float = 0.4
    cuisine_weight: float = 0.3
    course_weight: float = 0.15
    diet_weight: float = 0.15
    
    # Personalization weights
    nutrition_match_weight: float = 0.2
    dietary_compliance_weight: float = 0.3
    preference_weight: float = 0.2
    diversity_weight: float = 0.1
    
    # Filters
    require_dietary_compliance: bool = True
    min_nutrition_completeness: float = 0.0  # 0 = no filter, 1 = complete only
    exclude_unverified_dietary: bool = True
    max_results: int = 10
    
    # Meal slot awareness
    meal_slot_aware: bool = True
    meal_slot_weights: Dict[str, float] = field(default_factory=lambda: {
        "BREAKFAST": 1.0,
        "LUNCH": 1.0,
        "DINNER": 1.0,
        "MORNING_SNACK": 0.8,
        "EVENING_SNACK": 0.8,
    })


class PersonalizedRecommender:
    """
    Personalized recipe recommender integrating:
    - Phase 5 content-based recommender (TF-IDF + metadata)
    - Phase 4 dietary constraints
    - Phase 4 nutrition targets
    - Phase 3 nutrition engine (for nutrition matching)
    """
    
    def __init__(
        self,
        base_recommender: ContentBasedRecipeRecommender,
        recipe_profile_collection: RecipeProfileCollection,
        dietary_engine: Optional[Any] = None,
        config: Optional[PersonalizedRecommenderConfig] = None
    ):
        self.base_recommender = base_recommender
        self.profile_collection = recipe_profile_collection
        self.dietary_engine = dietary_engine
        self.config = config or PersonalizedRecommenderConfig()
    
    def recommend(
        self,
        user_profile: Any,  # UserProfile
        nutrition_targets: Optional[Any] = None,  # CompleteNutritionTargets
        query_recipe_id: Optional[int] = None,
        query_ingredients: Optional[List[str]] = None,
        meal_slot: Optional[str] = None,
        k: int = 10,
        filters: Optional[Dict] = None
    ) -> List[PersonalizedRecommendationResult]:
        """
        Generate personalized recommendations.
        
        Args:
            user_profile: UserProfile with preferences, allergies, etc.
            nutrition_targets: CompleteNutritionTargets for nutritional matching
            query_recipe_id: Recipe ID for similar-recipe recommendations
            query_ingredients: Ingredient list for ingredient-based recommendations
            meal_slot: MealSlot for meal-aware recommendations
            k: Number of recommendations
            filters: Additional filters (cuisine, course, etc.)
            
        Returns:
            List of PersonalizedRecommendationResult
        """
        # Get base recommendations
        if query_ingredients:
            base_recs = self.base_recommender.recommend_by_ingredients(
                ingredients=query_ingredients,
                k=k * 3,  # Get more for filtering
                filters=filters
            )
        elif query_recipe_id:
            base_recs = self.base_recommender.recommend(
                query_recipe_id=query_recipe_id,
                k=k * 3,
                filters=filters
            )
        else:
            # No query - return diverse popular recipes
            base_recs = self._get_diverse_recommendations(k * 3, filters)
        
        # Apply personalization
        personalized = self._apply_personalization(
            base_recs, user_profile, nutrition_targets, meal_slot
        )
        
        # Sort by combined score
        personalized.sort(key=lambda x: self._combined_score(x), reverse=True)
        
        return personalized[:k]
    
    def recommend_for_meal_slot(
        self,
        user_profile: Any,
        nutrition_targets: Any,
        meal_slot: str,
        k: int = 5
    ) -> List[PersonalizedRecommendationResult]:
        """Get recommendations for a specific meal slot."""
        # Get target nutrients for this meal
        meal_targets = nutrition_targets.meal_targets.get(meal_slot, {})
        
        # Filter recipes by course appropriateness
        slot_courses = self._get_courses_for_slot(meal_slot)
        
        # Generate recommendations
        all_recs = []
        for course in slot_courses:
            recs = self.recommend(
                user_profile=user_profile,
                nutrition_targets=nutrition_targets,
                meal_slot=meal_slot,
                k=10,
                filters={"course": course} if course else None
            )
            all_recs.extend(recs)
        
        # Deduplicate and sort
        seen = set()
        unique_recs = []
        for rec in all_recs:
            if rec.recipe_id not in seen:
                seen.add(rec.recipe_id)
                unique_recs.append(rec)
        
        unique_recs.sort(key=lambda x: self._combined_score(x), reverse=True)
        return unique_recs[:k]
    
    def _get_diverse_recommendations(self, k: int, filters: Optional[Dict]) -> List[Dict]:
        """Get diverse recommendations when no query is provided."""
        # Sample from different cuisines/courses
        recipes = []
        for recipe_id, profile in self.profile_collection.profiles.items():
            if self._passes_filters(profile, filters):
                recipes.append({
                    "recipe_id": profile.recipe_id,
                    "recipe_name": profile.recipe_name,
                    "similarity_score": 0.5,  # Neutral score
                    "cuisine": profile.cuisine,
                    "course": profile.course,
                    "diet_labels": profile.diet_labels,
                    "shared_ingredients": [],
                    "explanation": "Diverse recommendation",
                    "component_scores": {},
                })
        
        # Sort by cuisine diversity
        recipes.sort(key=lambda x: x["recipe_id"])
        return recipes[:k]
    
    def _apply_personalization(
        self,
        base_recs: List[Dict],
        user_profile: Any,
        nutrition_targets: Optional[Any],
        meal_slot: Optional[str]
    ) -> List[PersonalizedRecommendationResult]:
        """Apply personalization filters and scoring to base recommendations."""
        results = []
        
        for rec in base_recs:
            recipe_id = rec["recipe_id"]
            profile = self.profile_collection.get(recipe_id)
            if profile is None:
                continue
            
            # Create personalized result
            personalized = PersonalizedRecommendationResult(
                recipe_id=recipe_id,
                recipe_name=rec["recipe_name"],
                similarity_score=rec["similarity_score"],
                cuisine=rec["cuisine"],
                course=rec["course"],
                diet_labels=rec["diet_labels"],
                shared_ingredients=rec["shared_ingredients"],
                explanation=rec["explanation"],
                component_scores=rec.get("component_scores", {}),
            )
            
            # 1. Dietary constraint evaluation
            if self.config.require_dietary_compliance:
                dietary_eval = self._evaluate_dietary(profile, user_profile)
                personalized.dietary_evaluation = dietary_eval.to_dict()
                
                if dietary_eval.overall_result == ConstraintResult.FAIL:
                    continue  # Hard filter out
                if dietary_eval.overall_result == ConstraintResult.UNVERIFIED and self.config.exclude_unverified_dietary:
                    continue  # Filter out unverified
            
            # 2. Nutrition completeness filter
            if self.config.min_nutrition_completeness > 0:
                if profile.nutrition_status.value == "UNAVAILABLE":
                    continue
                completeness = max(profile.nutrient_completeness.values()) if profile.nutrient_completeness else 0
                if completeness < self.config.min_nutrition_completeness:
                    continue
                personalized.nutrition_completeness = completeness
            
            # 3. Nutrition matching
            if nutrition_targets:
                personalized.per_serving_nutrients = profile.per_serving_nutrients
                personalized.nutrition_match_score = self._calculate_nutrition_match(
                    profile, nutrition_targets
                )
                personalized.meets_nutritional_targets = self._check_targets(profile, nutrition_targets)
            
            # 4. Meal slot appropriateness
            if meal_slot and self.config.meal_slot_aware:
                meal_score = self._meal_slot_score(profile, meal_slot)
                personalized.component_scores["meal_slot"] = meal_score
            
            # 5. Preference matching
            pref_score = self._preference_match_score(profile, user_profile)
            personalized.component_scores["preference"] = pref_score
            
            results.append(personalized)
        
        return results
    
    def _evaluate_dietary(self, profile: RecipeNutritionProfile, user_profile: Any) -> RecipeDietaryEvaluation:
        """Evaluate recipe against user dietary constraints."""
        if self.profile_collection is None:
            return RecipeDietaryEvaluation(recipe_id=0, recipe_name="", overall_result=ConstraintResult.UNVERIFIED)
        
        # Use dietary engine from profile collection builder
        # This is a placeholder - in real implementation, use the dietary engine
        from .dietary_constraints import RecipeDietaryEvaluation, ConstraintResult, ConstraintEvaluation
        
        # Get user dietary constraints
        preference = getattr(user_profile, 'dietary_profile', None)
        if preference:
            pref_value = preference.preference.value
        else:
            pref_value = "OMNIVORE"
        
        allergies = getattr(preference, 'allergies', []) if preference else []
        exclusions = getattr(preference, 'ingredient_exclusions', []) if preference else []
        
        # Simple evaluation based on profile's diet classification
        diet_type = profile.diet_classification.get("diet_type", "UNKNOWN")
        
        # Map preference to allowed types
        pref_map = {
            "VEGAN": ["VEGAN"],
            "VEGETARIAN": ["VEGAN", "VEGETARIAN"],
            "EGGETARIAN": ["VEGAN", "VEGETARIAN", "EGGETARIAN"],
            "NON_VEGETARIAN": ["VEGAN", "VEGETARIAN", "EGGETARIAN", "NON_VEGETARIAN"],
        }
        allowed = pref_map.get(pref_value.upper(), ["VEGAN", "VEGETARIAN", "EGGETARIAN", "NON_VEGETARIAN"])
        
        if diet_type in allowed:
            overall = ConstraintResult.PASS
        else:
            overall = ConstraintResult.FAIL
        
        return RecipeDietaryEvaluation(
            recipe_id=profile.recipe_id,
            recipe_name=profile.recipe_name,
            overall_result=overall,
            evaluations=[],
        )
    
    def _calculate_nutrition_match(
        self,
        profile: RecipeNutritionProfile,
        nutrition_targets: Any
    ) -> float:
        """Calculate how well recipe matches nutrition targets."""
        if not profile.per_serving_nutrients:
            return 0.0
        
        targets = nutrition_targets.macros
        score = 0.0
        count = 0
        
        # Energy match
        if profile.energy_kcal and targets.energy_kcal:
            diff = abs(profile.energy_kcal - targets.energy_kcal) / targets.energy_kcal
            score += max(0, 1 - diff)
            count += 1
        
        # Protein match
        if profile.protein_g and targets.protein_g:
            diff = abs(profile.protein_g - targets.protein_g) / targets.protein_g
            score += max(0, 1 - diff)
            count += 1
        
        # Carb match
        if profile.carb_g and targets.carbohydrate_g:
            diff = abs(profile.carb_g - targets.carbohydrate_g) / targets.carbohydrate_g
            score += max(0, 1 - diff)
            count += 1
        
        # Fat match
        if profile.fat_g and targets.fat_g:
            diff = abs(profile.fat_g - targets.fat_g) / targets.fat_g
            score += max(0, 1 - diff)
            count += 1
        
        return round(score / count, 3) if count > 0 else 0.0
    
    def _check_targets(self, profile: RecipeNutritionProfile, nutrition_targets: Any) -> Dict[str, bool]:
        """Check which nutritional targets are met."""
        if not profile.per_serving_nutrients:
            return {}
        
        targets = nutrition_targets.macros
        results = {}
        
        for nutrient, target in [
            ("energy", profile.energy_kcal, getattr(targets, 'energy_kcal', None)),
            ("protein", profile.protein_g, getattr(targets, 'protein_g', None)),
            ("carb", profile.carb_g, getattr(targets, 'carbohydrate_g', None)),
            ("fat", profile.fat_g, getattr(targets, 'fat_g', None)),
        ]:
            name, actual, target = nutrient
            if actual is not None and target is not None and target > 0:
                diff = abs(actual - target) / target
                results[f"meets_{name}"] = diff <= 0.2  # Within 20%
            else:
                results[f"meets_{name}"] = False
        
        return results
    
    def _meal_slot_score(self, profile: RecipeNutritionProfile, meal_slot: str) -> float:
        """Score recipe appropriateness for meal slot."""
        # Simple course-based scoring
        slot_courses = self._get_courses_for_slot(meal_slot)
        if profile.course in slot_courses:
            return 1.0
        return 0.3
    
    def _get_courses_for_slot(self, meal_slot: str) -> List[str]:
        """Get appropriate courses for a meal slot."""
        slot_courses = {
            "BREAKFAST": ["breakfast", "snack", "beverage"],
            "MORNING_SNACK": ["snack", "beverage", "dessert"],
            "LUNCH": ["main course", "lunch", "rice", "bread", "curry", "dal"],
            "EVENING_SNACK": ["snack", "beverage", "dessert", "street food"],
            "DINNER": ["main course", "dinner", "rice", "bread", "curry", "dal"],
        }
        return slot_courses.get(meal_slot.upper(), [])
    
    def _preference_match_score(self, profile: RecipeNutritionProfile, user_profile: Any) -> float:
        """Calculate preference match score."""
        score = 0.0
        count = 0
        
        # Cuisine preference
        if hasattr(user_profile, 'dietary_profile') and user_profile.dietary_profile:
            prefs = user_profile.dietary_profile.cuisine_preferences
            if prefs and profile.cuisine in prefs:
                score += 1.0
            count += 1
        
        # Course preference (could be added)
        
        return score / count if count > 0 else 0.5
    
    def _passes_filters(self, profile: RecipeNutritionProfile, filters: Optional[Dict]) -> bool:
        if not filters:
            return True
        if "cuisine" in filters and profile.cuisine != filters["cuisine"]:
            return False
        if "course" in filters and profile.course != filters["course"]:
            return False
        if "diet_labels" in filters:
            required = set(filters["diet_labels"])
            if not required.issubset(set(profile.diet_labels)):
                return False
        return True
    
    def _combined_score(self, rec: PersonalizedRecommendationResult) -> float:
        """Calculate combined personalization score."""
        score = 0.0
        
        # Base similarity
        score += rec.similarity_score * 0.3
        
        # Nutrition match
        if rec.nutrition_match_score is not None:
            score += rec.nutrition_match_score * 0.25
        
        # Dietary compliance (binary but important)
        if rec.dietary_evaluation:
            if rec.dietary_evaluation.get("overall_result") == "PASS":
                score += 0.25
            else:
                score -= 1.0  # Heavy penalty for dietary violation
        
        # Meal slot
        if "meal_slot" in rec.component_scores:
            score += rec.component_scores["meal_slot"] * 0.1
        
        # Preference
        if "preference" in rec.component_scores:
            score += rec.component_scores["preference"] * 0.1
        
        return score


def create_personalized_recommender(
    recipe_profile_collection: RecipeProfileCollection,
    base_recommender: ContentBasedRecipeRecommender,
    dietary_engine: Optional[Any] = None,
    config: Optional[PersonalizedRecommenderConfig] = None
) -> PersonalizedRecommender:
    """Factory function to create personalized recommender."""
    return PersonalizedRecommender(
        base_recommender=base_recommender,
        recipe_profile_collection=recipe_profile_collection,
        dietary_engine=dietary_engine,
        config=config
    )