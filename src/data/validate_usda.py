#!/usr/bin/env python3
"""
Smoke validation script for USDA FoodData Central datasets.
Run: python -m src.data.validate_usda
Outputs JSON report to data/interim/validation_reports/usda_validation.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd


def validate_usda_datasets(data_dir: Path) -> dict:
    """Run smoke validation checks on USDA FDC datasets."""
    report = {
        "dataset": "USDA_FoodData_Central",
        "source_dir": str(data_dir),
        "validation_timestamp": datetime.utcnow().isoformat() + "Z",
        "checks": {}
    }

    # 1. food.csv
    food_path = data_dir / "food.csv"
    if food_path.exists():
        df_food = pd.read_csv(food_path, low_memory=False)
        report["checks"]["food"] = {
            "rows": int(len(df_food)),
            "columns": list(df_food.columns),
            "fdc_id_unique": int(df_food["fdc_id"].nunique()) == len(df_food),
            "missing_description": int(df_food["description"].isnull().sum()),
            "missing_food_category_id": int(df_food["food_category_id"].isnull().sum()),
            "data_type_counts": df_food["data_type"].value_counts().to_dict()
        }
    else:
        report["checks"]["food"] = {"error": "File not found"}

    # 2. nutrient.csv
    nutrient_path = data_dir / "nutrient.csv"
    if nutrient_path.exists():
        df_nut = pd.read_csv(nutrient_path)
        report["checks"]["nutrient"] = {
            "rows": int(len(df_nut)),
            "columns": list(df_nut.columns),
            "id_unique": int(df_nut["id"].nunique()) == len(df_nut),
            "unit_name_counts": df_nut["unit_name"].value_counts().head(10).to_dict()
        }
    else:
        report["checks"]["nutrient"] = {"error": "File not found"}

    # 3. food_nutrient.csv (sample check - large file)
    fn_path = data_dir / "food_nutrient.csv"
    if fn_path.exists():
        # Read first 10000 rows for speed
        df_fn = pd.read_csv(fn_path, nrows=10000, low_memory=False)
        report["checks"]["food_nutrient_sample"] = {
            "sample_rows": int(len(df_fn)),
            "columns": list(df_fn.columns),
            "unique_fdc_id_sample": int(df_fn["fdc_id"].nunique()),
            "unique_nutrient_id_sample": int(df_fn["nutrient_id"].nunique()),
            "missing_amount": int(df_fn["amount"].isnull().sum()),
            "derivation_id_counts": df_fn["derivation_id"].value_counts().head(5).to_dict()
        }
        # Full row count via fast method
        with open(fn_path, "r") as f:
            full_rows = sum(1 for _ in f) - 1  # minus header
        report["checks"]["food_nutrient_sample"]["full_row_count_estimate"] = full_rows
    else:
        report["checks"]["food_nutrient_sample"] = {"error": "File not found"}

    # 4. measure_unit.csv
    mu_path = data_dir / "measure_unit.csv"
    if mu_path.exists():
        df_mu = pd.read_csv(mu_path)
        report["checks"]["measure_unit"] = {
            "rows": int(len(df_mu)),
            "columns": list(df_mu.columns),
            "sample": df_mu.head(10).to_dict("records")
        }
    else:
        report["checks"]["measure_unit"] = {"error": "File not found"}

    # 5. food_portion.csv
    fp_path = data_dir / "food_portion.csv"
    if fp_path.exists():
        df_fp = pd.read_csv(fp_path, low_memory=False)
        report["checks"]["food_portion"] = {
            "rows": int(len(df_fp)),
            "columns": list(df_fp.columns),
            "missing_fdc_id": int(df_fp["fdc_id"].isnull().sum()),
            "missing_gram_weight": int(df_fp["gram_weight"].isnull().sum()),
            "missing_portion_description": int(df_fp["portion_description"].isnull().sum()),
            "gram_weight_stats": {
                "min": float(df_fp["gram_weight"].min()),
                "max": float(df_fp["gram_weight"].max()),
                "median": float(df_fp["gram_weight"].median())
            }
        }
    else:
        report["checks"]["food_portion"] = {"error": "File not found"}

    # Overall: all files present
    expected_files = ["food.csv", "nutrient.csv", "food_nutrient.csv", "measure_unit.csv", "food_portion.csv"]
    present = all((data_dir / f).exists() for f in expected_files)
    report["overall_passed"] = present

    return report


def main():
    project_root = Path(__file__).resolve().parents[2]
    data_dir = project_root / "datasets"
    output_dir = project_root / "data" / "interim" / "validation_reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Validating USDA FDC datasets in {data_dir}...")
    report = validate_usda_datasets(data_dir)

    output_path = output_dir / "usda_validation.json"
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Validation report written to {output_path}")
    print(f"Overall passed: {report['overall_passed']}")

    for check_name, result in report["checks"].items():
        if "error" in result:
            print(f"  ❌ {check_name}: {result['error']}")
        else:
            print(f"  ✅ {check_name}: {result.get('rows', 'N/A')} rows")

    if not report["overall_passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()