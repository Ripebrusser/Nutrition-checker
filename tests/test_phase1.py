#!/usr/bin/env python3
"""
Unit tests for Phase 1 data validation and preprocessing.
Run: python -m pytest tests/test_phase1.py -v
"""

import json
from pathlib import Path

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
DOCS_DIR = PROJECT_ROOT / "docs" / "dataset_documentation"
RAW_DIR = PROJECT_ROOT / "datasets"


class TestRawDataIntegrity:
    """Tests that raw data files exist and have expected hashes."""

    def test_recipe_csv_exists(self):
        assert (RAW_DIR / "IndianFoodDatasetCSV.csv").exists()

    def test_recipe_xlsx_exists(self):
        assert (RAW_DIR / "IndianFoodDatasetXLS.xlsx").exists()

    def test_indb_exists(self):
        assert (RAW_DIR / "Anuvaad_INDB_2024.11.xlsx").exists()

    def test_usda_files_exist(self):
        for f in ["food.csv", "nutrient.csv", "food_nutrient.csv", "measure_unit.csv", "food_portion.csv"]:
            assert (RAW_DIR / f).exists(), f"Missing {f}"

    def test_nhanes_files_exist(self):
        for f in ["BMX_L.xpt", "DEMO_L.xpt", "DIQ_L.xpt", "DR1TOT_L.xpt", "PAQ_L.xpt"]:
            assert (RAW_DIR / f).exists(), f"Missing {f}"


class TestRecipeDataset:
    """Tests for recipe dataset structure and quality."""

    @pytest.fixture(scope="class")
    def recipe_df(self):
        return pd.read_csv(RAW_DIR / "IndianFoodDatasetCSV.csv")

    def test_row_count(self, recipe_df):
        assert len(recipe_df) == 6871

    def test_column_count(self, recipe_df):
        assert len(recipe_df.columns) == 15

    def test_expected_columns(self, recipe_df):
        expected = ["Srno", "RecipeName", "TranslatedRecipeName", "Ingredients",
                    "TranslatedIngredients", "PrepTimeInMins", "CookTimeInMins",
                    "TotalTimeInMins", "Servings", "Cuisine", "Course", "Diet",
                    "Instructions", "TranslatedInstructions", "URL"]
        assert list(recipe_df.columns) == expected

    def test_pk_unique(self, recipe_df):
        assert recipe_df["Srno"].nunique() == len(recipe_df)

    def test_url_unique(self, recipe_df):
        assert recipe_df["URL"].nunique() == len(recipe_df)

    def test_missing_ingredients_count(self, recipe_df):
        missing = recipe_df["Ingredients"].isna().sum()
        assert missing == 6

    def test_time_consistency(self, recipe_df):
        inconsistent = (recipe_df["TotalTimeInMins"] !=
                        (recipe_df["PrepTimeInMins"] + recipe_df["CookTimeInMins"])).sum()
        assert inconsistent == 0

    def test_no_negative_times(self, recipe_df):
        for col in ["PrepTimeInMins", "CookTimeInMins", "TotalTimeInMins"]:
            assert (recipe_df[col] >= 0).all()

    def test_servings_positive(self, recipe_df):
        assert (recipe_df["Servings"] >= 1).all()

    def test_duplicate_translated_names(self, recipe_df):
        dup = recipe_df["TranslatedRecipeName"].duplicated(keep=False).sum()
        assert dup == 54  # 27 pairs

    def test_cuisine_pollution(self, recipe_df):
        course_like = {"Appetizer", "Snack", "Side Dish", "Dessert", "Dinner", "Lunch", "Brunch", "World Breakfast"}
        polluted = recipe_df[recipe_df["Cuisine"].isin(course_like)]
        assert len(polluted) == 15

    def test_course_pollution(self, recipe_df):
        diet_like = {"Vegetarian", "High Protein Vegetarian", "Vegan", "Non Vegeterian",
                     "Eggetarian", "No Onion No Garlic (Sattvic)", "Sugar Free Diet"}
        polluted = recipe_df[recipe_df["Course"].isin(diet_like)]
        assert len(polluted) == 62


class TestINDBDataset:
    """Tests for INDB dataset structure and quality."""

    @pytest.fixture(scope="class")
    def indb_df(self):
        return pd.read_excel(RAW_DIR / "Anuvaad_INDB_2024.11.xlsx", sheet_name="Sheet1")

    def test_row_count(self, indb_df):
        assert len(indb_df) == 1014

    def test_column_count(self, indb_df):
        assert len(indb_df.columns) == 82

    def test_food_code_unique(self, indb_df):
        assert indb_df["food_code"].nunique() == len(indb_df)

    def test_food_name_unique(self, indb_df):
        assert indb_df["food_name"].nunique() == len(indb_df)

    def test_no_missing_identifiers(self, indb_df):
        assert indb_df["food_code"].isna().sum() == 0
        assert indb_df["food_name"].isna().sum() == 0

    def test_per_serving_missing_pattern(self, indb_df):
        serving_cols = [c for c in indb_df.columns if c.startswith("unit_serving_")]
        missing_all = indb_df[serving_cols].isnull().all(axis=1).sum()
        assert missing_all == 82

    def test_no_negative_nutrients(self, indb_df):
        nutrient_cols = [c for c in indb_df.columns
                         if c not in ["food_code", "food_name", "primarysource", "servings_unit"]
                         and not c.startswith("unit_serving_")]
        for col in nutrient_cols:
            assert (indb_df[col] >= 0).all(), f"Negative values in {col}"


class TestProcessedOutputs:
    """Tests for processed data outputs."""

    def test_processed_recipes_exist(self):
        assert (PROCESSED_DIR / "recipes.parquet").exists()
        assert (PROCESSED_DIR / "recipes.csv").exists()

    def test_processed_indb_exist(self):
        assert (PROCESSED_DIR / "indb_foods.parquet").exists()
        assert (PROCESSED_DIR / "indb_foods.csv").exists()

    def test_recipes_schema(self):
        df = pd.read_parquet(PROCESSED_DIR / "recipes.parquet")
        expected_cols = {"recipe_id", "recipe_name_original", "recipe_name_en",
                         "ingredients_raw", "ingredients_en", "prep_time_min",
                         "cook_time_min", "total_time_min", "servings", "recipe_type",
                         "cuisine", "course", "diet_labels", "instructions_raw",
                         "instructions_en", "source_url", "source_domain",
                         "created_at", "updated_at"}
        assert set(df.columns) == expected_cols

    def test_recipes_pk_unique(self):
        df = pd.read_parquet(PROCESSED_DIR / "recipes.parquet")
        assert df["recipe_id"].nunique() == len(df)

    def test_recipes_time_consistency(self):
        df = pd.read_parquet(PROCESSED_DIR / "recipes.parquet")
        assert (df["total_time_min"] == df["prep_time_min"] + df["cook_time_min"]).all()

    def test_recipes_no_missing_ingredients(self):
        df = pd.read_parquet(PROCESSED_DIR / "recipes.parquet")
        assert df["ingredients_raw"].isna().sum() == 0
        assert df["ingredients_en"].isna().sum() == 0

    def test_recipes_recipe_types(self):
        df = pd.read_parquet(PROCESSED_DIR / "recipes.parquet")
        valid_types = {"main", "condiment", "prep", "beverage", "dessert"}
        assert set(df["recipe_type"].unique()).issubset(valid_types)

    def test_indb_schema(self):
        df = pd.read_parquet(PROCESSED_DIR / "indb_foods.parquet")
        assert "food_code" in df.columns
        assert "food_name" in df.columns
        assert df["food_code"].nunique() == len(df)

    def test_indb_missing_serving_flag(self):
        df = pd.read_parquet(PROCESSED_DIR / "indb_foods.parquet")
        assert "missing_serving_data" in df.columns
        assert df["missing_serving_data"].sum() == 82


class TestValidationReports:
    """Tests that validation reports were generated."""

    def test_recipe_validation_report(self):
        path = INTERIM_DIR / "validation_reports" / "recipe_validation.json"
        assert path.exists()
        with open(path) as f:
            report = json.load(f)
        assert report["overall_passed"] is True
        assert report["row_count"] == 6871

    def test_indb_validation_report(self):
        path = INTERIM_DIR / "validation_reports" / "indb_validation.json"
        assert path.exists()
        with open(path) as f:
            report = json.load(f)
        assert report["overall_passed"] is True
        assert report["row_count"] == 1014

    def test_usda_validation_report(self):
        path = INTERIM_DIR / "validation_reports" / "usda_validation.json"
        assert path.exists()
        with open(path) as f:
            report = json.load(f)
        assert report["overall_passed"] is True

    def test_nhanes_validation_report(self):
        path = INTERIM_DIR / "validation_reports" / "nhanes_validation.json"
        assert path.exists()
        with open(path) as f:
            report = json.load(f)
        assert report["overall_passed"] is True


class TestPreprocessingLogs:
    """Tests that preprocessing logs were generated."""

    def test_recipe_preprocessing_log(self):
        path = INTERIM_DIR / "preprocessing_log.json"
        assert path.exists()
        with open(path) as f:
            log = json.load(f)
        assert log["input_rows"] == 6871
        assert log["output"]["processed_rows"] == 6865  # 6871 - 6 missing ingredients

    def test_indb_preprocessing_log(self):
        path = INTERIM_DIR / "indb_preprocessing_log.json"
        assert path.exists()
        with open(path) as f:
            log = json.load(f)
        assert log["input_rows"] == 1014
        assert log["output"]["rows"] == 1014

    def test_missing_ingredients_archived(self):
        path = INTERIM_DIR / "recipes_missing_ingredients.csv"
        assert path.exists()
        df = pd.read_csv(path)
        assert len(df) == 6

    def test_condiments_archived(self):
        path = INTERIM_DIR / "recipes_condiments.csv"
        assert path.exists()
        df = pd.read_csv(path)
        assert len(df) == 35


class TestDocumentation:
    """Tests that documentation files exist."""

    def test_dataset_inventory(self):
        assert (DOCS_DIR / "dataset_inventory.md").exists()

    def test_dataset_quality_report(self):
        assert (DOCS_DIR / "dataset_quality_report.md").exists()

    def test_data_dictionary(self):
        assert (DOCS_DIR / "data_dictionary.md").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])