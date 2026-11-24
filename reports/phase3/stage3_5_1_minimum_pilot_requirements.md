# Stage 3.5.1: Minimum Pilot Requirements

**Date:** 206-11-18  
**Objective:** Define the minimum scientifically and operationally necessary conditions for a controlled 50-unit pilot

---

## Executive Summary

A restricted 50-unit pilot **can be conducted** with the following minimum requirements. This pilot is **distinct from full-scale review authorization** and makes no inter-rater reliability claims.

---

## Minimum Requirements for Pilot Authorization

### 1. People (Minimum 4 Named Individuals)

| Role | Count | Commitment | Must Be Secured Before Pilot |
|------|-------|------------|------------------------------|
| Primary Reviewer | 1 | 50 units over 1-2 weeks | ✅ Written commitment |
| Quality Auditor | 1 | 10 units (20% sample) | ✅ Written commitment |
| Domain Expert (Adjudication) | 2 | On-call, 48h SLA | ✅ Written commitment |

**Total: 4 named individuals with written commitments**

> **Note:** This satisfies the "reviewer model selected with commitments" intent of Gate B without requiring 4 full-time reviewers. The auditor is part-time (20% sample); adjudicators are on-call.

### 2. Workbench Safeguards (Code Changes Required)

| # | Safeguard | Blocker | Implementation |
|---|-----------|---------|----------------|
| 1 | Auto-accept excludes NOT_SPECIFIED | BLK-003, 008, 011 | Add `preparation_state != 'NOT_SPECIFIED'` to auto-accept check |
| 2 | MappingDecision enum includes CONFLICT | BLK-012 | Add CONFLICT to enum in workbench |
| 3 | WorkflowStatus allows revisiting | BLK-013 | Allow AMBIGUOUS→IN_REVIEW, UNMATCHED→IN_REVIEW transitions |
| 4 | ACCEPTED enforces 15 evidence fields | BLK-015 | Validate `len(evidence_references) >= 15` for ACCEPTED |
| 5 | Blind mode for auditor | BLK-017 | "Blind Review" mode: hides decision, rationale, confidence; shows only ingredient + candidates + evidence panel |

**All 5 must be implemented and tested before pilot starts.**

### 3. Protocol Documents (Must Be Written Before Pilot)

| Document | Purpose | Blocker |
|----------|---------|---------|
| Pilot Protocol | End-to-end pilot procedure, roles, timeline, deliverables | — |
| Blind Audit Procedure | How auditor reviews 10 units without seeing primary decisions | BLK-017 |
| Adjudication Protocol | Disagreement resolution: panel, SLA (48h), authority, documentation | BLK-018 |
| Evidence Checklist | 15 mandatory fields for ACCEPTED with definitions/examples | BLK-015 |
| Auto-Accept Verification | Manual check procedure for the 3 auto-accepted units | BLK-003, 008 |

### 4. Calibration (Must Complete Before Pilot)

| Requirement | Standard |
|-------------|----------|
| Both primary and auditor complete 5-unit calibration set | ✅ Independent |
| Consensus on all 5 units | ✅ Required |
| Discrepancies resolved and documented | ✅ Required |
| Calibration records retained | ✅ Required |

### 5. Sampling (Defined in Stage 3.5)

| Requirement | Specification |
|-------------|---------------|
| Population | 7,992 corrected review units |
| Sample size | 50 units |
| Method | Stratified random (seed=42) |
| Strata | Per Stage 3.5 sampling report |
| Auto-accepted inclusion | All 3 auto-accepted units included for verification |
| Auditor sample | 20% (10 units), random stratified from 50 |

### 6. Review Process Requirements

| Requirement | Specification |
|-------------|---------------|
| Primary review | All 50 units; decision + rationale (≥50 chars) + evidence refs + confidence (1-5) |
| Blind audit | Auditor sees ONLY: ingredient expression, candidate IFCT records, evidence panel |
| Blind audit | Auditor does NOT see: primary decision, rationale, confidence, reviewer ID |
| Adjudication | All disagreements → domain expert panel; 48h SLA; written rationale |
| Evidence | ACCEPTED requires all 15 fields; others require rationale + refs |
| No auto-accept | Pilot reviewers manually verify all units including 3 auto-accepted |

### 7. Data Integrity Requirements

| Requirement | Specification |
|-------------|---------------|
| Frozen inputs unchanged | 8 SHA-256 hashes verified pre/post pilot |
| No candidate data modification | Pilot only records decisions |
| Audit trail | Every decision + change logged with reviewer_id, timestamp |
| Export | Parquet + CSV of all pilot decisions |
| Provenance | Each decision links to review_unit_id, recipe_ids |

### 8. Reporting Requirements

| Deliverable | Content |
|-------------|---------|
| Pilot Results Report | Agreement rate (raw), disagreement analysis, evidence completeness, time/unit |
| Disagreement Analysis | Categorized root causes, corrective recommendations |
| Calibration Report | Calibration outcomes for both reviewers |
| Adjudication Log | Every disagreement with panel decision and rationale |
| Pilot Gate Recommendation | A/B/C with evidence |

---

## What the Pilot Does NOT Require

| Item | Reason |
|------|--------|
| 4 full-time reviewers | Not scientifically necessary (Stage 3.3.1) |
| Cohen's κ / Gwet's AC1 | n=50 insufficient; prevalence bias; not pilot purpose |
| Full-review priority bands | Pilot uses own stratified sample |
| Full-review workload arithmetic | Pilot fixed at 50 units |
| Full-review sampling plan (1,379 units) | Pilot is separate 50-unit exercise |
| Nutrition calculations | Phase 4 — forbidden |
| Changes to frozen candidate data | Pilot only records decisions |
| Automatic mapping acceptance | All decisions manual in pilot |
| Production deployment | Pilot is evaluation only |

---

## What the Pilot CANNOT Claim

| Claim | Status | Reason |
|-------|--------|--------|
| "Inter-rater reliability validated" | ❌ Cannot claim | Only 2 raters on 10 units; no κ |
| "Reviewer consistency proven" | ❌ Cannot claim | Single primary reviewer for 40 units |
| "Full-review readiness proven" | ❌ Cannot claim | Pilot evaluates tool/process, not scale |
| "Mapping accuracy measured" | ❌ Cannot claim | No ground truth; only reviewer judgment |
| "Blocker resolution validated" | ⚠️ Partial | Only validates pilot safeguards |

---

## What the Pilot CAN Claim (If Successful)

| Claim | Basis |
|-------|-------|
| "Workbench functions correctly for decision recording" | All 50 units processed without data loss |
| "Schema v1.1 supports required decision types" | All 5 decision types used; transitions work |
| "Evidence enforcement works" | ACCEPTED decisions have 15 fields |
| "Blind audit process feasible" | Auditor completed 10 units blind |
| "Adjudication process works" | All disagreements resolved per protocol |
| "Calibration effective" | Both reviewers achieved consensus on 5 units |
| "Tool usability acceptable" | Time/unit within expected range; no critical bugs |
| "Disagreement categories identified" | Root causes documented for process improvement |

---

## Pilot Authorization Checklist

| # | Requirement | Status | Verification |
|---|-------------|--------|--------------|
| 1 | Gate A (Architecture) approved | ✅ | Stage 3.3.2 |
| 2 | Prototype accepted (Stage 3.4.1) | ✅ | A — Prototype Accepted |
| 3 | Calibration materials ready | ✅ | Stage 3.5 calibration report |
| 4 | Primary reviewer committed (written) | ❌ | Pending |
| 5 | Quality auditor committed (written) | ❌ | Pending |
| 6 | 2 domain experts committed (written) | ❌ | Pending |
| 7 | Workbench safeguard 1: NOT_SPECIFIED auto-accept fix | ❌ | Code change needed |
| 8 | Workbench safeguard 2: CONFLICT in MappingDecision | ❌ | Code change needed |
| 9 | Workbench safeguard 3: Revisitable transitions | ❌ | Code change needed |
| 10 | Workbench safeguard 4: 15-field ACCEPTED enforcement | ❌ | Code change needed |
| 11 | Workbench safeguard 5: Blind audit mode | ❌ | Code change needed |
| 12 | Pilot protocol document | ❌ | To be written |
| 13 | Blind audit procedure | ❌ | To be written |
| 14 | Adjudication protocol | ❌ | To be written |
| 15 | Evidence checklist | ❌ | To be written |
| 16 | Auto-accept verification procedure | ❌ | To be written |
| 17 | Calibration consensus achieved | ❌ | Requires #4, #5 |
| 18 | SHA-256 hashes verified pre-pilot | ❌ | Pre-pilot check |

**Total: 18 requirements | 3 met | 15 pending**

---

## Authorization Decision Logic

```
IF (Gate A approved) AND
   (Prototype accepted) AND
   (Calibration ready) AND
   (Primary + Auditor + 2 Experts committed) AND
   (5 workbench safeguards implemented AND tested) AND
   (5 protocol documents written) AND
   (Calibration consensus achieved) AND
   (Pre-pilot hash verification passed)
THEN
   Pilot Authorization = GRANTED (Restricted)
ELSE
   Pilot Authorization = DENIED
```

---

## Distinction: Pilot Authorization ≠ Full Review Authorization

| Aspect | Pilot Authorization | Full Review Authorization |
|--------|---------------------|---------------------------|
| Scope | 50 units | 7,992 units |
| Reviewers | 1 primary + 1 auditor | ≥2 primary + auditors (per model) |
| Reliability claims | None | Per chosen model |
| Blockers | 10 pilot-relevant (with safeguards) | All 15 resolved |
| Timeline | 1-2 weeks | 19-93 weeks |
| Purpose | Tool/process evaluation | Production mapping |
| Gate | C (new — Pilot Authorization) | D (new — Full Review) |

---

## Recommended Next Steps

1. **Secure 4 written commitments** (Primary, Auditor, 2 Experts)
2. **Implement 5 workbench safeguards** (1-2 days development)
3. **Write 5 protocol documents** (1-2 days)
4. **Complete calibration** (0.5 days)
5. **Verify hashes** (0.1 days)
6. **Formal Gate C sign-off** (QA Lead + Project Lead)
7. **Conduct 50-unit pilot** (1-2 weeks)
8. **Produce pilot reports** (1 week)
9. **Gate D evaluation** for full review

---

*End of Minimum Pilot Requirements*