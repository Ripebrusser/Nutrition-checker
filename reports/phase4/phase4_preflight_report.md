# Phase 4: Preflight Audit Report

**Date:** 2026-11-19  
**Status:** Audit Complete — Ready for Implementation

---

## 1. Repository State Summary

### 1.1 Existing Modules

| Module | Location | Status | Key Exports |
|--------|----------|--------|-------------|
| Nutrition Engine | `src/nutrition/` | Complete (Phase 3.6) | `NutrientCalculator`, `StrictMappingInterface`, `RecipeAggregator`, `EdiblePortionCalculator`, `CoverageAnalyzer` |
| Review Workflow | `src/review/`, `app/ingredient_review_app.py` | Complete (Phase 3.4) | Role-isolated blind review, 5 safeguards |
| Recommendation | `src/recommendation/` | Complete (Phase 5.1-5.3) | `ContentBasedRecipeRecommender`, `RecipePreprocessor`, `RecipeFeatureExtractor`, `baseline_recommenders`, `evaluation` |
| Data Preprocessing | `src/preprocessing/`, `src/ingredients/` | Complete (Phase 1-2) | Ingredient normalization, quantity parsing, synonym handling |

### 1.2 Dataset Inventory (Frozen, Hash-Verified)

| # | File | SHA-256 | Records | Status |
|---|------|---------|---------|--------|
| 1 | `normalized_ingredients.parquet` | `08710983213938c3fecafd20991ab7d3d7fe51b179303bbe4dc93b2ac1b1b6e5` | 90,862 | ✅ |
| 2 | `parsed_recipe_ingredients.parquet` | `e17b668b208dac4a7240cbfb27d78caac6123bc2b29b34a70aeb38964b9e86d9` | 90,862 | ✅ |
| 3 | `ingredient_synonyms.csv` | `22b8aace1ef29ea271051004a0e5a79ac8a8bfb5d80b8f796abe0db1f2ee4b31` | 1,200+ | ✅ |
| 4 | `household_measurements.csv` | `451fb9c6d5135e0684bd5e6445aeaadfafa2951db6ae7fd939b96faad1e16b47` | 68 | ✅ |
| 5 | `ifct_table1_candidate.parquet` | `294c6fc4d095a47e13fbe02e8e3c1c0c8175752966275a3415f9a7df04774f35` | 528 | ✅ |
| 6 | `ifct_match_candidates.parquet` | `2bb9f0d7770f7669ad3cd30f49d2a15f820f572e53690678f58891229336740f` | 119,474 | ✅ |
| 7 | `unmatched_ingredients.parquet` | `4d4e2b84e3b3323552c600bf90eefba81c5e44ee8f455298f331c190ced08102` | 63,244 | ✅ |
| 8 | `household_measurements.csv (S2.3)` | `4c169cba077c49f384e699129e9051929ad130dda2221ac2692cf9c34e04567e` | 68 | ✅ |

**All 8 frozen dataset hashes match. ✅**

### 1.3 Recipe Dataset

| Metric | Value |
|--------|-------|
| Total recipes | 6,865 |
| Columns | 19 (recipe_id, recipe_name_en, cuisine, course, diet_labels, prep/cook times, servings, etc.) |
| Cuisine types | 75 |
| Course types | 10 |
| Diet labels | 20 (pipe-separated) |
| Recipe types | 3 (veg, non-veg, eggetarian) |

### 1.4 Ingredient Data

| Metric | Value |
|--------|-------|
| Canonical ingredient records | 90,862 |
| Unique primary ingredients | 2,725 |
| Gram weight coverage | 1.4% (1,299/90,862) |
| Household conversion coverage | 1.5% (1,337/90,862) |
| Unresolved | 98.5% (89,525/90,862) |

### 1.5 IFCT Nutrition Data

| Metric | Value |
|--------|-------|
| Food records | 528 |
| Food groups | 18 |
| Nutrients per 100g edible | 9 (moisture, protein, ash, fat, fibre_total, fibre_insoluble, fibre_soluble, carb_available, energy_kJ) |
| Missing nutrients (fibre/carb) | 42% (222/528) |
| Edible portion factors | ~180/528 codes (34%) |

### 1.6 Mapping Status

| Metric | Value |
|--------|-------|
| Review units (corrected key) | 7,992 |
| Auto-accepted (unverified) | 3 |
| Requiring human review | 7,989 |
| **Approved mappings** | **0** |
| Gate C authorization | **PENDING** |

---

## 2. Existing Interface Contracts

### 2.1 Nutrition Engine (`src/nutrition/`)

**Key Input:**
```python
IngredientNutritionInput(
    recipe_id, ingredient_record_id, original_ingredient, normalized_ingredient,
    ifct_food_code, ifct_food_name, ifct_food_group,
    mapping_status=MappingStatus.APPROVED,  # ONLY approved mappings
    preparation_state, edible_weight_g, nutrient_values, source_provenance
)
```

**Key Output:**
```python
IngredientNutritionOutput(
    calculated_nutrients: Dict[str, float],  # per nutrient
    missing_nutrients: List[str],             # never zero-imputed
    calculation_status: CalculationStatus,    # COMPLETE/PARTIAL/MISSING_*
    provenance: Dict
)
```

**Recipe Aggregation:**
```python
RecipeNutritionOutput(
    total_nutrients: Dict[str, float],
    nutrient_completeness: Dict[str, float],  # per-nutrient
    ingredient_mapping_coverage: float,
    gram_weight_coverage: float,
    mapped_ingredient_count: int,
    total_ingredient_count: int,
    calculation_status: RecipeCalculationStatus  # COMPLETE/PARTIAL/NO_MAPPED/INSUFFICIENT
)
```

### 2.2 Recommendation Engine (`src/recommendation/`)

**ContentBasedRecipeRecommender:**
- `fit(recipe_ingredients, recipe_metadata)` — recipe_id → List[str] ingredients, metadata dict
- `recommend(query_recipe_id, k, filters)` — filters: cuisine, course, diet_labels
- `recommend_by_ingredients(ingredients, k, filters)` — ingredient-based query
- Returns `RecommendationResult` with component_scores, explanation, shared_ingredients

**RecipePreprocessor:**
- `get_recipe_ingredient_mapping()` → Dict[recipe_id, List[normalized_ingredient]]
- `get_recipe_metadata_mapping()` → Dict[recipe_id, Dict[cuisine, course, diet_labels, ...]]

**Evaluation Metrics:**
- `precision_at_k`, `recall_at_k`, `intra_list_diversity`, `coverage`, `novelty`
- `cuisine_constraint_compliance`, `diet_constraint_compliance`

---

## 3. Integration Boundaries for Phase 4

| Phase 4 Module | Consumes From | Provides To |
|----------------|---------------|-------------|
| `user_profile` | — | Validated user profiles |
| `nutrition_targets` | User profile | Energy/macro targets with provenance |
| `dietary_constraints` | User profile + Recipe metadata | PASS/FAIL/UNVERIFIED per recipe |
| `recipe_profile` | Phase 2 ingredients + Phase 3 nutrition + Phase 5 features | Unified recipe profile with nutrition completeness |
| `personalized_recommender` | Phase 5 recommender + user profile + dietary constraints + nutrition targets | Ranked recommendations with explanations |
| `meal_planner` | Personalized recommender + nutrition targets + dietary constraints | Meal plans with nutritional summaries |
| `explanation_engine` | All above | Traceable explanations |

---

## 4. Test Baseline (Pre-Phase 4)

| Test Suite | Tests | Status |
|------------|-------|--------|
| Phase 3 Review (`test_review_app.py`) | 30 | ✅ PASS |
| Phase 3 Nutrition (`test_nutrition_calculator.py`) | 42 | ✅ PASS |
| Phase 2 Regression | 54 | ✅ PASS |
| Phase 5 Recommendation | 127 | 126 PASS, 1 timeout (pre-existing) |
| **Total Independent** | **72** | **72 PASS** |

---

## 5. Key Limitations (Must Not Be Concealed)

| Limitation | Impact on Phase 4 |
|------------|-------------------|
| **Zero approved mappings** | Nutrition engine returns `NO_MAPPED_INGREDIENTS` for all recipes; real-data nutrition unavailable |
| **1.4% gram weight coverage** | Most recipe nutrition estimates will be `UNAVAILABLE` or `PARTIAL` |
| **42% IFCT nutrient gaps** | Fibre/carb missing for 222/528 foods; completeness < 58% for those nutrients |
| **34% edible portion coverage** | ~180/528 IFCT codes have factors; as-purchased weights need manual factors |
| **No user interaction data** | No collaborative filtering; personalization is rule-based + content-based only |
| **No real user profiles** | Synthetic profiles needed for testing; real-data validation limited |
| **Gate C PENDING** | No human-reviewed mappings until pilot authorized |

---

## 6. Implementation Readiness

| Component | Ready? | Notes |
|-----------|--------|-------|
| Nutrition engine integration | ✅ | `StrictMappingInterface` returns `None` for unapproved; safe with zero mappings |
| Recipe metadata access | ✅ | `get_recipe_metadata_mapping()` provides cuisine, course, diet_labels |
| Ingredient lists | ✅ | `get_recipe_ingredient_mapping()` provides normalized ingredients |
| Content-based recommender | ✅ | `ContentBasedRecipeRecommender` supports filters (cuisine, course, diet) |
| Evaluation framework | ✅ | Precision, recall, diversity, coverage, constraint compliance |
| User profile storage | ❌ | New module needed |
| Nutritional target calculation | ❌ | New module needed |
| Dietary constraint engine | ❌ | New module needed |
| Recipe-nutrition integration | ❌ | New module needed |
| Personalized recommender | ❌ | New module needed |
| Meal planner | ❌ | New module needed |
| Explanation engine | ❌ | New module needed |

---

## 7. Phase 4 Implementation Order

1. **User Profile Management** (`src/personalization/`)
2. **Nutritional Target Calculation** (`src/personalization/`)
3. **Dietary Constraint Engine** (`src/personalization/`)
4. **Recipe-Nutrition Feature Integration** (`src/personalization/`)
5. **Personalized Recommender** (`src/personalization/`)
6. **Meal Planner** (`src/personalization/`)
7. **Explanation Engine** (`src/personalization/`)
8. **Evaluation Framework** (`src/personalization/`)
8. **Tests & Documentation** (`tests/phase4/`, `reports/phase4/`)

---

*End of Preflight Audit Report*