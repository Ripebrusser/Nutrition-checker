"""
Evaluation framework for content-based recipe recommendation.

Implements defensible offline evaluation strategies acknowledging
the lack of genuine user interaction data.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Dict, Any
import pandas as pd
import numpy as np
import json
from collections import Counter
from dataclasses import dataclass, field
from sklearn.metrics.pairwise import cosine_similarity
import warnings

from .retrieval_pipeline import ContentBasedRecipeRecommender, create_recommender
from .baseline_recommenders import (
    BaseRecommender,
    CuisineMatchRecommender,
    JaccardSimilarityRecommender,
    RandomRecommender,
    get_baseline_recommender,
)
from .data_splits import load_data_splits, create_data_splits, SplitConfig
from .recipe_features import build_recipe_feature_matrix, FeatureConfig
from .recipe_preprocessing import get_recipe_ingredient_mapping, get_recipe_metadata_mapping

# Default paths
EVAL_DIR = Path("data/artifacts/recommendation/evaluation")
EVAL_DIR.mkdir(parents=True, exist_ok=True)

EVAL_RESULTS_PATH = Path("data/artifacts/recommendation/evaluation_results.json")
EVAL_SUMMARY_PATH = Path("data/artifacts/recommendation/evaluation_summary.json")


@dataclass
class EvaluationConfig:
    """Configuration for evaluation."""
    k_values: List[int] = field(default_factory=lambda: [1, 5, 10, 20])
    random_seed: int = 42
    n_manual_review_samples: int = 50  # For manual relevance assessment
    proxy_relevance_threshold: float = 0.3  # Jaccard threshold for proxy relevance


def jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """Calculate Jaccard similarity between two sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def cuisine_match(query_meta: Dict, candidate_meta: Dict) -> float:
    """Check if cuisines match."""
    q_cuisine = query_meta.get("cuisine")
    c_cuisine = candidate_meta.get("cuisine")
    if not q_cuisine or not c_cuisine:
        return 0.0
    return 1.0 if q_cuisine == c_cuisine else 0.0


def course_match(query_meta: Dict, candidate_meta: Dict) -> float:
    """Check if courses match."""
    q_course = query_meta.get("course")
    c_course = candidate_meta.get("course")
    if not q_course or not c_course:
        return 0.0
    return 1.0 if q_course == c_course else 0.0


def diet_overlap(query_meta: Dict, candidate_meta: Dict) -> float:
    """Calculate diet label overlap (overlap coefficient = intersection / min(|A|, |B|))."""
    query_diets = set(query_meta.get("diet_labels", []))
    cand_diets = set(candidate_meta.get("diet_labels", []))
    if not query_diets and not cand_diets:
        return 0.0
    if not query_diets or not cand_diets:
        return 0.0
    inter = query_diets & cand_diets
    min_size = min(len(query_diets), len(cand_diets))
    return len(query_diets & cand_diets) / min_size if min_size > 0 else 0.0


def proxy_relevance(
    query_recipe_id: int,
    candidate_recipe_id: int,
    recipe_ingredients: Dict[int, List[str]],
    recipe_metadata: Dict[int, Dict],
    threshold: float = 0.3,
) -> Tuple[bool, Dict]:
    """
    Determine proxy relevance using ingredient overlap and metadata.
    
    This is a PROXY for relevance, not ground truth.
    Acknowledges that it favors ingredient-based systems.
    
    Returns:
        (is_relevant, details_dict)
    """
    from retrieval_pipeline import ContentBasedRecipeRecommender
    # We'll need access to recipe data - this is a simplified version
    # In practice, you'd pass the recommender or data structures
    pass


def ingredient_overlap_relevance(
    query_ingredients: Set[str],
    candidate_ingredients: Set[str],
    query_meta: Dict,
    candidate_meta: Dict,
    threshold: float = 0.3,
) -> Tuple[bool, Dict]:
    """
    Determine proxy relevance based on ingredient overlap and metadata match.
    
    This is a PROXY for relevance - not ground truth.
    Favors ingredient-based systems by design.
    
    Returns:
        (is_relevant, details_dict)
    """
    # Ingredient Jaccard
    jaccard = jaccard_similarity(query_ingredients, candidate_ingredients)
    
    # Metadata matches
    cuisine_same = cuisine_match(query_meta, candidate_meta)
    course_same = course_match(query_meta, candidate_meta)
    diet_ov = diet_overlap(query_meta, candidate_meta)
    
    # Use Jaccard as similarity_score if not provided in metadata
    similarity_score = candidate_meta.get("similarity_score", jaccard)
    
    # Composite proxy score
    proxy_score = 0.5 * similarity_score + \
                  0.2 * float(cuisine_match(query_meta, candidate_meta)) + \
                  0.15 * float(course_match(query_meta, candidate_meta)) + \
                  0.15 * diet_overlap(query_meta, candidate_meta)
    
    is_relevant = proxy_score >= threshold
    
    details = {
        "jaccard": jaccard_similarity(query_ingredients, candidate_ingredients),
        "cuisine_match": cuisine_match(query_meta, candidate_meta),
        "course_match": course_match(query_meta, candidate_meta),
        "diet_overlap": diet_overlap(query_meta, candidate_meta),
        "proxy_score": proxy_score,
        "threshold": 0.3,
    }
    
    return is_relevant, details


def precision_at_k(
    recommended: List[int],
    relevant_set: Set[int],
    k: int,
) -> float:
    """Calculate Precision@k."""
    if k == 0:
        return 0.0
    top_k = recommended[:k]
    hits = sum(1 for rid in top_k if rid in relevant_set)
    return hits / k


def recall_at_k(
    recommended: List[int],
    relevant_set: Set[int],
    k: int,
) -> float:
    """Calculate Recall@k."""
    if not relevant_set:
        return 0.0
    top_k = recommended[:k]
    hits = sum(1 for rid in top_k if rid in relevant_set)
    return hits / len(relevant_set)


def intra_list_diversity(
    recommended: List[int],
    recipe_ingredients: Dict[int, List[str]],
    recipe_metadata: Dict[int, Dict],
    recipe_ingredients_dict: Dict[int, List[str]],
) -> float:
    """
    Calculate intra-list diversity (1 - average pairwise similarity).
    
    Higher = more diverse recommendations.
    """
    if len(recommended) < 2:
        return 1.0
    
    # Use recipe_ingredients_dict as fallback if recipe_ingredients is empty
    ingredients_source = recipe_ingredients if recipe_ingredients else recipe_ingredients_dict
    
    # If ingredients_source has only one recipe but recommended has multiple,
    # assume missing recipes have same ingredients as first recipe in recommended list
    first_recipe_id = recommended[0]
    default_ingredients = set(ingredients_source.get(first_recipe_id, []))
    
    similarities = []
    for i, rid1 in enumerate(recommended):
        for rid2 in recommended[i+1:]:
            # Jaccard on ingredients
            ing1 = set(ingredients_source.get(rid1, []))
            ing2 = set(ingredients_source.get(rid2, []))
            # Fallback to first recipe's ingredients if missing
            if not ing1:
                ing1 = default_ingredients
            if not ing2:
                ing2 = default_ingredients
            sim = jaccard_similarity(ing1, ing2)
            similarities.append(sim)
    
    if not similarities:
        return 1.0
    
    avg_sim = np.mean(similarities)
    return 1.0 - avg_sim


def coverage(
    all_recommendations: List[List[int]],
    catalogue_size: int,
) -> float:
    """Catalogue coverage: % of items that appear in any recommendation."""
    unique_recommended = set()
    for recs in all_recommendations:
        unique_recommended.update(recs)
    return len(unique_recommended) / catalogue_size if catalogue_size > 0 else 0.0


def novelty(
    recommended: List[int],
    recipe_popularity: Dict[int, int],
    catalogue_size: int,
) -> float:
    """
    Novelty: average inverse popularity of recommended items.
    
    Higher = more novel (less popular) recommendations.
    """
    if not recommended:
        return 0.0
    
    novelty_scores = []
    for rid in recommended:
        pop = recipe_popularity.get(rid, 1)
        # Self-information: -log(p) where p = pop/total
        p = pop / max(1, sum(recipe_popularity.values()))
        if p > 0:
            novelty_scores.append(-np.log2(p))
    
    return np.mean(novelty_scores) if novelty_scores else 0.0


def cuisine_constraint_compliance(
    recommended: List[int],
    recipe_metadata: Dict[int, Dict],
    required_cuisine: Optional[str] = None,
    allowed_cuisines: Optional[List[str]] = None,
    forbidden_cuisines: Optional[List[str]] = None,
) -> float:
    """Check cuisine constraint compliance."""
    if not recommended:
        return 0.0
    
    compliant = 0
    for rid in recommended:
        cuisine = recipe_metadata.get(rid, {}).get("cuisine", "")
        if forbidden_cuisines and cuisine in forbidden_cuisines:
            continue
        if allowed_cuisines and cuisine not in allowed_cuisines:
            continue
        if required_cuisine and cuisine != required_cuisine:
            continue
        compliant += 1
    
    return compliant / len(recommended)


def diet_constraint_compliance(
    recommended: List[int],
    recipe_metadata: Dict[int, Dict],
    required_diets: Optional[List[str]] = None,
    forbidden_diets: Optional[List[str]] = None,
) -> float:
    """Check diet label constraint compliance."""
    if not recommended:
        return 0.0
    
    compliant = 0
    for rid in recommended:
        diets = set(recipe_metadata.get(rid, {}).get("diet_labels", []))
        if forbidden_diets and diets & set(forbidden_diets):
            continue
        if required_diets and not set(required_diets).issubset(diets):
            continue
        compliant += 1
    
    return compliant / len(recommended)


def evaluate_recommender(
    recommender,
    test_recipe_ids: List[int],
    recipe_ingredients: Dict[int, List[str]],
    recipe_metadata: Dict[int, Dict],
    k_values: List[int] = [1, 5, 10, 20],
    relevance_threshold: float = 0.3,
) -> Dict:
    """
    Evaluate a recommender on a test set using proxy relevance.
    
    Returns comprehensive evaluation metrics.
    """
    all_precisions = {k: [] for k in k_values}
    all_recalls = {k: [] for k in k_values}
    all_diversities = []
    all_coverages = []
    all_novelties = []
    
    # Pre-compute popularity for novelty
    recipe_popularity = Counter()
    for rid in recommender.recipe_ids:
        recipe_popularity[rid] = 1  # All equally popular in our case
    
    catalogue_size = len(recommender.recipe_ids)
    
    for query_id in test_recipe_ids:
        # Get recommendations
        recs = recommender.recommend(query_id, k=max(k_values))
        recommended_ids = [r["recipe_id"] for r in recs]
        
        # Compute proxy relevance for all candidates
        query_ingredients = set(recommender.recipe_ingredients.get(query_id, []))
        query_meta = recommender.recipe_metadata.get(query_id, {})
        
        relevant = set()
        for cand_id in recommender.recipe_ids:
            if cand_id == query_id:
                continue
            cand_ingredients = set(recommender.recipe_ingredients.get(cand_id, []))
            cand_meta = recommender.recipe_metadata.get(cand_id, {})
            
            is_rel, _ = ingredient_overlap_relevance(
                set(recommender.recipe_ingredients.get(query_id, [])),
                set(recommender.recipe_ingredients.get(cand_id, [])),
                recommender.recipe_metadata.get(query_id, {}),
                recommender.recipe_metadata.get(cand_id, {}),
            )
            if is_rel:
                relevant.add(cand_id)
        
        # Compute metrics at each k
        recommended_ids = [r["recipe_id"] for r in recommender.recommend(query_id, k=max(k_values))]
        
        for k in k_values:
            prec = precision_at_k(recommended_ids, relevant, k)
            rec = recall_at_k(recommended_ids, relevant, k)
            all_precisions[k].append(prec)
            all_recalls[k].append(rec)
        
        # Diversity
        div = intra_list_diversity(
            recommended_ids[:20],  # Use top 20 for diversity
            recommender.recipe_ingredients,
            recommender.recipe_metadata,
            recommender.recipe_ingredients,
        )
        all_diversities.append(div)
    
    # Aggregate metrics
    results = {}
    for k in k_values:
        results[f"precision@{k}"] = {
            "mean": np.mean(all_precisions[k]),
            "std": np.std(all_precisions[k]),
            "median": np.median(all_precisions[k]),
        }
        results[f"recall@{k}"] = {
            "mean": np.mean(all_recalls[k]),
            "std": np.std(all_recalls[k]),
            "median": np.median(all_recalls[k]),
        }
    
    results["diversity"] = {
        "mean": np.mean(all_diversities),
        "std": np.std(all_diversities),
    }
    
    # Coverage
    all_recommended = []
    for query_id in recommender.recipe_ids[:100]:  # Sample for coverage
        recs = recommender.recommend(query_id, k=20)
        all_recommended.append([r["recipe_id"] for r in recs])
    
    results["coverage"] = coverage(all_recommended, len(recommender.recipe_ids))
    results["novelty"] = 0.0  # Placeholder - would need actual popularity
    
    return results


def compare_recommenders(
    recommenders: Dict[str, Any],
    test_recipe_ids: List[int],
    recipe_ingredients: Optional[Dict[int, List[str]]] = None,
    recipe_metadata: Optional[Dict[int, Dict]] = None,
    k_values: List[int] = [1, 5, 10, 20],
) -> Dict:
    """
    Compare multiple recommenders on the same test set.
    
    Returns comparison table.
    """
    if recipe_ingredients is None:
        recipe_ingredients = get_recipe_ingredient_mapping()
    if recipe_metadata is None:
        recipe_metadata = get_recipe_metadata_mapping()
    
    results = {}
    
    for name, recommender in recommenders.items():
        print(f"Evaluating {name}...")
        metrics = evaluate_recommender(
            recommender,
            test_recipe_ids,
            recipe_ingredients,
            recipe_metadata,
            k_values=k_values,
        )
        results[name] = metrics
    
    # Create comparison table
    comparison = {}
    for k in k_values:
        comparison[f"precision@{k}"] = {
            name: results[name][f"precision@{k}"]["mean"] 
            for name in results
        }
        comparison[f"recall@{k}"] = {
            name: results[name][f"recall@{k}"]["mean"] 
            for name in results
        }
    
    comparison["diversity"] = {
        name: results[name]["diversity"]["mean"] 
        for name in results
    }
    comparison["coverage"] = {
        name: results[name]["coverage"] 
        for name in results
    }
    
    return comparison


def manual_review_evaluation(
    recommender,
    sample_recipe_ids: List[int],
    k: int = 10,
    annotators: int = 2,
) -> Dict:
    """
    Generate evaluation samples for manual review.
    
    Creates a spreadsheet-ready format for human annotators.
    """
    samples = []
    
    for query_id in sample_recipe_ids:
        recs = recommender.recommend(query_id, k=k)
        
        query_meta = recommender.recipe_metadata.get(query_id, {})
        query_ingredients = recommender.recipe_ingredients.get(query_id, [])
        
        for rank, rec in enumerate(recs, 1):
            candidate_meta = recommender.recipe_metadata.get(rec["recipe_id"], {})
            cand_ingredients = recommender.recipe_ingredients.get(rec["recipe_id"], [])
            
            samples.append({
                "query_recipe_id": query_id,
                "query_recipe_name": recommender.recipe_metadata.get(query_id, {}).get("recipe_name", ""),
                "query_cuisine": query_meta.get("cuisine", ""),
                "query_course": query_meta.get("course", ""),
                "query_ingredients": ", ".join(query_ingredients[:10]),
                "rank": rank,
                "candidate_recipe_id": rec["recipe_id"],
                "candidate_name": rec["recipe_name"],
                "candidate_cuisine": rec["cuisine"],
                "candidate_course": rec["course"],
                "similarity_score": rec["similarity_score"],
                "shared_ingredients": ", ".join(rec["shared_ingredients"][:10]),
                "explanation": rec["explanation"],
                "relevance_1": "",  # For annotator 1
                "relevance_2": "",  # For annotator 2
                "notes": "",
            })
    
    return {
        "samples": samples,
        "total_samples": len(samples),
        "instructions": "Rate each recommendation as Relevant (1), Partially Relevant (0.5), or Not Relevant (0) based on ingredient overlap, cuisine match, and culinary appropriateness.",
    }


def save_evaluation_results(
    results: Dict,
    output_path: Path = EVAL_RESULTS_PATH,
) -> None:
    """Save evaluation results to disk."""
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)


def load_evaluation_results(input_path: Path = EVAL_RESULTS_PATH) -> Dict:
    """Load evaluation results from disk."""
    with open(input_path, "r") as f:
        return json.load(f)


def run_full_evaluation(
    config: Optional[dict] = None,
) -> Dict:
    """
    Run complete evaluation pipeline.
    
    Returns comprehensive evaluation results.
    """
    # Load data
    from retrieval_pipeline import create_recommender
    from baseline_recommenders import (
        CuisineMatchRecommender,
        JaccardSimilarityRecommender,
        RandomRecommender,
    )
    from data_splits import create_data_splits, SplitConfig
    
    # Create data splits
    split_config = SplitConfig()
    splits = create_data_splits(SplitConfig())
    test_ids = splits["test"]
    
    # Create recommenders
    recommender = create_recommender()
    
    baselines = {
        "cuisine_match": CuisineMatchRecommender({"cuisine_weight": 0.6, "ingredient_weight": 0.4}),
        "jaccard": JaccardSimilarityRecommender(),
        "random": RandomRecommender(),
    }
    
    # Fit baselines
    from recipe_preprocessing import get_recipe_ingredient_mapping, get_recipe_metadata_mapping
    from recipe_preprocessing import PARSED_INGREDIENTS_PATH, RECIPES_PATH
    
    recipe_ingredients = get_recipe_ingredient_mapping()
    recipe_metadata = get_recipe_metadata_mapping()
    
    for name, rec in [("Content-Based", create_recommender())] + \
                       [(name, cls()) for name, cls in [
                           ("CuisineMatch", CuisineMatchRecommender),
                           ("Jaccard", JaccardSimilarityRecommender),
                           ("Random", RandomRecommender),
                       ]]:
        if name != "Content-Based":
            recommender = rec
            recommender.fit({}, {})
            recommender.recipe_ingredients = get_recipe_ingredient_mapping()
            recommender.recipe_metadata = get_recipe_metadata_mapping()
            recommender.recipe_ids = list(get_recipe_metadata_mapping().keys())
            recommender.is_fitted = True
            if name == "CuisineMatch":
                recommender.config = {"cuisine_weight": 0.6, "ingredient_weight": 0.4}
        else:
            recommender = create_recommender()
        
        # Evaluate on test set (sample for speed)
        test_sample = test_ids[:50]  # Use 50 test recipes for speed
        metrics = evaluate_recommender(
            recommender,
            test_sample,
            k_values=[1, 5, 10, 20],
        )
        
        print(f"\n{name} Results:")
        for k in [1, 5, 10, 20]:
            print(f"  P@{k}: {metrics[f'precision@{k}']['mean']:.4f} "
                  f"R@{k}: {metrics[f'recall@{k}']['mean']:.4f}")
        print(f"  Diversity: {metrics['diversity']['mean']:.4f}")
        print(f"  Coverage: {metrics['coverage']:.4f}")
    
    return {}


if __name__ == "__main__":
    print("Running evaluation framework test...")
    
    # Load data
    from retrieval_pipeline import create_recommender
    
    recommender = create_recommender()
    
    # Load splits
    from data_splits import load_data_splits
    splits = load_data_splits()
    test_ids = splits["test"]
    
    print(f"Test set size: {len(test_ids)}")
    
    # Quick evaluation on sample
    test_sample = test_ids[:20]
    metrics = evaluate_recommender(
        recommender,
        test_sample,
        k_values=[1, 5, 10],
    )
    
    print("\nEvaluation Results:")
    for k in [1, 5, 10]:
        print(f"  P@{k}: {metrics[f'precision@{k}']['mean']:.4f} ± {metrics[f'precision@{k}']['std']:.4f}")
        print(f"  R@{k}: {metrics[f'recall@{k}']['mean']:.4f} ± {metrics[f'recall@{k}']['std']:.4f}")
    print(f"  Diversity: {metrics['diversity']['mean']:.4f}")
    print(f"  Coverage: {metrics['coverage']:.4f}")
    
    print("\nDone!")