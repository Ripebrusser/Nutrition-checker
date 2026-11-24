"""Nutrition service for nutrition calculations."""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.nutrition import (
    NutrientCalculator,
    RecipeAggregator,
    StrictMappingInterface,
    ApprovedMappingStore,
    IngredientWeightInfo,
    EdiblePortionCalculator,
    load_approved_mappings_from_jsonl,
    create_weight_infos_from_parsed,
)
from app.database.session import get_db
from app.database.models import Recipe
import pandas as pd
from pathlib import Path

class NutritionService:
    """Service for nutrition calculations."""
    
    def __init__(self):
        # Load IFCT data
        self.ifct_df = pd.read_parquet("data/interim/ifct_final_candidate/ifct_table1_candidate.parquet")
        
        # Initialize nutrition calculator
        self.calculator = NutrientCalculator(self.ifct_df)
        
        # Load approved mappings
        mapping_path = Path("data/processed/phase3/approved_mappings.jsonl")
        self.approved_store = load_approved_mappings_from_jsonl(mapping_path)
        self.mapping_interface = StrictMappingInterface(self.approved_store, self.ifct_df)
        self.edible_portion_calc = EdiblePortionCalculator()
        
        # Initialize aggregator
        from app.nutrition import AggregationConfig
        self.aggregator = RecipeAggregator(
            self.calculator,
            self.mapping_interface,
            self.edible_portion_calc,
            AggregationConfig()
        )
    
    def calculate_recipe_nutrition(self, recipe_id: int) -> Optional[dict]:
        """Calculate nutrition for a single recipe."""
        # This would need access to parsed ingredients and approved mappings
        # For now, return None as no approved mappings exist
        return None
    
    def calculate_recipe_nutrition_from_ingredients(
        self,
        ingredients: List[dict],
        servings: int = 4
    ) -> dict:
        """Calculate nutrition from ingredient list."""
        # Would use the nutrition calculator
        return {
            "total_nutrients": {},
            "per_serving_nutrients": {},
            "nutrition_status": "UNAVAILABLE",
        }
    
    def get_nutrient_info(self, nutrient: str) -> Dict:
        """Get information about a nutrient."""
        if not self.ifct_df.empty:
            # Get nutrient stats from IFCT
            col = nutrient
            if col in self.ifct_df.columns:
                vals = pd.to_numeric(self.ifct_df[col], errors='coerce').dropna()
                return {
                    "mean": float(vals.mean()),
                    "median": float(vals.median()),
                    "min": float(vals.min()),
                    "max": float(vals.max()),
                    "count": int(vals.count()),
                    "missing": len(self.ifct_df) - int(vals.count()),
                }
        return {}
    
    def get_nutrient_comparison(self, recipes: List[int], nutrient: str) -> List[Dict]:
        """Compare nutrient values across recipes."""
        results = []
        for recipe_id in recipes:
            # Would fetch recipe nutrition
            pass
        return []


def get_nutrition_service() -> NutritionService:
    """Get singleton nutrition service."""
    return NutritionService()