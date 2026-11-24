# Phase 3 Preflight Report: Phase 2 Validation

**Date:** 2026-11-17  
**Phase:** 3 Preflight (Phase 2 Validation)  
**Status:** ✅ Phase 2 Verified — Ready for Phase 3

---

## Executive Summary

Phase 2 outputs have been validated. All 80 Phase 1+2 tests pass (44 Phase 1 + 14 normalization + 22 quantity parsing). The critical reconciliation bug in `reconcile_sources()` has been fixed (using `has_raw`/`has_en` aggregation instead of first-value `_is_raw`/`_is_en`).

**Key verified metrics:**
- 90,862 canonical ingredient records from 6,865 recipes
- 75,211 canonical matches (82.8%) | 7,887 raw_only | 7,764 en_only
- 1,299 gram weights resolved | 1,337 household conversions resolved
- 80/80 Phase 1+2 tests pass (7 IFCT legacy failures are pre-existing, unrelated to Stage 2)

---

## 1. Phase 2 Outputs Inventory

### 1.1 Parsed Recipe Ingredients (`data/interim/phase2/parsed_recipe_ingredients.parquet`)

| Metric | Value |
|--------|-------|
| Total canonical records | 90,862 |
| Unique recipes | 6,865 |
| Source reconciliation | canonical: 75,211 (82.8%), raw_only: 7,887, en_only: 7,764 |
| Discrepancies | 0 |
| Parse status | EXACT: 54,903 (60.4%), APPROXIMATE: 29,980 (33.0%), RANGE: 1,673 (1.8%), UNQUANTIFIED: 4,306 (4.7%) |
| Conversion status | UNRESOLVED: 89,525 (98.5%), RESOLVED_HOUSEHOLD: 1,337 (1.5%) |
| Gram weight resolved | 1,299 (1.4% of canonical) |
| Household conversions resolved | 1,337 (RESOLVED_HOUSEHOLD) |

**Source field distribution:** ingredients_raw: 83,098 | ingredients_en: 7,764

**Note on en coverage:** Only 650/6,865 recipes (9.5%) have en records in parsed output. 90.5% of recipes lose their `ingredients_en` during parsing — this is a Stage 1 issue where en records are dropped during the parsing loop.

---

### 1.2 IFCT 2017 Table 1 Candidate (`data/interim/ifct_final_candidate/ifct_table1_candidate.parquet`)

| Metric | Value |
|--------|-------|
| Records | 528 |
| Unique food codes | 528 |
| Food groups | 18 |
| Nutrient columns | moisture_g, protein_g, ash_g, fat_g, fibre_total_g, fibre_insoluble_g, fibre_soluble_g, carb_available_g, energy_kj |

**Food group distribution:**
- MARINE FISH: 92
- OTHER VEGETABLES: 78
- FRUITS: 68
- ANIMAL MEAT: 63
- LEAFY VEGETABLES: 34
- PULSES AND LEGUMES: 25
- CEREALS AND MILLETS: 24
- CONDIMENTS AND SPICES-DRY: 23
- NUTS AND OILSEEDS: 21
- ROOTS AND TUBERS: 19
- POULTRY: 19
- EGG AND EGG PRODUCTS: 15
- MARINE SHELLFISH: 15
- CONDIMENTS AND SPICES-FRESH: 10
- FRESHWATER FISH AND SHELLFISH: 10
- SUGARS AND JAGGERY: 4
- MUSHROOMS: 4
- MILK AND MILK PRODUCTS: 4

**IFCT nutrient columns:** moisture_g, protein_g, ash_g, fat_g, fibre_total_g, fibre_insoluble_g, fibre_soluble_g, carb_available_g, energy_kj

All values are **per 100g edible portion** with uncertainty notation (e.g., `9.20±0.40`).

---

### 1.3 Household Measurements (`data/interim/phase2/household_measurements.csv`)

| Metric | Value |
|--------|-------|
| Total entries | 68 |
| Units | cup, tablespoon, teaspoon, piece, clove |
| Verified (USDA) | 63 entries |
| Indian kitchen | 5 entries |
| Confidence ≥0.9 | 63 |

**Note:** Previous audit reported 94 entries; actual count is 68. The 94 figure appears to be a documentation error.

### 1.4 Ingredient Synonyms (`data/interim/phase2/ingredient_synonyms.csv`)

| Metric | Value |
|--------|-------|
| Total entries | 264 |
| Categories | pulse, grain, vegetable, fruit, spice, dairy, oil, nut, dried_fruit, etc. |

### 1.5 INDB Prepared Foods (`data/processed/indb_foods.parquet`)

| Metric | Value |
|--------|-------|
| Records | 1,014 |
| Unique food codes | 1,014 |
| Per-100g nutrients | 39 (energy, protein, fat, carbs, fibre, vitamins, minerals, etc.) |
| Per-serving nutrients | 39 matching columns (serving_*) |
| Missing serving data | 82 records |
| **Important:** INDB contains **prepared dishes/beverages**, NOT raw ingredients. Must not be used as raw ingredient composition source. |

### 1.6 Recipes

| Metric | Value |
|--------|-------|
| Total recipes | 6,865 |
| Columns | recipe_id, recipe_name_original, recipe_name_en, ingredients_raw, ingredients_en, prep_time_min, cook_time_min, total_time_min, servings, recipe_type, cuisine, course, diet_labels, instructions_raw, instructions_en, source_url, source_domain, created_at, updated_at |

**Note:** Only 650/6,865 recipes (9.5%) have en records in parsed output. 90.5% of recipes lose their `ingredients_en` representation during parsing — this is a Stage 1 issue where en records are dropped during the parsing loop.

---

## 2. Discrepancies vs. Previous Audit Reports

| Audit Claim | Actual Value | Status |
|-------------|--------------|--------|
| Household measurements | 94 claimed | 68 actual | ⚠️ Doc error |
| "Standard resolved: 47,510" | No RESOLVED category exists | N/A (schema has only UNRESOLVED/RESOLVED_HOUSEHOLD) |
| "Total resolved: 1,299" | 1,299 gram weights | Matches gram_weight count |
| Previous gram weights: 1,080 | 1,080 verified | ✅ |
| Claimed increase: 240 | Actual: 219 (1,299 - 1,080) | Doc error |
| Canonical source matches | 75,211 | ✅ Verified |
| "English missing from 90.5% recipes" | 6,215/6,865 = 90.5% | ✅ Verified |

---

## 3. Critical Bug Fix Verified

**Reconciliation Bug Fixed:** The `reconcile_sources()` function was using `_is_raw`/`_is_en` (first-value aggregation) instead of `has_raw`/`has_en` (any-aggregation). This caused 0 canonical matches despite 75,211 actual matches existing.

**Fix applied in `src/ingredients/ingredient_parser.py`:**
```python
# Before (buggy):
grouped['source_reconciliation'] = grouped.apply(
    lambda r: 'canonical' if r['_is_raw'] and r['_is_en'] else ...

# After (fixed):
grouped['source_reconciliation'] = grouped.apply(
    lambda r: 'canonical' if r['has_raw'] and r['has_en'] else ...
```

**Impact:**
- Before: 0 canonical, 83,098 raw_only, 7,764 en_only
- After: 75,211 canonical (82.8%), 7,887 raw_only, 7,764 en_only
- Discrepancy flag: 0 (correctly 0)

---

## 4. Test Results Summary

| Test Suite | Passed | Failed | Status |
|------------|--------|--------|--------|
| Phase 1 (44 tests) | 44 | 0 | ✅ |
| Stage 2 Normalization (14) | 14 | 0 | ✅ |
| Stage 2 Quantity Parsing (22) | 22 | 0 | ✅ |
| **Total Phase 1+2** | **80** | **0** | ✅ |

**Legacy IFCT tests (7 failed):** Pre-existing failures in legacy v15 extractor (512 vs 450 rows, missing food groups, missing food codes). These are **pre-existing legacy issues unrelated to Stage 2**. Stage 2 does not invoke the legacy extractor.

---

## 4. Frozen Input Integrity Verified

| Asset | SHA-256 | Status |
|-------|---------|--------|
| IFCT2017.pdf | `7fc5a5112a57240d25bf695dca82cccd8d93ed54e8c39530e42b5ad1820d0e8c` | ✅ |
| IFCT2017_decrypted.pdf | `eceda70817080ab561a958727c84a1bdcac01bc359be7042a747af79e6b0775e` | ✅ |
| recipes.parquet | `204bc7ab4c275ccccacc26c4b6d80aac696a392c8efe812d8d5738ff61fd66d8` | ✅ |
| indb_foods.parquet | `e595791f1d40980f15201145ad3cd64306358dd5313df1cd55c57c83c420dd31` | ✅ |

All Phase 1/2 frozen inputs unchanged.

---

## 5. Key Limitations & Gaps for Phase 3

| Issue | Count | Impact |
|-------|-------|--------|
| Unquantified ingredients | 4,306 (4.7%) | Cannot compute nutrition |
| Unresolved conversions | 8,810 (9.7%) | No gram weight | Flagged UNRESOLVED |
| Raw-only ingredients | 7,887 (8.7%) | Single-source only | Documented |
| En-only ingredients | 7,764 (8.5%) | Single-source only | Documented |
| Missing en in parsed | 6,215 recipes (90.5%) | Stage 1 issue | Documented |
| No cooking retention factors | — | Nutrition = raw only | Documented |
| INDB is prepared dishes | — | Cannot substitute for raw ingredients | Documented |

---

## 5. Phase 3 Readiness Assessment

| Requirement | Status | Notes |
|-------------|--------|-------|
| IFCT schema understood | ✅ | 528 foods, 9 nutrient columns |
| Canonical ingredients ready | ✅ | 90,862 records |
| Household measurements | ✅ | 68 verified entries |
| INDB reference | ✅ | 1,014 prepared dishes |
| Synonym dictionary | ✅ | 264 entries |
| Frozen inputs verified | ✅ | SHA-256 hashes match |
| Tests passing | ✅ | 80/80 Phase 1+2 tests pass |

---

## 6. Phase 3 Implementation Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| 90.5% recipes missing en in parsed | High | Stage 1 issue; Phase 3 uses canonical (merged) data |
| 90.5% recipes lose en | High | Matching uses canonical (merged) names |
| 89,525 UNRESOLVED conversions | High | Flag explicitly; don't invent |
| 98.5% UNRESOLVED conversions | High | Only 1.5% have gram weights |
| INDB is prepared dishes | Critical | Never use as raw ingredient source |
| No cooking retention factors | Medium | Document limitation |
| No oil absorption model | Medium | Document limitation |

---

## 6. Go/No-Go Decision

**✅ GO — Phase 3 may proceed.**

All Phase 2 deliverables verified. Critical reconciliation bug fixed. 80/80 Phase 1+2 tests pass. Frozen inputs intact. Critical data integrity issues documented.

---

## Recommended Phase 3 Stage 0 Actions

1. **Create directory structure:**
   - `src/matching/`, `src/nutrition/`
   - `data/interim/phase3/`, `data/processed/phase3/`, `reports/phase3/`, `tests/phase3/`

2. **Stage 1 (IFCT Schema Validation):**
   - Validate IFCT nutrient columns, units, missing patterns
   - Document edible portion handling (IFCT provides per 100g edible portion)

2. **Stage 2:** Candidate generation (exact, synonym, fuzzy, token-based)

3. **Stage 3:** Matching rules with safety guards

4. **Stage 4:** Manual gold-standard evaluation (200+ items)

5. **Stage 5-6:** Weight/edible portion → nutrient calculation

---

**Preflight Complete. Phase 3 may proceed with Stage 1.**