# Stage 5.3: Baseline Experiment Results

**Date:** 2026-11-18  
**Status:** Complete  
**Phase:** 5.3 — Baseline Experiments, Recommendation Evaluation & Model Selection

---

## Executive Summary

Ran baseline recommendation experiments comparing three methods: Random, Cuisine Match, and Jaccard Similarity. All experiments used proxy relevance evaluation with proxy_score threshold of 0.3.

---

## Experimental Configuration

| Parameter | Value |
|-----------|-------|
| Random Seed | 42 |
| Test Queries | 50 (sampled from 1,367 test recipes) |
| K Values | [5, 10, 20] |
| Proxy Threshold | 0.3 |
| Proxy Weights | Jaccard: 0.5, Cuisine: 0.2, Course: 0.15, Diet: 0.15 |

---

## Results Summary

| Method | P@5 | R@5 | Diversity@10 | Coverage | Time (s) |
|--------|-----|-----|--------------|----------|----------|
| Random | 0.128 | 0.0006 | 0.958 | 0.254 | 5.5 |
| Cuisine Match | 0.904 | 0.011 | 0.824 | 0.225 | 19.5 |
| Jaccard | 0.548 | 0.005 | 0.773 | 0.220 | 10.4 |

---

## Detailed Results

### Random Baseline
| Metric | Value |
|--------|-------|
| Precision@5 | 0.128 ± 0.335 |
| Recall@5 | 0.0006 ± 0.004 |
| Precision@10 | 0.112 ± 0.258 |
| Recall@10 | 0.001 ± 0.006 |
| Precision@20 | 0.108 ± 0.196 |
| Recall@20 | 0.002 ± 0.009 |
| Diversity@10 | 0.958 |
| Coverage@20 | 0.254 |
| Time/query | 0.11s |

### Cuisine Match
| Metric | Value |
|--------|-------|
| Precision@5 | 0.904 ± 0.295 |
| Recall@5 | 0.011 ± 0.040 |
| Precision@10 | 0.756 ± 0.342 |
| Recall@10 | 0.021 ± 0.058 |
| Precision@20 | 0.604 ± 0.352 |
| Recall@20 | 0.034 ± 0.078 |
| Diversity@10 | 0.824 |
| Coverage@20 | 0.225 |
| Time/query | 0.39s |

### Jaccard Similarity
| Metric | Value |
|--------|-------|
| Precision@5 | 0.548 ± 0.498 |
| Recall@5 | 0.005 ± 0.018 |
| Precision@10 | 0.416 ± 0.404 |
| Recall@10 | 0.009 ± 0.025 |
| Precision@20 | 0.344 ± 0.362 |
| Recall@20 | 0.015 ± 0.033 |
| Diversity@10 | 0.773 |
| Coverage@20 | 0.220 |
| Time/query | 0.21s |

---

## Analysis

### Key Findings

1. **Cuisine Match dominates on Precision@5 (0.904)** — Strong cuisine filtering dramatically improves precision by restricting candidates to same cuisine.

2. **Jaccard provides better balance** — Better precision/recall tradeoff than random, with reasonable diversity (0.773).

3. **Random baseline is weak** — As expected, random recommendations have very low precision/recall but highest diversity (0.958).

3. **All methods have low recall** — Proxy relevance threshold (0.3) is strict; few candidates meet the proxy relevance threshold.

4. **Cuisine Match has lower diversity** — Restricting to same cuisine reduces diversity but increases precision.

---

## Method Comparison

| Criterion | Random | Cuisine Match | Jaccard |
|-----------|--------|---------------|---------|
| Precision@5 | 0.128 | **0.904** | 0.548 |
| Recall@5 | 0.001 | **0.011** | 0.005 |
| Diversity@10 | **0.958** | 0.824 | 0.773 |
| Coverage@20 | 0.254 | 0.225 | 0.220 |
| Speed | Fastest | Slow | Medium |

---

## Limitations (Explicit)

1. **Proxy relevance bias** — Proxy favors ingredient-based methods (Jaccard, TF-IDF)
2. **Low recall across all methods** — Proxy threshold (0.3) is strict
3. **No ground truth** — All metrics based on proxy relevance, not human judgments
4. **Small test sample** — 50 queries from 1,367 test recipes

---

*End of Baseline Results Report*