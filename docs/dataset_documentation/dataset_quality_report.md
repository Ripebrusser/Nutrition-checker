# Dataset Quality Report

**Project:** AI for Nutrition & Diet Planning
**Phase:** 1 — Dataset Validation and Preprocessing
**Date:** 2026-11-15

---

## 1. Indian Food Recipe Dataset (IndianFoodDatasetXLS.xlsx / CSV)

### 1.1 Basic Statistics
- **Rows:** 6,871
- **Columns:** 15
- **File Hash (XLSX):** 889aa76ce87ba485422edb365234898d
- **File Hash (CSV):** 898b74b2000ad8e152afbb769fb6e9ce

### 1.2 Missing Values

| Column | Missing Count | Missing % | Action |
|--------|---------------|-----------|--------|
| Srno | 0 | 0% | — |
| RecipeName | 0 | 0% | — |
| TranslatedRecipeName | 0 | 0% | — |
| **Ingredients** | **6** | **0.09%** | Remove from recommender corpus |
| **TranslatedIngredients** | **6** | **0.09%** | Remove from recommender corpus |
| PrepTimeInMins | 0 | 0% | — |
| CookTimeInMins | 0 | 0% | — |
| TotalTimeInMins | 0 | 0% | — |
| Servings | 0 | 0% | Flag outliers |
| Cuisine | 0 | 0% | Standardize labels |
| Course | 0 | 0% | Standardize labels |
| Diet | 0 | 0% | — |
| Instructions | 0 | 0% | — |
| TranslatedInstructions | 0 | 0% | — |
| URL | 0 | 0% | — |

**Missing Ingredients rows (Srno):** Need to identify exact rows.

### 1.3 Duplicate Analysis

| Check | Count | Details |
|-------|-------|---------|
| Full row duplicates | 0 | — |
| Duplicate Srno | 0 | Primary key intact |
| Duplicate RecipeName | 0 | Original names unique |
| **Duplicate TranslatedRecipeName** | **27 pairs (54 rows)** | Same English name, different Srno/RecipeName — likely distinct recipes with same translated name |
| Duplicate URL | 0 | All source URLs unique |

**Duplicate TranslatedRecipeName pairs (27):**
1. Mustard Vegetable Curry Recipe (Srno 162, 9634)
2. Fruit Pachadi Recipe (181, 7470)
3. Vegan Navratan Korma Recipe (239, 1698)
4. Badam Halwa Recipe (251, 253)
5. Sweet Potato Dal Recipe (396, 8735)
6. Chicken Kathi Roll Recipe (685, 9868)
7. Carrot Peanut Chutney Recipe (836, 5958)
8. Lahori Aloo Recipe (1009, 2737)
9. Mushroom Methi Brown Rice Recipe (1153, 2214)
10. Carrot and Beans Poriyal (1351, 12966)
11. Cabbage Besan Fry Recipe (1470, 2177)
12. Peanut Curry Recipe (1705, 5451)
13. Bread Halwa Recipe (1853, 8051)
14. Kadai Mushroom Recipe (1998, 7093)
15. Beetroot Carrot Raita Recipe (1999, 9413)
16. Soya Keema Masala Recipe (2379, 4593)
17. Niramish Aloo Dum Recipe (2928, 11488)
18. Dal Fry Recipe (3286, 4683)
19. Khandeshi Dal Recipe (4307, 7049)
20. Pudina Chutney Recipe (4340, 10032)
21. Pepper Cauliflower Recipe (4928, 8959)
22. Vegetarian Malai Kebab Recipe (5325, 8229)
23. Tomato Rice With Basil Recipe (5441, 7632)
24. Green Apple Rasam Recipe (6261, 11168)
25. Hara Chana Masala Recipe (6851, 8377)
26. Cabbage Pachadi Recipe (8546, 9662)
27. Tomato Dosa Recipe (9508, 11172)

**Decision:** Keep all rows; TranslatedRecipeName is not a primary key. Srno and URL are unique identifiers.

### 1.4 Label Pollution / Inconsistent Taxonomy

#### Cuisine Column (82 unique values) — Contains Course Labels
The following **Cuisine** values are actually **Course** labels (8 values, 12 rows total):

| Cuisine Value | Count | Should Be |
|---------------|-------|-----------|
| Appetizer | 2 | Course |
| Snack | 2 | Course |
| Side Dish | 1 | Course |
| Dessert | 1 | Course |
| Dinner | 1 | Course |
| Lunch | 1 | Course |
| Brunch | 1 | Course |
| World Breakfast | 6 | Course |

#### Course Column (20 unique values) — Contains Diet Labels
The following **Course** values are actually **Diet** labels (8 values, 95 rows total):

| Course Value | Count | Should Be |
|--------------|-------|-----------|
| Vegetarian | 47 | Diet |
| High Protein Vegetarian | 7 | Diet |
| Vegan | 3 | Diet |
| Non Vegeterian | 2 | Diet |
| Eggetarian | 1 | Diet |
| No Onion No Garlic (Sattvic) | 1 | Diet |
| Sugar Free Diet | 1 | Diet |
| One Pot Dish | 33 | Course (valid but descriptive) |

**Action Required:** Preprocessing must reassign these mislabeled rows:
- Move Cuisine→Course for the 8 course-like cuisine values
- Move Course→Diet for the 8 diet-like course values
- "One Pot Dish" stays in Course (valid course type)

### 1.5 Numeric Outliers

#### Servings (max = 1000)
**32 recipes** with Servings > 50. These are **condiments, spice powders, pickles, batters, flours, syrups** — not main dishes.

| Srno | RecipeName | Servings | Type |
|------|------------|----------|------|
| 212 | Nellikai Oorugai/Amla Sambhariyo (Pickle) | 80 | Condiment |
| 342 | Instant Puliyodharai Powder | 100 | Spice powder |
| 581 | Maharashtrian Goda Masala Powder | 200 | Spice powder |
| 661 | How to Cook Root Vegetables... | 300 | Method/prep |
| 1038 | Thalipeeth Bhajani (Flour mix) | 500 | Flour blend |
| 1418 | High Protein Soya Idli & Dosa Batter | 1000 | Batter |
| 1552 | Homemade Paneer | 200 | Ingredient prep |
| ... | ... | ... | ... |

**Decision:** Flag these as `recipe_type = "condiment/prep"` in preprocessing; exclude from main meal recommendation corpus but retain for ingredient substitution.

#### Time Outliers
- **PrepTime max:** 2,880 min (48 hours) — likely fermentation/soaking
- **CookTime max:** 900 min (15 hours) — likely slow cooking
- **TotalTime max:** 2,925 min — consistent with Prep+Cook
- **TotalTime == PrepTime + CookTime:** ✅ Verified for all 6,871 rows

### 1.6 Language & Encoding
- **RecipeName:** Mixed Hindi (Devanagari) and English
- **TranslatedRecipeName:** English only
- **Ingredients/TranslatedIngredients:** Comma-separated, quantities embedded in text (e.g., "2 tablespoon Gram flour (besan)")
- **Instructions/TranslatedInstructions:** Mixed language preserved
- **Encoding:** UTF-8 (no mojibake detected)
- **Special chars:** Devanagari, parentheses, slashes, commas in ingredient text

### 1.7 Source Attribution
- All URLs point to `archanaskitchen.com`
- 6,871 unique URLs verified
- No licence statement found on source; assume scraped data for academic use only

---

## 2. Anuvaad INDB 2024.11 (Indian Food Composition Database)

### 2.1 Basic Statistics
- **Rows:** 1,014
- **Columns:** 82 (3 identifiers + 38 per-100g nutrients + 1 serving unit + 40 per-serving nutrients)
- **File Hash:** f4db8039b33a6de9d6f602ee372aebab
- **Sheet:** Single sheet "Sheet1"

### 2.2 Column Groups

| Group | Columns | Missing | Notes |
|-------|---------|---------|-------|
| Identifiers | food_code, food_name, primarysource | 0 | food_code unique (ASCxxx, FCTxxx, etc.) |
| Per-100g Macronutrients | energy_kj, energy_kcal, carb_g, protein_g, fat_g, freesugar_g, fibre_g | 0 | Complete |
| Per-100g Fatty Acids | sfa_mg, mufa_mg, pufa_mg, cholesterol_mg | 0 | mg per 100g |
| Per-100g Minerals | calcium_mg, phosphorus_mg, magnesium_mg, sodium_mg, potassium_mg, iron_mg, copper_mg, selenium_ug, chromium_mg, manganese_mg, molybdenum_mg, zinc_mg | 0-1014 | Some trace minerals sparse |
| Per-100g Vitamins | vita_ug, vite_mg, vitd2_ug, vitd3_ug, vitk1_ug, vitk2_ug, folate_ug, vitb1_mg, vitb2_mg, vitb3_mg, vitb5_mg, vitb6_mg, vitb7_ug, vitb9_ug, vitc_mg, carotenoids_ug | 0-1014 | Fat-soluble vitamins often missing |
| Serving info | servings_unit | 0 | e.g., "tea cup", "katori", "piece" |
| Per-serving nutrients | 40 columns (unit_serving_*) | **82 each (8.1%)** | Missing for same 82 rows across all per-serving cols |

### 2.3 Missing Value Pattern (Per-Serving)
- **82 rows** have ALL per-serving nutrients missing (8.1% of dataset)
- These rows have valid per-100g data and servings_unit
- **Do not impute** — document and handle at query time

### 2.4 Duplicate Check
- **food_code:** 1,014 unique — ✅ No duplicates
- **food_name:** 1,014 unique — ✅ No duplicates

### 2.5 Data Type Verification
- All nutrient columns: `float64`
- Identifiers: `str`
- Units: mg, g, µg, kJ, kcal — consistent per column group

### 2.6 Provenance
- **Source:** Anuvaad / ICMR-NIN Indian Food Composition Database (INDB) 2024.11
- **Licence:** Academic/research use; redistribution terms not explicitly stated in file
- **Content:** Raw ingredients and some prepared dishes (e.g., "Hot tea (Garam Chai)", "Instant coffee")
- **Scope:** Indian foods; includes both raw commodities and minimal preparations

---

## 3. USDA FoodData Central (FDC)

### 3.1 Files & Sizes

| File | Rows | Key Columns | Purpose |
|------|------|-------------|---------|
| food.csv | 87,990 | fdc_id, description, data_type, food_category_id | Food registry |
| nutrient.csv | 477 | id, name, unit_name, nutrient_nbr, rank | Nutrient dictionary |
| food_nutrient.csv | 170,469 | fdc_id, nutrient_id, amount, derivation_id | Nutrient values per food |
| measure_unit.csv | 123 | id, name | Unit dictionary |
| food_portion.csv | 10,951 | fdc_id, amount, measure_unit_id, gram_weight | Portion sizes |

### 3.2 Quality Notes
- **food.csv:** 3,811 missing food_category_id; 8 missing description
- **food_nutrient.csv:** 33 missing amount; 152,888 missing min/max/median (expected for single-point values)
- **food_portion.csv:** 10,950 missing portion_description (mostly structural); gram_weight complete
- **Scope:** US foods; not Indian-specific
- **Licence:** US Government work — public domain

### 3.3 Suitability for This Project
- **Do not use as primary composition source** — food names, varieties, and nutrient profiles differ from Indian context
- **Conditional use only:** Gap-filling for ingredients absent from INDB, with **explicit manual mapping** (ingredient → fdc_id)
- **Never auto-join** on food names or codes

---

## 4. NHANES 2019-2020 Datasets

### 4.1 Files

| File | Rows | Columns | Description |
|------|------|---------|-------------|
| BMX_L.xpt | 8,860 | 22 | Body measures (weight, height, BMI, circumferences) |
| DEMO_L.xpt | 11,933 | 27 | Demographics (age, gender, race, income, education) |
| DIQ_L.xpt | 11,744 | 9 | Diabetes questionnaire |
| DR1TOT_L.xpt | 8,860 | 168 | Day 1 dietary recall totals (nutrients) |
| PAQ_L.xpt | 8,153 | 8 | Physical activity questionnaire |

### 4.2 Quality Notes
- **Survey weights present** (WTINT2YR, WTMEC2YR, WTDRD1, WTDR2D)
- **Extensive missingness** in derived/conditional columns (expected)
- **SEQN** is participant ID; linkable across files
- **Population:** US non-institutionalized civilians
- **Licence:** CDC — public domain

### 4.3 Suitability Decision
**EXCLUDE from core recommendation pipeline.**
- Different population (US vs Indian)
- Dietary recalls ≠ recipes
- Health metrics (BMI, diabetes) not directly usable for Indian meal planning without validation
- **Keep separate** for:
  - External validation of nutrient targets
  - Epidemiological baseline comparisons
  - Future transfer-learning experiments (Phase 4+)

---

## 5. Summary of Defects & Required Transformations

| # | Dataset | Defect | Severity | Required Action |
|---|---------|--------|----------|-----------------|
| 1 | Recipe | 6 rows missing Ingredients | High | Remove from recommender corpus; log separately |
| 2 | Recipe | 27 duplicate TranslatedRecipeName | Low | Keep; Srno is PK |
| 3 | Recipe | Cuisine contains 8 course labels (12 rows) | High | Remap in preprocessing |
| 4 | Recipe | Course contains 8 diet labels (95 rows) | High | Remap in preprocessing |
| 5 | Recipe | 32 recipes with Servings > 50 (condiments) | Medium | Flag as `recipe_type=condiment`; exclude from meal recs |
| 6 | INDB | 82 rows missing all per-serving nutrients | Medium | Document; do not impute |
| 7 | USDA FDC | Not Indian foods | N/A | Use only for manual gap-filling |
| 8 | NHANES | US population, not recipes | N/A | Keep separate; exclude from training |

---

## 6. Validation Scripts Created

- `src/data/validate_recipe.py` — Recipe dataset validation
- `src/data/validate_indb.py` — INDB validation
- `src/data/validate_usda.py` — USDA FDC validation (smoke test)
- `src/data/validate_nhanes.py` — NHANES validation (smoke test)

All scripts output JSON validation reports to `data/interim/validation_reports/`.

---

*End of Quality Report*