"""
Recipe feature engineering for content-based recommendation pipeline.

Implements TF-IDF on ingredients, metadata encoding, and combined feature representations.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
import pandas as pd
import numpy as np
import json
import pickle
import warnings
from collections import Counter
from dataclasses import dataclass, field
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, MultiLabelBinarizer
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np

from .recipe_preprocessing import (
    RecipePreprocessor,
    get_recipe_ingredient_mapping,
    get_recipe_metadata_mapping,
    RECIPES_PATH,
    PARSED_INGREDIENTS_PATH,
)

# Default paths for saving artifacts
ARTIFACTS_DIR = Path("data/artifacts/recommendation")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

TFIDF_VECTORIZER_PATH = ARTIFACTS_DIR / "tfidf_vectorizer.pkl"
CUISINE_ENCODER_PATH = ARTIFACTS_DIR / "cuisine_encoder.pkl"
COURSE_ENCODER_PATH = ARTIFACTS_DIR / "course_encoder.pkl"
DIET_ENCODER_PATH = ARTIFACTS_DIR / "diet_encoder.pkl"
RECIPE_FEATURES_PATH = ARTIFACTS_DIR / "recipe_features.npz"
RECIPE_IDS_PATH = ARTIFACTS_DIR / "recipe_ids.npy"
FEATURE_METADATA_PATH = ARTIFACTS_DIR / "feature_metadata.json"

# Default configuration
DEFAULT_TFIDF_MAX_FEATURES = 2000
DEFAULT_TFIDF_NGRAM_RANGE = (1, 2)
DEFAULT_TFIDF_MIN_DF = 2
DEFAULT_TFIDF_MAX_DF = 0.95
DEFAULT_RANDOM_SEED = 42


@dataclass
class FeatureConfig:
    """Configuration for feature engineering."""
    tfidf_max_features: int = DEFAULT_TFIDF_MAX_FEATURES
    tfidf_ngram_range: Tuple[int, int] = DEFAULT_TFIDF_NGRAM_RANGE
    tfidf_min_df: int = DEFAULT_TFIDF_MIN_DF
    tfidf_max_df: float = DEFAULT_TFIDF_MAX_DF
    tfidf_sublinear_tf: bool = True
    tfidf_norm: str = "l2"
    ingredient_weight: float = 1.0
    cuisine_weight: float = 1.0
    course_weight: float = 1.0
    diet_weight: float = 1.0
    random_seed: int = DEFAULT_RANDOM_SEED


class RecipeFeatureExtractor:
    """
    Extracts and manages recipe features for content-based recommendation.
    
    Handles:
    - TF-IDF on normalized ingredient text
    - One-hot encoding of cuisine, course, diet labels
    - Combined feature representations with configurable weights
    - Train/test split aware fitting (fit on train only)
    - Artifact persistence for reproducibility
    """
    
    def __init__(
        self,
        config: Optional[FeatureConfig] = None,
        artifacts_dir: Path = ARTIFACTS_DIR,
    ):
        self.config = config or FeatureConfig()
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        # Fitted transformers
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.cuisine_encoder: Optional[OneHotEncoder] = None
        self.course_encoder: Optional[OneHotEncoder] = None
        self.diet_encoder: Optional[MultiLabelBinarizer] = None
        
        # Fitted feature matrices
        self.recipe_ids: Optional[np.ndarray] = None
        self.tfidf_matrix: Optional[np.ndarray] = None
        self.cuisine_matrix: Optional[np.ndarray] = None
        self.course_matrix: Optional[np.ndarray] = None
        self.diet_matrix: Optional[np.ndarray] = None
        
        # Metadata
        self.feature_metadata: Dict = {}
        self.recipe_ids: List[int] = []
        self.is_fitted: bool = False
    
    def load_recipe_data(
        self,
        recipes_path: str = RECIPES_PATH,
        parsed_ingredients_path: str = PARSED_INGREDIENTS_PATH,
    ) -> Tuple[pd.DataFrame, Dict[int, List[str]], Dict[int, Dict]]:
        """Load recipe data and extract ingredients and metadata."""
        preprocessor = RecipePreprocessor()
        preprocessor.load_data()
        
        recipes_df = pd.read_parquet(RECIPES_PATH)
        recipe_ingredients = get_recipe_ingredient_mapping(PARSED_INGREDIENTS_PATH)
        recipe_metadata = get_recipe_metadata_mapping(RECIPES_PATH)
        
        return recipes_df, recipe_ingredients, recipe_metadata
    
    def prepare_recipe_texts(
        self,
        recipe_ingredients: Dict[int, List[str]],
        recipe_ids: List[int],
    ) -> List[str]:
        """
        Prepare ingredient text for TF-IDF.
        
        Joins normalized ingredient names into a single text per recipe.
        """
        texts = []
        for rid in recipe_ids:
            ingredients = recipe_ingredients.get(rid, [])
            if ingredients:
                # Join with space - ingredients are already normalized
                text = " ".join(ingredients)
            else:
                text = ""
            texts.append(text)
        return texts
    
    def fit(
        self,
        recipe_ingredients: Dict[int, List[str]],
        recipe_metadata: Dict[int, Dict],
        recipe_ids: Optional[List[int]] = None,
    ) -> "RecipeFeatureExtractor":
        """
        Fit all feature transformers on training data.
        
        Args:
            recipe_ingredients: Mapping from recipe_id to list of ingredient names
            recipe_metadata: Mapping from recipe_id to metadata dict
            recipe_ids: List of recipe IDs to use (if None, use all from metadata)
        
        Returns:
            Self for chaining.
        """
        if recipe_ids is None:
            recipe_ids = sorted(recipe_metadata.keys())
        
        self.recipe_ids = sorted(recipe_ids)
        n_recipes = len(self.recipe_ids)
        
        # Prepare ingredient texts
        texts = self.prepare_recipe_texts(recipe_ingredients, self.recipe_ids)
        
        # Fit TF-IDF on ingredient texts
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=self.config.tfidf_max_features,
            ngram_range=self.config.tfidf_ngram_range,
            min_df=self.config.tfidf_min_df,
            max_df=self.config.tfidf_max_df,
            sublinear_tf=self.config.tfidf_sublinear_tf,
            norm=self.config.tfidf_norm,
            lowercase=True,
            strip_accents="unicode",
            token_pattern=r"(?u)\b\w[\w\-']*\b",  # Include hyphens in tokens
        )
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
        self.tfidf_matrix = tfidf_matrix.toarray() if hasattr(tfidf_matrix, "toarray") else tfidf_matrix
        
        # Prepare metadata arrays
        cuisines = []
        courses = []
        diet_labels_list = []
        
        for rid in self.recipe_ids:
            meta = recipe_metadata.get(rid, {})
            cuisines.append(meta.get("cuisine", "Unknown"))
            courses.append(meta.get("course", "Unknown"))
            diet_labels_list.append(meta.get("diet_labels", []))
        
        # Fit cuisine encoder
        self.cuisine_encoder = OneHotEncoder(
            sparse_output=False,
            handle_unknown="ignore",
            dtype=np.float32,
        )
        cuisine_array = np.array(cuisines).reshape(-1, 1)
        self.cuisine_matrix = self.cuisine_encoder.fit_transform(cuisine_array)
        
        # Fit course encoder
        self.course_encoder = OneHotEncoder(
            sparse_output=False,
            handle_unknown="ignore",
            dtype=np.float32,
        )
        course_array = np.array(courses).reshape(-1, 1)
        self.course_matrix = self.course_encoder.fit_transform(course_array)
        
        # Fit diet label encoder (multi-label)
        self.diet_encoder = MultiLabelBinarizer(sparse_output=False)
        self.diet_matrix = self.diet_encoder.fit_transform(diet_labels_list).astype(np.float32)
        
        # Store feature metadata
        self.feature_metadata = {
            "n_recipes": n_recipes,
            "tfidf_vocab_size": len(self.tfidf_vectorizer.vocabulary_),
            "tfidf_max_features": self.config.tfidf_max_features,
            "cuisine_categories": self.cuisine_encoder.categories_[0].tolist(),
            "course_categories": self.course_encoder.categories_[0].tolist(),
            "diet_categories": self.diet_encoder.classes_.tolist(),
            "config": {
                "tfidf_max_features": self.config.tfidf_max_features,
                "tfidf_ngram_range": self.config.tfidf_ngram_range,
                "tfidf_min_df": self.config.tfidf_min_df,
                "tfidf_max_df": self.config.tfidf_max_df,
                "ingredient_weight": self.config.ingredient_weight,
                "cuisine_weight": self.config.cuisine_weight,
                "course_weight": self.config.course_weight,
                "diet_weight": self.config.diet_weight,
            },
            "recipe_ids": self.recipe_ids,
        }
        
        self.is_fitted = True
        return self
    
    def transform(
        self,
        recipe_ingredients: Dict[int, List[str]],
        recipe_metadata: Dict[int, Dict],
        recipe_ids: Optional[List[int]] = None,
    ) -> Dict[str, np.ndarray]:
        """
        Transform recipes using fitted transformers.
        
        Args:
            recipe_ingredients: Mapping from recipe_id to ingredient lists
            recipe_metadata: Mapping from recipe_id to metadata
            recipe_ids: List of recipe IDs to transform
        
        Returns:
            Dictionary with feature matrices.
        """
        if not self.is_fitted:
            raise ValueError("Feature extractor must be fitted before transform")
        
        if recipe_ids is None:
            recipe_ids = sorted(recipe_metadata.keys())
        
        # Prepare texts
        texts = self.prepare_recipe_texts(recipe_ingredients, recipe_ids)
        
        # Transform TF-IDF
        tfidf_matrix = self.tfidf_vectorizer.transform(texts)
        tfidf_array = tfidf_matrix.toarray() if hasattr(tfidf_matrix, "toarray") else tfidf_matrix
        
        # Transform metadata
        cuisines = []
        courses = []
        diet_labels_list = []
        
        for rid in recipe_ids:
            meta = recipe_metadata.get(rid, {})
            cuisines.append(meta.get("cuisine", "Unknown"))
            courses.append(meta.get("course", "Unknown"))
            diet_labels_list.append(meta.get("diet_labels", []))
        
        cuisine_array = np.array(cuisines).reshape(-1, 1)
        course_array = np.array(courses).reshape(-1, 1)
        
        cuisine_matrix = self.cuisine_encoder.transform(cuisine_array)
        course_matrix = self.course_encoder.transform(course_array)
        diet_matrix = self.diet_encoder.transform(diet_labels_list).astype(np.float32)
        
        return {
            "tfidf": tfidf_array,
            "cuisine": cuisine_matrix,
            "course": course_matrix,
            "diet": diet_matrix,
            "recipe_ids": np.array(recipe_ids),
        }
    
    def get_combined_features(
        self,
        feature_dict: Dict[str, np.ndarray],
        weights: Optional[Dict[str, float]] = None,
    ) -> np.ndarray:
        """
        Combine feature matrices with configurable weights.
        
        Args:
            feature_dict: Output from transform()
            weights: Dict with keys 'ingredient', 'cuisine', 'course', 'diet'
        
        Returns:
            Combined feature matrix.
        """
        if weights is None:
            weights = {
                "ingredient": self.config.ingredient_weight,
                "cuisine": self.config.cuisine_weight,
                "course": self.config.course_weight,
                "diet": self.config.diet_weight,
            }
        
        # Normalize each feature matrix to unit norm per sample
        def normalize_rows(mat: np.ndarray) -> np.ndarray:
            norms = np.linalg.norm(mat, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            return mat / norms
        
        tfidf_norm = normalize_rows(feature_dict["tfidf"]) * weights.get("ingredient", 1.0)
        cuisine_norm = normalize_rows(feature_dict["cuisine"]) * weights.get("cuisine", 1.0)
        course_norm = normalize_rows(feature_dict["course"]) * weights.get("course", 1.0)
        diet_norm = normalize_rows(feature_dict["diet"]) * weights.get("diet", 1.0)
        
        # Concatenate
        combined = np.hstack([tfidf_norm, cuisine_norm, course_norm, diet_norm])
        return combined
    
    def get_separate_features(self, feature_dict: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Return feature matrices separately (not combined)."""
        return {
            "tfidf": feature_dict["tfidf"],
            "cuisine": feature_dict["cuisine"],
            "course": feature_dict["course"],
            "diet": feature_dict["diet"],
        }
    
    def save_artifacts(self, artifacts_dir: Optional[Path] = None) -> None:
        """Save all fitted transformers and feature matrices."""
        if artifacts_dir is None:
            artifacts_dir = self.artifacts_dir
        artifacts_dir = Path(artifacts_dir)
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.is_fitted:
            raise ValueError("Cannot save artifacts: extractor not fitted")
        
        # Save TF-IDF vectorizer
        with open(artifacts_dir / "tfidf_vectorizer.pkl", "wb") as f:
            pickle.dump(self.tfidf_vectorizer, f)
        
        # Save encoders
        with open(artifacts_dir / "cuisine_encoder.pkl", "wb") as f:
            pickle.dump(self.cuisine_encoder, f)
        with open(artifacts_dir / "course_encoder.pkl", "wb") as f:
            pickle.dump(self.course_encoder, f)
        with open(artifacts_dir / "diet_encoder.pkl", "wb") as f:
            pickle.dump(self.diet_encoder, f)
        
        # Save feature matrices
        np.savez_compressed(
            artifacts_dir / "recipe_features.npz",
            tfidf=self.tfidf_matrix,
            cuisine=self.cuisine_matrix,
            course=self.course_matrix,
            diet=self.diet_matrix,
            recipe_ids=self.recipe_ids,
        )
        
        # Save metadata
        with open(artifacts_dir / "feature_metadata.json", "w") as f:
            json.dump(self.feature_metadata, f, indent=2, default=str)
    
    def load_artifacts(self, artifacts_dir: Optional[Path] = None) -> "RecipeFeatureExtractor":
        """Load fitted transformers and feature matrices."""
        if artifacts_dir is None:
            artifacts_dir = self.artifacts_dir
        artifacts_dir = Path(artifacts_dir)
        
        with open(artifacts_dir / "tfidf_vectorizer.pkl", "rb") as f:
            self.tfidf_vectorizer = pickle.load(f)
        with open(artifacts_dir / "cuisine_encoder.pkl", "rb") as f:
            self.cuisine_encoder = pickle.load(f)
        with open(artifacts_dir / "course_encoder.pkl", "rb") as f:
            self.course_encoder = pickle.load(f)
        with open(artifacts_dir / "diet_encoder.pkl", "rb") as f:
            self.diet_encoder = pickle.load(f)
        
        data = np.load(artifacts_dir / "recipe_features.npz")
        self.tfidf_matrix = data["tfidf"]
        self.cuisine_matrix = data["cuisine"]
        self.course_matrix = data["course"]
        self.diet_matrix = data["diet"]
        self.recipe_ids = data["recipe_ids"].tolist()
        
        with open(artifacts_dir / "feature_metadata.json", "r") as f:
            self.feature_metadata = json.load(f)
        
        self.is_fitted = True
        return self
    
    def get_feature_names(self) -> Dict[str, List[str]]:
        """Get feature names for interpretability."""
        if not self.is_fitted:
            raise ValueError("Extractor not fitted")
        
        return {
            "tfidf": self.tfidf_vectorizer.get_feature_names_out().tolist(),
            "cuisine": [f"cuisine_{c}" for c in self.cuisine_encoder.categories_[0]],
            "course": [f"course_{c}" for c in self.course_encoder.categories_[0]],
            "diet": [f"diet_{d}" for d in self.diet_encoder.classes_],
        }


def build_recipe_feature_matrix(
    recipes_path: str = RECIPES_PATH,
    parsed_ingredients_path: str = PARSED_INGREDIENTS_PATH,
    config: Optional[FeatureConfig] = None,
    artifacts_dir: Optional[Path] = None,
) -> RecipeFeatureExtractor:
    """
    Build complete recipe feature matrix from raw data.
    
    This is the main entry point for building recipe features.
    """
    if config is None:
        config = FeatureConfig()
    
    if artifacts_dir is None:
        artifacts_dir = ARTIFACTS_DIR
    
    # Load data
    preprocessor = RecipePreprocessor()
    preprocessor.load_data()
    
    recipe_ingredients = get_recipe_ingredient_mapping(PARSED_INGREDIENTS_PATH)
    recipe_metadata = get_recipe_metadata_mapping(RECIPES_PATH)
    
    # Build feature extractor
    extractor = RecipeFeatureExtractor(config=config, artifacts_dir=artifacts_dir)
    extractor.fit(recipe_ingredients, recipe_metadata)
    
    # Save artifacts
    extractor.save_artifacts(artifacts_dir)
    
    return extractor


def load_recipe_feature_extractor(
    artifacts_dir: Optional[Path] = None,
) -> RecipeFeatureExtractor:
    """Load a previously fitted feature extractor."""
    if artifacts_dir is None:
        artifacts_dir = ARTIFACTS_DIR
    extractor = RecipeFeatureExtractor(artifacts_dir=artifacts_dir)
    extractor.load_artifacts(artifacts_dir)
    return extractor


if __name__ == "__main__":
    # Quick test
    print("Building recipe feature matrix...")
    extractor = build_recipe_feature_matrix()
    print(f"Fitted on {extractor.feature_metadata['n_recipes']} recipes")
    print(f"TF-IDF vocab size: {extractor.feature_metadata['tfidf_vocab_size']}")
    print(f"Cuisine categories: {len(extractor.feature_metadata['cuisine_categories'])}")
    print(f"Course categories: {len(extractor.feature_metadata['course_categories'])}")
    print(f"Diet categories: {len(extractor.feature_metadata['diet_categories'])}")
    print("Done!")