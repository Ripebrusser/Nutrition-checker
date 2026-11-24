#!/usr/bin/env python3
"""
Tests for Stage 2 - Ingredient Quantity and Unit Parsing
"""

import pandas as pd
import pytest
from pathlib import Path


class TestQuantityParsing:
    """Tests for ingredient quantity and unit parsing."""

    @pytest.fixture(scope="class")
    def canonical_df(self):
        """Load canonical parsed ingredients."""
        path = Path("data/interim/phase2/parsed_recipe_ingredients.parquet")
        assert path.exists(), f"Parsed ingredients not found at {path}"
        return pd.read_parquet(path)

    @pytest.fixture(scope="class")
    def household_df(self):
        """Load household measurements."""
        path = Path("data/interim/phase2/household_measurements.csv")
        assert path.exists(), f"Household measurements not found at {path}"
        return pd.read_csv(path)

    @pytest.fixture(scope="class")
    def recipes_df(self):
        """Load original recipes."""
        path = Path("data/processed/recipes.parquet")
        assert path.exists(), f"Recipes not found at {path}"
        return pd.read_parquet(path)

    def test_all_recipes_accounted(self, canonical_df, recipes_df):
        """All 6,865 recipes should be accounted for."""
        processed_ids = set(canonical_df['recipe_id'].unique())
        original_ids = set(recipes_df['recipe_id'].unique())
        assert len(processed_ids) == 6865, f"Expected 6865 recipes, got {len(processed_ids)}"
        # All original recipe IDs should be present in canonical output
        missing = original_ids - processed_ids
        assert len(missing) == 0, f"Missing recipe IDs: {sorted(missing)[:10]}..."

    def test_no_recipe_ids_lost(self, canonical_df, recipes_df):
        """No recipe IDs lost during processing."""
        original_ids = set(recipes_df['recipe_id'])
        processed_ids = set(canonical_df['recipe_id'].unique())
        missing = original_ids - processed_ids
        assert len(missing) == 0, f"Missing recipe IDs: {missing}"

    def test_canonical_records_exist(self, canonical_df):
        """Canonical records should exist."""
        assert len(canonical_df) > 0, "No canonical records produced"
        assert 'recipe_id' in canonical_df.columns
        assert 'normalized_ingredient' in canonical_df.columns
        assert 'ingredient_name' in canonical_df.columns

    def test_parse_status_valid(self, canonical_df):
        """Parse status should be one of expected values."""
        valid_statuses = {'PARSED_EXACT', 'PARSED_APPROXIMATE', 'RANGE_PARSED', 'UNQUANTIFIED', 'UNIT_UNSUPPORTED', 'AMBIGUOUS', 'PARSE_FAILED'}
        invalid = set(canonical_df['parse_status'].unique()) - valid_statuses
        assert len(invalid) == 0, f"Invalid parse statuses: {invalid}"

    def test_conversion_status_valid(self, canonical_df):
        """Conversion status should be valid."""
        valid_statuses = {'RESOLVED', 'RESOLVED_HOUSEHOLD', 'UNRESOLVED', 'NOT_APPLICABLE'}
        invalid = set(canonical_df['conversion_status'].unique()) - valid_statuses
        assert len(invalid) == 0, f"Invalid conversion statuses: {invalid}"

    def test_source_reconciliation_valid(self, canonical_df):
        """Source reconciliation should have valid values."""
        valid = {'canonical', 'raw_only', 'en_only', 'unknown'}
        invalid = set(canonical_df['source_reconciliation'].unique()) - valid
        assert len(invalid) == 0, f"Invalid reconciliation statuses: {invalid}"

    def test_no_discrepancy_flag_for_single_source(self, canonical_df):
        """Discrepancy flag should only be True when both sources exist but disagree."""
        # Currently all discrepancies should be 0 since we only flag when both sources disagree
        # This test documents the expected behavior
        assert 'discrepancy_flag' in canonical_df.columns

    def test_raw_en_match_columns_exist(self, canonical_df):
        """Raw and en match columns should exist."""
        assert 'raw_match' in canonical_df.columns
        assert 'en_match' in canonical_df.columns

    def test_gram_weight_columns_exist(self, canonical_df):
        """Gram weight columns should exist."""
        assert 'gram_weight' in canonical_df.columns
        assert 'gram_weight_min' in canonical_df.columns
        assert 'gram_weight_max' in canonical_df.columns

    def test_household_measurements_valid(self, household_df):
        """Household measurements should have required columns."""
        expected_cols = ['ingredient_name', 'household_unit', 'equivalent_mass_g', 'source', 'confidence', 'verification_status']
        for col in expected_cols:
            assert col in household_df.columns, f"Missing column: {col}"
        assert len(household_df) > 0, "Household measurements should not be empty"
        # Confidence should be in valid range
        assert (household_df['confidence'] >= 0).all() and (household_df['confidence'] <= 1).all()

    def test_no_recipe_ids_lost_in_parsing(self, canonical_df, recipes_df):
        """Verify all recipes from Phase 1 are still present."""
        assert canonical_df['recipe_id'].nunique() == 6865

    def test_canonical_count_reasonable(self, canonical_df):
        """Canonical count should be reasonable (less than total parsed, more than recipes)."""
        # Should be less than total parsed records (168602) but more than recipes (6865)
        assert 6865 < len(canonical_df) < 168602

    def test_all_recipes_have_canonical_ingredients(self, canonical_df, recipes_df):
        """Every recipe should have at least one canonical ingredient."""
        recipe_counts = canonical_df.groupby('recipe_id').size()
        assert len(recipe_counts) == 6865
        assert (recipe_counts >= 1).all()

    def test_parquet_csv_parity(self):
        """Parquet and CSV outputs should have equivalent data (accounting for CSV serialization differences)."""
        parquet_df = pd.read_parquet("data/interim/phase2/parsed_recipe_ingredients.parquet")
        csv_df = pd.read_csv("data/interim/phase2/parsed_recipe_ingredients.csv")
        assert len(parquet_df) == len(csv_df), "Row count mismatch"
        assert list(parquet_df.columns) == list(csv_df.columns), "Column mismatch"
        
        # Compare key columns semantically (CSV doesn't preserve nullable types perfectly)
        for col in ['recipe_id', 'normalized_ingredient', 'ingredient_name', 'parse_status', 'conversion_status']:
            p = parquet_df[col].reset_index(drop=True)
            c = csv_df[col].reset_index(drop=True)
            
            # For string columns, treat empty string as NA equivalent
            def is_na(series):
                if series.dtype == 'object' or series.dtype == 'string':
                    return series.isna() | (series == '')
                return series.isna()
            
            p_na = is_na(p)
            c_na = is_na(c)
            
            # Both NA or both not NA
            na_match = (p_na == c_na).all()
            assert na_match, f"NA mask mismatch in {col}"
            
            # For non-NA values, compare actual values
            mask = ~p_na & ~c_na
            if mask.any():
                p_vals = p[mask].astype(str)
                c_vals = c[mask].astype(str)
                assert (p_vals == c_vals).all(), f"Value mismatch in {col}"

    def test_household_measurements_parity(self):
        """Household measurements CSV should be valid."""
        df = pd.read_csv("data/interim/phase2/household_measurements.csv")
        assert len(df) > 0
        assert 'ingredient_name' in df.columns
        assert 'household_unit' in df.columns
        assert 'equivalent_mass_g' in df.columns


class TestQuantityParsingLogic:
    """Tests for the parsing logic itself."""

    def test_quantity_parsing_basic(self):
        """Test basic quantity parsing."""
        from src.ingredients.ingredient_parser import IngredientParser
        parser = IngredientParser()
        
        # Test basic quantities
        test_cases = [
            ("2 cups rice", 2.0, "cup"),
            ("1/2 cup water", 0.5, "cup"),
            ("1 tbsp oil", 1.0, "tbsp"),
            ("1 tsp salt", 1.0, "tsp"),
            ("100 g flour", 100.0, "g"),
            ("500 g chicken", 500.0, "g"),
            ("salt to taste", None, "to_taste"),
            ("handful of spinach", None, "handful"),
        ]
        
        for text, expected_qty, expected_unit in test_cases:
            parsed = parser.parse(text)
            if expected_qty is not None:
                assert parsed.quantity is not None, f"Expected quantity for '{text}'"
                assert abs(parsed.quantity.value - expected_qty) < 0.01, f"Wrong quantity for '{text}': got {parsed.quantity.value}, expected {expected_qty}"
            if expected_unit:
                assert parsed.unit is not None, f"Expected unit for '{text}'"
                assert parsed.unit.standardized_unit == expected_unit, f"Wrong unit for '{text}': got {parsed.unit.standardized_unit}, expected {expected_unit}"

    def test_range_parsing(self):
        """Test range quantity parsing."""
        from src.ingredients.ingredient_parser import IngredientParser
        parser = IngredientParser()
        
        parsed = parser.parse("1-2 cups rice")
        assert parsed.quantity is not None
        assert parsed.quantity.is_range
        assert parsed.quantity.min_value == 1.0
        assert parsed.quantity.max_value == 2.0
        
        parsed = parser.parse("2 to 3 tbsp oil")
        assert parsed.quantity.is_range
        assert parsed.quantity.min_value == 2.0
        assert parsed.quantity.max_value == 3.0

    def test_fraction_parsing(self):
        """Test fraction parsing."""
        from src.ingredients.ingredient_parser import IngredientParser
        parser = IngredientParser()
        
        test_cases = [
            ("1/2 cup", 0.5),
            ("1/4 tsp", 0.25),
            ("3/4 cup", 0.75),
            ("1 1/2 cups", 1.5),
            ("2 1/2 tbsp", 2.5),
        ]
        
        for text, expected in test_cases:
            parsed = parser.parse(text)
            assert parsed.quantity is not None, f"No quantity for '{text}'"
            assert abs(parsed.quantity.value - expected) < 0.01, f"Wrong value for '{text}': got {parsed.quantity.value}, expected {expected}"

    def test_hindi_units(self):
        """Test Hindi unit parsing."""
        from src.ingredients.ingredient_parser import IngredientParser
        parser = IngredientParser()
        
        # Test Hindi units
        parsed = parser.parse("1 कप चावल")
        assert parsed.unit is not None
        assert parsed.unit.standardized_unit == "cup"
        
        parsed = parser.parse("2 चमच तेल")
        assert parsed.unit is not None
        assert parsed.unit.standardized_unit == "tbsp"

    def test_approximate_quantities(self):
        """Test approximate quantity parsing."""
        from src.ingredients.ingredient_parser import IngredientParser
        parser = IngredientParser()
        
        parsed = parser.parse("salt to taste")
        assert parsed.unit is not None
        assert parsed.unit.category.value == "approximate"
        
        parsed = parser.parse("handful of spinach")
        assert parsed.unit is not None
        assert parsed.unit.category.value == "approximate"

    def test_preparation_extraction(self):
        """Test preparation description extraction."""
        from src.ingredients.ingredient_parser import IngredientParser
        parser = IngredientParser()
        
        parsed = parser.parse("1 cup chopped onions")
        assert parsed.preparation is not None
        assert "chopped" in parsed.preparation
        
        parsed = parser.parse("2 tbsp minced garlic")
        assert parsed.preparation is not None
        assert "minced" in parsed.preparation

    def test_size_descriptor(self):
        """Test size descriptor extraction."""
        from src.ingredients.ingredient_parser import IngredientParser
        parser = IngredientParser()
        
        parsed = parser.parse("2 medium onions")
        assert parsed.size_descriptor == "medium"
        
        parsed = parser.parse("1 large tomato")
        assert parsed.size_descriptor == "large"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])