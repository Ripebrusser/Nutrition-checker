"""
Tests for clustering features module.
"""

import pytest
import numpy as np
import tempfile
from pathlib import Path

from src.recommendation.clustering_features import (
    ClusteringConfig,
    ClusteringFeatureBuilder,
    build_clustering_features,
    load_clustering_features,
    get_clustering_features,
    get_clustering_embeddings,
    CLUSTERING_DIR,
)


class TestClusteringConfig:
    """Tests for ClusteringConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = ClusteringConfig()
        assert config.tfidf_max_features == 2000
        assert config.tfidf_ngram_range == (1, 2)
        assert config.tfidf_min_df == 2
        assert config.tfidf_max_df == 0.95
        assert config.include_ingredients is True
        assert config.include_cuisine is True
        assert config.include_course is True
        assert config.include_diet is True
        assert config.pca_components == 50
        assert config.umap_n_neighbors == 15
        assert config.umap_min_dist == 0.1
        assert config.umap_n_components == 2
        assert config.tsne_perplexity == 30
        assert config.tsne_n_components == 2
        assert config.scale_features is True
        assert config.random_seed == 42
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = ClusteringConfig(
            tfidf_max_features=1000,
            pca_components=20,
            random_seed=123,
        )
        assert config.tfidf_max_features == 1000
        assert config.pca_components == 20
        assert config.random_seed == 123


class TestClusteringFeatureBuilder:
    """Tests for ClusteringFeatureBuilder."""
    
    @pytest.fixture(scope="class")
    def builder(self):
        """Create a fitted builder for testing."""
        config = ClusteringConfig(
            tfidf_max_features=100,
            pca_components=10,
            random_seed=42,
        )
        builder = ClusteringFeatureBuilder(config=config)
        builder.load_data()
        builder.build_features()
        return builder
    
    def test_load_data(self, builder):
        """Test data loading."""
        assert len(builder.recipe_ids) == 6865
        assert len(builder.recipe_ingredients) == 6865
        assert len(builder.recipe_metadata) == 6865
    
    def test_prepare_texts(self, builder):
        """Test text preparation for TF-IDF."""
        texts = builder.prepare_texts(builder.recipe_ids[:5])
        assert len(texts) == 5
        assert all(isinstance(t, str) for t in texts)
        # Check ingredients are joined
        for text in texts:
            if text:
                assert " " in text or len(text.split()) == 1
    
    def test_build_features(self, builder):
        """Test feature building."""
        assert builder.is_fitted
        
        # Check feature matrices exist
        assert "tfidf" in builder.feature_matrices
        assert "cuisine" in builder.feature_matrices
        assert "course" in builder.feature_matrices
        assert "diet" in builder.feature_matrices
        assert "combined" in builder.feature_matrices
        assert "combined_scaled" in builder.feature_matrices
        
        # Check shapes
        n = len(builder.recipe_ids)
        assert builder.feature_matrices["tfidf"].shape[0] == n
        assert builder.feature_matrices["cuisine"].shape[0] == n
        assert builder.feature_matrices["course"].shape[0] == n
        assert builder.feature_matrices["diet"].shape[0] == n
        assert builder.feature_matrices["combined"].shape[0] == n
        assert builder.feature_matrices["combined_scaled"].shape[0] == n
    
    def test_tfidf_features(self, builder):
        """Test TF-IDF feature matrix."""
        tfidf = builder.feature_matrices["tfidf"]
        assert tfidf.shape[0] == len(builder.recipe_ids)
        assert tfidf.shape[1] <= 100  # max_features=100
        # Check L2 normalization (allow zero norms for empty documents)
        norms = np.linalg.norm(tfidf, axis=1)
        # Allow zero norms for empty documents
        non_zero_norms = norms[norms > 0]
        np.testing.assert_allclose(non_zero_norms, 1.0, rtol=1e-5)
    
    def test_metadata_encoding(self, builder):
        """Test metadata encoding."""
        # Cuisine
        cuisine = builder.feature_matrices["cuisine"]
        assert cuisine.shape[0] == len(builder.recipe_ids)
        assert cuisine.shape[1] > 1  # Multiple cuisines
        # Check one-hot
        row_sums = cuisine.sum(axis=1)
        np.testing.assert_allclose(row_sums, 1.0, rtol=1e-5)
        
        # Course
        course = builder.feature_matrices["course"]
        assert course.shape[0] == len(builder.recipe_ids)
        row_sums = course.sum(axis=1)
        np.testing.assert_allclose(row_sums, 1.0, rtol=1e-5)
        
        # Diet
        diet = builder.feature_matrices["diet"]
        assert diet.shape[0] == len(builder.recipe_ids)
        # Multi-label, so rows can have multiple 1s
        assert np.all((diet == 0) | (diet == 1))
    
    def test_combined_features(self, builder):
        """Test combined feature matrix."""
        combined = builder.feature_matrices["combined"]
        assert combined.shape[0] == len(builder.recipe_ids)
        # Should have TF-IDF + cuisine + course + diet features
        expected_cols = (builder.config.tfidf_max_features + 
                        builder.feature_matrices["cuisine"].shape[1] +
                        builder.feature_matrices["course"].shape[1] +
                        builder.feature_matrices["diet"].shape[1])
        assert combined.shape[1] == expected_cols
    
    def test_scaled_features(self, builder):
        """Test scaled features."""
        scaled = builder.feature_matrices["combined_scaled"]
        assert scaled.shape == builder.feature_matrices["combined"].shape
        # Check zero mean, unit variance (approximately)
        means = np.mean(builder.feature_matrices["combined_scaled"], axis=0)
        stds = np.std(builder.feature_matrices["combined_scaled"], axis=0)
        np.testing.assert_allclose(means, 0, atol=1e-10)
        np.testing.assert_allclose(stds, 1.0, rtol=0.1)
    
    def test_pca_embedding(self, builder):
        """Test PCA embedding."""
        assert "pca" in builder.embeddings
        pca = builder.embeddings["pca"]
        assert pca is not None
        assert pca.shape[0] == len(builder.recipe_ids)
        assert pca.shape[1] <= 10  # pca_components=10
        
        # Check explained variance
        assert "pca_explained_variance" in builder.embeddings
        var = builder.embeddings["pca_explained_variance"]
        assert len(var) == builder.config.pca_components
        assert np.sum(var) <= 1.0
    
    def test_umap_embedding(self, builder):
        """Test UMAP embedding (if available)."""
        # UMAP might not be available in test environment
        if "umap" in builder.embeddings and builder.embeddings["umap"] is not None:
            umap = builder.embeddings["umap"]
            assert umap.shape[0] == len(builder.recipe_ids)
            assert umap.shape[1] == 2  # umap_n_components=2
    
    def test_tsne_embedding(self, builder):
        """Test t-SNE embedding."""
        assert "tsne" in builder.embeddings
        tsne = builder.embeddings["tsne"]
        assert tsne is not None
        assert tsne.shape[0] == len(builder.recipe_ids)
        assert tsne.shape[1] == 2  # tsne_n_components=2
    
    def test_get_feature_matrix(self, builder):
        """Test getting feature matrix by name."""
        tfidf = builder.get_feature_matrix("tfidf")
        assert tfidf is not None
        assert tfidf.shape[0] == len(builder.recipe_ids)
        
        # Non-existent
        assert builder.get_feature_matrix("nonexistent") is None
    
    def test_get_embedding(self, builder):
        """Test getting embedding by name."""
        pca = builder.get_embedding("pca")
        assert pca is not None
        
        umap = builder.get_embedding("umap")
        # May be None if UMAP not available
        
        tsne = builder.get_embedding("tsne")
        assert tsne is not None
        
        assert builder.get_embedding("nonexistent") is None
    
    def test_get_recipe_ids(self, builder):
        """Test getting recipe IDs."""
        ids = builder.get_recipe_ids()
        assert len(ids) == 6865
        assert all(isinstance(x, int) for x in ids)
    
    def test_save_load_artifacts(self):
        """Test saving and loading artifacts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            artifacts_dir = Path(tmpdir) / "test_clustering"
            
            config = ClusteringConfig(
                tfidf_max_features=50,
                pca_components=5,
                random_seed=42,
            )
            builder = ClusteringFeatureBuilder(config=config, artifacts_dir=artifacts_dir)
            builder.load_data()
            builder.build_features()
            builder.save_artifacts()
            
            # Load artifacts
            loaded = load_clustering_features(artifacts_dir)
            
            assert loaded.is_fitted
            assert loaded.recipe_ids == builder.recipe_ids
            
            # Check matrices match
            for key in builder.feature_matrices:
                if key in loaded.feature_matrices:
                    np.testing.assert_array_almost_equal(
                        loaded.feature_matrices[key],
                        builder.feature_matrices[key]
                    )


class TestClusteringFeatureFunctions:
    """Tests for clustering feature utility functions."""
    
    def test_build_clustering_features(self):
        """Test build_clustering_features function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            artifacts_dir = Path(tmpdir) / "test_clustering"
            
            config = ClusteringConfig(
                tfidf_max_features=50,
                pca_components=5,
                random_seed=42,
            )
            builder = build_clustering_features(config=config, artifacts_dir=artifacts_dir)
            
            assert builder.is_fitted
            assert len(builder.recipe_ids) == 6865
            
            # Check artifacts saved - add small delay for Windows file system
            import time
            time.sleep(0.1)
            assert (Path(artifacts_dir) / "clustering_features.npz").exists()
            assert (Path(artifacts_dir) / "clustering_metadata.json").exists()
    
    def test_load_clustering_features(self):
        """Test load_clustering_features function."""
        import time
        with tempfile.TemporaryDirectory() as tmpdir:
            artifacts_dir = Path(tmpdir) / "test_clustering"
            
            config = ClusteringConfig(
                tfidf_max_features=50,
                pca_components=5,
                random_seed=42,
            )
            builder = build_clustering_features(config=config, artifacts_dir=artifacts_dir)
            
            # Small delay to ensure files are written
            time.sleep(0.1)
            loaded = load_clustering_features(artifacts_dir)
            assert loaded.is_fitted
            assert loaded.recipe_ids == builder.recipe_ids
    
    def test_get_clustering_features(self):
        """Test get_clustering_features utility function."""
        import time
        with tempfile.TemporaryDirectory() as tmpdir:
            artifacts_dir = Path(tmpdir) / "test_clustering"
            
            config = ClusteringConfig(
                tfidf_max_features=50,
                pca_components=5,
                random_seed=42,
            )
            build_clustering_features(config=config, artifacts_dir=artifacts_dir)
            time.sleep(0.1)
            
            # Test getting different feature types
            for feature_type in ["tfidf", "cuisine", "course", "diet", "combined", "combined_scaled"]:
                features, ids = get_clustering_features(feature_type, artifacts_dir)
                assert features is not None
                assert len(ids) == 6865
                assert features.shape[0] == 6865
            
            # Non-existent type
            features, ids = get_clustering_features("nonexistent", artifacts_dir)
            assert features is None
    
    def test_get_clustering_embeddings(self):
        """Test get_clustering_embeddings utility function."""
        import time
        with tempfile.TemporaryDirectory() as tmpdir:
            artifacts_dir = Path(tmpdir) / "test_clustering"
            
            config = ClusteringConfig(
                tfidf_max_features=50,
                pca_components=5,
                random_seed=42,
            )
            build_clustering_features(config=config, artifacts_dir=artifacts_dir)
            time.sleep(0.1)
            
            # Test getting embeddings
            for emb_type in ["pca", "tsne"]:
                emb, ids = get_clustering_embeddings(emb_type, artifacts_dir)
                assert emb is not None
                assert len(ids) == 6865
                assert emb.shape[0] == 6865
            
            # UMAP might not be available
            umap_emb, umap_ids = get_clustering_embeddings("umap", artifacts_dir)
            if umap_emb is not None:
                assert umap_emb.shape[0] == 6865
            
            # Non-existent
            emb, ids = get_clustering_embeddings("nonexistent", artifacts_dir)
            assert emb is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])