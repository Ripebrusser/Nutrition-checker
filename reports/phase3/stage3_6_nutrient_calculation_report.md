# Stage 3.6: Nutrient Calculation Report

**Date:** 2026-11-19  
**Status:** Implementation Complete

---

## 1. Calculation Formula

### Core Formula
```
nutrient_contribution = nutrient_per_100g_edible × edible_weight_g / 100
```

Where:
- `nutrient_per_100g_edible` = IFCT value (per 100g edible portion)
- `edible_weight_g` = Edible portion weight in grams
- Result = Absolute nutrient amount in the ingredient portion

### Energy Conversion
```
energy_kcal = energy_kj / 4.184
```
- IFCT stores energy in **kJ per 100g edible**
- kcal output provided for usability
- Conversion factor: 1 kcal = 4.184 kJ (exact)

---

## 2. Nutrients Calculated

| Nutrient | IFCT Column | Unit | Description |
|----------|-------------|------|-------------|
| Moisture | moisture_g | g | Water content |
| Protein | protein_g | g | Total protein |
| Ash | ash_g | g | Mineral residue |
| Fat | fat_g | g | Total fat (lipids) |
| Total Fibre | fibre_total_g | g | Total dietary fibre |
| Insoluble Fibre | fibre_insoluble_g | g | Insoluble fibre fraction |
| Soluble Fibre | fibre_soluble_g | g | Soluble fibre fraction |
| Available Carbohydrate | carb_available_g | g | Carbohydrates available for metabolism |
| Energy | energy_kj | kJ | Metabolizable energy |

**Note:** Fibre subcomponents NOT summed to derive total. Each from IFCT independently.

---

## 3. Input Modes

### Mode 1: Explicit Nutrient Values (Preferred)
```python
IngredientNutritionInput(
    nutrient_values={'protein_g': 7.5, 'fat_g': 0.5, ...},  # Only these calculated
    edible_weight_g=100.0
)
```
- Only explicitly provided nutrients calculated
- Missing keys in dict → not calculated, not in `missing_nutrients`
- Explicit `None` values → tracked in `missing_nutrients`

### Mode 2: IFCT Fallback (nutrient_values=None)
```python
IngredientNutritionInput(
    nutrient_values=None,  # Fallback to IFCT record
    edible_weight_g=100.0
)
```
- All 9 standard nutrients attempted from IFCT
- Missing IFCT values → tracked in `missing_nutrients`

### Mode 3: Empty Dict (No Calculation)
```python
IngredientNutritionInput(
    nutrient_values={},  # Explicitly empty
    edible_weight_g=100.0
)
```
- No nutrients calculated
- Status: `MISSING_NUTRIENTS`

---

## 4. Calculation Examples

### Example 1: 100g Rice (IFCT A001)
| Nutrient | IFCT (per 100g) | Weight | Calculated |
|----------|-----------------|--------|------------|
| Protein | 7.5 g | 100g | 7.5 g |
| Fat | 0.5 g | 100g | 0.5 g |
| Carbs | 78.0 g | 100g | 78.0 g |
| Energy | 350 kJ | 100g | 350 kJ / 83.65 kcal |

### Example 2: 50g Dal (IFCT B001)
| Nutrient | IFCT (per 100g) | Weight | Calculated |
|----------|-----------------|--------|------------|
| Protein | 22.0 g | 50g | 11.0 g |
| Fat | 1.5 g | 50g | 0.75 g |
| Carbs | 47.0 g | 50g | 23.5 g |
| Energy | 1200 kJ | 50g | 600 kJ / 143.4 kcal |

### Example 3: 85g Edible Spinach (100g raw × 0.85)
| Nutrient | IFCT (per 100g) | Edible Weight | Calculated |
|----------|-----------------|---------------|------------|
| Protein | 2.9 g | 85g | 2.465 g |
| Fat | 0.4 g | 85g | 0.34 g |
| Carbs | 2.0 g | 85g | 1.7 g |
| Energy | 120 kJ | 85g | 102 kJ / 24.4 kcal |

---

## 5. Missing Value Handling

### Principles
1. **Missing ≠ Zero** - Never impute zero for missing nutrients
2. **Explicit Tracking** - Every missing nutrient listed in `missing_nutrients`
3. **Provenance** - Source of each value documented
4. **No Silent Fallback** - Explicit `nutrient_values` controls calculation

### Behavior Matrix

| Input Mode | IFCT Has Value | Result |
|------------|----------------|--------|
| Explicit dict with value | N/A | Calculated |
| Explicit dict with `None` | N/A | In `missing_nutrients` |
| Explicit dict, key absent | N/A | Not calculated, not missing |
| `nutrient_values=None` | Yes | Calculated |
| `nutrient_values=None` | No | In `missing_nutrients` |
| `nutrient_values={}` | N/A | No calculation, `MISSING_NUTRIENTS` |

---

## 6. Calculation Status

| Status | Condition |
|--------|-----------|
| `COMPLETE` | All expected nutrients calculated |
| `PARTIAL` | Some expected nutrients missing |
| `MISSING_NUTRIENTS` | No nutrients calculated (empty input) |
| `MISSING_WEIGHT` | `edible_weight_g` is None/NaN |
| `MISSING_MAPPING` | Mapping not APPROVED |
| `INVALID_INPUT` | Invalid weight (≤0) or missing IFCT record |

---

## 7. Provenance Tracking

Each `IngredientNutritionOutput` includes:

```python
provenance = {
    'source': 'mapping:reviewer_id:timestamp;ifct:verified;weight:RESOLVED',
    'ifct_verification': 'verified',
    'weight_factor': 1.0,  # edible_weight_g / 100
    'validation': {
        'is_valid': True/False,
        'warnings': [...],
    }
}
```

---

## 8. IFCT Data Parsing

### String Format Handling
IFCT nutrients stored as strings, may contain:
- Plain numbers: `"350.0"`
- Mean ± SD: `"61.46±0.60"` → parsed as `61.46`

### Parser Logic (`_parse_nutrient()`)
```python
def _parse_nutrient(value):
    if value is None or pd.isna(value): return None
    if isinstance(value, (int, float)): return float(value)
    if isinstance(value, str):
        if '±' in value:
            return float(value.split('±')[0].strip())
        return float(value)
    return None
```

---

## 9. Precision & Rounding

- Calculations: Full float precision
- Output: Rounded to **4 decimal places**
- Energy kcal: Rounded to **2 decimal places**
- Display: As needed for reporting

---

## 10. Validation (Informational)

Validation runs but **does not block calculation**:

| Check | Severity | Action |
|-------|----------|--------|
| Range per 100g | ERROR | Logged in provenance |
| Atwater energy consistency | ERROR | Logged if >20% diff |
| Macronutrient sum | WARNING | Logged if >105g |
| Negative contributions | ERROR | Logged |

**Note:** Many real IFCT values fail Atwater check (IFCT uses different methods).

---

## 11. Files

| File | Purpose |
|------|---------|
| `src/nutrition/nutrient_calculator.py` | `NutrientCalculator`, `calculate_nutrient_contribution()` |
| `src/nutrition/nutrient_validation.py` | `NutrientValidator`, ranges, Atwater factors |
| `src/nutrition/nutrition_models.py` | `IngredientNutritionInput`, `IngredientNutritionOutput` |
| `tests/phase3/test_nutrition_calculator.py::TestNutrientCalculation` | 8 tests |

---

## 12. Testing

**Tests in `tests/phase3/test_nutrition_calculator.py::TestNutrientCalculation`:**
- `test_100g_ingredient` ✅
- `test_50g_ingredient` ✅
- `test_250g_ingredient` ✅
- `test_zero_weight_rejection` ✅
- `test_negative_weight_rejection` ✅
- `test_missing_nutrient` ✅
- `test_missing_ingredient_weight` ✅
- `test_kj_to_kcal_conversion` ✅
- `test_multiple_ingredient_aggregation` ✅

**All 9 calculation tests pass.**

---

*End of Nutrient Calculation Report*