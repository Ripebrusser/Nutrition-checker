"""
Baseline recommendation methods for content-based recipe recommendation.

Implements simple, interpretable baselines for comparison with advanced methods.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any
import pandas as pd
import numpy as np
import json
import random
from collections import Counter
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .recipe_preprocessing import (
    get_recipe_ingredient_mapping,
    get_recipe_metadata_mapping,
    RecipePreprocessor,
    PARSED_INGREDIENTS_PATH,
    RECIPES_PATH,
)
from .recipe_features import RecipeFeatureExtractor, FeatureConfig
from .data_splits import load_data_splits

# Default paths
BASELINES_DIR = Path("data/artifacts/recommendation/baselines")
BASELINES_DIR.mkdir(parents=True, exist_ok=True)

BASELINE_OUTPUTS_DIR = BASELINES_DIR / "outputs"
BASELINE_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class BaselineConfig:
    """Configuration for baseline recommenders."""
    cuisine_weight: float = 0.6
    ingredient_weight: float = 0.4
    max_recommendations: int = 10
    random_seed: int = 42


class BaseRecommender:
    """Base class for recommenders."""
    
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.recipe_ingredients: Dict[int, List[str]] = {}
        self.recipe_metadata: Dict[int, Dict] = {}
        self.recipe_ids: List[int] = []
        self.is_fitted: bool = False
    
    def fit(
        self,
        recipe_ingredients: Dict[int, List[str]],
        recipe_metadata: Dict[int, Dict],
        recipe_ids: Optional[List[int]] = None,
    ) -> "BaseRecommender":
        """Fit the recommender (prepare internal data structures)."""
        if self.recipe_ids is None or len(self.recipe_ids) == 0:
            self.recipe_ingredients = {k: v for k, v in self.recipe_ingredients.items() if k in self.recipe_ids}
            self.recipe_metadata = {k: v for k, v in self.recipe_metadata.items() if k in self.recipe_ids}
        return self
    
    def recommend(
        self,
        query_recipe_id: int,
        k: int = 10,
        exclude: Optional[List[int]] = None,
        **kwargs
    ) -> List[Dict]:
        """Generate recommendations for a query recipe."""
        raise NotImplementedError
    
    def _exclude_self_and_duplicates(
        self,
        results: List[Dict],
        query_id: int,
        exclude: Optional[List[int]] = None,
    ) -> List[Dict]:
        """Remove query recipe and duplicates from results."""
        exclude_set = set(exclude or [])
        exclude_set.add(query_id)
        
        seen = set()
        filtered = []
        for rec in results:
            rid = rec["recipe_id"]
            if rid in exclude_set or rid in seen:
                continue
            seen.add(rid)
            filtered.append(rec)
        return filtered


class CuisineMatchRecommender(BaseRecommender):
    """
    Baseline A: Cuisine matching recommender.
    
    Ranks recipes by cuisine compatibility first, then by ingredient overlap.
    """
    
    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self.cuisine_weight = self.config.get("cuisine_weight", 0.6)
        self.ingredient_weight = self.config.get("ingredient_weight", 0.4)
        self.region_mapping = self._load_region_mapping()
    
    def _load_region_mapping(self) -> Dict[str, str]:
        """Map cuisines to regions for partial matching."""
        # Simplified region mapping
        return {
            "Indian": "Indian",
            "North Indian Recipes": "Indian",
            "South Indian Recipes": "Indian",
            "Gujarati": "Indian",
            "Maharashtrian": "Indian",
            "Punjabi": "Indian",
            "Rajasthani": "Indian",
            "Bengali": "Indian",
            "Goan": "Indian",
            "Kashmiri": "Indian",
            "Kerala": "Indian",
            "Andhra": "Indian",
            "Tamil": "Indian",
            "Karnataka": "Indian",
            "Continental": "Western",
            "Italian Recipes": "Western",
            "Mexican": "Western",
            "Chinese": "Asian",
            "Thai": "Asian",
            "Japanese": "Asian",
            "Korean": "Asian",
            "Vietnamese": "Asian",
            "Middle Eastern": "Middle Eastern",
            "Mediterranean": "Mediterranean",
        }
    
    def _cuisine_similarity(self, cuisine_a: str, cuisine_b: str) -> float:
        """Calculate cuisine similarity score."""
        if cuisine_a == cuisine_b:
            return 1.0
        region_a = self.region_mapping.get(cuisine_a, "Other")
        region_b = self.region_mapping.get(cuisine_b, "Other")
        if region_a == region_b:
            return 0.5
        return 0.0
    
    def _jaccard_similarity(self, ingredients_a: List[str], ingredients_b: List[str]) -> float:
        """Calculate Jaccard similarity between ingredient sets."""
        set_a = set(ingredients_a)
        set_b = set(ingredients_b)
        if not set_a or not set_b:
            return 0.0
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        return intersection / union if union > 0 else 0.0
    
    def fit(
        self,
        recipe_ingredients: Dict[int, List[str]],
        recipe_metadata: Dict[int, Dict],
        recipe_ids: Optional[List[int]] = None,
    ) -> "CuisineMatchRecommender":
        super().fit(None, None)  # Just set the data
        self.recipe_ingredients = {k: v for k, v in recipe_ingredients.items()}
        self.recipe_metadata = recipe_metadata
        self.recipe_ids = list(recipe_metadata.keys())
        self.is_fitted = True
        return self
    
    def recommend(
        self,
        query_recipe_id: int,
        k: int = 10,
        exclude: Optional[List[int]] = None,
        **kwargs
    ) -> List[Dict]:
        if not self.is_fitted:
            raise ValueError("Recommender not fitted")
        
        query_meta = self.recipe_metadata.get(query_recipe_id, {})
        query_cuisine = query_meta.get("cuisine", "")
        query_ingredients = set(self.recipe_ingredients.get(query_recipe_id, []))
        
        scores = []
        for rid in self.recipe_ids:
            if rid == query_recipe_id:
                continue
            
            meta = self.recipe_metadata.get(rid, {})
            cuisine_sim = self._cuisine_similarity(
                query_cuisine, meta.get("cuisine", "")
            )
            ing_sim = self._jaccard_similarity(
                self.recipe_ingredients.get(rid, []),
                list(query_ingredients)
            )
            
            score = (self.cuisine_weight * cuisine_sim + 
                    self.ingredient_weight * self._jaccard_similarity(
                        self.recipe_ingredients.get(rid, []),
                        list(query_ingredients)
                    ))
            
            meta = self.recipe_metadata.get(rid, {})
            shared_ingredients = list(set(self.recipe_ingredients.get(rid, [])) & 
                                     set(self.recipe_ingredients.get(query_recipe_id, [])))
            
            scores.append({
                "recipe_id": rid,
                "recipe_name": meta.get("recipe_name", ""),
                "similarity_score": round(score, 4),
                "cuisine_match": self._cuisine_similarity(query_cuisine, meta.get("cuisine", "")),
                "ingredient_overlap": round(self._jaccard_similarity(
                    self.recipe_ingredients.get(rid, []),
                    list(query_ingredients)
                ), 4),
                "shared_ingredients": shared_ingredients[:10],
                "cuisine": meta.get("cuisine", ""),
                "course": meta.get("course", ""),
                "diet_labels": meta.get("diet_labels", []),
                "explanation": self._generate_explanation(
                    query_cuisine, meta.get("cuisine", ""),
                    list(query_ingredients),
                    self.recipe_ingredients.get(rid, [])
                ),
            })
        
        # Sort by score descending
        scores.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        # Filter and return top k
        results = self._exclude_self_and_duplicates(scores, query_recipe_id, exclude)
        return results[:k]
    
    def _generate_explanation(
        self,
        query_cuisine: str,
        candidate_cuisine: str,
        query_ingredients: List[str],
        candidate_ingredients: List[str],
    ) -> str:
        """Generate human-readable explanation."""
        reasons = []
        
        if query_cuisine == candidate_cuisine:
            reasons.append(f"Same cuisine ({query_cuisine})")
        elif query_cuisine != candidate_cuisine:
            reasons.append(f"Different cuisine ({candidate_cuisine} vs {query_cuisine})")
        
        query_set = set(query_ingredients)
        candidate_set = set(candidate_ingredients)
        shared = query_set & candidate_set
        
        if shared:
            shared_list = ", ".join(list(shared)[:5])
            reasons.append(f"Shares ingredients: {shared_list}")
        
        return "; ".join(reasons)


class JaccardSimilarityRecommender(BaseRecommender):
    """
    Baseline B: Pure ingredient Jaccard similarity.
    
    Ranks recipes by Jaccard similarity of ingredient sets.
    """
    
    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
    
    def fit(
        self,
        recipe_ingredients: Dict[int, List[str]],
        recipe_metadata: Dict[int, Dict],
        recipe_ids: Optional[List[int]] = None,
    ) -> "JaccardSimilarityRecommender":
        self.recipe_ingredients = {k: v for k, v in recipe_ingredients.items()}
        self.recipe_metadata = recipe_metadata
        self.recipe_ids = list(recipe_metadata.keys())
        self.is_fitted = True
        return self
    
    def _jaccard(self, set_a: Set[str], set_b: Set[str]) -> float:
        if not set_a or not set_b:
            return 0.0
        inter = len(set_a & set_b)
        union = len(set_a | set_b)
        return inter / union if union > 0 else 0.0
    
    def recommend(
        self,
        query_recipe_id: int,
        k: int = 10,
        exclude: Optional[List[int]] = None,
        **kwargs
    ) -> List[Dict]:
        if not self.is_fitted:
            raise ValueError("Recommender not fitted")
        
        query_ingredients = set(self.recipe_ingredients.get(query_recipe_id, []))
        
        scores = []
        for rid in self.recipe_ids:
            if rid == query_recipe_id:
                continue
            
            candidate_ingredients = set(self.recipe_ingredients.get(rid, []))
            jaccard = self._jaccard(query_ingredients, candidate_ingredients)
            
            if jaccard == 0:
                continue
            
            meta = self.recipe_metadata.get(rid, {})
            shared = list(set(self.recipe_ingredients.get(rid, [])) & 
                         set(self.recipe_ingredients.get(query_recipe_id, [])))
            
            scores.append({
                "recipe_id": rid,
                "recipe_name": meta.get("recipe_name", ""),
                "similarity_score": round(jaccard, 4),
                "shared_ingredients": shared[:10],
                "cuisine": meta.get("cuisine", ""),
                "course": meta.get("course", ""),
                "diet_labels": meta.get("diet_labels", []),
                "explanation": f"Shares {len(shared)} ingredients" if shared else "No shared ingredients",
            })
        
        scores.sort(key=lambda x: x["similarity_score"], reverse=True)
        results = self._exclude_self_and_duplicates(scores, query_recipe_id, exclude)
        return results[:k]


class RandomRecommender(BaseRecommender):
    """
    Baseline C: Random recommendation.
    
    Returns random recipes as a baseline for comparison.
    """
    
    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self.random_seed = self.config.get("random_seed", 42)
        self._rng = random.Random(self.random_seed)
    
    def fit(
        self,
        recipe_ingredients: Dict[int, List[str]],
        recipe_metadata: Dict[int, Dict],
        recipe_ids: Optional[List[int]] = None,
    ) -> "RandomRecommender":
        self.recipe_ingredients = recipe_ingredients
        self.recipe_metadata = recipe_metadata
        self.recipe_ids = list(recipe_metadata.keys())
        self.is_fitted = True
        return self
    
    def recommend(
        self,
        query_recipe_id: int,
        k: int = 10,
        exclude: Optional[List[int]] = None,
        **kwargs
    ) -> List[Dict]:
        if not self.is_fitted:
            raise ValueError("Recommender not fitted")
        
        candidates = [rid for rid in self.recipe_ids if rid != query_recipe_id]
        if exclude:
            candidates = [rid for rid in candidates if rid not in exclude]
        
        # Use fixed seed for reproducibility
        self._rng.shuffle(candidates)
        selected = candidates[:k]
        
        results = []
        for rid in selected:
            meta = self.recipe_metadata.get(rid, {})
            shared = list(set(self.recipe_ingredients.get(rid, [])) & 
                         set(self.recipe_ingredients.get(query_recipe_id, [])))
            
            results.append({
                "recipe_id": rid,
                "recipe_name": meta.get("recipe_name", ""),
                "similarity_score": 0.0,  # Random has no similarity
                "shared_ingredients": shared[:10],
                "cuisine": meta.get("cuisine", ""),
                "course": meta.get("course", ""),
                "diet_labels": meta.get("diet_labels", []),
                "explanation": "Random recommendation (baseline)",
            })
        
        return results


def get_baseline_recommender(
    baseline_type: str,
    config: Optional[dict] = None,
) -> BaseRecommender:
    """
    Factory function to get baseline recommender by type.
    
    Args:
        baseline_type: One of "cuisine_match", "jaccard", "random"
        config: Configuration dictionary
    
    Returns:
        Initialized recommender instance.
    """
    if baseline_type == "cuisine_match":
        return CuisineMatchRecommender(config)
    elif baseline_type == "jaccard":
        return JaccardSimilarityRecommender(config)
    elif baseline_type == "random":
        return RandomRecommender(config)
    else:
        raise ValueError(f"Unknown baseline type: {baseline_type}")


def run_baseline_comparison(
    query_recipe_ids: List[int],
    recipe_ingredients: Dict[int, List[str]],
    recipe_metadata: Dict[int, Dict],
    k: int = 10,
    config: Optional[dict] = None,
) -> Dict[str, List[List[Dict]]]:
    """
    Run all baselines on a set of query recipes.
    
    Returns:
        Dictionary mapping baseline name to list of recommendations per query.
    """
    baselines = {
        "cuisine_match": CuisineMatchRecommender(config),
        "jaccard": JaccardSimilarityRecommender(config),
        "random": RandomRecommender(config),
    }
    
    results = {}
    for name, recommender in baselines.items():
        # Initialize recommender with data directly
        recommender.recipe_ingredients = {k: v for k, v in recipe_ingredients.items()}
        recommender.recipe_metadata = recipe_metadata
        recommender.recipe_ids = list(recipe_metadata.keys())
        recommender.is_fitted = True
        
        all_recs = []
        for qid in query_recipe_ids:
            recs = recommender.recommend(qid, k=k)
            all_recs.append(recs)
        results[name] = all_recs
    
    return results


def save_baseline_outputs(
    outputs: Dict[str, List[List[Dict]]],
    output_dir: Path = BASELINE_OUTPUTS_DIR,
) -> None:
    """Save baseline outputs to disk."""
    BASELINE_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    
    for name, recs in outputs.items():
        output_path = BASELINE_OUTPUTS_DIR / f"{name}_recommendations.json"
        with open(output_path, "w") as f:
            json.dump(recs, f, indent=2, default=str)
    
    # Save summary
    summary = {
        name: {
            "n_queries": len(recs),
            "avg_recommendations": np.mean([len(r) for r in recs]) if recs else 0,
        }
        for name, recs in outputs.items()
    }
    
    with open(BASELINES_DIR / "baseline_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)


if __name__ == "__main__":
    print("Testing baseline recommenders...")
    
    # Load data
    preprocessor = RecipePreprocessor()
    preprocessor.load_data()
    recipe_ingredients = get_recipe_ingredient_mapping(PARSED_INGREDIENTS_PATH)
    recipe_metadata = get_recipe_metadata_mapping(RECIPES_PATH)
    
    # Test with a few recipes
    test_query_ids = list(recipe_metadata.keys())[:5]
    print(f"Testing on query recipes: {test_query_ids}")
    
    config = {"cuisine_weight": 0.6, "ingredient_weight": 0.4}
    
    # Test each baseline
    for name in ["cuisine_match", "jaccard", "random"]:
        recommender = get_baseline_recommender(name, config)
        recommender.fit(None, None)
        recommender.recipe_ingredients = {k: v for k, v in recipe_ingredients.items()}
        recommender.recipe_metadata = recipe_metadata
        recommender.recipe_ids = list(recipe_metadata.keys())
        recommender.is_fitted = True
        
        recs = recommender.recommend(test_query_ids[0], k=5)
        print(f"\n{name} recommendations for recipe {test_query_ids[0]}:")
        for rec in recs[:3]:
            print(f"  {rec['recipe_id']}: {rec['recipe_name']} (score: {rec['similarity_score']})")
    
    print("\nDone!")