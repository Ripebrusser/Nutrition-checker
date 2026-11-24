"""
Recipe preprocessing for content-based recommendation pipeline.

Handles recipe data loading, cleaning, ingredient extraction, and quality checks.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import pandas as pd
import numpy as np
import json
import hashlib
from collections import Counter
import warnings

# Default paths
RECIPES_PATH = "data/processed/recipes.parquet"
PARSED_INGREDIENTS_PATH = "data/interim/phase2/parsed_recipe_ingredients.parquet"
NORMALIZED_INGREDIENTS_PATH = "data/interim/phase2/normalized_ingredients.parquet"
IFCT_MATCH_CANDIDATES_PATH = "data/interim/phase3/stage2_3/ifct_match_candidates.parquet"


class RecipePreprocessor:
    """
    Preprocesses recipe data for content-based recommendation pipeline.
    
    Handles data loading, quality checks, ingredient extraction,
    duplicate detection, and recipe-level feature preparation.
    """
    
    def __init__(
        self,
        recipes_path: str = RECIPES_PATH,
        parsed_ingredients_path: str = PARSED_INGREDIENTS_PATH,
        normalized_ingredients_path: str = NORMALIZED_INGREDIENTS_PATH,
        ifct_match_candidates_path: str = IFCT_MATCH_CANDIDATES_PATH,
    ):
        self.recipes_path = Path(recipes_path)
        self.parsed_ingredients_path = Path(parsed_ingredients_path)
        self.normalized_ingredients_path = Path(normalized_ingredients_path)
        self.ifct_match_candidates_path = Path(ifct_match_candidates_path)
        
        self._recipes_df: Optional[pd.DataFrame] = None
        self._parsed_ingredients_df: Optional[pd.DataFrame] = None
        self._normalized_ingredients_df: Optional[pd.DataFrame] = None
        self._ifct_match_candidates_df: Optional[pd.DataFrame] = None
        
        self.recipe_ingredients: Dict[int, List[str]] = {}
        self.recipe_metadata: Dict[int, Dict] = {}
        self.quality_report: Dict = {}
    
    def load_data(self) -> None:
        """Load all required data files."""
        self._recipes_df = pd.read_parquet(self.recipes_path)
        self._parsed_ingredients_df = pd.read_parquet(self.parsed_ingredients_path)
        self._normalized_ingredients_df = pd.read_parquet(self.normalized_ingredients_path)
        self._ifct_match_candidates_df = pd.read_parquet(self.ifct_match_candidates_path)
    
    def check_data_quality(self) -> Dict:
        """
        Perform comprehensive data quality checks.
        
        Returns:
            Dictionary with quality metrics and issues found.
        """
        if self._recipes_df is None:
            self.load_data()
        
        recipes = self._recipes_df
        parsed = self._parsed_ingredients_df
        
        report = {
            "recipes": {
                "total_recipes": len(recipes),
                "columns": list(recipes.columns),
                "missing_values": recipes.isnull().sum().to_dict(),
                "dtypes": {col: str(dtype) for col, dtype in recipes.dtypes.items()},
            },
            "parsed_ingredients": {
                "total_lines": len(parsed),
                "unique_recipes": parsed["recipe_id"].nunique(),
                "unique_ingredient_names": parsed["ingredient_name"].nunique(),
                "parse_status_distribution": parsed["parse_status"].value_counts().to_dict(),
                "conversion_status_distribution": parsed["conversion_status"].value_counts().to_dict(),
                "gram_weight_coverage": {
                    "total": len(parsed),
                    "with_gram_weight": parsed["gram_weight"].notna().sum(),
                    "coverage_pct": parsed["gram_weight"].notna().mean() * 100,
                },
                "missing_values": parsed.isnull().sum().to_dict(),
            },
            "cuisine_distribution": recipes["cuisine"].value_counts().to_dict(),
            "course_distribution": recipes["course"].value_counts().to_dict(),
            "diet_labels_distribution": recipes["diet_labels"].value_counts().to_dict(),
            "recipe_type_distribution": recipes["recipe_type"].value_counts().to_dict(),
        }
        
        # Check for duplicate recipes (by ingredient list)
        duplicate_check = self._check_duplicate_recipes()
        report["duplicate_analysis"] = duplicate_check
        
        # Check for identical/near-identical ingredient lists
        near_duplicate_check = self._check_near_duplicate_recipes()
        report["near_duplicate_analysis"] = near_duplicate_check
        
        self.quality_report = report
        return report
    
    def _check_duplicate_recipes(self) -> Dict:
        """Check for exact duplicate recipes based on ingredient lists."""
        if self._parsed_ingredients_df is None:
            return {"error": "Parsed ingredients not loaded"}
        
        parsed = self._parsed_ingredients_df
        
        # Group by recipe_id and create ingredient signature
        recipe_signatures = {}
        for recipe_id, group in parsed.groupby("recipe_id"):
            ingredients = sorted(group["ingredient_name"].str.lower().str.strip().tolist())
            signature = "|".join(ingredients)
            recipe_signatures[recipe_id] = signature
        
        # Find duplicates
        signature_to_recipes = {}
        for recipe_id, sig in recipe_signatures.items():
            if sig not in signature_to_recipes:
                signature_to_recipes[sig] = []
            signature_to_recipes[sig].append(recipe_id)
        
        duplicates = {sig: ids for sig, ids in signature_to_recipes.items() if len(ids) > 1}
        
        return {
            "total_recipes_checked": len(recipe_signatures),
            "duplicate_groups": len(duplicates),
            "duplicate_recipes": sum(len(ids) for ids in duplicates.values()),
            "duplicate_groups_detail": duplicates,
        }
    
    def _check_near_duplicate_recipes(self, jaccard_threshold: float = 0.9) -> Dict:
        """
        Check for near-duplicate recipes using Jaccard similarity of ingredient sets.
        
        Args:
            jaccard_threshold: Threshold above which recipes are considered near-duplicates.
        
        Returns:
            Dictionary with near-duplicate analysis.
        """
        if self._parsed_ingredients_df is None:
            return {"error": "Parsed ingredients not loaded"}
        
        parsed = self._parsed_ingredients_df
        
        # Build ingredient sets per recipe
        recipe_ingredient_sets = {}
        for recipe_id, group in parsed.groupby("recipe_id"):
            ingredients = set(group["ingredient_name"].str.lower().str.strip())
            recipe_ingredient_sets[recipe_id] = ingredients
        
        # Check for near-duplicates (sample-based for efficiency)
        recipe_ids = list(recipe_ingredient_sets.keys())
        near_duplicates = []
        
        # Sample-based comparison to avoid O(n^2) for all 6865 recipes
        sample_size = min(1000, len(recipe_ids))
        sampled_ids = np.random.choice(recipe_ids, size=sample_size, replace=False)
        
        for i, id1 in enumerate(sampled_ids):
            set1 = recipe_ingredient_sets[id1]
            if len(set1) == 0:
                continue
            for id2 in sampled_ids[i+1:]:
                set2 = recipe_ingredient_sets[id2]
                if len(set2) == 0:
                    continue
                intersection = len(set1 & set2)
                union = len(set1 | set2)
                if union > 0:
                    jaccard = intersection / union
                    if jaccard >= jaccard_threshold:
                        near_duplicates.append({
                            "recipe_id_1": int(id1),
                            "recipe_id_2": int(id2),
                            "jaccard_similarity": round(jaccard, 4),
                            "ingredients_1": len(set1),
                            "ingredients_2": len(set2),
                            "shared": intersection,
                        })
        
        return {
            "threshold": jaccard_threshold,
            "sample_size": sample_size,
            "near_duplicate_pairs_found": len(near_duplicates),
            "near_duplicates": near_duplicates[:50],  # Limit output
        }
    
    def extract_recipe_ingredients(self) -> Dict[int, List[str]]:
        """
        Extract normalized ingredient lists per recipe.
        
        Returns:
            Dictionary mapping recipe_id to list of normalized ingredient names.
        """
        if self._parsed_ingredients_df is None:
            self.load_data()
        
        parsed = self._parsed_ingredients_df
        
        # Use normalized ingredient names from parsed ingredients
        recipe_ingredients = {}
        for recipe_id, group in parsed.groupby("recipe_id"):
            ingredients = group["ingredient_name"].str.lower().str.strip().tolist()
            # Remove empty strings and deduplicate while preserving order
            seen = set()
            unique_ingredients = []
            for ing in ingredients:
                if ing and ing not in seen:
                    seen.add(ing)
                    unique_ingredients.append(ing)
            recipe_ingredients[int(recipe_id)] = unique_ingredients
        
        self.recipe_ingredients = recipe_ingredients
        return recipe_ingredients
    
    def extract_recipe_metadata(self) -> Dict[int, Dict]:
        """
        Extract metadata for each recipe.
        
        Returns:
            Dictionary mapping recipe_id to metadata dict.
        """
        if self._recipes_df is None:
            self.load_data()
        
        recipes = self._recipes_df
        metadata = {}
        
        for _, row in recipes.iterrows():
            recipe_id = int(row["recipe_id"])
            
            # Parse diet labels (pipe-separated)
            diet_labels = []
            if row["diet_labels"] and isinstance(row["diet_labels"], str):
                diet_labels = [d.strip() for d in row["diet_labels"].split("|") if d.strip()]
            
            metadata[recipe_id] = {
                "recipe_name": row["recipe_name_en"],
                "cuisine": row["cuisine"],
                "course": row["course"],
                "recipe_type": row["recipe_type"],
                "diet_labels": diet_labels,
                "prep_time_min": int(row["prep_time_min"]) if pd.notna(row["prep_time_min"]) else 0,
                "cook_time_min": int(row["cook_time_min"]) if pd.notna(row["cook_time_min"]) else 0,
                "total_time_min": int(row["total_time_min"]) if pd.notna(row["total_time_min"]) else 0,
                "servings": int(row["servings"]) if pd.notna(row["servings"]) else 4,
            }
        
        self.recipe_metadata = metadata
        return metadata
    
    def get_recipe_ingredient_sets(self) -> Dict[int, Set[str]]:
        """
        Get ingredient sets per recipe for Jaccard similarity calculations.
        
        Returns:
            Dictionary mapping recipe_id to set of ingredient names.
        """
        if not self.recipe_ingredients:
            self.extract_recipe_ingredients()
        
        return {rid: set(ings) for rid, ings in self.recipe_ingredients.items()}
    
    def identify_missing_ingredients(self) -> Dict:
        """
        Identify recipes with missing ingredient data.
        
        Returns:
            Dictionary with missing ingredient statistics.
        """
        if self._parsed_ingredients_df is None:
            self.load_data()
        
        parsed = self._parsed_ingredients_df
        recipes_with_ingredients = set(parsed["recipe_id"].unique())
        all_recipe_ids = set(range(1, 6866))  # Assuming recipe IDs 1-6865
        
        missing_recipes = all_recipe_ids - recipes_with_ingredients
        
        return {
            "total_recipes": 6865,
            "recipes_with_ingredients": len(recipes_with_ingredients),
            "recipes_missing_ingredients": len(missing_recipes),
            "missing_recipe_ids": sorted(list(missing_recipes))[:100],  # Limit output
        }


def load_recipes_dataframe(path: str = RECIPES_PATH) -> pd.DataFrame:
    """Load recipes dataframe."""
    return pd.read_parquet(path)


def load_parsed_ingredients_dataframe(path: str = PARSED_INGREDIENTS_PATH) -> pd.DataFrame:
    """Load parsed ingredients dataframe."""
    return pd.read_parquet(path)


def get_recipe_ingredient_mapping(
    parsed_ingredients_path: str = PARSED_INGREDIENTS_PATH
) -> Dict[int, List[str]]:
    """
    Get mapping from recipe_id to list of normalized ingredient names.
    
    This is the primary function for getting recipe-ingredient mappings
    for the recommendation pipeline.
    """
    preprocessor = RecipePreprocessor(parsed_ingredients_path=parsed_ingredients_path)
    return preprocessor.extract_recipe_ingredients()


def get_recipe_metadata_mapping(
    recipes_path: str = RECIPES_PATH
) -> Dict[int, Dict]:
    """
    Get mapping from recipe_id to metadata dict.
    """
    preprocessor = RecipePreprocessor(recipes_path=recipes_path)
    return preprocessor.extract_recipe_metadata()


if __name__ == "__main__":
    # Quick test
    preprocessor = RecipePreprocessor()
    preprocessor.load_data()
    quality = preprocessor.check_data_quality()
    print("Data Quality Report:")
    print(json.dumps(quality, indent=2, default=str))