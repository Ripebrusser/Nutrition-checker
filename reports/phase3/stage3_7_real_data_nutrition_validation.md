# Stage 3.7: Real-Data Nutrition Validation Report

**Date:** 2026-11-19  
**Status:** No Real-Data Validation Possible — Zero Approved Mappings

---

## 1. Executive Summary

**No approved ingredient mappings exist.** The nutrition calculation engine correctly returns `NO_MAPPED_INGREDIENTS` for all recipes. No real-data nutrition calculations can be performed until human review produces approved mappings via the Gate C authorized pilot.

This report documents the validation framework and confirms the pipeline operates correctly with synthetic fixtures.

---

## 2. Current Mapping State

| Metric | Value |
|--------|-------|
| Approved mappings (Primary) | 0 |
| Approved mappings (Auditor) | 0 |
| Approved mappings (Adjudication) | 0 |
| **Total approved mappings** | **0** |
| Review units pending | 7,992 |
| Auto-accepted (unverified) | 3 |

**The nutrition engine's `StrictMappingInterface` returns `None` for all ingredients** since no `MappingStatus.APPROVED` mappings exist in the `ApprovedMappingStore`.

---

## 3. Validation Framework (Ready for Real Data)

### 3.1 Pipeline Stages

```
Approved Mappings (review decisions)
        ↓
StrictMappingInterface.create_nutrition_input()
        ↓
IngredientNutritionInput (edible_weight_g + nutrient_values)
        ↓
NutrientCalculator.calculate_ingredient_nutrition()
        ↓
IngredientNutritionOutput (calculated_nutrients + missing_nutrients)
        ↓
RecipeAggregator.aggregate_recipe()
        ↓
RecipeNutritionOutput (total_nutrients + nutrient_completeness)
        ↓
CoverageAnalyzer.analyze_results()
```

### 3.2 Validation Points at Each Stage

| Stage | Validation |
|-------|------------|
| **Mapping** | Only `MappingStatus.APPROVED` accepted; rejected/ambiguous/candidate blocked |
| **Weight** | `edible_weight_g` required; `None` → `MISSING_WEIGHT`; never zero-imputed |
| **Edible Portion** | Validated factor (0-1) or `is_already_edible=True`; double-conversion prevented |
| **Nutrients** | Only explicit `nutrient_values` calculated; missing IFCT values tracked |
| **Energy** | kJ from IFCT; kcal = kJ/4.184 (exact conversion) |
| **Validation** | Range checks, Atwater consistency, macro sums — informational only |
| **Aggregation** | Only COMPLETE/PARTIAL ingredients summed; completeness per-nutrient |
| **Coverage** | Mapping coverage, weight coverage, nutrient completeness reported |

### 3.3 Provenance Preservation
Every output includes complete traceability:
- Mapping: reviewer_id, timestamp, evidence_references, confidence
- IFCT: food_code, verification_status, source_page, source_table
- Weight: conversion_status, household_source, confidence, prep_state
- Edible portion: factor, source, waste_description
- Validation: is_valid, warnings, errors

---

## 4. Synthetic Validation Results

Since no approved mappings exist, the pipeline was validated using clearly labeled synthetic fixtures (see `src/nutrition/demo.py` and `tests/phase3/test_nutrition_calculator.py::TestSyntheticFixtures`).

### 4.1 Synthetic Calculation Correctness
| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| 100g rice | protein=7.5, fat=0.5, carb=78, energy=350 | 7.5, 0.5, 78, 350 | 7.5, 0.5, 78, 350 | ✅ |
| 50g dal | protein=22, fat=1.5, carb=47, energy=1200 | 11.0, 0.75, 23.5, 600 | 11.0, 0.75, 23.5, 600 | ✅ |
| 250g rice | protein=7.5, fat=0.5, carb=78, energy=350 | 18.75, 1.25, 195, 875 | 18.75, 1.25, 195, 875 | ✅ |

### 4.2 Synthetic Recipe Aggregation
| Recipe | Ingredients | Expected Protein | Actual Protein | Status |
|--------|-------------|------------------|----------------|--------|
| Rice+Dal+Spinach | 100g+50g+50g | 19.95g | 19.95g | ✅ |

### 4.3 Edible Portion Calculation
| Input | IFCT Code | Factor | Gross | Edible | Status |
|-------|-----------|--------|-------|--------|--------|
| 100g spinach | C001 | 0.85 | 100g | 85g | ✅ |
| 100g potato | D001 | 0.80 | 100g | 80g | ✅ |
| 50g edible spinach | C001 | N/A | 50g | 50g | ✅ |

### 4.4 Missing Value Handling
| Mode | Input | Calculated | Missing | Status |
|------|-------|------------|---------|--------|
| IFCT fallback | nutrient_values=None | 6/9 | 3 (fibre) | ✅ PARTIAL |
| Explicit dict | {protein: 10} | 1/9 | 0 | ✅ COMPLETE |
| Empty dict | {} | 0/9 | 0 | ✅ MISSING_NUTRIENTS |

### 4.5 kJ → kcal Conversion
| Energy (kJ) | Expected kcal | Actual kcal | Status |
|-------------|---------------|-------------|--------|
| 350 | 83.65 | 83.65 | ✅ |
| 1200 | 286.81 | 286.81 | ✅ |

---

## 5. Real-Data Validation Blockers

| Blocker | Impact | Resolution |
|---------|--------|------------|
| **Zero approved mappings** | Engine returns `NO_MAPPED_INGREDIENTS` for all recipes | Complete Gate C pilot |
| **No gram weights for 98.6%** | Most ingredients → `MISSING_WEIGHT` | Expand household conversions |
| **42% IFCT nutrient gaps** | Fibre/carb missing for 222 foods | Supplement from USDA |
| **88% NOT_SPECIFIED prep** | Cannot verify IFCT compatibility | Capture prep state in review |

---

## 6. Validation Test Suite (42 Tests)

| Category | Tests | Status |
|----------|-------|--------|
| Basic Calculation (100g, 50g, 250g) | 3 | ✅ |
| Edge Cases (zero, negative, missing) | 5 | ✅ |
| Mapping Interface (approved/rejected/ambiguous) | 8 | ✅ |
| Edible Portion (known, missing, double-conv) | 5 | ✅ |
| Recipe Aggregation (full, partial, none, dup) | 6 | ✅ |
| Data Integrity (hashes, determinism, provenance) | 5 | ✅ |
| Synthetic Fixtures | 2 | ✅ |
| Nutrient Validation (ranges, Atwater, macros) | 3 | ✅ |
| Edge Cases (NaN, empty dict, ± parsing) | 3 | ✅ |
| **Total** | **42** | **✅ 42/42 PASS** |

---

## 7. What Real-Data Validation Will Require

Once Gate C pilot completes and approved mappings exist:

### 7.1 Minimum Validation Checklist
- [ ] At least 1 recipe with ≥1 approved mapping + resolved weight
- [ ] Ingredient-to-IFCT mapping provenance verified
- [ ] Preparation-state compatibility confirmed
- [ ] Gram weight source traced (direct/household)
- [ ] Edible portion factor validated (or `is_already_edible=True`)
- [ ] Nutrient units match IFCT (g or kJ per 100g edible)
- [ ] Missing nutrients tracked in `missing_nutrients` (not zero)
- [ ] Recipe aggregation sums only valid ingredients
- [ ] Completeness status correctly assigned (COMPLETE/PARTIAL/NO_MAPPED)
- [ ] No double edible-portion conversion
- [ ] No zero-imputation for missing values
- [ ] Partial sums not presented as complete nutrition

### 7.2 Coverage Metrics to Report
1. Total recipes in dataset
2. Recipes with ≥1 approved mapping
3. Recipes with all ingredients mapped
4. Recipes with usable ingredient weights
5. Recipes with complete energy estimates
6. Recipes with complete protein estimates
7. Recipes with complete carbohydrate estimates
8. Recipes with complete fat estimates
9. Recipes with complete fibre estimates
10. Recipes with partial nutrition
11. Recipes with unavailable nutrition

---

## 8. Conclusion

**No real-data nutrition validation has been performed** because zero approved mappings exist. This is correct behavior — the engine is designed to operate safely with zero mappings.

The validation framework is **complete, tested, and ready**. When the Gate C pilot produces approved mappings, the pipeline will:
1. Calculate nutrient contributions per ingredient
2. Aggregate to recipe level with completeness tracking
3. Report coverage honestly with limitations
4. Preserve full provenance for audit

**No fabricated results, no zero-imputation, no candidate-as-approved usage.**

---

*End of Real-Data Nutrition Validation Report*