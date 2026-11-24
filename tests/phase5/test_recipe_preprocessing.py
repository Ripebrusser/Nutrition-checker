"""
Tests for recipe preprocessing module.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from src.recommendation.recipe_preprocessing import (
    RecipePreprocessor,
    get_recipe_ingredient_mapping,
    get_recipe_metadata_mapping,
    load_recipes_dataframe,
    load_parsed_ingredients_dataframe,
)


class TestRecipePreprocessing:
    """Tests for recipe preprocessing functionality."""
    
    def test_load_recipes_dataframe(self):
        """Test loading recipes dataframe."""
        df = load_recipes_dataframe()
        assert len(df) == 6865
        assert "recipe_id" in df.columns
        assert "recipe_name_en" in df.columns
        assert "cuisine" in df.columns
        assert "course" in df.columns
        assert "diet_labels" in df.columns
    
    def test_load_parsed_ingredients_dataframe(self):
        """Test loading parsed ingredients dataframe."""
        df = load_parsed_ingredients_dataframe()
        assert len(df) == 90862
        assert "recipe_id" in df.columns
        assert "ingredient_name" in df.columns
        assert "parse_status" in df.columns
        assert "conversion_status" in df.columns
    
    def test_recipe_preprocessor_load(self):
        """Test RecipePreprocessor loads data correctly."""
        preprocessor = RecipePreprocessor()
        preprocessor.load_data()
        
        assert preprocessor._recipes_df is not None
        assert preprocessor._parsed_ingredients_df is not None
        assert preprocessor._normalized_ingredients_df is not None
        assert preprocessor._ifct_match_candidates_df is not None
        
        assert len(preprocessor._recipes_df) == 6865
        assert len(preprocessor._parsed_ingredients_df) == 90862
    
    def test_get_recipe_ingredient_mapping(self):
        """Test getting recipe-ingredient mapping."""
        mapping = get_recipe_ingredient_mapping()
        assert isinstance(mapping, dict)
        assert len(mapping) == 6865  # All recipes should have ingredients
        
        # Check first recipe has ingredients
        first_recipe = list(mapping.keys())[0]
        assert isinstance(mapping[first_recipe], list)
        assert len(mapping[first_recipe]) > 0
    
    def test_get_recipe_metadata_mapping(self):
        """Test getting recipe metadata mapping."""
        mapping = get_recipe_metadata_mapping()
        assert isinstance(mapping, dict)
        assert len(mapping) == 6865
        
        # Check first recipe has metadata
        first_recipe = list(mapping.keys())[0]
        meta = mapping[first_recipe]
        assert "recipe_name" in meta
        assert "cuisine" in meta
        assert "course" in meta
        assert "diet_labels" in meta
        assert isinstance(meta["diet_labels"], list)
    
    def test_recipe_preprocessor_extract_ingredients(self):
        """Test extracting recipe ingredients."""
        preprocessor = RecipePreprocessor()
        preprocessor.load_data()
        ingredients = preprocessor.extract_recipe_ingredients()
        
        assert isinstance(ingredients, dict)
        assert len(ingredients) == 6865
        
        # Check ingredients are normalized (lowercase, stripped)
        for ingredients_list in preprocessor.recipe_ingredients.values():
            for ing in ingredients_list:
                assert ing == ing.lower().strip()
    
    def test_recipe_preprocessor_extract_metadata(self):
        """Test extracting recipe metadata."""
        preprocessor = RecipePreprocessor()
        preprocessor.load_data()
        metadata = preprocessor.extract_recipe_metadata()
        
        assert isinstance(metadata, dict)
        assert len(metadata) == 6865
        
        # Check diet labels are parsed correctly
        for meta in metadata.values():
            assert isinstance(meta["diet_labels"], list)
    
    def test_get_recipe_ingredient_sets(self):
        """Test getting ingredient sets for Jaccard similarity."""
        preprocessor = RecipePreprocessor()
        preprocessor.load_data()
        preprocessor.extract_recipe_ingredients()
        
        sets = preprocessor.get_recipe_ingredient_sets()
        assert isinstance(sets, dict)
        assert len(sets) == 6865
        
        # Check all values are sets
        for ing_set in sets.values():
            assert isinstance(sets[list(sets.keys())[0]], set)
    
    def test_identify_missing_ingredients(self):
        """Test identifying missing ingredients."""
        preprocessor = RecipePreprocessor()
        preprocessor.load_data()
        missing = preprocessor.identify_missing_ingredients()
        
        assert "total_recipes" in missing
        assert "recipes_with_ingredients" in missing
        assert "recipes_missing_ingredients" in missing
        assert missing["total_recipes"] == 6865
    
    def test_data_quality_report(self):
        """Test data quality report generation."""
        preprocessor = RecipePreprocessor()
        preprocessor.load_data()
        quality = preprocessor.check_data_quality()
        
        assert "recipes" in quality
        assert "parsed_ingredients" in quality
        assert "cuisine_distribution" in quality
        assert "course_distribution" in quality
        assert "diet_labels_distribution" in quality
        assert "recipe_type_distribution" in quality
        assert "duplicate_analysis" in quality
        assert "near_duplicate_analysis" in quality
        
        # Check duplicate analysis structure
        dup = quality["duplicate_analysis"]
        assert "total_recipes_checked" in dup
        assert "duplicate_groups" in dup
        assert "duplicate_recipes" in dup
        
        # Check near-duplicate analysis structure
        near_dup = quality["near_duplicate_analysis"]
        assert "threshold" in near_dup
        assert "sample_size" in near_dup
        assert "near_duplicate_pairs_found" in near_dup


class TestRecipePreprocessingIntegration:
    """Integration tests for recipe preprocessing."""
    
    def test_full_preprocessing_pipeline(self):
        """Test the full preprocessing pipeline runs without errors."""
        preprocessor = RecipePreprocessor()
        preprocessor.load_data()
        
        # Run all main methods
        quality = preprocessor.check_data_quality()
        ingredients = preprocessor.extract_recipe_ingredients()
        metadata = preprocessor.extract_recipe_metadata()
        ingredient_sets = preprocessor.get_recipe_ingredient_sets()
        missing = preprocessor.identify_missing_ingredients()
        
        # Verify consistency
        assert quality["recipes"]["total_recipes"] == 6865
        assert len(ingredients) == 6865
        assert len(metadata) == 6865
        assert len(ingredients) == len(metadata)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])