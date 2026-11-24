"""
Tests for data splitting module.
"""

import pytest
import numpy as np
import json
from pathlib import Path
import tempfile
from collections import Counter

from src.recommendation.data_splits import (
    SplitConfig,
    DataSplitter,
    create_data_splits,
    load_data_splits,
    verify_split_leakage,
    SPLITS_DIR,
)
from src.recommendation.recipe_preprocessing import RecipePreprocessor


class TestSplitConfig:
    """Tests for SplitConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = SplitConfig()
        assert config.test_size == 0.15
        assert config.val_size == 0.15
        assert config.random_seed == 42
        assert config.stratify_by == "cuisine"
        assert config.min_category_count == 5
        assert config.check_near_duplicates is True
        assert config.near_duplicate_threshold == 0.9
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = SplitConfig(
            test_size=0.2,
            val_size=0.1,
            random_seed=123,
            stratify_by="course",
            min_category_count=10,
            check_near_duplicates=False,
        )
        assert config.test_size == 0.2
        assert config.val_size == 0.1
        assert config.random_seed == 123
        assert config.stratify_by == "course"
        assert config.min_category_count == 10
        assert config.check_near_duplicates is False


class TestDataSplitter:
    """Tests for DataSplitter."""
    
    @pytest.fixture(scope="class")
    def splitter(self):
        """Create a DataSplitter instance with test config."""
        config = SplitConfig(
            test_size=0.2,
            val_size=0.1,
            random_seed=42,
            stratify_by="cuisine",
            min_category_count=5,
            check_near_duplicates=True,
            near_duplicate_threshold=0.9,
        )
        splitter = DataSplitter(config=config)
        splitter.load_data()
        return splitter
    
    def test_load_data(self, splitter):
        """Test data loading."""
        assert len(splitter.recipe_ids) == 6865
        assert len(splitter.recipe_metadata) == 6865
        assert len(splitter.recipe_ingredients) == 6865
    
    def test_create_splits(self, splitter):
        """Test split creation."""
        splits = splitter.create_splits()
        
        assert "train" in splitter.split_ids
        assert "val" in splitter.split_ids
        assert "test" in splitter.split_ids
        
        # Check all recipes are accounted for
        total = (len(splitter.split_ids["train"]) + 
                len(splitter.split_ids["val"]) + 
                len(splitter.split_ids["test"]))
        assert total <= 6865  # Some may be dropped due to stratification
        
        # Check no overlap
        train_set = set(splitter.split_ids["train"])
        val_set = set(splitter.split_ids["val"])
        test_set = set(splitter.split_ids["test"])
        
        assert len(train_set & val_set) == 0
        assert len(train_set & test_set) == 0
        assert len(val_set & test_set) == 0
    
    def test_split_sizes(self, splitter):
        """Test split sizes are approximately correct."""
        splits = splitter.create_splits()
        total = len(splitter.recipe_ids)
        
        train_pct = len(splitter.split_ids["train"]) / len(splitter.recipe_ids)
        val_pct = len(splitter.split_ids["val"]) / len(splitter.recipe_ids)
        test_pct = len(splitter.split_ids["test"]) / len(splitter.recipe_ids)
        
        # Allow some tolerance due to stratification
        assert 0.65 <= train_pct <= 0.75
        assert 0.08 <= val_pct <= 0.18
        assert 0.12 <= test_pct <= 0.20
    
    def test_stratification(self, splitter):
        """Test stratification by cuisine."""
        splits = splitter.create_splits()
        
        # Check that each split has similar cuisine distribution
        train_cuisines = Counter()
        val_cuisines = Counter()
        test_cuisines = Counter()
        
        for rid in splitter.split_ids["train"]:
            meta = splitter.recipe_metadata.get(rid, {})
            train_cuisines[meta.get("cuisine", "Unknown")] += 1
        
        for rid in splitter.split_ids["val"]:
            meta = splitter.recipe_metadata.get(rid, {})
            val_cuisines[meta.get("cuisine", "Unknown")] += 1
        
        for rid in splitter.split_ids["test"]:
            meta = splitter.recipe_metadata.get(rid, {})
            test_cuisines[meta.get("cuisine", "Unknown")] += 1
        
        # Check that major cuisines appear in all splits
        major_cuisines = ["Indian", "Continental", "North Indian Recipes", "South Indian Recipes"]
        for cuisine in major_cuisines:
            assert cuisine in train_cuisines or cuisine in val_cuisines or cuisine in test_cuisines
    
    def test_split_stats(self, splitter):
        """Test split statistics computation."""
        splits = splitter.create_splits()
        
        assert "overall" in splitter.split_stats
        assert "train" in splitter.split_stats
        assert "val" in splitter.split_stats
        assert "test" in splitter.split_stats
        
        # Check overall stats
        overall = splitter.split_stats["overall"]
        assert "total_recipes" in overall
        assert "train_pct" in overall
        assert "val_pct" in overall
        assert "test_pct" in overall
        assert overall["random_seed"] == 42
        assert overall["stratify_by"] == "cuisine"
        
        # Check split-specific stats
        for split_name in ["train", "val", "test"]:
            stats = splitter.split_stats[split_name]
            assert "n_recipes" in stats
            assert "cuisine_distribution" in stats
            assert "course_distribution" in stats
            assert "diet_label_distribution" in stats
            assert "avg_ingredients_per_recipe" in stats
    
    def test_no_overlap(self, splitter):
        """Test that splits don't overlap."""
        splits = splitter.create_splits()
        
        train_ids = set(splits["train"])
        val_ids = set(splits["val"])
        test_ids = set(splits["test"])
        
        assert len(train_ids & val_ids) == 0
        assert len(train_ids & test_ids) == 0
        assert len(val_ids & test_ids) == 0
    
    def test_reproducibility(self):
        """Test that splits are reproducible with same seed."""
        config = SplitConfig(random_seed=123)
        splitter1 = DataSplitter(config=config)
        splitter1.load_data()
        splits1 = splitter1.create_splits()
        
        splitter2 = DataSplitter(config=config)
        splitter2.load_data()
        splits2 = splitter2.create_splits()
        
        assert splits1["train"] == splits2["train"]
        assert splits1["val"] == splits2["val"]
        assert splits1["test"] == splits2["test"]
    
    def test_different_seeds_produce_different_splits(self):
        """Test that different seeds produce different splits."""
        config1 = SplitConfig(random_seed=42)
        config2 = SplitConfig(random_seed=123)
        
        splitter1 = DataSplitter(config=config1)
        splitter1.load_data()
        splits1 = splitter1.create_splits()
        
        splitter2 = DataSplitter(config=config2)
        splitter2.load_data()
        splits2 = splitter2.create_splits()
        
        # At least one split should differ
        assert splits1["train"] != splits2["train"] or \
               splits1["val"] != splits2["val"] or \
               splits1["test"] != splits2["test"]
    
    def test_no_stratification(self):
        """Test splitting without stratification."""
        config = SplitConfig(stratify_by=None)
        splitter = DataSplitter(config=config)
        splitter.load_data()
        splits = splitter.create_splits()
        
        # Should still work without stratification
        assert "train" in splitter.split_ids
        assert "val" in splitter.split_ids
        assert "test" in splitter.split_ids
        
        total = len(splitter.split_ids["train"]) + len(splitter.split_ids["val"]) + len(splitter.split_ids["test"])
        assert total <= 6865
    
    def test_course_stratification(self):
        """Test stratification by course."""
        config = SplitConfig(stratify_by="course", min_category_count=5)
        splitter = DataSplitter(config=config)
        splitter.load_data()
        splits = splitter.create_splits()
        
        assert "train" in splits
        assert "val" in splits
        assert "test" in splits


class TestDataSplitPersistence:
    """Tests for split persistence."""
    
    def test_save_and_load_splits(self):
        """Test saving and loading splits."""
        with tempfile.TemporaryDirectory() as tmpdir:
            splits_dir = Path(tmpdir) / "splits"
            
            config = SplitConfig(random_seed=42)
            splitter = DataSplitter(config=config, splits_dir=splits_dir)
            splitter.load_data()
            splitter.create_splits()
            
            # Load splits
            loaded_splits = load_data_splits(splits_dir)
            
            # Verify loaded splits match
            original = splitter.split_ids
            for split_name in ["train", "val", "test"]:
                assert loaded_splits[split_name] == splitter.split_ids[split_name]


class TestLeakageDetection:
    """Tests for leakage detection."""
    
    @pytest.fixture(scope="class")
    def splitter(self):
        config = SplitConfig(random_seed=42, check_near_duplicates=True)
        splitter = DataSplitter(config=config)
        splitter.load_data()
        splitter.create_splits()
        return splitter
    
    def test_no_exact_overlap(self, splitter):
        """Test no exact recipe ID overlap between splits."""
        leakage = splitter.check_leakage()
        
        assert leakage["split_overlaps"]["train_val"] == 0
        assert leakage["split_overlaps"]["train_test"] == 0
        assert leakage["split_overlaps"]["val_test"] == 0
    
    def test_cross_split_near_duplicates(self, splitter):
        """Test near-duplicate detection across splits."""
        leakage = splitter.check_leakage()
        
        # Should report cross-split near-duplicates
        assert "cross_split_near_duplicates" in leakage
        assert "cross_split_duplicate_details" in leakage


class TestCreateDataSplitsFunction:
    """Tests for the create_data_splits convenience function."""
    
    def test_create_data_splits_default(self):
        """Test creating splits with default config."""
        splits = create_data_splits()
        
        assert "train" in splits
        assert "val" in splits
        assert "test" in splits
        
        total = len(splits["train"]) + len(splits["val"]) + len(splits["test"])
        assert total <= 6865
    
    def test_create_data_splits_custom_config(self):
        """Test creating splits with custom config."""
        config = SplitConfig(test_size=0.2, val_size=0.1, random_seed=999)
        splits = create_data_splits(config)
        
        assert "train" in splits
        assert "val" in splits
        assert "test" in splits


class TestLoadDataSplits:
    """Tests for loading data splits."""
    
    def test_load_existing_splits(self):
        """Test loading existing splits."""
        # First create splits
        create_data_splits(SplitConfig(random_seed=42))
        
        # Then load them
        loaded = load_data_splits()
        
        assert "train" in loaded
        assert "val" in loaded
        assert "test" in loaded


if __name__ == "__main__":
    pytest.main([__file__, "-v"])