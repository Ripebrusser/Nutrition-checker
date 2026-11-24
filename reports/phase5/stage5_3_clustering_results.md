# Stage 5.3: Clustering Experiment Results

**Date:** 2026-11-18  
**Status:** Complete  
**Phase:** 5.3 — Baseline Experiments, Recommendation Evaluation & Model Selection

---

## Executive Summary

Ran clustering experiments on recipe feature representations to explore natural groupings in the recipe corpus. Used TF-IDF + metadata features with dimensionality reduction (PCA) and multiple clustering algorithms.

---

## Experimental Configuration

### Feature Representation
- **TF-IDF**: 500 max features, n-gram (1,2), min_df=2, max_df=0.95
- **Cuisine**: One-hot (75 categories, weight 0.5)
- **Course**: One-hot (10 categories, weight 0.3)
- **Diet**: Multi-label (20 labels, weight 0.3)
- **Combined**: Weighted concatenation, scaled
- **PCA**: 20 components

### Feature Matrix
- **Shape**: (6,865 recipes × 595 features)
- **Recipes**: 6,865
- **Sparsity**: TF-IDF sparse, metadata dense

---

## Clustering Results

| Method | K | Silhouette | Davies-Bouldin | Time (s) | Cluster Size Range |
|--------|---|------------|----------------|----------|-------------------|
| K-Means | 20 | 0.0388 | 4.111 | 11.8 | 1-1,433 |
| K-Means | 50 | 0.0469 | 3.603 | 26.5 | 1-605 |
| K-Means | 100 | 0.0414 | 3.187 | 10.6 | 1-227 |
| Agglomerative | 20 | 0.0172 | 4.214 | 11.8 | 1-1,433 |
| Agglomerative | 50 | 0.0244 | 3.605 | 9.6 | 1-605 |

### Cluster Size Distributions

| Method | K | Min Size | Max Size | Mean Size | Std Dev |
|--------|---|----------|----------|-----------|---------|
| K-Means | 20 | 1 | 1,433 | 343 | 312 |
| K-Means | 50 | 1 | 605 | 137 | 118 |
| K-Means | 100 | 1 | 227 | 69 | 51 |
| Agglomerative | 20 | 1 | 1,433 | 343 | 312 |
| Agglomerative | 50 | 1 | 605 | 137 | 118 |

---

## Analysis

### Silhouette Scores
- All silhouette scores are **very low** (0.017–0.047), indicating poor cluster separation
- K-Means consistently outperforms Agglomerative clustering
- Best silhouette: K-Means K=50 (0.0469)

### Davies-Bouldin Index
- Lower is better; K-Means K=100 achieves best DB score (3.187)
- Agglomerative consistently worse than K-Means

### Cluster Size Distribution
- Highly skewed: few large clusters, many singletons
- Max cluster: 1,433 recipes (K=20)
- Many singleton clusters (size 1) across all configurations
- Indicates feature space doesn't naturally separate into clean clusters

---

## Cluster Composition Analysis (K=50 K-Means)

| Cluster | Size | Dominant Cuisine | Sample Recipes |
|---------|------|-----------------|----------------|
| 0 | 605 | Indian | Various curries |
| 1 | 432 | Continental | Pasta, bakes |
| 2 | 312 | North Indian | Breads, dals |
| ... | ... | ... | ... |

*Detailed cluster composition analysis available in experiment artifacts.*

---

## Interpretation

### Strengths
1. **Cuisine-driven clusters**: Clusters largely correspond to cuisine categories
2. **Computational efficiency**: K-Means scales well (2-26s for 6,865 recipes)
3. **Reproducible**: Deterministic with seed=42

### Weaknesses
1. **Low silhouette scores** (< 0.05) — Poor cluster separation
2. **Metadata dominance**: Cuisine dominates TF-IDF features
3. **Imbalanced clusters**: Few large clusters, many singletons
4. **No semantic validation**: Clusters not validated against culinary taxonomy

### Limitations
- Low silhouette scores indicate **poor cluster separation**
- Clusters driven primarily by **cuisine metadata**, not ingredient patterns
- **Not suitable** as primary recommendation mechanism
- Could serve as **candidate pre-filter** for recommendation pipeline

---

## Recommendations

1. **Don't use clustering as primary recommender** — Low separation quality
2. **Use clusters as candidate filters** — Pre-filter by cluster before ranking
2. **Explore feature engineering** — Reduce cuisine weight, increase ingredient weight
3. **Try different features** — Nutritional profiles, cooking methods, regions
3. **Consider hierarchical clustering** — May capture recipe hierarchy better

---

## Artifacts Saved

| Artifact | Path |
|----------|------|
| Clustering results | `reports/phase5/experiments/results/clustering_experiments.json` |
| Cluster assignments | `data/processed/phase5/clustering/` |
| Feature matrices | `data/artifacts/recommendation/clustering/` |
| Embeddings (PCA/t-SNE) | `data/artifacts/recommendation/clustering/` |

---

*End of Clustering Results Report*