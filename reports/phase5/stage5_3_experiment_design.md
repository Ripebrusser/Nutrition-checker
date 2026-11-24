# Stage 5.3: Experiment Design

**Date:** 2026-11-18  
**Status:** Complete  
**Phase:** 5.3 — Baseline Experiments, Recommendation Evaluation & Model Selection

---

## 1. Experimental Objectives

Compare the following recommendation methods under controlled conditions:

| Experiment | Method | Description |
|------------|--------|-------------|
| **A** | Random Baseline | Uniform random selection from candidate pool |
| **B** | Cuisine Match | Cuisine compatibility + ingredient Jaccard |
| **C** | Jaccard Similarity | Pure ingredient set Jaccard overlap |
| **D** | TF-IDF Content-Based | Cosine similarity on TF-IDF ingredient vectors |
| **E** | Combined Content-Based | Weighted combination of TF-IDF + cuisine + course + diet |

---

## 2. Experimental Setup

### 2.1 Data Splits (Fixed, Reproducible)

| Split | Recipes | Source |
|-------|------------|--------|
| Train | 4,805 (70%) | Feature fitting, baseline training |
| Validation | 1,030 | Hyperparameter selection (if needed) |
| Test | 1,030 | Held-out evaluation (fixed) |

**Split Configuration:**
- Random seed: 42
- Stratification: By cuisine (75 categories)
- Minimum category count: 5
- Leakage prevention: ✅ Verified

### 2.2 Evaluation Query Set

- **Test set:** 1,030 recipes (held out)
- **Evaluation sample:** 100 queries (stratified sample from test set, seed=42)
- **Fixed K values:** K ∈ {5, 10, 20}

### 2.3 Candidate Pool

- **All recipes:** 6,865 (same candidate pool for all methods)
- **Exclusion:** Query recipe always excluded from its own recommendations
- **Duplicates:** Near-duplicates (Jaccard ≥ 0.9) flagged but not auto-excluded

---

## 3. Methods Under Comparison

| ID | Method | Features | Similarity | Parameters |
|------|--------|----------|------------|------------|
| **A** | Random | None | Uniform | seed=42 |
| **B** | Cuisine Match | Cuisine + Ingredients | `0.6×cuisine + 0.4×Jaccard` | cuisine_w=0.6, ing_w=0.4 |
| **C** | Jaccard | Ingredients only | Jaccard(A,B) | — |
| **D** | TF-IDF Content | Ingredients (TF-IDF) | Cosine similarity | max_features=2000, ngram=(1,2) |
| **E** | Combined | TF-IDF + Cuisine + Course + Diet | Weighted cosine | w_ing=1.0, w_cuisine=1.0, w_course=1.0, w_diet=1.0 |

### Weight Configurations for Method E (Combined)

| Config | w_ing | w_cuisine | w_course | w_diet | Notes |
|--------|-------|-----------|----------|--------|-------|
| E1 (Default) | 1.0 | 1.0 | 1.0 | 1.0 | Equal weights |
| E2 (Ingredient-focused) | 2.0 | 0.5 | 0.5 | 0.5 | Ingredient-heavy |
| E3 (Metadata-focused) | 0.5 | 1.5 | 1.0 | 1.0 | Metadata-heavy |

---

## 4. Evaluation Methods

### 4.1 Proxy Relevance (Primary)

Since no ground truth exists, we use a **proxy relevance function** based on:

```
proxy_score = 0.5 × Jaccard(ingredients) 
            + 0.20 × cuisine_match 
            + 0.15 × course_match 
            + 0.15 × diet_overlap
```

**Threshold:** `proxy_score ≥ 0.3` → proxy-relevant

**Known Bias:** This proxy favors ingredient-based methods (Jaccard, TF-IDF). Reported as limitation.

### 4.2 Metrics (Computed per query, averaged)

| Metric | Formula | Notes |
|--------|---------|-------|
| Precision@K | `|Relevant ∩ Top-K| / K` | Proxy-relevant |
| Recall@K | \|Relevant ∩ Top-K\| / \|Relevant\| | Proxy-relevant |
| Diversity@K | 1 - mean pairwise Jaccard in top-K | Ingredient-level |
| Coverage@K | \|Unique recommended in top-K\| / Catalogue size | Catalogue = test set |
| Novelty | Mean -log₂(popularity) | Popularity = 1 (uniform) |
| Cuisine Compliance | % matching required cuisine | Constraint check |
| Diet Compliance | % satisfying diet constraints | Constraint check |

### 4.3 Experimental Controls

| Control | Implementation |
|---------|----------------|
| Random seed | 42 (all methods, all splits) |
| Query set | Fixed 100 recipes from test set (stratified) |
| Candidate pool | All 6,865 recipes (same pool for all methods) |
| Exclusions | Query recipe always excluded |
| Duplicates | Removed from output (deduplicated) |
| K values | 5, 10, 20 |
| Seeds | Fixed: 42 (numpy, random, sklearn) |

---

## 5. Experiment Execution Plan

### Phase 1: Baseline Experiments
1. Run baseline methods (A, B, C) on evaluation set
2. Compute proxy metrics
2. Save per-query results

### Phase 2: Content-Based Experiments
3. Run TF-IDF (D) and Combined (E1, E2, E3)
4. Compute proxy metrics
4. Save per-query results

### Phase 3: Clustering Experiment
5. Build clustering features (TF-IDF + metadata)
3. Run K-Means (K=20, 50, 100) and Agglomerative (K=20, 50)
4. Evaluate cluster quality metrics
4. Save cluster assignments

### Phase 4: Error Analysis
4. Identify error patterns across methods
4. Categorize failure modes
4. Generate examples

### Phase 5: Model Selection
5. Consolidate all results
5. Apply selection criteria
5. Document decision rationale

---

## 6. Output Locations

| Output | Path |
|--------|------|
| Experiment configs | `reports/phase5/experiments/configs/` |
| Per-query results | `reports/phase5/experiments/results/` |
| Aggregate metrics | `reports/phase5/experiments/summary/` |
| Clustering assignments | `data/processed/phase5/clustering/` |
| Error analysis | `reports/phase5/experiments/error_analysis/` |

---

## 5. Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| All methods produce K recommendations for ≥95% queries | ≥95% |
| No self-recommendations | 0% |
| No duplicate recommendations | 0% |
| Deterministic (fixed seed) | Identical runs |
| Test suite passes | 100% |

---

## 6. Limitations (Explicit)

| Limitation | Impact | Disclosure |
|------------|--------|------------|
| No ground truth labels | Proxy metrics only | Explicitly stated in reports |
| Proxy favors ingredient methods | Jaccard/TF-IDF favored | Acknowledged in reports |
| No user preference data | No personalization eval | Explicitly stated |
| No nutrition integration | Phase 3.6 pending | Documented |
| Circular proxy risk | Ingredient-based proxy | Acknowledged |

---

*End of Experiment Design*