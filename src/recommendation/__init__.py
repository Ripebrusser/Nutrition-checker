"""
Recommendation package for content-based Indian recipe recommendation.

Exports main classes and functions for:
- Recipe preprocessing
- Feature engineering
- Data splitting
- Baseline recommenders
- Retrieval pipeline
- Evaluation
- Clustering features
"""

from .recipe_preprocessing import (
    RecipePreprocessor,
    get_recipe_ingredient_mapping,
    get_recipe_metadata_mapping,
    load_recipes_dataframe,
    load_parsed_ingredients_dataframe,
)

from .recipe_features import (
    FeatureConfig,
    RecipeFeatureExtractor,
    build_recipe_feature_matrix,
    load_recipe_feature_extractor,
    ARTIFACTS_DIR,
)

from .data_splits import (
    SplitConfig,
    DataSplitter,
    create_data_splits,
    load_data_splits,
    verify_split_leakage,
    SPLITS_DIR,
)

from .baseline_recommenders import (
    BaseRecommender,
    CuisineMatchRecommender,
    JaccardSimilarityRecommender,
    RandomRecommender,
    get_baseline_recommender,
    run_baseline_comparison,
    save_baseline_outputs,
    BASELINES_DIR,
)

from .retrieval_pipeline import (
    PipelineConfig,
    RecommendationResult,
    ContentBasedRecipeRecommender,
    create_recommender,
    load_recommender_from_artifacts,
    save_recommender_artifacts,
    PIPELINE_DIR,
)

from .evaluation import (
    EvaluationConfig,
    jaccard_similarity,
    cuisine_match,
    course_match,
    diet_overlap,
    ingredient_overlap_relevance,
    precision_at_k,
    recall_at_k,
    intra_list_diversity,
    coverage,
    novelty,
    cuisine_constraint_compliance,
    diet_constraint_compliance,
    evaluate_recommender,
    compare_recommenders,
    manual_review_evaluation,
    save_evaluation_results,
    load_evaluation_results,
    run_full_evaluation,
    EVAL_DIR,
)

from .clustering_features import (
    ClusteringConfig,
    ClusteringFeatureBuilder,
    build_clustering_features,
    load_clustering_features,
    get_clustering_features,
    get_clustering_embeddings,
    CLUSTERING_DIR,
)

__all__ = [
    # Recipe preprocessing
    "RecipePreprocessor",
    "get_recipe_ingredient_mapping",
    "get_recipe_metadata_mapping",
    "load_recipes_dataframe",
    "load_parsed_ingredients_dataframe",
    
    # Feature engineering
    "FeatureConfig",
    "RecipeFeatureExtractor",
    "build_recipe_feature_matrix",
    "load_recipe_feature_extractor",
    "ARTIFACTS_DIR",
    
    # Data splits
    "SplitConfig",
    "DataSplitter",
    "create_data_splits",
    "load_data_splits",
    "verify_split_leakage",
    "SPLITS_DIR",
    
    # Baseline recommenders
    "BaseRecommender",
    "CuisineMatchRecommender",
    "JaccardSimilarityRecommender",
    "RandomRecommender",
    "get_baseline_recommender",
    "run_baseline_comparison",
    "save_baseline_outputs",
    "BASELINES_DIR",
    
    # Retrieval pipeline
    "PipelineConfig",
    "RecommendationResult",
    "ContentBasedRecipeRecommender",
    "create_recommender",
    "load_recommender_from_artifacts",
    "save_recommender_artifacts",
    "PIPELINE_DIR",
    
    # Evaluation
    "EvaluationConfig",
    "jaccard_similarity",
    "cuisine_match",
    "course_match",
    "diet_overlap",
    "ingredient_overlap_relevance",
    "precision_at_k",
    "recall_at_k",
    "intra_list_diversity",
    "coverage",
    "novelty",
    "cuisine_constraint_compliance",
    "diet_constraint_compliance",
    "evaluate_recommender",
    "compare_recommenders",
    "manual_review_evaluation",
    "save_evaluation_results",
    "load_evaluation_results",
    "run_full_evaluation",
    "EVAL_DIR",
    
    # Clustering features
    "ClusteringConfig",
    "ClusteringFeatureBuilder",
    "build_clustering_features",
    "load_clustering_features",
    "get_clustering_features",
    "get_clustering_embeddings",
    "CLUSTERING_DIR",
]

__version__ = "1.0.0"