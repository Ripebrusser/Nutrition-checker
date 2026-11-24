#!/usr/bin/env python3
"""
Preprocessing pipeline for Anuvaad INDB 2024.11 Dataset.
Run: python -m src.preprocessing.preprocess_indb
Outputs:
  - data/processed/indb_foods.parquet
  - data/interim/indb_preprocessing_log.json
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Nutrient column mapping: source -> standardized
NUTRIENT_MAP_100G = {
    "energy_kj": "energy_kj_100g",
    "energy_kcal": "energy_kcal_100g",
    "carb_g": "carbohydrate_g_100g",
    "protein_g": "protein_g_100g",
    "fat_g": "fat_g_100g",
    "freesugar_g": "free_sugar_g_100g",
    "fibre_g": "fibre_g_100g",
    "sfa_mg": "sfa_mg_100g",
    "mufa_mg": "mufa_mg_100g",
    "pufa_mg": "pufa_mg_100g",
    "cholesterol_mg": "cholesterol_mg_100g",
    "calcium_mg": "calcium_mg_100g",
    "phosphorus_mg": "phosphorus_mg_100g",
    "magnesium_mg": "magnesium_mg_100g",
    "sodium_mg": "sodium_mg_100g",
    "potassium_mg": "potassium_mg_100g",
    "iron_mg": "iron_mg_100g",
    "copper_mg": "copper_mg_100g",
    "selenium_ug": "selenium_ug_100g",
    "chromium_mg": "chromium_mg_100g",
    "manganese_mg": "manganese_mg_100g",
    "molybdenum_mg": "molybdenum_mg_100g",
    "zinc_mg": "zinc_mg_100g",
    "vita_ug": "vitamin_a_ug_100g",
    "vite_mg": "vitamin_e_mg_100g",
    "vitd2_ug": "vitamin_d2_ug_100g",
    "vitd3_ug": "vitamin_d3_ug_100g",
    "vitk1_ug": "vitamin_k1_ug_100g",
    "vitk2_ug": "vitamin_k2_ug_100g",
    "folate_ug": "folate_ug_100g",
    "vitb1_mg": "vitamin_b1_mg_100g",
    "vitb2_mg": "vitamin_b2_mg_100g",
    "vitb3_mg": "vitamin_b3_mg_100g",
    "vitb5_mg": "vitamin_b5_mg_100g",
    "vitb6_mg": "vitamin_b6_mg_100g",
    "vitb7_ug": "vitamin_b7_ug_100g",
    "vitb9_ug": "vitamin_b9_ug_100g",
    "vitc_mg": "vitamin_c_mg_100g",
    "carotenoids_ug": "carotenoids_ug_100g",
}

NUTRIENT_MAP_SERVING = {
    "unit_serving_energy_kj": "serving_energy_kj",
    "unit_serving_energy_kcal": "serving_energy_kcal",
    "unit_serving_carb_g": "serving_carb_g",
    "unit_serving_protein_g": "serving_protein_g",
    "unit_serving_fat_g": "serving_fat_g",
    "unit_serving_freesugar_g": "serving_free_sugar_g",
    "unit_serving_fibre_g": "serving_fibre_g",
    "unit_serving_sfa_mg": "serving_sfa_mg",
    "unit_serving_mufa_mg": "serving_mufa_mg",
    "unit_serving_pufa_mg": "serving_pufa_mg",
    "unit_serving_cholesterol_mg": "serving_cholesterol_mg",
    "unit_serving_calcium_mg": "serving_calcium_mg",
    "unit_serving_phosphorus_mg": "serving_phosphorus_mg",
    "unit_serving_magnesium_mg": "serving_magnesium_mg",
    "unit_serving_sodium_mg": "serving_sodium_mg",
    "unit_serving_potassium_mg": "serving_potassium_mg",
    "unit_serving_iron_mg": "serving_iron_mg",
    "unit_serving_copper_mg": "serving_copper_mg",
    "unit_serving_selenium_ug": "serving_selenium_ug",
    "unit_serving_chromium_mg": "serving_chromium_mg",
    "unit_serving_manganese_mg": "serving_manganese_mg",
    "unit_serving_molybdenum_mg": "serving_molybdenum_mg",
    "unit_serving_zinc_mg": "serving_zinc_mg",
    "unit_serving_vita_ug": "serving_vitamin_a_ug",
    "unit_serving_vite_mg": "serving_vitamin_e_mg",
    "unit_serving_vitd2_ug": "serving_vitamin_d2_ug",
    "unit_serving_vitd3_ug": "serving_vitamin_d3_ug",
    "unit_serving_vitk1_ug": "serving_vitamin_k1_ug",
    "unit_serving_vitk2_ug": "serving_vitamin_k2_ug",
    "unit_serving_folate_ug": "serving_folate_ug",
    "unit_serving_vitb1_mg": "serving_vitamin_b1_mg",
    "unit_serving_vitb2_mg": "serving_vitamin_b2_mg",
    "unit_serving_vitb3_mg": "serving_vitamin_b3_mg",
    "unit_serving_vitb5_mg": "serving_vitamin_b5_mg",
    "unit_serving_vitb6_mg": "serving_vitamin_b6_mg",
    "unit_serving_vitb7_ug": "serving_vitamin_b7_ug",
    "unit_serving_vitb9_ug": "serving_vitamin_b9_ug",
    "unit_serving_vitc_mg": "serving_vitamin_c_mg",
    "unit_serving_carotenoids_ug": "serving_carotenoids_ug",
}


def preprocess_indb(input_path: Path, output_dir: Path, interim_dir: Path) -> dict:
    """Main preprocessing function for INDB."""
    logger.info(f"Reading {input_path}")
    df = pd.read_excel(input_path, sheet_name="Sheet1")

    log = {
        "input_file": str(input_path),
        "input_rows": int(len(df)),
        "input_hash": "f4db8039b33a6de9d6f602ee372aebab",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "steps": []
    }

    # Step 1: Verify primary key
    assert df["food_code"].nunique() == len(df), "Duplicate food_code"
    assert df["food_name"].nunique() == len(df), "Duplicate food_name"
    log["steps"].append({
        "step": "verify_keys",
        "food_code_unique": True,
        "food_name_unique": True
    })

    # Step 2: Rename columns to standardized names
    rename_map = {}
    rename_map.update(NUTRIENT_MAP_100G)
    rename_map.update(NUTRIENT_MAP_SERVING)
    rename_map["primarysource"] = "primary_source"
    rename_map["servings_unit"] = "serving_unit"

    df_renamed = df.rename(columns=rename_map)
    log["steps"].append({
        "step": "rename_columns",
        "columns_renamed": len(rename_map)
    })

    # Step 3: Identify per-serving missing pattern (exclude serving_unit)
    serving_nutrient_cols = [c for c in df_renamed.columns if c.startswith("serving_") and c != "serving_unit"]
    nutrient_100g_cols = sorted([c for c in df_renamed.columns if c.endswith("_100g")])
    missing_all_serving = df_renamed[serving_nutrient_cols].isnull().all(axis=1)
    missing_count = int(missing_all_serving.sum())
    missing_food_codes = df_renamed.loc[missing_all_serving, "food_code"].tolist()
    log["steps"].append({
        "step": "identify_missing_serving",
        "serving_nutrient_columns": len(serving_nutrient_cols),
        "rows_missing_all_serving": missing_count,
        "missing_food_codes": missing_food_codes
    })

    # Step 4: Add metadata columns
    df_renamed["missing_serving_data"] = missing_all_serving
    df_renamed["nutrient_completeness_100g"] = df_renamed[nutrient_100g_cols].notna().sum(axis=1)
    df_renamed["created_at"] = datetime.utcnow().isoformat() + "Z"
    df_renamed["updated_at"] = datetime.utcnow().isoformat() + "Z"

    # Step 5: Ensure consistent ordering
    id_cols = ["food_code", "food_name", "primary_source", "serving_unit", "missing_serving_data", "nutrient_completeness_100g"]
    serving_nutrient_cols_sorted = sorted([c for c in df_renamed.columns if c.startswith("serving_") and c != "serving_unit"])
    meta_cols = ["created_at", "updated_at"]

    final_cols = id_cols + nutrient_100g_cols + serving_nutrient_cols_sorted + meta_cols
    df_final = df_renamed[final_cols]

    # Step 6: Validate
    assert df_final["food_code"].nunique() == len(df_final)
    assert (df_final["nutrient_completeness_100g"] >= 0).all()

    # Step 7: Save
    output_path = output_dir / "indb_foods.parquet"
    df_final.to_parquet(output_path, index=False)
    logger.info(f"Saved {len(df_final)} INDB foods to {output_path}")

    # Also save CSV
    csv_path = output_dir / "indb_foods.csv"
    df_final.to_csv(csv_path, index=False)

    log["output"] = {
        "rows": int(len(df_final)),
        "columns": int(len(df_final.columns)),
        "path": str(output_path),
        "per_100g_nutrients": len(nutrient_100g_cols),
        "per_serving_nutrients": len(serving_nutrient_cols_sorted),
        "missing_serving_rows": missing_count,
        "primary_source_distribution": df_final["primary_source"].value_counts().to_dict(),
        "serving_unit_distribution": df_final["serving_unit"].value_counts().head(20).to_dict()
    }

    # Save log
    log_path = interim_dir / "indb_preprocessing_log.json"
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)
    logger.info(f"Preprocessing log saved to {log_path}")

    return log


def main():
    project_root = Path(__file__).resolve().parents[2]
    input_path = project_root / "datasets" / "Anuvaad_INDB_2024.11.xlsx"
    output_dir = project_root / "data" / "processed"
    interim_dir = project_root / "data" / "interim"

    output_dir.mkdir(parents=True, exist_ok=True)
    interim_dir.mkdir(parents=True, exist_ok=True)

    try:
        log = preprocess_indb(input_path, output_dir, interim_dir)
        print("\n✅ INDB preprocessing completed successfully")
        print(f"Processed foods: {log['output']['rows']}")
        print(f"Per-100g nutrients: {log['output']['per_100g_nutrients']}")
        print(f"Per-serving nutrients: {log['output']['per_serving_nutrients']}")
        print(f"Missing serving data: {log['output']['missing_serving_rows']} rows")
    except Exception as e:
        logger.error(f"Preprocessing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()