# Stage 3.5: Calibration Report

**Date:** 2026-11-18  
**Status:** Calibration materials verified — Pilot NOT authorized

---

## Executive Summary

The 5-unit calibration set from Stage 3.4 has been verified and is ready for use. However, **the 50-unit pilot review is NOT authorized** per Stage 3.3.2 governance decision (Gate B and Gate C both not met). This report documents the calibration verification only.

---

## Calibration Set Verification

The calibration set at `reports/phase3/stage3_4_calibration_set.md` contains 5 units covering the range of matching scenarios:

| Unit | Ingredient | Prep State | Match Method | Expected Decision | Key Reason |
|------|------------|------------|--------------|-------------------|------------|
| 1 | Turmeric powder (haldi) | FRESH | EXACT | **ACCEPTED** | EXACT + FRESH + sim=1.0 + single IFCT |
| 2 | Coriander powder (dhania) | NOT_SPECIFIED | SYNONYM | **REVIEW_REQUIRED** | NOT_SPECIFIED never auto-accepted |
| 3 | Lemon juice | NOT_SPECIFIED | TOKEN_EQUIVALENT | **REVIEW_REQUIRED** | TOKEN_EQUIVALENT ≠ EXACT + NOT_SPECIFIED |
| 4 | Red chilli powder | POWDERED | TOKEN_SIMILARITY | **AMBIGUOUS** | 7 equally plausible IFCT codes |
| 5 | Quinoa | NOT_SPECIFIED | — | **NO_IFCT_EQUIVALENT** | Not in IFCT 2017 |

### Verification Results

| Check | Result |
|-------|--------|
| All 5 units load in workbench | ✅ Verified |
| IFCT candidates traceable | ✅ Verified |
| Evidence requirements align with schema v1.1 | ✅ Verified |
| Auto-accept policy correctly reflected | ✅ Verified |
| NOT_SPECIFIED correctly requires review | ✅ Verified |
| TOKEN_EQUIVALENT correctly not auto-accepted | ✅ Verified |
| Multi-code ambiguity correctly marked AMBIGUOUS | ✅ Verified |
| Absent ingredient correctly marked NO_IFCT_EQUIVALENT | ✅ Verified |

---

## Calibration Procedure (For Future Use)

When pilot is authorized, calibration shall proceed as:

1. **Independent Review** — Each reviewer independently evaluates all 5 units in the workbench
2. **Decision Recording** — Record decision, rationale (≥50 chars), evidence references (15 fields for ACCEPTED), confidence (1-5)
3. **Comparison** — Compare decisions against expected decisions in calibration set
4. **Discrepancy Resolution** — Discuss any discrepancies with calibration coordinator
5. **Consensus Requirement** — All reviewers must achieve consistency on all 5 units before proceeding to pilot

### Evidence Requirements for ACCEPTED (15 Mandatory Fields)

Per schema v1.1, ACCEPTED decisions require all 15 evidence references:
1. `ifct_food_code`
2. `ifct_food_name`
3. `ifct_food_group`
4. `ifct_source_page`
5. `ifct_table_number`
6. `match_method`
7. `similarity_score`
8. `preparation_state`
9. `preparation_confidence`
10. `prep_state_compat`
11. `extracted_aliases`
12. `ambiguity_flags`
13. `species_verification`
14. `edible_part_verification`
15. `prep_compatibility_evidence`

---

## Calibration Readiness

| Item | Status |
|------|--------|
| Calibration set prepared | ✅ Complete |
| Calibration set verified | ✅ Complete |
| Workbench loads calibration units | ✅ Verified |
| Reviewers trained | ❌ NOT APPLICABLE (Pilot not authorized) |
| Consensus achieved | ❌ NOT APPLICABLE (Pilot not authorized) |

---

## Authorization Status

**CALIBRATION MATERIALS: ✅ READY**  
**PILOT REVIEW: ❌ NOT AUTHORIZED**

Per Stage 3.3.2 Final Gate Decision:
- Gate B (Implementation Authorization): ❌ NOT AUTHORIZED — 15 blockers unresolved
- Gate C (Pilot Acceptance): ❌ NOT MET — Prerequisites unmet
- "Prototype Testing - ❌ BLOCKED (requires Gate B)"
- "Pilot Review - ❌ BLOCKED (requires Gate C)"
- "No gate can be bypassed. Each gate requires explicit sign-off from designated authorities."

The calibration materials are prepared and verified for future use when pilot authorization is granted.

---

*End of Calibration Report*