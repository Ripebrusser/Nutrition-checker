# Phase 5.1: ML Problem Definitions

**Date:** 2026-11-18  
**Objective:** Define and evaluate candidate ML problems for the project

---

## 1. Candidate ML Problems Evaluated

### Problem 1: Content-Based Recipe Recommendation

| Aspect | Detail |
|--------|--------|
| **Problem Type** | Content-based filtering / Item-item similarity |
| **Input** | Recipe features: ingredients (normalized), cuisine, course, diet_labels, prep/cook times, nutritional profile (estimated) |
| **Target** | Similar recipes (no explicit labels - unsupervised/semi-supervised) |
| **Dataset** | `recipes.parquet` + `parsed_recipe_ingredients.parquet` + IFCT nutrition estimates |
| **Target Availability** | ❌ No explicit relevance labels; similarity-based |
| **Supervised Learning** | ❌ Not directly - no labeled pairs |
| **Unsupervised Learning** | ✅ Yes - content-based similarity, clustering |
| **Approach** | TF-IDF on ingredients + cuisine/course/diet one-hot + nutritional vectors → cosine similarity / k-NN |
| **Baseline** | Popularity-based (most viewed/cooked), cuisine-based, random |
| **Valid Metrics** | Precision@k (offline), diversity, coverage, novelty (offline); CTR, dwell time (online - not available) |
| **Limitations** | No ground truth relevance; cold start for new recipes; no user feedback loop |
| **Feasibility** | **FEASIBLE NOW** - All features available |

---

### Problem 2: Recipe Ranking by Nutritional Constraints

| Aspect | Detail |
|--------|--------|
| **Problem Type** | Constraint optimization / Learning to rank |
| **Input** | Recipe nutritional profile (estimated), user constraints (calories, protein min/max, carb max, diet restrictions) |
| **Target** | Ranked list of recipes satisfying constraints |
| **Dataset** | `recipes.parquet` + estimated nutrition from IFCT mappings |
| **Target Availability** | ❌ No explicit ranking labels |
| **Supervised Learning** | ❌ No labeled rankings |
| **Unsupervised/Rule-based** | ✅ Constraint satisfaction / Multi-objective optimization |
| **Approach** | Filter recipes by hard constraints (diet, allergies) → score by nutritional distance to targets → rank |
| **Baseline** | Random filter, calorie-only filter, macro-only filter |
| **Valid Metrics** | Constraint satisfaction rate, nutritional distance (MAE), diversity |
| **Limitations** | Estimated nutrition has gaps (fibre/carb 42% missing); gram weights 98.5% missing |
| **Feasibility** | **FEASIBLE AFTER DATA PREP** - Need nutrition estimation pipeline (Phase 3.6) |

---

### Problem 3: Ingredient Substitution Recommendation

| Aspect | Detail |
|--------|--------|
| **Problem Type** | Item-item substitution / Similarity search |
| **Input** | Ingredient features: name, category, preparation_state, IFCT food_group, nutritional profile, culinary role |
| **Target** | Suitable substitutes for a given ingredient in a recipe context |
| **Dataset** | `ifct_match_candidates.parquet`, `disambiguated_ingredients.parquet`, `ifct_table1_candidate.parquet` |
| **Target Availability** | ❌ No verified substitution pairs/labels |
| **Supervised Learning** | ❌ No labeled substitution pairs |
| **Unsupervised/Rule-based** | ✅ Similarity-based (nutritional + culinary + preparation compatibility) |
| **Approach** | Nutritional similarity (cosine on nutrient vectors) + culinary compatibility rules (prep_state, food_group) + recipe context |
| **Baseline** | Same food_group, same preparation_state, random from category |
| **Valid Metrics** | Nutritional distance, culinary compatibility score (expert eval), user acceptance (not available) |
| **Limitations** | No ground truth substitutions; culinary knowledge not encoded; context-dependent |
| **Feasibility** | **FEASIBLE AFTER DATA PREP** - Needs culinary compatibility rules + nutritional similarity |

---

### Problem 4: Recipe Clustering by Cuisine and Ingredient Composition

| Aspect | Detail |
|--------|--------|
| **Problem Type** | Unsupervised clustering / Dimensionality reduction |
| **Input** | Recipe features: ingredient presence (TF-IDF), cuisine, course, diet_labels, nutritional profile |
| **Target** | Cluster assignments (no labels - discovery) |
| **Dataset** | `recipes.parquet` + `parsed_recipe_ingredients.parquet` |
| **Target Availability** | N/A - Unsupervised |
| **Supervised Learning** | N/A |
| **Unsupervised Learning** | ✅ Primary approach |
| **Approach** | TF-IDF on ingredients (13,049 unique) + cuisine/course/diet one-hot → PCA/UMAP → K-means / HDBSCAN |
| **Baseline** | Cuisine-based grouping, course-based grouping |
| **Valid Metrics** | Silhouette score, Davies-Bouldin, cluster coherence (expert eval), cuisine purity |
| **Limitations** | No ground truth clusters; high-dimensional sparse ingredients |
| **Feasibility** | **FEASIBLE NOW** - All features available |

---

### Problem 5: Portion-Size Prediction

| Aspect | Detail |
|--------|--------|
| **Problem Type** | Regression (grams per serving) |
| **Input** | Recipe features: ingredient list, quantities, units, cuisine, course, total_time, servings |
| **Target** | Gram weight per serving (per ingredient + total) |
| **Dataset** | `parsed_recipe_ingredients.parquet` (gram_weight target) |
| **Target Availability** | ❌ 98.5% MISSING (1,299 / 90,862 have gram_weight) |
| **Supervised Learning** | ❌ INSUFFICIENT TARGETS (1.4% coverage) |
| **Unsupervised/Semi-supervised** | ⚠️ Possible but unreliable |
| **Approach** | Household measure conversion rules (existing), ML on 1,299 samples (insufficient) |
| **Baseline** | Household measure conversion (existing pipeline) |
| **Valid Metrics** | MAE, RMSE, MAPE (on 1,299 samples - not representative) |
| **Limitations** | Severe target sparsity (1.4%); conversion pipeline already exists |
| **Feasibility** | **NOT JUSTIFIED** - Insufficient training data; rule-based pipeline exists |

---

### Problem 6: User Preference Prediction

| Aspect | Detail |
|--------|--------|
| **Problem Type** | Classification / Ranking |
| **Input** | User features (demographics, health metrics, diet_labels, allergies) + recipe features |
| **Target** | User preference score / probability of selection |
| **Dataset** | ❌ NO USER DATA |
| **Target Availability** | ❌ NO USER DATA |
| **Supervised Learning** | ❌ IMPOSSIBLE |
| **Feasibility** | **NOT JUSTIFIED** - No user data exists |

---

### Problem 7: Personalized Meal Recommendation

| Aspect | Detail |
|--------|--------|
| **Problem Type** | Multi-objective recommendation / Constrained optimization |
| **Input** | User profile (health metrics, preferences, restrictions) + Recipe pool with nutrition |
| **Target** | Daily/weekly meal plan meeting nutritional targets |
| **Dataset** | Requires: User profiles (❌), Nutrition engine (Phase 3.6+), Recipe pool (✅) |
| **Target Availability** | ❌ No user data; nutrition engine not ready |
| **Supervised Learning** | ❌ No user-meal interaction labels |
| **Approach** | Constraint optimization (nutritional targets + preferences) + content-based ranking |
| **Baseline** | Random meal plan, cuisine-filtered random, macro-targeted greedy |
| **Valid Metrics** | Nutritional target adherence, constraint satisfaction, diversity |
| **Limitations** | No user data for personalization; nutrition engine not ready (Phase 3.6+) |
| **Feasibility** | **REQUIRES NEW DATA** (user profiles) + Phase 3.6 completion |

---

## 2. Summary Comparison Table

| Problem | Data Available | Target Validity | ML Feasibility | Baseline | Evaluation | Priority |
|---------|----------------|-----------------|----------------|----------|------------|----------|
| 1. Content-Based Recipe Recommendation | ✅ Full | ❌ No labels (unsupervised) | ✅ FEASIBLE NOW | Popularity, cuisine-based | Precision@k, diversity, coverage | **HIGH** |
| 2. Recipe Ranking by Nutritional Constraints | ⚠️ Partial (nutrition est. needed) | ❌ No labels (optimization) | ⚠️ FEASIBLE AFTER DATA PREP | Calorie-only, macro-only | Constraint satisfaction, MAE | MEDIUM |
| 3. Ingredient Substitution | ⚠️ Partial (no substitution labels) | ❌ No labels | ⚠️ FEASIBLE AFTER DATA PREP | Food_group match, prep_state match | Nutritional distance, expert eval | MEDIUM |
| 4. Recipe Clustering | ✅ Full | N/A (unsupervised) | ✅ FEASIBLE NOW | Cuisine/course grouping | Silhouette, cuisine purity, expert eval | HIGH |
| 5. Portion-Size Prediction | ✅ Features | ❌ 98.5% missing | ❌ NOT JUSTIFIED | Household conversion (existing) | MAE/RMSE (on 1.4% data) | LOW |
| 6. User Preference Prediction | ❌ No user data | ❌ NO DATA | ❌ NOT JUSTIFIED | N/A | N/A | NONE |
| 7. Personalized Meal Recommendation | ⚠️ Partial (no user data, no nutrition engine) | ❌ No labels/user data | ❌ REQUIRES NEW DATA + PHASE 3.6 | Random, cuisine-filtered | Nutritional adherence | LOW (future) |

---

## 3. Classification Summary

| Classification | Problems |
|----------------|----------|
| **FEASIBLE NOW** | 1. Content-Based Recipe Recommendation, 4. Recipe Clustering |
| **FEASIBLE AFTER DATA PREPARATION** | 2. Recipe Ranking by Nutritional Constraints, 3. Ingredient Substitution |
| **REQUIRES NEW DATA** | 7. Personalized Meal Recommendation |
| **NOT JUSTIFIED** | 5. Portion-Size Prediction, 6. User Preference Prediction |

---

## 4. Recommended Experimental Direction

### Primary ML Problem: **Content-Based Recipe Recommendation (Problem 1)**

**Justification:**
- ✅ All required data available now (6,865 recipes, 13,049 unique ingredients, cuisine/course/diet labels)
- ✅ Well-defined problem with clear evaluation methodology
- ✅ Scientifically defensible: content-based filtering is established methodology
- ✅ Can be evaluated offline with proper metrics (Precision@k, diversity, coverage, novelty)
- ✅ Directly serves the project's core use case: "help users find recipes"
- ✅ Rule-based baseline (cuisine-based, ingredient-overlap) is implementable and defensible
- ❌ No user data needed - works with item-item similarity
- ❌ No fabrication of user ratings or interactions required

**Experimental Design:**
- **Features:** TF-IDF on normalized ingredients (13,049 vocab) + cuisine (75) one-hot + course (10) one-hot + diet_labels (20) multi-hot + estimated nutrition (Phase 3.6 output when available)
- **Model:** TF-IDF cosine similarity baseline → optionally learn metric (Siamese network) if supervision emerges
- **Evaluation:** Leave-one-recipe-out; Precision@5, @10; diversity (intra-list distance); coverage (% recipes recommendable)
- **Baseline:** Cuisine-matched random, ingredient Jaccard overlap, popularity proxy (recipe_id order)

---

### Secondary ML Problem: **Recipe Clustering by Cuisine and Ingredient Composition (Problem 4)**

**Justification:**
- ✅ Pure unsupervised - no labels needed
- ✅ Exploratory value: discover natural recipe groupings beyond cuisine labels
- ✅ Can reveal ingredient-based patterns that cross cuisine boundaries
- ✅ Useful for diversity in recommendation (avoid over-clustering)
- ✅ All features available now
- ✅ Evaluation via internal metrics (silhouette) + expert qualitative assessment

**Experimental Design:**
- **Features:** TF-IDF on ingredients (13,049 vocab, max_features=2000) + cuisine (75) + course (10) + diet_labels (20)
- **Dimensionality Reduction:** PCA → UMAP (2D/3D for visualization)
- **Clustering:** HDBSCAN (handles variable density) + K-means (baseline)
- **Evaluation:** Silhouette, Davies-Bouldin, cuisine purity per cluster, expert review of cluster coherence
- **Baseline:** Cuisine labels (75 classes), course labels (10 classes)

---

### Rule-Based Baseline: **Cuisine/Ingredient-Overlap Recipe Recommendation**

**Justification:**
- Required as honest baseline for any ML recommendation system
- Transparent, interpretable, no training needed
- Uses only existing data: cuisine match + ingredient Jaccard overlap
- Defensible as "traditional" approach before ML

**Implementation:**
```
score(recipe_a, recipe_b) = w1 * cuisine_match(a,b) + w2 * jaccard(ingredients_a, ingredients_b)
```
- cuisine_match = 1 if same cuisine, 0.5 if same region, 0 otherwise
- jaccard = |ingredients_a ∩ ingredients_b| / |ingredients_a ∪ ingredients_b|
- Weights tuned on held-out set (if any validation signal exists) or set a priori (e.g., w1=0.6, w2=0.4)

---

## 5. Next Steps: Phase 5.2 Feature Engineering

### Immediate Actions:
1. **Build recipe feature matrix:** TF-IDF on ingredients (max_features=2000) + structured metadata (cuisine, course, diet_labels)
2. **Build ingredient feature matrix:** For substitution problem - nutritional vectors, food_group, preparation_state
2. **Define train/validation/test splits:** By recipe_id (not ingredient lines) to prevent leakage; stratify by cuisine
3. **Implement baseline recommenders:** Cuisine-match, ingredient Jaccard, random
4. **Set up evaluation framework:** Precision@k, diversity, coverage, novelty metrics
5. **Document leakage prevention:** Recipe-level splits, no target leakage from IFCT match features

---

## 6. Final Recommendation Summary

| Decision | Rationale |
|----------|-----------|
| **Primary ML Problem** | Content-Based Recipe Recommendation - feasible now, defensible, serves core use case |
| **Secondary ML Problem** | Recipe Clustering - feasible now, exploratory value, unsupervised |
| **Rule-Based Baseline** | Cuisine/Ingredient-Overlap - transparent, no training, defensible |
| **Deferred** | Nutritional ranking, substitution, personalization - need Phase 3.6 + user data |
| **Rejected** | Portion prediction (insufficient targets), User preference (no user data) |

**Next Task:** Phase 5.2 Feature Engineering - Build recipe and ingredient feature matrices, define splits, implement baselines.

---

*End of ML Problem Definitions*