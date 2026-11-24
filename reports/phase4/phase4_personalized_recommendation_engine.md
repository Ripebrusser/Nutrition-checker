# Phase 4: Personalized Recommendation Engine Report

**Date:** 2026-11-19  
**Status:** Implementation Complete

---

## 1. Overview

The Personalized Recommendation Engine (`src/personalization/personalized_recommender.py`) integrates:
- Phase 5: Content-based recommender (TF-IDF + metadata)
- Phase 4: Dietary constraints, nutrition targets, user profiles
- Phase 3: Recipe nutrition profiles

---

## 2. Architecture

### 2.1 Core Components

| Class | Purpose |
|-------|---------|
| `PersonalizedRecommender` | Main orchestrator |
| `PersonalizedRecommenderConfig` | Weight configuration |
| `PersonalizedRecommendationResult` | Enhanced recommendation with personalization data |

### 2.2 Configuration
```python
@dataclass
class PersonalizedRecommenderConfig:
    # Base recommender weights
    ingredient_weight: float = 0.4
    cuisine_weight: float = 0.3
    course_weight: float = 0.15
    diet_weight: float = 0.15
    
    # Personalization weights
    nutrition_match_weight: float = 0.2
    dietary_compliance_weight: float = 0.3
    preference_weight: float = 0.2
    diversity_weight: float = 0.1
    
    # Filters
    require_dietary_compliance: bool = True
    min_nutrition_completeness: float = 0.0
    exclude_unverified_dietary: bool = True
    max_results: int = 10
    
    # Meal slot awareness
    meal_slot_aware: bool = True
    meal_slot_weights: Dict[str, float] = {...}
```

### 2.3 Enhanced Recommendation Result
```python
@dataclass
class PersonalizedRecommendationResult:
    recipe_id: int
    recipe_name: str
    similarity_score: float
    cuisine: str
    course: str
    diet_labels: List[str]
    shared_ingredients: List[str]
    explanation: str
    component_scores: Dict[str, float]
    
    # Personalization additions
    dietary_evaluation: Optional[Dict]
    nutrition_match_score: Optional[float]
    per_serving_nutrients: Optional[Dict[str, float]]
    nutrition_completeness: Optional[float]
    meets_nutritional_targets: Optional[Dict[str, bool]]
    personalization_notes: List[str]
```

---

## 3. Recommendation Process

### 3.1 Pipeline
```python
def recommend(user_profile, nutrition_targets, query_recipe_id=None, 
              query_ingredients=None, meal_slot=None, k=10, filters=None):
    1. Get base recommendations from Phase 5 recommender
       (3×k for filtering headroom)
    
    2. Apply personalization:
       a. Dietary constraint evaluation (HARD filter)
       b. Nutrition completeness filter
       c. Nutrition match scoring
       d. Meal slot appropriateness
       e. Preference matching
    
    3. Sort by combined score
    
    4. Return top-k
```

### 3.2 Base Recommendation Sources
| Source | Method | Use Case |
|--------|--------|----------|
| Similar recipe | `recommender.recommend(query_recipe_id, k, filters)` | "More like this" |
| Ingredient-based | `recommender.recommend_by_ingredients(ingredients, k, filters)` | "What can I make with..." |
| Diverse | `_get_diverse_recommendations(k, filters)` | Cold start / exploration |

---

## 4. Personalization Filters

### 4.1 Dietary Compliance (HARD Filter)
```python
if config.require_dietary_compliance:
    dietary_eval = _evaluate_dietary(profile, user_profile)
    if dietary_eval.overall_result == FAIL:
        continue  # Skip - hard filter
    if dietary_eval.overall_result == UNVERIFIED and config.exclude_unverified_dietary:
        continue  # Skip unverified
```

### 4.2 Nutrition Completeness Filter
```python
if config.min_nutrition_completeness > 0:
    if profile.nutrition_status == UNAVAILABLE:
        continue
    completeness = max(profile.nutrient_completeness.values())
    if completeness < config.min_nutrition_completeness:
        continue
```

### 4.3 Nutrition Match Scoring
```python
def _calculate_nutrition_match(profile, nutrition_targets):
    # Compare per-serving nutrients to targets
    # Energy, protein, carb, fat each scored 0-1
    # Returns average match score
```

### 4.4 Target Achievement Check
```python
def _check_targets(profile, nutrition_targets):
    # Within 20% of target = "meets"
    # Returns dict: {"meets_energy": True, "meets_protein": False, ...}
```

### 4.5 Meal Slot Appropriateness
```python
slot_courses = {
    "BREAKFAST": ["breakfast", "snack", "beverage"],
    "LUNCH": ["main course", "lunch", "rice", "bread", "curry", "dal"],
    "DINNER": ["main course", "dinner", "rice", "bread", "curry", "dal"],
    "MORNING_SNACK": ["snack", "beverage", "dessert"],
    "EVENING_SNACK": ["snack", "beverage", "dessert", "street food"],
}
```

### 4.6 Preference Matching
```python
def _preference_match_score(profile, user_profile):
    # Cuisine preference match
    if user_profile.dietary_profile.cuisine_preferences:
        if profile.cuisine in prefs: score += 1.0
    return score / count
```

---

## 5. Combined Scoring

```python
def _combined_score(rec):
    score = 0.0
    
    # Base similarity (30%)
    score += rec.similarity_score * 0.3
    
    # Nutrition match (25%)
    if rec.nutrition_match_score:
        score += rec.nutrition_match_score * 0.25
    
    # Dietary compliance (25% - binary but critical)
    if rec.dietary_evaluation:
        if dietary_result == PASS:
            score += 0.25
        else:
            score -= 1.0  # Heavy penalty
    
    # Meal slot (10%)
    if "meal_slot" in rec.component_scores:
        score += rec.component_scores["meal_slot"] * 0.1
    
    # Preference (10%)
    if "preference" in rec.component_scores:
        score += rec.component_scores["preference"] * 0.1
    
    return score
```

---

## 6. Meal-Slot Aware Recommendations

### 6.1 recommend_for_meal_slot()
```python
def recommend_for_meal_slot(user_profile, nutrition_targets, meal_slot, k=5):
    slot_courses = _get_courses_for_slot(meal_slot)
    
    all_recs = []
    for course in slot_courses:
        recs = recommend(..., filters={"course": course})
        all_recs.extend(recs)
    
    # Deduplicate, sort, return top-k
```

### 6.2 Meal Energy Distribution
| MealFrequency | Distribution |
|---------------|--------------|
| 3 meals | B: 30%, L: 40%, D: 30% |
| 4 meals | B: 25%, L: 35%, S: 15%, D: 25% |
| 5 meals | B: 25%, M: 10%, L: 35%, E: 10%, D: 20% |
| 6 meals | B: 20%, M: 10%, L: 30%, A: 10%, E: 10%, D: 20% |

---

## 7. Integration with Phase 5 Recommender

### 7.1 ContentBasedRecipeRecommender Interface
```python
base_recommender = ContentBasedRecipeRecommender()
base_recommender.fit(
    recipe_ingredients={rid: [ingredients]},
    recipe_metadata={rid: {cuisine, course, diet_labels, ...}}
)
```

### 7.2 Feature Weights (Phase 5 Default)
| Component | Weight |
|-----------|--------|
| Ingredient Jaccard | 0.40 |
| Cuisine Match | 0.30 |
| Course Match | 0.15 |
| Diet Overlap | 0.15 |

### 7.3 Recommendation Result Structure
```python
RecommendationResult:
    recipe_id, recipe_name, similarity_score
    cuisine, course, diet_labels
    shared_ingredients
    explanation
    component_scores: {ingredient_jaccard, cuisine_match, course_match, diet_overlap}
```

---

## 8. Factory Function
```python
def create_personalized_recommender(
    recipe_profile_collection: RecipeProfileCollection,
    base_recommender: ContentBasedRecipeRecommender,
    dietary_engine: DietaryConstraintEngine,
    config: Optional[PersonalizedRecommenderConfig] = None
) -> PersonalizedRecommender
```

---

## 8. Limitations

1. **No collaborative filtering** - No user interaction history
2. **Proxy nutrition matching** - Based on per-serving nutrients vs targets
3. **Binary dietary compliance** - No partial compliance scoring
4. **Static weights** - Not learned from user feedback
5. **Meal slot courses heuristic** - Based on course labels, not time-of-day
6. **No portion size optimization** - Servings fixed at 1.0

---

## 9. Files

| File | Purpose |
|------|---------|
| `src/personalization/personalized_recommender.py` | Core engine |
| `tests/phase4/test_personalization.py` | Tests (via integration) |

---

*End of Personalized Recommendation Engine Report*