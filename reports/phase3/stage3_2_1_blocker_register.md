# Stage 3.2.1: Blocker Register

**Date:** 2026-11-18  
**Status:** Active — All blockers must be resolved before workbench implementation

---

## Blocker Register

| ID | Title | Severity | Description | Impact | Resolution | Owner | Target Date | Status |
|----|-------|----------|-------------|--------|------------|-------|-------------|--------|
| BLK-001 | Priority band totals don't match corrected review unit count | CRITICAL | Correction report claims 7,992 review units but priority bands sum to 7,165 (old count). 810 units unaccounted. | Cannot schedule reviews; priority queue broken | Recalculate priority bands for corrected 7,992 review units | Architect | 2026-11-20 | 🔴 OPEN |
| BLK-002 | Priority band figures in correction report don't match actual data | CRITICAL | Reported High=237, actual=95; Medium=1284 vs 1589; Standard=2898 vs 5463 | Wrong review prioritization; resource misallocation | Recalculate priority scores for all 7,992 units with corrected weights | Architect | 2026-11-20 | 🔴 OPEN |
| BLK-003 | Auto-accept "6 units" includes duplicates; NOT_SPECIFIED incorrectly auto-accepted | HIGH | 6 auto-accept count includes duplicates; NOT_SPECIFIED prep state incorrectly auto-accepted | Incorrect mappings approved; safety risk | Fix Stage 2.3 gate: NOT_SPECIFIED must not auto-accept; deduplicate corrected auto-accept count | Engineer | 2026-11-20 | 🔴 OPEN |
| BLK-004 | Sampling plan uses old key populations | HIGH | TOKEN_SIMILARITY sample 50 vs 695 needed; strata populations wrong | Inadequate audit coverage; false confidence | Recalculate strata populations from corrected 7,992 review units | QA Lead | 2026-11-20 | 🔴 OPEN |
| BLK-005 | Workload arithmetic error (2,116 vs 2,080 hrs) | MEDIUM | 2,115.8 hrs actual vs 2,080 reported | Timeline underestimation | Fix arithmetic: 1,700.5 + 340 + 35.8 + 40 = 2,115.8 hrs | PM | 2026-11-20 | 🔴 OPEN |
| BLK-005 | Workflow status vs mapping decision not separated | HIGH | Single `status` field conflates workflow progress with mapping decision | Cannot track review progress; decision history unclear | Add `workflow_status` (DRAFT→PENDING→IN_REVIEW→COMPLETED) separate from `mapping_decision` (ACCEPTED/REJECTED/AMBIGUOUS/UNMATCHED/NO_IFCT_EQUIVALENT) | Architect | 2026-11-22 | 🔴 OPEN |
| BLK-006 | Sampling plan uses old key populations | HIGH | Strata populations based on 7,165 review units, not 7,992 | Under/over-sampling bias | Recalculate all strata populations from corrected 7,992 review units | QA Lead | 2026-11-22 | 🔴 OPEN |
| BLK-007 | No corrected-key priority analysis | CRITICAL | No priority band analysis exists for 7,992 corrected review units | Cannot prioritize review work | Generate priority bands for corrected 7,992 units | Architect | 2026-11-20 | 🔴 OPEN |
| BLK-008 | Auto-accept NOT_SPECIFIED prep state incorrectly allowed | HIGH | 2 auto-accepted units have NOT_SPECIFIED prep (coriander leaves) | Safety risk: prep-state mismatch | Fix Stage 2.3 gate: NOT_SPECIFIED requires explicit evidence, not auto-accept | Engineer | 2026-11-20 | 🔴 OPEN |
| BLK-009 | Workload arithmetic error (2,116 vs 2,080 hrs) | MEDIUM | 2,115.8 hrs actual vs 2,080 reported | Timeline underestimation | Fix arithmetic: 1,700.5 + 340 + 35.8 + 40 = 2,115.8 hrs | PM | 2026-11-20 | 🔴 OPEN |
| BLK-010 | 8 reviewers unconfirmed | HIGH | Plan assumes 8 reviewers; 0 confirmed | Schedule risk | Secure ≥4 written commitments | PM | 2026-11-25 | 🔴 OPEN |
| BLK-011 | Single-reviewer fallback not viable | HIGH | 2,116 hrs / 10 hrs/week = 212 weeks (4 years) | Project failure if team < 4 | Define minimum viable team (4 reviewers) and contingency plan | PM | 2026-11-25 | 🔴 OPEN |
| BLK-011 | CONFLICT status missing from decisions table | MEDIUM | CONFLICT in review_units but not in decisions table | Audit trail broken | Add CONFLICT to decisions.valid_statuses | Architect | 2026-11-22 | 🔴 OPEN |
| BLK-012 | AMBIGUOUS/UNMATCHED not revisitable in decisions table | MEDIUM | Status transitions don't allow revisiting | Mappings can't be corrected | Add transitions: AMBIGUOUS→REVIEW_REQUIRED, UNMATCHED→REVIEW_REQUIRED | Architect | 2026-11-22 | 🔴 OPEN |
| BLK-013 | Evidence references not enforced for ACCEPTED | HIGH | Schema says mandatory but validation only checks rationale length | Weak evidence trail | Add validation: ACCEPTED requires evidence_references field populated | Engineer | 2026-11-22 | 🔴 OPEN |
| BLK-014 | Cohen's κ without CI / prevalence adjustment | MEDIUM | κ biased by class imbalance; no CI reported | Misleading quality metric | Add Gwet's AC1 + 95% CI for κ | QA Lead | 2026-11-22 | 🔴 OPEN |
| BLK-015 | Second review not truly blind | HIGH | "Blind to first decision (except rationale)" — rationale reveals decision | Bias in second review | Hide first decision AND rationale from second reviewer | Engineer | 2026-11-22 | 🔴 OPEN |
| BLK-015 | Senior reviewer role undefined | MEDIUM | No selection criteria, SLA, or authority defined | Escalation path broken | Define role, selection, SLA (24h), authority | PM | 2026-11-25 | 🔴 OPEN |

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
| BLK-006 | [PENDING] Recalculate strata from 7,992 corrected units | | |
| BLK-007 | [PENDING] Generate priority bands for 7,992 corrected units | | |
| BLK-008 | [PENDING] Fix Stage 2.3 gate; NOT_SPECIFIED requires evidence | | |
| BLK-009 | [PENDING] Fix workload arithmetic: 2,115.8 hrs | | |
| BLK-010 | [PENDING] Secure ≥4 written reviewer commitments | | |
| BLK-011 | [PENDING] Define single-reviewer contingency plan | | |
| BLK-012 | [PENDING] Add CONFLICT to decisions.valid_statuses | | |
| BLK-013 | [PENDING] Add AMBIGUOUS→REVIEW_REQUIRED, UNMATCHED→REVIEW_REQUIRED transitions | | |
| BLK-014 | [PENDING] Add validation: ACCEPTED requires evidence_references | | |
| BLK-015 | [PENDING] Blind second review (hide decision + rationale) | | |
| BLK-016 | [PENDING] Define senior reviewer role, SLA, authority | | |

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
- **Scope reduction:** Review only Critical (25) + High (95) + Medium (1,599) = 1,719 units
- **Effort:** 1,719 × 12 min avg = 344 hrs primary + 69 audit = 413 hrs
- **Duration:** 413 hrs / (2 hrs/day × 5 days/wk) = 41 weeks
- **Defer:** Standard (5,463), Low (0), Ambiguous (1,255), Unmatched (11,310) → Phase 3b
- **Risk:** 76% of review units deferred; nutrition calculations incomplete

---

**Audit Complete.** All findings documented. No workbench implementation until all CRITICAL and HIGH blockers resolved.