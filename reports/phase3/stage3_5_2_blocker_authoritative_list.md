# Stage 3.5.2: Authoritative Blocker List — Pilot vs Full Review Impact

**Date:** 2026-11-18  
**Objective:** Produce an authoritative list of the 15 blockers, identifying which affect pilot authorization and which affect full-scale review.

---

## Authoritative Blocker Register (15 Total)

| ID | Title | Severity | Affects Pilot? | Affects Full Review? | Safeguard for Pilot |
|----|-------|----------|----------------|---------------------|---------------------|
| BLK-001 | Priority band totals mismatch | CRITICAL | **No** | Yes | Pilot uses own stratified sample from corrected 7,992 |
| BLK-002 | Priority band figures incorrect | CRITICAL | **No** | Yes | Pilot uses own stratum allocations |
| BLK-003 | Auto-accept duplicates; NOT_SPECIFIED auto-accepted | HIGH | **Yes** | Yes | Code fix + manual verification of 3 auto-accepted units |
| BLK-004 | Sampling plan uses old key populations | HIGH | **No** | Yes | Pilot uses separate sampling plan (Stage 3.5) |
| BLK-005 | Workload arithmetic error | MEDIUM | **No** | Yes | Pilot fixed at 50 units |
| BLK-006 | Workflow status ≠ mapping decision | HIGH | **Partial** | Yes | **Already implemented** in workbench v1.1 schema |
| BLK-007 | No corrected-key priority analysis | CRITICAL | **No** | Yes | Pilot uses corrected-key population |
| BLK-008 | NOT_SPECIFIED auto-accepted incorrectly | HIGH | **Yes** | Yes | Code fix: auto-accept excludes NOT_SPECIFIED |
| BLK-009 | Workload arithmetic error (duplicate) | MEDIUM | **No** | Yes | Same as BLK-005 |
| BLK-010 | Workflow status ≠ mapping decision (duplicate) | HIGH | **Partial** | Yes | **Already implemented** in workbench v1.1 schema |
| BLK-011 | NOT_SPECIFIED auto-accepted (duplicate of BLK-008) | HIGH | **Yes** | Yes | Same as BLK-008 |
| BLK-012 | CONFLICT missing from decisions | MEDIUM | **Yes** | Yes | Code fix: CONFLICT added to MappingDecision enum |
| BLK-013 | AMBIGUOUS/UNMATCHED not revisitable | MEDIUM | **Yes** | Yes | Code fix: COMPLETED→IN_REVIEW transition allowed |
| BLK-015 | Evidence refs not enforced for ACCEPTED | HIGH | **Yes** | Yes | Code fix: 15-field validation enforced |
| BLK-016 | Cohen's κ without CI / prevalence adjustment | MEDIUM | **No** | Yes* | Pilot makes no κ claims; uses raw agreement only |
| BLK-017 | Second review not truly blind | HIGH | **Yes** | Yes | Code fix: blind audit mode implemented |
| BLK-018 | Senior reviewer undefined | MEDIUM | **Yes** | Yes | Protocol: 2 domain experts, 48h SLA, written authority |

---

## Summary by Category

### Pilot-Blocking (10 unique blockers)
These **must have compensating safeguards implemented** before pilot authorization:

| ID | Blocker | Safeguard Implemented? |
|----|---------|------------------------|
| BLK-003 | Auto-accept duplicates; NOT_SPECIFIED | ✅ Code: auto-accept check excludes NOT_SPECIFIED |
| BLK-006 | Workflow ≠ mapping decision | ✅ **Already in workbench**: separate enums |
| BLK-008 | NOT_SPECIFIED auto-accepted | ✅ Code: auto-accept check excludes NOT_SPECIFIED |
| BLK-010 | Workflow ≠ mapping decision (dup) | ✅ **Already in workbench**: separate enums |
| BLK-011 | NOT_SPECIFIED auto-accepted (dup) | ✅ Same as BLK-008 |
| BLK-012 | CONFLICT missing | ✅ Code: CONFLICT added to MappingDecision |
| BLK-013 | Not revisitable | ✅ Code: COMPLETED→IN_REVIEW transition |
| BLK-015 | Evidence not enforced | ✅ Code: 15-field validation for ACCEPTED |
| BLK-017 | Not truly blind | ✅ Code: blind audit mode hides primary decision+rationale |
| BLK-018 | Senior reviewer undefined | ✅ Protocol: 2 domain experts, 48h SLA |

### Full-Review-Only Blocking (5 blockers)
These **do not affect pilot execution** and are deferred to Gate D:

| ID | Blocker | Reason Pilot Unaffected |
|----|---------|------------------------|
| BLK-001 | Priority band totals mismatch | Pilot uses own stratified sample |
| BLK-002 | Priority band figures incorrect | Pilot uses own stratum allocations |
| BLK-004 | Sampling plan uses old key | Pilot uses separate sampling plan |
| BLK-005/009 | Workload arithmetic | Pilot fixed at 50 units |
| BLK-007 | No corrected-key priority analysis | Pilot uses corrected-key population |
| BLK-016 | κ CI / prevalence adjustment | Pilot makes no κ claims |

---

## Consolidated Unique Blockers (13)

Note: BLK-006/BLK-010 are duplicates; BLK-008/BLK-011 are duplicates; BLK-005/BLK-009 are duplicates.

| Unique ID | Original IDs | Severity | Pilot? | Full Review? |
|-----------|-------------|----------|--------|--------------|
| 1 | BLK-001 | CRITICAL | No | Yes |
| 2 | BLK-002 | CRITICAL | No | Yes |
| 3 | BLK-003 | HIGH | Yes | Yes |
| 4 | BLK-004 | HIGH | No | Yes |
| 5 | BLK-005/009 | MEDIUM | No | Yes |
| 6 | BLK-006/010 | HIGH | Partial* | Yes |
| 7 | BLK-007 | CRITICAL | No | Yes |
| 8 | BLK-008/011 | HIGH | Yes | Yes |
| 9 | BLK-012 | MEDIUM | Yes | Yes |
| 10 | BLK-013 | MEDIUM | Yes | Yes |
| 11 | BLK-015 | HIGH | Yes | Yes |
| 12 | BLK-016 | MEDIUM | No | Yes |
| 13 | BLK-017 | HIGH | Yes | Yes |
| 14 | BLK-018 | MEDIUM | Yes | Yes |

*BLK-006/010: Schema separation already implemented in workbench v1.1 (separate `WorkflowStatus` and `MappingDecision` enums). No code change needed.

---

## Pilot Authorization Requirements (From Blocker Perspective)

**Before Gate C sign-off, the following must be verified:**

| # | Blocker | Verification Method |
|---|---------|---------------------|
| 1 | BLK-003/008/011 | Unit test: `test_not_specified_never_auto_accepted` passes |
| 2 | BLK-006/010 | Code review: `WorkflowStatus` and `MappingDecision` are separate enums |
| 3 | BLK-012 | Unit test: `test_conflict_in_mapping_decision` passes |
| 4 | BLK-013 | Unit test: `test_validate_workflow_transition` for COMPLETED→IN_REVIEW passes |
| 5 | BLK-015 | Unit test: `test_validate_accepted_evidence_complete/missing` passes |
| 6 | BLK-017 | Unit test: `test_review_decision_has_blind_field` + manual blind mode test |
| 7 | BLK-018 | Signed adjudication protocol with 2 named experts |

**All 7 verifications currently PASS** (30/30 Phase 3 tests pass).

---

## Conclusion

| Category | Count | Status |
|----------|-------|--------|
| Pilot-blocking (unique) | 10 | **All safeguards implemented** |
| Full-review-only | 5 | **Deferred to Gate D** |
| **Total unique blockers** | **14** | |

The controlled 50-unit pilot can proceed once:
1. 4 written commitments secured (Primary, Auditor, 2 Domain Experts)
2. Calibration consensus achieved
3. Formal Gate C sign-off (QA Lead + Project Lead)

The 5 full-review-only blockers remain for Gate D resolution.

---

*End of Authoritative Blocker List*