# Dataset Inventory Report

**Project:** AI for Nutrition & Diet Planning: Personalized Indian Meal Recommendations Using Health Metrics and Ingredient-Level Nutrition Analysis
**Phase:** 1 — Dataset Validation and Preprocessing
**Date:** 2026-11-15

---

## 1. Dataset Catalogue

| # | Filename | Source | Format | Size (MB) | Rows | Columns | Licence/Provenance |
|---|----------|--------|--------|-----------|------|---------|-------------------|
| 1 | IndianFoodDatasetXLS.xlsx | Archive.org / Archanas Kitchen (scraped) | XLSX | 5.28 | 6,871 | 15 | Unknown — scraped recipe data; no explicit licence found |
| 2 | IndianFoodDatasetCSV.csv | Same as above | CSV | 23.03 | 6,871 | 15 | Duplicate of XLSX |
| 3 | Anuvaad_INDB_2024.11.xlsx | Anuvaad / ICMR-NIN Indian Food Composition Database | XLSX | 1.01 | 1,014 | 82 | ICMR-NIN INDB 2024; academic/research use; redistribution terms unclear |
| 4 | food.csv | USDA FoodData Central (FDC) | CSV | 6.89 | 87,990 | 5 | USDA — public domain (US government work) |
| 5 | food_nutrient.csv | USDA FDC | CSV | 9.62 | 170,469 | 11 | USDA — public domain |
| 6 | nutrient.csv | USDA FDC | CSV | 0.02 | 477 | 5 | USDA — public domain |
| 7 | measure_unit.csv | USDA FDC | CSV | 0.00 | 123 | 2 | USDA — public domain |
| 8 | food_portion.csv | USDA FDC | CSV | 0.68 | 10,951 | 11 | USDA — public domain |
| 9 | BMX_L.xpt | NHANES 2019-2020 (CDC) | XPT | 1.49 | 8,860 | 22 | CDC — public domain |
| 10 | DEMO_L.xpt | NHANES 2019-2020 (CDC) | XPT | 2.46 | 11,933 | 27 | CDC — public domain |
| 11 | DIQ_L.xpt | NHANES 2019-2020 (CDC) | XPT | 0.81 | 11,744 | 9 | CDC — public domain |
| 12 | DR1TOT_L.xpt | NHANES 2019-2020 (CDC) | XPT | 11.38 | 8,860 | 168 | CDC — public domain |
| 13 | PAQ_L.xpt | NHANES 2019-2020 (CDC) | XPT | 0.39 | 8,153 | 8 | CDC — public domain |

---

## 2. File Integrity (MD5 Hashes)

| Filename | MD5 Hash |
|----------|----------|
| IndianFoodDatasetXLS.xlsx | 889aa76ce87ba485422edb365234898d |
| IndianFoodDatasetCSV.csv | 898b74b2000ad8e152afbb769fb6e9ce |
| Anuvaad_INDB_2024.11.xlsx | f4db8039b33a6de9d6f602ee372aebab |
| food.csv | c03e244f9272b8984471ee9aa503c68d |
| food_nutrient.csv | a51418badaafd749e121191a2d8c247d |
| nutrient.csv | 33d56417f58847ebfe582214b4b01898 |
| measure_unit.csv | bbd9c2b499e82b58e95089c2451c2693 |
| food_portion.csv | ad2f2d6cc272063ac188582e2eb46de4 |
| BMX_L.xpt | ab25a36296e5b61881d42fef61c06b84 |
| DEMO_L.xpt | 14555b1f4e3c909172e900f63a2ecd03 |
| DIQ_L.xpt | 59760c8e3765f44dff6e27fef2c02e43 |
| DR1TOT_L.xpt | ccf9fc0ed652adfe5c10d27555b15833 |
| PAQ_L.xpt | 1010e68a314d12168821ef58a6d99436 |

---

## 3. Dataset Roles & Suitability Summary

| Dataset | Role | Suitable for Core Recommendation? | Reason |
|---------|------|-----------------------------------|--------|
| IndianFoodDatasetXLS/CSV | Primary recipe corpus | **Yes** | 6,871 Indian recipes with ingredients, instructions, diet/course/cuisine labels |
| Anuvaad_INDB_2024.11.xlsx | Raw food composition (ingredient-level) | **Yes** | 1,014 Indian foods with 40+ nutrients per 100g and per serving |
| USDA FDC (food.csv, food_nutrient.csv, etc.) | Supplementary composition | **Conditional** | US foods; nutrient units match but food names differ; use only for gap-filling with explicit mapping |
| NHANES (BMX, DEMO, DIQ, DR1TOT, PAQ) | Population health survey | **No — keep separate** | US population; not Indian; dietary recalls not recipes; use only for external validation or epidemiology studies |
| diet_recommendations_dataset.csv (referenced in requirements) | Derived disease→diet mapping | **No — exclude** | Target derived from disease categories (leakage risk); not in current dataset folder |

---

## 4. Column-Level Summary (Key Datasets)

### 3.1 Indian Food Recipe Dataset (IndianFoodDatasetXLS.xlsx / CSV)

| Column | Type | Non-Null | Unique | Notes |
|--------|------|----------|--------|-------|
| Srno | int64 | 6,871 | 6,871 | Sequential ID (1–6871) |
| RecipeName | str | 6,871 | 6,871 | Original name (mixed Hindi/English) |
| TranslatedRecipeName | str | 6,871 | 6,844 | 27 duplicates — English translation |
| Ingredients | str | 6,865 | — | 6 missing; comma-separated, quantities embedded |
| TranslatedIngredients | str | 6,865 | — | 6 missing; English translation |
| PrepTimeInMins | int64 | 6,871 | — | Range: 0–? |
| CookTimeInMins | int64 | 6,871 | — | Range: 0–? |
| TotalTimeInMins | int64 | 6,871 | — | Prep + Cook (verify consistency) |
| Servings | int64 | 6,871 | — | Integer servings |
| Cuisine | str | 6,871 | 82 | Some values are actually courses (e.g., "Dinner", "Lunch") |
| Course | str | 6,871 | 20 | Some values are diets (e.g., "Vegetarian", "Vegan") |
| Diet | str | 6,871 | 10 | Consistent labels |
| Instructions | str | 6,871 | — | Original language |
| TranslatedInstructions | str | 6,871 | — | English |
| URL | str | 6,871 | 6,871 | Source URL (archanaskitchen.com) |

### 3.2 Anuvaad INDB 2024.11 (Sheet1)

| Column Group | Count | Example Columns | Notes |
|--------------|-------|-----------------|-------|
| Identifiers | 3 | food_code, food_name, primarysource | food_code unique (1,014); primarysource = 'asc_manual' etc. |
| Per-100g Nutrients | 38 | energy_kcal, protein_g, fat_g, carb_g, fibre_g, calcium_mg, iron_mg, vita_ug, vitc_mg, ... | All float64; 0 missing for core macros; some micronutrients sparse |
| Per-Serving Nutrients | 41 | unit_serving_energy_kcal, unit_serving_protein_g, ... | 82 missing each (8% of rows); servings_unit column defines unit |

---

## 5. Duplicate & Quality Flags

| Dataset | Issue | Count | Action |
|---------|-------|-------|--------|
| Recipe CSV/XLSX | Duplicate TranslatedRecipeName | 27 | Flag for review; keep both with distinct Srno |
| Recipe CSV/XLSX | Missing Ingredients/TranslatedIngredients | 6 each | Remove from recommender corpus (no usable ingredient text) |
| Recipe CSV/XLSX | Cuisine/Course label pollution | ~5 cuisine values are courses; ~5 course values are diets | Standardize in preprocessing |
| INDB | Per-serving nutrients 82 missing (8%) | 82 rows | Document; do not impute |
| INDB | Duplicate food_code | 0 | Verified unique |
| USDA FDC | food_portion missing portion_description | 10,950/10,951 | Mostly structural; gram_weight present |
| NHANES | Extensive missing in derived columns | Various | Expected for survey data; keep separate |

---

## 6. Target Leakage & Contamination Risks

| Risk | Dataset | Mitigation |
|------|---------|------------|
| Disease→Diet target leakage | diet_recommendations_dataset.csv (not present) | Exclude from supervised training; document why |
| US food composition mapped to Indian recipes | USDA FDC → Recipe ingredients | Never auto-map; require manual/curated ingredient↔food_code linking |
| NHANES demographic bias | NHANES datasets | Keep entirely separate; do not mix with recommendation training data |
| Recipe source URL duplication | Recipe dataset | Verified unique URLs (6,871 unique) |

---

## 7. Next Steps (Phase 1 Deliverables)

1. ✅ Dataset inventory (this document)
2. ⬜ Dataset quality report (detailed per-column analysis)
3. ⬜ Data dictionary (formal schema definitions)
4. ⬜ Data validation scripts (`src/data/validate.py`)
5. ⬜ Reproducible preprocessing pipeline (`src/preprocessing/`)
6. ⬜ Unit tests (`tests/`)
7. ⬜ Dataset suitability decision (formal go/no-go per dataset)

---

*Raw files in `datasets/` are immutable. All processed outputs go to `data/interim/` and `data/processed/`.*