# Phase 4: Recipe Feature Integration Report

**Date:** 2026-11-19  
**Status:** Implementation Complete

---

## 1. Overview

The Recipe Feature Integration module (`src/personalization/recipe_profile.py`) creates unified recipe profiles that integrate:
- Phase 1: Recipe metadata (cuisine, course, diet labels)
- Phase 2: Normalized ingredient lists
- Phase 3: Nutrition calculations (when approved mappings exist)
- Phase 5: Recommendation features (TF-IDF, metadata)

---

## 2. Architecture

### 2.1 Core Data Models

```python
class NutritionCompleteness(Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    UNAVAILABLE = "UNAVAILABLE"
    NO_MAPPED_INGREDIENTS = "NO_MAPPED_INGREDIENTS"
```

```python
@dataclass
class RecipeNutritionProfile:
    recipe_id: int
    recipe_name: str
    cuisine: str
    course: str
    diet_labels: List[str]
    prep_time_min: int
    cook_time_min: int
    total_time_min: int
    servings: int
    
    ingredients: List[str]
    ingredient_count: int
    
    # Nutrition (from Phase 3 engine)
    nutrition_status: NutritionCompleteness
    total_nutrients: Dict[str, float]
    per_serving_nutrients: Dict[str, float]
    nutrient_completeness: Dict[str, float]
    mapping_coverage: float
    weight_coverage: float
    mapped_ingredient_count: int
    total_ingredient_count: int
    missing_nutrients: List[str]
    
    # Dietary classification
    diet_classification: Dict[str, Any]
    
    # Provenance
    nutrition_provenance: Dict[str, Any]
```

### 2.2 Collection with Indexes
```python
@dataclass
class RecipeProfileCollection:
    profiles: Dict[int, RecipeNutritionProfile]
    cuisine_index: Dict[str, Set[int]]
    course_index: Dict[str, Set[int]]
    diet_label_index: Dict[str, Set[int]]
    nutrition_status_index: Dict[NutritionCompleteness, Set[int]]
    
    # Filter methods
    def filter(self, **criteria) -> List[RecipeNutritionProfile]
```

---

## 3. RecipeProfileBuilder (Main Integration Class)

### 3.1 Dependencies
```python
class RecipeProfileBuilder:
    def __init__(
        self,
        nutrition_calculator: Optional[NutrientCalculator] = None,
        recipe_aggregator: Optional[RecipeAggregator] = None,
        mapping_interface: Optional[StrictMappingInterface] = None,
        dietary_engine: Optional[DietaryConstraintEngine] = None,
        preprocessor: Optional[RecipePreprocessor] = None
    )
```

### 3.2 Data Loading
```python
def load_data(self):
    # Loads via RecipePreprocessor:
    self._recipe_ingredients = preprocessor.extract_recipe_ingredients()
    self._recipe_metadata = preprocessor.extract_recipe_metadata()
    self._parsed_ingredients_df = preprocessor._parsed_ingredients_df
    self._ifct_df = pd.read_parquet(ifct_path)
```

### 3.3 Profile Building
```python
def build_recipe_profile(self, recipe_id: int) -> RecipeNutritionProfile:
    # 1. Get metadata + ingredients
    # 2. Dietary classification
    # 3. Nutrition calculation (if aggregator available)
    #    - Creates IngredientWeightInfo from parsed data
    #    - Runs RecipeAggregator.aggregate_recipe()
    #    - Populates nutrition fields
```

### 3.4 Nutrition Population
```python
def _populate_nutrition(self, profile, nutrition_result):
    # Maps RecipeCalculationStatus → NutritionCompleteness
    # Copies total_nutrients, nutrient_completeness
    # Calculates per-serving nutrients
    # Tracks missing nutrients
```

### 3.5 Batch Building
```python
def build_all_profiles(self, recipe_ids=None) -> RecipeProfileCollection
```

---

## 4. Data Sources Integration

### 4.1 Phase 1 (Recipe Metadata)
| Source | Fields |
|--------|--------|
| `data/processed/recipes.parquet` | recipe_id, recipe_name_en, cuisine, course, diet_labels, prep/cook times, servings, recipe_type |

### 4.2 Phase 2 (Ingredients)
| Source | Fields |
|--------|--------|
| `data/interim/phase2/parsed_recipe_ingredients.parquet` | recipe_id, ingredient_name, gram_weight, conversion_status, preparation, etc. |

### 4.3 Phase 3 (Nutrition)
| Source | Purpose |
|--------|---------|
| `data/interim/ifct_final_candidate/ifct_table1_candidate.parquet` | 528 IFCT foods, 9 nutrients |
| `data/processed/phase3/approved_mappings.jsonl` | Approved ingredient→IFCT mappings |

### 4.4 Phase 5 (Recommendation Features)
| Source | Purpose |
|--------|---------|
| `src/recommendation/recipe_preprocessing.py` | Ingredient normalization, TF-IDF features |

---

## 5. Nutrition Calculation Flow

```
Phase 2 Parsed Ingredients (90,862 records)
         │
         ▼
Create IngredientWeightInfo per recipe
         │
         ▼
StrictMappingInterface.create_nutrition_input()
(Only uses APPROVED mappings)
         │
         ▼
NutrientCalculator.calculate_ingredient_nutrition()
(Formula: nutrient = IFCT_per_100g × edible_weight_g / 100)
         │
         ▼
RecipeAggregator.aggregate_recipe()
(Sums valid ingredients, tracks completeness)
         │
         ▼
RecipeNutritionProfile populated
```

---

## 6. Current Limitations (Critical)

### 6.1 Zero Approved Mappings
- **Result:** All recipes return `NutritionCompleteness.UNAVAILABLE`
- **Reason:** No human-reviewed mappings exist yet
- **Engine behavior:** Correctly returns `NO_MAPPED_INGREDIENTS`

### 6.2 Weight Coverage
| Status | Count | % |
|--------|-------|---|
| RESOLVED (gram) | 1,299 | 1.4% |
| RESOLVED_HOUSEHOLD | 1,337 | 1.5% |
| UNRESOLVED | 89,525 | 98.5% |

### 6.3 IFCT Nutrient Gaps
| Nutrient | Available | Missing | Coverage |
|----------|-----------|---------|----------|
| protein, fat, energy, moisture, ash | 528 | 0 | 100% |
| fibre_total, fibre_insoluble, fibre_soluble, carb_available | 306 | 222 | 58% |

### 6.5 Edible Portion Database
- Coverage: ~180/528 IFCT codes (34%)

---

## 6. Recipe Profile Features for Recommendation

### 6.1 get_recipe_features_for_recommendation()
Returns formatted data for Phase 5 recommender:
```python
{
    "recipe_ingredients": {recipe_id: [ingredients]},
    "recipe_metadata": {recipe_id: {cuisine, course, diet_labels, ...}}
}
```

### 6.2 Dietary Evaluation Integration
```python
def evaluate_recipe_dietary(self, recipe_id, user_preference, user_allergies, user_exclusions)
    → RecipeDietaryEvaluation
```

---

## 7. Summary Statistics

### 7.1 get_recipe_nutrition_summary()
```python
{
    "total_recipes": 6865,
    "recipes_with_nutrition": 0,  # Currently 0
    "by_nutrition_status": {...},
    "cuisines": 75,
    "courses": 10,
    "diet_labels": 20,
}
```

---

## 8. Files

| File | Purpose |
|------|---------|
| `src/personalization/recipe_profile.py` | Core integration module |
| `tests/phase4/test_personalization.py` | Integration tests (profile building, dietary eval) |

---

## 9. Key Design Decisions

1. **Strict mapping interface** - Only APPROVED mappings used; never candidates
2. **Missing nutrition tracked** - Never zero-imputed; `missing_nutrients` list maintained
3. **Per-serving calculation** - Total nutrients divided by servings
4. **Provenance preserved** - Every calculation traces to mapping decision + IFCT + weight source
5. **Dietary classification at build time** - Cached in profile for fast filtering
5. **Graceful degradation** - Engine works with zero mappings, returns UNAVAILABLE

---

## 10. Files

| File | Purpose |
|------|---------|
| `src/personalization/recipe_profile.py` | Core integration module |
| `tests/phase4/test_personalization.py` | Integration tests |

---

*End of Recipe Feature Integration Report*