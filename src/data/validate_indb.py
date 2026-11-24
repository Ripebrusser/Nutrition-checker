#!/usr/bin/env python3
"""
Validation script for Anuvaad INDB 2024.11 Dataset.
Run: python -m src.data.validate_indb
Outputs JSON report to data/interim/validation_reports/indb_validation.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd


def validate_indb_dataset(xlsx_path: Path) -> dict:
    """Run all validation checks on the INDB dataset."""
    df = pd.read_excel(xlsx_path, sheet_name="Sheet1")

    report = {
        "dataset": "Anuvaad_INDB_2024.11",
        "source_file": str(xlsx_path),
        "validation_timestamp": datetime.utcnow().isoformat() + "Z",
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "checks": {}
    }

    # 1. Primary key uniqueness (food_code)
    pk_unique = df["food_code"].nunique() == len(df)
    report["checks"]["pk_unique"] = {
        "column": "food_code",
        "unique_count": int(df["food_code"].nunique()),
        "total_count": int(len(df)),
        "passed": bool(pk_unique)
    }

    # 2. food_name uniqueness
    name_unique = df["food_name"].nunique() == len(df)
    report["checks"]["food_name_unique"] = {
        "unique_count": int(df["food_name"].nunique()),
        "total_count": int(len(df)),
        "passed": bool(name_unique)
    }

    # 3. Missing values per column
    missing = df.isnull().sum().to_dict()
    report["checks"]["missing_values"] = {
        col: {"count": int(cnt), "pct": round(cnt / len(df) * 100, 2)}
        for col, cnt in missing.items()
    }

    # 4. Per-serving missing pattern (should be same 82 rows across all unit_serving_* columns)
    serving_cols = [c for c in df.columns if c.startswith("unit_serving_")]
    if serving_cols:
        missing_serving = df[serving_cols].isnull().all(axis=1)
        missing_count = int(missing_serving.sum())
        missing_rows = df[missing_serving]["food_code"].tolist()
        consistent = all(df[col].isnull().sum() == missing_count for col in serving_cols)
        report["checks"]["per_serving_missing_pattern"] = {
            "serving_columns_count": len(serving_cols),
            "rows_missing_all_serving": missing_count,
            "missing_row_food_codes": missing_rows,
            "consistent_across_columns": bool(consistent),
            "passed": bool(missing_count == 82)
        }

    # 5. Nutrient column groups
    nutrient_cols_100g = [c for c in df.columns if not c.startswith("unit_serving_")
                          and c not in ["food_code", "food_name", "primarysource", "servings_unit"]]
    report["checks"]["nutrient_columns"] = {
        "per_100g_count": len(nutrient_cols_100g),
        "per_serving_count": len(serving_cols),
        "per_100g_columns": nutrient_cols_100g,
        "per_serving_columns": serving_cols
    }

    # 6. Primary source values
    source_counts = df["primarysource"].value_counts().to_dict()
    report["checks"]["primary_source"] = {
        "unique_values": list(source_counts.keys()),
        "counts": {k: int(v) for k, v in source_counts.items()}
    }

    # 7. Serving unit values
    serving_unit_counts = df["servings_unit"].value_counts().head(20).to_dict()
    report["checks"]["serving_units"] = {
        "unique_count": int(df["servings_unit"].nunique()),
        "top_20": {k: int(v) for k, v in serving_unit_counts.items()}
    }

    # 8. Data types
    report["checks"]["dtypes"] = {col: str(dtype) for col, dtype in df.dtypes.items()}

    # 9. Numeric ranges for key nutrients (sanity check)
    key_nutrients = ["energy_kcal", "protein_g", "fat_g", "carb_g", "fibre_g",
                     "calcium_mg", "iron_mg", "vitc_mg"]
    range_checks = {}
    for nut in key_nutrients:
        if nut in df.columns:
            s = df[nut]
            range_checks[nut] = {
                "min": float(s.min()),
                "max": float(s.max()),
                "median": float(s.median()),
                "null_count": int(s.isnull().sum())
            }
    report["checks"]["key_nutrient_ranges"] = range_checks

    # 10. Negative values check (nutrients should be >= 0)
    negative_checks = {}
    for nut in nutrient_cols_100g:
        neg_count = int((df[nut] < 0).sum())
        if neg_count > 0:
            negative_checks[nut] = neg_count
    report["checks"]["negative_values"] = {
        "columns_with_negatives": negative_checks,
        "passed": bool(len(negative_checks) == 0)
    }

    # Overall pass/fail
    critical_checks = ["pk_unique", "food_name_unique", "per_serving_missing_pattern", "negative_values"]
    report["overall_passed"] = all(report["checks"][c]["passed"] for c in critical_checks)

    return report


def main():
    project_root = Path(__file__).resolve().parents[2]
    xlsx_path = project_root / "datasets" / "Anuvaad_INDB_2024.11.xlsx"
    output_dir = project_root / "data" / "interim" / "validation_reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Validating {xlsx_path}...")
    report = validate_indb_dataset(xlsx_path)

    output_path = output_dir / "indb_validation.json"
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Validation report written to {output_path}")
    print(f"Overall passed: {report['overall_passed']}")

    for check_name, result in report["checks"].items():
        status = "✅" if result.get("passed", True) else "❌"
        print(f"  {status} {check_name}")

    if not report["overall_passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()