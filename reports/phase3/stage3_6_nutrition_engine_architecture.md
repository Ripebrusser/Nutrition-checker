# Stage 3.6: Nutrition Engine Architecture Report

**Date:** 2026-11-19  
**Status:** Implementation Complete

---

## 1. Architecture Overview

The nutrition calculation engine is implemented as a modular Python package (`src/nutrition/`) with clear separation of concerns:

```
src/nutrition/
├── __init__.py                    # Package exports
├── nutrition_models.py            # Data contracts (Pydantic-like dataclasses)
├── ingredient_mapping.py          # Strict mapping interface (approved only)
├── edible_portion.py              # Edible portion weight handling
├── nutrient_calculator.py         # Core nutrient calculation logic
├── nutrient_validation.py         # Validation of nutrient values
├── recipe_aggregator.py           # Recipe-level aggregation
├── coverage_report.py             # Coverage analysis & reporting
└── demo.py                        # Controlled demonstration
```

---

## 2. Data Contracts (nutrition_models.py)

### Core Enums
| Enum | Values | Purpose |
|------|--------|---------|
| `MappingStatus` | APPROVED, REJECTED, AMBIGUOUS, UNMATCHED, CANDIDATE | Mapping decision state |
| `CalculationStatus` | COMPLETE, PARTIAL, MISSING_WEIGHT, MISSING_MAPPING, MISSING_NUTRIENTS, INVALID_INPUT | Per-ingredient calculation result |
| `RecipeCalculationStatus` | COMPLETE, PARTIAL, INSUFFICIENT_DATA, NO_MAPPED_INGREDIENTS, UNAVAILABLE | Per-recipe aggregation result |

### Input Contracts
| Class | Key Fields |
|-------|------------|
| `IFCTNutrientRecord` | food_code, food_name, food_group, 9 nutrient fields (per 100g edible) |
| `ApprovedMapping` | recipe_id, ingredient_record_id, ifct_food_code, mapping_status, reviewer_id, timestamp |
| `IngredientWeightInfo` | recipe_id, ingredient_record_id, gram_weight, conversion_status, preparation_state, is_edible_weight |
| `IngredientNutritionInput` | recipe_id, ingredient_record_id, ifct_food_code, edible_weight_g, nutrient_values, mapping_status |

### Output Contracts
| Class | Key Fields |
|-------|------------|
| `IngredientNutritionOutput` | calculated_nutrients, missing_nutrients, calculation_status, provenance |
| `RecipeNutritionOutput` | total_nutrients, nutrient_completeness, mapping_coverage, weight_coverage, ingredient_details |

### Standard Nutrients (NUTRIENT_NAMES)
```
['moisture_g', 'protein_g', 'ash_g', 'fat_g', 
 'fibre_total_g', 'fibre_insoluble_g', 'fibre_soluble_g',
 'carb_available_g', 'energy_kj']
```

### Units (NUTRIENT_UNITS)
All nutrients in **g per 100g edible portion** except `energy_kj` in **kJ per 100g edible portion**.

---

## 3. Module Responsibilities

### 3.1 ingredient_mapping.py - Strict Mapping Interface
**Purpose:** Enforce that ONLY explicitly approved mappings enter calculation.

**Key Classes:**
- `ApprovedMappingStore` - Stores only APPROVED mappings, rejects duplicates with different IFCT codes
- `StrictMappingInterface` - Gateway between mapping store and calculator
- `MappingReviewRecord` - Review decision persistence (APPROVE/REJECT/AMBIGUOUS/DEFER)

**Rules Enforced:**
1. Only `MappingStatus.APPROVED` mappings usable
2. Rejected mappings never used
3. Ambiguous mappings never auto-used
4. Candidate similarity scores ≠ probabilities
5. Preparation-state compatibility checked
6. IFCT raw-food basis respected

### 3.2 edible_portion.py - Edible Portion Handling
**Purpose:** Convert gross weights to edible weights using validated factors.

**Key Features:**
- Hardcoded database (~180 IFCT codes) with edible portion percentages
- Source: IFCT 2017, USDA, validated Indian food data
- `EdiblePortionCalculator.calculate_edible_weight()` handles:
  - Already-edible weights (no conversion)
  - Gross weights with validated factors
  - Missing factors → returns None (not zero)
  - Double-conversion prevention

**Database Coverage:**
- Cereals/pulses: 100% edible (dry goods)
- Leafy vegetables: 70-85% (stems discarded)
- Roots/tubers: 75-85% (peel removed)
- Fruits: 55-85% (peel/seeds removed)
- Nuts: 50-100% (shell removed)
- Animal foods: 70-100% (bones/waste removed)
- Spices/oils/sugars: 100% (fully used)

### 3.3 nutrient_calculator.py - Core Calculation
**Purpose:** Calculate nutrient contributions from approved mappings + weights.

**Formula:**
```
nutrient_contribution = nutrient_per_100g_edible × edible_weight_g / 100
```

**Key Logic:**
- Uses ONLY explicitly provided `nutrient_values` (no fallback unless None)
- Empty dict `{}` = explicitly no nutrients → MISSING_NUTRIENTS
- `nutrient_values=None` = fallback to IFCT record
- Missing IFCT values → tracked in `missing_nutrients` (never zero)
- kJ → kcal conversion: 1 kcal = 4.184 kJ
- Validation runs but doesn't block calculation (informational)

### 3.4 nutrient_validation.py - Validation
**Purpose:** Validate nutrient values for consistency.

**Checks:**
1. Range validation per 100g (ERROR if outside IFCT-typical ranges)
2. Energy consistency via Atwater factors (ERROR if >20% discrepancy)
3. Macronutrient sum ≤ 105g per 100g (WARNING)
4. Negative contributions → ERROR

**Atwater Factors (kJ/g):**
- Protein: 17, Fat: 37, Available Carb: 17, Fibre: 8

### 3.5 recipe_aggregator.py - Recipe Aggregation
**Purpose:** Sum ingredient contributions into recipe-level nutrition.

**Aggregation Rules:**
- Only valid (COMPLETE/PARTIAL) ingredient outputs summed
- Missing nutrients preserved (not imputed)
- Coverage metrics: mapping_coverage, gram_weight_coverage
- Per-nutrient completeness = ingredients_with_nutrient / mapped_ingredients
- Status: COMPLETE only if ALL ingredients mapped AND calculated

### 3.6 coverage_report.py - Analysis & Reporting
**Purpose:** Generate comprehensive coverage analysis.

**Outputs:**
- Summary statistics (JSON)
- Per-recipe details (CSV)
- Nutrient coverage analysis (CSV)
- Ingredient coverage analysis (JSON)
- Full markdown report with limitations & recommendations

---

## 4. Data Flow

```
┌─────────────────┐
│ Phase 2 Parsed  │
│ Ingredients     │
│ (90,862 records)│
└────────┬────────┘
         │ create_weight_infos_from_parsed()
         ▼
┌─────────────────┐
│ IngredientWeightInfo
│ List per Recipe
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ StrictMapping   │────▶│ ApprovedMapping │
│ Interface       │     │ Store           │
│ (approved only) │     │ (human reviewed)│
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ EdiblePortion   │     │ IFCT Nutrient   │
│ Calculator      │     │ Data (528 foods)│
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────────────────────────┐
│ NutrientCalculator                  │
│ (per-ingredient calculation)        │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ RecipeAggregator                    │
│ (sums ingredients, tracks coverage) │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ CoverageAnalyzer                    │
│ (generates reports)                 │
└─────────────────────────────────────┘
```

---

## 5. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Dataclasses over Pydantic | Zero dependencies, stdlib only, sufficient for contracts |
| Explicit nutrient_values | No silent fallback to IFCT; user controls what's calculated |
| Missing = NaN, not 0 | Scientific integrity; missing ≠ absent |
| Strict mapping interface | Prevents candidate→approved confusion; audit trail |
| Edible portion DB hardcoded | No external dependency; validated sources only |
| Validation informational | Doesn't block calculation; provenance preserved |
| Coverage per-nutrient | Different nutrients have different IFCT completeness |

---

## 6. Integration Points

| Phase | Integration |
|-------|-------------|
| Phase 1 | Recipe metadata (cuisine, course, diet) - not used in nutrition calc |
| Phase 2 | `parsed_recipe_ingredients.parquet` → `IngredientWeightInfo` |
| Phase 3.2.3 | `ifct_match_candidates.parquet` → review app → approved mappings |
| Phase 3.6 | **This engine** - consumes approved mappings + weights |
| Phase 4 | Recipe nutrition output → personalization layer |
| Phase 5 | Nutrition features → recommender enhancement |

---

## 7. Testing

**Test Coverage:** 42 unit tests in `tests/phase3/test_nutrition_calculator.py`

| Category | Tests |
|----------|-------|
| Basic calculation (100g, 50g, 250g) | 3 |
| Edge cases (zero, negative, missing) | 5 |
| Mapping interface (approved/rejected/ambiguous) | 8 |
| Edible portion (known, missing, double-conversion) | 4 |
| Recipe aggregation (full, partial, none, duplicates) | 6 |
| Data integrity (hashes, determinism, provenance) | 5 |
| Synthetic fixtures | 2 |
| Validation (ranges, energy, macros) | 3 |
| Edge cases (NaN, empty dict, ± parsing) | 3 |

**All 42 tests pass.** Existing regression tests (280+) continue to pass.

---

## 8. Limitations Documented

1. **No approved mappings exist yet** - Requires human review via Stage 3.4 app
2. **Gram weight coverage: 1.4%** - Most ingredients lack resolved weights
3. **IFCT nutrient gaps:** 42% missing for fibre/carb columns
4. **Preparation state:** 88% NOT_SPECIFIED - compatibility uncertain
5. **Edible portion DB:** ~180/528 IFCT codes covered
6. **No cooked IFCT entries** - Cooked preparations not supported
7. **Energy validation strict** - Many IFCT values differ from Atwater >20%

---

## 9. Files Created/Modified

| File | Status |
|------|--------|
| `src/nutrition/__init__.py` | Updated exports |
| `src/nutrition/nutrition_models.py` | Created (data contracts) |
| `src/nutrition/ingredient_mapping.py` | Created (strict interface) |
| `src/nutrition/edible_portion.py` | Enhanced (DB + logic) |
| `src/nutrition/nutrient_calculator.py` | Rewritten (complete logic) |
| `src/nutrition/nutrient_validation.py` | Enhanced (ranges + Atwater) |
| `src/nutrition/recipe_aggregator.py` | Created (aggregation logic) |
| `src/nutrition/coverage_report.py` | Created (analysis + reports) |
| `src/nutrition/demo.py` | Created (controlled demo) |
| `tests/phase3/test_nutrition_calculator.py` | Created (42 tests) |
| `reports/phase3/stage3_6_preflight_report.md` | Created |
| `reports/phase3/stage3_6_nutrition_engine_architecture.md` | **This report** |

---

*End of Architecture Report*