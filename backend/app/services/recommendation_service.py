"""Recommendation service integrating with Phase 5 recommendation engine and Phase 4 personalization."""

from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.db.models import UserProfile, Recipe

# Import Phase 4/5 modules (ML packages live under src/)
from src.personalization.personalized_recommender import PersonalizedRecommender, PersonalizedRecommenderConfig
from src.personalization.dietary_constraints import DietaryConstraintEngine
from src.personalization.recipe_profile import build_recipe_profiles, RecipeProfileCollection
from src.recommendation import ContentBasedRecipeRecommender, create_recommender


class RecommendationService:
    """Service for generating personalized recommendations using Phase 4/5 engines."""

    def __init__(self, db: Session):
        self.db = db
        self._base_recommender = None
        self._recipe_profiles = None
        self._dietary_engine = DietaryConstraintEngine()
        self._initialized = False

    def _initialize(self):
        """Lazy initialization of recommendation engines."""
        if self._initialized:
            return

        # Load all recipes
        recipes = self.db.query(Recipe).all()
        if not recipes:
            self._initialized = True
            return

        def split_ingredients(raw: Optional[str]) -> List[str]:
            """The stored ingredient text uses commas (and sometimes newlines)."""
            if not raw:
                return []
            items: List[str] = []
            for line in raw.replace('\r', '\n').split('\n'):
                items.extend(part.strip() for part in line.split(',') if part.strip())
            return items

        # Build recipe ingredient mappings for TF-IDF
        recipe_ingredients = {}
        recipe_metadata = {}
        for recipe in recipes:
            recipe_ingredients[recipe.id] = split_ingredients(recipe.ingredients)
            recipe_metadata[recipe.id] = {
                'cuisine': recipe.cuisine,
                'course': recipe.course,
                'diet_labels': recipe.diet_labels.split('|') if recipe.diet_labels else [],
                'recipe_type': recipe.recipe_type,
                'total_time_min': recipe.total_time_min,
            }

        # Create base recommender (Phase 5 TF-IDF content-based model)
        self._base_recommender = create_recommender()
        self._base_recommender.fit(recipe_ingredients, recipe_metadata)

        # Phase 4 recipe profiles (nutrition-aware layer). Built from the frozen
        # recipe dataset; nutrition stays UNAVAILABLE while zero IFCT mappings
        # are approved, so profiles carry no invented nutrient values.
        self._recipe_profiles = build_recipe_profiles()

        self._initialized = True

    def get_recommendations(
        self,
        user_profile: UserProfile,
        meal_slot: Optional[str] = None,
        cuisine: Optional[str] = None,
        diet_labels: Optional[List[str]] = None,
        exclude_allergens: Optional[List[str]] = None,
        exclude_ingredients: Optional[List[str]] = None,
        max_prep_time: Optional[int] = None,
        max_cook_time: Optional[int] = None,
        k: int = 10,
    ) -> Dict[str, Any]:
        """Get personalized recommendations for a user."""
        self._initialize()

        if not self._base_recommender:
            return {
                "recommendations": [],
                "query_info": {
                    "profile_complete": False,
                    "nutrition_data_available": False,
                    "dietary_constraints_applied": [],
                }
            }

        from src.personalization.profile_models import (
            Anthropometrics,
            DietaryPreference,
            DietaryProfile,
            Sex,
            UserProfile as Phase4UserProfile,
        )

        def enum_or(enum_cls, value, default):
            try:
                return enum_cls(value)
            except (ValueError, TypeError):
                return default

        # Merge request-level constraints into the stored profile.
        allergies = list(user_profile.allergies or [])
        exclusions = list(user_profile.ingredient_exclusions or [])
        if exclude_allergens:
            allergies = sorted(set(allergies + list(exclude_allergens)))
        if exclude_ingredients:
            exclusions = sorted(set(exclusions + list(exclude_ingredients)))

        dietary = DietaryProfile(
            preference=enum_or(
                DietaryPreference, user_profile.dietary_preference, DietaryPreference.NON_VEGETARIAN
            ),
            allergies=allergies,
            ingredient_exclusions=exclusions,
            cuisine_preferences=list(user_profile.cuisine_preferences or []),
            cuisine_exclusions=list(user_profile.cuisine_exclusions or []),
            disliked_ingredients=list(user_profile.disliked_ingredients or []),
            religious_restrictions=list(user_profile.religious_restrictions or []),
            medical_conditions=list(user_profile.medical_conditions or []),
        )

        phase4_profile = Phase4UserProfile(
            user_id=user_profile.user_id,
            anthropometrics=Anthropometrics(
                height_cm=user_profile.height_cm,
                weight_kg=user_profile.weight_kg,
                age_years=user_profile.age_years,
                sex=enum_or(Sex, user_profile.sex, Sex.MALE),
            ),
            dietary_profile=dietary,
        )

        # Create personalized recommender (hard dietary constraints enforced)
        config = PersonalizedRecommenderConfig(
            require_dietary_compliance=True,
            nutrition_match_weight=0.3,
        )
        personalized_recommender = PersonalizedRecommender(
            base_recommender=self._base_recommender,
            recipe_profile_collection=self._recipe_profiles,
            dietary_engine=self._dietary_engine,
            config=config,
        )

        filters: Dict[str, Any] = {}
        if cuisine:
            filters['cuisine'] = cuisine
        if diet_labels:
            filters['diet_labels'] = diet_labels
        if max_prep_time is not None:
            filters['max_prep_time'] = max_prep_time
        if max_cook_time is not None:
            filters['max_cook_time'] = max_cook_time

        # Get recommendations
        try:
            recommendations = personalized_recommender.recommend(
                user_profile=phase4_profile,
                meal_slot=meal_slot,
                k=k,
                filters=filters or None,
            )

            # Format results
            results = []
            for rec in recommendations:
                recipe = self.db.query(Recipe).filter(Recipe.id == rec.recipe_id).first()
                if recipe:
                    results.append({
                        "recipe_id": rec.recipe_id,
                        # Phase 4/5 expose similarity_score, not a single blended score.
                        "score": round(float(rec.similarity_score or 0.0), 4),
                        "explanation": rec.explanation,
                        "component_scores": rec.component_scores or {},
                        "shared_ingredients": rec.shared_ingredients or [],
                    })

            # Get applied constraints
            constraints_applied = []
            if user_profile.dietary_preference:
                constraints_applied.append(f"Dietary: {user_profile.dietary_preference}")
            if user_profile.allergies:
                constraints_applied.append(f"Allergens: {', '.join(user_profile.allergies)}")
            if user_profile.religious_restrictions:
                constraints_applied.append(f"Religious: {', '.join(user_profile.religious_restrictions)}")
            if exclude_allergens:
                constraints_applied.append(f"Excluded allergens: {', '.join(exclude_allergens)}")
            if exclude_ingredients:
                constraints_applied.append(f"Excluded ingredients: {', '.join(exclude_ingredients)}")
            if diet_labels:
                constraints_applied.append(f"Diet labels: {', '.join(diet_labels)}")

            return {
                "recommendations": results,
                "query_info": {
                    "profile_complete": all([
                        user_profile.age_years,
                        user_profile.sex,
                        user_profile.height_cm,
                        user_profile.weight_kg,
                        user_profile.activity_level,
                    ]),
                    "nutrition_data_available": False,  # No approved mappings
                    "dietary_constraints_applied": constraints_applied,
                }
            }

        except Exception as e:
            # Fallback to base recommender
            return self._fallback_recommendations(
                user_profile, meal_slot, cuisine, diet_labels,
                exclude_allergens, exclude_ingredients,
                max_prep_time, max_cook_time, k
            )

    def _fallback_recommendations(
        self,
        user_profile: UserProfile,
        meal_slot: Optional[str],
        cuisine: Optional[str],
        diet_labels: Optional[List[str]],
        exclude_allergens: Optional[List[str]],
        exclude_ingredients: Optional[List[str]],
        max_prep_time: Optional[int],
        max_cook_time: Optional[int],
        k: int,
    ) -> Dict[str, Any]:
        """Fallback to base content-based recommender."""
        filters = {}
        if cuisine:
            filters['cuisine'] = cuisine
        if diet_labels:
            filters['diet_labels'] = diet_labels
        if meal_slot:
            # Map meal slot to course
            course_map = {
                'BREAKFAST': 'Breakfast',
                'LUNCH': 'Lunch',
                'DINNER': 'Dinner',
            }
            if meal_slot in course_map:
                filters['course'] = course_map[meal_slot]

        # Use base recommender with a dummy query (first recipe)
        recipes = self.db.query(Recipe).limit(1).all()
        if recipes:
            query_recipe_id = recipes[0].id
            results = self._base_recommender.recommend(query_recipe_id, k=k * 3, filters=filters)
            
            # Filter by dietary constraints manually
            filtered_results = []
            for rec in results:
                # The base recommender returns plain dicts.
                rec_id = rec["recipe_id"]
                recipe = self.db.query(Recipe).filter(Recipe.id == rec_id).first()
                if recipe and self._passes_constraints(recipe, user_profile, exclude_allergens, exclude_ingredients, max_prep_time, max_cook_time):
                    filtered_results.append({
                        "recipe_id": rec_id,
                        "score": round(float(rec.get("similarity_score") or 0.0), 4),
                        "explanation": rec.get("explanation", ""),
                        "component_scores": rec.get("component_scores", {}),
                        "shared_ingredients": rec.get("shared_ingredients", []),
                    })
                    if len(filtered_results) >= k:
                        break

            return {
                "recommendations": filtered_results,
                "query_info": {
                    "profile_complete": False,
                    "nutrition_data_available": False,
                    "dietary_constraints_applied": ["Content-based similarity (fallback)"],
                }
            }

        return {
            "recommendations": [],
            "query_info": {
                "profile_complete": False,
                "nutrition_data_available": False,
                "dietary_constraints_applied": [],
            }
        }

    def _passes_constraints(
        self,
        recipe: Recipe,
        user_profile: UserProfile,
        exclude_allergens: Optional[List[str]],
        exclude_ingredients: Optional[List[str]],
        max_prep_time: Optional[int],
        max_cook_time: Optional[int],
    ) -> bool:
        """Check if recipe passes hard dietary constraints."""
        # Check recipe type matches dietary preference
        if user_profile.dietary_preference == "VEGETARIAN" and recipe.recipe_type != "veg":
            return False
        if user_profile.dietary_preference == "VEGAN" and recipe.recipe_type not in ["veg", "vegan"]:
            return False
        if user_profile.dietary_preference == "EGGETARIAN" and recipe.recipe_type not in ["veg", "eggetarian"]:
            return False

        # Check allergens
        all_allergens = set(user_profile.allergies or [])
        if exclude_allergens:
            all_allergens.update(exclude_allergens)
        if all_allergens:
            recipe_ingredients = set(i.lower().strip() for i in recipe.ingredients.split('\n') if i.strip())
            for allergen in all_allergens:
                if any(allergen.lower() in ing for ing in recipe_ingredients):
                    return False

        # Check ingredient exclusions
        all_exclusions = set(user_profile.ingredient_exclusions or [])
        if exclude_ingredients:
            all_exclusions.update(exclude_ingredients)
        if all_exclusions:
            recipe_ingredients = set(i.lower().strip() for i in recipe.ingredients.split('\n') if i.strip())
            for exclusion in all_exclusions:
                if any(exclusion.lower() in ing for ing in recipe_ingredients):
                    return False

        # Check time constraints
        if max_prep_time and recipe.prep_time_min > max_prep_time:
            return False
        if max_cook_time and recipe.cook_time_min > max_cook_time:
            return False

        # Check cuisine exclusions
        if user_profile.cuisine_exclusions and recipe.cuisine in user_profile.cuisine_exclusions:
            return False

        return True

    def get_similar_recipes(self, recipe_id: int, k: int = 10) -> Dict[str, Any]:
        """Get recipes similar to a given recipe."""
        self._initialize()

        if not self._base_recommender:
            return {"recommendations": [], "query_info": {}}

        try:
            results = self._base_recommender.recommend(recipe_id, k=k)
            formatted = []
            for rec in results:
                recipe = self.db.query(Recipe).filter(Recipe.id == rec.recipe_id).first()
                if recipe:
                    formatted.append({
                        "recipe_id": rec.recipe_id,
                        "score": rec.score,
                        "explanation": rec.explanation,
                        "component_scores": rec.component_scores,
                        "shared_ingredients": rec.shared_ingredients,
                    })
            return {
                "recommendations": formatted,
                "query_info": {"method": "content_based_similarity"}
            }
        except Exception:
            return {"recommendations": [], "query_info": {}}