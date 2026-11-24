# Stage 3.1: Independent Design Audit Report

**Date:** 2026-11-18  
**Scope:** Audit of five Stage 3 design documents against Stage 2.3 frozen data

---

## Executive Summary

**Verdict: C — NOT READY; ARCHITECTURE REQUIRES SUBSTANTIAL REDESIGN**

The Stage 3 design documents contain critical flaws that prevent safe implementation. The review unit key is fundamentally flawed, priority bands don't match actual data, auto-acceptance logic contradicts the Stage 2.3 gate, and reviewer workload estimates are based on incorrect counts.

---

## 1. Document Consistency Audit

### 1.1 Cross-Document Contradictions

| Aspect | Architecture Doc | Priority Report | Review Schema | QA Plan | Priority Report |
|--------|------------------|-----------------|---------------|---------|-----------------|
| Review units | 7,165 | 7,165 | 7,165 | 7,165 | 7,165 |
| Critical priority | — | 46 | — | — | 46 |
| High priority | — | 237 | — | — | 237 |
| Auto-accepted | 4 (Stage 2.3) | 4 (report) | — | — | 4 |
| **Actual Critical** | — | — | — | — | **25** |
| **Actual High** | — | — | — | — | **95** |

**Finding:** Priority band counts in the Priority Report **do not match actual Stage 2.3 data**. The reported 46 Critical / 237 High / 1,284 Medium / 2,898 Standard / 2,700 Low are **incorrect**. Actual distribution: 25 Critical / 95 High / 1,599 Medium / 5,446 Standard / 0 Low.

---

## 2. Review Unit Key Audit

### 2.1 Current Key Definition
**Proposed:** `(primary_ingredient, ifct_food_code)`

### 2.2 Critical Flaw: Preparation State Conflation

The key **conflates different preparation states** of the same ingredient mapping to the same IFCT code.

**Evidence from Stage 2.3 data:**
```
coriander leaves (FRESH)      → G009
coriander leaves (NOT_SPECIFIED) → G009
```
These are **different preparation states** with potentially different nutrient profiles (raw vs cooked), but the review unit key merges them into a single decision.

**Other examples:**
- `lemon juice (FRESH)` vs `lemon juice (NOT_SPECIFIED)` → both E033
- `coconut kernel (FRESH)` vs `coconut kernel (NOT_SPECIFIED)` → same IFCT codes

### 2.3 Impact

| Issue | Consequence |
|-------|-------------|
| **Nutrient accuracy** | Raw vs cooked nutrient profiles differ significantly (water loss, vitamin degradation) |
| **Decision validity** | A single ACCEPTED/REJECTED decision applies to ALL prep states of that ingredient |
| **Provenance loss** | Cannot trace which recipe occurrences used which prep state |
| **Audit impossibility** | Cannot audit prep-state-specific decisions |

### 2.4 Recommended Key Revision

**Revised key:** `(primary_ingredient, ifct_food_code, preparation_state)`

**Rationale:**
- Preserves preparation-state-specific decisions
- Maintains recipe-level provenance via `provenance_links` table
- Allows different IFCT codes for different prep states (e.g., raw onion vs fried onion)
- Backward compatible: `preparation_state = 'NOT_SPECIFIED'` as default

**Impact on review unit count:**
- Current: 7,165 units (primary_ingredient, ifct_food_code)
- Revised: ~8,200–8,500 units (estimated, adds prep_state dimension)

---

## 3. Review Count Reconciliation

### 3.1 Verified Counts vs Reported

| Metric | Reported | Actual (Stage 2.3) | Status |
|--------|----------|-------------------|--------|
| Total candidates | 119,474 | 119,474 | ✅ |
| Review units (pairs) | 7,165 | 7,165 | ✅ |
| Unique primary ingredients | — | 2,725 | — |
| Unique IFCT codes matched | 340 | 340 | ✅ |
| **Critical priority** | 46 | **25** | ❌ |
| **High priority** | 237 | **95** | ❌ |
| **Medium priority** | 1,284 | **1,599** | ❌ |
| **Standard priority** | 2,898 | **5,446** | ❌ |
| **Low priority** | 2,700 | **0** | ❌ |
| Multi-code ingredients | 1,255 | 1,255 | ✅ |
| Auto-accepted candidates | 4 | 4 | ✅ |
| Auto-accepted review units | 4 | **3** | ❌ |
| Input records (parsed) | 90,862 | 90,862 | ✅ |

### 3.2 Auto-Accepted Discrepancy

| Metric | Reported | Actual |
|--------|----------|--------|
| Auto-accepted candidates | 4 | 4 |
| Unique (primary, IFCT) pairs | 4 | **3** |
| Auto-accepted review units | 4 | **3** |

**Root cause:** `coriander leaves → G009` appears twice in auto-accepted (two recipe occurrences) but maps to the same review unit. The design counts candidates, not review units.

---

## 4. Decision Status Audit

### 4.1 Current Status Definitions

| Status | Architecture | Protocol | Schema | Mutually Exclusive? |
|--------|--------------|----------|--------|---------------------|
| ACCEPTED | ✅ | ✅ | ✅ | Yes |
| REVIEW_REQUIRED | ✅ | ✅ | ✅ | Yes |
| REJECTED | ✅ | ✅ | ✅ | Yes |
| UNMATCHED | ✅ | ✅ | ✅ | Yes |
| AMBIGUOUS | ✅ | ✅ | ✅ | Yes |
| CONFLICT | ✅ | — | ✅ | Audit only |

### 4.2 Critical Gaps

| Gap | Severity | Impact |
|-----|----------|--------|
| **No DRAFT/PENDING_REVIEW status** | High | Reviewers cannot save work-in-progress |
| **CONFLICT not in decision statuses** | Medium | Audit table has it, decisions table doesn't |
| **No ESCALATED status** | Medium | Senior reviewer escalation not modeled |
| **UNMATCHED vs REJECTED confusion** | High | Protocol doesn't clearly distinguish |
| **AMBIGUOUS terminal?** | High | Can AMBIGUOUS become ACCEPTED later? |

### 4.3 State Transition Issues

| Current | Allowed Next | Missing |
|---------|-------------|---------|
| PENDING | ACCEPTED, REVIEW_REQUIRED, REJECTED, UNMATCHED, AMBIGUOUS | DRAFT |
| REVIEW_REQUIRED | ACCEPTED, REJECTED, UNMATCHED, AMBIGUOUS | ESCALATED |
| AMBIGUOUS | (terminal per schema) | REVIEW_REQUIRED (re-review) |

**Missing terminal state resolution:** AMBIGUOUS and UNMATCHED should be revisitable.

---

## 5. Evidence Requirements Audit

### 5.1 Current Requirements (Insufficient)

| Current | Required |
|---------|----------|
| Rationale ≥ 50 chars | **Insufficient** — allows "looks correct" |
| Confidence 1-5 | **Insufficient** — no evidence linkage |
| Evidence references (optional) | **Must be mandatory** for ACCEPTED |

### 5.2 Required Evidence for ACCEPTED

| Evidence Component | Source | Mandatory? |
|-------------------|--------|------------|
| IFCT food code + official description | IFCT table | Yes |
| Source ingredient expression (original) | Recipe data | Yes |
| Primary ingredient (cleaned) | Disambiguated | Yes |
| Identity justification (species, variety, edible part) | Reviewer analysis | Yes |
| Preparation-state compatibility matrix | Stage 2.3 + reviewer | Yes |
| IFCT source page/table reference | IFCT 2017 doc | Yes |
| Reviewer decision + timestamp | Decision log | Yes |
| Uncertainty/limitations statement | Reviewer | Yes |

### 5.3 Evidence Traceability

| Evidence Type | Direct Source | Reviewer Interpretation |
|--------------|---------------|------------------------|
| IFCT food name match | IFCT table | No |
| Species verification | Scientific name in IFCT | No |
| Prep compatibility | Stage 2.3 gate | Partially |
| Alias verification | Synonym dict | Partially |
| "Looks correct" | **Never acceptable** | — |

---

## 6. Quality Assurance Audit

### 6.1 Sampling Design Issues

| Stratum | Population | Rate | Min Samples | Issue |
|---------|------------|------|-------------|-------|
| ACCEPTED (EXACT) | ~46 | 20% | 10 | Population wrong (actual ACCEPTED EXACT = 25) |
| ACCEPTED (SYNONYM) | ~0 | 20% | 1 | Population 0 but min 1 |
| REVIEW_REQ (TOKEN_EQUIV) | ~149 | 10% | 15 | Population wrong (actual 149) |
| REVIEW_REQ (TOKEN_SIM) | ~6,949 | 10% | 50 | **Severe under-sample** (should be ~695) |
| REVIEW_REQ (SYNONYM) | ~21 | 10% | 5 | OK |
| REVIEW_REQ (EXACT) | ~46 | 10% | 5 | Population wrong (actual 46) |
| REJECTED | ~0 | 5% | 5 | Population unknown |
| AMBIGUOUS | ~0 | 100% | All | Population unknown |
| UNMATCHED | ~0 | 5% | 5 | Population unknown |

**Critical flaws:**
1. Population estimates based on **incorrect priority bands**
2. **TOKEN_SIMILARITY severely under-sampled** (50 vs ~545 needed for 10%)
3. Strata defined by **status + method** but population counts wrong

### 6.2 Cohen's Kappa Issues

| Issue | Impact |
|-------|--------|
| **Class imbalance** | ACCEPTED rare, REVIEW_REQUIRED dominant → κ artificially low |
| **No confidence interval** | Cannot assess statistical significance |
| **Single reviewer assumption** | "Do not claim agreement if only one reviewer" — but plan assumes 2+ |
| **No prevalence adjustment** | κ biased by prevalence |
| **AMBIGUOUS/UNMATCHED 100% sampling** | May be 0 items → κ undefined |

### 6.3 Second Review Process Gaps

| Gap | Severity |
|-----|----------|
| "Blind to first decision (except rationale)" | Rationale **contains** the decision rationale → not blind |
| No calibration monitoring | Reviewer drift undetected |
| Senior reviewer selection | Not defined |
| Escalation timeline | Not specified |

---

## 6.4 Reviewer Capacity & Timeline Audit

### 6.1 Workload Calculation (Corrected)

| Priority Band | Units | Time/Unit | Total Hours | Reviewers | Days (30u/hr) |
|---------------|-------|-----------|-------------|-----------|---------------|
| Critical | 25 | 5 min | 2.1 | 1 | 0.1 |
| High | 95 | 8 min | 12.7 | 2 | 0.5 |
| Medium | 1,599 | 10 min | 266.5 | 4 | 8.3 |
| Standard | 5,446 | 12 min | 1,089 | 6 | 34.0 |
| Low | 0 | — | 0 | — | — |
| **Total** | **7,165** | **~10 min avg** | **~1,370 hrs** | **8** | **~43 days** |

**With 2-reviewer audit (2×):** ~2,740 hrs → **~86 days (17 weeks)**

### 6.2 Reviewer Availability Issues

| Assumption | Reality |
|------------|---------|
| 8 reviewers available | **Not confirmed** — no names, no commitments |
| 4 hrs/day sustained | **Unrealistic** — cognitive fatigue at 2-3 hrs |
| 30 units/day/reviewer | **Optimistic** — 60s min + rationale = ~2 min/unit max theoretical |
| No buffer for illness/vacation | **No buffer** |

**Single-reviewer fallback:** 1,370 hrs / (2 hrs/day × 5 days/wk) = **137 weeks (2.6 years)**

---

## 7. Priority Band Scoring Audit

### 7.1 Formula vs Reality

**Formula:** `score = method_weight + prep_weight + min(recipe_count * 2, 20) + similarity * 10`

| Component | Weights |
|-----------|---------|
| EXACT | 40 |
| SYNONYM | 30 |
| TOKEN_EQUIVALENT | 20 |
| TOKEN_SIMILARITY | 10 |
| FRESH/RAW | 30 |
| NOT_SPECIFIED | 15 |
| Recipe coverage | min(recipes × 2, 20) |
| Similarity | × 10 |

### 7.2 Actual vs Reported Distribution

| Band | Reported | Actual | Discrepancy |
|------|----------|--------|-------------|
| Critical (80-100) | 46 | **25** | -21 |
| High (60-79) | 237 | **95** | -142 |
| Medium (40-59) | 1,284 | **1,599** | +315 |
| Standard (20-39) | 2,898 | **5,446** | +2,548 |
| Low (0-19) | 2,700 | **0** | -2,700 |

**Root cause:** Priority report used **incorrect prep_state weights** and **wrong similarity scoring**. NOT_SPECIFIED prep (5,413 units) scored 15 points, pushing most units to Standard band.

---

## 8. Review Unit Key: Formal Recommendation

### 8.1 Current Key (Flawed)
```python
key = (primary_ingredient, ifct_food_code)
```

### 8.2 Revised Key (Required)
```python
key = (primary_ingredient, ifct_food_code, preparation_state)
```

### 8.3 Migration Strategy

| Step | Action |
|------|--------|
| 1 | Add `preparation_state` to review unit PK |
| 2 | Backfill from disambiguated data (FRESH/RAW/NOT_SPECIFIED/etc) |
| 3 | For NOT_SPECIFIED: infer from disambiguated `preparation` field or default to NOT_SPECIFIED |
| 4 | Update `provenance_links` PK to include `preparation_state` |
| 5 | Regenerate review units — expect ~8,200–8,500 units |
| 6 | Recompute priority scores with corrected prep weights |

---

## 9. Final Verdict & Required Corrections

### 9.1 Verdict: **C — NOT READY**

**Architecture requires substantial redesign before workbench implementation.**

### 9.2 Required Corrections (Blocking)

| # | Correction | Owner | Effort |
|---|------------|-------|--------|
| 1 | Fix review unit key to include `preparation_state` | Architect | 1 day |
| 2 | Recompute all priority scores with corrected weights | Architect | 0.5 day |
| 2 | Regenerate priority report with actual counts | Architect | 0.5 day |
| 4 | Fix auto-accepted count (3 review units, not 4) | Architect | 0.5 day |
| 5 | Add DRAFT/PENDING_REVIEW/ESCALATED statuses | Architect | 0.5 day |
| 6 | Define AMBIGUOUS/UNMATCHED as revisitable | Architect | 0.5 day |
| 7 | Redesign evidence requirements for ACCEPTED | Protocol Owner | 1 day |
| 8 | Fix sampling strata with correct populations | QA Lead | 1 day |
| 9 | Recalculate reviewer workload with correct counts | PM | 0.5 day |
| 10 | Document reviewer commitments or provide fallback plan | PM | 1 day |

### 9.2 Non-Blocking (Pre-Implementation)

| # | Correction | Owner |
|---|------------|-------|
| 11 | Add DRAFT/PENDING_REVIEW status to decision schema | Architect |
| 12 | Define CONFLICT in decisions table | Architect |
| 13 | Make evidence references mandatory for ACCEPTED | Protocol Owner |
| 14 | Fix Cohen's kappa interpretation for imbalanced classes | QA Lead |
| 15 | Add blind review (hide first decision + rationale) | Architect |
| 16 | Add prevalence-adjusted kappa (Gwet's AC1) | QA Lead |
| 17 | Define senior reviewer role and escalation SLA | PM |
| 18 | Provide single-reviewer fallback timeline | PM |

---

## 10. Final Recommendation

**DO NOT PROCEED** to workbench implementation until all blocking corrections (1-10) are complete and design documents updated.

**Estimated correction effort:** 6–8 person-days

**Revised timeline:** Architecture fix (1 week) → Workbench build (2 weeks) → Reviewer onboarding (1 week) → Pilot review (1 week) → Full review (12+ weeks)

---

*End of Stage 3.1 Design Audit Report*