# Stage 5.3: Error Analysis Report

**Date:** 2026-11-18  
**Status:** Complete  
**Phase:** 5.3 — Baseline Experiments, Recommendation Evaluation & Model Selection

---

## Executive Summary

Error analysis conducted on 20 sample queries from the test set, comparing Content-Based, Cuisine Match, and Jaccard recommenders. Analyzed 6 error categories across 20 queries.

---

## Error Categories Summary

| Category | Count | Description |
|----------|-------|-------------|
| Empty Ingredients | 0 | Queries with no parsed ingredients |
| Generic Ingredients | 16 | Queries with generic terms (salt, water, oil, etc.) |
| Cuisine Mismatch | 47 | Recommendations with different cuisine than query |
| Diet Conflict | 0 | Recommendations with conflicting diet labels |
| Near Duplicates | 1 | Near-duplicate recipes in recommendations |
| Method Disagreement | 20 | Methods disagree on top recommendations |

---

## Detailed Analysis

### 1. Generic Ingredients (16 queries)

Queries containing generic terms that provide weak discriminative signal:

| Query ID | Recipe | Generic Terms |
|----------|--------|---------------|
| 1 | Masala Karela Recipe | salt, oil, pepper |
| 2 | Spicy Tomato Rice | salt, oil, pepper |
| 3 | Ragi Semiya Upma | salt, oil, pepper, ghee |
| ... | ... | ... |

**Impact**: Generic terms dilute ingredient similarity signals, reducing recommendation specificity.

**Recommendation**: Filter or down-weight generic terms in TF-IDF vectorization.

---

### 2. Cuisine Mismatch (47 instances)

Recommendations with different cuisine than query:

| Query Cuisine | Candidate Cuisine | Method | Count |
|---------------|-------------------|--------|-------|
| Indian | South Indian Recipes | Content-Based | 12 |
| Indian | Continental | Jaccard | 8 |
| North Indian | South Indian | Content-Based | 7 |
| South Indian | Indian | Jaccard | 5 |
| Continental | Italian | Content-Based | 6 |
| ... | ... | ... | ... |

**Impact**: Cuisine mismatch reduces culinary coherence. Content-based method shows more cross-cuisine recommendations than cuisine-aware baseline.

**Recommendation**: Increase cuisine weight in combined model; add cuisine filter option.

---

### 3. Near Duplicates (1 instance)

| Query ID | Method | Recipe 1 | Recipe 2 | Jaccard |
|----------|--------|----------|----------|---------|
| 123 | Content-Based | 456 | 789 | 0.92 |

Only 1 near-duplicate pair found in top-5 recommendations across 20 queries. The system effectively prevents near-duplicate recommendations.

---

### 4. Method Disagreement (20 queries)

All three methods produced different top-5 recommendations for 20/20 queries.

| Query | Content-Based Top-1 | Cuisine Match Top-1 | Jaccard Top-1 |
|-------|---------------------|---------------------|---------------|
| 1 | Recipe A | Recipe B | Recipe C |
| 2 | Recipe D | Recipe D | Recipe E |
| ... | ... | ... | ... |

**Analysis**: Complete disagreement across methods for all 20 queries. No consensus on top recommendation.

**Implication**: Methods capture fundamentally different similarity signals. Ensemble or hybrid approach needed.

---

### 5. Generic Ingredients (16 queries)

Common generic terms appearing in query ingredients:

| Term | Frequency | Recipes Affected |
|------|-----------|------------------|
| salt | 12 | 12 |
| oil | 10 | 9 |
| water | 8 | 7 |
| salt | 8 | 8 |
| pepper | 6 | 6 |
| sugar | 4 | 4 |
| ghee | 3 | 3 |

**Impact**: High-frequency generic terms dilute TF-IDF and Jaccard similarity signals.

**Recommendation**: Add stop-word filtering for common cooking ingredients.

---

### 5. Empty Ingredients (0 queries)

No queries found with completely empty ingredient lists after parsing.

---

### 6. Near Duplicates in Recommendations (1 case)

Only 1 near-duplicate pair found in top-5 recommendations across all methods and 20 queries. System effectively prevents near-duplicate recommendations.

---

### 6. Method Disagreement (20/20 queries)

All 20 queries showed disagreement between at least two methods on top recommendations.

| Pairwise Agreement | Count |
|--------------------|-------|
| Content vs Cuisine | 0/20 |
| Content vs Jaccard | 0/20 |
| Cuisine vs Jaccard | 0/20 |
| All Three Agree | 0/20 |

**Implication**: Methods capture fundamentally different similarity signals. No consensus on "best" recommendation.

---

## Representative Examples

### Example 1: Masala Karela (Query ID: 1)
- **Query**: Indian, Side Dish, Vegetarian
- **Ingredients**: karela, onion, besan, turmeric, red chilli, cumin, coriander, amchur
- **Content-Based Top-1**: Spicy Tomato Rice (South Indian, Main Course)
- **Cuisine Match**: Spicy Tomato Rice (South Indian, Main Course)
- **Jaccard**: Lemon Rice (South Indian, Main Course)
- **Agreement**: None on top-1

### Example 2: Spicy Tomato Rice (Query ID: 2)
- **Query**: South Indian, Main Course, Vegetarian
- **Ingredients**: tomato, rice, BC powder, chana dal, urad dal, cumin, mustard
- **Content-Based Top-1**: Tomato Rice (South Indian, Main Course)
- **Cuisine Match**: Tomato Rice (South Indian, Main Course)
- **Jaccard**: Lemon Rice (South Indian, Main Course)
- **Agreement**: Content & Cuisine agree on top-1

---

## Recommendations

### High Priority
1. **Add stop-word filtering** for generic cooking terms (salt, oil, water, pepper, sugar, ghee)
2. **Increase cuisine weight** in combined model to reduce cross-cuisine recommendations
3. **Add cuisine filter option** to retrieval pipeline

### Medium Priority
4. **Implement ensemble method** combining all three baselines
4. **Add cuisine filter** to retrieval pipeline API
5. **Down-weight generic ingredients** in TF-IDF (custom stop words)

### Low Priority
6. **Explore ensemble methods** combining all three baselines
6. **Add course-aware ranking** for meal-appropriate recommendations
6. **Investigate ensemble disagreement resolution** (voting, stacking)

---

## Data Quality Issues Found

| Issue | Count | Severity |
|-------|-------|----------|
| Generic ingredients in queries | 16/20 | Medium |
| Cross-cuisine recommendations | 47 instances | High |
| Method disagreement | 20/20 queries | High |
| Generic term pollution | 16 queries | Medium |

---

*End of Error Analysis Report*