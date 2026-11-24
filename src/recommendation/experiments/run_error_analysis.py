"""
Error Analysis for Phase 5.3
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import numpy as np
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.recommendation.retrieval_pipeline import create_recommender
from src.recommendation.baseline_recommenders import (
    CuisineMatchRecommender, JaccardSimilarityRecommender, RandomRecommender
)
from src.recommendation.recipe_preprocessing import (
    get_recipe_ingredient_mapping,
    get_recipe_metadata_mapping,
)
from src.recommendation.data_splits import load_data_splits

# Output paths
OUTPUT_DIR = Path("reports/phase5/experiments/results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run_error_analysis():
    """Run error analysis on recommender outputs."""
    print("=" * 60)
    print("PHASE 5.3: ERROR ANALYSIS")
    print("=" * 60)
    
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
    output_path = Path("reports/phase5/experiments/results/error_analysis.json")
    with open(output_path, "w") as f:
        json.dump(analysis, f, indent=2, default=str)
    
    print(f"\nError analysis saved to: {output_path}")
    
    # Print summary
    for category, items in analysis.items():
        print(f"  {category}: {len(items)} issues")
    
    return analysis


if __name__ == "__main__":
    import json
    import time
    from pathlib import Path
    from typing import Dict, List, Optional, Any, Set
    import numpy as np
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    from src.recommendation.retrieval_pipeline import create_recommender
    from src.recommendation.baseline_recommenders import (
        CuisineMatchRecommender, JaccardSimilarityRecommender, RandomRecommender
    )
    from src.recommendation.recipe_preprocessing import (
        get_recipe_ingredient_mapping,
        get_recipe_metadata_mapping,
    )
    from src.recommendation.data_splits import load_data_splits
    
    # Output paths
    OUTPUT_DIR = Path("reports/phase5/experiments/results")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    from src.recommendation.retrieval_pipeline import create_recommender
    from src.recommendation.baseline_recommenders import (
        CuisineMatchRecommender, JaccardSimilarityRecommender, RandomRecommender
    )
    from src.recommendation.recipe_preprocessing import (
        get_recipe_ingredient_mapping,
        get_recipe_metadata_mapping,
    )
    from src.recommendation.data_splits import load_data_splits
    
    # Output paths
    OUTPUT_DIR = Path("reports/phase5/experiments/results")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    run_error_analysis()