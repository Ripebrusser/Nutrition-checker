# Phase 5.1: Experiment Recommendation

**Date:** 2026-11-18  
**Objective:** Recommend experimental direction for Phase 5 ML work

---

## Executive Summary

Based on the dataset feasibility audit and ML problem evaluation, I recommend the following experimental direction for Phase 5:

| Priority | Problem | Classification | Start |
|----------|---------|----------------|-------|
| **Primary** | Content-Based Recipe Recommendation | FEASIBLE NOW | Immediately |
| **Secondary** | Recipe Clustering by Cuisine/Ingredients | FEASIBLE NOW | Immediately |
| **Baseline** | Cuisine/Ingredient-Overlap Recommendation | Rule-based | Immediately |
| **Deferred** | Nutritional Constraint Ranking | FEASIBLE AFTER DATA PREP | After Phase 3.6 |
| **Deferred** | Ingredient Substitution | FEASIBLE AFTER DATA PREP | After Phase 3.6 |
| **Deferred** | Personalized Meal Recommendation | REQUIRES NEW DATA | After Phase 4 + user data |
| **Rejected** | Portion-Size Prediction | NOT JUSTIFIED | Never |
| **Rejected** | User Preference Prediction | NOT JUSTIFIED | Never |

---

## Primary Problem: Content-Based Recipe Recommendation

### Why This Problem

1. **All data available now** - 6,865 recipes, 13,049 unique ingredients, 75 cuisines, 10 courses, 20 diet labels
2. **No user data required** - Pure content-based approach; no collaborative filtering needed
3. **Directly serves project goal** - "Help users find recipes" is the core use case
4. **Scientifically defensible** - Content-based filtering is established, well-understood methodology
5. **Evaluatable offline** - Precision@k, diversity, coverage, novelty metrics available
6. **Rule-based baseline exists** - Cuisine match + ingredient Jaccard overlap is implementable and transparent
7. **No fabricated data** - No need to invent user ratings, clicks, or preferences

### Problem Formulation

**Task:** Given a recipe (or ingredient set), recommend k similar recipes

**Formulation:** Item-item similarity recommendation (not user-item)

**Input Features (per recipe):**
- TF-IDF vector of normalized ingredients (vocab: 13,049 → max_features=2000)
- Cuisine one-hot (75 categories)
- Course one-hot (10 categories)
- Diet labels multi-hot (20 labels)
- Estimated nutrition vector (when Phase 3.6 completes) - 7 core nutrients

**Output:** Ranked list of k recipes with similarity scores

**Similarity Function:**
```
sim(recipe_a, recipe_b) = w1 * cosine(tfidf_a, tfidf_b) + w2 * cuisine_match + w3 * course_match + w4 * diet_overlap + w5 * nutrition_distance
```

---

## Secondary Problem: Recipe Clustering

### Why This Problem

1. **Pure unsupervised** - No labels needed
2. **Exploratory value** - Discover natural recipe groupings beyond cuisine labels
3. **Supports primary problem** - Cluster-aware recommendation improves diversity
3. **All features available now** - No additional data needed
4. **Evaluation possible** - Internal metrics + expert qualitative assessment

### Problem Formulation

**Task:** Group recipes into coherent clusters based on ingredient composition and metadata

**Approach:**
1. Feature matrix: TF-IDF ingredients (max_features=2000) + cuisine/course/diet one-hot
2. Dimensionality reduction: PCA (50 components) → UMAP (2D/3D for visualization)
3. Clustering: HDBSCAN (handles variable density) + K-means (baseline)
4. Evaluation: Silhouette, Davies-Bouldin, cuisine purity, expert qualitative review

---

## Rule-Based Baseline

### Cuisine/Ingredient-Overlap Recommender

**Rationale:** Required honest baseline for any ML recommendation system. Transparent, no training, interpretable.

**Formula:**
```
score(a, b) = 0.6 * cuisine_match(a, b) + 0.4 * jaccard(ingredients_a, ingredients_b)
```

Where:
- `cuisine_match(a, b) = 1.0` if same cuisine, `0.5` if same region, `0.0` otherwise
- `jaccard(A, B) = |ingredients_A ∩ ingredients_B| / |ingredients_A ∪ ingredients_B|`
- Weights fixed a priori (no tuning on test data)

**Why these weights:** Cuisine is strong signal (user typically wants same cuisine); ingredient overlap captures fine-grained similarity. Weights set a priori, not tuned on test.

---

## Experimental Design

### Data Splits (Critical: Prevent Leakage)

| Split | Method | Size | Rationale |
|-------|--------|------|-----------|
| Train | 70% recipes | 4,805 | Model development (for learned metrics) |
| Validation | 15% recipes | 1,030 | Hyperparameter tuning |
| Test | 15% recipes | 1,030 | Final evaluation |

**CRITICAL:** Split by **recipe_id** (not ingredient lines). Stratify by cuisine to maintain distribution.

### Leakage Prevention Checklist

- [ ] Split by recipe_id, NOT ingredient lines
- [ ] No IFCT match features in training that leak target mapping
- [ ] No recipe_id in test appearing in train (obvious but critical)
- [ ] Cuisine stratification maintained across splits
- [ ] No user data leakage (no user data exists)
- [ ] Nutrition features from Phase 3.6 only (not IFCT direct)

---

## Evaluation Protocol

### Primary Metrics (Content-Based Recommendation)

| Metric | Definition | Target |
|--------|------------|--------|
| **Precision@5** | % of top-5 recommendations that are relevant | > 0.30 |
| **Precision@10** | % of top-10 recommendations that are relevant | > 0.20 |
| **Diversity@10** | 1 - mean pairwise similarity in top-10 | > 0.50 |
| **Coverage** | % of recipes that appear in any top-10 | > 0.70 |
| **Novelty** | Mean inverse popularity of recommended items | > median |

**Relevance Definition (Offline Proxy):**
- Same cuisine = relevant (strong signal)
- Same course = partially relevant
- High ingredient Jaccard (>0.3) = relevant
- Same diet labels = partially relevant

### Secondary Metrics (Clustering)

| Metric | Target |
|--------|--------|
| Silhouette Score | > 0.30 |
| Davies-Bouldin Index | < 1.5 |
| Cuisine Purity (per cluster) | > 0.60 |
| Cluster Coherence (expert) | Qualitative "coherent" |

---

## Implementation Plan (Phase 5.2)

### Week 1: Feature Engineering & Splits
- [ ] Build recipe feature matrix: TF-IDF ingredients (max_features=2000) + cuisine/course/diet one-hot
- [ ] Build ingredient feature matrix (for substitution): nutritional vectors + food_group + preparation_state
- [ ] Implement recipe_id-based stratified splits (stratify by cuisine)
- [ ] Verify no leakage across splits

### Week 2: Baseline Implementation
- [ ] Implement cuisine-match + ingredient Jaccard baseline
- [ ] Implement TF-IDF cosine similarity baseline
- [ ] Implement cuisine-matched random baseline
- [ ] Build evaluation framework (Precision@k, diversity, coverage)

### Week 3: Clustering & Evaluation
- [ ] Build clustering feature matrix (TF-IDF + metadata)
- [ ] Run HDBSCAN + K-means baseline
- [ ] Compute internal metrics (silhouette, DB-index)
- [ ] Expert review of cluster coherence

### Week 4: Documentation & Reporting
- [ ] Compare all methods on test set
- [ ] Document leakage prevention measures
- [ ] Produce Stage 5.2 deliverables

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| No ground truth relevance labels | Certain | High | Use proxy relevance (cuisine/ingredient overlap); document limitation |
| Cuisine imbalance (Indian 1157 vs others) | Certain | Medium | Stratified splits; per-cuisine metrics |
| High-dimensional sparse ingredients | Certain | Medium | TF-IDF max_features=2000; feature selection |
| No user feedback for validation | Certain | High | Offline proxy metrics only; document clearly |
| Nutrition features not ready | High | Medium | Run experiments without nutrition first; add when Phase 3.6 done |
| Clustering evaluation subjective | Medium | Medium | Expert review + internal metrics |

---

## Deliverables for Phase 5.1 (This Stage)

| Deliverable | Path | Status |
|-------------|------|--------|
| Dataset Feasibility Audit | `reports/phase5/stage5_1_dataset_feasibility_audit.md` | ✅ Complete |
| ML Problem Definitions | `reports/phase5/stage5_1_ml_problem_definitions.md` | ✅ Complete |
| Target & Feature Inventory | `reports/phase5/stage5_1_target_and_feature_inventory.csv` | ✅ Complete |
| Experiment Recommendation | `reports/phase5/stage5_1_experiment_recommendation.md` | ✅ Complete (this doc) |

---

## Next Task: Phase 5.2 Feature Engineering

**Immediate Actions:**
1. Build recipe feature matrix (TF-IDF ingredients + structured metadata)
2. Build ingredient feature matrix (for substitution problem)
3. Implement stratified train/val/test splits by recipe_id
4. Implement baseline recommenders (cuisine-match, ingredient Jaccard, random)
5. Set up evaluation framework (Precision@k, diversity, coverage)

**Dependencies:** None - all data available now.

---

*End of Experiment Recommendation*