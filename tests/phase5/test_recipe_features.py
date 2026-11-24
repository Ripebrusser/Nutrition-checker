"""
Tests for recipe feature engineering module.
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import tempfile
import shutil

from src.recommendation.recipe_features import (
    FeatureConfig,
    RecipeFeatureExtractor,
    build_recipe_feature_matrix,
    load_recipe_feature_extractor,
    ARTIFACTS_DIR,
)
from src.recommendation.recipe_preprocessing import (
    get_recipe_ingredient_mapping,
    get_recipe_metadata_mapping,
)


class TestFeatureConfig:
    """Tests for FeatureConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = FeatureConfig()
        assert config.tfidf_max_features == 2000
        assert config.tfidf_ngram_range == (1, 2)
        assert config.tfidf_min_df == 2
        assert config.tfidf_max_df == 0.95
        assert config.ingredient_weight == 1.0
        assert config.cuisine_weight == 1.0
        assert config.course_weight == 1.0
        assert config.diet_weight == 1.0
        assert config.random_seed == 42
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = FeatureConfig(
            tfidf_max_features=1000,
            ingredient_weight=0.5,
            cuisine_weight=2.0,
        )
        assert config.tfidf_max_features == 1000
        assert config.ingredient_weight == 0.5
        assert config.cuisine_weight == 2.0


class TestRecipeFeatureExtractor:
    """Tests for RecipeFeatureExtractor."""
    
    @pytest.fixture(scope="class")
    def recipe_data(self):
        """Load recipe data for testing."""
        from src.recommendation.recipe_preprocessing import RecipePreprocessor
        preprocessor = RecipePreprocessor()
        preprocessor.load_data()
        recipe_ingredients = get_recipe_ingredient_mapping()
        recipe_metadata = get_recipe_metadata_mapping()
        return recipe_ingredients, recipe_metadata
    
    def test_feature_config_defaults(self):
        """Test FeatureConfig default values."""
        config = FeatureConfig()
        assert config.tfidf_max_features == 2000
        assert config.tfidf_ngram_range == (1, 2)
        assert config.tfidf_min_df == 2
        assert config.tfidf_max_df == 0.95
    
    def test_fit_transform_cycle(self, recipe_data):
        """Test fit and transform cycle."""
        recipe_ingredients, recipe_metadata = recipe_data
        recipe_ids = list(recipe_metadata.keys())[:100]  # Use subset for speed
        
        config = FeatureConfig(tfidf_max_features=100)
        extractor = RecipeFeatureExtractor(config=config)
        extractor.fit(recipe_ingredients, recipe_metadata, recipe_ids)
        
        assert extractor.is_fitted
        assert len(extractor.recipe_ids) == 100
        assert extractor.tfidf_matrix.shape[0] == 100
        assert extractor.tfidf_matrix.shape[1] <= 100  # max_features=100
        
        # Test transform
        features = extractor.transform(recipe_ingredients, recipe_metadata, recipe_ids)
        assert "tfidf" in features
        assert "cuisine" in features
        assert "course" in features
        assert "diet" in features
        assert features["tfidf"].shape[0] == 100
        assert features["cuisine"].shape[0] == 100
    
    def test_tfidf_vocabulary(self, recipe_data):
        """Test TF-IDF vocabulary extraction."""
        recipe_ingredients, recipe_metadata = recipe_data
        recipe_ids = list(recipe_metadata.keys())[:50]
        
        config = FeatureConfig(tfidf_max_features=50)
        extractor = RecipeFeatureExtractor(config=config)
        extractor.fit(recipe_ingredients, recipe_metadata, recipe_ids)
        
        vocab = extractor.tfidf_vectorizer.get_feature_names_out()
        assert len(vocab) <= 50
        assert all(isinstance(term, str) for term in vocab)
    
    def test_cuisine_encoding(self, recipe_data):
        """Test cuisine one-hot encoding."""
        recipe_ingredients, recipe_metadata = recipe_data
        recipe_ids = list(recipe_metadata.keys())[:100]
        
        config = FeatureConfig(tfidf_max_features=100)
        extractor = RecipeFeatureExtractor(config=config)
        extractor.fit(recipe_ingredients, recipe_metadata, recipe_ids)
        
        cuisine_matrix = extractor.cuisine_matrix
        assert cuisine_matrix.shape[0] == 100
        assert cuisine_matrix.shape[1] > 1  # Multiple cuisines
        
        # Check one-hot property: each row sums to 1
        row_sums = extractor.cuisine_matrix.sum(axis=1)
        np.testing.assert_allclose(row_sums, 1.0, rtol=1e-5)
    
    def test_course_encoding(self, recipe_data):
        """Test course one-hot encoding."""
        recipe_ingredients, recipe_metadata = recipe_data
        recipe_ids = list(recipe_metadata.keys())[:100]
        
        config = FeatureConfig(tfidf_max_features=100)
        extractor = RecipeFeatureExtractor(config=config)
        extractor.fit(recipe_ingredients, recipe_metadata, recipe_ids)
        
        course_matrix = extractor.course_matrix
        assert course_matrix.shape[0] == 100
        assert course_matrix.shape[1] > 1
        
        # Check one-hot property
        row_sums = extractor.course_matrix.sum(axis=1)
        np.testing.assert_allclose(row_sums, 1.0, rtol=1e-5)
    
    def test_diet_encoding(self, recipe_data):
        """Test diet label multi-label binarization."""
        recipe_ingredients, recipe_metadata = recipe_data
        recipe_ids = list(recipe_metadata.keys())[:100]
        
        config = FeatureConfig(tfidf_max_features=100)
        extractor = RecipeFeatureExtractor(config=config)
        extractor.fit(recipe_ingredients, recipe_metadata, recipe_ids)
        
        diet_matrix = extractor.diet_matrix
        assert diet_matrix.shape[0] == 100
        assert diet_matrix.shape[1] > 1
        
        # Check values are binary
        assert np.all((diet_matrix == 0) | (diet_matrix == 1))
    
    def test_get_combined_features(self, recipe_data):
        """Test combined feature matrix creation."""
        recipe_ingredients, recipe_metadata = recipe_data
        recipe_ids = list(recipe_metadata.keys())[:50]
        
        config = FeatureConfig(
            tfidf_max_features=50,
            ingredient_weight=1.0,
            cuisine_weight=0.5,
            course_weight=0.3,
            diet_weight=0.2,
        )
        extractor = RecipeFeatureExtractor(config=config)
        extractor.fit(recipe_ingredients, recipe_metadata, recipe_ids)
        
        features = extractor.transform(recipe_ingredients, recipe_metadata, recipe_ids)
        combined = extractor.get_combined_features(features)
        
        assert combined.shape[0] == 50
        # Should have TF-IDF + cuisine + course + diet features
        expected_cols = 50 + len(extractor.cuisine_encoder.categories_[0]) + \
                        len(extractor.course_encoder.categories_[0]) + \
                        len(extractor.diet_encoder.classes_)
        assert combined.shape[1] == expected_cols
    
    def test_get_separate_features(self, recipe_data):
        """Test getting separate feature matrices."""
        recipe_ingredients, recipe_metadata = recipe_data
        recipe_ids = list(recipe_metadata.keys())[:50]
        
        config = FeatureConfig(tfidf_max_features=50)
        extractor = RecipeFeatureExtractor(config=config)
        extractor.fit(recipe_ingredients, recipe_metadata, recipe_ids)
        
        features = extractor.transform(recipe_ingredients, recipe_metadata, recipe_ids)
        separate = extractor.get_separate_features(features)
        
        assert "tfidf" in separate
        assert "cuisine" in separate
        assert "course" in separate
        assert "diet" in separate
        
        # Check shapes match original matrices
        assert separate["tfidf"].shape == extractor.tfidf_matrix.shape
        assert separate["cuisine"].shape == extractor.cuisine_matrix.shape
        assert separate["course"].shape == extractor.course_matrix.shape
        assert separate["diet"].shape == extractor.diet_matrix.shape
    
    def test_feature_names(self, recipe_data):
        """Test getting feature names for interpretability."""
        recipe_ingredients, recipe_metadata = recipe_data
        recipe_ids = list(recipe_metadata.keys())[:50]
        
        config = FeatureConfig(tfidf_max_features=50)
        extractor = RecipeFeatureExtractor(config=config)
        extractor.fit(recipe_ingredients, recipe_metadata, recipe_ids)
        
        names = extractor.get_feature_names()
        
        assert "tfidf" in names
        assert "cuisine" in names
        assert "course" in names
        assert "diet" in names
        
        assert len(names["tfidf"]) <= 50
        assert len(names["cuisine"]) == len(extractor.cuisine_encoder.categories_[0])
        assert len(names["course"]) == len(extractor.course_encoder.categories_[0])
        assert len(names["diet"]) == len(extractor.diet_encoder.classes_)
    
    def test_save_load_artifacts(self, recipe_data):
        """Test saving and loading artifacts."""
        recipe_ingredients, recipe_metadata = recipe_data
        recipe_ids = list(recipe_metadata.keys())[:50]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            artifacts_dir = Path(tmpdir) / "test_artifacts"
            
            config = FeatureConfig(tfidf_max_features=50)
            extractor = RecipeFeatureExtractor(config=config, artifacts_dir=artifacts_dir)
            extractor.fit(recipe_ingredients, recipe_metadata, recipe_ids)
            extractor.save_artifacts()
            
            # Load artifacts
            loaded = load_recipe_feature_extractor(artifacts_dir)
            
            assert loaded.is_fitted
            assert loaded.recipe_ids == extractor.recipe_ids
            assert loaded.feature_metadata["n_recipes"] == extractor.feature_metadata["n_recipes"]
            
            # Check matrices match
            np.testing.assert_array_almost_equal(
                loaded.tfidf_matrix, extractor.tfidf_matrix
            )
            np.testing.assert_array_almost_equal(
                loaded.cuisine_matrix, extractor.cuisine_matrix
            )
    
    def test_build_recipe_feature_matrix(self):
        """Test the main entry point function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            artifacts_dir = Path(tmpdir) / "test_artifacts"
            
            config = FeatureConfig(tfidf_max_features=100)
            extractor = build_recipe_feature_matrix(artifacts_dir=artifacts_dir, config=config)
            
            assert extractor.is_fitted
            assert extractor.feature_metadata["n_recipes"] == 6865
            assert extractor.feature_metadata["tfidf_vocab_size"] <= 100


class TestFeatureConfigValidation:
    """Tests for FeatureConfig validation."""
    
    def test_invalid_ngram_range(self):
        """Test that invalid ngram ranges are handled."""
        # This should not raise an error - validation is in TfidfVectorizer
        config = FeatureConfig(tfidf_ngram_range=(2, 1))
        assert config.tfidf_ngram_range == (2, 1)
    
    def test_weight_configuration(self):
        """Test weight configuration."""
        config = FeatureConfig(
            ingredient_weight=0.5,
            cuisine_weight=2.0,
            course_weight=0.5,
            diet_weight=0.0,
        )
        assert config.ingredient_weight == 0.5
        assert config.cuisine_weight == 2.0
        assert config.course_weight == 0.5
        assert config.diet_weight == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])