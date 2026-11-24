"""
Simple, fast baseline experiments for Phase 5.3
Runs with smaller sample sizes for quick execution.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import numpy as np
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.recommendation.recipe_preprocessing import (
    get_recipe_ingredient_mapping,
    get_recipe_metadata_mapping,
)
from src.recommendation.baseline_recommenders import (
    CuisineMatchRecommender,
    JaccardSimilarityRecommender,
    RandomRecommender,
)
from src.recommendation.data_splits import load_data_splits
from src.recommendation.evaluation import (
    evaluate_recommender,
    compare_recommenders,
    ingredient_overlap_relevance,
    save_evaluation_results,
)

# Output paths
OUTPUT_DIR = Path("reports/phase5/experiments/results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_DIR = Path("reports/phase5/experiments/configs")
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

SUMMARY_DIR = Path("reports/phase5/experiments/summary")
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

# Fixed configuration
RANDOM_SEED = 42
K_VALUES = [5, 10, 20]
EVAL_SAMPLE_SIZE = 50  # Smaller sample for faster execution


def load_data_and_splits():
    """Load recipe data and data splits."""
    print("Loading data and splits...")
    
    recipe_ingredients = get_recipe_ingredient_mapping()
    recipe_metadata = get_recipe_metadata_mapping()
    splits = load_data_splits()
    
    test_ids = splits["test"]
    
    # Sample evaluation queries (stratified)
    np.random.seed(42)
    eval_queries = np.random.choice(
        test_ids, 
        size=min(50, len(test_ids)),  # Smaller sample for speed
        replace=False
    ).tolist()
    
    print(f"Loaded {len(get_recipe_metadata_mapping())} recipes")
    print(f"Test set: {len(test_ids)} recipes")
    print(f"Evaluation queries: {len(eval_queries)}")
    
    return {
        "recipe_ingredients": get_recipe_ingredient_mapping(),
        "recipe_metadata": get_recipe_metadata_mapping(),
        "test_ids": test_ids,
        "eval_queries": eval_queries,
    }


def create_baseline_recommenders():
    """Create and fit all baseline recommenders."""
    print("Creating baseline recommenders...")
    
    recipe_ingredients = get_recipe_ingredient_mapping()
    recipe_metadata = get_recipe_metadata_mapping()
    
    # Cuisine Match
    cuisine_rec = CuisineMatchRecommender()
    cuisine_rec.fit({}, {})
    cuisine_rec.recipe_ingredients = recipe_ingredients
    cuisine_rec.recipe_metadata = get_recipe_metadata_mapping()
    cuisine_rec.recipe_ids = list(get_recipe_metadata_mapping().keys())
    cuisine_rec.is_fitted = True
    cuisine_rec.config = {"cuisine_weight": 0.6, "ingredient_weight": 0.4}
    
    # Jaccard Similarity
    jaccard_rec = JaccardSimilarityRecommender()
    jaccard_rec.fit({}, {})
    jaccard_rec.recipe_ingredients = get_recipe_ingredient_mapping()
    jaccard_rec.recipe_metadata = get_recipe_metadata_mapping()
    jaccard_rec.recipe_ids = list(get_recipe_metadata_mapping().keys())
    jaccard_rec.is_fitted = True
    
    # Random
    random_rec = RandomRecommender()
    random_rec.fit({}, {})
    random_rec.recipe_ingredients = get_recipe_ingredient_mapping()
    random_rec.recipe_metadata = get_recipe_metadata_mapping()
    random_rec.recipe_ids = list(get_recipe_metadata_mapping().keys())
    random_rec.is_fitted = True
    
    return {
        "random": random_rec,
        "cuisine_match": cuisine_rec,
        "jaccard": jaccard_rec,
    }


def run_baseline_experiments():
    """Run all baseline experiments."""
    print("=" * 60)
    print("PHASE 5.3: BASELINE EXPERIMENTS")
    print("=" * 60)
    
    start_time = time.time()
    
    # Load data
    data = load_data_and_splits()
    eval_queries = data["eval_queries"]
    
    # Create recommenders
    baselines = create_baseline_recommenders()
    
    # Evaluate each baseline
    results = {}
    for name, recommender in {
        "random": baselines["random"],
        "cuisine_match": baselines["cuisine_match"],
        "jaccard": baselines["jaccard"],
    }.items():
        print(f"\nEvaluating {name}...")
        start = time.time()
        
        metrics = evaluate_recommender(
            recommender=recommender,
            test_recipe_ids=data["test_ids"][:50],  # Use first 50 test recipes for speed
            recipe_ingredients=get_recipe_ingredient_mapping(),
            recipe_metadata=get_recipe_metadata_mapping(),
            k_values=[5, 10, 20],
        )
        
        elapsed = time.time() - start
        results[name] = {
            "metrics": metrics,
            "time_seconds": elapsed,
        }
        print(f"  Completed in {elapsed:.2f}s")
        print(f"  P@5: {metrics['precision@5']['mean']:.4f}")
        print(f"  R@5: {metrics['recall@5']['mean']:.4f}")
        print(f"  Diversity: {metrics['diversity']['mean']:.4f}")
        print(f"  Coverage: {metrics['coverage']:.4f}")
    
    # Save results
    output_path = Path("reports/phase5/experiments/results/baseline_experiments.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    # Save config
    config = {
        "experiment": "baseline_comparison",
        "random_seed": 42,
        "k_values": [5, 10, 20],
        "eval_queries": 50,
        "methods": ["random", "cuisine_match", "jaccard"],
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(CONFIG_DIR / "baseline_experiment_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    elapsed = time.time() - start_time
    print(f"\nBaseline experiments completed in {time.time() - start_time:.2f}s")
    print(f"Results saved to: {output_path}")
    
    return results


def main():
    print("=" * 60)
    print("PHASE 5.3: BASELINE EXPERIMENTS (Fast Mode)")
    print("=" * 60)
    
    results = run_baseline_experiments()
    
    # Save summary
    summary_path = Path("reports/phase5/experiments/summary/baseline_summary.json")
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load results and create summary
    with open("reports/phase5/experiments/results/baseline_experiments.json", "r") as f:
        results = json.load(f)
    
    summary = {
        "experiment": "baseline_comparison",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "methods": list(results.keys()),
        "results": {
            name: {
                "precision@5": results[name]["metrics"]["precision@5"]["mean"],
                "recall@5": results[name]["metrics"]["recall@5"]["mean"],
                "diversity": results[name]["metrics"]["diversity"]["mean"],
                "coverage": results[name]["metrics"]["coverage"],
                "time_seconds": results[name]["time_seconds"],
            }
            for name in results
        }
    }
    
    with open("reports/phase5/experiments/summary/baseline_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    
    print("\nBaseline experiments complete!")
    return results


if __name__ == "__main__":
    main()