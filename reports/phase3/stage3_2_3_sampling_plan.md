# Stage 3.2.3: Sampling Plan (Corrected)

**Date:** 2026-11-18  
**Status:** Authoritative — based on Stage 2.3 frozen data

---

## 1. Population Overview

| Metric | Value |
|--------|-------|
| Total review units (corrected key) | 7,992 |
| Total review units (flawed key) | 7,165 |
| Difference | +827 units |

---

## 2. Population by Stratum

### 2.1 By Match Method (Corrected Key)

| Match Method | Population | % of Total |
|--------------|------------|------------|
| EXACT | 73 | 0.9% |
| SYNONYM | 39 | 0.5% |
| TOKEN_EQUIVALENT | 160 | 2.0% |
| TOKEN_SIMILARITY | 7,720 | 96.6% |
| FUZZY | 0 | 0.0% |
| **Total** | **7,992** | **100%** |

### 2.2 Population by Priority Band (Corrected Key)

| Priority Band | Score Range | Count | % of Total |
|---------------|-------------|-------|------------|
| Critical | 80–100 | 30 | 0.4% |
| High | 60–79 | 160 | 2.0% |
| Medium | 40–59 | 1,727 | 21.6% |
| Standard | 20–39 | 6,075 | 76.0% |
| Low | 0–19 | 0 | 0.0% |
| **Total** | | **7,992** | **100%** |

### 2.3 Cross-Tabulation: Match Method × Priority Band

| Match Method \ Priority Band | Critical | High | Medium | Standard | Low | Total |
|------------------------------|----------|------|--------|----------|-----|-------|
| EXACT | 25 | 0 | 0 | 48 | 0 | 73 |
| SYNONYM | 0 | 0 | 0 | 39 | 0 | 39 |
| TOKEN_EQUIVALENT | 5 | 12 | 34 | 123 | 0 | 160 |
| TOKEN_SIMILARITY | 0 | 148 | 1,693 | 5,872 | 0 | 7,720 |
| FUZZY | 0 | 0 | 0 | 0 | 0 | 0 |
| **Total** | **30** | **160** | **1,727** | **6,075** | **0** | **7,992** |

---

## 3. Sampling Design

### 3.1 Stratification Strategy

Stratification by: **match_method × priority_band**

Rationale: Match method and priority band are the primary determinants of review complexity and evidence requirements.

### 3.2 Sampling Rates by Stratum

| Stratum | Population | Rate | Min Samples | Samples |
|---------|------------|------|-------------|---------|
| ACCEPTED_EXACT | 30 | 20% | 10 | 10 |
| ACCEPTED_SYNONYM | 0 | 20% | 1 | 0 |
| REVIEW_REQ_EXACT | 43 | 10% | 5 | 5 |
| REVIEW_REQ_SYNONYM | 39 | 10% | 5 | 5 |
| REVIEW_REQ_TOKEN_EQUIV | 160 | 10% | 16 | 16 |
| REVIEW_REQ_TOKEN_SIM | 7,720 | 10% | **772** | 772 |
| REJECTED | 0 | 5% | 5 | 0 |
| AMBIGUOUS | 610 ingredients | 100% | All | All |
| UNMATCHED | 11,310 | 5% | 565 | 565 |
| CONFLICT | all | 100% | All | All |

**Total audit samples: ~1,379** (vs previous ~200–250)

### 2.4 Special Strata

| Stratum | Population | Rate | Method | Notes |
|---------|------------|------|--------|-------|
| AMBIGUOUS | 610 ingredients | 100% | Census | All ambiguous ingredients fully audited |
| CONFLICT | All | 100% | Census | All reviewer disagreements |
| AUTO_ACCEPTED | 3 | 100% | Census | Verify auto-accept logic |

---

## 3. Sampling Method

### 3.1 Method
**Stratified random sampling** with fixed random seed.

### 3.2 Implementation

```python
def draw_audit_sample(review_units: pd.DataFrame, 
                      decisions: pd.DataFrame, 
                      seed: int = 42) -> pd.DataFrame:
    """
    Draw stratified audit sample from review units.
    
    Args:
        review_units: DataFrame of all review units (corrected key)
        decisions: DataFrame of reviewer decisions
        seed: Random seed (default 42)
    
    Returns:
        DataFrame of sampled audit units
    """
    np.random.seed(seed)
    
    # Merge decisions with review units
    merged = review_units.merge(decisions, on='review_unit_id', how='inner')
    
    samples = []
    for stratum_name, (rate, min_n) in STRATA_CONFIG.items():
        stratum = merged[merged['status'] == stratum_name]
        n = max(int(len(stratum) * rate), min_n)
        n = min(n, len(stratum))
        if n > 0:
            sample = stratum.sample(n=n, random_state=seed)
            samples.append(sample)
    
    return pd.concat(samples, ignore_index=True)
```

### 3.3 Random Seed
- **Seed:** 42 (fixed, documented, reproducible)
- **Method:** NumPy random state with fixed seed
- **Reproducibility:** Deterministic ✅

### 3.4 Duplicate Prevention

- Sampling at **review unit level** (unique `(primary_ingredient, preparation_state, ifct_food_code)`)
- Each review unit appears at most once in audit sample
- Auto-accepted units excluded from audit sampling (already verified)

---

## 3. Auto-Accepted Units Exclusion

Auto-accepted review units (3 units) are **excluded from audit sampling** because:
- They have already passed the auto-accept gate with full evidence
- Including them would waste audit capacity
- Their correctness is verified by the auto-accept gate logic

---

## 5. Ambiguity and Unmatched Coverage

### 5.1 Ambiguous Ingredients (610)
- All 610 ingredients with multi-code ambiguity → **100% census**
- Each ingredient's candidate IFCT codes fully audited
- Domain expert review required

### 5.2 Unmatched Ingredients (11,310 unique)
- 5% random sample (565 units)
- Focus: identify non-IFCT foods, transliteration needs, composites

---

## 6. Duplicate Prevention

| Check | Method |
|-------|--------|
| Review unit uniqueness | PK = (ingredient, prep_state, IFCT_code) |
| Sample uniqueness | Sample IDs tracked in audit_samples table |
| Cross-stratum overlap | PK constraint prevents duplicates |
| Auto-accepted exclusion | Filtered before sampling |

---

## 6. Reproducibility

| Aspect | Specification |
|--------|---------------|
| Random seed | 42 (fixed, documented) |
| Random library | NumPy random state |
| Stratification | Deterministic with fixed seed |
| Reproducibility | Deterministic ✅ |

### Verification Command
```python
# Verify reproducibility
sample1 = draw_audit_sample(review_units, decisions, seed=42)
sample2 = draw_audit_sample(review_units, decisions, seed=42)
assert sample1.equals(sample2)  # Must pass
```

---

## 7. Special Coverage Requirements

| Category | Requirement |
|----------|-------------|
| Auto-accepted mappings | 100% census (3 units) |
| Multi-code ambiguous ingredients | 100% census (610 ingredients) |
| Preparation-state mismatches | 100% census (flagged units) |
| Multi-code ingredients | Proportional to population |
| Unmatched ingredients | 5% random sample (565 units) |

---

## 7. Deliverables

| Output | Format | Location |
|--------|--------|----------|
| Audit sample list | Parquet | `data/interim/phase3/audit_sample.parquet` |
| Sample manifest | JSON | `reports/phase3/audit_sample_manifest.json` |
| Selection log | CSV | `reports/phase3/audit_sample_selection_log.csv` |

---

## 8. Validation Checks

| Check | Method | Threshold |
|-------|--------|-----------|
| Sample size per stratum | Count rows | ≥ min_samples |
| No duplicate review units | `duplicated().sum()` | 0 |
| No auto-accepted in sample | `merge` with auto-accepted | 0 overlap |
| Seed reproducibility | Run twice with seed=42 | Identical output |
| Population coverage | Sum samples / population | ≥ rate - 0.5% |

---

## 9. Changes from Previous Plan

| Aspect | Previous | Corrected |
|--------|----------|-----------|
| Total population | 7,165 | **7,992** |
| TOKEN_SIMILARITY pop | 6,949 | **7,720** |
| TOKEN_SIMILARITY sample | 695 | **772** |
| Total samples | ~250 | **~1,379** |
| AMBIGUOUS population | ~0 | **610 ingredients** |
| UNMATCHED population | ~0 | **11,310** |
| Auto-accepted in sample | Included | **Excluded** |

---

## 9. Validation Checks

| Check | Method | Pass Criteria |
|-------|--------|---------------|
| Population sum | `sum(strata) == 7,992` | ✅ |
| Sample size per stratum | `len(sample) >= min_n` | ✅ |
| No auto-accepted in sample | `merge` with auto-accepted | 0 overlap |
| Seed reproducibility | Two runs, seed=42 | Identical |
| Stratum coverage | All methods + bands covered | ✅ |

---

*End of Sampling Plan (Corrected)*