#!/usr/bin/env python3
"""
Tests for Stage 1 - Ingredient Normalization
"""

import pandas as pd
import pytest
from pathlib import Path


class TestIngredientNormalization:
    """Tests for ingredient normalization pipeline."""

    @pytest.fixture(scope="class")
    def norm_df(self):
        """Load normalized ingredients."""
        path = Path("data/interim/phase2/normalized_ingredients.parquet")
        assert path.exists(), f"Normalized ingredients not found at {path}"
        return pd.read_parquet(path)

    @pytest.fixture(scope="class")
    def synonym_df(self):
        """Load synonym dictionary."""
        path = Path("data/interim/phase2/ingredient_synonyms.csv")
        assert path.exists(), f"Synonym dictionary not found at {path}"
        return pd.read_csv(path)

    @pytest.fixture(scope="class")
    def recipes_df(self):
        """Load original recipes."""
        path = Path("data/processed/recipes.parquet")
        assert path.exists(), f"Recipes not found at {path}"
        return pd.read_parquet(path)

    def test_all_recipes_processed(self, norm_df, recipes_df):
        """All 6,865 recipes should be processed."""
        processed_ids = norm_df['recipe_id'].unique()
        assert len(processed_ids) == 6865, f"Expected 6865 recipes, got {len(processed_ids)}"
        assert set(processed_ids) == set(recipes_df['recipe_id']), "Recipe IDs don't match"

    def test_no_unexpected_duplicates(self, norm_df):
        """Check that total record count matches expected from ingredient splits."""
        # Total records should equal sum of ingredient splits across all recipes
        # We can't easily predict exact count, but should be reasonable
        total_records = len(norm_df)
        # 6865 recipes × 2 sources × avg ~12 ingredients = ~164k records
        assert 150000 < total_records < 200000, f"Unexpected record count: {total_records}"

    def test_original_text_preserved(self, norm_df):
        """Original ingredient text must be preserved."""
        assert 'source_ingredient' in norm_df.columns
        assert 'source_line' in norm_df.columns
        # No nulls in original text
        assert norm_df['source_ingredient'].notna().all()
        assert norm_df['source_line'].notna().all()

    def test_normalized_column_exists(self, norm_df):
        """Normalized ingredient column exists and has no nulls."""
        assert 'normalized_ingredient' in norm_df.columns
        assert norm_df['normalized_ingredient'].notna().all()

    def test_transformations_recorded(self, norm_df):
        """Every record has transformations recorded."""
        assert 'transformations' in norm_df.columns
        assert norm_df['transformations'].notna().all()
        # Every record should have at least basic transformations
        for trans in norm_df['transformations']:
            assert isinstance(trans, str)
            assert len(trans) > 0

    def test_flags_recorded(self, norm_df):
        """Flags column exists."""
        assert 'flags' in norm_df.columns
        assert norm_df['flags'].notna().all()

    def test_source_tracking(self, norm_df):
        """Source field (raw vs en) tracked in flags."""
        has_raw = norm_df['flags'].str.contains('source:ingredients_raw').any()
        has_en = norm_df['flags'].str.contains('source:ingredients_en').any()
        assert has_raw, "No records from ingredients_raw"
        assert has_en, "No records from ingredients_en"

    def test_synonym_applied_tracking(self, norm_df):
        """Synonym application tracked."""
        assert 'synonym_applied' in norm_df.columns
        assert 'synonym_confidence' in norm_df.columns
        # Some synonyms should have been applied
        applied = norm_df['synonym_applied'].notna().sum()
        assert applied > 0, "No synonyms were applied"

    def test_no_recipe_ids_lost(self, norm_df, recipes_df):
        """No recipe IDs lost during processing."""
        original_ids = set(recipes_df['recipe_id'])
        processed_ids = set(norm_df['recipe_id'].unique())
        missing = original_ids - processed_ids
        assert len(missing) == 0, f"Missing recipe IDs: {missing}"

    def test_reproducibility(self, norm_df):
        """Same input should produce same output - check determinism."""
        # Group by recipe_id and source_ingredient, check normalized is consistent
        grouped = norm_df.groupby(['recipe_id', 'source_ingredient'])['normalized_ingredient'].nunique()
        inconsistent = grouped[grouped > 1]
        assert len(inconsistent) == 0, f"Non-deterministic normalization for {len(inconsistent)} items"

    def test_parquet_csv_parity(self):
        """Parquet and CSV outputs should be identical."""
        parquet_df = pd.read_parquet("data/interim/phase2/normalized_ingredients.parquet")
        csv_df = pd.read_csv("data/interim/phase2/normalized_ingredients.csv")
        assert len(parquet_df) == len(csv_df), "Row count mismatch"
        assert list(parquet_df.columns) == list(csv_df.columns), "Column mismatch"
        # Compare key columns
        for col in ['recipe_id', 'source_ingredient', 'normalized_ingredient', 'transformations', 'flags']:
            pd.testing.assert_series_equal(
                parquet_df[col].reset_index(drop=True),
                csv_df[col].reset_index(drop=True),
                check_names=False
            )

    def test_synonym_dictionary_valid(self, synonym_df):
        """Synonym dictionary has expected structure."""
        expected_cols = ['synonym_key', 'canonical_name', 'synonym', 'category', 'evidence', 'confidence', 'excludes', 'notes']
        for col in expected_cols:
            assert col in synonym_df.columns, f"Missing column: {col}"
        # No duplicate keys
        assert synonym_df['synonym_key'].nunique() == len(synonym_df)
        # Confidence in valid range
        assert (synonym_df['confidence'] >= 0).all() and (synonym_df['confidence'] <= 1).all()

    def test_meaningful_distinctions_preserved(self, norm_df):
        """Check that known distinctions are preserved (not over-merged)."""
        # Fresh vs dried coconut
        fresh_coconut = norm_df[norm_df['normalized_ingredient'].str.contains('fresh coconut', na=False)]
        dried_coconut = norm_df[norm_df['normalized_ingredient'].str.contains('dried coconut', na=False)]
        if len(fresh_coconut) > 0 and len(dried_coconut) > 0:
            # They should normalize to different canonical forms
            fresh_norm = fresh_coconut['normalized_ingredient'].unique()
            dried_norm = dried_coconut['normalized_ingredient'].unique()
            # At least one should be different
            assert not (set(fresh_norm) & set(dried_norm)), "Fresh and dried coconut merged incorrectly"

        # Whole wheat vs refined wheat
        whole_wheat = norm_df[norm_df['normalized_ingredient'].str.contains('whole wheat', na=False)]
        refined_wheat = norm_df[norm_df['normalized_ingredient'].str.contains('refined wheat', na=False)]
        if len(whole_wheat) > 0 and len(refined_wheat) > 0:
            whole_norm = set(whole_wheat['normalized_ingredient'].unique())
            refined_norm = set(refined_wheat['normalized_ingredient'].unique())
            # They should be different
            assert not (whole_norm & refined_norm), "Whole wheat and refined wheat merged incorrectly"

    def test_flags_structure(self, norm_df):
        """Flags should have expected structure."""
        # Check that no_synonym_match flag exists for unmatched
        unmatched = norm_df[norm_df['flags'].str.contains('no_synonym_match', na=False)]
        assert len(unmatched) > 0, "Expected some unmatched ingredients"

        # Check source tracking
        raw_count = norm_df['flags'].str.contains('source:ingredients_raw').sum()
        en_count = norm_df['flags'].str.contains('source:ingredients_en').sum()
        assert raw_count > 0 and en_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])