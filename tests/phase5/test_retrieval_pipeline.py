"""
Tests for retrieval pipeline module.
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile

from src.recommendation.retrieval_pipeline import (
    PipelineConfig,
    RecommendationResult,
    ContentBasedRecipeRecommender,
    create_recommender,
    load_recommender_from_artifacts,
    save_recommender_artifacts,
    PIPELINE_DIR,
)
from src.recommendation.recipe_preprocessing import (
    get_recipe_ingredient_mapping,
    get_recipe_metadata_mapping,
)


class TestPipelineConfig:
    """Tests for PipelineConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = PipelineConfig()
        assert config.ingredient_weight == 1.0
        assert config.cuisine_weight == 1.0
        assert config.course_weight == 1.0
        assert config.diet_weight == 1.0
        assert config.max_recommendations == 10
        assert config.min_similarity_threshold == 0.0
        assert config.cuisine_weight_baseline == 0.6
        assert config.ingredient_weight_baseline == 0.4
        assert config.tfidf_max_features == 2000
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = PipelineConfig(
            ingredient_weight=0.5,
            cuisine_weight=2.0,
            max_recommendations=20,
        )
        assert config.ingredient_weight == 0.5
        assert config.cuisine_weight == 2.0
        assert config.max_recommendations == 20


class TestRecommendationResult:
    """Tests for RecommendationResult dataclass."""
    
    def test_creation(self):
        """Test creating a recommendation result."""
        result = RecommendationResult(
            recipe_id=123,
            recipe_name="Test Recipe",
            similarity_score=0.85,
            cuisine="Indian",
            course="Main Course",
            diet_labels=["Vegetarian"],
            shared_ingredients=["onion", "tomato"],
            cuisine_match=1.0,
            ingredient_overlap=0.75,
            explanation="Same cuisine, shares 2 ingredients",
            component_scores={"ingredient": 0.75, "cuisine": 1.0},
        )
        
        assert result.recipe_id == 123
        assert result.similarity_score == 0.85
        assert result.cuisine == "Indian"
        assert len(result.shared_ingredients) == 2
        assert result.component_scores["ingredient"] == 0.75
    
    def test_to_dict(self):
        """Test serialization to dict."""
        result = RecommendationResult(
            recipe_id=123,
            recipe_name="Test Recipe",
            similarity_score=0.85,
            cuisine="Indian",
            course="Main Course",
            diet_labels=["Vegetarian"],
            shared_ingredients=["onion", "tomato"],
            cuisine_match=1.0,
            ingredient_overlap=0.75,
            explanation="Test explanation",
        )
        
        d = result.to_dict()
        assert d["recipe_id"] == 123
        assert d["recipe_name"] == "Test Recipe"
        assert d["similarity_score"] == 0.85
        assert d["cuisine"] == "Indian"
        assert d["shared_ingredients"] == ["onion", "tomato"]
        assert "explanation" in d


class TestContentBasedRecipeRecommender:
    """Tests for ContentBasedRecipeRecommender."""
    
    @pytest.fixture(scope="class")
    def recommender(self):
        """Create a fitted recommender for testing."""
        from src.recommendation.retrieval_pipeline import create_recommender
        return create_recommender()
    
    def test_initialization(self):
        """Test recommender initialization."""
        recommender = ContentBasedRecipeRecommender()
        assert not recommender.is_fitted
        assert recommender.recipe_ids == []
        assert recommender.recipe_ingredients == {}
    
    def test_fit(self):
        """Test fitting the recommender."""
        from src.recommendation.recipe_preprocessing import (
            get_recipe_ingredient_mapping,
            get_recipe_metadata_mapping,
        )
        
        recipe_ingredients = get_recipe_ingredient_mapping()
        recipe_metadata = get_recipe_metadata_mapping()
        
        recommender = ContentBasedRecipeRecommender()
        recommender.fit(recipe_ingredients, recipe_metadata)
        
        assert recommender.is_fitted
        assert len(recommender.recipe_ids) == 6865
        assert len(recommender.recipe_ingredients) == 6865
        assert len(recommender.recipe_metadata) == 6865
        assert len(recommender.recipe_id_to_idx) == 6865
    
    def test_jaccard_similarity(self):
        """Test Jaccard similarity calculation."""
        recommender = ContentBasedRecipeRecommender()
        
        # Test cases
        assert recommender._jaccard_similarity(set(), set()) == 0.0
        assert recommender._jaccard_similarity({"a", "b"}, {"a", "b"}) == 1.0
        assert recommender._jaccard_similarity({"a", "b"}, {"b", "c"}) == 1/3
        assert recommender._jaccard_similarity({"a"}, {"b"}) == 0.0
        assert recommender._jaccard_similarity(set(), {"a"}) == 0.0
    
    def test_cuisine_similarity(self):
        """Test cuisine similarity calculation."""
        recommender = ContentBasedRecipeRecommender()
        
        assert recommender._cuisine_similarity("Indian", "Indian") == 1.0
        assert recommender._cuisine_similarity("Indian", "Continental") == 0.0
        assert recommender._cuisine_similarity("", "Indian") == 0.0
        assert recommender._cuisine_similarity("Indian", "") == 0.0
    
    def test_get_shared_ingredients(self):
        """Test getting shared ingredients."""
        recommender = ContentBasedRecipeRecommender()
        
        shared = recommender._get_shared_ingredients({"a", "b", "c"}, {"b", "c", "d"})
        assert set(shared) == {"b", "c"}
        
        shared = recommender._get_shared_ingredients(set(), {"a"})
        assert shared == []
    
    def test_recommend(self):
        """Test basic recommendation."""
        recommender = create_recommender()
        
        # Test with first recipe
        query_id = list(recommender.recipe_metadata.keys())[0]
        recs = recommender.recommend(query_id, k=5)
        
        assert len(recs) <= 5
        assert len(recs) > 0
        
        # Check structure
        for rec in recs:
            assert "recipe_id" in rec
            assert "recipe_name" in rec
            assert "similarity_score" in rec
            assert "cuisine" in rec
            assert "course" in rec
            assert "diet_labels" in rec
            assert "shared_ingredients" in rec
            assert "cuisine_match" in rec
            assert "ingredient_overlap" in rec
            assert "explanation" in rec
            assert "component_scores" in rec
        
        # Check scores are descending
        scores = [r["similarity_score"] for r in recs]
        assert scores == sorted(scores, reverse=True)
        
        # Query recipe should not be in results
        query_id = list(recs[0]["recipe_id"] for r in [recs[0]])[0] if recs else None
        # Actually, just check query is not in results
        query_id = list(recommender.recipe_metadata.keys())[0]
        result_ids = [r["recipe_id"] for r in recs]
        assert query_id not in result_ids
    
    def test_recommend_with_filters(self):
        """Test recommendations with filters."""
        from src.recommendation.retrieval_pipeline import create_recommender
        
        recommender = create_recommender()
        
        # Test cuisine filter
        query_id = list(recommender.recipe_metadata.keys())[0]
        recs = recommender.recommend(query_id, k=10, filters={"cuisine": "Indian"})
        
        for rec in recs:
            assert rec["cuisine"] == "Indian"
        
        # Test course filter
        recs = recommender.recommend(query_id, k=10, filters={"course": "Main Course"})
        for rec in recs:
            assert rec["course"] == "Main Course"
        
        # Test diet filter
        recs = recommender.recommend(query_id, k=10, filters={"diet_labels": ["Vegetarian"]})
        for rec in recs:
            assert "Vegetarian" in rec["diet_labels"]
    
    def test_recommend_by_ingredients(self):
        """Test recommending by ingredient list."""
        from src.recommendation.retrieval_pipeline import create_recommender
        
        recommender = create_recommender()
        
        # Test with ingredients
        ingredients = ["onion", "tomato", "cumin"]
        recs = recommender.recommend_by_ingredients(ingredients, k=5)
        
        assert len(recs) <= 5
        for rec in recs:
            assert "recipe_id" in rec
            assert "similarity_score" in rec
            assert rec["similarity_score"] > 0
    
    def test_recommend_by_ingredients_with_filters(self):
        """Test recommending by ingredients with filters."""
        from src.recommendation.retrieval_pipeline import create_recommender
        
        recommender = create_recommender()
        
        ingredients = ["onion", "tomato"]
        recs = recommender.recommend_by_ingredients(
            ingredients, k=5, filters={"cuisine": "Indian"}
        )
        
        for rec in recs:
            assert rec["cuisine"] == "Indian"
    
    def test_get_recipe_details(self):
        """Test getting recipe details."""
        from src.recommendation.retrieval_pipeline import create_recommender
        
        recommender = create_recommender()
        recipe_id = list(recommender.recipe_metadata.keys())[0]
        
        details = recommender.get_recipe_details(recipe_id)
        
        assert details is not None
        assert details["recipe_id"] == recipe_id
        assert "recipe_name" in details
        assert "cuisine" in details
        assert "ingredients" in details
    
    def test_get_recipe_details_not_found(self):
        """Test getting details for non-existent recipe."""
        from src.recommendation.retrieval_pipeline import create_recommender
        
        recommender = create_recommender()
        details = recommender.get_recipe_details(999999)
        assert details is None
    
    def test_fit_not_called_error(self):
        """Test that recommend fails if not fitted."""
        recommender = ContentBasedRecipeRecommender()
        
        with pytest.raises(ValueError, match="not fitted"):
            recommender.recommend(1, k=5)
    
    def test_query_not_found_error(self):
        """Test that querying unknown recipe raises error."""
        from src.recommendation.retrieval_pipeline import create_recommender
        
        recommender = create_recommender()
        with pytest.raises(ValueError, match="not found"):
            recommender.recommend(999999, k=5)


class TestCreateRecommender:
    """Tests for create_recommender factory function."""
    
    def test_create_recommender(self):
        """Test creating recommender from raw data."""
        recommender = create_recommender()
        
        assert isinstance(recommender, ContentBasedRecipeRecommender)
        assert recommender.is_fitted
        assert len(recommender.recipe_ids) == 6865
    
    def test_create_with_config(self):
        """Test creating recommender with custom config."""
        config = {"ingredient_weight": 0.5, "cuisine_weight": 2.0}
        recommender = create_recommender(config=config)
        
        assert recommender.config["ingredient_weight"] == 0.5
        assert recommender.config["cuisine_weight"] == 2.0


class TestSaveLoadArtifacts:
    """Tests for saving and loading recommender artifacts."""
    
    def test_save_load_artifacts(self):
        """Test saving and loading recommender artifacts."""
        from src.recommendation.retrieval_pipeline import create_recommender, save_recommender_artifacts, load_recommender_from_artifacts
        
        with tempfile.TemporaryDirectory() as tmpdir:
            artifacts_dir = Path(tmpdir) / "test_artifacts"
            
            recommender = create_recommender()
            save_recommender_artifacts(recommender, artifacts_dir)
            
            # Check files exist
            assert (Path(artifacts_dir) / "pipeline_config.json").exists()
            
            # Load recommender
            loaded = load_recommender_from_artifacts(artifacts_dir)
            
            assert loaded.is_fitted
            assert len(loaded.recipe_ids) == 6865


if __name__ == "__main__":
    pytest.main([__file__, "-v"])