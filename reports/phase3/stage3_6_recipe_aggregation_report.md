# Stage 3.6: Recipe Aggregation Report

**Date:** 2026-11-19  
**Status:** Implementation Complete

---

## 1. Purpose

Aggregate ingredient-level nutrient contributions into recipe-level nutrition summaries, preserving missingness and tracking coverage at every level.

---

## 2. Aggregation Logic

### Input
- List of `IngredientNutritionOutput` (one per mapped ingredient)

### Process
1. Sum calculated nutrients across all valid ingredients
2. Track per-nutrient ingredient counts
3. Calculate completeness metrics
4. Determine overall recipe status

### Output: RecipeNutritionOutput
```python
RecipeNutritionOutput(
    recipe_id: int,
    total_nutrients: Dict[str, float],           # Summed contributions
    nutrient_completeness: Dict[str, float],     # Per-nutrient coverage
    ingredient_mapping_coverage: float,          # Mapped / total ingredients
    gram_weight_coverage: float,                 # With resolved weights / total
    mapped_ingredient_count: int,
    total_ingredient_count: int,
    unresolved_ingredient_count: int,
    calculation_status: RecipeCalculationStatus,
    ingredient_details: List[IngredientNutritionOutput],
    provenance: Dict
)
```

---

## 3. Completeness Definitions

### Per-Nutrient Completeness
```
nutrient_completeness[nutrient] = ingredients_with_nutrient / max(mapped_ingredients, 1)
```

**Interpretation:** Proportion of *mapped* ingredients contributing to this nutrient.

### Overall Completeness
```
overall_completeness = mean(nutrient_completeness.values())
```

**Interpretation:** Average nutrient coverage across all 9 standard nutrients.

### Mapping Coverage
```
ingredient_mapping_coverage = mapped_ingredients / total_ingredients
```

### Gram Weight Coverage
```
gram_weight_coverage = ingredients_with_resolved_weight / total_ingredients
```

---

## 4. Recipe Calculation Status

| Status | Condition |
|--------|-----------|
| `COMPLETE` | All ingredients mapped AND all calculated COMPLETE |
| `PARTIAL` | At least 1 mapped ingredient, but not all |
| `NO_MAPPED_INGREDIENTS` | Zero ingredients with approved mappings |
| `INSUFFICIENT_DATA` | Edge case (should not occur) |
| `UNAVAILABLE` | Default (no input) |

---

## 5. Aggregation Examples

### Example 1: Complete Recipe
```
Recipe: Rice + Dal
Ingredients: 2 mapped, 2 total
Rice (100g): protein=7.5g, energy=350kJ
Dal (50g): protein=11.0g, energy=600kJ
```
**Result:**
- total_nutrients: protein=18.5g, energy=950kJ
- mapping_coverage: 1.0 (2/2)
- status: COMPLETE

### Example 2: Partial Recipe
```
Recipe: Rice + Unknown Spice
Ingredients: 1 mapped, 2 total
Rice (100g): protein=7.5g, energy=350kJ
Spice: no mapping
```
**Result:**
- total_nutrients: protein=7.5g, energy=350kJ
- mapping_coverage: 0.5 (1/2)
- unresolved: 1
- status: PARTIAL

### Example 3: Duplicate Ingredients
```
Recipe: Rice (50g) + Rice (50g)  # Two separate records
Ingredients: 2 mapped, 2 total (both same food)
Each: protein=3.75g
```
**Result:**
- total_nutrients: protein=7.5g (summed)
- mapping_coverage: 1.0
- status: COMPLETE

---

## 6. Missingness Preservation

### Rules
1. **No imputation** - Missing nutrients never become zero
2. **Per-nutrient tracking** - Each nutrient has independent completeness
3. **Ingredient-level detail** - Every ingredient's status preserved in `ingredient_details`
4. **Provenance chain** - Source traced to mapping decision + IFCT + weight

### Output Example (Partial Recipe)
```json
{
  "recipe_id": 1,
  "total_nutrients": {"protein_g": 7.5, "energy_kj": 350},
  "nutrient_completeness": {
    "protein_g": 1.0,
    "fat_g": 0.0,
    "carb_available_g": 0.0,
    "energy_kj": 1.0,
    ...
  },
  "ingredient_mapping_coverage": 0.5,
  "calculation_status": "PARTIAL",
  "ingredient_details": [
    {
      "calculated_nutrients": {"protein_g": 7.5, "energy_kj": 350},
      "missing_nutrients": [],
      "calculation_status": "COMPLETE"
    },
    {
      "calculated_nutrients": {},
      "missing_nutrients": [],
      "calculation_status": "MISSING_MAPPING"
    }
  ]
}
```

---

## 7. AggregationConfig

```python
AggregationConfig(
    min_mapped_ingredients: int = 1,
    min_gram_weight_coverage: float = 0.0,
    require_all_nutrients: bool = False,
    completeness_threshold: float = 0.5
)
```
- Currently not enforced (passive thresholds)
- Available for future filtering

---

## 8. Batch Processing

```python
aggregator.aggregate_recipes(recipe_ids, all_weight_infos)
```
- Groups weight_infos by recipe_id
- Processes each recipe independently
- Returns List[RecipeNutritionOutput]

---

## 9. Coverage Analysis Integration

```python
analyzer = CoverageAnalyzer(aggregator)
report = analyzer.analyze_results(results)
analyzer.export_report(report, output_dir, prefix)
```

**Outputs:**
- `coverage_summary.json` - Overall statistics
- `coverage_recipe_details.csv` - Per-recipe breakdown
- `coverage_nutrient_coverage.csv` - Per-nutrient statistics
- `coverage_ingredient_coverage.json` - Mapping/weight stats
- `coverage_report.md` - Human-readable with limitations

---

## 10. Current Limitations (with Real Data)

| Limitation | Impact |
|------------|--------|
| 0 approved mappings | All recipes → NO_MAPPED_INGREDIENTS |
| 1.4% gram weight coverage | Most ingredients → MISSING_WEIGHT |
| 42% IFCT nutrient gaps | Fibre/carb often missing |
| 88% NOT_SPECIFIED prep | Compatibility unknown |
| No cooked IFCT entries | Cooked preparations unsupported |

---

## 11. Files

| File | Purpose |
|------|---------|
| `src/nutrition/recipe_aggregator.py` | `RecipeAggregator`, `AggregationConfig`, helpers |
| `src/nutrition/coverage_report.py` | `CoverageAnalyzer`, `CoverageReport`, export |
| `src/nutrition/nutrition_models.py` | `RecipeNutritionOutput`, `RecipeCalculationStatus` |
| `tests/phase3/test_nutrition_calculator.py::TestRecipeAggregation` | 6 tests |

---

## 12. Testing

**Tests in `tests/phase3/test_nutrition_calculator.py::TestRecipeAggregation`:**
- `test_fully_mapped_recipe` ✅
- `test_partially_mapped_recipe` ✅
- `test_no_mapped_ingredients` ✅
- `test_missing_nutrients_in_aggregation` ✅
- `test_missing_weights_in_aggregation` ✅
- `test_duplicate_ingredient_records` ✅

**All 6 aggregation tests pass.**

---

*End of Recipe Aggregation Report*