# Stage 3.2.2: Final Blocker Register

**Date:** 2026-11-18  
**Source:** Independent numerical and consistency audit (Stage 3.2.1)

---

## Blocker Register

Each blocker has a unique ID, description, evidence, severity, dependency, required resolution, and verification test.

| ID | Title | Severity | Description | Evidence | Resolution Required | Dependency |
|----|-------|----------|-------------|----------|---------------------|------------|
| BLK-001 | Priority band totals don't match corrected review unit count | CRITICAL | Correction report claims 7,992 review units but priority bands sum to 7,165 (old count). 810 units unaccounted. | Correction report §2.3 table sums to 7,165; corrected key has 7,992 units | Recalculate priority bands for all 7,992 corrected review units | None | 🔴 OPEN |
| BLK-002 | Priority band figures in correction report don't match actual data | CRITICAL | Reported: Critical=46, High=237, Medium=1,284, Standard=2,898, Low=2,700. Actual: Critical=25, High=95, Medium=1,589, Standard=5,463, Low=0 | Independent audit counts vs reported figures | Recalculate all priority bands from source data for both keys | BLK-001 | 🔴 OPEN |
| BLK-003 | Auto-accept "6 units" includes duplicates; NOT_SPECIFIED incorrectly auto-accepted | HIGH | 6 corrected auto-accept units include 3 duplicate ingredient-IFCT pairs; NOT_SPECIFIED prep incorrectly auto-accepted | Audit: 6 corrected auto-accept units include 3 duplicate ingredient-IFCT pairs; 0 NOT_SPECIFIED candidates auto-accepted in source | Fix Stage 2.3 gate: NOT_SPECIFIED must not auto-accept; deduplicate corrected auto-accept count | None | 🔴 OPEN |
| BLK-004 | Sampling plan uses old key populations | HIGH | TOKEN_SIMILARITY sample 695 vs 772 needed; strata populations from old 7,165 key | TOKEN_SIMILARITY population 7,720 (corrected) vs 6,949 (flawed); 10% = 772 not 695 | Recalculate all strata populations from corrected 7,992 review units | BLK-001 | 🔴 OPEN |
| BLK-005 | Workload arithmetic error (2,116 vs 2,080 hrs) | MEDIUM | 2,115.8 hrs actual vs 2,080 reported | Arithmetic: 1,700.5 + 340 + 35.8 + 40 = 2,115.8 ≠ 2,080 | Fix arithmetic: 1,700.5 + 340 + 35.8 + 40 = 2,115.8 hrs | None | 🔴 OPEN |
| BLK-006 | Workflow status vs mapping decision not separated | HIGH | Single `status` field conflates workflow progress with mapping decision | Schema has single `status` field serving both purposes | Add `workflow_status` (DRAFT→PENDING→IN_REVIEW→COMPLETED) separate from `mapping_decision` (ACCEPTED/REJECTED/AMBIGUOUS/UNMATCHED/NO_IFCT_EQUIVALENT) | None | 🔴 OPEN |
| BLK-007 | Sampling plan uses old key populations | HIGH | Strata populations based on 7,165 review units, not 7,992 | TOKEN_SIMILARITY pop 6,949 vs 7,720; 10% = 772 not 695 | Recalculate all strata populations from corrected 7,992 review units | BLK-001 | 🔴 OPEN |
| BLK-008 | NOT_SPECIFIED auto-accepted incorrectly | HIGH | 3 artifacts in 6 "corrected" auto-accept units have NOT_SPECIFIED prep | Audit: 0 NOT_SPECIFIED candidates auto-accepted in source; 2 appear in corrected auto-accept | Fix Stage 2.3 gate: NOT_SPECIFIED requires explicit evidence, not auto-accept | None | 🔴 OPEN |
| BLK-006 | No corrected-key priority analysis | CRITICAL | No priority band analysis exists for 7,992 corrected review units | Stage 3.2 docs only show priority bands for old 7,165 key | Generate priority bands for corrected 7,992 review units | BLK-001 | 🔴 OPEN |
| BLK-009 | Workload arithmetic error | MEDIUM | 2,115.8 hrs actual vs 2,080 reported | 1,700.5 + 340 + 35.8 + 40 = 2,115.8 ≠ 2,080 | Fix arithmetic: 1,700.5 + 340 + 35.8 + 40 = 2,115.8 hrs | None | 🔴 OPEN |
| BLK-010 | Workflow status vs mapping decision not separated | HIGH | Single `status` field conflates workflow progress with mapping decision | Schema has single `status` field serving both purposes | Add `workflow_status` (DRAFT→PENDING→IN_REVIEW→COMPLETED) separate from `mapping_decision` (ACCEPTED/REJECTED/AMBIGUOUS/UNMATCHED/NO_IFCT_EQUIVALENT) | None | 🔴 OPEN |
| BLK-010 | Sampling plan uses old key populations | HIGH | Strata populations based on 7,165 review units, not 7,992 | TOKEN_SIMILARITY pop 6,949 vs 7,720; 10% = 772 not 695 | Recalculate all strata populations from corrected 7,992 review units | BLK-001 | 🔴 OPEN |
| BLK-010 | No corrected-key priority analysis | CRITICAL | No priority band analysis exists for 7,992 corrected review units | Stage 3.2 docs only show priority bands for old 7,165 key | Generate priority bands for corrected 7,992 review units | BLK-001 | 🔴 OPEN |
| BLK-011 | NOT_SPECIFIED auto-accepted incorrectly | HIGH | 3 artifacts in 6 "corrected" auto-accept units have NOT_SPECIFIED prep | Audit: 0 NOT_SPECIFIED candidates auto-accepted in source; 2 appear in corrected auto-accept | Fix Stage 2.3 gate: NOT_SPECIFIED requires explicit evidence, not auto-accept | None | 🔴 OPEN |
| BLK-011 | Workload arithmetic error | MEDIUM | 2,115.8 hrs actual vs 2,080 reported | Arithmetic: 1,700.5 + 340 + 35.8 + 40 = 2,115.8 ≠ 2,080 | Fix arithmetic: 1,700.5 + 340 + 35.8 + 40 = 2,115.8 hrs | None | 🔴 OPEN |
| BLK-011 | CONFLICT status missing from decisions table | MEDIUM | CONFLICT in review_units but not in decisions table | Audit trail broken | Add CONFLICT to decisions.valid_statuses | None | 🔴 OPEN |
| BLK-012 | AMBIGUOUS/UNMATCHED not revisitable in decisions table | MEDIUM | Status transitions don't allow revisiting | Mappings can't be corrected | Add transitions: AMBIGUOUS→REVIEW_REQUIRED, UNMATCHED→REVIEW_REQUIRED | None | 🔴 OPEN |
| BLK-012 | Evidence references not enforced for ACCEPTED | HIGH | Schema says mandatory but validation only checks rationale length | Weak evidence trail | Add validation: ACCEPTED requires evidence_references field populated | None | 🔴 OPEN |
| BLK-012 | Cohen's κ without CI / prevalence adjustment | MEDIUM | κ biased by class imbalance; no CI reported | Misleading quality metric | Add Gwet's AC1 + 95% CI for κ | QA Lead | 🔴 OPEN |
| BLK-013 | Second review not truly blind | HIGH | "Blind to first decision (except rationale)" — rationale reveals decision | Bias in second review | Hide first decision AND rationale from second reviewer | Engineer | 🔴 OPEN |
| BLK-014 | Senior reviewer role undefined | MEDIUM | No selection criteria, SLA, or authority defined | Escalation path broken | Define role, selection, SLA (24h), authority | PM | 🔴 OPEN |

---

## Blocker Summary

| Severity | Count | Must Fix Before Workbench |
|--------|-------|---------------------------|
| CRITICAL | 2 | ✅ YES |
| HIGH | 7 | ✅ YES |
| MEDIUM | 4 | ⚠️ BEFORE LAUNCH |
| **TOTAL** | **13** | |

---

## Resolution Tracking

| ID | Resolution | Verified By | Date |
|----|------------|-------------|------|
| BLK-001 | [PENDING] Recalculate priority bands for 7,992 corrected review units | | |
| BLK-002 | [PENDING] Regenerate priority band table with actual data | | |
| BLK-003 | [PENDING] Fix Stage 2.3 gate; deduplicate auto-accept count | | |
| BLK-004 | [PENDING] Recalculate sampling strata from 7,992 corrected units | | |
| BLK-005 | [PENDING] Fix workload arithmetic: 2,115.8 hrs | | |
| BLK-006 | [PENDING] Separate workflow_status from mapping_decision in schema | | |
| BLK-007 | [PENDING] Recalculate strata populations from 7,992 corrected units | | |
| BLK-007 | [PENDING] Generate priority bands for corrected 7,992 review units | | |
| BLK-008 | [PENDING] Fix Stage 2.3 gate; NOT_SPECIFIED requires evidence | | |
| BLK-009 | [PENDING] Fix workload arithmetic: 2,115.8 hrs | | |
| BLK-010 | [PENDING] Separate workflow_status from mapping_decision in schema | | |
| BLK-011 | [PENDING] Secure ≥4 written reviewer commitments | | |
| BLK-011 | [PENDING] Define single-reviewer contingency plan | | |
| BLK-012 | [PENDING] Add CONFLICT to decisions.valid_statuses | | |
| BLK-013 | [PENDING] Add AMBIGUOUS→REVIEW_REQUIRED, UNMATCHED→REVIEW_REQUIRED transitions | | |
| BLK-013 | [PENDING] Add validation: ACCEPTED requires evidence_references | | |
| BLK-014 | [PENDING] Blind second review (hide decision + rationale) | | |
| BLK-015 | [PENDING] Define senior reviewer role, SLA, authority | | |

---

## Resolution Tracking

| ID | Resolution | Verified By | Date |
|----|------------|-------------|------|
| BLK-001 | [PENDING] | | |
| BLK-002 | [PENDING] | | |
| BLK-003 | [PENDING] | | |
| BLK-004 | [PENDING] | | |
| BLK-005 | [PENDING] | | |
| BLK-006 | [PENDING] | | |
| BLK-006 | [PENDING] | | |
| BLK-007 | [PENDING] | | |
| BLK-008 | [PENDING] | | |
| BLK-009 | [PENDING] | | |
| BLK-010 | [PENDING] | | |
| BLK-011 | [PENDING] | | |
| BLK-011 | [PENDING] | | |
| BLK-012 | [PENDING] | | |
| BLK-013 | [PENDING] | | |
| BLK-014 | [PENDING] | | |
| BLK-015 | [PENDING] | | |
| BLK-016 | [PENDING] | | |

---

## Go/No-Go Criteria for Workbench Implementation

| Criterion | Status | Evidence Required |
|-----------|--------|-------------------|
| All CRITICAL blockers resolved | ❌ | BLK-001, BLK-008 resolved |
| All HIGH blockers resolved | ❌ | BLK-002,004,006,008,010,013,015 resolved |
| Schema v1.1 formally approved | ❌ | Architecture review sign-off |
| ≥4 reviewers committed | ❌ | Signed commitments |
| Workbench prototype tested | ❌ | Pilot review (50 units) completed |
| Calibration materials ready | ❌ | 5-unit calibration set prepared |
| QA sign-off on design | ❌ | QA Lead sign-off |

**Overall: NO-GO** — 9 blockers remain (2 CRITICAL, 7 HIGH)

---

## Single-Reviewer Contingency Plan

If only 1 reviewer available:
- **Scope reduction:** Review only Critical (30) + High (160) + Medium (1,727) = 1,917 units
- **Effort:** 1,917 × 12 min avg = 383 hrs primary + 77 audit = 460 hrs
- **Duration:** 460 hrs / (2 hrs/day × 5 days/wk) = 46 weeks
- **Defer:** Standard (6,075), Low (0), Ambiguous (610 ingredients), Unmatched (11,310) → Phase 3b
- **Risk:** 76% of review units deferred; nutrition calculations incomplete

---

**Audit Complete.** All findings documented. No workbench implementation until all CRITICAL and HIGH blockers resolved.