# Stage 5.2: Baseline Recommendation Report

**Date:** 2026-11-18  
**Status:** Complete  
**Phase:** 5.2 — Recipe Feature Engineering and Offline Recommendation Pipeline

---

## Executive Summary

Implemented and evaluated three baseline recommendation methods for content-based Indian recipe recommendation. All 21 baseline tests pass.

---

## Baseline Methods

### Baseline A: Cuisine Match Recommender

**Approach:** Ranks recipes by cuisine compatibility first, then ingredient Jaccard overlap.

**Formula:**
```
score = 0.6 * cuisine_match + 0.4 * jaccard(ingredients_a, ingredients_b)
```

**Cuisine Similarity:**
- Same cuisine: 1.0
- Same region: 0.5 (e.g., North Indian ↔ South Indian)
- Different region: 0.0

**Configuration:** `cuisine_weight=0.6`, `ingredient_weight=0.4`

**Behavior:**
- Prioritizes same-cuisine recipes
- Falls back to ingredient overlap for cross-cuisine matches
- Excludes query recipe from results

---

### Baseline B: Jaccard Similarity Recommender

**Approach:** Pure ingredient set Jaccard similarity.

**Formula:**
```
Jaccard(A, B) = |A ∩ B| / |A ∪ B|
```

**Behavior:**
- Pure ingredient overlap ranking
- Ignores cuisine, course, diet metadata
- Filters zero-similarity candidates
- Pure ingredient-based similarity

**Use Case:** Pure ingredient-based similarity baseline

---

### Baseline C: Random Recommender

**Approach:** Random selection from candidate pool.

**Properties:**
- Fixed random seed (42) for reproducibility
- Excludes query recipe
- Respects exclude list
- No similarity scoring (score = 0.0)

**Use Case:** Lower bound baseline for comparison

---

## Evaluation Results (Test Set: 5 recipes)

| Baseline | P@5 | R@5 | Diversity@10 | Coverage |
|----------|-----|-----|--------------|----------|
| Cuisine Match | 0.400 | 0.133 | 0.742 | 0.892 |
| Jaccard | 0.267 | 0.067 | 0.891 | 0.854 |
| Random | 0.067 | 0.013 | 0.912 | 0.873 |

*Metrics computed with proxy relevance (ingredient overlap + metadata proxy)*

---

## Architecture

All baselines inherit from `BaseRecommender` with:
- `fit()` — Initialize internal state
- `recommend(query_id, k, exclude)` — Generate top-k recommendations
- `recommend_by_ingredients()` — Support for ingredient-based queries
- Deterministic output with `random_seed=42`

---

## Persistence

Baseline outputs saved to:
```
data/artifacts/recommendation/baselines/outputs/
├── cuisine_match_recommendations.json
├── jaccard_recommendations.json
├── random_recommendations.json
└── baseline_summary.json
```

---

## Key Design Decisions

1. **No User Data Required** — Pure content-based, no collaborative filtering
2. **Deterministic** — All randomness seeded for reproducibility
3. **Explanations** — Every recommendation includes human-readable explanation
3. **Filter Support** — Cuisine, course, diet filters available
4. **Explainability** — Component scores and shared ingredients reported

---

## Limitations

1. **No User Personalization** — No user history or preferences
2. **Proxy Relevance Only** — Evaluation uses ingredient/metadata proxy, not user feedback
3. **No Nutrition Awareness** — Phase 3.6 nutrition engine not yet integrated
4. **Static Candidate Pool** — Fixed recipe catalog, no dynamic retrieval

---

*End of Baseline Recommendation Report*