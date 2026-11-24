# Phase 4: Explanation Engine Report

**Date:** 2026-11-19  
**Status:** Implementation Complete

---

## 1. Overview

The Explanation Engine (`src/personalization/explanation_engine.py`) generates transparent, traceable explanations for recommendations and meal plans. Every explanation includes evidence references, confidence levels, and known limitations.

---

## 2. Architecture

### 2.1 Core Components

| Class | Purpose |
|-------|---------|
| `ExplanationEngine` | Main generator |
| `RecommendationExplanation` | Single recommendation explanation |
| `MealPlanExplanation` | Complete meal plan explanation |
| `ExplanationSegment` | Atomic explanation unit with provenance |

### 2.2 Explanation Types
```python
class ExplanationType(Enum):
    RECOMMENDATION = "RECOMMENDATION"
    MEAL_PLAN = "MEAL_PLAN"
    DAILY_PLAN = "DAILY_PLAN"
    NUTRITION_MATCH = "NUTRITION_MATCH"
    DIETARY_COMPLIANCE = "DIETARY_COMPLIANCE"
    NUTRIENT_GAP = "NUTRIENT_GAP"
    VARIETY = "VARIETY"
    SUBSTITUTION = "SUBSTITUTION"
```

---

## 3. Explanation Segments

### 3.1 Structure
```python
@dataclass
class ExplanationSegment:
    type: ExplanationType
    title: str
    content: str
    evidence: List[str] = field(default_factory=list)
    confidence: float = 1.0
    provenance: Dict[str, Any] = field(default_factory=dict)
```

### 3.2 Key Properties
- **type** - Category of explanation
- **title** - Human-readable section header
- **content** - Natural language explanation
- **evidence** - Specific data points supporting claim
- **confidence** - 0.0-1.0 reliability score
- **provenance** - Traceability to source data

---

## 4. Recommendation Explanations

### 4.1 Structure
```python
@dataclass
class RecommendationExplanation:
    recipe_id: int
    recipe_name: str
    overall_reason: str
    segments: List[ExplanationSegment]
    confidence: float
    limitations: List[str]
```

### 4.2 Segment Types Generated

| Segment | Trigger | Content |
|---------|---------|---------|
| **Content Similarity** | `component_scores` present | "Selected based on ingredient overlap (30%), cuisine match (100%), course match (0%)" |
| **Shared Ingredients** | `shared_ingredients` non-empty | "Shares 3 ingredients: rice, dal, turmeric" |
| **Dietary Compliance** | `dietary_evaluation` present | PASS/FAIL/UNVERIFIED with evidence |
| **Nutrition Match** | `nutrition_match_score` + targets | "Matches targets with 85% score" |
| **Target Achievement** | `meets_nutritional_targets` | "Meets protein target for this meal" |
| **Ingredient Overlap** | `shared_ingredients` | Detailed ingredient list |

### 4.3 Overall Reason Generation
```python
# Combines top component scores
if cuisine_match == 1.0: "same cuisine"
if ingredient_jaccard > 0.3: "strong ingredient overlap"
elif ingredient_jaccard > 0: "some shared ingredients"
# → "Recommended because of same cuisine and strong ingredient overlap"
```

### 4.4 Limitations Tracking
```python
# Automatically generated
if no nutrition_match_score: "Nutrition match score not available"
if no dietary_evaluation: "Dietary compliance not evaluated"
if no per_serving_nutrients: "Per-serving nutrition data not available"
```

### 4.4 Output Formats
```python
# Structured dict
explanation.to_dict()

# Human-readable text
explanation.to_text()
# Output:
# Recommendation: Dal Rice
# Overall: Recommended because of same cuisine and strong ingredient overlap
# 
# Details:
#   • Content Similarity: Selected based on cuisine match (100%), ingredient overlap (30%)
#     Evidence: Similarity score: 0.85
#   • Shared Ingredients: Shares 2 ingredients: rice, dal
#     Evidence: Shared ingredients: rice, dal
#   • Dietary Compliance: Recipe meets all your dietary requirements
#     Evidence: Dietary evaluation: PASS
#
# Limitations:
#   • Nutrition match score not available
```

---

## 5. Meal Plan Explanations

### 5.1 Structure
```python
@dataclass
class MealPlanExplanation:
    plan_date: str
    overall_summary: str
    daily_explanations: Dict[str, str]
    nutrient_achievement_summary: Dict[str, str]
    dietary_compliance_summary: str
    variety_summary: str
    limitations: List[str]
    nutritional_gaps: List[str]
```

### 5.2 Daily Plan Explanation
```python
def _explain_daily_plan(day, targets):
    parts = []
    filled = [s for s in day.slots.values() if s.recipe_id]
    parts.append(f"{len(filled)}/{len(day.slots)} meals: {recipe_names}")
    
    if day.nutrient_achievement:
        avg = mean(day.nutrient_achievement.values())
        status = "met" if avg >= 0.95 else "low" if avg < 0.9 else "partial"
        parts.append(f"Nutrient targets: {avg:.0%} ({status})")
    
    parts.append(f"Status: {day.status}")
    return "; ".join(parts)
```

### 5.3 Nutrient Achievement Summary
```python
# Average across week
nutrient_summary[nutrient] = f"{avg_achievement:.0%} average ({status})"
# status: met (≥95%), low (<90%), partial (90-95%)
```

### 5.4 Nutritional Gaps
```python
def _identify_nutritional_gaps(plan, targets):
    gaps = []
    for nutrient, target in targets.macros.__dict__.items():
        if target and nutrient in plan.weekly_achievement:
            ach = plan.weekly_achievement[nutrient]
            if ach < 0.9:
                gaps.append(f"Weekly {nutrient} only {ach:.0%} of target")
    return gaps
```

### 5.5 Limitations
```python
def _identify_limitations(plan, targets):
    limitations = []
    # Unfilled slots
    if unfilled > 0: limitations.append(f"{unfilled} meal slots unfilled")
    
    # Nutrition completeness
    if incomplete_rate > 0.5:
        limitations.append("Over 50% of meals have incomplete nutrition data")
    
    if not targets:
        limitations.append("No nutrition targets provided for validation")
    
    return limitations
```

---

## 6. Provenance & Traceability

### 6.1 Segment Provenance
Each `ExplanationSegment` includes:
```python
provenance = {
    "source": "mapping:reviewer_id:timestamp;ifct:verified;weight:RESOLVED",
    "base_similarity_components": {...},
    "shared_ingredients": [...],
    "dietary_evaluation": {...},
    "nutrition_match_score": 0.85,
    "per_serving": {...},
    "meets_targets": {...}
}
```

### 6.2 Evidence References
- Specific data points cited in `evidence` list
- Direct quotes from calculation results
- Traceable to original data sources

---

## 7. Integration Points

### 7.1 Recommendation Explanation
```python
engine = ExplanationEngine()
explanation = engine.explain_recommendation(
    rec=PersonalizedRecommendationResult(...),
    user_profile=UserProfile(...),
    nutrition_targets=CompleteNutritionTargets(...)
)
```

### 7.2 Meal Plan Explanation
```python
explanation = engine.explain_meal_plan(
    plan=WeeklyMealPlan(...),
    user_profile=UserProfile(...),
    nutrition_targets=CompleteNutritionTargets(...),
    recipe_collection=RecipeProfileCollection(...)
)
```

### 7.3 Convenience Functions
```python
generate_recommendation_explanation(rec, user_profile, nutrition_targets)
generate_meal_plan_explanation(plan, user_profile, nutrition_targets, recipe_collection)
```

---

## 7. Output Formats

| Format | Method | Use Case |
|--------|--------|----------|
| Structured dict | `to_dict()` | API responses, logging |
| Human-readable text | `to_text()` | User-facing display, debugging |

---

## 8. Limitations & Honest Disclosure

Every explanation automatically includes limitations:
- Missing nutrition data
- Unverified dietary compliance
- Proxy metrics (no ground truth)
- No clinical validation
- Synthetic test data separation

---

## 9. Files

| File | Purpose |
|------|---------|
| `src/personalization/explanation_engine.py` | Core engine |
| `tests/phase4/test_personalization.py` | Explanation tests |

---

*End of Explanation Engine Report*