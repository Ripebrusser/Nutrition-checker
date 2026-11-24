# Stage 5.2: Evaluation Protocol

**Date:** 2026-11-18  
**Status:** Complete  
**Phase:** 5.2 — Recipe Feature Engineering and Offline Recommendation Pipeline

---

## Executive Summary

Defines the offline evaluation protocol for the content-based recipe recommendation system. Since no genuine user interaction data exists, the protocol uses a defensible proxy relevance framework with explicit acknowledgment of limitations.

---

## Evaluation Challenge

**No Ground Truth:** No user ratings, click logs, or historical meal selections exist.

**Solution:** Proxy relevance based on ingredient overlap + metadata matches.

---

## Proxy Relevance Definition

A candidate recipe is considered *proxy-relevant* to a query recipe if:

```
proxy_score = 0.5 * jaccard(ingredients) 
            + 0.2 * cuisine_match 
            + 0.15 * course_match 
            + 0.15 * diet_overlap
```

**Threshold:** `proxy_score ≥ 0.3` → *proxy-relevant*

---

## Proxy Components

| Component | Weight | Computation |
|-----------|--------|-------------|
| Ingredient Jaccard | 0.50 | `|A ∩ B| / |A ∪ B|` |
| Cuisine Match | 0.20 | 1.0 if same cuisine, else 0.0 |
| Course Match | 0.15 | 1.0 if same course, else 0.0 |
| Diet Overlap | 0.15 | Overlap coefficient = \|A ∩ B\| / min(\|A\|, \|B\|) |

**Threshold:** `proxy_score ≥ 0.3` → proxy-relevant

---

## Evaluation Metrics

### Primary Metrics (Proxy-based)

| Metric | Definition |
|--------|------------|
| **Precision@k** | \|Relevant ∩ Top-k\| / k |
| **Recall@k** | \|Relevant ∩ Top-k\| / \|Relevant\| |
| **Diversity@k** | 1 - mean pairwise Jaccard in top-k |
| **Coverage** | \|Unique recommended recipes\| / Catalogue size |
| **Novelty** | Mean -log₂(popularity) of recommended items |

### Constraint Compliance

| Constraint | Metric |
|------------|--------|
| Cuisine | % recommendations matching required/allowed cuisines |
| Diet | % recommendations satisfying required/forbidden diets |

---

## Evaluation Protocol

### 1. Data Splits
- **Test Set:** 1,030 recipes (15% of 6,865)
- **Stratification:** By cuisine
- **Seed:** 42 (reproducible)

### 2. Evaluation Procedure

For each query recipe in test set:
1. Generate top-max(k) recommendations
2. Compute proxy relevance for all candidates
3. Calculate Precision@k, Recall@k for k ∈ {1, 5, 10, 20}
4. Compute diversity, coverage, constraint compliance

### 3. Baseline Comparison

Compare three baselines:
1. Content-Based (TF-IDF + metadata)
2. Cuisine Match + Jaccard
3. Jaccard Only
4. Random

---

## Proxy Relevance Limitations (Explicit)

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Favors ingredient-based systems | Biased toward ingredient similarity | Acknowledged in reporting |
| No user preference signal | Cannot validate personalization | Explicitly stated |
| Metadata bias | Cuisine/course from source data | Acknowledge source bias |
| No user behavior | No click/ratings data | Cannot measure true satisfaction |

---

## Statistical Rigor

- **Sample Size:** Full test set (1,030 recipes)
- **k Values:** {1, 5, 10, 20}
- **Reporting:** Mean ± std, median
- **Significance:** Not claimed (no statistical test without ground truth)

---

## Reporting Requirements

Each evaluation run produces:

1. **Metrics Table** — Precision@k, Recall@k, Diversity, Coverage per recommender
2. **Baseline Comparison** — Side-by-side metric comparison
3. **Disagreement Analysis** — Where baselines disagree
4. **Coverage Report** — Catalogue coverage %
3. **Constraint Compliance** — Cuisine/diet compliance rates
4. **Limitations Statement** — Explicit proxy limitations

---

## Reproducibility

- **Random Seed:** 42 (fixed)
- **Data Splits:** Fixed via seed 42
- **Recommenders:** Deterministic (seeded random)
- **Artifacts:** Feature matrices, splits, models persisted

---

## Limitations Statement (Required in Reports)

> *"This evaluation uses a proxy relevance metric based on ingredient overlap and metadata similarity. It does not measure actual user preference or recommendation quality. Results indicate system behavior under the proxy, not validated user satisfaction. No claim of user preference modeling is made."*

---

*End of Evaluation Protocol*