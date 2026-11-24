# Stage 3.5: Disagreement Analysis Report

**Date:** 2026-11-18  
**Status:** **NOT APPLICABLE** — Pilot not conducted

---

## Executive Summary

No disagreement analysis can be performed because the 50-unit pilot review was **not authorized and not conducted** per Stage 3.3.2 governance (Gate B and Gate C not met).

---

## Pilot Status

| Item | Status |
|------|--------|
| Pilot authorized | ❌ NO |
| Pilot conducted | ❌ NO |
| Primary reviewer decisions | 0 |
| Second reviewer decisions | 0 |
| Disagreements identified | 0 |
| Disagreement analysis | NOT APPLICABLE |

---

## Required for Disagreement Analysis (When Pilot Authorized)

When the pilot is authorized and conducted, the following analysis would be performed:

### 1. Agreement Metrics

- **Raw Agreement Rate** — % of units with identical decisions
- **Cohen's κ** — Chance-corrected agreement (with 95% CI)
- **Gwet's AC1** — Prevalence-adjusted agreement (with 95% CI)
- **Per-Category Agreement** — Agreement by decision type (ACCEPTED, REJECTED, AMBIGUOUS, UNMATCHED, NO_IFCT_EQUIVALENT)

### 2. Error Categorization

For each disagreement:

| Category | Description |
|----------|-------------|
| Incorrect ingredient identity | Reviewer misidentified primary ingredient |
| Incorrect IFCT food selection | Wrong IFCT code chosen despite correct ingredient |
| Preparation-state mismatch | Prep state not properly considered |
| Food-group mismatch | IFCT food group inconsistent with ingredient |
| Insufficient evidence | ACCEPTED without 15 mandatory fields |
| Multiple plausible candidates | AMBIGUOUS vs. definitive choice |
| Missing IFCT equivalent | NO_IFCT_EQUIVALENT vs. forced match |
| Reviewer interpretation difference | Same evidence, different conclusion |

### 3. Corrective Recommendations

- Per-disagreement root cause
- Schema/process/workbench fixes
- Reviewer training updates
- Evidence requirement clarifications

---

## Current Blocker Impact on Reliability Claims

Even if pilot were conducted, the following unresolved blockers would limit reliability claims:

| Blocker | Impact on Reliability |
|---------|----------------------|
| BLK-017: Second review not truly blind | Rationale reveals first decision → bias in κ |
| BLK-016: Cohen's κ without CI / prevalence adjustment | κ biased by class imbalance; no CI reported |
| BLK-006/010: Workflow ≠ mapping decision | Decision schema conflates process with outcome |
| BLK-015: Evidence refs not enforced | ACCEPTED decisions may lack mandatory evidence |

These must be resolved before any statistical reliability claims can be made.

---

## Conclusion

**NO DISAGREEMENT ANALYSIS PERFORMED.** Pilot review not authorized.

---

*End of Disagreement Analysis Report*