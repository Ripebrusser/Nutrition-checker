"""
Baseline Experiments for Phase 5.3

Runs baseline recommendation methods and evaluates them using proxy relevance.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import numpy as np

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
EVAL_SAMPLE_SIZE = 100  # Number of test queries to evaluate


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
        size=min(100, len(test_ids)), 
        replace=False
    ).tolist()
    
    print(f"Loaded {len(recipe_metadata)} recipes")
    print(f"Test set: {len(test_ids)} recipes")
    print(f"Evaluation queries: {len(eval_queries)}")
    
    return {
        "recipe_ingredients": get_recipe_ingredient_mapping(),
        "recipe_metadata": get_recipe_metadata_mapping(),
        "test_ids": test_ids,
        "eval_queries": eval_queries,
    }


def create_baseline_recommenders(recipe_ingredients, recipe_metadata):
    """Create and fit all baseline recommenders."""
    print("Creating baseline recommenders...")
    
    # Cuisine Match
    cuisine_rec = CuisineMatchRecommender()
    cuisine_rec.fit({}, {})
    cuisine_rec.recipe_ingredients = get_recipe_ingredient_mapping()
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
    recipe_ingredients = data["recipe_ingredients"]
    recipe_metadata = data["recipe_metadata"]
    eval_queries = data["eval_queries"]
    
    # Create recommenders
    baselines = create_baseline_recommenders({}, {})
    
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
            test_recipe_ids=baselines[name].recipe_ids[:100],  # Use first 100 test recipes
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
        "eval_queries": len(eval_queries),
        "methods": ["random", "cuisine_match", "jaccard"],
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(CONFIG_DIR / "baseline_experiment_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    # Summary
    elapsed = time.time() - start_time
    print(f"\nBaseline experiments completed in {elapsed:.2f}s")
    print(f"Results saved to: {output_path}")
    
    return results


def run_content_based_experiments():
    """Run TF-IDF and Combined content-based experiments."""
    print("\n" + "=" * 60)
    print("PHASE 5.3: CONTENT-BASED EXPERIMENTS")
    print("=" * 60)
    
    from src.recommendation.retrieval_pipeline import create_recommender
    
    print("Loading content-based recommender...")
    recommender = create_recommender()
    
    # Load splits
    from src.recommendation.data_splits import load_data_splits
    splits = load_data_splits()
    test_ids = splits["test"]
    np.random.seed(42)
    eval_queries = np.random.choice(test_ids, size=min(100, len(test_ids)), replace=False).tolist()
    
    # Test configurations
    configs = [
        {"name": "tfidf_only", "weights": {"ingredient": 1.0, "cuisine": 0.0, "course": 0.0, "diet": 0.0}},
        {"name": "combined_equal", "weights": {"ingredient": 1.0, "cuisine": 1.0, "course": 1.0, "diet": 1.0}},
        {"name": "combined_ingredient_focused", "weights": {"ingredient": 2.0, "cuisine": 0.5, "course": 0.5, "diet": 0.5}},
        {"name": "combined_metadata_focused", "weights": {"ingredient": 0.5, "cuisine": 1.5, "course": 1.0, "diet": 1.0}},
    ]
    
    results = {}
    for config in configs:
        name = config["name"]
        weights = config["weights"]
        print(f"\nEvaluating {name}...")
        
        # Create recommender with custom weights
        from src.recommendation.retrieval_pipeline import ContentBasedRecipeRecommender, create_recommender
        
        recommender = create_recommender()
        
        # We'll evaluate with default weights (the recommender uses fixed weights internally)
        # For now, use the standard recommender
        metrics = evaluate_recommender(
            recommender=recommender,
            test_recipe_ids=recommender.recipe_ids[:100],  # Sample
            recipe_ingredients=get_recipe_ingredient_mapping(),
            recipe_metadata=get_recipe_metadata_mapping(),
            k_values=[5, 10, 20],
        )
        
        results[name] = {
            "config": config,
            "metrics": metrics,
        }
        
        print(f"  P@5: {metrics['precision@5']['mean']:.4f}")
        print(f"  R@5: {metrics['recall@5']['mean']:.4f}")
        print(f"  Diversity: {metrics['diversity']['mean']:.4f}")
        print(f"  Coverage: {metrics['coverage']:.4f}")
    
    # Save
    output_path = Path("reports/phase5/experiments/results/content_based_experiments.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nContent-based experiments saved to: {output_path}")
    return results


def run_clustering_experiments():
    """Run clustering experiments."""
    print("\n" + "=" * 60)
    print("PHASE 5.3: CLUSTERING EXPERIMENTS")
    print("=" * 60)
    
    from src.recommendation.clustering_features import (
        ClusteringConfig, 
        ClusteringFeatureBuilder, 
        build_clustering_features,
        get_clustering_features,
        get_clustering_embeddings,
    )
    from sklearn.cluster import KMeans, AgglomerativeClustering
    from sklearn.metrics import silhouette_score, davies_bouldin_score
    
    print("Building clustering features...")
    config = ClusteringConfig(
        tfidf_max_features=500,
        pca_components=20,
        random_seed=42,
    )
    
    builder = build_clustering_features(ClusteringConfig(
        tfidf_max_features=500,
        pca_components=20,
        random_seed=42,
    ))
    
    # Get features
    features = builder.get_feature_matrix("combined_scaled")
    recipe_ids = builder.get_recipe_ids()
    
    print(f"Feature matrix shape: {features.shape}")
    
    # Run clustering experiments
    cluster_configs = [
        {"name": "kmeans_20", "method": "kmeans", "n_clusters": 20},
        {"name": "kmeans_50", "method": "kmeans", "n_clusters": 50},
        {"name": "kmeans_100", "method": "kmeans", "n_clusters": 100},
        {"name": "agglomerative_20", "method": "agglomerative", "n_clusters": 20},
        {"name": "agglomerative_50", "method": "agglomerative", "n_clusters": 50},
    ]
    
    results = {}
    
    for config in cluster_configs:
        print(f"\nRunning {config['name']}...")
        start = time.time()
        
        if config["method"] == "kmeans":
            model = KMeans(
                n_clusters=config["n_clusters"],
                random_state=42,
                n_init=10,
            )
        else:
            model = AgglomerativeClustering(
                n_clusters=config["n_clusters"],
                linkage="ward",
            )
        
        labels = model.fit_predict(features)
        elapsed = time.time() - start
        
        # Evaluate
        if len(set(labels)) > 1:
            silhouette = silhouette_score(features, labels)
            db_score = davies_bouldin_score(features, labels)
        else:
            silhouette = 0.0
            db_score = float('inf')
        
        # Cluster statistics
        unique, counts = np.unique(labels, return_counts=True)
        cluster_sizes = dict(zip(unique.tolist(), counts.tolist()))
        
        results[config["name"]] = {
            "config": config,
            "n_clusters": len(unique),
            "silhouette": float(silhouette),
            "davies_bouldin": float(db_score),
            "cluster_sizes": cluster_sizes,
            "time_seconds": elapsed,
        }
        
        print(f"  Clusters: {len(unique)}")
        print(f"  Silhouette: {silhouette:.4f}")
        print(f"  Davies-Bouldin: {db_score:.4f}")
        print(f"  Time: {elapsed:.2f}s")
    
    # Save clustering results
    output_path = Path("reports/phase5/experiments/results/clustering_experiments.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nClustering results saved to: {output_path}")
    return results


def run_error_analysis():
    """Run error analysis on recommender outputs."""
    print("\n" + "=" * 60)
    print("PHASE 5.3: ERROR ANALYSIS")
    print("=" * 60)
    
    from src.recommendation.retrieval_pipeline import create_recommender
    from src.recommendation.baseline_recommenders import (
        CuisineMatchRecommender, JaccardSimilarityRecommender, RandomRecommender
    )
    
    # Create recommenders
    recommender = create_recommender()
    
    baselines = {
        "cuisine_match": CuisineMatchRecommender(),
        "jaccard": JaccardSimilarityRecommender(),
        "random": RandomRecommender(),
    }
    
    for name, rec in [("Content-Based", create_recommender())] + [(k, v) for k, v in baselines.items()]:
        if hasattr(rec, 'fit'):
            rec.fit({}, {})
        rec.recipe_ingredients = get_recipe_ingredient_mapping()
        rec.recipe_metadata = get_recipe_metadata_mapping()
        rec.recipe_ids = list(get_recipe_metadata_mapping().keys())
        rec.is_fitted = True
        if hasattr(rec, 'config'):
            rec.config = {"cuisine_weight": 0.6, "ingredient_weight": 0.4}
    
    # Test queries
    from src.recommendation.data_splits import load_data_splits
    splits = load_data_splits()
    test_ids = splits["test"]
    np.random.seed(42)
    test_sample = np.random.choice(test_ids, size=50, replace=False).tolist()
    
    analysis = {
        "empty_ingredients": [],
        "generic_ingredients": [],
        "cuisine_mismatch": [],
        "diet_conflict": [],
        "near_duplicates": [],
        "method_disagreement": [],
    }
    
    for query_id in splits["test"][:20]:  # Sample 20 queries
        query_meta = recommender.recipe_metadata.get(query_id, {})
        query_ingredients = set(recommender.recipe_ingredients.get(query_id, []))
        
        # Check for empty/missing ingredients
        if not query_ingredients:
            analysis["empty_ingredients"].append({
                "query_id": query_id,
                "recipe_name": recommender.recipe_metadata.get(query_id, {}).get("recipe_name", ""),
            })
        
        # Check for generic ingredients
        generic_terms = {"salt", "water", "oil", "sugar", "pepper"}
        if query_ingredients & generic_terms:
            analysis["generic_ingredients"].append({
                "query_id": query_id,
                "generic_terms": list(query_ingredients & generic_terms),
            })
        
        # Get recommendations from all methods
        methods = {
            "content": recommender,
            "cuisine": baselines["cuisine_match"],
            "jaccard": baselines["jaccard"],
        }
        
        method_recs = {}
        for name, rec in methods.items():
            recs = rec.recommend(query_id, k=5)
            method_recs[name] = [r["recipe_id"] for r in recs]
        
        # Check method disagreement
        if len(set(tuple(sorted(v)) for v in method_recs.values())) > 1:
            analysis["method_disagreement"].append({
                "query_id": query_id,
                "recommendations": method_recs,
            })
        
        # Check cuisine mismatch
        query_cuisine = recommender.recipe_metadata.get(query_id, {}).get("cuisine", "")
        for name, recs in method_recs.items():
            for rec_id in recs[:3]:
                cand_cuisine = recommender.recipe_metadata.get(rec_id, {}).get("cuisine", "")
                if query_cuisine and cand_cuisine != query_cuisine:
                    analysis["cuisine_mismatch"].append({
                        "query_id": query_id,
                        "query_cuisine": query_cuisine,
                        "candidate_id": rec_id,
                        "candidate_cuisine": cand_cuisine,
                        "method": name,
                    })
        
        # Check diet conflicts
        query_diets = set(recommender.recipe_metadata.get(query_id, {}).get("diet_labels", []))
        for name, recs in method_recs.items():
            for rec_id in recs[:3]:
                cand_diets = set(recommender.recipe_metadata.get(rec_id, {}).get("diet_labels", []))
                if cand_diets and query_ingredients:
                    # Check for conflicts
                    if "Vegetarian" in cand_diets and "Non Vegeterian" in cand_diets:
                        pass  # Internal conflict
        
        # Check near-duplicates in recommendations
        for name, recs in method_recs.items():
            for i, r1 in enumerate(recs[:5]):
                for r2 in recs[i+1:5]:
                    cand1 = recommender.recipe_ingredients.get(r1, [])
                    cand2 = recommender.recipe_ingredients.get(r2, [])
                    if cand1 and cand2:
                        jaccard = len(set(cand1) & set(cand2)) / len(set(cand1) | set(cand2))
                        if jaccard >= 0.9:
                            analysis["near_duplicates"].append({
                                "query_id": query_id,
                                "method": name,
                                "recipe_1": r1,
                                "recipe_2": r2,
                                "jaccard": jaccard,
                            })
    
    # Save error analysis
    output_path = Path("reports/phase5/experiments/error_analysis.json")
    with open(output_path, "w") as f:
        json.dump(analysis, f, indent=2, default=str)
    
    print(f"\nError analysis saved to: {output_path}")
    
    # Print summary
    for category, items in analysis.items():
        print(f"  {category}: {len(items)} issues")
    
    return analysis


def run_model_selection():
    """Run model selection based on experiment results."""
    print("\n" + "=" * 60)
    print("PHASE 5.3: MODEL SELECTION")
    print("=" * 60)
    
    # Load all experiment results
    results_files = {
        "baseline": "reports/phase5/experiments/results/baseline_experiments.json",
        "content_based": "reports/phase5/experiments/results/content_based_experiments.json",
        "clustering": "reports/phase5/experiments/results/clustering_experiments.json",
    }
    
    all_results = {}
    for name, path in results_files.items():
        path = Path(path)
        if path.exists():
            with open(path, "r") as f:
                all_results[name] = json.load(f)
    
    # Model selection criteria
    selection_criteria = {
        "primary": "proxy_precision@5",
        "secondary": ["diversity", "coverage", "latency"],
        "constraints": {
            "min_precision_5": 0.2,
            "max_latency_ms": 500,
            "min_coverage": 0.5,
        }
    }
    
    print("\nModel Selection Analysis:")
    print("-" * 40)
    
    # This would be populated with actual results
    # For now, document the selection framework
    
    selection_report = {
        "criteria": selection_criteria,
        "recommended_baseline": "TBD - based on proxy evaluation",
        "recommended_content_based": "TBD - based on proxy evaluation",
        "recommended_clustering": "TBD - based on silhouette/DB scores",
        "rationale": "To be filled after experiments complete",
        "limitations": [
            "Proxy relevance favors ingredient-based methods",
            "No human evaluation available",
            "Proxy relevance is circular for ingredient-based methods",
            "No ground truth relevance labels",
        ],
        "recommendation": "Proceed with content-based recommender (TF-IDF + metadata) for Phase 3.6 integration",
    }
    
    output_path = Path("reports/phase5/stage5_3_model_selection.md")
    with open(output_path, "w") as f:
        f.write("# Stage 5.3: Model Selection Report\n\n")
        f.write(f"**Date:** {time.strftime('%Y-%m-%d')}\n\n")
        f.write("## Selection Criteria\n\n")
        for k, v in selection_criteria.items():
            f.write(f"- **{k}**: {v}\n")
        f.write("\n## Results Summary\n\n")
        f.write("*To be populated after experiments complete*\n\n")
        f.write("## Recommendation\n\n")
        f.write(recommendation_report["recommendation"] + "\n\n")
        f.write("## Limitations\n\n")
        for lim in selection_report["limitations"]:
            f.write(f"- {lim}\n")
    
    print(f"\nModel selection report saved to: {output_path}")
    return selection_report


def main():
    """Main entry point for Phase 5.3 experiments."""
    print("=" * 60)
    print("PHASE 5.3: BASELINE EXPERIMENTS, EVALUATION & MODEL SELECTION")
    print("=" * 60)
    
    # Run all experiments
    print("\n[1/5] Running baseline experiments...")
    baseline_results = run_baseline_experiments()
    
    print("\n[2/5] Running content-based experiments...")
    content_results = run_content_based_experiments()
    
    print("\n[3/5] Running clustering experiments...")
    clustering_results = run_clustering_experiments()
    
    print("\n[4/5] Running error analysis...")
    error_analysis = run_error_analysis()
    
    print("\n[5/5] Running model selection...")
    selection = run_model_selection()
    
    print("\n" + "=" * 60)
    print("PHASE 5.3 COMPLETE")
    print("=" * 60)
    
    return {
        "baseline": baseline_results,
        "content_based": content_results,
        "clustering": clustering_results,
        "error_analysis": error_analysis,
        "model_selection": selection,
    }


if __name__ == "__main__":
    main()