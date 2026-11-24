# Stage 3.5.2: Safeguard Test Report

**Date:** 2026-11-18  
**Test Suite:** `tests/phase3/test_review_app.py` (30 tests)  
**Full Regression:** `tests/` (149 tests)  
**Python:** 3.15.2, pytest 9.2.0

---

## Phase 3 Application Test Results (30/30 PASS)

| Test Class | Test | Safeguard | Status |
|------------|------|-----------|--------|
| **TestDataLoading** | test_load_review_units | — | ✅ |
| | test_load_ifct_data | — | ✅ |
| | test_load_unmatched | — | ✅ |
| | test_load_ifct | — | ✅ |
| **TestReviewUnitKey** | test_flawed_key_has_duplicates | — | ✅ |
| | test_corrected_key_uniqueness | — | ✅ |
| **TestAutoAcceptance** | test_auto_accept_count | 1 | ✅ |
| | test_auto_accept_are_exact_fresh | 1 | ✅ |
| | test_not_specified_never_auto_accepted | **1** | ✅ |
| | test_auto_accept_eligibility_check | **1** | ✅ |
| **TestDecisionValidation** | test_accept_requires_15_evidence_fields | **4** | ✅ |
| | test_validate_accepted_evidence_complete | **4** | ✅ |
| | test_validate_accepted_evidence_missing | **4** | ✅ |
| | test_confidence_constraints | 4 | ✅ |
| **TestConflictDecision** | test_conflict_in_mapping_decision | **2** | ✅ |
| | test_conflict_requires_alt_code | 2 | ✅ |
| **TestWorkflowTransitions** | test_allowed_transitions | **3** | ✅ |
| | test_validate_workflow_transition | **3** | ✅ |
| **TestBlindAuditMode** | test_review_decision_has_blind_field | **5** | ✅ |
| | test_auditor_role_supported | **5** | ✅ |
| **TestPersistence** | test_decision_persistence | — | ✅ |
| | test_history_preserved | — | ✅ |
| **TestDuplicatePrevention** | test_no_duplicate_decisions_same_reviewer | — | ✅ |
| **TestAuditHistory** | test_audit_history_preserved | — | ✅ |
| **TestMissingNutrientHandling** | test_missing_nutrients_preserved | — | ✅ |
| **TestCandidateFiltering** | test_filter_by_preparation_state | — | ✅ |
| **TestPreparationStateCompatibility** | test_prep_state_compat_raw_fresh | — | ✅ |
| | test_prep_state_compat_not_specified | — | ✅ |
| **TestExportConsistency** | test_export_consistency | — | ✅ |
| **TestCalibrationSet** | test_calibration_set_exists | — | ✅ |

**Total: 30 passed, 0 failed, 0 skipped**

---

## Safeguard-Specific Test Coverage

| Safeguard | Tests | Description |
|-----------|-------|-------------|
| **1. NOT_SPECIFIED auto-accept prevention** | 2 | `test_not_specified_never_auto_accepted`, `test_auto_accept_eligibility_check` |
| **2. CONFLICT decision support** | 2 | `test_conflict_in_mapping_decision`, `test_conflict_requires_alt_code` |
| **3. Revisitable workflow transitions** | 2 | `test_allowed_transitions`, `test_validate_workflow_transition` |
| **4. ACCEPTED evidence enforcement** | 3 | `test_accept_requires_15_evidence_fields`, `test_validate_accepted_evidence_complete`, `test_validate_accepted_evidence_missing` |
| **5. Blind audit mode** | 2 | `test_review_decision_has_blind_field`, `test_auditor_role_supported` |
| **Total safeguard tests** | **11** | |

---

## Full Regression Test Results (149 tests)

| Module | Tests | Passed | Failed | Notes |
|--------|-------|--------|--------|-------|
| Phase 1 (`test_phase1.py`) | 44 | 44 | 0 | |
| Phase 2 Normalization | 14 | 14 | 0 | |
| Phase 2 Quantity | 27 | 27 | 0 | |
| Phase 3 Application | 30 | 30 | 0 | **All new safeguard tests pass** |
| IFCT Extraction | 34 | 27 | 7 | Pre-existing raw extraction issues |
| **Total** | **149** | **142** | **7** | **7 pre-existing, 0 new regressions** |

### IFCT Extraction Failures (Pre-Existing, Not New)

| Test | Issue | Classification |
|------|-------|----------------|
| `test_parsed_rows` | 512 rows vs expected ≤450 | Raw CSV has more rows than expected |
| `test_food_groups_identified` | Missing CONDIMENTS AND SPICES-DRY | Raw CSV missing group |
| `test_amaranth_seed` | A001 missing from raw CSV | Raw CSV missing food code |
| `test_button_mushroom` | J001 missing from raw CSV | Raw CSV missing food code |
| `test_chicken_leg` | N001 missing from raw CSV | Raw CSV missing food code |
| `test_allathi_fish` | P001 missing from raw CSV | Raw CSV missing food code |
| `test_crab` | Q001 missing from raw CSV | Raw CSV missing food code |

**Note:** The application uses `ifct_table1_candidate.parquet` (528 rows, complete), not the raw extraction CSV (512 rows, incomplete). These 7 failures are pre-existing data quality issues in the intermediate extraction artifact and do not affect the workbench.

---

## Persistence & Integrity Tests

| Test | Verifies |
|------|----------|
| `test_decision_persistence` | Decisions survive save/load cycle |
| `test_history_preserved` | History file accumulates all saves |
| `test_no_duplicate_decisions_same_reviewer` | Same reviewer/unit replaces previous |
| `test_audit_history_preserved` | Both decisions retained in history |
| `test_export_consistency` | Round-trip save/load matches original |

All **5/5 pass**.

---

## Data Integrity Verification

| Check | Result |
|-------|--------|
| Frozen input hashes (8/8) | ✅ All match |
| Missing nutrients remain NaN | ✅ Not converted to zero |
| Review unit uniqueness (corrected key) | ✅ 7,992 unique |
| Auto-accepted units | ✅ 3 unique (4 rows) |
| NOT_SPECIFIED never auto-accepted | ✅ Verified |

---

## Manual Verification

| Check | Method | Result |
|-------|--------|--------|
| App launches | `streamlit run app/ingredient_review_app.py` | ✅ http://localhost:8503 |
| Blind mode toggle visible | Auditor role in sidebar | ✅ |
| CONFLICT in decision radio | MappingDecision enum | ✅ |
| 15-field evidence list | Placeholder text in form | ✅ |
| Workflow transitions | ALLOWED_TRANSITIONS dict | ✅ |
| NOT_SPECIFIED warning | Candidate display panel | ✅ |

---

## Test Execution Commands

```bash
# Phase 3 application tests only
py -m pytest tests/phase3/test_review_app.py -v

# Full regression suite
py -m pytest tests/ -v
```

---

## Summary

| Metric | Value |
|--------|-------|
| Phase 3 tests | 30/30 PASS |
| Safeguard-specific tests | 11/11 PASS |
| Full regression | 142/149 PASS (7 pre-existing) |
| New regressions | 0 |
| Frozen inputs | 8/8 verified |
| App launch | ✅ Verified |

**All five safeguards are implemented and independently testable.**

---

*End of Safeguard Test Report*