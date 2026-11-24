#!/usr/bin/env python3
"""
Preprocessing pipeline for Indian Food Recipe Dataset.
Run: python -m src.preprocessing.preprocess_recipes
Outputs:
  - data/processed/recipes.parquet (main corpus)
  - data/interim/recipes_missing_ingredients.csv (excluded)
  - data/interim/recipes_condiments.csv (flagged condiments)
  - data/interim/preprocessing_log.json
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Controlled vocabularies (from data dictionary)
CUISINE_REMAP = {
    # Course labels mistakenly in Cuisine -> move to Course
    "Appetizer": "Course",
    "Snack": "Course",
    "Side Dish": "Course",
    "Dessert": "Course",
    "Dinner": "Course",
    "Lunch": "Course",
    "Brunch": "Course",
    "World Breakfast": "Course",
}

COURSE_REMAP = {
    # Diet labels mistakenly in Course -> move to Diet
    "Vegetarian": "Diet",
    "High Protein Vegetarian": "Diet",
    "Vegan": "Diet",
    "Non Vegeterian": "Diet",
    "Eggetarian": "Diet",
    "No Onion No Garlic (Sattvic)": "Diet",
    "Sugar Free Diet": "Diet",
    # Valid course but descriptive
    "One Pot Dish": "One Pot Dish",
}

VALID_CUISINES = {
    "Indian", "Continental", "North Indian Recipes", "South Indian Recipes",
    "Italian Recipes", "Bengali Recipes", "Maharashtrian Recipes", "Kerala Recipes",
    "Tamil Nadu", "Karnataka", "Fusion", "Rajasthani", "Mexican", "Andhra",
    "Gujarati Recipes", "Goan Recipes", "Punjabi", "Chettinad", "Asian",
    "Thai", "Chinese", "Kashmiri", "French", "Middle Eastern", "Mangalorean",
    "Parsi Recipes", "Indo Chinese", "Awadhi", "Oriya Recipes", "Sindhi",
    "Konkan", "Mughlai", "Bihari", "Mediterranean", "Hyderabadi", "Assamese",
    "European", "North East India Recipes", "Greek", "African", "Himachal",
    "Udupi", "Sri Lankan", "Coorg", "Coastal Karnataka", "North Karnataka",
    "Uttar Pradesh", "Lucknowi", "Malabar", "Japanese", "Vietnamese", "Pakistani",
    "South Karnataka", "Malvani", "Indonesian", "Nepalese", "Cantonese",
    "American", "Sichuan", "British", "Malaysian", "Nagaland", "Arab",
    "Caribbean", "Uttarakhand-North Kumaon", "Haryana", "Korean", "Kongunadu",
    "Hunan", "Afghan", "Shandong", "Jewish", "Burmese", "Kongunadu"
}

VALID_COURSES = {
    "Breakfast", "Brunch", "Lunch", "Dinner", "Main Course", "Side Dish",
    "Snack", "Appetizer", "Dessert", "One Pot Dish", "Beverage"
}

VALID_DIETS = {
    "Vegetarian", "High Protein Vegetarian", "Non Vegeterian", "Eggetarian",
    "Diabetic Friendly", "High Protein Non Vegetarian", "No Onion No Garlic (Sattvic)",
    "Vegan", "Gluten Free", "Sugar Free Diet"
}


def standardize_cuisine(val: str) -> str:
    """Standardize cuisine value."""
    if val in CUISINE_REMAP:
        return "Other"  # Will be handled by course remapping
    return val.strip()


def standardize_course(val: str, cuisine_val: str) -> str:
    """Standardize course value, incorporating cuisine pollution."""
    # First check if cuisine had a course label
    if cuisine_val in CUISINE_REMAP:
        cuisine_course_map = {
            "Appetizer": "Appetizer",
            "Snack": "Snack",
            "Side Dish": "Side Dish",
            "Dessert": "Dessert",
            "Dinner": "Dinner",
            "Lunch": "Lunch",
            "Brunch": "Brunch",
            "World Breakfast": "Breakfast",
        }
        return cuisine_course_map.get(cuisine_val, val)

    # Then check course pollution
    if val in COURSE_REMAP:
        if COURSE_REMAP[val] == "Diet":
            return "Main Course"  # Default fallback; diet handled separately
        return COURSE_REMAP[val]

    # Normalize breakfast variants
    breakfast_variants = {
        "South Indian Breakfast": "Breakfast",
        "North Indian Breakfast": "Breakfast",
        "Indian Breakfast": "Breakfast",
        "World Breakfast": "Breakfast",
    }
    return breakfast_variants.get(val, val)


def standardize_diet(val: str, course_val: str) -> List[str]:
    """Standardize diet value, incorporating course pollution."""
    diets = [d.strip() for d in val.split(",")] if pd.notna(val) else []

    # Add diet labels that were in Course column
    if course_val in COURSE_REMAP and COURSE_REMAP[course_val] == "Diet":
        diets.append(course_val)

    # Normalize
    normalized = []
    for d in diets:
        if d in VALID_DIETS:
            normalized.append(d)
        elif d == "Non Vegetarian":  # Typo variant
            normalized.append("Non Vegeterian")
        elif d:
            logger.warning(f"Unknown diet label: {d}")

    return list(set(normalized))  # Deduplicate


def classify_recipe_type(row) -> str:
    """Classify recipe as main, condiment, prep, beverage, or dessert."""
    course = row["course_clean"]
    servings = row["Servings"]
    cuisine = row["cuisine_clean"]
    diet = row["diet_clean"]

    # Condiments: high servings (>50) typically spice mixes, pickles, batters
    if servings > 50:
        return "condiment"

    # Beverages: cuisine or course indicates drink
    if cuisine in ["Beverage"] or course == "Beverage":
        return "beverage"

    # Prep: "How to" recipes, ingredient preparations
    name = str(row["TranslatedRecipeName"]).lower()
    if name.startswith("how to") or "batter" in name or "flour" in name or "masala powder" in name:
        return "prep"

    # Dessert
    if course == "Dessert":
        return "dessert"

    return "main"


def preprocess_recipes(input_path: Path, output_dir: Path, interim_dir: Path) -> Dict:
    """Main preprocessing function."""
    logger.info(f"Reading {input_path}")
    df = pd.read_csv(input_path)

    log = {
        "input_file": str(input_path),
        "input_rows": int(len(df)),
        "input_hash": "898b74b2000ad8e152afbb769fb6e9ce",  # CSV hash
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "steps": []
    }

    # Step 1: Handle missing ingredients
    missing_ing = df[df["Ingredients"].isna()].copy()
    df_clean = df.dropna(subset=["Ingredients"]).copy()
    log["steps"].append({
        "step": "remove_missing_ingredients",
        "rows_removed": int(len(missing_ing)),
        "recipe_ids": missing_ing["Srno"].tolist(),
        "rows_remaining": int(len(df_clean))
    })

    # Save excluded recipes
    missing_path = interim_dir / "recipes_missing_ingredients.csv"
    missing_ing.to_csv(missing_path, index=False)
    logger.info(f"Saved {len(missing_ing)} missing-ingredient recipes to {missing_path}")

    # Step 2: Standardize cuisine
    df_clean["cuisine_original"] = df_clean["Cuisine"]
    df_clean["cuisine_clean"] = df_clean["Cuisine"].apply(standardize_cuisine)
    cuisine_changes = (df_clean["cuisine_original"] != df_clean["cuisine_clean"]).sum()
    log["steps"].append({
        "step": "standardize_cuisine",
        "values_remapped": int(cuisine_changes),
        "mapping": CUISINE_REMAP
    })

    # Step 3: Standardize course (uses original cuisine for pollution detection)
    df_clean["course_original"] = df_clean["Course"]
    df_clean["course_clean"] = df_clean.apply(
        lambda r: standardize_course(r["Course"], r["Cuisine"]), axis=1
    )
    course_changes = (df_clean["course_original"] != df_clean["course_clean"]).sum()
    log["steps"].append({
        "step": "standardize_course",
        "values_remapped": int(course_changes),
        "mapping": COURSE_REMAP,
        "cuisine_pollution_handled": True
    })

    # Step 4: Standardize diet (uses original course for pollution detection)
    df_clean["diet_original"] = df_clean["Diet"]
    df_clean["diet_clean"] = df_clean.apply(
        lambda r: standardize_diet(r["Diet"], r["Course"]), axis=1
    )
    log["steps"].append({
        "step": "standardize_diet",
        "course_pollution_incorporated": True,
        "diet_labels_per_row": df_clean["diet_clean"].apply(len).value_counts().to_dict()
    })

    # Step 5: Classify recipe type
    df_clean["recipe_type"] = df_clean.apply(classify_recipe_type, axis=1)
    type_counts = df_clean["recipe_type"].value_counts().to_dict()
    log["steps"].append({
        "step": "classify_recipe_type",
        "distribution": type_counts
    })

    # Step 6: Flag condiments
    condiments = df_clean[df_clean["recipe_type"] == "condiment"].copy()
    condiment_path = interim_dir / "recipes_condiments.csv"
    condiments.to_csv(condiment_path, index=False)
    log["steps"].append({
        "step": "flag_condiments",
        "count": int(len(condiments)),
        "saved_to": str(condiment_path)
    })

    # Step 7: Create final processed schema
    processed = pd.DataFrame({
        "recipe_id": df_clean["Srno"].astype(int),
        "recipe_name_original": df_clean["RecipeName"].str.strip(),
        "recipe_name_en": df_clean["TranslatedRecipeName"].str.strip(),
        "ingredients_raw": df_clean["Ingredients"].str.strip(),
        "ingredients_en": df_clean["TranslatedIngredients"].str.strip(),
        "prep_time_min": df_clean["PrepTimeInMins"].astype(int),
        "cook_time_min": df_clean["CookTimeInMins"].astype(int),
        "total_time_min": df_clean["TotalTimeInMins"].astype(int),
        "servings": df_clean["Servings"].astype(int),
        "recipe_type": df_clean["recipe_type"],
        "cuisine": df_clean["cuisine_clean"],
        "course": df_clean["course_clean"],
        "diet_labels": df_clean["diet_clean"].apply(lambda x: "|".join(sorted(x)) if x else ""),
        "instructions_raw": df_clean["Instructions"].str.strip(),
        "instructions_en": df_clean["TranslatedInstructions"].str.strip(),
        "source_url": df_clean["URL"].str.strip(),
        "source_domain": "archanaskitchen.com",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
    })

    # Step 8: Validate processed data
    assert processed["recipe_id"].nunique() == len(processed), "Duplicate recipe_ids"
    assert processed["source_url"].nunique() == len(processed), "Duplicate URLs"
    assert (processed["total_time_min"] == processed["prep_time_min"] + processed["cook_time_min"]).all(), "Time inconsistency"
    assert (processed["servings"] >= 1).all(), "Invalid servings"

    # Step 9: Save processed data
    output_path = output_dir / "recipes.parquet"
    processed.to_parquet(output_path, index=False)
    logger.info(f"Saved {len(processed)} processed recipes to {output_path}")

    # Also save CSV for readability
    csv_path = output_dir / "recipes.csv"
    processed.to_csv(csv_path, index=False)

    log["output"] = {
        "processed_rows": int(len(processed)),
        "processed_path": str(output_path),
        "recipe_type_distribution": type_counts,
        "cuisine_distribution": processed["cuisine"].value_counts().to_dict(),
        "course_distribution": processed["course"].value_counts().to_dict(),
        "diet_label_distribution": processed["diet_labels"].str.split("|").explode().value_counts().to_dict()
    }

    # Save log
    log_path = interim_dir / "preprocessing_log.json"
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)
    logger.info(f"Preprocessing log saved to {log_path}")

    return log


def main():
    project_root = Path(__file__).resolve().parents[2]
    input_path = project_root / "datasets" / "IndianFoodDatasetCSV.csv"
    output_dir = project_root / "data" / "processed"
    interim_dir = project_root / "data" / "interim"

    output_dir.mkdir(parents=True, exist_ok=True)
    interim_dir.mkdir(parents=True, exist_ok=True)

    try:
        log = preprocess_recipes(input_path, output_dir, interim_dir)
        print("\n✅ Preprocessing completed successfully")
        print(f"Processed recipes: {log['output']['processed_rows']}")
        print(f"Recipe types: {log['output']['recipe_type_distribution']}")
    except Exception as e:
        logger.error(f"Preprocessing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()