# Stage 3.5.1: Reviewer Model Decision

**Date:** 2026-11-18  
**Objective:** Determine the minimum scientifically and operationally defensible reviewer model for a controlled 50-unit pilot

---

## Executive Summary

**Recommendation: Option C — One Primary Reviewer + External Independent Quality Auditor (2 people total)**

This is the minimum defensible model for a controlled 50-unit pilot. It balances scientific validity with operational feasibility. It does NOT support inter-rater reliability claims (Cohen's κ, Gwet's AC1). If inter-rater reliability is a formal project requirement, Option B (4 reviewers) is required.

---

## Reconciliation of Conflicting Recommendations

| Source | Recommendation | Basis |
|--------|---------------|-------|
| Stage 3.3.1 Reviewer Model Comparison | "Minimum 2 reviewers (Primary + Auditor) required for Gate B. 4 reviewers preferred if resources allow. 4 reviewers NOT scientifically necessary." | Scientific necessity assessment |
| Stage 3.3.2 Final Gate Decision | "Gate B requires: Reviewer model selected (≥4 reviewers committed)" | Operational choice, not scientific |
| Stage 3.3.2 Governance Report | "4 reviewers are NOT scientifically necessary... The requirement for ≥4 reviewers is an operational choice" | Explicit statement |
| Stage 3.2.3 Blocker Register (BLK-011) | "Secure ≥4 written reviewer commitments" | Copied from Gate B requirement |

### Root Cause of Conflict

The **"≥4 reviewers"** requirement in Gate B and BLK-011 was **copied from an earlier operational assumption** without updating it after Stage 3.3.1 explicitly concluded that 4 reviewers are NOT scientifically necessary. The governance report (Stage 3.3.2) acknowledges this but the gate criteria were not updated.

**Evidence:** Stage 3.3.2 Governance Report §3.1: "Four reviewers are NOT scientifically necessary. The architecture supports both models. The requirement for ≥4 reviewers is an operational choice, not a scientific necessity."

---

## Scientific Necessity Assessment

### When Is Multi-Reviewer (≥4) Scientifically Required?

| Condition | Required? | Project Context |
|-----------|-----------|-----------------|
| Inter-rater reliability claim (κ, AC1) needed | ✅ Yes | Not required for pilot |
| Regulatory submission requiring κ | ✅ No | ML research project |
| High-stakes clinical decisions | ✅ No | Ingredient mapping |
| Published methodology paper | ❌ No | Internal tool |
| Exploratory analysis / pilot | ❌ No | This project |

**Conclusion:** For a **controlled 50-unit pilot** in an ML nutrition research project, inter-rater reliability measurement is **not scientifically necessary**. The pilot's purpose is to evaluate mapping quality, reviewer workflow, and tool usability — not to publish κ statistics.

---

## Option Evaluation

### Option A: Two Independent Reviewers (Primary + Secondary)

| Aspect | Assessment |
|--------|------------|
| **Inter-rater reliability** | Measurable (Cohen's κ, Gwet's AC1) |
| **Bias reduction** | ✅ Two perspectives |
| **Statistical power (n=50)** | **Low** — κ CI very wide; prevalence bias severe |
| **Adjudication** | Required for disagreements |
| **Resource requirement** | 2 committed reviewers |
| **Workbench support** | Needs blind review mode (BLK-017) |
| **Pilot feasibility** | ✅ Feasible |

**Limitation:** With 50 units and expected decision distribution (mostly REVIEW_REQUIRED/STANDARD), Cohen's κ will have very wide confidence intervals and be biased by class imbalance. Gwet's AC1 is more robust but still limited at n=50.

**Verdict:** Statistically weak for reliability claims. Operationally feasible.

---

### Option B: Four Reviewers (2 Primary + 2 Secondary)

| Aspect | Assessment |
|--------|------------|
| **Inter-rater reliability** | Measurable with better power |
| **Bias reduction** | ✅ Four perspectives |
| **Statistical power (n=50)** | Still limited — 50 units across 4 reviewers = 12-13 units/reviewer pair |
| **Adjudication** | Senior reviewer (BLK-018 undefined) |
| **Resource requirement** | 4 committed reviewers + senior adjudicator |
| **Workbench support** | Needs blind review + adjudication workflow |
| **Pilot feasibility** | ❌ Not feasible — no 4 reviewers available |

**Verdict:** Better statistical properties but **operationally impossible** — no reviewer commitments secured. Gate B requirement of "≥4 reviewers committed" has blocked progress for months.

---

### Option C: One Primary Reviewer + External Independent Quality Auditor (RECOMMENDED)

| Aspect | Assessment |
|--------|------------|
| **Inter-rater reliability** | **Not measurable** — explicitly no κ claim |
| **Bias reduction** | ✅ Independent audit (20% sample) |
| **Statistical power** | N/A — no reliability claim |
| **Audit process** | Auditor reviews 20% sample (10 units) blind to primary decisions |
| **Adjudication** | Domain expert panel (2 experts, defined SLA) |
| **Resource requirement** | 1 primary reviewer + 1 auditor + 2 domain experts (on-call) |
| **Workbench support** | Needs blind audit mode (subset of BLK-017) |
| **Pilot feasibility** | ✅ Feasible — minimal commitments |

**Verdict:** **Minimum defensible model.** Scientifically valid for pilot evaluation. No reliability claims made. Audit provides quality check. Escalation panel handles disagreements.

---

### Option D: Single Reviewer Only

| Aspect | Assessment |
|--------|------------|
| **Inter-rater reliability** | Not measurable |
| **Bias reduction** | ❌ No independent check |
| **Resource requirement** | 1 reviewer |
| **Pilot feasibility** | ✅ Feasible |

**Verdict:** **Not defensible.** No independent quality check. High risk of systematic bias going undetected. Rejected.

---

## Detailed Recommendation: Option C (Primary + Auditor)

### Roles and Commitments

| Role | Count | Commitment | Selection Criteria |
|------|-------|------------|-------------------|
| **Primary Reviewer** | 1 | Full pilot (50 units) | Domain expertise in Indian food composition; trained on calibration set |
| **Quality Auditor** | 1 | 20% sample (10 units) | Independent; no involvement in primary review; trained on calibration set |
| **Domain Expert Panel** | 2 | On-call (48h SLA) | IFCT/nutrition expertise; authority to adjudicate |

### Workflow

```
1. Calibration (both primary + auditor complete 5-unit set independently)
      ↓
2. Primary Review (50 units, blinded to auditor)
      ↓
3. Audit Sample Selection (random 20% = 10 units, stratified)
      ↓
4. Auditor Blind Review (10 units, sees ONLY ingredient + candidates + evidence)
      ↓
5. Agreement Analysis (raw agreement only; NO κ, NO AC1)
      ↓
6. Disagreement Adjudication (domain expert panel, 48h SLA)
      ↓
7. Pilot Results Report (agreement rate, disagreement categories, recommendations)
```

### Safeguards Against Bias

| Risk | Safeguard |
|------|-----------|
| Primary reviewer systematic bias | 20% independent audit by auditor blind to decisions |
| Calibration bias | Both complete calibration independently; consensus required |
| Adjudication bias | Panel of 2 experts; documented rationale for each decision |
| Tool-induced bias | Workbench blind mode hides previous decisions (BLK-017) |
| Evidence gaps | 15-field enforcement for ACCEPTED (BLK-015) |

### What This Model Does NOT Support

- ❌ Cohen's κ (requires ≥2 raters on same units)
- ❌ Gwet's AC1 (requires ≥3 raters)
- ❌ Per-status reliability metrics
- ❌ Confidence intervals for agreement
- ❌ Generalization to full-review reliability

### What This Model DOES Support

- ✅ Raw agreement rate (primary vs auditor on 10 units)
- ✅ Disagreement categorization and root cause analysis
- ✅ Evidence completeness audit
- ✅ Workflow usability assessment
- ✅ Tool functionality validation
- ✅ Calibration effectiveness verification
- ✅ Adjudication process validation

---

## Formal Decision

**Selected Model: Option C — Primary Reviewer + Independent Quality Auditor**

**Rationale:**
1. **Scientifically valid** for pilot purpose (quality evaluation, not reliability measurement)
2. **Operationally feasible** — requires only 2 committed people + on-call experts
3. **Consistent with Stage 3.3.1** — "Minimum 2 reviewers (Primary + Auditor) required for Gate B"
4. **Addresses BLK-017** — Auditor is truly blind (no rationale, no decision visibility)
5. **Addresses BLK-018** — Domain expert panel defined with SLA and authority
6. **Does not claim** inter-rater reliability — explicit limitation documented

**Conditions:**
- Workbench blind mode implemented (hides decision + rationale from auditor)
- Calibration consensus achieved by both primary and auditor
- Audit sample randomly selected (seed=42), stratified
- Adjudication protocol documented before pilot starts
- Pilot results explicitly state: "No inter-rater reliability claim"

---

## If Project Governance Mandates 4 Reviewers

If formal governance requires 4 reviewers despite scientific assessment:

1. **Document as operational constraint** — not scientific requirement
2. **Gate B criterion should read:** "Reviewer model selected AND commitments secured" (not "≥4 reviewers")
3. **Pilot proceeds with Option C** — 4-reviewer requirement applies to full-scale review
4. **Full-review plan** documents 4-reviewer model if resources permit

---

*End of Reviewer Model Decision*