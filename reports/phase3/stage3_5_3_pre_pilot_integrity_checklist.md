# Stage 3.5.3: Pre-Pilot Integrity Checklist

**Date:** 2026-11-18  
**Status:** Draft — To Be Completed Before Pilot Execution

---

## Purpose

This checklist verifies data integrity and system state before the controlled 50-unit pilot begins. All items must be verified and documented before Gate C authorization.

**No items have been verified.** This is a template for pre-pilot execution.

---

## Checklist

### 1. Frozen Input Hashes (8 Files)

| # | File | Expected SHA-256 | Actual SHA-256 | Match? | Verified By | Date |
|---|------|------------------|----------------|--------|-------------|------|
| 1 | `data/interim/phase2/normalized_ingredients.parquet` | `08710983213938c3fecafd20991ab7d3d7fe51b179303bbe4dc93b2ac1b1b6e5` | | ☐ Yes ☐ No | | |
| 2 | `data/interim/phase2/parsed_recipe_ingredients.parquet` | `e17b668b208dac4a7240cbfb27d78caac6123bc2b29b34a70aeb38964b9e86d9` | | ☐ Yes ☐ No | | |
| 3 | `data/interim/phase2/ingredient_synonyms.csv` | `22b8aace1ef29ea271051004a0e5a79ac8a8bfb5d80b8f796abe0db1f2ee4b31` | | ☐ Yes ☐ No | | |
| 4 | `data/interim/phase2/household_measurements.csv` | `451fb9c6d5135e0684bd5e6445aeaadfafa2951db6ae7fd939b96faad1e16b47` | | ☐ Yes ☐ No | | |
| 5 | `data/interim/ifct_final_candidate/ifct_table1_candidate.parquet` | `294c6fc4d095a47e13fbe02e8e3c1c0c8175752966275a3415f9a7df04774f35` | | ☐ Yes ☐ No | | |
| 6 | `data/interim/phase3/stage2_3/ifct_match_candidates.parquet` | `2bb9f0d7770f7669ad3cd30f49d2a15f820f572e53690678f58891229336740f` | | ☐ Yes ☐ No | | |
| 7 | `data/interim/phase3/stage2_3/unmatched_ingredients.parquet` | `4d4e2b84e3b3323552c600bf90eefba81c5e44ee8f455298f331c190ced08102` | | ☐ Yes ☐ No | | |
| 8 | `data/interim/phase3/stage2_3/household_measurements.csv` | `4c169cba077c49f384e699129e9051929ad130dda2221ac2692cf9c34e04567e` | | ☐ Yes ☐ No | | |

**All 8 hashes must match.** Any mismatch = BLOCKER.

---

### 2. Stage 2.3 Candidate Data Integrity

| Check | Description | Method | Pass? | Verified By | Date |
|-------|-------------|--------|-------|-------------|------|
| 2.1 | Candidate count | `len(ifct_match_candidates) == 119474` | ☐ Yes ☐ No | | |
| 2.2 | Unique review units (corrected key) | `df.groupby(['primary_ingredient','preparation_state','ifct_food_code']).ngroup().nunique() == 7992` | ☐ Yes ☐ No | | |
| 2.3 | Auto-accepted units | `df[~df['requires_review']]['review_unit_id'].nunique() == 3` | ☐ Yes ☐ No | | |
| 2.4 | NOT_SPECIFIED auto-accepted | `df[(df['preparation_state']=='NOT_SPECIFIED') & (~df['requires_review'])].empty == True` | ☐ Yes ☐ No | | |
| 2.5 | Review unit IDs present | `review_unit_id` column exists, no nulls | ☐ Yes ☐ No | | |
| 2.6 | IFCT food codes present | `ifct_food_code` column exists, no nulls | ☐ Yes ☐ No | | |
| 2.7 | Match methods valid | All values in {EXACT, SYNONYM, TOKEN_EQUIVALENT, TOKEN_SIMILARITY, FUZZY} | ☐ Yes ☐ No | | |
| 2.8 | Preparation states valid | All values in known enum | ☐ Yes ☐ No | | |
| 2.9 | Similarity scores range | All values in [0.0, 1.0] | ☐ Yes ☐ No | | |

---

### 3. IFCT Final Candidate Integrity

| Check | Description | Method | Pass? | Verified By | Date |
|-------|-------------|--------|-------|-------------|------|
| 3.1 | Row count | `len(ifct_table1_candidate) == 528` | ☐ Yes ☐ No | | |
| 3.2 | Food codes unique | `food_code.nunique() == 528` | ☐ Yes ☐ No | | |
| 3.3 | Food codes format | All match `[A-Z][0-9]{3}` | ☐ Yes ☐ No | | |
| 3.4 | Food groups present | All 18 expected groups present | ☐ Yes ☐ No | | |
| 3.5 | Key food codes present | A001, J001, N001, P001, Q001 present | ☐ Yes ☐ No | | |
| 3.6 | Nutrient columns present | All 9 nutrient columns exist | ☐ Yes ☐ No | | |
| 3.7 | No negative nutrients | All nutrient values ≥ 0 or NaN | ☐ Yes ☐ No | | |
| 3.8 | Missing nutrients preserved | NaN values not converted to 0 | ☐ Yes ☐ No | | |

---

### 4. Review Schema Version

| Check | Description | Expected | Actual | Pass? | Verified By | Date |
|-------|-------------|----------|--------|-------|-------------|------|
| 4.1 | Schema version | v1.1 | | ☐ Yes ☐ No | | |
| 4.2 | MappingDecision enum | 6 values (ACCEPTED, REJECTED, AMBIGUOUS, UNMATCHED, NO_IFCT_EQUIVALENT, CONFLICT) | | ☐ Yes ☐ No | | |
| 4.3 | WorkflowStatus enum | 5 values (DRAFT, PENDING, IN_REVIEW, ESCALATED, COMPLETED) | | ☐ Yes ☐ No | | |
| 4.4 | Evidence fields | 15 mandatory for ACCEPTED | | ☐ Yes ☐ No | | |
| 4.5 | Blind review flag | `is_blind_review` field present | | ☐ Yes ☐ No | | |

---

### 5. Separation of Reviewer Storage

| Check | Description | Method | Pass? | Verified By | Date |
|-------|-------------|--------|-------|-------------|------|
| 5.1 | Primary decisions directory exists | `data/interim/phase3/decisions/primary/` exists | ☐ Yes ☐ No | | |
| 5.2 | Auditor decisions directory exists | `data/interim/phase3/decisions/auditor/` exists | ☐ Yes ☐ No | | |
| 5.3 | Adjudication decisions directory exists | `data/interim/phase3/decisions/adjudication/` exists | ☐ Yes ☐ No | | |
| 5.4 | Primary decisions file | `primary/review_decisions.parquet` exists | ☐ Yes ☐ No | | |
| 5.5 | Auditor decisions file | `auditor/review_decisions.parquet` exists | ☐ Yes ☐ No | | |
| 5.6 | Adjudication decisions file | `adjudication/review_decisions.parquet` exists | ☐ Yes ☐ No | | |
| 5.6 | Primary history file | `primary/review_decisions_history.parquet` exists | ☐ Yes ☐ No | | |
| 5.7 | Auditor history file | `auditor/review_decisions_history.parquet` exists | ☐ Yes ☐ No | | |
| 5.8 | Adjudication history file | `adjudication/review_decisions_history.parquet` exists | ☐ Yes ☐ No | | |
| 5.9 | Submission states file | `submission_states.parquet` exists | ☐ Yes ☐ No | | |
| 5.10 | Primary cannot read auditor file | Verify app loads only `primary/` for PRIMARY role | ☐ Yes ☐ No | | |
| 5.11 | Auditor cannot read primary file | Verify app loads only `auditor/` for AUDITOR role | ☐ Yes ☐ No | | |

---

### 6. No Accidental Reuse of Prior Pilot Decisions

| Check | Description | Method | Pass? | Verified By | Date |
|-------|-------------|--------|-------|-------------|------|
| 6.1 | Primary decisions file empty | `len(primary_decisions) == 0` | ☐ Yes ☐ No | | |
| 6.2 | Auditor decisions file empty | `len(auditor_decisions) == 0` | ☐ Yes ☐ No | | |
| 6.3 | Adjudication decisions file empty | `len(adjudication_decisions) == 0` | ☐ Yes ☐ No | | |
| 6.4 | Submission states empty | `submission_states` all NOT_STARTED | ☐ Yes ☐ No | | |
| 6.5 | No prior pilot decisions in history | History files empty or only headers | ☐ Yes ☐ No | | |
| 6.6 | No Stage 3.4 test decisions present | Verify no test data in pilot dirs | ☐ Yes ☐ No | | |

---

### 7. No Unadjudicated Pilot Mapping Treated as Accepted

| Check | Description | Method | Pass? | Verified By | Date |
|-------|-------------|--------|-------|-------------|------|
| 7.1 | Submission state machine enforced | `VALID_TRANSITIONS` prevents NOT_STARTED → ADJUDICATED | ☐ Yes ☐ No | | |
| 7.2 | Adjudication gate enforced | `can_adjudicate()` requires BOTH_SUBMITTED | ☐ Yes ☐ No | | |
| 7.3 | No ACCEPTED without evidence | 15-field validation blocks incomplete ACCEPTED | ☐ Yes ☐ No | | |
| 7.4 | NOT_SPECIFIED never auto-accepted | `check_auto_accept_eligibility()` rejects NOT_SPECIFIED | ☐ Yes ☐ No | | |
| 7.5 | Adjudication decisions stored separately | Adjudication decisions in `adjudication/` dir | ☐ Yes ☐ No | | |
| 7.6 | Original submissions preserved | Primary + auditor decisions unchanged after adjudication | ☐ Yes ☐ No | | |

---

### 8. Workbench Safeguards Active

| Check | Description | Method | Pass? | Verified By | Date |
|-------|-------------|--------|-------|-------------|------|
| 8.1 | NOT_SPECIFIED auto-accept prevention | Unit test `test_not_specified_never_auto_accepted` passes | ☐ Yes ☐ No | | |
| 8.2 | CONFLICT decision support | Unit test `test_conflict_in_mapping_decision` passes | ☐ Yes ☐ No | | |
| 8.3 | Revisitable transitions | Unit test `test_allowed_transitions` passes | ☐ Yes ☐ No | | |
| 8.4 | 15-field ACCEPTED enforcement | Unit test `test_validate_accepted_evidence_missing` passes | ☐ Yes ☐ No | | |
| 8.5 | Blind audit mode enforced | Unit tests `test_review_decision_has_blind_field`, `test_auditor_role_supported` pass | ☐ Yes ☐ No | | |

---

### 9. Application Launch and Authentication

| Check | Description | Method | Pass? | Verified By | Date |
|-------|-------------|--------|-------|-------------|------|
| 9.1 | App launches | `streamlit run app/ingredient_review_app.py` → localhost | ☐ Yes ☐ No | | |
| 9.2 | Login screen displayed | Authentication screen shown first | ☐ Yes ☐ No | | |
| 9.3 | Primary login works | Valid primary ID → primary workspace | ☐ Yes ☐ No | | |
| 9.3 | Auditor login works | Valid auditor ID → auditor workspace | ☐ Yes ☐ No | | |
| 9.4 | Adjudicator login works | Valid adjudicator ID → adjudicator workspace | ☐ Yes ☐ No | | |
| 9.5 | Invalid ID rejected | Unknown ID → error | ☐ Yes ☐ No | | |
| 9.6 | Role enforced | No role dropdown in sidebar | ☐ Yes ☐ No | | |
| 9.7 | Logout works | Logout button clears session | ☐ Yes ☐ No | | |

---

### 10. Blind Review Verification

| Check | Description | Method | Pass? | Verified By | Date |
|-------|-------------|--------|-------|-------------|------|
| 10.1 | Primary cannot see auditor decisions | Login primary, check dashboard → no auditor data | ☐ Yes ☐ No | | |
| 10.2 | Auditor cannot see primary decisions | Login auditor, check dashboard → no primary data | ☐ Yes ☐ No | | |
| 10.3 | Blind status message | When other submitted → "🔒 Blind Review Active" | ☐ Yes ☐ No | | |
| 10.4 | Submission state advances | Primary submits → PRIMARY_SUBMITTED; Auditor submits → BOTH_SUBMITTED | ☐ Yes ☐ No | | |
| 10.5 | Adjudication enabled after both | State = READY_FOR_ADJUDICATION after BOTH_SUBMITTED | ☐ Yes ☐ No | | |

---

### 11. Calibration Verification

| Check | Description | Method | Pass? | Verified By | Date |
|-------|-------------|--------|-------|-------------|------|
| 11.1 | Calibration units load | Navigate to 5 calibration units in workbench | ☐ Yes ☐ No | | |
| 11.2 | Primary calibration complete | Primary reviewer completed all 5 units | ☐ Yes ☐ No | | |
| 11.3 | Auditor calibration complete | Auditor completed all 5 units | ☐ Yes ☐ No | | |
| 11.4 | Calibration consensus | Consensus achieved on all 5 units | ☐ Yes ☐ No | | |
| 11.5 | Consensus record filed | `stage3_5_3_calibration_consensus_record.md` completed | ☐ Yes ☐ No | | |

---

## Summary

| Section | Total Checks | Passed | Failed | Blocked |
|---------|-------------|--------|--------|---------|
| 1. Frozen Input Hashes | 8 | | | |
| 2. Stage 2.3 Candidate Data | 9 | | | |
| 3. IFCT Final Candidate | 8 | | | |
| 4. Review Schema Version | 5 | | | |
| 5. Reviewer Storage Separation | 11 | | | |
| 6. No Prior Pilot Decision Reuse | 6 | | | |
| 7. No Unadjudicated Accepted | 6 | | | |
| 8. Safeguards Active | 5 | | | |
| 9. App Launch & Auth | 7 | | | |
| 10. Blind Review Verification | 5 | | | |
| 11. Calibration Verification | 5 | | | |
| **TOTAL** | **71** | | | |

---

## Final Verification Statement

**All 71 checks must PASS for pre-pilot integrity verification.**

| Outcome | Action |
|---------|--------|
| **All PASS** | Proceed to Gate C sign-off |
| **Any FAIL** | Block pilot; resolve failure; re-verify |
| **Any BLOCKED** | Cannot proceed; escalate |

---

## Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| QA Lead (Verifier) | | | |
| Project Lead (Approver) | | | |

---

*End of Pre-Pilot Integrity Checklist*