"""
Tests for baseline recommenders module.
"""

import pytest
import numpy as np
from collections import Counter

from src.recommendation.baseline_recommenders import (
    BaseRecommender,
    CuisineMatchRecommender,
    JaccardSimilarityRecommender,
    RandomRecommender,
    get_baseline_recommender,
    run_baseline_comparison,
    BASELINE_OUTPUTS_DIR,
)
from src.recommendation.recipe_preprocessing import (
    get_recipe_ingredient_mapping,
    get_recipe_metadata_mapping,
)


class TestBaseRecommender:
    """Tests for base recommender functionality."""
    
    @pytest.fixture(scope="class")
    def recipe_data(self):
        """Load recipe data for testing."""
        recipe_ingredients = get_recipe_ingredient_mapping()
        recipe_metadata = get_recipe_metadata_mapping()
        return recipe_ingredients, recipe_metadata
    
    def test_recommender_interface(self, recipe_data):
        """Test that BaseRecommender defines the interface."""
        recipe_ingredients, recipe_metadata = recipe_data
        
        # BaseRecommender is abstract, can't instantiate directly
        # But we can test that subclasses implement required methods
        recommender = JaccardSimilarityRecommender()
        recommender.fit({}, {})
        recommender.recipe_ingredients = get_recipe_ingredient_mapping()
        recommender.recipe_metadata = get_recipe_metadata_mapping()
        recommender.recipe_ids = list(get_recipe_metadata_mapping().keys())
        recommender.is_fitted = True
        
        assert hasattr(recommender, "recommend")
        assert callable(recommender.recommend)


class TestCuisineMatchRecommender:
    """Tests for CuisineMatchRecommender."""
    
    @pytest.fixture(scope="class")
    def recipe_data(self):
        recipe_ingredients = get_recipe_ingredient_mapping()
        recipe_metadata = get_recipe_metadata_mapping()
        return recipe_ingredients, recipe_metadata
    
    def test_initialization(self):
        """Test recommender initialization."""
        config = {"cuisine_weight": 0.7, "ingredient_weight": 0.3}
        recommender = CuisineMatchRecommender(config)
        
        assert recommender.cuisine_weight == 0.7
        assert recommender.ingredient_weight == 0.3
        assert "Indian" in recommender.region_mapping
        assert "Continental" in recommender.region_mapping
    
    def test_default_weights(self):
        """Test default weights."""
        recommender = CuisineMatchRecommender()
        assert recommender.cuisine_weight == 0.6
        assert recommender.ingredient_weight == 0.4
    
    def test_cuisine_similarity(self):
        """Test cuisine similarity calculation."""
        recommender = CuisineMatchRecommender()
        
        # Same cuisine
        assert recommender._cuisine_similarity("Indian", "Indian") == 1.0
        
        # Different cuisine
        assert recommender._cuisine_similarity("Indian", "Continental") == 0.0
        
        # Same region
        assert recommender._cuisine_similarity("North Indian Recipes", "South Indian Recipes") == 0.5
    
    def test_jaccard_similarity(self):
        """Test Jaccard similarity calculation."""
        recommender = CuisineMatchRecommender()
        
        # Identical sets
        assert recommender._jaccard_similarity({"a", "b", "c"}, {"a", "b", "c"}) == 1.0
        
        # Partial overlap
        assert recommender._jaccard_similarity({"a", "b"}, {"b", "c"}) == 1/3
        
        # No overlap
        assert recommender._jaccard_similarity({"a", "b"}, {"c", "d"}) == 0.0
        
        # Empty set
        assert recommender._jaccard_similarity(set(), {"a", "b"}) == 0.0
        assert recommender._jaccard_similarity(set(), set()) == 0.0
    
    def test_recommend(self):
        """Test recommendation generation."""
        from src.recommendation.recipe_preprocessing import get_recipe_ingredient_mapping, get_recipe_metadata_mapping
        
        recipe_ingredients = get_recipe_ingredient_mapping()
        recipe_metadata = get_recipe_metadata_mapping()
        
        recommender = CuisineMatchRecommender()
        recommender.fit({}, {})
        recommender.recipe_ingredients = {k: v for k, v in get_recipe_ingredient_mapping().items()}
        recommender.recipe_metadata = get_recipe_metadata_mapping()
        recommender.recipe_ids = list(get_recipe_metadata_mapping().keys())
        recommender.is_fitted = True
        
        # Test with first recipe
        query_id = list(get_recipe_metadata_mapping().keys())[0]
        recs = recommender.recommend(query_id, k=5)
        
        assert len(recs) <= 5
        assert len(recs) > 0
        
        # Check structure
        for rec in recs:
            assert "recipe_id" in rec
            assert "recipe_name" in rec
            assert "similarity_score" in rec
            assert "cuisine_match" in rec
            assert "ingredient_overlap" in rec
            assert "explanation" in rec
            assert "shared_ingredients" in rec
            assert "cuisine" in rec
            assert "course" in rec
            assert "diet_labels" in rec
        
        # Check scores are in descending order
        scores = [r["similarity_score"] for r in recs]
        assert scores == sorted(scores, reverse=True)
    
    def test_exclude_query_recipe(self):
        """Test that query recipe is excluded from recommendations."""
        from src.recommendation.recipe_preprocessing import get_recipe_ingredient_mapping, get_recipe_metadata_mapping
        
        recommender = CuisineMatchRecommender()
        recommender.fit({}, {})
        recommender.recipe_ingredients = get_recipe_ingredient_mapping()
        recommender.recipe_metadata = get_recipe_metadata_mapping()
        recommender.recipe_ids = list(get_recipe_metadata_mapping().keys())
        recommender.is_fitted = True
        
        query_id = list(get_recipe_metadata_mapping().keys())[0]
        recs = recommender.recommend(query_id, k=10)
        
        # Query recipe should not be in results
        recipe_ids = [r["recipe_id"] for r in recs]
        assert query_id not in recipe_ids
    
    def test_exclude_list(self):
        """Test exclude list functionality."""
        from src.recommendation.recipe_preprocessing import get_recipe_ingredient_mapping, get_recipe_metadata_mapping
        
        recommender = CuisineMatchRecommender()
        recommender.fit({}, {})
        recommender.recipe_ingredients = get_recipe_ingredient_mapping()
        recommender.recipe_metadata = get_recipe_metadata_mapping()
        recommender.recipe_ids = list(get_recipe_metadata_mapping().keys())
        recommender.is_fitted = True
        
        query_id = list(get_recipe_metadata_mapping().keys())[0]
        # Exclude second recipe
        exclude_id = list(get_recipe_metadata_mapping().keys())[1]
        recs = recommender.recommend(query_id, k=5, exclude=[exclude_id])
        
        recipe_ids = [r["recipe_id"] for r in recs]
        assert exclude_id not in recipe_ids


class TestJaccardSimilarityRecommender:
    """Tests for JaccardSimilarityRecommender."""
    
    def test_initialization(self):
        """Test initialization."""
        recommender = JaccardSimilarityRecommender()
        assert recommender.config == {}
    
    def test_jaccard_similarity(self):
        """Test Jaccard similarity method."""
        recommender = JaccardSimilarityRecommender()
        
        # Identical sets
        assert recommender._jaccard({"a", "b", "c"}, {"a", "b", "c"}) == 1.0
        
        # Partial overlap
        assert recommender._jaccard({"a", "b"}, {"b", "c"}) == 1/3
        
        # No overlap
        assert recommender._jaccard({"a", "b"}, {"c", "d"}) == 0.0
        
        # Empty set
        assert recommender._jaccard(set(), {"a", "b"}) == 0.0
        assert recommender._jaccard(set(), set()) == 0.0
    
    def test_recommend(self):
        """Test recommendation generation."""
        from src.recommendation.recipe_preprocessing import get_recipe_ingredient_mapping, get_recipe_metadata_mapping
        
        recommender = JaccardSimilarityRecommender()
        recommender.fit({}, {})
        recommender.recipe_ingredients = get_recipe_ingredient_mapping()
        recommender.recipe_metadata = get_recipe_metadata_mapping()
        recommender.recipe_ids = list(get_recipe_metadata_mapping().keys())
        recommender.is_fitted = True
        
        query_id = list(get_recipe_metadata_mapping().keys())[0]
        recs = recommender.recommend(query_id, k=5)
        
        assert len(recs) <= 5
        assert len(recs) > 0
        
        for rec in recs:
            assert "recipe_id" in rec
            assert "recipe_name" in rec
            assert "similarity_score" in rec
            assert "shared_ingredients" in rec
            assert "explanation" in rec
            assert rec["similarity_score"] >= 0
        
        # Scores should be descending
        scores = [r["similarity_score"] for r in recs]
        assert scores == sorted(scores, reverse=True)
    
    def test_exclude_query(self):
        """Test query recipe exclusion."""
        from src.recommendation.recipe_preprocessing import get_recipe_ingredient_mapping, get_recipe_metadata_mapping
        
        recommender = JaccardSimilarityRecommender()
        recommender.fit({}, {})
        recommender.recipe_ingredients = get_recipe_ingredient_mapping()
        recommender.recipe_metadata = get_recipe_metadata_mapping()
        recommender.recipe_ids = list(get_recipe_metadata_mapping().keys())
        recommender.is_fitted = True
        
        query_id = list(get_recipe_metadata_mapping().keys())[0]
        recs = recommender.recommend(query_id, k=10)
        
        recipe_ids = [r["recipe_id"] for r in recs]
        assert query_id not in recipe_ids


class TestRandomRecommender:
    """Tests for RandomRecommender."""
    
    def test_initialization(self):
        """Test initialization with seed."""
        recommender = RandomRecommender({"random_seed": 123})
        assert recommender.random_seed == 123
        assert recommender._rng is not None
    
    def test_recommend(self):
        """Test random recommendations."""
        from src.recommendation.recipe_preprocessing import get_recipe_ingredient_mapping, get_recipe_metadata_mapping
        
        recommender = RandomRecommender({"random_seed": 42})
        recommender.fit({}, {})
        recommender.recipe_ingredients = get_recipe_ingredient_mapping()
        recommender.recipe_metadata = get_recipe_metadata_mapping()
        recommender.recipe_ids = list(get_recipe_metadata_mapping().keys())
        recommender.is_fitted = True
        
        query_id = list(get_recipe_metadata_mapping().keys())[0]
        recs = recommender.recommend(query_id, k=5)
        
        assert len(recs) <= 5
        assert len(recs) > 0
        
        for rec in recs:
            assert "recipe_id" in rec
            assert "similarity_score" in rec
            assert rec["similarity_score"] == 0.0  # Random has no similarity
            assert rec["explanation"] == "Random recommendation (baseline)"
    
    def test_reproducibility(self):
        """Test that same seed produces same results."""
        from src.recommendation.recipe_preprocessing import get_recipe_ingredient_mapping, get_recipe_metadata_mapping
        
        recipe_ingredients = get_recipe_ingredient_mapping()
        recipe_metadata = get_recipe_metadata_mapping()
        
        rec1 = RandomRecommender({"random_seed": 42})
        rec1.fit({}, {})
        rec1.recipe_ingredients = get_recipe_ingredient_mapping()
        rec1.recipe_metadata = get_recipe_metadata_mapping()
        rec1.recipe_ids = list(get_recipe_metadata_mapping().keys())
        rec1.is_fitted = True
        
        rec2 = RandomRecommender({"random_seed": 42})
        rec2.fit({}, {})
        rec2.recipe_ingredients = get_recipe_ingredient_mapping()
        rec2.recipe_metadata = get_recipe_metadata_mapping()
        rec2.recipe_ids = list(get_recipe_metadata_mapping().keys())
        rec2.is_fitted = True
        
        query_id = list(get_recipe_metadata_mapping().keys())[0]
        recs1 = rec1.recommend(0, k=5)
        recs2 = rec2.recommend(0, k=5)
        
        ids1 = [r["recipe_id"] for r in recs1]
        ids2 = [r["recipe_id"] for r in recs2]
        
        assert ids1 == ids2
    
    def test_exclude_query(self):
        """Test query exclusion."""
        from src.recommendation.recipe_preprocessing import get_recipe_ingredient_mapping, get_recipe_metadata_mapping
        
        recommender = RandomRecommender({"random_seed": 42})
        recommender.fit({}, {})
        recommender.recipe_ingredients = get_recipe_ingredient_mapping()
        recommender.recipe_metadata = get_recipe_metadata_mapping()
        recommender.recipe_ids = list(get_recipe_metadata_mapping().keys())
        recommender.is_fitted = True
        
        query_id = list(get_recipe_metadata_mapping().keys())[0]
        recs = recommender.recommend(query_id, k=10)
        
        recipe_ids = [r["recipe_id"] for r in recs]
        assert query_id not in recipe_ids


class TestGetBaselineRecommender:
    """Tests for get_baseline_recommender factory function."""
    
    def test_cuisine_match(self):
        """Test getting cuisine match recommender."""
        recommender = get_baseline_recommender("cuisine_match", {"cuisine_weight": 0.7})
        assert isinstance(recommender, CuisineMatchRecommender)
        assert recommender.cuisine_weight == 0.7
    
    def test_jaccard(self):
        """Test getting Jaccard recommender."""
        recommender = get_baseline_recommender("jaccard")
        assert isinstance(recommender, JaccardSimilarityRecommender)
    
    def test_random(self):
        """Test getting random recommender."""
        recommender = get_baseline_recommender("random", {"random_seed": 123})
        assert isinstance(recommender, RandomRecommender)
        assert recommender.random_seed == 123
    
    def test_invalid_type(self):
        """Test invalid baseline type raises error."""
        with pytest.raises(ValueError):
            get_baseline_recommender("invalid_type")


class TestRunBaselineComparison:
    """Tests for run_baseline_comparison function."""
    
    def test_run_baseline_comparison(self):
        """Test running baseline comparison."""
        from src.recommendation.recipe_preprocessing import get_recipe_ingredient_mapping, get_recipe_metadata_mapping
        
        recipe_ingredients = get_recipe_ingredient_mapping()
        recipe_metadata = get_recipe_metadata_mapping()
        
        query_ids = list(get_recipe_metadata_mapping().keys())[:3]
        config = {"cuisine_weight": 0.6, "ingredient_weight": 0.4}
        
        results = run_baseline_comparison(query_ids, recipe_ingredients, recipe_metadata, k=5, config=config)
        
        assert "cuisine_match" in results
        assert "jaccard" in results
        assert "random" in results
        
        # Each should have results for all 3 queries
        for name in ["cuisine_match", "jaccard", "random"]:
            assert len(results[name]) == 3
            for recs in results[name]:
                assert len(recs) <= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])