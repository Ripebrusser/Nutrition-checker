# Stage 3.6: Edible Weight Handling Report

**Date:** 2026-11-19  
**Status:** Implementation Complete

---

## 1. Purpose

Convert ingredient weights from various sources (grams, household measures, counts) into **edible portion weights in grams** for nutrient calculation, using only defensible, documented conversions.

---

## 2. Weight Source Hierarchy

| Priority | Source | Conversion Method | Confidence |
|----------|--------|-------------------|------------|
| 1 | Resolved gram weight | Direct use (if `is_edible_weight=True`) | High |
| 2 | Resolved gram weight + edible portion factor | `gross_g × factor` | High |
| 3 | Household measure (cup, tbsp, etc.) | Ingredient-specific conversion table | Medium |
| 4 | Count (pieces) | Not implemented - requires piece weight | N/A |
| 5 | Approximate/range | Not converted - flagged unresolved | N/A |
| 6 | Unresolved | **Not converted to zero** - remains missing | N/A |

---

## 3. Gram Weight Coverage (Phase 2 Data)

| Status | Count | Percentage |
|--------|-------|------------|
| PARSED_EXACT | 54,903 | 60.4% |
| PARSED_APPROXIMATE | 29,980 | 33.0% |
| UNQUANTIFIED | 4,306 | 4.7% |
| RANGE_PARSED | 1,673 | 1.8% |
| **Total** | **90,862** | **100%** |

| Conversion Status | Count | Percentage |
|-------------------|-------|------------|
| RESOLVED (gram) | 1,299 | **1.4%** |
| RESOLVED_HOUSEHOLD | 1,337 | 1.5% |
| UNRESOLVED | 89,525 | 98.5% |
| **Total** | **90,862** | **100%** |

**Key Finding:** Only **1.4%** of ingredient records have resolved gram weights.

---

## 4. Household Measurement Conversions

### Phase 2 Table (68 entries)
| Ingredient | Unit | Equivalent (g) | Confidence | Verification |
|------------|------|----------------|------------|--------------|
| basmati rice (raw) | cup | 200 | 0.95 | verified |
| wheat flour (whole) | cup | 120 | 0.95 | verified |
| chickpea flour (besan) | cup | 110 | 0.95 | verified |
| sugar (white) | cup | 200 | 0.99 | verified |
| oil, vegetable | tbsp | 14 | 0.95 | verified |
| ... | ... | ... | ... | ... |

**Rules:**
- Ingredient-specific (no universal "1 cup = 240g")
- Confidence scores recorded
- Verification status tracked
- Only verified conversions used

### Stage 2.3 Table
Same data, copied for pipeline independence.

---

## 5. Edible Portion Factor Database

**Source:** IFCT 2017, USDA, validated Indian food composition data  
**Coverage:** ~180 / 528 IFCT codes (34%)

### Examples
| IFCT Code | Food | Edible % | Waste % | Description |
|-----------|------|----------|---------|-------------|
| A001 | Rice, raw | 100% | 0% | Fully edible |
| C001 | Spinach | 85% | 15% | Thick stems discarded |
| D001 | Potato | 80% | 20% | Peel removed |
| F001 | Mango, ripe | 75% | 25% | Skin + seed removed |
| H001 | Egg, hen | 88% | 12% | Shell removed |
| G003 | Groundnut | 50% | 50% | Shell removed |
| I001 | Turmeric powder | 100% | 0% | Fully used |
| J001 | Ghee | 100% | 0% | Fully edible |

### Categories
| Category | Typical Edible % | Examples |
|----------|------------------|----------|
| Dry cereals/pulses | 100% | Rice, wheat, dals |
| Leafy vegetables | 70-85% | Spinach, fenugreek, amaranth |
| Root vegetables | 75-85% | Potato, carrot, onion |
| Fruits | 55-85% | Mango (75%), banana (70%), orange (65%) |
| Nuts/seeds | 50-100% | Groundnut (50%), cashew (65%), sesame (100%) |
| Animal foods | 70-100% | Egg (88%), chicken (70%), fish (75%) |
| Spices/condiments | 100% | All powders, seeds |
| Fats/oils | 100% | Ghee, oils |
| Sugars | 100% | Sugar, jaggery, honey |

---

## 6. Conversion Logic

### EdiblePortionCalculator.calculate_edible_weight()

```python
def calculate_edible_weight(
    gross_weight_g: float,
    ifct_food_code: str,
    is_already_edible: bool = False
) -> Tuple[Optional[float], Optional[EdiblePortionInfo], str]:
```

**Behavior:**

| Input | Output |
|-------|--------|
| `is_already_edible=True` | Returns `gross_weight_g` unchanged |
| `is_already_edible=False` + factor exists | Returns `gross_weight_g × factor` |
| `is_already_edible=False` + no factor | Returns `None`, logs "No edible portion data" |
| `gross_weight_g ≤ 0` | Returns `None`, logs "Invalid gross weight" |

**Double-Conversion Prevention:**
```python
# First conversion: 100g raw spinach → 85g edible
weight1, _, _ = calc.calculate_edible_weight(100.0, "C001")
# weight1 = 85.0

# Second conversion on edible weight: 85g → 85g (no change)
weight2, _, _ = calc.calculate_edible_weight(weight1, "C001", is_already_edible=True)
# weight2 = 85.0 ✓
```

---

## 7. IngredientWeightInfo Contract

```python
IngredientWeightInfo(
    recipe_id: int,
    ingredient_record_id: str,
    original_ingredient: str,
    normalized_ingredient: str,
    quantity: Optional[float],           # Parsed quantity
    unit: Optional[str],                 # Parsed unit
    gram_weight: Optional[float],        # Resolved gram weight
    gram_weight_min: Optional[float],    # Range minimum
    gram_weight_max: Optional[float],    # Range maximum
    conversion_status: str,              # RESOLVED / RESOLVED_HOUSEHOLD / UNRESOLVED
    household_conversion_source: str,    # Source of conversion
    household_conversion_confidence: float,
    is_edible_weight: bool,              # True if already edible portion
    edible_portion_factor: Optional[float],  # Explicit factor (0-1)
    edible_portion_source: str,          # Source of factor
    preparation_state: str               # RAW, COOKED, NOT_SPECIFIED, etc.
)
```

---

## 8. Unresolved Weight Handling

| Scenario | Handling |
|----------|----------|
| `gram_weight = None` | `edible_weight_g = None` → `CalculationStatus.MISSING_WEIGHT` |
| `conversion_status = UNRESOLVED` | Not converted; ingredient excluded from calculation |
| Range (`gram_weight_min`, `gram_weight_max`) | Not converted; flagged for manual resolution |
| Approximate quantities | Not converted; requires human review |
| Count-based ("2 onions") | Not converted; requires piece weight database |

**Critical Rule:** Unresolved weights **never become zero**. They remain `None` and the ingredient is marked unresolved.

---

## 9. Current Limitations

1. **Gram weight coverage: 1.4%** - Severe bottleneck
2. **Household conversions: 68 ingredients only** - Limited coverage
3. **Edible portion DB: 34% of IFCT codes** - Many foods lack factors
4. **No piece weight database** - Count-based quantities unusable
5. **Preparation state: 88% NOT_SPECIFIED** - Cannot verify IFCT compatibility
6. **No range resolution** - Min/max ranges not automatically converted

---

## 10. Files

| File | Purpose |
|------|---------|
| `src/nutrition/edible_portion.py` | `EdiblePortionCalculator`, `EdiblePortionInfo`, hardcoded DB |
| `src/nutrition/nutrition_models.py` | `IngredientWeightInfo`, `EdiblePortionStatus` |
| `data/interim/phase2/household_measurements.csv` | Phase 2 conversions (68 entries) |
| `data/interim/phase3/stage2_3/household_measurements.csv` | Stage 2.3 copy |
| `tests/phase3/test_nutrition_calculator.py::TestEdiblePortion` | 4 tests |

---

## 11. Testing

**Tests in `tests/phase3/test_nutrition_calculator.py::TestEdiblePortion`:**
- `test_already_edible_weight` ✅
- `test_validated_edible_portion_conversion` ✅
- `test_missing_edible_portion_factor` ✅
- `test_double_conversion_prevention` ✅
- `test_known_codes` ✅

**All 5 edible portion tests pass.**

---

*End of Weight Handling Report*