# Phase 3 Stage 1: Confidence Policy

**Date:** 2026-11-17  
**Phase:** 3 — Stage 1  
**Status:** Design Document — For Review

---

## 1. Confidence Policy Overview

This document defines the confidence policy for the IFCT ingredient matching system. It establishes measurable acceptance conditions, threshold calibration methodology, and explicitly distinguishes between parser accuracy, unit conversion accuracy, source reconciliation accuracy, and source reconciliation accuracy.

---

## 1. Confidence Level Definitions

### 1.1 Confidence Levels

| Level | Score Range | Action | Use Case |
|-------|-------------|--------|----------|
| **HIGH** (Auto-accept) | ≥ 0.90 | Auto-accept, log provenance | EXACT_MATCH, SYNONYM_MATCH (conf≥0.95), TRANSLITERATION (conf≥0.90), REGIONAL_VARIANT (conf≥0.90) |
| **MEDIUM** (Review) | 0.70 – 0.89 | Flag for human review | HIGH_CONFIDENCE_MATCH, PREP_STATE_COMPATIBLE, EDIBLE_PART_COMPATIBLE, VARIETY_MATCH, SPECIES_MATCH, COMPOSITE_DECOMPOSED |
| **LOW** (Review) | 0.50 – 0.69 | Flag for human review | AMBIGUOUS_MATCH, weak candidates |
| **UNMATCHED** | < 0.50 | Log, no match | No candidate ≥ 0.50 |

### 1.2 Confidence vs. Probability

> **Critical Principle:** A similarity score is **not** a probability of correctness unless calibrated and validated against independent ground truth.

- **Similarity score** = weighted composite of string similarity, synonym confidence, food group compatibility, prep state compatibility
- **Confidence level** = calibrated mapping from similarity score to reliability tier
- **Probability of correctness** = only claimable after calibration against independent ground truth (Stage 4 gold standard)

**Initial Thresholds (Subject to Calibration):**

| Level | Score Range | Calibration Status |
|-------|-------------|-------------------|
| HIGH | ≥ 0.90 | Initial — requires calibration |
| MEDIUM | 0.70 – 0.89 | Initial — requires calibration |
| LOW | 0.50 – 0.69 | Initial — requires calibration |
| UNMATCHED | < 0.50 | N/A |

---

## 2. Component Scoring Weights

### 2.1 Scoring Components

The composite similarity score is a weighted sum:

```
score = w1 * exact_match + w2 * synonym_conf + w3 * token_similarity + w4 * food_group_compat + w5 * prep_state_compat
```

| Component | Weight | Range | Description |
|-----------|--------|-------|-------------|
| `exact_match` | 1.0 | {0, 1} | Binary: normalized string == IFCT food_name |
| `synonym_conf` | 0.95 | [0, 1] | Synonym dictionary confidence |
| `token_similarity` | 0.70 | [0, 1] | Jaccard on normalized tokens |
| `food_group_compat` | 0.15 | {0, 0.5, 1.0} | IFCT food group compatibility |
| `prep_state_compat` | 0.10 | {0, 0.5, 1.0} | Prep state compatibility |

**Note:** Weights are initial values. Final calibration requires gold-standard evaluation (Stage 4).

### 2.2 Score Components Detail

#### 2.2.1 Exact Match
- Binary: 1.0 if normalized ingredient == IFCT `food_name` (case/whitespace insensitive)
- 0.0 otherwise

#### 2.2.2 Synonym Confidence
- From `ingredient_synonyms.csv` `confidence` column
- 0.95–1.00 for verified synonyms
- 0.85–0.94 for regional variants (review required)
- 0.0 if no synonym match

#### 2.2.3 Token Similarity
- Jaccard index on normalized tokens (whitespace-delimited)
- Normalized: lowercase, punctuation removed, parentheses content preserved
- Range: 0.0 (no overlap) to 1.0 (identical token sets)

#### 2.2.4 Food Group Compatibility
| Compatibility | Score | Condition |
|---------------|-------|-----------|
| Same IFCT food group | 1.0 | Exact group match |
| Related group (e.g., VEGETABLES ↔ LEAFY VEGETABLES) | 0.5 | Semantic proximity |
| Unrelated | 0.0 | Different major categories |

Group relatedness matrix defined in `ingredient_taxonomy.py`.

#### 2.2.5 Preparation State Compatibility
| Compatibility | Score | Condition |
|---------------|-------|-----------|
| Compatible (raw↔raw, powder↔powder) | 1.0 | Same prep category |
| Compatible (fresh ↔ raw) | 1.0 | Fresh treated as raw |
| Unknown prep state | 0.5 | No prep descriptor |
| Incompatible (raw ↔ cooked) | 0.0 | Explicit prep conflict |
| Unknown | 0.0 | Explicit conflict |

---

## 2. Confidence Calibration Methodology

### 2.1 Calibration Requirements

**Thou shalt not claim accuracy without calibration.**

| Requirement | Status | Method |
|-------------|--------|--------|
| Gold standard dataset | Required | Stage 4 manual review (≥200 items) |
| Threshold calibration | Required | ROC analysis on gold standard |
| Per-category accuracy | Required | Per-match-type confusion matrix |
| Cross-validation | Required | k-fold on gold standard |

**Calibration Procedure:**
1. Build gold standard: ≥200 manually verified (ingredient, IFCT_code) pairs
2. Stratify by match type (EXACT, SYNONYM, TRANSLITERATION, REGIONAL, TOKEN, FUZZY)
- 2. Compute ROC curves per category
- 3. Select thresholds maximizing F1 per category
- 4. Report per-category precision/recall/F1
- 5. Lock thresholds for production

### 2.2 Calibration Data Requirements

| Requirement | Minimum | Notes |
|-------------|---------|-------|
| Gold standard size | ≥ 200 | Stratified by match type |
| EXACT_MATCH samples | ≥ 50 | Easy to obtain |
| SYNONYM_MATCH samples | ≥ 50 | From synonym dict |
| TRANSLITERATION samples | ≥ 20 | Hindi/English pairs |
| REGIONAL_VARIANT | ≥ 20 | Regional names |
| HIGH_CONFIDENCE | ≥ 30 | Variety/species/prep |
| AMBIGUOUS | ≥ 20 | Known ambiguous cases |
| UNMATCHED | ≥ 30 | Known absent from IFCT |

**Total minimum: 220 samples** (recommend 300+ for safety)

---

## 3. Accuracy Claims — What We Can and Cannot Say

### 3.1 What We Can Claim (After Calibration)

| Claim | Condition | Evidence Required |
|-------|-----------|-------------------|
| "Parser accuracy: X%" | After calibration | Confusion matrix on gold standard |
| "Unit conversion accuracy: Y%" | After calibration | 30+ spot-checks vs USDA/IFCT |
| "Source reconciliation accuracy: Z%" | After calibration | Reconciliation audit |
| "Parser accuracy: 100% on test set" | After calibration | Test set results |

### 3.2 What We Cannot Claim

| Claim | Why Not |
|-------|---------|
| "100% accuracy" | No system is perfect; unverifiable |
| "Probability of correctness = X%" | Similarity ≠ probability without calibration |
| "Nutrition accuracy: X%" | Depends on IFCT data quality, cooking effects, weight resolution |
| "Better than USDA" | Different scope, different foods |
| "Production ready" | Requires Stage 4 validation |

### 3.2 Accuracy Reporting Template

| Metric | Value | Confidence Interval | Method |
|--------|-------|---------------------|--------|
| Parser EXACT accuracy | X% | [X%, Y%] | Gold standard n=X |
| Parser APPROXIMATE accuracy | X% | [X%, Y%] | Gold standard n=X |
| Synonym match precision | X% | [X%, Y%] | Gold standard n=X |
| Synonym match recall | X% | [X%, Y%] | Gold standard n=X |
| Transliteration precision | X% | [X%, Y%] | Gold standard n=X |
| Regional variant precision | X% | [X%, Y%] | Gold standard n=X |
| Household conversion accuracy | X% | [X%, Y%] | 30 spot-checks vs USDA |
| Reconciliation accuracy | X% | [X%, Y%] | Audit of 100 samples |

---

## 4. Calibration Procedure

### 4.1 Gold Standard Construction (Stage 4)

```python
# Gold standard schema
gold_standard = [
    {
        "input_text": "toor dal",
        "expected_ifct_code": "B001",  # pigeon pea
        "expected_match_status": "SYNONYM_MATCH",
        "category": "pulse",
        "notes": "Common synonym"
    },
    {
        "input_text": "हल्दी",
        "expected_ifct_code": "S056",  # turmeric
        "expected_match_status": "TRANSLITERATION_MATCH",
        "category": "spice",
        "notes": "Devanagari input"
    },
    # ... 200+ items
]
```

### 4.2 Calibration Steps

1. **Collect Gold Standard** (Stage 4)
   - Minimum 200 manually verified (ingredient, IFCT_code) pairs
   - Stratified: 50 EXACT, 50 SYNONYM, 20 TRANSLITERATION, 20 REGIONAL, 30 HIGH_CONFIDENCE, 20 AMBIGUOUS, 30 UNMATCHED

2. **Run Matcher on Gold Standard**
   ```python
   predictions = matcher.predict_batch(gold_standard_inputs)
   ```

3. **Compute Per-Category Metrics**
   ```python
   for category in MatchStatus:
       tp = sum(1 for p, g in zip(preds, gold) if p == g == category)
       fp = sum(1 for p, g in zip(preds, gold) if p == category and g != category)
       fn = sum(1 for p, g in zip(preds, gold) if p != category and g == category)
       precision = tp / (tp + fp) if (tp + fp) > 0 else 0
       recall = tp / (tp + fn) if (tp + fn) > 0 else 0
       f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
   ```

3. **Select Thresholds**
   - Maximize F1 per category
   - Ensure recall ≥ 0.90 for AUTO-ACCEPT categories
   - Ensure precision ≥ 0.95 for AUTO-ACCEPT categories

4. **Lock Thresholds**
   - Save calibrated thresholds to config
   - Lock for production use

4. **Report**
   - Per-category precision, recall, F1
   - Overall accuracy
   - Confusion matrix
   - Failure analysis (top 20 errors)

---

## 2.3 Accuracy Claims — What We Can and Cannot Say

### What We CAN Claim (After Calibration)

| Claim | Condition | Evidence |
|-------|-----------|----------|
| "Parser EXACT accuracy: X%" | After calibration | Confusion matrix on gold standard (n≥50) |
| "Parser APPROXIMATE accuracy: Y%" | After calibration | Gold standard (n≥50) |
| "Synonym match precision: X%" | After calibration | Gold standard (n≥50) |
| "Synonym match recall: Y%" | After calibration | Gold standard (n≥50) |
| "Transliteration precision: X%" | After calibration | Gold standard (n≥20) |
| "Household conversion accuracy: X%" | After calibration | 30 spot-checks vs USDA/IFCT |
| "Reconciliation accuracy: X%" | After calibration | 100-sample audit |

### What We CANNOT Claim

| Claim | Why Not |
|-------|---------|
| "100% accuracy" | No system is perfect; unverifiable |
| "Probability of correctness = X%" | Similarity ≠ probability without calibration |
| "Nutrition accuracy: X%" | Depends on IFCT data quality, cooking effects, weight resolution |
| "Better than USDA" | Different scope, different foods |
| "Production ready without validation" | Requires Stage 4 validation |

---

## 3. Calibration Status Tracker

| Component | Status | Gold Standard Size | Target |
|-----------|--------|-------------------|--------|
| EXACT_MATCH | ❌ Not Calibrated | 0/50 | ≥50 |
| SYNONYM_MATCH | ❌ Not Calibrated | 0/50 | ≥50 |
| TRANSLITERATION_MATCH | ❌ Not Calibrated | 0/20 | ≥20 |
| REGIONAL_VARIANT | ❌ Not Calibrated | 0/20 | ≥20 |
| HIGH_CONFIDENCE_MATCH | ❌ Not Calibrated | 0/30 | ≥30 |
| AMBIGUOUS_MATCH | ❌ Not Calibrated | 0/20 | ≥20 |
| UNMATCHED | ❌ Not Calibrated | 0/30 | ≥30 |
| **Total** | **Not Calibrated** | **0/220** | **≥220** |

**Status:** 🔴 **NOT CALIBRATED** — Cannot claim accuracy percentages

---

## 4. Calibration Roadmap

### Stage 4: Gold Standard Construction
1. **Sample Selection** — Stratified sample from 90,862 canonical records
2. **Manual Annotation** — 2+ annotators, adjudication for disagreements
- Target: 300 samples minimum
- Stratification: 50 EXACT, 50 SYNONYM, 20 TRANSLITERATION, 20 REGIONAL, 30 HIGH_CONFIDENCE, 20 AMBIGUOUS, 30 UNMATCHED
3. **Adjudication** — 2 annotators, 3rd adjudicator for conflicts
- Target κ ≥ 0.90 inter-annotator agreement
4. **Calibration Run** — Run matcher on gold standard, compute metrics
5. **Threshold Optimization** — Grid search for per-category F1 max
5. **Lock Thresholds** — Save to config, version control
6. **Document** — Update confidence policy with calibrated thresholds

### Calibration Timeline
| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Gold standard construction | 1 week | Annotator availability |
| Annotation | 1 week | 2 annotators |
| Adjudication | 2 days | 3rd adjudicator |
| Calibration run | 1 day | Gold standard ready |
| Documentation | 0.5 day | Calibration complete |
| **Total** | **~10 days** | After Stage 3 implementation |

---

## 4. Accuracy Reporting Template

### 4.1 Per-Category Report Template

```
# Matcher Calibration Report

## Executive Summary
- Gold Standard Size: N samples
- Inter-annotator Agreement: κ = X.XX
- Overall Accuracy: X% (95% CI: [X%, Y%])
- Overall F1: X.XX

## Per-Category Performance

| Category | Samples | Precision | Recall | F1 | Threshold |
|----------|---------|-----------|------|----|-----------|
| EXACT_MATCH | N | X% | Y% | Z% | 1.0 |
| SYNONYM_MATCH | N | X% | Y% | Z% | ≥0.95 |
| TRANSLITERATION | N | X% | Y% | Z% | ≥0.90 |
| REGIONAL_VARIANT | N | X% | Y% | Z% | ≥0.90 |
| HIGH_CONFIDENCE | N | X% | Y% | Z% | ≥0.70 |
| AMBIGUOUS | N | X% | Y% | Z% | 0.50-0.69 |
| UNMATCHED | N | X% | Y% | Z% | <0.50 |

## Confusion Matrix (Normalized)
[Confusion matrix heatmap]

## Failure Analysis
Top 10 error patterns:
1. Error type: count (X%)
2. ...

## Threshold Recommendations
| Category | Current | Recommended | Rationale |
|----------|---------|-------------|-----------|
| SYNONYM | 0.95 | 0.95 | Already optimal |
| TRANSLITERATION | 0.90 | 0.88 | Slightly lower for recall |
| REGIONAL | 0.90 | 0.92 | Slightly higher for precision |
| HIGH_CONFIDENCE | 0.70 | 0.72 | Slightly higher |

## Limitations
- Gold standard size: N samples (target: 300)
- Inter-annotator agreement: κ = X.XX
- Categories with <20 samples: [list]
- Classes with zero samples: [list]

## Next Steps
1. Expand gold standard to 300 samples
2. Re-calibrate after synonym dictionary expansion
3. Add per-food-group calibration
```

---

## 5. Accuracy Claims — Final Policy

### What We CAN Say (After Calibration)

| Claim | Condition |
|-------|-----------|
| "Parser EXACT accuracy: X% (95% CI: [X%, Y%])" | After calibration, n≥50 EXACT samples |
| "Synonym match precision: X% (95% CI: [X%, Y%])" | After calibration, n≥50 |
| "Synonym match recall: X% (95% CI: [X%, Y%])" | After calibration, n≥50 |
| "Transliteration precision: X% (95% CI: [X%, Y%])" | After calibration, n≥20 |
| "Household conversion accuracy: X% (n=30 spot-checks vs USDA/IFCT)" | 30+ manual verifications |
| "Reconciliation accuracy: X% (n=100 audit sample)" | Manual audit |
| "Zero discrepancies in reconciliation" | Audit of 90,862 records |

### What We CANNOT Say

| Claim | Reason |
|-------|--------|
| "100% accuracy" | Impossible; no system is perfect |
| "Probability of correctness = X%" | Similarity ≠ probability without calibration |
| "Nutrition accuracy: X%" | Depends on IFCT data quality, cooking effects, weight resolution |
| "Better than USDA" | Different scope, different foods, different purpose |
| "Production ready without validation" | Requires Stage 4 validation |

---

## 6. Confidence Policy Summary

| Principle | Policy |
|-----------|--------|
| **Similarity ≠ Probability** | Never present similarity score as probability of correctness without calibration |
| **Thresholds are Initial** | All thresholds are initial estimates; must be calibrated |
| **Calibration Required** | No accuracy claims without gold-standard calibration |
| **Per-Category Metrics** | Report precision/recall/F1 per match type |
| **Gold Standard Required** | ≥200 samples, stratified, κ≥0.90 IAA |
| **Calibration Lock** | Thresholds locked after calibration; version controlled |
| **Re-calibration** | Required after synonym dict expansion, IFCT update |
| **Documentation** | All calibration runs documented with gold standard version |

---

## 6. Calibration Status Tracker

| Component | Status | Gold Std Size | Target | Last Calibrated |
|-----------|--------|---------------|--------|-----------------|
| EXACT_MATCH | 🔴 Not Calibrated | 0/50 | ≥50 | Never |
| SYNONYM_MATCH | 🔴 Not Calibrated | 0/50 | ≥50 | Never |
| TRANSLITERATION | 🔴 Not Calibrated | 0/20 | ≥20 | Never |
| REGIONAL_VARIANT | 🔴 Not Calibrated | 0/20 | ≥20 | Never |
| HIGH_CONFIDENCE | 🔴 Not Calibrated | 0/30 | ≥30 | Never |
| AMBIGUOUS | 🔴 Not Calibrated | 0/20 | ≥20 | Never |
| UNMATCHED | 🔴 Not Calibrated | 0/30 | ≥30 | Never |
| **TOTAL** | 🔴 **NOT CALIBRATED** | **0/220** | **≥220** | **Never** |

---

## Final Policy Statement

> **No accuracy claims will be made without completed calibration against an independently constructed gold standard.**
> 
> All similarity scores are **ranking indicators**, not calibrated probabilities.
> 
> Accuracy claims require:
> 1. Gold standard construction (≥200 samples)
> 2. Inter-annotator agreement (κ ≥ 0.90)
> 3. Per-category precision/recall/F1 reporting
> 4. Threshold locking with version control
> 4. Documentation of limitations and failure modes
> 
> **Until calibration is complete, all confidence levels are INITIAL ESTIMATES ONLY.**