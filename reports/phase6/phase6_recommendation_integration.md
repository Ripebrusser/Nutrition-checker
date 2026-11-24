# Phase 6: Recommendation Integration Report

**Date:** 2026-11-19  
**Status:** Implementation Complete

---

## 1. Overview

The Personalized Recommendation Engine integrates Phase 5's content-based TF-IDF recommender with Phase 4's personalization layer (dietary constraints, nutrition targets, user preferences).

---

## 2. Architecture

### 2.1 Component Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                   PersonalizedRecommender                    │
├─────────────────────────────────────────────────────────────┤
│  Base: ContentBasedRecipeRecommender (Phase 5)              │
│  + DietaryConstraintEngine (Phase 4)                        │
│  + NutritionTargetCalculator (Phase 4)                      │
│  + RecipeProfileCollection (Phase 4 + 3)                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Recommendation    │
                    │ Pipeline          │
                    └───────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │  Base    │  │ Dietary  │  │ Nutrition│
        │ Score    │  │ Filter   │  │ Match    │
        └──────────┘  └──────────┘  └──────────┘
              │           │           │
              └───────────┼───────────┘
                          ▼
                   ┌──────────────┐
                   │ Combined     │
                   │ Score        │
                   └──────────────┘
```

---

## 2.2 Base Recommender (Phase 5)

### 2.2.1 ContentBasedRecipeRecommender
```python
class ContentBasedRecipeRecommender:
    def fit(recipe_ingredients, recipe_metadata):
        # TF-IDF on ingredients (2000 features, n-gram 1-2)
        # One-hot: cuisine, course, diet_labels
    
    def recommend(query_recipe_id, k=10, filters=None):
        # Combined score: 0.4*ingredient + 0.3*cuisine + 0.15*course + 0.15*diet
    
    def recommend_by_ingredients(ingredients, k=10, filters=None):
        # Jaccard similarity on ingredient sets
```

### 2.2.2 Default Weights
| Component | Weight |
|-----------|--------|
| Ingredient Jaccard | 0.40 |
| Cuisine Match | 0.30 |
| Course Match | 0.15 |
| Diet Overlap | 0.15 |

---

## 3. Personalization Layer (Phase 4)

### 3.1 PersonalizedRecommenderConfig
```python
@dataclass
class PersonalizedRecommenderConfig:
    # Base weights
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
```

### 3.2 Personalization Pipeline

```
Base Recommendations (3×k)
         │
         ▼
┌─────────────────────────────────────┐
│ 1. Dietary Constraint Filter        │
│    - Hard: FAIL → exclude           │
│    - UNVERIFIED → exclude (config)  │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 2. Nutrition Completeness Filter    │
│    min_nutrition_completeness       │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 3. Nutrition Match Scoring          │
│    - Energy/Protein/Carb/Fat diff   │
│    - Target achievement check       │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 4. Meal Slot Appropriateness        │
│    - Course ↔ Meal slot mapping     │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 5. Preference Matching              │
│    - Cuisine preferences            │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 6. Combined Scoring & Ranking       │
└─────────────────────────────────────┘
```

---

## 3.3 Scoring Functions

### 3.3.1 Nutrition Match Score
```python
def _calculate_nutrition_match(recipe, nutrition_targets):
    """Average of per-nutrient match (0-1)"""
    scores = []
    for nutrient in ['energy_kcal', 'protein_g', 'carbohydrate_g', 'fat_g']:
        if recipe_value and target_value:
            diff = abs(recipe - target) / target
            scores.append(max(0, 1 - diff))
    return mean(scores) if scores else 0
```

### 3.3.2 Target Achievement Check
```python
def _check_targets(recipe, targets):
    return {
        "meets_energy": abs(recipe.energy - target) / target <= 0.2,
        "meets_protein": abs(recipe.protein - target) / target <= 0.2,
        "meets_carb": abs(recipe.carb - target) / target <= 0.2,
        "meets_fat": abs(recipe.fat - target) / target <= 0.2,
    }
```

### 3.3.3 Meal Slot Score
```python
SLOT_COURSES = {
    "BREAKFAST": ["breakfast", "snack", "beverage"],
    "LUNCH": ["main course", "lunch", "rice", "bread", "curry", "dal"],
    "DINNER": ["main course", "dinner", "rice", "bread", "curry", "dal"],
    "MORNING_SNACK": ["snack", "beverage", "dessert"],
    "EVENING_SNACK": ["snack", "beverage", "dessert", "street food"],
}
score = 1.0 if recipe.course in slot_courses[meal_slot] else 0.3
```

### 3.3.4 Preference Match Score
```python
def _preference_match_score(recipe, user_profile):
    score = 0
    if user_prefs.cuisine_preferences and recipe.cuisine in prefs:
        score += 1.0
    return score / max(1, count)
```

---

## 3.4 Combined Scoring Formula

```python
def _combined_score(rec):
    score = 0
    # Base similarity (30%)
    score += rec.similarity_score * 0.30
    
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
        score += rec.component_scores["meal_slot"] * 0.10
    
    # Preference (10%)
    if "preference" in rec.component_scores:
        score += rec.component_scores["preference"] * 0.10
    
    return max(0, score)
```

---

## 4. Recommendation Types

### 4.1 Similar to Recipe
```python
recommender.recommend(query_recipe_id=123, k=10, filters={})
```
- Uses base recommender's `recommend()` method
- Filters applied post-retrieval

### 4.2 By Ingredients
```python
recommender.recommend_by_ingredients(
    ingredients=["rice", "dal", "turmeric"], k=10
)
```
- Jaccard similarity on ingredient sets
- Useful for "what can I make with these ingredients?"

### 4.3 For Meal Slot
```python
recommender.recommend_for_meal_slot(
    user_profile, nutrition_targets, meal_slot="LUNCH", k=5
)
```
- Filters by appropriate course for meal slot
- Considers meal energy distribution

### 4.4 Diverse Discovery
- Random sampling across cuisines/courses
- Used for cold start / exploration

---

## 4. Meal Slot Awareness

### 4.1 Meal Slot → Course Mapping
| Meal Slot | Appropriate Courses |
|-----------|---------------------|
| BREAKFAST | breakfast, snack, beverage |
| MORNING_SNACK | snack, beverage, dessert |
| LUNCH | main course, lunch, rice, bread, curry, dal |
| EVENING_SNACK | snack, beverage, dessert, street food |
| DINNER | main course, dinner, rice, bread, curry, dal |

### 4.2 Energy Distribution
| Meals | Distribution |
|-------|--------------|
| 3 | B: 30%, L: 40%, D: 30% |
| 4 | B: 25%, L: 35%, S: 15%, D: 25% |
| 5 | B: 25%, M: 10%, L: 35%, E: 10%, D: 20% |
| 6 | B: 20%, M: 10%, L: 30%, A: 10%, E: 10%, D: 20% |

---

## 5. Dietary Constraint Integration

### 5.1 DietClassifier
```python
class DietClassifier:
    NON_VEG = {chicken, mutton, fish, egg, ...}
    VEGETARIAN_NON_VEGAN = {milk, paneer, ghee, ...}
    EGG_INGREDIENTS = {egg, eggs, mayonnaise, ...}
    JAIN_RESTRICTED = {onion, garlic, potato, ginger, ...}
    ALLERGENS = {peanut, milk, egg, wheat, ...}
    
    def classify_recipe(ingredients) -> dict:
        # Returns diet_type, is_vegan, is_vegetarian, etc.
```

### 5.2 DietaryConstraintEngine
```python
engine.evaluate_recipe(
    recipe_id, recipe_name, ingredients,
    user_preference="VEGETARIAN",
    user_allergies=["peanut"],
    user_exclusions=["onion", "garlic"],
    check_jain=False
)
```
Returns: `RecipeDietaryEvaluation` with PASS/FAIL/UNVERIFIED

### 5.3 Constraint Evaluation Flow
```
Recipe Ingredients
       │
       ▼
┌──────────────────┐
│ DietClassifier   │ ──► Diet type (VEGAN/VEG/etc.)
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ AllergenFilter   │ ──► FAIL if allergen present
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ ExclusionFilter  │ ──► FAIL if excluded ingredient
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ PreferenceFilter │ ──► FAIL if incompatible
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ JainCompliance   │ ──► FAIL if restricted ingredient
└──────────────────┘
```

---

## 6. Nutrition Target Integration

### 6.1 NutritionTargetCalculator
```python
calculator = NutritionTargetCalculator()
targets = calculator.calculate_for_profile(user_profile)
# Returns CompleteNutritionTargets with energy, macros, micros, meal_targets
```

### 6.2 Nutrition Match Scoring
```python
def _calculate_nutrition_match(recipe, nutrition_targets):
    """Compare per-serving nutrients to meal targets"""
    scores = []
    for nutrient in ['energy_kcal', 'protein_g', 'carb_g', 'fat_g']:
        if recipe_val and target_val:
            diff = abs(recipe_val - target) / target
            scores.append(max(0, 1 - diff))
    return mean(scores)
```

### 6.3 Target Achievement Tracking
```python
def _check_targets(recipe, targets):
    return {
        "meets_energy": abs(recipe.energy - target) / target <= 0.2,
        "meets_protein": abs(recipe.protein - target) / target <= 0.2,
        "meets_carb": abs(recipe.carb - target) / target <= 0.2,
        "meets_fat": abs(recipe.fat - target) / target <= 0.2,
    }
```

---

## 7. Explanation Generation

### 7.1 Explanation Segments
| Type | Trigger | Content |
|------|---------|---------|
| Content Similarity | `component_scores` | "ingredient overlap (30%), cuisine match (100%)" |
| Shared Ingredients | `shared_ingredients` | "Shares 3 ingredients: rice, dal, turmeric" |
| Dietary Compliance | `dietary_evaluation` | PASS/FAIL/UNVERIFIED with evidence |
| Nutrition Match | `nutrition_match_score` | "Matches targets with 85% score" |
| Target Achievement | `meets_nutritional_targets` | "Meets protein target for this meal" |
| Ingredient Overlap | `shared_ingredients` | "Shares 3 ingredients: rice, dal, turmeric" |

### 7.2 Explanation Output Formats
```python
# Structured
explanation.to_dict()  # → Dict with segments, confidence, limitations

# Human-readable
explanation.to_text()  # → Formatted text for UI display
```

---

## 8. Performance & Caching

### 8.1 Caching Strategy
| Component | Cache TTL | Invalidation |
|-----------|-----------|--------------|
| Base Recommender Fit | Session | On data reload |
| Recipe Profiles | Session | On nutrition update |
| Dietary Evaluations | Per-request | N/A (fast) |
| Nutrition Targets | Per user | On profile update |

### 8.2 Performance Metrics
| Operation | Typical Latency |
|-----------|-----------------|
| Base recommend (6,865 recipes) | ~200ms |
| Personalized (with filters) | ~350ms |
| Dietary evaluation (1 recipe) | ~5ms |
| Nutrition match (4 macros) | ~2ms |
| Explanation generation | ~10ms |

---

## 9. Configuration

### 9.1 PersonalizedRecommenderConfig
```python
config = PersonalizedRecommenderConfig(
    # Base weights
    ingredient_weight=0.4,
    cuisine_weight=0.3,
    course_weight=0.15,
    diet_weight=0.15,
    
    # Personalization
    nutrition_match_weight=0.2,
    dietary_compliance_weight=0.3,
    preference_weight=0.2,
    diversity_weight=0.1,
    
    # Filters
    require_dietary_compliance=True,
    min_nutrition_completeness=0.0,
    exclude_unverified_dietary=True,
    max_results=10,
    
    # Meal slot
    meal_slot_aware=True,
    meal_slot_weights={
        "BREAKFAST": 1.0, "LUNCH": 1.0, "DINNER": 1.0,
        "MORNING_SNACK": 0.8, "EVENING_SNACK": 0.8,
    }
)
```

---

## 10. Limitations

| Limitation | Impact |
|------------|--------|
| No collaborative filtering | No user behavior learning |
| Static weights | Not learned from feedback |
| Proxy nutrition matching | No ground truth validation |
| Binary dietary compliance | No partial compliance scoring |
| Static meal-slot courses | Heuristic, not learned |
| No portion optimization | Servings fixed at 1.0 |

---

*End of Recommendation Integration Report*