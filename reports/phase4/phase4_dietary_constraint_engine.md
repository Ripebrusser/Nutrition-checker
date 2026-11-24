# Phase 4: Dietary Constraint Engine Report

**Date:** 2026-11-19  
**Status:** Implementation Complete

---

## 1. Overview

The Dietary Constraint Engine (`src/personalization/dietary_constraints.py`) evaluates recipes against user dietary preferences, allergies, ingredient exclusions, and religious restrictions. It provides traceable PASS/FAIL/UNVERIFIED results with detailed evidence.

---

## 2. Architecture

### 2.1 Core Components

| Class | Purpose |
|-------|---------|
| `DietClassifier` | Classifies recipes into dietary categories (VEGAN, VEGETARIAN, EGGETARIAN, NON_VEGETARIAN, JAIN) |
| `AllergenFilter` | Checks recipes against user allergies |
| `IngredientExclusionFilter` | Filters recipes containing excluded ingredients |
| `DietaryPreferenceFilter` | Matches recipes to user dietary preference |
| `JainComplianceFilter` | Checks Jain dietary restrictions |
| `DietaryConstraintEngine` | Main orchestrator combining all filters |

### 2.2 Result Types

```python
class ConstraintResult(Enum):
    PASS = "PASS"           # Recipe passes constraint
    FAIL = "FAIL"           # Recipe fails constraint (hard block)
    UNVERIFIED = "UNVERIFIED"  # Cannot verify (missing ingredient info)
```

### 2.3 Evaluation Result
```python
@dataclass
class RecipeDietaryEvaluation:
    recipe_id: int
    recipe_name: str
    overall_result: ConstraintResult
    evaluations: List[ConstraintEvaluation]
    hard_fails: List[ConstraintEvaluation]
    soft_fails: List[ConstraintEvaluation]
    unverified: List[ConstraintEvaluation]
    passes: List[ConstraintEvaluation]
    
    @property
    def is_suitable(self) -> bool:
        return len(self.hard_fails) == 0
```

---

## 2. Ingredient Taxonomy

### 3.1 Non-Vegetarian Ingredients
| Category | Examples |
|----------|----------|
| Meats | chicken, mutton, lamb, goat, beef, pork, venison, duck, quail, turkey, rabbit |
| Organ meats | liver, kidney, heart, brain, tongue, tripe |
| Seafood | fish, prawn, shrimp, crab, lobster, mussel, clam, oyster, scallop, squid, octopus |
| Processed | bacon, ham, salami, sausage, pepperoni, chorizo |

**Eggs handled separately** for eggetarian classification.

### 3.2 Vegetarian Non-Vegan (Dairy)
| Ingredients |
|-------------|
| milk, curd, yogurt, yoghurt, butter, ghee, cream, cheese, paneer, khoya, mawa, condensed milk, whey, casein, lassi, buttermilk, dahi |

### 3.3 Egg Ingredients (Eggetarian)
| Ingredients |
|-------------|
| egg, eggs, egg white, egg yolk, omelette, mayonnaise |

### 3.4 Jain-Restricted Ingredients
| Category | Examples |
|----------|----------|
| Root vegetables | onion, garlic, potato, carrot, radish, beetroot, ginger, turmeric, yam, colocasia, turnip, parsnip, sweet potato, taro, cassava |
| Fermented | yeast, vinegar, alcohol, wine, beer, fermented |
| Others | mushroom, honey, gelatin, fig, pomegranate |

### 3.5 Allergens (15 Categories)
| Allergen | Example Ingredients |
|----------|---------------------|
| peanut | peanut, groundnut, peanut butter, peanut oil |
| tree_nut | almond, cashew, walnut, pistachio, hazelnut, macadamia, pecan, brazil nut, pine nut |
| milk | milk, curd, yogurt, butter, ghee, cream, cheese, paneer, khoya, whey, casein, lassi |
| egg | egg, eggs, egg white, egg yolk, mayonnaise, omelette |
| wheat | wheat, atta, maida, flour, bread, roti, chapati, naan, paratha, puri, biscuit, cookie, cake, semolina, suji, rava, sevai, vermicelli, pasta, noodles |
| soy | soy, soya, tofu, tempeh, soy sauce, soy milk, edamame |
| fish | fish, salmon, tuna, mackerel, sardine, anchovy |
| shellfish | prawn, shrimp, crab, lobster, mussel, clam, oyster, scallop |
| sesame | sesame, til, tahini, sesame oil, gingelly oil |
| mustard | mustard, sarson, mustard seeds, mustard oil |
| celery | celery, ajwain, celery seed |

---

## 4. Classification Logic

### 4.1 Recipe Diet Type Determination
```python
if non_veg_found:
    diet_type = "NON_VEGETARIAN"
elif egg_found and not dairy_found:
    diet_type = "EGGETARIAN"
elif dairy_found:
    diet_type = "VEGETARIAN"
else:
    diet_type = "VEGAN"
```

**Priority:** Non-veg > Eggetarian > Vegetarian > Vegan

### 4.2 Jain Compliance
```python
jain_compliant = len(jain_restricted_found) == 0
```

### 4.3 Allergen Matching
- Exact match in ingredient set
- Partial match (substring in compound ingredients)
- Case-insensitive

### 4.4 Exclusion Matching
- Exact match
- Substring in either direction (exclusion in ingredient OR ingredient in exclusion)

---

## 5. Constraint Evaluation

### 5.1 Evaluation Types

| Constraint | Type | Severity | Description |
|------------|------|----------|-------------|
| ALLERGEN | Hard block | HARD | User allergies |
| EXCLUSION | Configurable | HARD/SOFT | User ingredient exclusions |
| DIETARY_PREFERENCE | Hard block | HARD | Veg/non-veg/jain/omnivore |
| JAIN_COMPLIANCE | Hard block | HARD | Jain dietary rules |

### 5.2 Evaluation Result
```python
@dataclass
class ConstraintEvaluation:
    constraint_type: str
    constraint_name: str
    result: ConstraintResult  # PASS/FAIL/UNVERIFIED
    reason: str
    matched_items: List[str]
    severity: str  # HARD, SOFT, ADVISORY
```

### 5.3 Overall Result Logic
```python
if hard_fails:
    overall = FAIL
elif unverified:
    overall = UNVERIFIED
else:
    overall = PASS
```

---

## 6. DietaryConstraintEngine (Main Interface)

### 6.1 Constructor
```python
engine = DietaryConstraintEngine()
# Initializes all sub-filters
```

### 6.2 evaluate_recipe()
```python
engine.evaluate_recipe(
    recipe_id=1,
    recipe_name="Dal Rice",
    ingredients=["rice", "dal", "vegetables", "ghee"],
    user_preference="VEGETARIAN",
    user_allergies=["peanut"],
    user_exclusions=["onion"],
    check_jain=False,
    exclusion_severity="HARD"
) -> RecipeDietaryEvaluation
```

### 6.3 filter_suitable()
```python
engine.filter_suitable(
    recipes=[{"recipe_id": 1, "recipe_name": "...", "ingredients": [...]}],
    user_preference="VEGETARIAN",
    user_allergies=["peanut"],
    user_exclusions=["onion"],
    check_jain=False,
    include_unverified=False
) -> List[Dict]  # Only PASS (and optionally UNVERIFIED)
```

### 6.4 evaluate_batch()
```python
engine.evaluate_batch(
    recipes=[...],
    user_preference="VEGETARIAN",
    user_allergies=["peanut"],
    user_exclusions=["onion"],
    check_jain=False
) -> List[RecipeDietaryEvaluation]
```

---

## 7. Convenience Functions

```python
evaluate_recipe_dietary(
    recipe_id=1,
    recipe_name="Test",
    ingredients=["rice", "dal"],
    user_preference="VEGETARIAN",
    user_allergies=["peanut"],
    user_exclusions=["onion"],
    check_jain=False
) -> RecipeDietaryEvaluation

filter_recipes_by_diet(
    recipes=[...],
    user_preference="VEGETARIAN",
    user_allergies=["peanut"],
    user_exclusions=["onion"],
    check_jain=False
) -> List[Dict]
```

---

## 8. Decision Logic Examples

### 8.1 Vegetarian User, Vegetarian Recipe
```python
ingredients = ["rice", "dal", "vegetables", "ghee"]
preference = "VEGETARIAN"
# Result: PASS (dairy allowed for vegetarian)
```

### 8.2 Vegetarian User, Non-Veg Recipe
```python
ingredients = ["chicken", "rice"]
preference = "VEGETARIAN"
# Result: FAIL (chicken is non-veg)
```

### 8.3 Vegan User, Vegetarian Recipe
```python
ingredients = ["rice", "dal", "vegetables", "ghee"]
preference = "VEGAN"
# Result: FAIL (ghee is dairy)
```

### 8.4 Jain User, Recipe with Onion
```python
ingredients = ["onion", "rice", "dal"]
check_jain = True
# Result: FAIL (onion is Jain-restricted)
```

### 8.5 Allergy Check
```python
ingredients = ["peanut", "rice"]
allergies = ["peanut"]
# Result: FAIL (peanut detected)
```

### 8.6 Exclusion Check
```python
ingredients = ["onion", "garlic", "rice"]
exclusions = ["onion"]
# Result: FAIL (onion excluded)
```

---

## 9. Safety Rules

1. **Hard restrictions never overridden** by recommendation scores
2. **Missing ingredient info ≠ absence** of allergen (returns UNVERIFIED)
3. **Unverified recipes marked** as UNVERIFIED, not PASS
4. **No inference from recipe titles** - only ingredient list used
5. **Jain ≠ Vegetarian** - Jain is stricter subset

---

## 10. Testing

### 10.1 Unit Tests (`tests/phase4/test_personalization.py::TestDietaryConstraints`)
| Test | Status |
|------|--------|
| test_diet_classifier_vegan | ✅ |
| test_diet_classifier_vegetarian | ✅ |
| test_diet_classifier_non_veg | ✅ |
| test_diet_classifier_eggetarian | ✅ |
| test_allergen_filter | ✅ |
| test_allergen_filter_pass | ✅ |
| test_ingredient_exclusion | ✅ |
| test_dietary_preference_filter | ✅ |
| test_dietary_preference_pass | ✅ |
| test_jain_compliance | ✅ |
| test_dietary_constraint_engine | ✅ |

**All 12 tests pass.**

---

## 11. Limitations

1. **Ingredient normalization required** - Assumes ingredients pre-normalized
2. **No quantity consideration** - Trace amounts treated same as main ingredients
3. **No cross-contamination model** - Only explicit ingredients checked
4. **Static ingredient lists** - May miss regional variations
5. **No compound ingredient decomposition** - "garam masala" treated as single token
6. **Jain list not exhaustive** - Based on common restrictions, traditions vary
7. **Allergen lists may need localization** - Indian-specific allergens may differ

---

## 12. Files

| File | Purpose |
|------|---------|
| `src/personalization/dietary_constraints.py` | Core engine + filters |
| `tests/phase4/test_personalization.py::TestDietaryConstraints` | 11 unit tests |

---

*End of Dietary Constraint Engine Report*