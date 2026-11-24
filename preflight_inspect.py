#!/usr/bin/env python3
"""
Stage 0 Preflight Inspection - Repository and Data Structure
"""

import pandas as pd
import json
from pathlib import Path

print("="*70)
print("STAGE 0 - REPOSITORY AND DATA PREFLIGHT")
print("="*70)

# ============================================================
# 1. REPOSITORY STRUCTURE
# ============================================================
print("\n1. REPOSITORY STRUCTURE")
print("-"*40)

import os
for root, dirs, files in os.walk("C:\\Users\\Sachin\\OneDrive\\Documents\\ML_proj"):
    level = root.replace("C:\\Users\\Sachin\\OneDrive\\Documents\\ML_proj", "").count(os.sep)
    indent = " " * 2 * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = " " * 2 * (level + 1)
    for file in sorted(files):
        if not file.startswith('__pycache__') and not file.endswith('.pyc'):
            print(f"{subindent}{file}")

# ============================================================
# 2. INPUT FILE PATHS
# ============================================================
print("\n\n2. INPUT FILE PATHS AND EXISTENCE")
print("-"*40)

input_files = {
    "recipes.csv": "data/processed/recipes.csv",
    "recipes.parquet": "data/processed/recipes.parquet",
    "ifct_candidate.csv": "data/interim/ifct_final_candidate/ifct_table1_candidate.csv",
    "ifct_candidate.parquet": "data/interim/ifct_final_candidate/ifct_table1_candidate.parquet",
    "indb_foods.parquet": "data/processed/indb_foods.parquet",
    "indb_foods.csv": "data/processed/indb_foods.csv",
    "ifct_official.pdf": "data/raw/nutrition/IFCT_2017/IFCT2017.pdf",
    "ifct_decrypted.pdf": "data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf",
    "IndianFoodDatasetXLS.xlsx": "datasets/IndianFoodDatasetXLS.xlsx",
    "Anuvaad_INDB_2024.11.xlsx": "datasets/Anuvaad_INDB_2024.11.xlsx",
}

for name, path in input_files.items():
    exists = Path(path).exists()
    size = Path(path).stat().st_size if exists else 0
    print(f"  {name}: {'✅' if exists else '❌'} ({size:,} bytes) - {path}")

# ============================================================
# 3. RECIPES SCHEMA
# ============================================================
print("\n\n3. RECIPES SCHEMA (6,865 records)")
print("-"*40)

recipes = pd.read_parquet("data/processed/recipes.parquet")
print(f"Shape: {recipes.shape}")
print(f"Columns ({len(recipes.columns)}):")
for col in recipes.columns:
    dtype = recipes[col].dtype
    nulls = recipes[col].isna().sum()
    print(f"  {col}: {dtype} (nulls: {nulls})")

# Show sample ingredient data
print("\nSample ingredients_raw:")
for i in range(min(5, len(recipes))):
    print(f"  Recipe {recipes.iloc[i]['recipe_id']}: {recipes.iloc[i]['ingredients_raw'][:100]}...")

print("\nSample ingredients_en:")
for i in range(min(5, len(recipes))):
    print(f"  Recipe {recipes.iloc[i]['recipe_id']}: {recipes.iloc[i]['ingredients_en'][:100]}...")

# ============================================================
# 4. IFCT SCHEMA
# ============================================================
print("\n\n4. IFCT CANDIDATE SCHEMA (528 records)")
print("-"*40)

ifct = pd.read_parquet("data/interim/ifct_final_candidate/ifct_table1_candidate.parquet")
print(f"Shape: {ifct.shape}")
print(f"Columns ({len(ifct.columns)}):")
for col in ifct.columns:
    dtype = ifct[col].dtype
    nulls = ifct[col].isna().sum()
    print(f"  {col}: {dtype} (nulls: {nulls})")

# Nutrient columns detail
nutrient_cols = [c for c in ifct.columns if any(kw in c for kw in ['g', 'kj', 'energy', 'fibre', 'protein', 'fat', 'ash', 'moisture', 'carb'])]
print(f"\nNutrient columns: {nutrient_cols}")

# Sample records
print("\nSample IFCT records:")
for i in range(min(5, len(ifct))):
    row = ifct.iloc[i]
    print(f"  {row['food_code']}: {row['food_name'][:50]} | {row['food_group']} | moisture={row['moisture_g']} | protein={row['protein_g']} | fat={row['fat_g']} | energy={row['energy_kj']}")

# Food group distribution
print(f"\nFood group distribution:")
print(ifct['food_group'].value_counts())

# ============================================================
# 5. INDB SCHEMA
# ============================================================
print("\n\n5. INDB SCHEMA (1,014 records)")
print("-"*40)

indb = pd.read_parquet("data/processed/indb_foods.parquet")
print(f"Shape: {indb.shape}")
print(f"Columns ({len(indb.columns)}):")
for col in indb.columns:
    dtype = indb[col].dtype
    nulls = indb[col].isna().sum()
    print(f"  {col}: {dtype} (nulls: {nulls})")

# Per-serving columns
per_serving = [c for c in indb.columns if 'serving' in c.lower()]
print(f"\nPer-serving columns ({len(per_serving)}): {per_serving}")

# 100g columns
per_100g = [c for c in indb.columns if '100g' in c.lower()]
print(f"\nPer-100g columns ({len(per_100g)}): {per_100g[:20]}...")

# Sample
print("\nSample INDB records:")
for i in range(min(3, len(indb))):
    row = indb.iloc[i]
    print(f"  {row['food_code']}: {row['food_name'][:50]} | serving_unit={row.get('serving_unit', 'N/A')} | energy_kcal_100g={row.get('energy_kcal_100g', 'N/A')}")

# ============================================================
# 6. EXISTING CODE INSPECTION
# ============================================================
print("\n\n6. EXISTING PREPROCESSING CODE")
print("-"*40)

preprocess_files = [
    "src/preprocessing/preprocess_recipes.py",
    "src/preprocessing/preprocess_indb.py",
    "src/preprocessing/run_all.py",
]

for f in preprocess_files:
    if Path(f).exists():
        print(f"\n--- {f} ---")
        with open(f, 'r') as fp:
            content = fp.read()
            print(content[:2000])
            if len(content) > 2000:
                print(f"... ({len(content)} total chars)")

# ============================================================
# 7. DEPENDENCIES AND TEST INFRASTRUCTURE
# ============================================================
print("\n\n7. DEPENDENCIES AND TEST INFRASTRUCTURE")
print("-"*40)

# Check requirements
if Path("requirements.txt").exists():
    with open("requirements.txt") as f:
        print("requirements.txt:")
        print(f.read())
else:
    print("No requirements.txt found")

# Check test files
test_files = list(Path("tests").glob("*.py"))
print(f"\nTest files: {[str(f) for f in test_files]}")

with open("tests/test_phase1.py") as f:
    print("\ntest_phase1.py (first 100 lines):")
    for i, line in enumerate(f):
        if i < 100:
            print(line.rstrip())
        else:
            break

# ============================================================
# 8. DOCUMENTATION FILES
# ============================================================
print("\n\n8. KEY DOCUMENTATION FILES")
print("-"*40)

doc_files = [
    "docs/dataset_documentation/ifct_independent_acceptance_review.md",
    "docs/dataset_documentation/final_evidence_reconciliation.md",
    "docs/dataset_documentation/ifct_final_acceptance_audit.md",
    "docs/dataset_documentation/data_dictionary.md",
]

for f in doc_files:
    if Path(f).exists():
        print(f"\n--- {f} ---")
        with open(f) as fp:
            print(fp.read()[:500])
            print("...")

# ============================================================
# 9. IFCT EXTRACTOR CODE
# ============================================================
print("\n\n9. IFCT EXTRACTOR CODE (for reference)")
print("-"*40)

extractor_files = list(Path("src/data").glob("*ifct*"))
print(f"IFCT extractor files: {[str(f) for f in extractor_files]}")

# ============================================================
# 10. DATA LIMITATIONS AND ISSUES
# ============================================================
print("\n\n10. DATA LIMITATIONS AND ISSUES IDENTIFIED")
print("-"*40)

print("""
RECIPES:
- 6,865 recipes with ingredients_raw and ingredients_en
- ingredients_raw: original text (may contain regional names, quantities, preparation notes)
- ingredients_en: translated/standardized English version
- 6 records excluded (missing ingredients), 35 condiments flagged
- No parsed quantity/unit structure yet

IFCT:
- 528 verified food records with nutrient values per 100g
- Nutrients: moisture_g, protein_g, fat_g, ash_g, fibre_total_g, fibre_insoluble_g, fibre_soluble_g, carb_available_g, energy_kj
- Some nutrients have ± uncertainty notation (e.g., "76.51±0.20")
- Missing fibre/carb data for many items (animal products, some others)
- Food groups verified against PDF section structure

INDB:
- 1,014 prepared dishes/beverages (NOT raw ingredients)
- Per-100g and per-serving nutrition
- Many missing per-serving values
- Cannot be used as raw ingredient substitutes

LIMITATIONS:
- Recipe ingredients need normalization, parsing, matching
- No household measurement conversion table exists yet
- No ingredient-IFCT matching system exists yet
- Cooking retention factors not available
- No gold-standard evaluation set for matching
""")

print("\n\n=== PREFLIGHT INSPECTION COMPLETE ===")