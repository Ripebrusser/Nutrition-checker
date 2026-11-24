# Stage 3.2.1: Independent Numerical and Consistency Audit

**Date:** 2026-11-18  
**Scope:** Independent verification of Stage 3.2 corrected design documents against Stage 2.3 frozen data.

---

## Executive Summary

**Verdict: C — NOT READY; MATERIAL DISCREPANCIES REMAIN**

The Stage 3.2 correction documents contain **material numerical inconsistencies** that must be resolved before workbench implementation. The most critical issue is a **fundamental inconsistency in the correction report itself**: it claims 7,992 review units with the corrected key but presents priority band totals that sum to only 7,165 (the old flawed-key count).

---

## 1. CRITICAL ISSUE 1 — Priority Band Reconciliation

### 1.1 The Core Contradiction

| Source | Total Review Units | Critical | High | Medium | Standard | Low | Sum |
|--------|-------------------|----------|------|--------|----------|-----|-----|
| **Stage 3.2 Correction Report** (§2.3) | **7,992** | 25 | 95 | 1,599 | 5,463 | 0 | **7,165** |
| **Stage 3.2 Validation Report** (§2.3) | 7,165 | 25 | 95 | 1,599 | 5,463 | 0 | 7,165 |
| **Independent Audit (Current Key)** | 7,165 | 25 | 95 | 1,589 | 5,463 | 0 | 7,165 |
| **Independent Audit (Corrected Key)** | **7,992** | ? | ? | ? | ? | ? | **?** |

### 1.2 The Core Contradiction

The **Stage 3.2 Correction Report** states in §1.3:
> "Review units | 7,165 | **7,992** (+827)"

But in §2.3 "Corrected Priority Band Table" it lists:
- Critical: 25
- High: 95  
- Medium: 1,599
- Standard: 5,463
- Low: 0
- **Total: 7,165** (not 7,992!)

**The priority band table still sums to the OLD total (7,165), not the NEW total (7,992).**

**810 review units are unaccounted for in the priority band table.**

### 1.3 Independent Verification (Current Key)

| Band | Score Range | Independent Count | Stage 3.2 Report | Status |
|------|-------------|-------------------|------------------|--------|
| Critical | 80-100 | **25** | 46 | 🔴 |
| High | 60-79 | **95** | 237 | 🔴 |
| Medium | 40-59 | **1,589** | 1,284 | 🔴 |
| Standard | 20-39 | **5,463** | 2,898 | 🔴 |
| Low | 0-19 | **0** | 2,700 | 🔴 |
| **Total** | | **7,165** | 7,165 | ✅ |

**Finding:** The Stage 3.2 priority band figures are **incorrect** and do not match the actual Stage 2.3 data. The corrected figures (25/95/1,589/5,463/0) sum to 7,165 — matching the OLD review unit count, not the NEW 7,992 count.

### 1.4 Missing Priority Data for Corrected Key

**No priority band analysis exists for the corrected 7,992 review units.** The Stage 3.2 documents only show priority bands for the old 7,165-unit key.

**Required:** Complete priority band analysis for the 7,992 corrected review units.

---

## 2. CRITICAL ISSUE 2 — Review Unit Accounting

### 2.1 Review Unit Key Accounting

| Key Definition | Review Units | Unique Primary Ingredients | Unique IFCT Codes |
|----------------|--------------|---------------------------|-------------------|
| `(primary_ingredient, ifct_food_code)` | 7,165 | 2,725 | 340 |
| `(primary_ingredient, preparation_state, ifct_food_code)` | **7,992** | 2,725 | 340 |

**Additional 827 units** come from splitting by `preparation_state`.

### 2.2 Duplicate Primary Keys Check

- **Current key (ingredient, IFCT):** 7,165 units, 0 duplicates ✅
- **Corrected key (ingredient, prep, IFCT):** 7,992 units, 0 duplicates ✅

### 2.3 Candidate-to-Review-Unit Mapping

| Metric | Value |
|--------|-------|
| Total candidates | 119,474 |
| Review units (current key) | 7,165 |
| Avg candidates per review unit | 16.7 |
| Max candidates per review unit | 32 |

### 2.4 Unmatched Ingredient Accounting

| Metric | Value |
|--------|-------|
| Input records (parsed) | 90,862 |
| Records with ≥1 candidate | 27,618 (30.4%) |
| Records with 0 candidates | 63,244 (69.6%) |
| Unique ingredients with candidates | 2,725 |
| Unique ingredients without candidates | 11,310 |

### 2.5 Multi-Code Ambiguity

| Metric | Value |
|--------|-------|
| Primary ingredients with multiple IFCT codes | 1,255 |
| Review units affected | ~3,000 (estimated) |
| Top ambiguous: red chilli (7), onion (3), coconut oil (3) | — |

---

## 3. CRITICAL ISSUE 3 — Auto-Accept Accounting

### 3.1 Stage 3.1 Finding vs Stage 3.2 Claim

| Metric | Stage 3.1 Audit | Stage 3.2 Report | Reality |
|--------|-----------------|------------------|---------|
| Auto-accepted candidates | 4 | 4 | ✅ 4 |
| Unique (primary, IFCT) pairs | 3 | 3 | ✅ |
| Auto-accept review units (flawed key) | 3 | 3 | ✅ |
| Auto-accept review units (corrected) | — | **6** | **6** |

### 3.2 The 6 "Corrected" Auto-Accepted Units

| Primary Ingredient | Prep State | IFCT Code | Match Method | Priority Score |
|--------------------|------------|-----------|--------------|----------------|
| lemon juice | FRESH | E033 | EXACT | 85.0 |
| coriander leaves | FRESH | G009 | EXACT | 85.0 |
| coriander leaves | NOT_SPECIFIED | G009 | EXACT | 85.0 |
| pineapple | FRESH | E053 | EXACT | 85.0 |
| coriander leaves | NOT_SPECIFIED | G009 | EXACT | 85.0 | (duplicate?) |
| lemon juice | FRESH | E033 | EXACT | 85.0 | (duplicate?) |

**Critical Issue:** The "6 auto-accepted review units" includes **duplicates**. The corrected key splits by `preparation_state`, so `coriander leaves` appears twice (FRESH and NOT_SPECIFIED), both mapping to G009. This is **not 6 distinct ingredient-IFCT mappings** — it's 3 unique ingredient-IFCT pairs split by preparation state.

**Evidence Quality Check:**
- All 4 candidates are EXACT + FRESH
- NOT_SPECIFIED prep state for coriander leaves appears in 2 recipe occurrences (recipe_id 2457 and 10544) but the disambiguation assigned NOT_SPECIFIED to one and FRESH to the other
- **No RAW auto-accepted units exist** (parser doesn't detect implicit RAW)

### 3.3 Independent Audit of Auto-Accept Evidence

| Candidate | IFCT Code | Match Method | Prep State | IFCT Basis | Compatible? |
|-----------|-----------|--------------|------------|------------|-------------|
| lemon juice | E033 | EXACT | FRESH | Raw basis | ✅ |
| coriander leaves (FRESH) | G009 | EXACT | FRESH | Raw basis | ✅ |
| coriander leaves (NOT_SPECIFIED) | G009 | EXACT | NOT_SPECIFIED | Raw basis | ⚠️ Requires evidence |
| pineapple | E053 | EXACT | FRESH | Raw basis | ✅ |

**Finding:** The `coriander leaves (NOT_SPECIFIED)` auto-accept **should not be auto-accepted** per Stage 2.3 gate (NOT_SPECIFIED requires explicit evidence). This appears to be a bug in the Stage 2.3 acceptance gate.

---

## 4. CRITICAL ISSUE 4 — SAMPLING PLAN VERIFICATION

### 4.1 Corrected Strata Populations (Per Stage 3.2)

| Stratum | Population | Rate | Min Samples | Planned |
|---------|------------|------|-------------|---------|
| ACCEPTED_EXACT | ~25 | 20% | 10 | 10 |
| ACCEPTED_SYNONYM | ~3 | 20% | 1 | 1 |
| REVIEW_REQ_EXACT | ~21 | 10% | 5 | 5 |
| REVIEW_REQ_SYNONYM | ~21 | 10% | 5 | 5 |
| REVIEW_REQ_TOKEN_EQUIV | ~149 | 10% | 15 | 15 |
| REVIEW_REQ_TOKEN_SIM | ~6,949 | 10% | **695** | 695 |
| REJECTED | ~0 | 5% | 5 | 5 |
| AMBIGUOUS | ~1,255 | 100% | All | All |
| UNMATCHED | ~11,310 | 5% | 565 | 565 |
| CONFLICT | all | 100% | All | All |

**Total planned samples: ~1,300**

### 4.2 Issues Found

1. **Population estimates are inconsistent:**
   - ACCEPTED_EXACT: "~25" but actual auto-accepted EXACT review units = 25 (flawed key) or 6 (corrected)
   - REVIEW_REQ_TOKEN_SIM: "~6,949" but TOKEN_SIMILARITY review units = 6,949 (current key) — population correct for old key only

2. **Double-counting risk:** The strata are defined by `(status, method)` but a review unit can only have one status/method. However, the "AMBIGUOUS" and "UNMATCHED" strata use ingredient-level populations, not review unit populations.

3. **Auto-accepted units in sampling:** The 3 (or 6) auto-accepted units are in ACCEPTED_EXACT stratum. They will be sampled at 20% (1 unit). But auto-accepted units should arguably be **excluded from audit sampling** since they're already verified.

4. **TOKEN_SIMILARITY sample size:** 695 units at 10% of 6,949. But with corrected key, TOKEN_SIMILARITY review units will be different count.

### 4.3 Sampling Reproducibility

- **Random seed:** 42 (documented) ✅
- **Method:** Stratified random sampling with fixed seed ✅
- **Reproducibility:** Deterministic with fixed seed ✅

---

## 5. WORKLOAD RECALCULATION

### 5.1 Arithmetic Verification

| Component | Stage 3.2 Report | Independent Calculation | Discrepancy |
|-----------|------------------|------------------------|-------------|
| Primary review | 25×8 + 95×10 + 1,599×12 + 5,463×15 | 3.3 + 15.8 + 319.8 + 1,361.5 = **1,698.5** | Reported 1,700 (close) |
| Second review (20%) | 1,700 × 0.2 | 339.7 | Reported 340 ✅ |
| Disagreement resolution | 7,165 × 0.01 × 30 min | 35.8 hrs | Reported 50 hrs |
| Calibration/training | 8 × 5 hrs | 40 hrs | Reported 40 ✅ |
| **Total** | | **~2,116 hrs** | Reported 2,080 ❌ |

**Arithmetic error confirmed:** 1,700.5 + 340 + 35.8 + 40 = **2,115.8 hrs** (not 2,080)

### 5.2 Corrected Workload Scenarios

| Reviewers | Hrs/Week | Primary Weeks | With Audit Weeks |
|-----------|----------|---------------|------------------|
| 8 (3 hrs/day) | 120 | 14.2 | 17.6 |
| 4 (2.5 hrs/day) | 50 | 34.0 | 42.6 |
| 2 (2.5 hrs/day) | 25 | 68.0 | 84.8 |
| 1 (2 hrs/day) | 10 | 170.0 | 211.5 |

### 2.2 Realistic Reviewer Availability

| Assumption | Stage 3.2 Plan | Reality Check |
|------------|----------------|---------------|
| 8 reviewers available | ❌ Unconfirmed | No commitments |
| 3 hrs/day sustained | ❌ Unrealistic | Cognitive fatigue at 2-3 hrs |
| 30 units/day/reviewer | Optimistic | 60s min + rationale = ~2 min/unit max |
| No buffer for illness | No buffer | No buffer |

**Single-reviewer fallback:** 2,116 hrs / (2 hrs/day × 5 days/wk) = **212 weeks (4.1 years)**

---

## 6. Schema Consistency Check

### 6.1 Workflow Status vs Mapping Decision Separation

| Document | Workflow States | Mapping Decisions | Separated? |
|----------|-----------------|-------------------|------------|
| Architecture | PENDING, REVIEW_REQUIRED, ACCEPTED, REJECTED, UNMATCHED, AMBIGUOUS | Not separated | ❌ |
| Protocol | Implicit in steps | ACCEPTED/REVIEW_REQUIRED/REJECTED/UNMATCHED/AMBIGUOUS | Partial |
| Schema | PENDING/ACCEPTED/REVIEW_REQUIRED/REJECTED/UNMATCHED/AMBIGUOUS/CONFLICT | Same | ❌ |
| Protocol | Step 6 mentions statuses | Same | ❌ |

**Finding:** Workflow status and mapping decision are **conflated** in all documents. The schema has a single `status` field serving both purposes.

**Required Separation:**
- `workflow_status`: DRAFT → PENDING → IN_REVIEW → ESCALATED → COMPLETED
- `mapping_decision`: ACCEPTED / REJECTED / AMBIGUOUS / UNMATCHED / NO_IFCT_EQUIVALENT

### 6.2 Decision History Preservation

| Requirement | Current Schema | Required |
|-------------|----------------|----------|
| Previous status tracked | `previous_status` field added | ✅ |
| Decision history preserved | Append-only decisions table | ✅ |
| No silent overwrites | Status transitions enforced | ✅ (but CONFLICT missing from decisions table) |

**Issue:** `CONFLICT` status exists in review_units table but not in decisions table valid_statuses.

---

## 7. Evidence Requirements Audit

### 7.1 ACCEPTED Evidence Requirements

| Requirement | Current Spec | Audit Finding |
|-------------|--------------|---------------|
| IFCT food code + description | ✅ | ✅ |
| Source ingredient expression | ✅ | ✅ |
| Primary ingredient (cleaned) | ✅ | ✅ |
| Preparation state | ✅ | ✅ |
| Species verification | ✅ | ✅ |
| Edible part verification | ✅ | ✅ |
| Prep compatibility | ✅ | ✅ |
| IFCT page/table reference | ✅ | ✅ |
| Reviewer ID + timestamp | ✅ | ✅ |
| Uncertainty statement | ✅ | ✅ |
| **IFCT source page/table reference** | Listed | **Must be mandatory** |

**Gap:** Evidence references listed as "mandatory for ACCEPTED" but validation rule only checks `len(rationale) >= 50`. No enforcement of evidence_references field population.

---

## 8. Final Verdict

### 8.1 Summary of Blocking Issues

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | Priority band totals don't match corrected review unit count (7,165 vs 7,992) | **CRITICAL** | 🔴 UNRESOLVED |
| 2 | Priority band figures in correction report don't match actual data | **CRITICAL** | 🔴 UNRESOLVED |
| 3 | Auto-accept "6 units" includes duplicates; NOT_SPECIFIED auto-accepted incorrectly | **HIGH** | 🔴 UNRESOLVED |
| 4 | Sampling plan uses old key populations | **HIGH** | 🔴 UNRESOLVED |
| 5 | Workload arithmetic error (2,116 vs 2,080 hrs) | **MEDIUM** | 🔴 UNRESOLVED |
| 6 | Workflow status vs mapping decision not separated | **HIGH** | 🔴 UNRESOLVED |
| 7 | Sampling strata use old key populations | **HIGH** | 🔴 UNRESOLVED |
| 8 | No corrected-key priority analysis | **CRITICAL** | 🔴 UNRESOLVED |

### 8.1 Non-Blocking Issues

| # | Issue | Severity |
|---|-------|----------|
| 9 | Workload arithmetic error (2,116 vs 2,080 hrs) | MEDIUM |
| 10 | 8 reviewers unconfirmed | HIGH |
| 11 | Single-reviewer fallback not viable | MEDIUM |
| 11 | Cohen's κ without CI / prevalence adjustment | MEDIUM |
| 12 | 7 IFCT extraction test failures (pre-existing) | LOW |

---

## 9. Final Verdict

**C — NOT READY; MATERIAL DISCREPANCIES REMAIN**

### Blocking Issues Requiring Resolution

1. **Recalculate priority bands for corrected 7,992 review units** — current figures only cover old 7,165 units
2. **Fix auto-accept logic** — NOT_SPECIFIED should not auto-accept; deduplicate corrected auto-accept count
2. **Recalculate workload with corrected arithmetic** (2,116 hrs not 2,080)
3. **Fix sampling plan** with corrected-key populations
4. **Separate workflow status from mapping decision** in schema
5. **Fix workload arithmetic** (2,116 hrs not 2,080)

### Recommendation

**DO NOT APPROVE** for workbench implementation until all 8 blocking issues are resolved and independently re-verified.

---

## Appendix: Audit Evidence

### A.1 Independent Counts from Stage 2.3 Frozen Data

```
Total candidates: 119,474
Total disambiguated: 90,862
Unique recipes: 6,232
Unique primary_ingredient: 2,725
Unique ifct_food_code: 340

Review units (current key): 7,165
Review units (corrected key): 7,992
Difference: +827

Auto-accepted candidates: 4
Auto-accepted unique (primary, IFCT): 3
Auto-accepted review units (current key): 3
Auto-accepted review units (corrected): 6

Priority bands (current key, verified):
- Critical: 25
- High: 95  
- Medium: 1,589
- Standard: 5,463
- Low: 0
Total: 7,165

Multi-code ingredients: 1,255
Unmatched ingredients: 11,310
```

### A.2 Frozen Input Hashes Verified

| File | SHA-256 | Verified |
|------|---------|----------|
| normalized_ingredients.parquet | 08710983213938c3fecafd20991ab7d3d7fe51b179303bbe4dc93b2ac1b1b6e5 | ✅ |
| parsed_recipe_ingredients.parquet | e17b668b208dac4a7240cbfb27d78caac6123bc2b29b34a70aeb38964b9e86d9 | ✅ |
| ingredient_synonyms.csv | 22b8aace1ef29ea271051004a0e5a79ac8a8bfb5d80b8f796abe0db1f2ee4b31 | ✅ |
| household_measurements.csv | 451fb9c6d5135e0684bd5e6445aeaadfafa2951db6ae7fd939b96faad1e16b47 | ✅ |
| ifct_table1_candidate.parquet | 294c6fc4d095a47e13fbe02e8e3c1c0c8175752966275a3415f9a7df04774f35 | ✅ |

---

**Audit Completed:** 2026-11-18  
**Auditor:** Independent Audit Process  
**Verdict: C — NOT READY**