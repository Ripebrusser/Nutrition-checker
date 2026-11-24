# Phase 2 Preflight Report

**Project:** AI for Nutrition & Diet Planning: Personalized Indian Meal Recommendations Using Health Metrics and Ingredient-Level Nutrition Analysis  
**Stage:** 0 — Repository and Data Preflight  
**Date:** 2026-11-15  
**Status:** ✅ COMPLETE — Ready for Stage 1 Implementation  

---

## 1. Repository Structure

```
ML_proj/
├── data/
│   ├── interim/
│   │   ├── ifct_final_candidate/          # Phase 1 accepted IFCT (528 records)
│   │   ├── ifct_verified/                 # Forensic recovery evidence
│   │   ├── ifct_extracted/                # Raw extraction outputs
│   │   ├── validation_reports/            # Phase 1 validation JSON
│   │   ├── recipes_missing_ingredients.csv
│   │   ├── recipes_condiments.csv
│   │   ├── indb_preprocessing_log.json
│   │   └── preprocessing_log.json
│   ├── processed/
│   │   ├── recipes.parquet                # 6,865 recipes (FROZEN)
│   │   ├── recipes.csv                    # 6,865 recipes (FROZEN)
│   │   ├── indb_foods.parquet             # 1,014 prepared dishes (FROZEN)
│   │   └── indb_foods.csv                 # 1,014 prepared dishes (FROZEN)
│   └── raw/nutrition/IFCT_2017/
│       ├── IFCT2017.pdf                   # Official PDF
│       ├── IFCT2017_decrypted.pdf         # Decrypted PDF (verified)
│       └── download_metadata.json
├── datasets/
│   ├── IndianFoodDatasetXLS.xlsx          # Raw recipes source
│   ├── IndianFoodDatasetCSV.csv           # Raw recipes CSV
│   ├── Anuvaad_INDB_2024.11.xlsx          # Raw INDB source
│   └── USDA/NHANES reference datasets
├── docs/dataset_documentation/
│   ├── ifct_independent_acceptance_review.md   # Phase 1 final acceptance
│   ├── ifct_final_acceptance_audit.md
│   ├── ifct_final_remediation_audit.md
│   ├── final_evidence_reconciliation.md
│   ├── data_dictionary.md
│   └── ... (15+ audit reports)
├── src/
│   ├── preprocessing/
│   │   ├── preprocess_recipes.py          # Recipe preprocessing (FROZEN)
│   │   ├── preprocess_indb.py             # INDB preprocessing (FROZEN)
│   │   └── run_all.py
│   └── data/
│       ├── ifct_table1_final_v15.py       # Best IFCT extractor (reference)
│       ├── ifct_recovery.py               # Remediation script
│       └── ... (28 extractor versions)
├── tests/
│   ├── test_phase1.py                     # 44 passing tests
│   └── test_ifct_extraction.py
├── reports/                               # NEW - for Phase 2 outputs
├── models/                                # NEW - for trained models
├── Notebooks/                             # Legacy notebooks
├── outputs/                               # Legacy outputs
├── Previous works/                        # Legacy notebooks
├── Literature Review/                     # Literature references
└── web application/                       # Legacy web app
```

---

## 2. Input File Paths and Verification

| Dataset | Path | Format | Size | Status |
|---------|------|--------|------|--------|
| **Recipes (processed)** | `data/processed/recipes.parquet` | Parquet | 10.8 MB | ✅ Verified |
| **Recipes (CSV)** | `data/processed/recipes.csv` | CSV | 24.7 MB | ✅ Verified |
| **IFCT Candidate** | `data/interim/ifct_final_candidate/ifct_table1_candidate.parquet` | Parquet | 49 KB | ✅ Verified |
| **IFCT Candidate** | `data/interim/ifct_final_candidate/ifct_table1_candidate.csv` | CSV | 73 KB | ✅ Verified |
| **INDB Processed** | `data/processed/indb_foods.parquet` | Parquet | 590 KB | ✅ Verified |
| **INDB Processed** | `data/processed/indb_foods.csv` | CSV | 1.5 MB | ✅ Verified |
| **IFCT Official PDF** | `data/raw/nutrition/IFCT_2017/IFCT2017.pdf` | PDF | 12.4 MB | ✅ Verified |
| **IFCT Decrypted PDF** | `data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf` | PDF | 14.0 MB | ✅ Verified |
| **Raw Recipes XLSX** | `datasets/IndianFoodDatasetXLS.xlsx` | XLSX | 5.5 MB | ✅ Verified |
| **Raw Recipes CSV** | `datasets/IndianFoodDatasetCSV.csv` | CSV | (in datasets/) | ✅ Verified |
| **Raw INDB XLSX** | `datasets/Anuvaad_INDB_2024.11.xlsx` | XLSX | 1.1 MB | ✅ Verified |

**All Phase 1 accepted files present and verified.**

---

## 3. Dataset Schemas

### 3.1 Recipes (6,865 records — FROZEN)

**File:** `data/processed/recipes.parquet`  
**Shape:** (6865, 19)  
**Primary Key:** `recipe_id` (int64, unique, 1–6865)

| Column | Type | Nulls | Description |
|--------|------|-------|-------------|
| recipe_id | int64 | 0 | Unique identifier (original Srno) |
| recipe_name_original | str | 0 | Original recipe name |
| recipe_name_en | str | 0 | English translation |
| ingredients_raw | str | 0 | Original ingredient text with quantities |
| ingredients_en | str | 0 | Translated/standardized ingredients |
| prep_time_min | int64 | 0 | Preparation time (minutes) |
| cook_time_min | int64 | 0 | Cooking time (minutes) |
| total_time_min | int64 | 0 | Total time (minutes) |
| servings | int64 | 0 | Number of servings (≥1) |
| recipe_type | str | 0 | Indian / International / Ambiguous |
| cuisine | str | 0 | Cuisine category (cleaned) |
| course | str | 0 | Course category (cleaned) |
| diet_labels | str | 0 | Dietary labels (cleaned) |
| instructions_raw | str | 0 | Original instructions |
| instructions_en | str | 0 | Translated instructions |
| source_url | str | 0 | Source URL (unique) |
| source_domain | str | 0 | Source domain |
| created_at | str | 0 | Creation timestamp |
| updated_at | str | 0 | Update timestamp |

**Key observations:**
- `ingredients_raw`: Contains mixed English/Hindi/regional names with quantities, units, preparation notes
- `ingredients_en`: Translated version but still unparsed (quantities, units embedded in text)
- 6 records excluded during Phase 1 (missing ingredients)
- 35 condiment records flagged but retained
- No structured quantity/unit parsing exists yet

**Sample `ingredients_raw`:**
```
"6 Karela (Bitter Gourd/ Pavakkai) - deseeded,Salt - to taste,1 Onion - thinly sliced,3 tablespoon Groundnut Oil,..."
"2-1/2 कप चावल - पका ले,3 टमाटर,3 छोटा चमच्च बीसी बेले भात पाउडर,नमक - स्वाद अनुसार..."
"1-1/2 cups Rice Vermicelli Noodles (Thin),1 Onion - sliced,1/2 cup Carrots (Gajjar) - chopped,..."
```

### 3.2 IFCT Table 1 Candidate (528 records — FROZEN)

**File:** `data/interim/ifct_final_candidate/ifct_table1_candidate.parquet`  
**Shape:** (528, 18)  
**Primary Key:** `food_code` (str, unique, 528 codes)

| Column | Type | Nulls | Description |
|--------|------|-------|-------------|
| food_code | str | 0 | Unique code (A001–S010, no T-prefix) |
| food_name | str | 0 | Food name with scientific name |
| regions | int64 | 0 | Number of regions sampled |
| food_group | str | 0 | Standardized food group (18 groups) |
| source_page | int64 | 0 | PDF page number (39–68) |
| source_table | int64 | 0 | Always 1 (Table 1) |
| extraction_method | str | 0 | auto / auto_fixed / manual |
| verification_status | str | 0 | auto / verified_pdf |
| manual_recovery | bool | 0 | True for 4 genuine manual recoveries |
| moisture_g | str | 0 | Moisture per 100g (± notation preserved) |
| protein_g | str | 0 | Protein per 100g (± notation preserved) |
| ash_g | str | 0 | Ash per 100g (± notation preserved) |
| fat_g | str | 0 | Fat per 100g (± notation preserved) |
| fibre_total_g | str | 222 | Total dietary fibre per 100g |
| fibre_insoluble_g | str | 222 | Insoluble fibre per 100g |
| fibre_soluble_g | str | 222 | Soluble fibre per 100g |
| carb_available_g | str | 222 | Available carbohydrate per 100g |
| energy_kj | str | 0 | Energy per 100g in kJ (± notation preserved) |

**Nutrient coverage:**
- Core nutrients (moisture, protein, fat, ash, energy): 528/528 (100%)
- Fibre (total, insoluble, soluble) & carb_available: 306/528 (58%) — missing for animal products

**Food group distribution (18 groups):**
| Group | Count |
|-------|-------|
| MARINE FISH | 92 |
| OTHER VEGETABLES | 78 |
| FRUITS | 68 |
| ANIMAL MEAT | 63 |
| LEAFY VEGETABLES | 34 |
| PULSES AND LEGUMES | 25 |
| CEREALS AND MILLETS | 24 |
| CONDIMENTS AND SPICES-DRY | 23 |
| NUTS AND OILSEEDS | 21 |
| ROOTS AND TUBERS | 19 |
| POULTRY | 19 |
| EGG AND EGG PRODUCTS | 15 |
| MARINE SHELLFISH | 15 |
| CONDIMENTS AND SPICES-FRESH | 10 |
| FRESHWATER FISH AND SHELLFISH | 10 |
| SUGARS AND JAGGERY | 4 |
| MUSHROOMS | 4 |
| MILK AND MILK PRODUCTS | 4 |

**Critical validation notes:**
- All 528 codes verified against official PDF pages 39–68
- G013 corrected to CONDIMENTS AND SPICES-FRESH (was DRY)
- 4 genuine manual recoveries: D001, E004, G013, H005
- 14 fabricated T001–T014 removed
- ± uncertainty notation preserved in nutrient strings
- CSV/Parquet parity verified (0 mismatches)

### 3.3 INDB 2024.11 (1,014 records — FROZEN)

**File:** `data/processed/indb_foods.parquet`  
**Shape:** (1014, 86)  
**Primary Key:** `food_code` (str, unique)

**Column categories:**
- **Identifiers:** food_code, food_name, primary_source
- **Serving info:** serving_unit (97 nulls), missing_serving_data (bool)
- **Per-100g nutrients (40):** energy_kcal_100g, energy_kj_100g, carbohydrate_g_100g, protein_g_100g, fat_g_100g, fibre_g_100g, free_sugar_g_100g, cholesterol_mg_100g, fatty acids (SFA/MUFA/PUFA), cholesterol, minerals (Ca, P, Mg, Na, K, Fe, Cu, Se, Cr, Mn, Mo, Zn), vitamins (A, B1, B2, B3, B5, B6, B7, B9, C, D2, D3, E, K1, K2), carotenoids, folate
- **Per-serving nutrients (41):** Same nutrients with `serving_` prefix (82 nulls each)

**Critical classification:**
- **Prepared dishes and beverages only** — NOT raw ingredients
- Examples: "Hot tea (Garam Chai)", "Instant coffee", "Espresso coffee"
- Cannot be used as raw ingredient substitutes for IFCT matching
- Use only as prepared-dish reference/comparison dataset

---

## 4. Existing Code Assets

### 4.1 Reusable Preprocessing Code (FROZEN — Do Not Modify)

| File | Purpose | Status |
|------|---------|--------|
| `src/preprocessing/preprocess_recipes.py` | Recipe cleaning, cuisine/course/diet remapping, exclusion logic | FROZEN — reference only |
| `src/preprocessing/preprocess_indb.py` | INDB nutrient column mapping, per-100g/per-serving separation | FROZEN — reference only |
| `src/preprocessing/run_all.py` | Orchestration script | FROZEN |

**Key reusable components:**
- Cuisine/course/diet remapping dictionaries (VALID_CUISINES, CUISINE_REMAP, COURSE_REMAP)
- Nutrient column mapping dictionaries (NUTRIENT_MAP_100G, NUTRIENT_MAP_SERVING)
- Logging and validation patterns

### 4.2 IFCT Extractor Code (Reference Only)

**Best extractor:** `src/data/ifct_table1_final_v15.py` — Two-pass strategy achieving 512/528
**Remediation script:** `src/data/ifct_recovery.py` — Used for final candidate creation

**Not reusable for Phase 2:** All extractors are PDF-to-table extraction code, not ingredient matching.

### 4.3 Test Infrastructure

| File | Purpose |
|------|---------|
| `tests/test_phase1.py` | 44 comprehensive tests for Phase 1 (all passing) |
| `tests/test_ifct_extraction.py` | IFCT extraction validation tests |

**Test patterns to follow for Phase 2:**
- Class-scoped fixtures for data loading
- Data integrity tests (PK uniqueness, null checks, value ranges)
- Schema validation tests
- Preprocessing log validation tests

---

## 5. Dependencies and Environment

**No `requirements.txt` found** — dependencies must be inferred from imports.

**Observed imports in codebase:**
```python
# Standard library
json, logging, sys, pathlib, datetime, typing, re, subprocess, hashlib

# Data science
pandas, numpy

# PDF processing
fitz (PyMuPDF)

# Testing
pytest
```

**Recommended action:** Create `requirements.txt` for Phase 2:
```
pandas>=2.0
numpy>=1.24
pymupdf>=1.23
pytest>=7.0
rapidfuzz>=3.0  # for fuzzy matching
scikit-learn>=1.3  # for TF-IDF/similarity (if needed)
```

---

## 6. Data Limitations and Critical Constraints

### 6.1 Recipe Ingredients (Critical Gap)
- **Unparsed:** Quantities, units, ingredient names all in free text
- **Mixed languages:** English, Hindi (Devanagari), transliterated Hindi
- **Regional synonyms:** "Toor dal" = "Arhar dal" = "Pigeon pea"
- **Preparation states:** "fresh coconut" ≠ "dried coconut"; "whole wheat" ≠ "refined wheat"
- **Ambiguous quantities:** "salt to taste", "handful", "pinch", "as required"

### 6.2 IFCT Nutrient Data
- **Units:** All per 100g edible portion
- **Format:** Strings with ± uncertainty (e.g., "76.51±0.20")
- **Missing:** Fibre/carb data for ~42% of items (mainly animal products)
- **No cooking retention factors** available

### 6.3 INDB Usage Restriction
- **Prepared dishes only** — cannot substitute for raw ingredient nutrition
- **Per-serving data incomplete:** 82/1014 missing serving data
- **Use case:** Prepared-dish reference comparison only

### 6.4 Phase 1 Assets — FROZEN
| Asset | Path | Must Not Modify |
|-------|------|-----------------|
| Recipes processed | `data/processed/recipes.parquet/.csv` | ✅ |
| IFCT candidate | `data/interim/ifct_final_candidate/` | ✅ |
| INDB processed | `data/processed/indb_foods.parquet/.csv` | ✅ |
| Original PDFs | `data/raw/nutrition/IFCT_2017/` | ✅ |
| Phase 1 reports | `docs/dataset_documentation/` | ✅ |

---

## 7. Proposed Implementation Architecture

### 7.1 Directory Structure for Phase 2 Outputs

```
data/
├── interim/phase2/
│   ├── normalized_ingredients.parquet
│   ├── parsed_recipe_ingredients.parquet
│   ├── ingredient_ifct_mapping.parquet
│   ├── ingredient_match_review.csv
│   ├── ingredient_nutrition.parquet
│   ├── recipe_nutrition_estimates.parquet
│   ├── recipe_coverage.parquet
│   ├── indb_comparison.parquet
│   ├── ingredient_synonyms.csv
│   └── household_measurements.csv
├── processed/phase2/
│   └── (final validated outputs)

src/
├── ingredients/
│   ├── __init__.py
│   ├── normalizer.py
│   ├── parser.py
│   ├── synonyms.py
│   └── matcher.py
├── nutrition/
│   ├── __init__.py
│   ├── calculator.py
│   ├── schema.py
│   ├── coverage.py
│   └── indb_reference.py

tests/phase2/
├── test_normalization.py
├── test_parsing.py
├── test_matching.py
├── test_nutrition.py
├── test_coverage.py
└── test_integration.py

reports/phase2/
├── phase2_preflight_report.md          # THIS FILE
├── normalization_validation_report.md
├── quantity_parsing_report.md
├── matching_evaluation_report.md
├── nutrition_calculation_report.md
├── recipe_coverage_report.md
├── indb_comparison_report.md
├── phase2_test_report.md
├── ingredient_matching_gold_standard.csv
├── ingredient_matching_metrics.json
└── phase2_completion_report.md
```

### 7.2 Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| `ingredients.normalizer` | Text cleaning, Unicode norm, regional synonym expansion, prep-state detection |
| `ingredients.parser` | Quantity/unit/ingredient extraction, approximation detection |
| `ingredients.synonyms` | Regional synonym dictionary management, confidence scoring |
| `ingredients.matcher` | Multi-level IFCT matching (exact → synonym → token → fuzzy → semantic) |
| `nutrition.schema` | Nutrient definitions, units, missing-value policies |
| `nutrition.calculator` | Per-100g calculations, recipe aggregation, serving division |
| `nutrition.coverage` | Line/weight coverage, recipe confidence scoring |
| `nutrition.indb_reference` | Prepared-dish comparison workflow |

### 7.3 Data Flow

```
Raw Recipe (ingredients_raw)
    ↓
Ingredient Normalizer (ingredients_en + synonym expansion)
    ↓
Quantity/Unit Parser (extract qty, unit, ingredient, prep-state)
    ↓
Unit Converter (household measures → grams where supported)
    ↓
IFCT Matcher (multi-level, confidence-scored)
    ↓
Nutrition Calculator (per-100g × weight/100)
    ↓
Recipe Aggregator (sum ingredients → recipe totals)
    ↓
Per-Serving Calculator (when servings known)
    ↓
Coverage/Confidence Scorer
    ↓
Output: recipe_nutrition_estimates.parquet + coverage.parquet
```

---

## 8. Validation Gates (Per Phase 2 Specification)

| Stage | Gate | Validation Required |
|-------|------|---------------------|
| 0 | Preflight | ✅ Schema verified, architecture approved |
| 1 | Normalization | Validate normalized examples, synonym coverage |
| 2 | Quantity Parsing | Validate parsed quantities, conversion rules |
| 3 | IFCT Matching | Validate against gold-standard sample |
| 4 | Nutrition Calc | Manual verification of calculations |
| 5 | Coverage/Uncertainty | Validate metrics, confidence scoring |
| 6 | INDB Reference | Validate comparison eligibility logic |
| 7 | Testing | All Phase 2 tests pass |
| 8 | Experimental Eval | Report actual precision/recall/F1 |
| 9 | Reproducibility | Deterministic runs verified |
| 10 | Documentation | Phase 2 completion report complete |

---

## 9. Identified Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Regional synonym coverage incomplete | Missed matches | Build iterative synonym dictionary; flag unmatched for review |
| Volume-to-mass conversion unsupported | Unquantified nutrition | Explicit "unsupported conversion" flag; never invent factors |
| Cooking retention factors unavailable | Raw vs cooked discrepancy | Document limitation; report raw-ingredient estimates only |
| No gold-standard evaluation set | Cannot measure matching quality | Create manual review sample (Stage 8) |
| INDB prepared dishes confused with ingredients | Wrong nutrition | Strict separation; INDB only as prepared-dish reference |
| Ambiguous quantities ("to taste") | Missing nutrition | Flag as unquantified; report coverage impact |

---

## 10. Approval to Proceed

**Preflight Status:** ✅ **COMPLETE**

All Phase 1 accepted assets verified:
- ✅ 6,865 recipes schema documented
- ✅ 528 IFCT records schema documented (with G013 correction verified)
- ✅ 1,014 INDB prepared dishes schema documented (classified correctly)
- ✅ All Phase 1 files present and frozen
- ✅ Existing preprocessing code catalogued for reference
- ✅ Test infrastructure documented
- ✅ Dependencies identified
- ✅ Proposed architecture documented
- ✅ Validation gates defined

**No blocking issues identified.**

---

## 11. Next Steps

**Stage 1 — Ingredient Normalization** can begin immediately.

**Deliverables for Stage 1:**
1. `src/ingredients/normalizer.py` — Text cleaning, Unicode norm, regional synonyms
2. `src/ingredients/synonyms.py` — Synonym dictionary with confidence
3. `data/interim/phase2/normalized_ingredients.parquet` — Original + normalized + metadata
4. `data/interim/phase2/ingredient_synonyms.csv` — Synonym dictionary
5. `reports/phase2/normalization_validation_report.md` — Validation evidence

**Gate 1 criteria:** Normalized examples reviewed, synonym coverage documented, meaningful distinctions preserved (fresh vs dried, whole vs split, etc.), original text preserved.

---

**Report generated:** 2026-11-15  
**Next action:** Begin Stage 1 implementation