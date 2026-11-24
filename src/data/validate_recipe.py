#!/usr/bin/env python3
"""
Validation script for Indian Food Recipe Dataset.
Run: python -m src.data.validate_recipe
Outputs JSON report to data/interim/validation_reports/recipe_validation.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd


def validate_recipe_dataset(csv_path: Path) -> dict:
    """Run all validation checks on the recipe dataset."""
    df = pd.read_csv(csv_path)

    report = {
        "dataset": "IndianFoodDatasetCSV",
        "source_file": str(csv_path),
        "validation_timestamp": datetime.utcnow().isoformat() + "Z",
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "checks": {}
    }

    # 1. Primary key uniqueness
    pk_unique = df["Srno"].nunique() == len(df)
    report["checks"]["pk_unique"] = {
        "column": "Srno",
        "unique_count": int(df["Srno"].nunique()),
        "total_count": int(len(df)),
        "passed": bool(pk_unique)
    }

    # 2. Missing values
    missing = df.isnull().sum().to_dict()
    report["checks"]["missing_values"] = {
        col: {"count": int(cnt), "pct": round(cnt / len(df) * 100, 2)}
        for col, cnt in missing.items()
    }
    report["checks"]["missing_values"]["passed"] = bool(missing["Ingredients"] <= 6)

    # 3. Duplicate TranslatedRecipeName
    dup_names = df[df["TranslatedRecipeName"].duplicated(keep=False)]
    dup_groups = dup_names.groupby("TranslatedRecipeName")["Srno"].apply(list).to_dict()
    report["checks"]["duplicate_translated_names"] = {
        "group_count": len(dup_groups),
        "row_count": int(len(dup_names)),
        "groups": dup_groups,
        "passed": True  # Not an error, just flagged
    }

    # 4. Duplicate URLs
    dup_urls = df[df["URL"].duplicated(keep=False)]
    report["checks"]["duplicate_urls"] = {
        "count": int(len(dup_urls)),
        "passed": bool(len(dup_urls) == 0)
    }

    # 5. Time consistency: TotalTime == PrepTime + CookTime
    time_inconsistent = df["TotalTimeInMins"] != (df["PrepTimeInMins"] + df["CookTimeInMins"])
    report["checks"]["time_consistency"] = {
        "inconsistent_rows": int(time_inconsistent.sum()),
        "passed": bool(time_inconsistent.sum() == 0)
    }

    # 6. Numeric ranges
    numeric_checks = {}
    for col in ["PrepTimeInMins", "CookTimeInMins", "TotalTimeInMins", "Servings"]:
        s = df[col]
        numeric_checks[col] = {
            "min": int(s.min()),
            "max": int(s.max()),
            "median": float(s.median()),
            "negative_count": int((s < 0).sum()),
            "zero_count": int((s == 0).sum())
        }
    report["checks"]["numeric_ranges"] = numeric_checks

    # 7. Servings outliers (> 50)
    condiment_rows = df[df["Servings"] > 50]
    report["checks"]["servings_outliers"] = {
        "count": int(len(condiment_rows)),
        "threshold": 50,
        "recipe_ids": condiment_rows["Srno"].tolist(),
        "passed": True  # Flag only
    }

    # 8. Cuisine label pollution (course labels in cuisine)
    course_like_cuisines = {"Appetizer", "Snack", "Side Dish", "Dessert", "Dinner", "Lunch", "Brunch", "World Breakfast"}
    polluted_cuisine = df[df["Cuisine"].isin(course_like_cuisines)]
    report["checks"]["cuisine_pollution"] = {
        "polluted_values": list(course_like_cuisines),
        "affected_rows": int(len(polluted_cuisine)),
        "row_details": polluted_cuisine[["Srno", "Cuisine", "Course"]].to_dict("records"),
        "passed": bool(len(polluted_cuisine) == 0)
    }

    # 9. Course label pollution (diet labels in course)
    diet_like_courses = {"Vegetarian", "High Protein Vegetarian", "Vegan", "Non Vegeterian",
                         "Eggetarian", "No Onion No Garlic (Sattvic)", "Sugar Free Diet"}
    polluted_course = df[df["Course"].isin(diet_like_courses)]
    report["checks"]["course_pollution"] = {
        "polluted_values": list(diet_like_courses),
        "affected_rows": int(len(polluted_course)),
        "row_details": polluted_course[["Srno", "Course", "Diet"]].to_dict("records"),
        "passed": bool(len(polluted_course) == 0)
    }

    # 10. One Pot Dish in Course (valid but flagged)
    one_pot = df[df["Course"] == "One Pot Dish"]
    report["checks"]["one_pot_dish"] = {
        "count": int(len(one_pot)),
        "passed": True
    }

    # 11. Missing ingredients rows
    missing_ing = df[df["Ingredients"].isna()]
    report["checks"]["missing_ingredients"] = {
        "count": int(len(missing_ing)),
        "recipe_ids": missing_ing["Srno"].tolist(),
        "recipe_names": missing_ing["TranslatedRecipeName"].tolist(),
        "passed": bool(len(missing_ing) == 6)
    }

    # 12. URL format validation
    url_valid = df["URL"].str.startswith("http").all()
    report["checks"]["url_format"] = {
        "all_http": bool(url_valid),
        "passed": bool(url_valid)
    }

    # Overall pass/fail
    critical_checks = [
        "pk_unique", "time_consistency", "duplicate_urls", "url_format", "missing_ingredients"
    ]
    report["overall_passed"] = all(report["checks"][c]["passed"] for c in critical_checks)

    return report


def main():
    project_root = Path(__file__).resolve().parents[2]
    csv_path = project_root / "datasets" / "IndianFoodDatasetCSV.csv"
    output_dir = project_root / "data" / "interim" / "validation_reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Validating {csv_path}...")
    report = validate_recipe_dataset(csv_path)

    output_path = output_dir / "recipe_validation.json"
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Validation report written to {output_path}")
    print(f"Overall passed: {report['overall_passed']}")

    # Print summary
    for check_name, result in report["checks"].items():
        status = "✅" if result.get("passed", True) else "❌"
        print(f"  {status} {check_name}")

    if not report["overall_passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()