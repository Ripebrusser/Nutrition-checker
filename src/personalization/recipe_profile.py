"""Recipe Profile - Unified recipe representation integrating Phase 2, 3, and 5 data."""

from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import pandas as pd
import numpy as np

from ..nutrition import (
    NutrientCalculator, RecipeAggregator, StrictMappingInterface,
    ApprovedMappingStore, IngredientWeightInfo, IngredientNutritionInput,
    RecipeNutritionOutput, MappingStatus, CalculationStatus, RecipeCalculationStatus,
    load_approved_mappings_from_jsonl
)
from ..recommendation import (
    RecipePreprocessor, ContentBasedRecipeRecommender,
    get_recipe_ingredient_mapping, get_recipe_metadata_mapping,
    RecipeFeatureExtractor, FeatureConfig
)
from ..personalization.dietary_constraints import (
    DietaryConstraintEngine, RecipeDietaryEvaluation, ConstraintResult
)
from ..personalization.profile_models import DietaryPreference


class NutritionCompleteness(Enum):
    """Recipe nutrition completeness status."""
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    UNAVAILABLE = "UNAVAILABLE"
    NO_MAPPED_INGREDIENTS = "NO_MAPPED_INGREDIENTS"


@dataclass
class RecipeNutritionProfile:
    """Nutrition profile for a single recipe."""
    recipe_id: int
    recipe_name: str
    cuisine: str
    course: str
    diet_labels: List[str]
    prep_time_min: int
    cook_time_min: int
    total_time_min: int
    servings: int
    
    # Ingredients
    ingredients: List[str] = field(default_factory=list)
    ingredient_count: int = 0
    
    # Nutrition (from Phase 3 engine)
    nutrition_status: NutritionCompleteness = NutritionCompleteness.UNAVAILABLE
    total_nutrients: Dict[str, float] = field(default_factory=dict)
    per_serving_nutrients: Dict[str, float] = field(default_factory=dict)
    nutrient_completeness: Dict[str, float] = field(default_factory=dict)
    mapping_coverage: float = 0.0
    weight_coverage: float = 0.0
    mapped_ingredient_count: int = 0
    total_ingredient_count: int = 0
    missing_nutrients: List[str] = field(default_factory=list)
    
    # Dietary classification
    diet_classification: Dict[str, Any] = field(default_factory=dict)
    
    # Provenance
    nutrition_provenance: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "recipe_id": self.recipe_id,
            "recipe_name": self.recipe_name,
            "cuisine": self.cuisine,
            "course": self.course,
            "diet_labels": self.diet_labels,
            "prep_time_min": self.prep_time_min,
            "cook_time_min": self.cook_time_min,
            "total_time_min": self.total_time_min,
            "servings": self.servings,
            "ingredients": self.ingredients,
            "ingredient_count": self.ingredient_count,
            "nutrition_status": self.nutrition_status.value,
            "total_nutrients": {k: round(v, 2) for k, v in self.total_nutrients.items()},
            "per_serving_nutrients": {k: round(v, 2) for k, v in self.per_serving_nutrients.items()},
            "nutrient_completeness": {k: round(v, 3) for k, v in self.nutrient_completeness.items()},
            "mapping_coverage": round(self.mapping_coverage, 3),
            "weight_coverage": round(self.weight_coverage, 3),
            "mapped_ingredient_count": self.mapped_ingredient_count,
            "total_ingredient_count": self.total_ingredient_count,
            "missing_nutrients": self.missing_nutrients,
            "diet_classification": self.diet_classification,
            "nutrition_provenance": self.nutrition_provenance,
        }
    
    @property
    def has_nutrition(self) -> bool:
        return self.nutrition_status in (NutritionCompleteness.COMPLETE, NutritionCompleteness.PARTIAL)
    
    @property
    def energy_kcal(self) -> Optional[float]:
        if "energy_kcal" in self.total_nutrients:
            return self.total_nutrients["energy_kcal"]
        if "energy_kj" in self.total_nutrients:
            return self.total_nutrients["energy_kj"] / 4.184
        return None
    
    @property
    def protein_g(self) -> Optional[float]:
        return self.total_nutrients.get("protein_g")
    
    @property
    def carb_g(self) -> Optional[float]:
        return self.total_nutrients.get("carb_available_g")
    
    @property
    def fat_g(self) -> Optional[float]:
        return self.total_nutrients.get("fat_g")
    
    @property
    def fibre_g(self) -> Optional[float]:
        return self.total_nutrients.get("fibre_total_g")


@dataclass
class RecipeProfileCollection:
    """Collection of recipe nutrition profiles with indexing."""
    profiles: Dict[int, RecipeNutritionProfile] = field(default_factory=dict)
    cuisine_index: Dict[str, Set[int]] = field(default_factory=lambda: defaultdict(set))
    course_index: Dict[str, Set[int]] = field(default_factory=lambda: defaultdict(set))
    diet_label_index: Dict[str, Set[int]] = field(default_factory=lambda: defaultdict(set))
    nutrition_status_index: Dict[NutritionCompleteness, Set[int]] = field(default_factory=lambda: defaultdict(set))
    
    def add(self, profile: RecipeNutritionProfile):
        self.profiles[profile.recipe_id] = profile
        self.cuisine_index[profile.cuisine].add(profile.recipe_id)
        self.course_index[profile.course].add(profile.recipe_id)
        for label in profile.diet_labels:
            self.diet_label_index[label].add(profile.recipe_id)
        self.nutrition_status_index[profile.nutrition_status].add(profile.recipe_id)
    
    def get(self, recipe_id: int) -> Optional[RecipeNutritionProfile]:
        return self.profiles.get(recipe_id)
    
    def get_by_cuisine(self, cuisine: str) -> List[RecipeNutritionProfile]:
        ids = self.cuisine_index.get(cuisine, set())
        return [self.profiles[rid] for rid in ids if rid in self.profiles]
    
    def get_by_course(self, course: str) -> List[RecipeNutritionProfile]:
        ids = self.course_index.get(course, set())
        return [self.profiles[rid] for rid in ids if rid in self.profiles]
    
    def get_by_diet_label(self, label: str) -> List[RecipeNutritionProfile]:
        ids = self.diet_label_index.get(label, set())
        return [self.profiles[rid] for rid in ids if rid in self.profiles]
    
    def get_by_nutrition_status(self, status: NutritionCompleteness) -> List[RecipeNutritionProfile]:
        ids = self.nutrition_status_index.get(status, set())
        return [self.profiles[rid] for rid in ids if rid in self.profiles]
    
    def filter(self, **criteria) -> List[RecipeNutritionProfile]:
        """Filter profiles by criteria."""
        results = list(self.profiles.values())
        
        if "cuisine" in criteria:
            results = [p for p in results if p.cuisine == criteria["cuisine"]]
        if "course" in criteria:
            results = [p for p in results if p.course == criteria["course"]]
        if "diet_labels" in criteria:
            required = set(criteria["diet_labels"])
            results = [p for p in results if required.issubset(set(p.diet_labels))]
        if "nutrition_status" in criteria:
            status = criteria["nutrition_status"]
            if isinstance(status, list):
                results = [p for p in results if p.nutrition_status in status]
            else:
                results = [p for p in results if p.nutrition_status == status]
        if "has_nutrition" in criteria:
            if criteria["has_nutrition"]:
                results = [p for p in results if p.has_nutrition]
            else:
                results = [p for p in results if not p.has_nutrition]
        if "max_prep_time" in criteria:
            results = [p for p in results if p.total_time_min <= criteria["max_prep_time"]]
        if "min_protein_g" in criteria:
            results = [p for p in results if p.protein_g is not None and p.protein_g >= criteria["min_protein_g"]]
        if "max_calories" in criteria:
            results = [p for p in results if p.energy_kcal is not None and p.energy_kcal <= criteria["max_calories"]]
        
        return results


class RecipeProfileBuilder:
    """
    Build unified recipe profiles integrating Phase 2, 3, and 5 data.
    
    This is the main integration class for Phase 4.
    """
    
    def __init__(
        self,
        nutrition_calculator: Optional[NutrientCalculator] = None,
        recipe_aggregator: Optional[RecipeAggregator] = None,
        mapping_interface: Optional[StrictMappingInterface] = None,
        dietary_engine: Optional[Any] = None,
        preprocessor: Optional[RecipePreprocessor] = None
    ):
        self.nutrition_calculator = nutrition_calculator
        self.recipe_aggregator = recipe_aggregator
        self.mapping_interface = mapping_interface
        self.dietary_engine = dietary_engine
        self.preprocessor = preprocessor or RecipePreprocessor()
        
        # Lazy-loaded data
        self._recipe_ingredients: Dict[int, List[str]] = {}
        self._recipe_metadata: Dict[int, Dict] = {}
        self._parsed_ingredients_df: Optional[pd.DataFrame] = None
        self._ifct_df: Optional[pd.DataFrame] = None
    
    def load_data(self):
        """Load all required data."""
        # Load recipe data
        self.preprocessor.load_data()
        self._recipe_ingredients = self.preprocessor.extract_recipe_ingredients()
        self._recipe_metadata = self.preprocessor.extract_recipe_metadata()
        
        # Load parsed ingredients for weight info
        self._parsed_ingredients_df = self.preprocessor._parsed_ingredients_df
        
        # Load IFCT data if nutrition calculator not provided
        if self.nutrition_calculator is None:
            self._ifct_df = pd.read_parquet("data/interim/ifct_final_candidate/ifct_table1_candidate.parquet")
            self.nutrition_calculator = NutrientCalculator(self._ifct_df)
        
        # Initialize mapping interface if not provided
        if self.mapping_interface is None:
            # Try to load approved mappings
            approved_store = ApprovedMappingStore()
            mapping_path = Path("data/processed/phase3/approved_mappings.jsonl")
            if mapping_path.exists():
                approved_store = load_approved_mappings_from_jsonl(mapping_path)
            self.mapping_interface = StrictMappingInterface(approved_store, self._ifct_df)
        
        # Initialize recipe aggregator if not provided
        if self.recipe_aggregator is None:
            from ..nutrition import EdiblePortionCalculator, AggregationConfig
            self.recipe_aggregator = RecipeAggregator(
                self.nutrition_calculator,
                self.mapping_interface,
                EdiblePortionCalculator(),
                AggregationConfig()
            )
        
        # Initialize dietary engine if not provided
        if self.dietary_engine is None:
            from .dietary_constraints import DietaryConstraintEngine
            self.dietary_engine = DietaryConstraintEngine()
    
    def build_recipe_profile(self, recipe_id: int) -> RecipeNutritionProfile:
        """Build complete nutrition profile for a single recipe."""
        # Get basic metadata
        metadata = self._recipe_metadata.get(recipe_id, {})
        ingredients = self._recipe_ingredients.get(recipe_id, [])
        
        profile = RecipeNutritionProfile(
            recipe_id=recipe_id,
            recipe_name=metadata.get("recipe_name", ""),
            cuisine=metadata.get("cuisine", ""),
            course=metadata.get("course", ""),
            diet_labels=metadata.get("diet_labels", []),
            prep_time_min=metadata.get("prep_time_min", 0),
            cook_time_min=metadata.get("cook_time_min", 0),
            total_time_min=metadata.get("total_time_min", 0),
            servings=metadata.get("servings", 4),
            ingredients=ingredients,
            ingredient_count=len(ingredients),
        )
        
        # Dietary classification
        if self.dietary_engine:
            profile.diet_classification = self.dietary_engine.classifier.classify_recipe(ingredients)
        
        # Calculate nutrition if aggregator available
        if self.recipe_aggregator and self._parsed_ingredients_df is not None:
            # Get weight infos for this recipe
            weight_infos = self._create_weight_infos_for_recipe(recipe_id)
            
            if weight_infos:
                nutrition_result = self.recipe_aggregator.aggregate_recipe(recipe_id, weight_infos)
                self._populate_nutrition(profile, nutrition_result)
        
        return profile
    
    def _create_weight_infos_for_recipe(self, recipe_id: int) -> List[IngredientWeightInfo]:
        """Create IngredientWeightInfo objects for a recipe from parsed data."""
        if self._parsed_ingredients_df is None:
            return []
        
        weight_infos = []
        parsed = self._parsed_ingredients_df[self._parsed_ingredients_df["recipe_id"] == recipe_id]
        
        for idx, row in parsed.iterrows():
            gram_weight = row.get("gram_weight")
            if pd.isna(gram_weight):
                gram_weight = None
            
            gram_min = row.get("gram_weight_min")
            if pd.isna(gram_min):
                gram_min = None
            
            gram_max = row.get("gram_weight_max")
            if pd.isna(gram_max):
                gram_max = None
            
            info = IngredientWeightInfo(
                recipe_id=int(row["recipe_id"]),
                ingredient_record_id=str(idx),
                original_ingredient=row["original_ingredient"],
                normalized_ingredient=row["normalized_ingredient"],
                quantity=row.get("quantity"),
                unit=row.get("unit"),
                gram_weight=gram_weight,
                gram_weight_min=gram_min,
                gram_weight_max=gram_max,
                conversion_status=row.get("conversion_status", "UNRESOLVED"),
                preparation_state=row.get("preparation", "NOT_SPECIFIED"),
            )
            weight_infos.append(info)
        
        return weight_infos
    
    def _populate_nutrition(self, profile: RecipeNutritionProfile, nutrition_result: RecipeNutritionOutput):
        """Populate profile with nutrition calculation results."""
        # Map calculation status
        status_map = {
            RecipeCalculationStatus.COMPLETE: NutritionCompleteness.COMPLETE,
            RecipeCalculationStatus.PARTIAL: NutritionCompleteness.PARTIAL,
            RecipeCalculationStatus.NO_MAPPED_INGREDIENTS: NutritionCompleteness.NO_MAPPED_INGREDIENTS,
            RecipeCalculationStatus.INSUFFICIENT_DATA: NutritionCompleteness.UNAVAILABLE,
            RecipeCalculationStatus.UNAVAILABLE: NutritionCompleteness.UNAVAILABLE,
        }
        
        profile.nutrition_status = status_map.get(nutrition_result.calculation_status, NutritionCompleteness.UNAVAILABLE)
        profile.total_nutrients = nutrition_result.total_nutrients.copy()
        profile.nutrient_completeness = nutrition_result.nutrient_completeness.copy()
        profile.mapping_coverage = nutrition_result.ingredient_mapping_coverage
        profile.weight_coverage = nutrition_result.gram_weight_coverage
        profile.mapped_ingredient_count = nutrition_result.mapped_ingredient_count
        profile.total_ingredient_count = nutrition_result.total_ingredient_count
        profile.nutrition_provenance = nutrition_result.provenance
        
        # Calculate per-serving nutrients
        if profile.servings > 0:
            profile.per_serving_nutrients = {
                k: round(v / profile.servings, 2) for k, v in profile.total_nutrients.items()
            }
        
        # Collect missing nutrients
        all_nutrients = set(profile.total_nutrients.keys())
        standard_nutrients = {"moisture_g", "protein_g", "ash_g", "fat_g", "fibre_total_g",
                              "fibre_insoluble_g", "fibre_soluble_g", "carb_available_g", "energy_kj"}
        profile.missing_nutrients = sorted(standard_nutrients - all_nutrients)
    
    def build_all_profiles(self, recipe_ids: Optional[List[int]] = None) -> RecipeProfileCollection:
        """Build profiles for all recipes (or specified subset)."""
        if not self._recipe_ingredients:
            self.load_data()
        
        if recipe_ids is None:
            recipe_ids = list(self._recipe_ingredients.keys())
        
        collection = RecipeProfileCollection()
        for recipe_id in recipe_ids:
            try:
                profile = self.build_recipe_profile(recipe_id)
                collection.add(profile)
            except Exception as e:
                print(f"Error building profile for recipe {recipe_id}: {e}")
        
        return collection
    
    def get_recipe_features_for_recommendation(self, recipe_ids: List[int]) -> Dict:
        """
        Get recipe features formatted for Phase 5 recommendation pipeline.
        
        Returns dict with ingredient lists and metadata for recommender.
        """
        recipe_ingredients = {}
        recipe_metadata = {}
        
        for rid in recipe_ids:
            if rid in self._recipe_ingredients:
                recipe_ingredients[rid] = self._recipe_ingredients[rid]
            if rid in self._recipe_metadata:
                recipe_metadata[rid] = self._recipe_metadata[rid]
        
        return {
            "recipe_ingredients": recipe_ingredients,
            "recipe_metadata": recipe_metadata,
        }
    
    def evaluate_recipe_dietary(
        self,
        recipe_id: int,
        user_preference: str = "OMNIVORE",
        user_allergies: Optional[List[str]] = None,
        user_exclusions: Optional[List[str]] = None
    ) -> RecipeDietaryEvaluation:
        """Evaluate a recipe against user dietary constraints."""
        ingredients = self._recipe_ingredients.get(recipe_id, [])
        metadata = self._recipe_metadata.get(recipe_id, {})
        
        if self.dietary_engine:
            return self.dietary_engine.evaluate_recipe(
                recipe_id=recipe_id,
                recipe_name=metadata.get("recipe_name", ""),
                ingredients=ingredients,
                user_preference=user_preference,
                user_allergies=user_allergies,
                user_exclusions=user_exclusions
            )
        return RecipeDietaryEvaluation(recipe_id=recipe_id, recipe_name="", overall_result=ConstraintResult.UNVERIFIED)


def build_recipe_profiles(
    recipe_ids: Optional[List[int]] = None,
    nutrition_calculator: Optional[NutrientCalculator] = None
) -> RecipeProfileCollection:
    """
    Convenience function to build recipe profiles.
    
    This is the main entry point for Phase 4 recipe integration.
    """
    builder = RecipeProfileBuilder(nutrition_calculator=nutrition_calculator)
    return builder.build_all_profiles(recipe_ids)


def get_recipe_nutrition_summary(collection: RecipeProfileCollection) -> Dict:
    """Get summary statistics for a recipe profile collection."""
    total = len(collection.profiles)
    if total == 0:
        return {"total_recipes": 0}
    
    with_nutrition = sum(1 for p in collection.profiles.values() if p.has_nutrition)
    by_status = {}
    for status in NutritionCompleteness:
        by_status[status.value] = len(collection.nutrition_status_index.get(status, set()))
    
    return {
        "total_recipes": total,
        "recipes_with_nutrition": with_nutrition,
        "recipes_without_nutrition": total - with_nutrition,
        "by_nutrition_status": by_status,
        "cuisines": len(collection.cuisine_index),
        "courses": len(collection.course_index),
        "diet_labels": len(collection.diet_label_index),
    }