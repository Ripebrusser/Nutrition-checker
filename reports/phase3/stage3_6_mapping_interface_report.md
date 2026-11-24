# Stage 3.6: Verified Ingredient Mapping Interface Report

**Date:** 2026-11-19  
**Status:** Implementation Complete

---

## 1. Purpose

The mapping interface enforces a **strict boundary** between candidate mappings (Stage 2.3 output) and approved mappings (human-reviewed decisions). Only explicitly approved mappings can enter the nutrition calculation engine.

---

## 2. Architecture

### 2.1 ApprovedMappingStore
**Location:** `src/nutrition/ingredient_mapping.py`

Stores only `MappingStatus.APPROVED` mappings with:
- Composite key: `(recipe_id, ingredient_record_id)`
- Duplicate prevention: Same key + different IFCT code → `ValueError`
- Indexes: by recipe, by IFCT code
- Decision log: All review decisions preserved (APPROVE/REJECT/AMBIGUOUS/DEFER)

### 2.2 StrictMappingInterface
**Location:** `src/nutrition/ingredient_mapping.py`

Gateway between mapping store and calculator:
- `get_approved_mapping(recipe_id, ingredient_record_id)` → `ApprovedMapping` or `None`
- `create_nutrition_input(recipe_id, ingredient_record_id, weight_info)` → `IngredientNutritionInput` or `None`
- `validate_preparation_compatibility(prep_state, ifct_record)` → `(bool, message)`

### 2.3 MappingReviewRecord
**Location:** `src/nutrition/ingredient_mapping.py`

Persistence schema for review decisions:
```python
MappingReviewRecord(
    recipe_id, ingredient_record_id, original_ingredient, normalized_ingredient,
    ifct_food_code, ifct_food_name, ifct_food_group,
    decision: MappingDecision,  # APPROVE/REJECT/AMBIGUOUS/DEFER
    reviewer_id, timestamp, confidence, evidence,
    preparation_state, notes
)
```

JSONL persistence via `save_approved_mappings_to_jsonl()` / `load_approved_mappings_from_jsonl()`.

---

## 3. Enforcement Rules

| Rule | Implementation |
|------|----------------|
| Only APPROVED mappings usable | `ApprovedMappingStore.add_mapping()` raises `ValueError` if status ≠ APPROVED |
| Rejected never used | `StrictMappingInterface.create_nutrition_input()` returns `None` for non-APPROVED |
| Ambiguous never auto-used | Same as rejected - only APPROVED in store |
| Candidates ≠ probabilities | `similarity_score` stored but never used as probability |
| Preparation compatibility | `validate_preparation_compatibility()` checks prep state vs IFCT raw basis |
| IFCT raw-food basis | Cooked preparations flagged as incompatible |
| Duplicate prevention | Same `(recipe_id, ingredient_record_id)` with different IFCT code → error |
| Provenance preserved | Every mapping tracks reviewer, timestamp, evidence, confidence |

---

## 4. Current Mapping Status (from Preflight)

### Stage 2.3 Candidate Mappings
| Metric | Value |
|--------|-------|
| Total candidates | 119,474 |
| Match methods | TOKEN_SIMILARITY (100,658), EXACT (7,583), TOKEN_EQUIVALENT (6,198), SYNONYM (5,035) |
| Auto-accepted (EXACT + FRESH + sim=1.0) | 4 |
| Requires review | 119,470 (99.99%) |
| Preparation states | NOT_SPECIFIED (80,502), POWDERED (18,670), DRIED (12,091), FRESH (4,716) |

### Approved Mappings
| Metric | Value |
|--------|-------|
| Currently approved | **0** (awaiting human review) |
| Review app available | Yes (Stage 3.4: `app/ingredient_review_app.py`) |
| Calibration set | 5 units (`reports/phase3/stage3_4_calibration_set.md`) |

---

## 5. Interface Behavior Examples

### Example 1: Approved Mapping Used
```python
mapping = ApprovedMapping(
    recipe_id=1, ingredient_record_id="ing_1",
    ifct_food_code="A001", mapping_status=MappingStatus.APPROVED, ...
)
approved_store.add_mapping(mapping)

input_data = mapping_interface.create_nutrition_input(1, "ing_1", weight_info)
# Returns IngredientNutritionInput with IFCT data
```

### Example 2: Rejected Mapping Ignored
```python
# No mapping added for this ingredient
input_data = mapping_interface.create_nutrition_input(1, "ing_999", weight_info)
# Returns None - no calculation performed
```

### Example 3: Duplicate Prevention
```python
mapping1 = ApprovedMapping(..., ifct_food_code="A001", ...)
mapping2 = ApprovedMapping(..., ifct_food_code="B001", ...)  # Different code!
approved_store.add_mapping(mapping1)
approved_store.add_mapping(mapping2)  # Raises ValueError
```

### Example 4: Preparation State Validation
```python
# IFCT A001 = Rice, raw
compatible, msg = mapping_interface.validate_preparation_compatibility("COOKED", ifct_record)
# compatible=False, msg="Preparation state 'COOKED' requires cooked IFCT entry (not available)"

compatible, msg = mapping_interface.validate_preparation_compatibility("RAW", ifct_record)
# compatible=True, msg="Preparation state compatible with IFCT raw food basis"
```

---

## 6. Integration with Review App (Stage 3.4)

The review app (`app/ingredient_review_app.py`) produces decisions that feed this interface:

1. Reviewer sees candidate mappings with evidence
2. Reviewer decides: APPROVE / REJECT / AMBIGUOUS / DEFER
3. Decision saved to JSONL via `MappingReviewRecord`
4. `ApprovedMappingStore.load_approved_mappings_from_jsonl()` loads approved decisions
5. Nutrition engine uses `StrictMappingInterface` for calculation

**Schema Compatibility:** Stage 3.4 v1.1 schema matches `MappingReviewRecord` fields.

---

## 7. Zero-Mapping Operation

The engine **operates safely with zero approved mappings**:

```python
# No mappings in store
mapping_interface = StrictMappingInterface(empty_store, ifct_data)

# All create_nutrition_input() calls return None
# aggregate_recipe() returns NO_MAPPED_INGREDIENTS
# Coverage report shows 0% mapping coverage
# No errors, no fabricated data
```

---

## 8. Files

| File | Purpose |
|------|---------|
| `src/nutrition/ingredient_mapping.py` | Core implementation |
| `src/nutrition/nutrition_models.py` | `ApprovedMapping`, `MappingStatus`, `MappingDecision`, `MappingReviewRecord` |
| `app/ingredient_review_app.py` | Review interface (Stage 3.4) |
| `data/processed/phase3/approved_mappings.jsonl` | Persistence target (not yet created) |

---

## 9. Testing

**Tests in `tests/phase3/test_nutrition_calculator.py::TestMappingInterface`:**
- `test_approved_mapping_used` ✅
- `test_rejected_mapping_not_used` ✅
- `test_ambiguous_mapping_not_used` ✅
- `test_unmatched_ingredient` ✅
- `test_missing_food_code` ✅
- `test_preparation_state_mismatch` ✅
- `test_duplicate_mapping_same_code` ✅
- `test_duplicate_mapping_different_code` ✅
- `test_invalid_ifct_code` ✅

**All 8 mapping tests pass.**

---

*End of Mapping Interface Report*