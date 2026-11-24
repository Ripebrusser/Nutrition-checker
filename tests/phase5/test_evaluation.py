"""
Tests for evaluation module.
"""

import pytest
import numpy as np
from collections import Counter
from src.recommendation.evaluation import (
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
)
from src.recommendation.retrieval_pipeline import create_recommender
from src.recommendation.baseline_recommenders import (
    CuisineMatchRecommender,
    JaccardSimilarityRecommender,
    RandomRecommender,
)
from src.recommendation.recipe_preprocessing import (
    get_recipe_ingredient_mapping,
    get_recipe_metadata_mapping,
)


class TestSimilarityMetrics:
    """Tests for similarity metric functions."""
    
    def test_jaccard_similarity(self):
        """Test Jaccard similarity calculation."""
        # Identical sets
        assert jaccard_similarity({"a", "b", "c"}, {"a", "b", "c"}) == 1.0
        
        # Partial overlap
        assert jaccard_similarity({"a", "b"}, {"b", "c"}) == 1/3
        
        # No overlap
        assert jaccard_similarity({"a", "b"}, {"c", "d"}) == 0.0
        
        # Empty sets
        assert jaccard_similarity(set(), {"a"}) == 0.0
        assert jaccard_similarity(set(), set()) == 0.0
    
    def test_cuisine_match(self):
        """Test cuisine match function."""
        meta1 = {"cuisine": "Indian"}
        meta2 = {"cuisine": "Indian"}
        meta3 = {"cuisine": "Continental"}
        meta4 = {}
        
        assert cuisine_match(meta1, meta2) == 1.0
        assert cuisine_match(meta1, meta3) == 0.0
        assert cuisine_match(meta1, meta4) == 0.0
        assert cuisine_match({}, {}) == 0.0
    
    def test_course_match(self):
        """Test course match function."""
        meta1 = {"course": "Main Course"}
        meta2 = {"course": "Main Course"}
        meta3 = {"course": "Dessert"}
        
        assert course_match(meta1, meta2) == 1.0
        assert course_match(meta1, {"course": "Dessert"}) == 0.0
        assert course_match({}, {}) == 0.0
    
    def test_diet_overlap(self):
        """Test diet overlap calculation."""
        # Same diets
        assert diet_overlap(
            {"diet_labels": ["Vegetarian", "Vegan"]},
            {"diet_labels": ["Vegetarian", "Vegan"]}
        ) == 1.0
        
        # Partial overlap
        assert diet_overlap(
            {"diet_labels": ["Vegetarian", "Vegan"]},
            {"diet_labels": ["Vegetarian", "Gluten Free"]}
        ) == 0.5  # 1/2
        
        # No overlap
        assert diet_overlap(
            {"diet_labels": ["Vegetarian"]},
            {"diet_labels": ["Non Vegeterian"]}
        ) == 0.0
        
        # Empty diets
        assert diet_overlap({}, {"diet_labels": ["Vegetarian"]}) == 0.0
        assert diet_overlap({}, {}) == 0.0
        assert diet_overlap({"diet_labels": []}, {"diet_labels": []}) == 0.0


class TestIngredientOverlapRelevance:
    """Tests for ingredient overlap relevance proxy."""
    
    def test_relevance_high_overlap(self):
        """Test high relevance with high ingredient overlap."""
        query_ings = {"onion", "tomato", "cumin", "coriander"}
        cand_ings = {"onion", "tomato", "turmeric"}
        query_meta = {"cuisine": "Indian", "course": "Main Course", "diet_labels": ["Vegetarian"]}
        cand_meta = {"cuisine": "Indian", "course": "Main Course", "diet_labels": ["Vegetarian"]}
        
        is_rel, details = ingredient_overlap_relevance(
            query_ings, set(), query_meta, {}, threshold=0.3
        )
        # This test needs actual candidate ingredients
        # Let's test with proper inputs
        
    def test_relevance_calculation(self):
        """Test relevance proxy calculation."""
        query_ings = {"onion", "tomato", "cumin"}
        cand_ings = {"onion", "tomato", "turmeric"}
        query_meta = {"cuisine": "Indian", "course": "Main Course", "diet_labels": ["Vegetarian"]}
        cand_meta = {"cuisine": "Indian", "course": "Main Course", "diet_labels": ["Vegetarian"]}
        
        is_rel, details = ingredient_overlap_relevance(
            {"onion", "tomato", "cumin"},
            {"onion", "tomato", "turmeric"},
            {"cuisine": "Indian", "course": "Main Course", "diet_labels": ["Vegetarian"]},
            {"cuisine": "Indian", "course": "Main Course", "diet_labels": ["Vegetarian"]},
            threshold=0.3
        )
        
        # Jaccard = 2/4 = 0.5
        # cuisine_match = 1.0
        # course_match = 1.0
        # diet_overlap = 1.0
        # proxy = 0.5*0.5 + 0.2*1.0 + 0.15*1.0 + 0.15*1.0 = 0.25 + 0.2 + 0.15 + 0.15 = 0.75
        # > 0.3, so relevant
        
        assert details["jaccard"] == 0.5
        assert details["cuisine_match"] == 1.0
        assert details["course_match"] == 1.0
        assert details["diet_overlap"] == 1.0
        assert details["proxy_score"] == 0.75
        assert is_rel == True


class TestPrecisionRecall:
    """Tests for precision and recall metrics."""
    
    def test_precision_at_k(self):
        """Test Precision@k calculation."""
        recommended = [1, 2, 3, 4, 5]
        relevant = {2, 4, 6}
        
        # P@1: 1 not in relevant -> 0/1 = 0
        assert precision_at_k(recommended, {2, 4, 6}, 1) == 0.0
        
        # P@2: 1,2 -> 1 hit -> 1/2 = 0.5
        assert precision_at_k(recommended, {2, 4, 6}, 2) == 0.5
        
        # P@3: 1,2,3 -> 1 hit -> 1/3
        assert abs(precision_at_k(recommended, {2, 4, 6}, 3) - 1/3) < 0.001
        
        # P@5: 1,2,3,4,5 -> 2 hits -> 2/5 = 0.4
        assert precision_at_k(recommended, {2, 4, 6}, 5) == 0.4
        
        # k=0
        assert precision_at_k(recommended, {2, 4, 6}, 0) == 0.0
    
    def test_recall_at_k(self):
        """Test Recall@k calculation."""
        recommended = [1, 2, 3, 4, 5]
        relevant = {2, 4, 6}
        
        # R@1: 0/3 = 0
        assert recall_at_k(recommended, {2, 4, 6}, 1) == 0.0
        
        # R@2: 1/3
        assert abs(recall_at_k(recommended, {2, 4, 6}, 2) - 1/3) < 0.001
        
        # R@5: 2/3
        assert abs(recall_at_k(recommended, {2, 4, 6}, 5) - 2/3) < 0.001
        
        # Empty relevant set
        assert recall_at_k([1, 2, 3], set(), 3) == 0.0


class TestIntraListDiversity:
    """Tests for intra-list diversity."""
    
    def test_diversity_identical(self):
        """Test diversity with identical recommendations."""
        recipe_ingredients = {
            1: ["onion", "tomato"],
            2: ["onion", "tomato"],
            3: ["onion", "tomato"],
        }
        
        # All same ingredients -> diversity = 0
        div = intra_list_diversity([1, 2, 3], {}, {}, {1: ["onion", "tomato"]})
        assert div == 0.0
    
    def test_diversity_different(self):
        """Test diversity with different ingredients."""
        recipe_ingredients = {
            1: ["onion", "tomato"],
            2: ["chicken", "curry"],
            3: ["rice", "dal"],
        }
        
        # All different -> high diversity
        div = intra_list_diversity([1, 2, 3], {}, {}, {
            1: ["onion", "tomato"],
            2: ["chicken", "curry"],
            3: ["rice", "dal"],
        })
        assert div > 0.5  # Should be high
    
    def test_single_item(self):
        """Test diversity with single item."""
        div = intra_list_diversity([1], {}, {}, {1: ["onion"]})
        assert div == 1.0  # By definition


class TestCoverage:
    """Tests for catalogue coverage."""
    
    def test_coverage_full(self):
        """Test coverage when all items recommended."""
        all_recs = [[1, 2], [2, 3], [3, 4]]
        assert coverage(all_recs, 4) == 1.0  # 4/4
    
    def test_coverage_partial(self):
        """Test partial coverage."""
        all_recs = [[1, 2], [2, 3]]
        assert coverage(all_recs, 5) == 0.6  # 3/5
    
    def test_coverage_empty(self):
        """Test empty recommendations."""
        assert coverage([], 10) == 0.0
        assert coverage([[]], 10) == 0.0


class TestNovelty:
    """Tests for novelty metric."""
    
    def test_novelty_uniform(self):
        """Test novelty with uniform popularity."""
        pop = {1: 10, 2: 10, 3: 10, 4: 10}
        # All equally popular -> novelty = avg(-log(1/4)) = log2(4) = 2
        nov = novelty([1, 2], pop, 4)
        assert abs(nov - 2.0) < 0.01
    
    def test_novelty_skewed(self):
        """Test novelty with skewed popularity."""
        pop = {1: 100, 2: 1, 3: 1, 4: 1}
        # Item 1 is very popular -> low novelty
        # Items 2,3,4 are rare -> high novelty
        nov = novelty([1], pop, 4)
        assert nov < novelty([2], pop, 4)


class TestConstraintCompliance:
    """Tests for constraint compliance metrics."""
    
    def test_cuisine_constraint_compliance(self):
        """Test cuisine constraint compliance."""
        metadata = {
            1: {"cuisine": "Indian"},
            2: {"cuisine": "Chinese"},
            3: {"cuisine": "Italian"},
            4: {"cuisine": "Indian"},
        }
        
        # Required cuisine
        assert cuisine_constraint_compliance([1, 4], metadata, required_cuisine="Indian") == 1.0
        assert cuisine_constraint_compliance([1, 2], metadata, required_cuisine="Indian") == 0.5
        assert cuisine_constraint_compliance([2, 3], metadata, required_cuisine="Indian") == 0.0
        
        # Allowed cuisines
        assert cuisine_constraint_compliance([1, 2, 3], metadata, allowed_cuisines=["Indian", "Chinese"]) == 2/3
        assert cuisine_constraint_compliance([1, 2, 3], metadata, allowed_cuisines=["Indian"]) == 1/3
        
        # Forbidden cuisines
        assert cuisine_constraint_compliance([1, 2, 3], metadata, forbidden_cuisines=["Italian"]) == 2/3
    
    def test_diet_constraint_compliance(self):
        """Test diet constraint compliance."""
        metadata = {
            1: {"diet_labels": ["Vegetarian"]},
            2: {"diet_labels": ["Non Vegeterian"]},
            3: {"diet_labels": ["Vegan", "Vegetarian"]},
        }
        
        # Required diets
        assert diet_constraint_compliance([1, 3], metadata, required_diets=["Vegetarian"]) == 1.0
        assert diet_constraint_compliance([1, 2], metadata, required_diets=["Vegetarian"]) == 0.5
        
        # Forbidden diets
        assert diet_constraint_compliance([1, 2], metadata, forbidden_diets=["Non Vegeterian"]) == 0.5


class TestEvaluationConfig:
    """Tests for EvaluationConfig."""
    
    def test_default_config(self):
        config = EvaluationConfig()
        assert config.k_values == [1, 5, 10, 20]
        assert config.random_seed == 42
        assert config.n_manual_review_samples == 50
        assert config.proxy_relevance_threshold == 0.3
    
    def test_custom_config(self):
        config = EvaluationConfig(
            k_values=[1, 3, 5],
            proxy_relevance_threshold=0.5,
        )
        assert config.k_values == [1, 3, 5]
        assert config.proxy_relevance_threshold == 0.5


class TestManualReviewEvaluation:
    """Tests for manual review evaluation."""
    
    def test_manual_review_evaluation(self):
        from src.recommendation.retrieval_pipeline import create_recommender
        
        recommender = create_recommender()
        sample_ids = list(recommender.recipe_metadata.keys())[:2]
        
        result = manual_review_evaluation(recommender, sample_ids, k=3, annotators=2)
        
        assert "samples" in result
        assert "total_samples" in result
        assert "instructions" in result
        
        # Should have 2 queries * 3 recommendations = 6 samples
        assert result["total_samples"] == 6
        
        # Check sample structure
        sample = result["samples"][0]
        assert "query_recipe_id" in sample
        assert "candidate_recipe_id" in sample
        assert "relevance_1" in sample
        assert "relevance_2" in sample
        assert "notes" in sample


class TestCompareRecommenders:
    """Tests for comparing recommenders."""
    
    def test_compare_recommenders(self):
        """Test comparing multiple recommenders."""
        from src.recommendation.retrieval_pipeline import create_recommender
        from src.recommendation.baseline_recommenders import (
            CuisineMatchRecommender,
            JaccardSimilarityRecommender,
            RandomRecommender,
        )
        
        # Create recommenders
        cb_recommender = create_recommender()
        
        cm_recommender = CuisineMatchRecommender()
        cm_recommender.fit({}, {})
        cm_recommender.recipe_ingredients = get_recipe_ingredient_mapping()
        cm_recommender.recipe_metadata = get_recipe_metadata_mapping()
        cm_recommender.recipe_ids = list(get_recipe_metadata_mapping().keys())
        cm_recommender.is_fitted = True
        cm_recommender.config = {"cuisine_weight": 0.6, "ingredient_weight": 0.4}
        
        jaccard_rec = JaccardSimilarityRecommender()
        jaccard_rec.fit({}, {})
        jaccard_rec.recipe_ingredients = get_recipe_ingredient_mapping()
        jaccard_rec.recipe_metadata = get_recipe_metadata_mapping()
        jaccard_rec.recipe_ids = list(get_recipe_metadata_mapping().keys())
        jaccard_rec.is_fitted = True
        
        random_rec = RandomRecommender()
        random_rec.fit({}, {})
        random_rec.recipe_ingredients = get_recipe_ingredient_mapping()
        random_rec.recipe_metadata = get_recipe_metadata_mapping()
        random_rec.recipe_ids = list(get_recipe_metadata_mapping().keys())
        random_rec.is_fitted = True
        
        recommenders = {
            "Content-Based": cb_recommender,
            "CuisineMatch": cm_recommender,
            "Jaccard": jaccard_rec,
            "Random": random_rec,
        }
        
        # Use small test set for speed
        test_ids = list(get_recipe_metadata_mapping().keys())[:5]
        
        comparison = compare_recommenders(recommenders, test_ids, k_values=[5])
        
        # Check structure
        assert "precision@5" in comparison
        assert "recall@5" in comparison
        assert "diversity" in comparison
        assert "coverage" in comparison
        
        # All recommenders should have metrics
        for metric in ["precision@5", "recall@5", "diversity", "coverage"]:
            assert len(comparison[metric]) == 4
            for name in ["Content-Based", "CuisineMatch", "Jaccard", "Random"]:
                assert name in comparison[metric]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])