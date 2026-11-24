"""
Content-based recipe recommendation retrieval pipeline.

Main entry point for generating recipe recommendations with explanations.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import pandas as pd
import numpy as np
import json
import pickle
from dataclasses import dataclass, field

from .recipe_preprocessing import (
    RecipePreprocessor,
    get_recipe_ingredient_mapping,
    get_recipe_metadata_mapping,
    RECIPES_PATH,
    PARSED_INGREDIENTS_PATH,
)
from .recipe_features import RecipeFeatureExtractor, FeatureConfig, build_recipe_feature_matrix
from .baseline_recommenders import (
    BaseRecommender,
    CuisineMatchRecommender,
    JaccardSimilarityRecommender,
    RandomRecommender,
    get_baseline_recommender,
)

# Default paths
PIPELINE_DIR = Path("data/artifacts/recommendation/pipeline")
PIPELINE_DIR.mkdir(parents=True, exist_ok=True)

PIPELINE_CONFIG_PATH = Path("data/artifacts/recommendation/pipeline_config.json")


@dataclass
class PipelineConfig:
    """Configuration for the recommendation pipeline."""
    # Feature weights
    ingredient_weight: float = 1.0
    cuisine_weight: float = 1.0
    course_weight: float = 1.0
    diet_weight: float = 1.0
    
    # Retrieval settings
    max_recommendations: int = 10
    min_similarity_threshold: float = 0.0
    
    # Baseline weights
    cuisine_weight_baseline: float = 0.6
    ingredient_weight_baseline: float = 0.4
    
    # Feature config
    tfidf_max_features: int = 2000
    tfidf_ngram_range: Tuple[int, int] = (1, 2)
    tfidf_min_df: int = 2
    tfidf_max_df: float = 0.95


@dataclass
class RecommendationResult:
    """Structured recommendation result with explanations."""
    recipe_id: int
    recipe_name: str
    similarity_score: float
    cuisine: str
    course: str
    diet_labels: List[str]
    shared_ingredients: List[str]
    cuisine_match: float
    ingredient_overlap: float
    explanation: str
    # Component scores for transparency
    component_scores: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "recipe_id": self.recipe_id,
            "recipe_name": self.recipe_name,
            "similarity_score": round(self.similarity_score, 4),
            "cuisine": self.cuisine,
            "course": self.course,
            "diet_labels": self.diet_labels,
            "shared_ingredients": self.shared_ingredients,
            "cuisine_match": round(self.cuisine_match, 4),
            "ingredient_overlap": round(self.ingredient_overlap, 4),
            "explanation": self.explanation,
            "component_scores": {k: round(v, 4) for k, v in self.component_scores.items()},
        }


class ContentBasedRecipeRecommender:
    """
    Main content-based recipe recommendation pipeline.
    
    Combines TF-IDF ingredient similarity with metadata (cuisine, course, diet)
    to provide interpretable recipe recommendations with explanations.
    """
    
    def __init__(
        self,
        config: Optional[dict] = None,
        feature_extractor: Optional[Any] = None,
    ):
        """
        Initialize the recommender.
        
        Args:
            config: Configuration dictionary
            feature_extractor: Pre-fitted RecipeFeatureExtractor (optional)
        """
        self.config = config or {}
        self.feature_extractor = feature_extractor
        self.is_fitted = False
        
        # Data
        self.recipe_ids: List[int] = []
        self.recipe_metadata: Dict[int, Dict] = {}
        self.recipe_ingredients: Dict[int, List[str]] = {}
        self.feature_matrices: Dict[str, np.ndarray] = {}
        self.recipe_id_to_idx: Dict[int, int] = {}
        
        # Pre-computed similarity matrices (optional, for fast retrieval)
        self.similarity_matrix: Optional[np.ndarray] = None
        self.combined_features: Optional[np.ndarray] = None
        
        self.is_fitted: bool = False
    
    def fit(
        self,
        recipe_ingredients: Dict[int, List[str]],
        recipe_metadata: Dict[int, Dict],
        feature_extractor: Optional[Any] = None,
        precompute_similarities: bool = True,
    ) -> "ContentBasedRecipeRecommender":
        """
        Fit the recommender with recipe data.
        
        Args:
            recipe_ingredients: Dict mapping recipe_id to list of ingredient names
            recipe_metadata: Dict mapping recipe_id to metadata dict
            feature_extractor: Pre-fitted RecipeFeatureExtractor (optional)
            precompute_similarities: Whether to precompute all pairwise similarities
        """
        self.recipe_ingredients = {k: v for k, v in recipe_ingredients.items()}
        self.recipe_metadata = {k: v for k, v in recipe_metadata.items()}
        self.recipe_ids = sorted(recipe_metadata.keys())
        self.recipe_id_to_idx = {rid: i for i, rid in enumerate(self.recipe_ids)}
        
        n = len(self.recipe_ids)
        
        # Build ingredient sets for Jaccard similarity
        self.recipe_ingredient_sets = {
            rid: set(ingredients) for rid, ingredients in self.recipe_ingredients.items()
        }
        
        self.is_fitted = True
        return self
    
    def _jaccard_similarity(self, set_a: Set[str], set_b: Set[str]) -> float:
        """Compute Jaccard similarity between two sets."""
        if not set_a or not set_b:
            return 0.0
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        return intersection / union if union > 0 else 0.0
    
    def _compute_jaccard(self, set_a: Set[str], set_b: Set[str]) -> float:
        """Compute Jaccard similarity between two ingredient sets."""
        if not set_a or not set_b:
            return 0.0
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        return intersection / union if union > 0 else 0.0
    
    def _cuisine_similarity(self, cuisine_a: str, cuisine_b: str) -> float:
        """Calculate cuisine similarity score."""
        if not cuisine_a or not cuisine_b:
            return 0.0
        if cuisine_a == cuisine_b:
            return 1.0
        # Could add regional mapping here
        return 0.0
    
    def _get_shared_ingredients(self, set_a: Set[str], set_b: Set[str]) -> List[str]:
        """Get shared ingredients between two sets."""
        return list(set_a & set_b)
    
    def _generate_explanation(
        self,
        query_meta: Dict,
        candidate_meta: Dict,
        query_ingredients: Set[str],
        candidate_ingredients: Set[str],
        similarity_components: Dict[str, float],
    ) -> str:
        """Generate human-readable explanation for recommendation."""
        reasons = []
        
        # Cuisine match
        query_cuisine = query_meta.get("cuisine", "")
        cand_cuisine = candidate_meta.get("cuisine", "")
        if query_cuisine and cand_cuisine:
            if query_cuisine == cand_cuisine:
                reasons.append(f"Same cuisine ({query_cuisine})")
            else:
                reasons.append(f"Cuisine: {cand_cuisine} (query: {query_cuisine})")
        
        # Course match
        query_course = query_meta.get("course", "")
        cand_course = candidate_meta.get("course", "")
        if query_course and cand_course and query_course == cand_course:
            reasons.append(f"Same course ({query_course})")
        
        # Diet compatibility
        query_diets = set(query_meta.get("diet_labels", []))
        cand_diets = set(candidate_meta.get("diet_labels", []))
        shared_diets = query_diets & cand_diets
        if shared_diets:
            reasons.append(f"Dietary match: {', '.join(sorted(shared_diets))}")
        
        # Ingredient overlap
        query_ings = set(query_ingredients)
        cand_ings = set(candidate_ingredients)
        shared = query_ings & candidate_ingredients
        if shared:
            shared_list = ", ".join(sorted(shared)[:5])
            reasons.append(f"Shared ingredients: {', '.join(list(shared)[:5])}")
        
        return "; ".join(reasons) if reasons else "No strong similarity signals"
    
    def recommend(
        self,
        query_recipe_id: int,
        k: int = 10,
        filters: Optional[Dict] = None,
        use_tfidf: bool = False,
        feature_weights: Optional[Dict[str, float]] = None,
    ) -> List[Dict]:
        """
        Generate recommendations for a query recipe.
        
        Args:
            query_recipe_id: Recipe ID to find similar recipes for
            k: Number of recommendations to return
            filters: Optional filters (cuisine, course, diet_labels)
            use_tfidf: Whether to use TF-IDF similarity (requires feature extractor)
            feature_weights: Custom weights for feature combination
        
        Returns:
            List of recommendation dictionaries with explanations
        """
        if not self.is_fitted:
            raise ValueError("Recommender not fitted. Call fit() first.")
        
        if query_recipe_id not in self.recipe_metadata:
            raise ValueError(f"Query recipe {query_recipe_id} not found")
        
        query_meta = self.recipe_metadata[query_recipe_id]
        query_ingredients = set(self.recipe_ingredients.get(query_recipe_id, []))
        
        candidates = []
        
        for rid in self.recipe_ids:
            if rid == query_recipe_id:
                continue
            
            # Apply filters
            meta = self.recipe_metadata[rid]
            if filters:
                if "cuisine" in filters and filters["cuisine"] != meta.get("cuisine"):
                    continue
                if "course" in filters and filters["course"] != meta.get("course"):
                    continue
                if "diet_labels" in filters:
                    required = set(filters["diet_labels"])
                    if not required.issubset(set(meta.get("diet_labels", []))):
                        continue
            
            # Compute similarity components
            candidate_ingredients = set(self.recipe_ingredients.get(rid, []))
            
            # Jaccard similarity (ingredient overlap)
            jaccard = self._jaccard_similarity(
                set(self.recipe_ingredients.get(query_recipe_id, [])),
                set(self.recipe_ingredients.get(rid, []))
            )
            
            # Cuisine similarity
            cuisine_sim = 1.0 if self.recipe_metadata[query_recipe_id].get("cuisine") == \
                                self.recipe_metadata[rid].get("cuisine") else 0.0
            
            # Course similarity
            course_sim = 1.0 if self.recipe_metadata[query_recipe_id].get("course") == \
                                self.recipe_metadata[rid].get("course") else 0.0
            
            # Diet overlap
            query_diets = set(self.recipe_metadata[query_recipe_id].get("diet_labels", []))
            cand_diets = set(self.recipe_metadata[rid].get("diet_labels", []))
            diet_overlap = len(query_diets & cand_diets) / len(query_diets | cand_diets) if (query_diets | cand_diets) else 0.0
            
            # Combine scores
            weights = {
                "ingredient": 0.4,
                "cuisine": 0.3,
                "course": 0.15,
                "diet": 0.15,
            }
            
            combined_score = (
                weights["ingredient"] * jaccard +
                weights["cuisine"] * cuisine_sim +
                weights["course"] * course_sim +
                weights["diet"] * diet_overlap
            )
            
            if combined_score <= 0:
                continue
            
            # Get shared ingredients
            query_ings = set(self.recipe_ingredients.get(query_recipe_id, []))
            cand_ings = set(self.recipe_ingredients.get(rid, []))
            shared = list(query_ings & set(self.recipe_ingredients.get(rid, [])))
            
            meta = self.recipe_metadata[rid]
            query_meta = self.recipe_metadata[query_recipe_id]
            query_ingredients_set = set(self.recipe_ingredients.get(query_recipe_id, []))
            cand_ingredients_set = set(self.recipe_ingredients.get(rid, []))
            
            explanation = self._generate_explanation(
                query_meta, self.recipe_metadata[rid],
                query_ingredients_set, cand_ingredients_set,
                {"jaccard": jaccard, "cuisine": cuisine_sim, "course": course_sim, "diet": diet_overlap}
            )
            
            candidates.append({
                "recipe_id": rid,
                "recipe_name": self.recipe_metadata[rid].get("recipe_name", ""),
                "similarity_score": round(sum([
                    0.4 * jaccard,
                    0.3 * cuisine_sim,
                    0.15 * course_sim,
                    0.15 * diet_overlap
                ]), 4),
                "cuisine": meta.get("cuisine", ""),
                "course": meta.get("course", ""),
                "diet_labels": meta.get("diet_labels", []),
                "shared_ingredients": shared[:10],
                "cuisine_match": 1.0 if self.recipe_metadata[query_recipe_id].get("cuisine") == meta.get("cuisine") else 0.0,
                "ingredient_overlap": round(jaccard, 4),
                "explanation": explanation,
                "component_scores": {
                    "ingredient_jaccard": round(jaccard, 4),
                    "cuisine_match": round(cuisine_sim, 4),
                    "course_match": round(course_sim, 4),
                    "diet_overlap": round(diet_overlap, 4),
                },
            })
        
        # Sort by similarity score descending
        candidates.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        # Filter out query recipe and return top k
        results = [c for c in candidates if c["recipe_id"] != query_recipe_id]
        return results[:k]
    
    def recommend_by_ingredients(
        self,
        ingredients: List[str],
        k: int = 10,
        filters: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Recommend recipes based on a list of ingredients (not a query recipe).
        
        Useful for "what can I make with these ingredients?" queries.
        """
        if not self.is_fitted:
            raise ValueError("Recommender not fitted")
        
        query_ingredients = set(ing.lower().strip() for ing in ingredients if ing)
        if not query_ingredients:
            return []
        
        candidates = []
        
        for rid in self.recipe_ids:
            # Apply filters
            meta = self.recipe_metadata[rid]
            if filters:
                if "cuisine" in filters and filters["cuisine"] != meta.get("cuisine"):
                    continue
                if "course" in filters and filters["course"] != meta.get("course"):
                    continue
                if "diet_labels" in filters:
                    required = set(filters["diet_labels"])
                    if not required.issubset(set(meta.get("diet_labels", []))):
                        continue
            
            # Compute Jaccard with query ingredients
            candidate_ingredients = set(self.recipe_ingredients.get(rid, []))
            jaccard = self._jaccard_similarity(query_ingredients, candidate_ingredients)
            
            if jaccard <= 0:
                continue
            
            shared = list(query_ingredients & set(self.recipe_ingredients.get(rid, [])))
            meta = self.recipe_metadata[rid]
            
            candidates.append({
                "recipe_id": rid,
                "recipe_name": meta.get("recipe_name", ""),
                "similarity_score": round(jaccard, 4),
                "cuisine": meta.get("cuisine", ""),
                "course": meta.get("course", ""),
                "diet_labels": meta.get("diet_labels", []),
                "shared_ingredients": shared[:10],
                "ingredient_overlap": round(jaccard, 4),
                "explanation": f"Shares {len(shared)} ingredients: {', '.join(shared[:5])}",
                "component_scores": {"ingredient_jaccard": round(jaccard, 4)},
            })
        
        candidates.sort(key=lambda x: x["similarity_score"], reverse=True)
        return candidates[:k]
    
    def get_recipe_details(self, recipe_id: int) -> Optional[Dict]:
        """Get full details for a recipe."""
        if recipe_id not in self.recipe_metadata:
            return None
        
        meta = self.recipe_metadata[recipe_id]
        return {
            "recipe_id": recipe_id,
            "recipe_name": meta.get("recipe_name", ""),
            "cuisine": meta.get("cuisine", ""),
            "course": meta.get("course", ""),
            "diet_labels": meta.get("diet_labels", []),
            "prep_time_min": meta.get("prep_time_min", 0),
            "cook_time_min": meta.get("cook_time_min", 0),
            "total_time_min": meta.get("total_time_min", 0),
            "servings": meta.get("servings", 4),
            "ingredients": self.recipe_ingredients.get(recipe_id, []),
        }


def create_recommender(
    recipes_path: str = RECIPES_PATH,
    parsed_ingredients_path: str = PARSED_INGREDIENTS_PATH,
    config: Optional[dict] = None,
) -> ContentBasedRecipeRecommender:
    """
    Create and fit a content-based recipe recommender.
    
    This is the main entry point for creating a recommender from raw data.
    """
    # Load data
    preprocessor = RecipePreprocessor()
    preprocessor.load_data()
    
    recipe_ingredients = get_recipe_ingredient_mapping(PARSED_INGREDIENTS_PATH)
    recipe_metadata = get_recipe_metadata_mapping(RECIPES_PATH)
    
    # Create and fit recommender
    recommender = ContentBasedRecipeRecommender(config=config or {})
    recommender.fit(
        recipe_ingredients=recipe_ingredients,
        recipe_metadata=recipe_metadata,
    )
    
    return recommender


def load_recommender_from_artifacts(
    artifacts_dir: Path = Path("data/artifacts/recommendation"),
) -> ContentBasedRecipeRecommender:
    """Load a recommender from saved artifacts."""
    # Load feature extractor if available
    extractor = None
    tfidf_path = artifacts_dir / "tfidf_vectorizer.pkl"
    if tfidf_path.exists():
        extractor = RecipeFeatureExtractor()
        extractor.load_artifacts(artifacts_dir)
    
    # Load saved pipeline data
    data_path = artifacts_dir / "pipeline_data.pkl"
    if not data_path.exists():
        raise FileNotFoundError(f"No pipeline data found at {data_path}")
    
    with open(data_path, "rb") as f:
        data = pickle.load(f)
    
    # Create recommender with loaded feature extractor (if available)
    recommender = ContentBasedRecipeRecommender()
    recommender.fit(
        recipe_ingredients=data["recipe_ingredients"],
        recipe_metadata=data["recipe_metadata"],
        feature_extractor=extractor,
    )
    
    return recommender


def save_recommender_artifacts(
    recommender: ContentBasedRecipeRecommender,
    output_dir: Path = PIPELINE_DIR,
) -> None:
    """Save recommender state to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save configuration
    config = {
        "recipe_ids": recommender.recipe_ids,
        "n_recipes": len(recommender.recipe_ids),
    }
    with open(output_dir / "pipeline_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    # Save recipe data
    data = {
        "recipe_ingredients": recommender.recipe_ingredients,
        "recipe_metadata": recommender.recipe_metadata,
        "recipe_ids": recommender.recipe_ids,
    }
    with open(output_dir / "pipeline_data.pkl", "wb") as f:
        pickle.dump(data, f)
    
    # Save feature extractor if available
    if recommender.feature_extractor is not None:
        recommender.feature_extractor.save_artifacts(output_dir)


if __name__ == "__main__":
    print("Creating content-based recipe recommender...")
    
    recommender = create_recommender()
    
    # Test with a sample recipe
    test_recipe_id = list(recommender.recipe_metadata.keys())[0]
    print(f"\nTesting with recipe {test_recipe_id}: {recommender.recipe_metadata[test_recipe_id]['recipe_name']}")
    
    recs = recommender.recommend(test_recipe_id, k=5)
    print(f"\nTop 5 recommendations:")
    for i, rec in enumerate(recs, 1):
        print(f"  {i}. {rec['recipe_id']}: {rec['recipe_name']} "
              f"(score: {rec['similarity_score']:.4f}, cuisine: {rec['cuisine']})")
        print(f"      Explanation: {rec['explanation']}")
    
    print("\nDone!")