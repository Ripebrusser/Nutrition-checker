# Stage 3.5.2: Reviewer Commitment Model

**Date:** 2026-11-18  
**Objective:** Reconcile the two-person reviewer model against the four written commitments. Distinguish reviewers, domain experts and consultants.

---

## Executive Summary

The Stage 3.5.1 recommendation specified **Option C: Primary Reviewer + External Quality Auditor (2 people)** as the minimum defensible model for a controlled 50-unit pilot. However, it also required **4 written commitments** — this document clarifies the distinction.

---

## Reconciliation

### The Apparent Conflict

| Source | Statement |
|--------|-----------|
| Stage 3.5.1 Reviewer Model Decision | "Minimum 2 reviewers (Primary + Auditor) required... 4 written commitments" |
| Stage 3.5.1 Minimum Pilot Requirements | "4 written commitments (Primary, Auditor, 2 Experts)" |

### Resolution: Three Distinct Roles

| Role | Count | Function | Commitment Type |
|------|-------|----------|-----------------|
| **Primary Reviewer** | 1 | Conducts all 50 unit reviews | Full-time (1-2 weeks) |
| **Quality Auditor** | 1 | Blind audit of 20% sample (10 units) | Part-time (20% sample) |
| **Domain Expert (Adjudication Panel)** | 2 | Resolves disagreements, 48h SLA | On-call (as needed) |
| **Total** | **4** | | |

### Role Definitions

#### 1. Primary Reviewer (Reviewer)
- **Role:** Conducts independent review of all 50 pilot units
- **Qualifications:** Domain expertise in Indian food composition; trained on calibration set
- **Commitment:** Written commitment to complete 50 units within 2 weeks
- **Workbench Role:** `PRIMARY`
- **Output:** 50 decisions with rationale, evidence, confidence

#### 2. Quality Auditor (Reviewer)
- **Role:** Independent blind audit of 20% random sample (10 units)
- **Qualifications:** Independent of primary reviewer; same domain expertise; trained on calibration set
- **Commitment:** Written commitment to complete 10-unit blind audit within 1 week
- **Workbench Role:** `AUDITOR`
- **Key Constraint:** **Blind to primary decisions** — sees only ingredient + candidates + evidence panel
- **Output:** 10 independent decisions

#### 3. Domain Experts / Adjudication Panel (Consultants)
- **Role:** Resolve disagreements between Primary and Auditor
- **Qualifications:** Senior IFCT/nutrition expertise; authority to make final mapping determination
- **Commitment:** Written commitment to 48h SLA for adjudication requests
- **Workbench Role:** `ADJUDICATOR`
- **Output:** Binding adjudication decisions with written rationale
- **Not reviewers:** Do not conduct primary reviews or audits

### Why 4 Commitments for a "2-Reviewer" Model?

| Aspect | Explanation |
|--------|-------------|
| **Scientific reviewers** | 2 (Primary + Auditor) — the ones whose decisions are compared |
| **Operational commitments** | 4 (2 reviewers + 2 adjudicators) — all people who must be available |
| **Adjudicators are NOT reviewers** | They don't produce review decisions; they resolve conflicts |
| **Goverance requirement** | "Reviewer model selected with commitments" = all roles committed |

---

## Formal Commitment Template

Each of the 4 individuals must sign:

```
I, [Name], commit to serving as [Primary Reviewer / Quality Auditor / Domain Expert] 
for the Stage 3.5 controlled 50-unit pilot review.

Role responsibilities:
- Primary Reviewer: Complete 50 independent reviews within 2 weeks
- Quality Auditor: Complete 10 blind audit reviews within 1 week  
- Domain Expert: Respond to adjudication requests within 48 hours

I confirm:
- I have no conflict of interest with the primary reviewer / auditor
- I have completed the 5-unit calibration set with consensus
- I will follow the pilot protocol and blind review procedures
- I will not discuss cases outside the formal adjudication process

Signed: _________________ Date: _________________
```

---

## Workbench Role Mapping

| Commitment Role | Workbench Role | Access |
|-----------------|----------------|--------|
| Primary Reviewer | `PRIMARY` | Full review interface |
| Quality Auditor | `AUDITOR` | Blind mode interface (hides primary decisions) |
| Domain Expert | `ADJUDICATOR` | Adjudication view (sees all decisions) |

---

## Summary

- **2 Reviewers** (Primary + Auditor) — produce decisions, compared for agreement
- **2 Domain Experts** (Adjudication Panel) — resolve disagreements, not reviewers
- **4 Written Commitments** — all four individuals must formally commit
- **This satisfies** "reviewer model selected with commitments" for Gate C

---

*End of Reviewer Commitment Model*