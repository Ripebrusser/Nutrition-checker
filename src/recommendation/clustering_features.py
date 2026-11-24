"""
Recipe clustering features for secondary experiment.

Prepares feature representations for unsupervised clustering of recipes.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
import json
import pickle
import os
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, MultiLabelBinarizer, StandardScaler
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.manifold import TSNE
import warnings

warnings.filterwarnings("ignore")

from .recipe_preprocessing import (
    get_recipe_ingredient_mapping,
    get_recipe_metadata_mapping,
    RECIPES_PATH,
    PARSED_INGREDIENTS_PATH,
)
from .recipe_features import FeatureConfig, RecipeFeatureExtractor, ARTIFACTS_DIR

# Default paths
CLUSTERING_DIR = ARTIFACTS_DIR / "clustering"
CLUSTERING_DIR.mkdir(parents=True, exist_ok=True)

CLUSTERING_FEATURES_PATH = CLUSTERING_DIR / "clustering_features.npz"
CLUSTERING_METADATA_PATH = CLUSTERING_DIR / "clustering_metadata.json"
UMAP_EMBEDDING_PATH = CLUSTERING_DIR / "umap_embedding.npy"
TSNE_EMBEDDING_PATH = CLUSTERING_DIR / "tsne_embedding.npy"
PCA_MODEL_PATH = CLUSTERING_DIR / "pca_model.pkl"
UMAP_MODEL_PATH = CLUSTERING_DIR / "umap_model.pkl"


@dataclass
class ClusteringConfig:
    """Configuration for clustering feature preparation."""
    # TF-IDF settings
    tfidf_max_features: int = 2000
    tfidf_ngram_range: Tuple[int, int] = (1, 2)
    tfidf_min_df: int = 2
    tfidf_max_df: float = 0.95
    
    # Feature inclusion
    include_ingredients: bool = True
    include_cuisine: bool = True
    include_course: bool = True
    include_diet: bool = True
    
    # Dimensionality reduction
    pca_components: int = 50
    umap_n_neighbors: int = 15
    umap_min_dist: float = 0.1
    umap_n_components: int = 2
    tsne_perplexity: int = 30
    tsne_n_components: int = 2
    
    # Feature scaling
    scale_features: bool = True
    
    # Reproducibility
    random_seed: int = 42


class ClusteringFeatureBuilder:
    """
    Builds feature representations for recipe clustering.
    
    Creates multiple feature representations suitable for clustering:
    - TF-IDF on ingredients
    - Metadata encodings (cuisine, course, diet)
    - Combined representations
    - Dimensionality-reduced embeddings (PCA, UMAP, t-SNE)
    """
    
    def __init__(
        self,
        config: Optional[ClusteringConfig] = None,
        artifacts_dir: Optional[Path] = None,
    ):
        self.config = config or ClusteringConfig()
        if artifacts_dir is not None:
            self.artifacts_dir = Path(artifacts_dir)
        elif hasattr(self.config, 'artifacts_dir') and self.config.artifacts_dir:
            self.artifacts_dir = Path(self.config.artifacts_dir)
        else:
            self.artifacts_dir = CLUSTERING_DIR
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        # Data
        self.recipe_ids: List[int] = []
        self.recipe_ingredients: Dict[int, List[str]] = {}
        self.recipe_metadata: Dict[int, Dict] = {}
        
        # Fitted transformers
        self.tfidf_vectorizer: Optional[Any] = None
        self.cuisine_encoder: Optional[Any] = None
        self.course_encoder: Optional[Any] = None
        self.diet_encoder: Optional[Any] = None
        self.scaler: Optional[Any] = None
        self.pca_model: Optional[Any] = None
        self.umap_model: Optional[Any] = None
        
        # Feature matrices
        self.feature_matrices: Dict[str, np.ndarray] = {}
        self.embeddings: Dict[str, np.ndarray] = {}
        self.recipe_ids: List[int] = []
        
        self.is_fitted: bool = False
    
    def load_data(self) -> None:
        """Load recipe data."""
        from .recipe_preprocessing import RecipePreprocessor, get_recipe_ingredient_mapping, get_recipe_metadata_mapping
        preprocessor = RecipePreprocessor()
        preprocessor.load_data()
        
        self.recipe_ingredients = get_recipe_ingredient_mapping(PARSED_INGREDIENTS_PATH)
        self.recipe_metadata = get_recipe_metadata_mapping(RECIPES_PATH)
        self.recipe_ids = sorted(self.recipe_metadata.keys())
    
    def prepare_texts(self, recipe_ids: List[int]) -> List[str]:
        """Prepare ingredient texts for TF-IDF."""
        texts = []
        for rid in recipe_ids:
            ingredients = self.recipe_ingredients.get(rid, [])
            text = " ".join(ingredients) if ingredients else ""
            texts.append(text)
        return texts
    
    def build_features(self) -> "ClusteringFeatureBuilder":
        """Build all feature representations."""
        if not self.recipe_ids:
            self.load_data()
        
        # Prepare texts for TF-IDF
        texts = self.prepare_texts(self.recipe_ids)
        
        # TF-IDF on ingredients
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=self.config.tfidf_max_features,
            ngram_range=self.config.tfidf_ngram_range,
            min_df=self.config.tfidf_min_df,
            max_df=self.config.tfidf_max_df,
            sublinear_tf=True,
            norm="l2",
        )
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(
            self.prepare_texts(self.recipe_ids)
        )
        tfidf_dense = tfidf_matrix.toarray()
        self.feature_matrices["tfidf"] = tfidf_dense
        
        # Metadata features
        cuisines = []
        courses = []
        diet_labels = []
        
        for rid in self.recipe_ids:
            meta = self.recipe_metadata.get(rid, {})
            cuisines.append(meta.get("cuisine", "Unknown"))
            courses.append(meta.get("course", "Unknown"))
            diet_labels.append(meta.get("diet_labels", []))
        
        # One-hot encode cuisine
        from sklearn.preprocessing import OneHotEncoder
        self.cuisine_encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        cuisine_array = np.array(cuisines).reshape(-1, 1)
        cuisine_encoded = self.cuisine_encoder.fit_transform(cuisine_array)
        self.feature_matrices["cuisine"] = cuisine_encoded
        
        # One-hot encode course
        self.course_encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        course_array = np.array(courses).reshape(-1, 1)
        course_encoded = self.course_encoder.fit_transform(course_array)
        self.feature_matrices["course"] = course_encoded
        
        # Multi-label encode diet
        from sklearn.preprocessing import MultiLabelBinarizer
        self.diet_encoder = MultiLabelBinarizer(sparse_output=False)
        diet_encoded = self.diet_encoder.fit_transform(diet_labels)
        self.feature_matrices["diet"] = diet_encoded.astype(np.float32)
        
        # Combine features
        self._build_combined_features()
        
        # Dimensionality reduction
        self._compute_pca()
        self._compute_umap()
        self._compute_tsne()
        
        self.is_fitted = True
        return self
    
    def _build_combined_features(self) -> None:
        """Build combined feature matrix with configurable weights."""
        matrices = []
        weights = []
        
        if self.config.include_ingredients and "tfidf" in self.feature_matrices:
            matrices.append(self.feature_matrices["tfidf"])
            weights.append(1.0)
        
        if self.config.include_cuisine and "cuisine" in self.feature_matrices:
            matrices.append(self.feature_matrices["cuisine"])
            weights.append(0.5)
        
        if self.config.include_course and "course" in self.feature_matrices:
            matrices.append(self.feature_matrices["course"])
            weights.append(0.3)
        
        if self.config.include_diet and "diet" in self.feature_matrices:
            matrices.append(self.feature_matrices["diet"])
            weights.append(0.3)
        
        # Scale each matrix to unit norm per sample before combining
        def normalize(mat):
            norms = np.linalg.norm(mat, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            return mat / norms
        
        weighted_matrices = [normalize(m) * w for m, w in zip(matrices, weights)]
        combined = np.hstack(weighted_matrices)
        
        self.feature_matrices["combined"] = combined
        
        # Optional scaling
        if self.config.scale_features:
            from sklearn.preprocessing import StandardScaler
            self.scaler = StandardScaler()
            self.feature_matrices["combined_scaled"] = self.scaler.fit_transform(combined)
        else:
            self.feature_matrices["combined_scaled"] = combined
    
    def _compute_pca(self) -> None:
        """Compute PCA on combined features."""
        from sklearn.decomposition import PCA
        
        features = self.feature_matrices.get("combined_scaled", self.feature_matrices["combined"])
        
        n_components = min(self.config.pca_components, features.shape[1], features.shape[0] - 1)
        
        self.pca_model = PCA(
            n_components=n_components,
            random_state=self.config.random_seed,
        )
        pca_embedding = self.pca_model.fit_transform(features)
        
        self.embeddings["pca"] = pca_embedding
        self.embeddings["pca_explained_variance"] = self.pca_model.explained_variance_ratio_
    
    def _compute_umap(self) -> None:
        """Compute UMAP embedding."""
        try:
            import umap
        except ImportError:
            print("UMAP not available, skipping UMAP embedding")
            self.embeddings["umap"] = None
            return
        
        features = self.feature_matrices.get("combined_scaled", self.feature_matrices["combined"])
        
        self.umap_model = umap.UMAP(
            n_neighbors=self.config.umap_n_neighbors,
            min_dist=self.config.umap_min_dist,
            n_components=self.config.umap_n_components,
            random_state=self.config.random_seed,
            metric="cosine",
        )
        umap_embedding = self.umap_model.fit_transform(self.feature_matrices["combined"])
        
        self.embeddings["umap"] = umap_embedding
    
    def _compute_tsne(self) -> None:
        """Compute t-SNE embedding (on PCA-reduced features for efficiency)."""
        from sklearn.manifold import TSNE
        
        # Use PCA-reduced features for t-SNE
        pca_features = self.embeddings.get("pca")
        if pca_features is None:
            features = self.feature_matrices.get("combined_scaled", self.feature_matrices["combined"])
        else:
            features = pca_features
        
        n_samples = features.shape[0]
        perplexity = min(self.config.tsne_perplexity, max(5, n_samples // 10))
        
        self.tsne_model = TSNE(
            n_components=self.config.tsne_n_components,
            perplexity=perplexity,
            random_state=self.config.random_seed,
            metric="cosine",
            max_iter=1000,
            init="pca" if pca_features is not None else "random",
        )
        tsne_embedding = self.tsne_model.fit_transform(features)
        
        self.embeddings["tsne"] = tsne_embedding
    
    def get_feature_matrix(self, name: str) -> Optional[np.ndarray]:
        """Get a feature matrix by name."""
        return self.feature_matrices.get(name)
    
    def get_embedding(self, name: str) -> Optional[np.ndarray]:
        """Get an embedding by name."""
        return self.embeddings.get(name)
    
    def get_recipe_ids(self) -> List[int]:
        return self.recipe_ids
    
    def save_artifacts(self, artifacts_dir: Optional[Path] = None) -> None:
        """Save all artifacts to disk."""
        if artifacts_dir is None:
            artifacts_dir = self.artifacts_dir
        artifacts_dir = Path(artifacts_dir)
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.is_fitted:
            raise ValueError("Cannot save: not fitted")
        
        # Save feature matrices
        np.savez_compressed(
            artifacts_dir / "clustering_features.npz",
            **self.feature_matrices,
        )
        
        # Save embeddings
        np.savez_compressed(
            artifacts_dir / "clustering_embeddings.npz",
            **{k: v for k, v in self.embeddings.items() if v is not None},
        )
        
        # Save transformers
        with open(artifacts_dir / "tfidf_vectorizer.pkl", "wb") as f:
            pickle.dump(self.tfidf_vectorizer, f)
        
        with open(artifacts_dir / "cuisine_encoder.pkl", "wb") as f:
            pickle.dump(self.cuisine_encoder, f)
        
        with open(artifacts_dir / "course_encoder.pkl", "wb") as f:
            pickle.dump(self.course_encoder, f)
        
        with open(artifacts_dir / "diet_encoder.pkl", "wb") as f:
            pickle.dump(self.diet_encoder, f)
        
        if self.scaler:
            with open(artifacts_dir / "scaler.pkl", "wb") as f:
                pickle.dump(self.scaler, f)
        
        if self.pca_model:
            with open(artifacts_dir / "pca_model.pkl", "wb") as f:
                pickle.dump(self.pca_model, f)
        
        if hasattr(self, 'umap_model') and self.umap_model:
            try:
                with open(artifacts_dir / "umap_model.pkl", "wb") as f:
                    pickle.dump(self.umap_model, f)
            except:
                pass  # UMAP models may not be picklable
        
        # Save metadata
        metadata = {
            "recipe_ids": self.recipe_ids,
            "config": {
                "tfidf_max_features": self.config.tfidf_max_features,
                "tfidf_ngram_range": self.config.tfidf_ngram_range,
                "tfidf_min_df": self.config.tfidf_min_df,
                "tfidf_max_df": self.config.tfidf_max_df,
                "include_ingredients": True,
                "include_cuisine": True,
                "include_course": True,
                "include_diet": True,
                "pca_components": self.config.pca_components,
            },
            "feature_shapes": {k: v.shape for k, v in self.feature_matrices.items()},
            "embedding_shapes": {k: v.shape for k, v in self.embeddings.items() if v is not None},
        }
        
        metadata_path = artifacts_dir / "clustering_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2, default=str)
            f.flush()
            os.fsync(f.fileno())
    
    def load_artifacts(self, artifacts_dir: Optional[Path] = None) -> "ClusteringFeatureBuilder":
        """Load all artifacts from disk."""
        if artifacts_dir is None:
            artifacts_dir = self.artifacts_dir
        artifacts_dir = Path(artifacts_dir)
        
        # Load feature matrices
        data = np.load(artifacts_dir / "clustering_features.npz")
        self.feature_matrices = {k: data[k] for k in data.files}
        
        # Load embeddings
        if (artifacts_dir / "clustering_embeddings.npz").exists():
            emb_data = np.load(artifacts_dir / "clustering_embeddings.npz")
            self.embeddings = {k: emb_data[k] for k in emb_data.files}
        
        # Load transformers
        with open(artifacts_dir / "tfidf_vectorizer.pkl", "rb") as f:
            self.tfidf_vectorizer = pickle.load(f)
        with open(artifacts_dir / "cuisine_encoder.pkl", "rb") as f:
            self.cuisine_encoder = pickle.load(f)
        with open(artifacts_dir / "course_encoder.pkl", "rb") as f:
            self.course_encoder = pickle.load(f)
        with open(artifacts_dir / "diet_encoder.pkl", "rb") as f:
            self.diet_encoder = pickle.load(f)
        
        if (artifacts_dir / "scaler.pkl").exists():
            with open(artifacts_dir / "scaler.pkl", "rb") as f:
                self.scaler = pickle.load(f)
        
        if (artifacts_dir / "pca_model.pkl").exists():
            with open(artifacts_dir / "pca_model.pkl", "rb") as f:
                self.pca_model = pickle.load(f)
        
        # Load metadata
        with open(artifacts_dir / "clustering_metadata.json", "r") as f:
            metadata = json.load(f)
            self.recipe_ids = metadata["recipe_ids"]
        
        self.is_fitted = True
        return self


def build_clustering_features(
    config: Optional[ClusteringConfig] = None,
    artifacts_dir: Optional[Path] = None,
) -> ClusteringFeatureBuilder:
    """
    Build clustering feature representations from raw data.
    
    Main entry point.
    """
    if config is None:
        config = ClusteringConfig()
    
    if artifacts_dir is None:
        artifacts_dir = CLUSTERING_DIR
    
    builder = ClusteringFeatureBuilder(config=config, artifacts_dir=artifacts_dir)
    builder.load_data()
    builder.build_features()
    builder.save_artifacts(artifacts_dir)
    
    return builder


def load_clustering_features(
    artifacts_dir: Optional[Path] = None,
) -> ClusteringFeatureBuilder:
    """Load previously built clustering features."""
    if artifacts_dir is None:
        artifacts_dir = CLUSTERING_DIR
    
    builder = ClusteringFeatureBuilder(artifacts_dir=artifacts_dir)
    builder.load_artifacts(artifacts_dir)
    return builder


def get_clustering_features(
    feature_type: str = "combined",
    artifacts_dir: Path = CLUSTERING_DIR,
) -> Tuple[np.ndarray, List[int]]:
    """
    Quick access to clustering features.
    
    Args:
        feature_type: One of "tfidf", "cuisine", "course", "diet", "combined", "combined_scaled"
        artifacts_dir: Directory with saved features
    
    Returns:
        (feature_matrix, recipe_ids)
    """
    builder = load_clustering_features(artifacts_dir)
    features = builder.get_feature_matrix(feature_type)
    return features, builder.get_recipe_ids()


def get_clustering_embeddings(
    embedding_type: str = "pca",
    artifacts_dir: Path = CLUSTERING_DIR,
) -> Tuple[np.ndarray, List[int]]:
    """
    Quick access to clustering embeddings.
    
    Args:
        embedding_type: One of "pca", "umap", "tsne"
        artifacts_dir: Directory with saved embeddings
    
    Returns:
        (embedding_matrix, recipe_ids)
    """
    builder = load_clustering_features(artifacts_dir)
    embedding = builder.get_embedding(embedding_type)
    return embedding, builder.get_recipe_ids()


if __name__ == "__main__":
    print("Building clustering features...")
    
    builder = build_clustering_features()
    
    print(f"\nFeature matrix shapes:")
    for name, mat in builder.feature_matrices.items():
        print(f"  {name}: {mat.shape}")
    
    print(f"\nEmbedding shapes:")
    for name, emb in builder.embeddings.items():
        if emb is not None:
            print(f"  {name}: {emb.shape}")
    
    print(f"\nRecipe IDs: {len(builder.recipe_ids)}")
    print("\nDone!")