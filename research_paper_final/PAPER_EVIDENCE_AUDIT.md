# Evidence audit — IEEE_Final_Research_Paper.tex

Every number printed in the paper is traced below to a frozen artifact of the original
project (`../`, untouched). Status codes:

- **M** — measured directly from the artifact (regenerated here, value re-read).
- **I** — read from implementation source code (behaviour of the delivered program).
- **P** — derived from a project formula or definition, not independently validated
  against ground truth (the derivation is shown in the paper).

Reproduction commands assume the original project root as working directory.

## 1. Corpus, parsing and reference data

| Paper statement | Value | Source artifact / code | Status |
|---|---|---|---|
| Raw recipe records | 6,871 | `data/processed/recipes.parquet` (before malformed-row removal) | M |
| Analytic recipes | 6,865 | same file, after removal | M |
| Cuisines / courses / diet labels | 75 / 10 / 20 | same file, distinct counts of `cuisine`, `course`, `diet` | M |
| Parsed ingredient rows | 90,862 | `data/interim/phase2/parsed_recipe_ingredients.parquet` | M |
| Distinct ingredient names | 13,049 | same file | M |
| Parsed-row schema width | 22 fields | same file, column count | M |
| Exact parses | 54,903 (60.4 %) | same file, `parse_status == exact` | M |
| Approximate parses | 29,980 (33.0 %) | same file, `approx` | M |
| Range parses | 1,673 (1.8 %) | same file, `range` | M |
| Unquantified | 4,306 (4.7 %) | same file, `unquantified` | M |
| Rows with resolved gram weight | 1,299 (1.43 %) | same file, `weight_g.notna()` | M |
| Preparation state unspecified | 88.6 % of rows | same file, `prep_state` null / `unspecified` | M |
| IFCT foods / food groups / nutrient fields | 528 / 18 / 9 | `data/interim/ifct_final_candidate/ifct_table1_candidate.parquet` (18 stored columns incl. metadata) | M |
| IFCT fibre + available carbohydrate both missing | 222 of 528 (42.0 %) | same file | M |
| IFCT edible-portion factors present | 180 of 528 (34.1 %) | same file | M |
| INDB dishes × columns | 1,014 × 86 | `data/processed/indb_foods.csv` | M |
| Candidate mapping pairs generated | 119,474 | `reports/phase5/` IFCT candidate-generation output | M |
| Pairs without any candidate | 63,244 | same | M |
| Approved mappings | 0 | approved-mapping store (empty); enforced by `src/recommendation/` gate | M |
| Automated nutrition tests | 42 | project test suite for the nutrition engine | M |

## 2. Splits and evaluation protocol

| Paper statement | Value | Source | Status |
|---|---|---|---|
| Split sizes | 4,783 / 1,025 / 1,025 | `data/artifacts/recommendation/splits/split_stats.json` | M |
| Split percentages | 69.7 / 14.9 / 14.9 % | computed from the above over 6,865 | P (derived) |
| Cuisines retained at recipe level | 63 | same | M |
| Recipes dropped by the stratum minimum | 32 | same | M |
| Seed | 42 | `run_simple_experiments.py`, `run_baseline_experiments.py` | I |
| Queries evaluated | first 50 test recipes (`test_ids[:50]`) | `run_simple_experiments.py` — **not a random sample**, disclosed in the paper | I |
| Coverage denominator | first 100 catalogue recipes, top-20 lists | `src/recommendation/evaluation.py` | I |
| Latency definition | harness total seconds ÷ 50 | `reports/phase5/experiments/results/*.json` (`time_seconds`) | M |
| Latency values (ms) | 110.4 / 390.0 / 208.1 / 180 | same (180 ms for the deployed ranker taken from the phase-5 record) | M |

## 3. Recommendation results (Table III, Fig. 3, Fig. 4)

| Method | P@5 | R@5 | Div@10 | Cov@20 | Latency | Source | Status |
|---|---|---|---|---|---|---|---|
| Random | 0.128 | 0.000593 | 0.958 | 0.254 | 110.4 ms | `baseline_experiments.json` | M |
| Cuisine match | 0.904 | 0.011273 | 0.824 | 0.225 | 390.0 ms | same | M |
| Jaccard | 0.548 | 0.004591 | 0.773 | 0.220 | 208.1 ms | same | M |
| Weighted (deployed) | 0.996 | 0.015665 | 0.869 | 0.234 | 180 ms | `content_based_experiments.json` | M |

Composite Φ (Eq. 11) recomputed here from the measured inputs with the reliability term
fixed at its documented value of 1.0: **0.398 / 0.553 / 0.473 / 0.631**
(random / cuisine / Jaccard / weighted). Without the reliability term the values are
0.298 / 0.453 / 0.373 / 0.531. The composite recorded earlier in the project summary
(0.182 / 0.441 / 0.380 / 0.595) is **not reproducible** from the project's own formula
and is not used anywhere in the paper.

## 4. Clustering (Table IV, Fig. 5)

| k | Silhouette | Davies–Bouldin | Largest cluster | Source | Status |
|---|---|---|---|---|---|
| K-Means 20 | 0.0388 | 4.111 | 655 | `clustering_experiments.json` | M |
| K-Means 50 | 0.0469 | 3.603 | 287 | same | M |
| K-Means 100 | 0.0414 | 3.187 | 201 | same | M |
| Agglomerative 50 | 0.0172 | 4.214 | 1,516 | same | M |
| Agglomerative 100 | 0.0244 | 3.605 | 613 | same | M |

Feature basis: combined feature matrix reduced to 20 principal components, seed 42.

## 5. Claims about the implementation (Section III-E, Section V-E)

| Paper claim | Evidence | Status |
|---|---|---|
| Ranking score is `S = 0.4J + 0.3C + 0.15K + 0.15D` with literal weights | `src/recommendation/retrieval_pipeline.py`, `recommend()` | I |
| `use_tfidf` is accepted as a parameter and never used in ranking | same function; the flag is stored but no branch reads it | I |
| TF-IDF is fitted and used only by the clustering study | same module; matrix consumed in `experiments/` clustering path | I |
| The experiment label `tfidf_only` is a misnomer | `run_simple_experiments.py` label vs. `recommend()` code path | I |
| Four nominal weight configurations produce identical metrics | `reports/phase5/stage5_3_2_final_metric_correction.md` | M |
| Proxy relevance `ρ = 0.5J + 0.2C + 0.15K + 0.15D ≥ 0.3` | `src/recommendation/evaluation.py` | I |
| Metadata agreement alone scores 0.5 ≥ 0.3, so it is sufficient for relevance | arithmetic on the above; derived in Section V-B | P (derivation) |
| `D` in the proxy is an overlap coefficient while Eq. (4) uses Jaccard | both files compared | I |
| Nutrition engine returns `NO_MAPPED_INGREDIENTS` when the approved store is empty | `src/recommendation/` nutrition path + 42 tests | I/M |

## 6. Error analysis (Section V-C)

| Statement | Value | Source | Status |
|---|---|---|---|
| Inspected queries | 20 | phase-5 error-analysis record | M |
| Recommended items crossing a cuisine boundary | 47 | same | M |
| Queries containing only generic terms | 16 of 20 | same | M |

## 7. Statements the paper deliberately does not make

| Withheld claim | Reason |
|---|---|
| Any recipe-level energy, protein or micronutrient total | Zero approved IFCT mappings and 1.43 % mass coverage; the engine abstains by design. |
| Nutrient-accuracy or diet-quality improvement | Never measured; no human or clinical evaluation was run. |
| "TF-IDF-based ranking" | Contradicted by `recommend()`; the paper reports the matrix used and the score actually computed. |
| A validated composite utility score | The reliability term was never defined or measured and is held at 1.0. |
| Sensitivity of results to ranking weights | The four configurations are numerically identical, which is a defect, not evidence. |
| Generalisation beyond the 50-query sample | Queries are the first 50 test recipes under a proxy that shares features with the models it scores. |

## 8. Figures

All figures are generated by `figures/generate_figures.py`, which reads only frozen
JSON/parquet artifacts (no hand-entered numbers) and writes 600 dpi PNGs plus
`figure_data_summary.json`. Diagrams (Figs. 1 and 3) are drawn from the code paths cited
in Section III; no terminal output or code screenshots appear anywhere.
