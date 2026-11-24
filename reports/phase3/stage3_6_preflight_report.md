# Stage 3.6: Preflight Report

**Date:** 2026-11-19  
**Status:** Preflight Complete - Ready for Implementation

---

## 1. Input Dataset Verification

### 1.1 IFCT Final Candidate Dataset
- **Path:** `data/interim/ifct_final_candidate/ifct_table1_candidate.parquet`
- **Records:** 528 food items
- **Columns:** 18 (food_code, food_name, regions, food_group, source_page, source_table, extraction_method, verification_status, manual_recovery, moisture_g, protein_g, ash_g, fat_g, fibre_total_g, fibre_insoluble_g, fibre_soluble_g, carb_available_g, energy_kj)
- **Nutrient columns:** All stored as strings (some with ± notation)
- **Missing values:** fibre_total_g, fibre_insoluble_g, fibre_soluble_g, carb_available_g have 222 missing (42%)
- **SHA-256:** `294c6fc4d095a47e13fbe02e8e3c1c0c8175752966275a3415f9a7df04774f35` ✅ Verified

### 1.2 IFCT Match Candidates (Stage 2.3 Output)
- **Path:** `data/interim/phase3/stage2_3/ifct_match_candidates.parquet`
- **Records:** 119,474 candidate mappings
- **Primary key:** (recipe_id, original_ingredient, ifct_food_code) - implicit
- **Match methods:** TOKEN_SIMILARITY (100,658), EXACT (7,583), TOKEN_EQUIVALENT (6,198), SYNONYM (5,035)
- **Preparation states:** NOT_SPECIFIED (80,502), POWDERED (18,670), DRIED (12,091), FRESH (4,716), etc.
- **Requires review:** 119,470 True, 4 False
- **Auto-accepted:** 4 records (EXACT + FRESH + similarity=1.0)
- **SHA-256:** `2bb9f0d7770f7669ad3cd30f49d2a15f820f572e53690678f58891229336740f` ✅ Verified

### 1.3 Unmatched Ingredients
- **Path:** `data/interim/phase3/stage2_3/unmatched_ingredients.parquet`
- **Records:** 63,244 unmatched ingredients
- **Conversion status:** All UNRESOLVED (63,244)
- **Gram weight:** All NaN (no gram weights)

### 1.3 Disambiguated Ingredients
- **Path:** `data/interim/phase3/stage2_3/disambiguated_ingredients.parquet`
- **Records:** 90,862
- **Preparation states:** NOT_SPECIFIED (80,502), POWDERED (18,670), DRIED (12,091), etc.

### 1.4 Phase 2 Parsed Ingredients
- **Path:** `data/interim/phase2/parsed_recipe_ingredients.parquet`
- **Records:** 90,862 canonical ingredient lines
- **Gram weights:** Only 1,299 resolved (1.4%)
- **Parse status:** PARSED_EXACT (54,903), PARSED_APPROXIMATE (29,980), UNQUANTIFIED (4,306), RANGE_PARSED (1,673)
- **Conversion status:** 89,525 UNRESOLVED, 1,337 RESOLVED_HOUSEHOLD

### 1.5 IFCT Final Candidate Data
- **Path:** `data/interim/ifct_final_candidate/ifct_table1_candidate.parquet`
- **Records:** 528 food items
- **Nutrient columns (string format):** moisture_g, protein_g, ash_g, fat_g, fibre_total_g, fibre_insoluble_g, fibre_soluble_g, carb_available_g, energy_kj
- **Missing nutrients:** fibre_total_g, fibre_insoluble_g, fibre_soluble_g, carb_available_g - 222 missing each (42%)

### 1.5 Household Measurements
- **Phase 2:** `data/interim/phase2/household_measurements.csv` - 68 records, verified
- **Stage 2.3:** `data/interim/phase3/stage2_3/household_measurements.csv` - verified
- SHA-256 verified for both

### 1.6 Recipe Dataset
- **Processed recipes:** `data/processed/recipes.parquet` - 6,865 recipes
- **Columns:** 19 including cuisine (75 types), course (10 types), diet_labels (20 types)

---

## 2. Existing Nutrition Module Assessment

### Existing Implementation (src/nutrition/)
| Module | Status | Notes |
|--------|--------|-------|
| `nutrient_calculator.py` | Partial | Has dataclasses and NutrientCalculator class but incomplete implementation |
| `edible_portion.py` | Good | EdiblePortionCalculator with hardcoded database, ~180 entries |
| `nutrient_validation.py` | Good | Validation ranges, energy consistency checks, Atwater factors |
| `__init__.py` | Minimal | Just package marker |

### Key Gaps Identified:
1. **No ingredient mapping interface** - No strict interface for approved mappings only
2. **Incomplete nutrient_calculator** - Missing `_calculate_nutrients`, `_get_ifct_record`, `_empty_nutrition` implementations
3. **No ingredient mapping interface** - No strict interface for approved mappings only
4. **No recipe aggregation** - No recipe-level aggregation logic
5. **No validation pipeline** - No end-to-end validation pipeline
6. **No controlled demonstration** - No controlled demo with real/synthetic data

---

## 3. Input Data Summary

| Dataset | Records | Key Fields | Status |
|---------|---------|------------|--------|
| IFCT Table 1 | 528 | 9 nutrients (str) | Verified ✅ |
| IFCT Match Candidates | 119,474 | 23 fields | Verified ✅ |
| Unmatched Ingredients | 63,244 | 22 fields | Verified ✅ |
| Parsed Ingredients | 90,862 | 22 fields | Verified ✅ |
| Disambiguated Ingredients | 90,862 | 12 fields | Verified ✅ |
| Household Measurements | 68 | 6 fields | Verified ✅ |
| Recipes | 6,865 | 19 fields | Verified ✅ |
| Gram weights resolved | 1,299/90,862 | 1.4% | Verified ✅ |
| Household resolved | 1,337 | - | Verified ✅ |

---

## 4. Frozen Data Hashes (All Verified ✅)

| File | SHA-256 |
|------|---------|
| normalized_ingredients.parquet | `08710983213938c3fecafd20991ab7d3d7fe51b179303bbe4dc93b2ac1b1b6e5` |
| parsed_recipe_ingredients.parquet | `e17b668b208dac4a7240cbfb27d78caac6123bc2b29b34a70aeb38964b9e86d9` |
| ingredient_synonyms.csv | `22b8aace1ef29ea271051004a0e5a79ac8a8bfb5d80b8f796abe0db1f2ee4b31` |
| household_measurements.csv | `451fb9c6d5135e0684bd5e6445aeaadfafa2951db6ae7fd939b96faad1e16b47` |
| ifct_table1_candidate.parquet | `294c6fc4d095a47e13fbe02e8e3c1c0c8175752966275a3415f9a7df04774f35` |
| ifct_match_candidates.parquet | `2bb9f0d7770f7669ad3cd30f49d2a15f820f572e53690678f58891229336740f` |
| unmatched_ingredients.parquet | `4d4e2b84e3b3323552c600bf90eefba81c5e44ee8f455298f331c190ced08102` |
| household_measurements.csv (S2.3) | `4c169cba077c49f384e699129e9051929ad130dda2221ac2692cf9c34e04567e` |

---

## 5. Implementation Plan Summary

### Stage 1: Nutrition Engine Architecture
- Create modular nutrition engine with clear data contracts
- Define Pydantic models for all data contracts
- Implement ingredient mapping interface (approved mappings only)

### Stage 2: Verified Ingredient Mapping Interface
- Strict interface for approved mappings only
- Reject unapproved mappings automatically
- Preserve mapping evidence and provenance

### Stage 3: Edible Weight Handling
- Resolved gram weights only
- Household conversions with documented evidence
- Unresolved quantities remain unresolved (not zero)

### Stage 4: Nutrient Calculation
- Formula: `nutrient = IFCT_value_per_100g × edible_weight_g / 100`
- kJ to kcal conversion: 1 kcal = 4.184 kJ
- Missing values remain NaN (never zero)

### Stage 5: Recipe Aggregation
- Sum ingredient contributions
- Track completeness per nutrient
- Report COMPLETE/PARTIAL/INSUFFICIENT/NO_MAPPED

### Stage 6: Validation & QA
- Unit tests for all calculation paths
- Data integrity tests
- Missing value handling tests

### Stage 7: Controlled Demonstration
- Synthetic examples for calculation correctness
- Real-data demo with genuinely approved mappings

---

## 6. Key Constraints & Rules

| Rule | Enforcement |
|------|-------------|
| Never treat candidate mappings as verified | Strict interface |
| Never treat missing nutrients as zero | Keep NaN |
| Never convert unresolved quantities to zero | Keep NaN |
| Never invent edible portion factors | Hardcoded DB only |
| Never double-apply edible portion reduction | Track state |
| Never claim full nutrition from partial data | Track completeness |
| Never fabricate nutrition values | Strict validation |

---

## 7. Ready for Implementation

**Status:** ✅ Preflight Complete  
**Next Step:** Begin Stage 1 - Nutrition Engine Architecture Implementation

---

*End of Preflight Report*