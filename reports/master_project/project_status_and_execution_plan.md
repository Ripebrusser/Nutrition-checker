# Master Project Status and Execution Plan

**Date:** 2026-11-18  
**Project:** AI for Nutrition & Diet Planning: Personalized Indian Meal Recommendations Using Health Metrics and Ingredient-Level Nutrition Analysis

---

## Current Overall Project Status

| Phase | Name | Overall Status | Completion |
|-------|------|----------------|------------|
| **Phase 1** | Dataset Acquisition & Validation | ✅ **COMPLETE** | 100% |
| **Phase 2** | Ingredient Preprocessing | ✅ **COMPLETE** (with documented limitations) | 100% |
| **Phase 3** | IFCT Matching & Nutrition Engine | **IN PROGRESS** | ~85% |
| **Phase 4** | Personalization & Diet Planning | **NOT STARTED** | 0% |
| **Phase 5** | ML Experiments | **NOT STARTED** (can start in parallel) | 0% |
| **Phase 6** | Application Development | **NOT STARTED** (architecture can start) | 0% |
| **Phase 7** | System Integration & Validation | **NOT STARTED** | 0% |
| **Phase 8** | Research Paper & Final Submission | **NOT STARTED** (literature review can start) | 0% |

---

## Completed Phases and Stages

### Phase 1: Dataset Acquisition & Validation ✅ COMPLETE
- Indian recipe dataset acquired and validated
- IFCT 2017 acquired, decrypted, and extracted
- INDB 2024.11 acquired and validated
- USDA and NHANES datasets acquired
- Data cleaning, preprocessing, and validation complete
- Dataset validation reports generated
- Data provenance and SHA-256 hash verification complete
- All frozen datasets preserved with verified hashes

**Key Deliverables:**
- `data/raw/nutrition/IFCT_2017/IFCT2017.pdf` (hash verified)
- `data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf`
- `data/processed/recipes.parquet` (cleaned recipe dataset)
- `data/processed/indb_foods.parquet` (cleaned INDB dataset)
- `data/interim/ifct_final_candidate/ifct_table1_candidate.parquet` (528 IFCT foods)
- Validation reports in `reports/phase1/` and `docs/dataset_documentation/`

---

### Phase 2: Ingredient Preprocessing ✅ COMPLETE (with documented limitations)

**Completed Stages:**
- Stage 2.1: Ingredient normalization (synonym dictionary, canonical forms)
- Stage 2.2: Quantity and unit parsing (household measurements, gram weights)
- Stage 2.3: Source reconciliation and validation

**Known Limitations (Documented):**
- Some ingredient synonyms may be incomplete for regional variations
- Household measurement conversions have inherent approximation
- Some recipe ingredients remain unparsed (logged in `recipes_missing_ingredients.csv`)

**Key Deliverables:**
- `data/interim/phase2/normalized_ingredients.parquet` (hash: `08710983213938c3fecafd20991ab7d3d7fe51b179303bbe4dc93b2ac1b1b6e5`)
- `data/interim/phase2/parsed_recipe_ingredients.parquet` (hash: `e17b668b208dac4a7240cbfb27d78caac6123bc2b29b34a70aeb38964b9e86d9`)
- `data/interim/phase2/ingredient_synonyms.csv` (hash: `22b8aace1ef29ea271051004a0e5a79ac8a8bfb5d80b8f796abe0db1f2ee4b31`)
- `data/interim/phase2/household_measurements.csv` (hash: `451fb9c6d5135e0684bd5e6445aeaadfafa2951db6ae7fd939b96faad1e16b47`)
- Test suites: `tests/phase2/test_normalization.py` (14 tests), `tests/phase2/test_quantity_parser.py` (27 tests) — all passing

---

### Phase 3: IFCT Matching & Nutrition Engine — IN PROGRESS (~85%)

#### Completed Stages:

| Stage | Name | Status | Key Deliverables |
|-------|------|--------|------------------|
| 3.1 | Matching Architecture & Taxonomy | ✅ COMPLETE | `reports/phase3/stage3_1_matching_architecture.md`, `stage3_1_matching_taxonomy.md` |
| 3.2 | Candidate Generation | ✅ COMPLETE | `stage2_candidate_generation_report.md`, `ifct_match_candidates.parquet` (119,474 candidates) |
| 3.2.1 | Matching Correction | ✅ COMPLETE | `stage2_1_correction_report.md` |
| 3.2.2 | Ingredient Disambiguation & Prep States | ✅ COMPLETE | `stage2_2_name_disambiguation_report.md`, `stage2_2_preparation_state_report.md` |
| 3.2.3 | Matching Safety Corrections | ✅ COMPLETE | `stage3_2_3_remediation_report.md`, corrected review unit key (7,992 units) |
| 3.3 | Human Review Design & Approval | ✅ COMPLETE | `stage3_3_2_final_gate_decision.md` (Gate A: APPROVED), schema v1.1 approved |
| 3.4 | Review Workbench Prototype | ✅ COMPLETE | `app/ingredient_review_app.py`, `stage3_4_1_prototype_acceptance_report.md` (A — ACCEPTED) |
| 3.5 | Pilot Preparation & Governance | ✅ COMPLETE | Stage 3.5.1–3.5.3 complete |
| 3.5.1 | Blocker Rationalization | ✅ COMPLETE | `stage3_5_1_blocker_rationalization.md` |
| 3.5.2 | Safeguard Implementation | ✅ COMPLETE | `stage3_5_2_safeguard_implementation.md` |
| 3.5.2.1 | Test & Blind-Review Audit | ✅ COMPLETE | `stage3_5_2_1_blind_review_integrity_report.md` |
| 3.5.2.2 | Blind-Review Isolation | ✅ COMPLETE | `stage3_5_2_2_blind_review_implementation.md` |
| 3.5.3 | Governance Preparation | ✅ COMPLETE | All 5 protocol docs, commitment templates, calibration consensus record, pre-pilot checklist, Gate C package |

#### Phase 3 Test Status:
- **Phase 3 Application Tests:** 30/30 PASS
- **Full Regression Suite:** 149/156 PASS (7 pre-existing IFCT extraction failures unrelated to Phase 3.5)
- All frozen input hashes verified (8/8)

#### Key Phase 3 Data Artifacts:
- `data/interim/phase3/stage2_3/ifct_match_candidates.parquet` — 119,474 candidates, 7,992 unique review units (corrected key)
- `data/interim/phase3/stage2_3/unmatched_ingredients.parquet` — 63,244 unmatched
- `data/interim/ifct_final_candidate/ifct_table1_candidate.parquet` — 528 IFCT foods with 18 food groups
- Schema v1.1: Separate `MappingDecision` (6 values) and `WorkflowStatus` (5 values) enums

---

## Incomplete Stages

### Phase 3 Remaining:

| Stage | Name | Status | Blocker |
|-------|------|--------|---------|
| **3.5.4** | Controlled 50-Unit Pilot | **BLOCKED** | Gate C requires 4 signed commitments, 5 protocol approvals, calibration consensus, hash verification |
| **3.5.5** | Pilot Evaluation | **NOT STARTED** | Depends on 3.5.4 |
| **3.6** | Ingredient-Level Nutrition Calculation | **NOT STARTED** | Depends on pilot mappings (can start with subset) |
| **3.7** | Recipe-Level Nutrition Aggregation | **NOT STARTED** | Depends on 3.6 |
| **3.8** | Nutrition Engine Validation | **NOT STARTED** | Depends on 3.7 |

### Phase 4: Personalization & Diet Planning — NOT STARTED
All stages (4.1–4.6) pending nutrition engine (3.6–3.8)

### Phase 5: ML Experiments — NOT STARTED (CAN START IN PARALLEL)
Can begin with existing recipe/ingredient data; nutrition targets can use provisional estimates

### Phase 6: Application Development — NOT STARTED (ARCHITECTURE CAN START)
- 6.1 Architecture — can start now
- 6.2–6.5 depend on nutrition engine and ML models

### Phase 7: System Integration — NOT STARTED
Depends on Phases 3–6 completion

### Phase 8: Research Paper & Final Submission — NOT STARTED (LITERATURE REVIEW CAN START)
- 8.1 Literature Review — can start now
- 8.2–8.7 depend on earlier phases

---

## Existing Deliverables Summary

### Reports (100+ files in `reports/`)
- **Phase 1:** Validation reports, reconciliation, data dictionaries
- **Phase 2:** Normalization validation, quantity parsing, acceptance checklists, independent audits
- **Phase 3:** 60+ reports covering architecture, candidate generation, corrections, governance, workbench, pilot preparation

### Source Code (`src/`)
- `src/data/` — IFCT extraction, validation scripts
- `src/ingredients/` — Normalization, parsing
- `src/matching/` — Candidate generation, acceptance gate, taxonomy, disambiguation, pipeline
- `src/nutrition/` — Edible portion, nutrient calculator (stubs), validation
- `src/preprocessing/` — Recipe/INDB preprocessing
- `src/review/` — Persistence layer for workbench

### Application (`app/`)
- `ingredient_review_app.py` — Streamlit workbench with enforced blind-review isolation (Stage 3.5.2.2)

### Tests (`tests/`)
- Phase 1: 44 tests (all passing)
- Phase 2 Normalization: 14 tests (all passing)
- Phase 2 Quantity: 27 tests (all passing, 22 in test_quantity_parser.py)
- Phase 3 Application: 30 tests (all passing)
- IFCT Extraction: 46 tests (39 passing, 7 pre-existing failures in raw extraction CSV)

### Frozen Datasets (Hash Verified)
| File | SHA-256 |
|------|---------|
| `normalized_ingredients.parquet` | `08710983213938c3fecafd20991ab7d3d7fe51b179303bbe4dc93b2ac1b1b6e5` |
| `parsed_recipe_ingredients.parquet` | `e17b668b208dac4a7240cbfb27d78caac6123bc2b29b34a70aeb38964b9e86d9` |
| `ingredient_synonyms.csv` | `22b8aace1ef29ea271051004a0e5a79ac8a8bfb5d80b8f796abe0db1f2ee4b31` |
| `household_measurements.csv` (Phase 2) | `451fb9c6d5135e0684bd5e6445aeaadfafa2951db6ae7fd939b96faad1e16b47` |
| `ifct_table1_candidate.parquet` | `294c6fc4d095a47e13fbe02e8e3c1c0c8175752966275a3415f9a7df04774f35` |
| `ifct_match_candidates.parquet` | `2bb9f0d7770f7669ad3cd30f49d2a15f820f572e53690678f58891229336740f` |
| `unmatched_ingredients.parquet` | `4d4e2b84e3b3323552c600bf90eefba81c5e44ee8f455298f331c190ced08102` |
| `household_measurements.csv` (Stage 2.3) | `4c169cba077c49f384e699129e9051929ad130dda2221ac2692cf9c34e04567e` |

---

## Known Defects and Limitations

### Documented and Accepted:
1. **7 IFCT extraction test failures** — Pre-existing issues in raw extraction CSV (`data/interim/ifct_extracted/table1_parsed.csv`); final candidate parquet is complete and used by application
2. **Phase 2 household measurements** — Approximate conversions documented
3. **Unmatched ingredients** — 63,244 ingredients without IFCT candidates (logged, not a defect)
4. **Corrected review unit key** — 7,992 units vs flawed 7,165; documented in Stage 3.2.3

### Not Defects (By Design):
- No inter-rater reliability claims for pilot (Option C model: Primary + Auditor, no κ)
- Pilot scope limited to 50 units (not full 7,992)
- No nutrition calculations until Stage 3.6
- No ML models until Phase 5

---

## Dependencies Between Stages

```
Phase 1 (Complete)
    ↓
Phase 2 (Complete)
    ↓
Phase 3.1–3.5.3 (Complete)
    ↓
Phase 3.5.4 (Pilot) ──BLOCKED (Gate C)──→ 3.5.5 (Evaluation)
    ↓ (when authorized)
3.6 Nutrition Calculation → 3.7 Aggregation → 3.8 Validation
    ↓
Phase 4 (Personalization) ← requires 3.6+
Phase 5 (ML) ← CAN START NOW (independent)
Phase 6 (App) ← Architecture can start; UI needs 3.6+, ML needs 5+
Phase 7 (Integration) ← requires 3–6
Phase 8 (Paper) ← Literature review can start; rest needs 3–7
```

---

## Independent Tasks That Can Run in Parallel (Workstreams)

### Workstream A: Data & Nutrition (Sequential within, but Phase 3.6 can use pilot subset)
- Phase 3.5.4 → 3.5.5 → 3.6 → 3.7 → 3.8 (sequential, blocked on Gate C)
- Can begin 3.6 with a smaller manually verified mapping subset if pilot delayed

### Workstream B: Machine Learning (CAN START NOW)
- Phase 5.1–5.8: ML experiments using existing recipe/ingredient data
- Can use provisional nutrition estimates; refine when 3.6 completes
- Independent of Phase 3.5 pilot

### Workstream C: Application & Research (PARTIAL PARALLEL)
- **Phase 6.1 Architecture** — CAN START NOW
- **Phase 6.2–6.5 UI/Backend** — need nutrition engine (3.6) and ML models (5+)
- **Phase 8.1 Literature Review** — CAN START NOW
- **Phase 8.2 Methodology** — can draft now, finalize after 3–6

---

## Immediate Execution Priorities

### Priority 1: Unblock Gate C (Governance)
- **Action:** Project Lead secures 4 written commitments (Primary, Auditor, 2 Domain Experts)
- **Action:** QA Lead + Project Lead approve 5 protocol documents
- **Action:** Primary + Auditor complete calibration; achieve consensus
- **Action:** QA Lead executes 71-item pre-pilot integrity checklist
- **Action:** QA Lead + Project Lead sign Gate C authorization

### Priority 2: Start Independent Workstreams (CAN BEGIN IMMEDIATELY)
1. **Phase 5.1 ML Problem Definition** — Define ML tasks using existing recipe/ingredient data
2. **Phase 5.2 Feature Engineering** — Recipe features, ingredient features, user features
3. **Phase 6.1 Application Architecture** — Design frontend/backend/API/model integration
4. **Phase 8.1 Literature Review** — Systematic review of Indian food composition, nutrition recommendation, personalized diet planning

### Priority 3: Prepare for Nutrition Engine (Parallel Prep)
- Design `src/nutrient_calculator.py` interfaces
- Define edible portion handling logic
- Plan recipe-level aggregation
- Can use pilot mapping subset or manual verified subset if pilot delayed

---

## Single Best Next Task

**Start Phase 5.1 (ML Problem Definition) and Phase 6.1 (Application Architecture) in parallel** — these are completely independent of the Gate C authorization and can begin immediately with existing data.

**Simultaneously:** Project Lead should begin securing the 4 reviewer commitments for Gate C.

---

## Master Execution Tracker and Blocked Work Documents

Created alongside this document:
- `reports/master_project/master_execution_tracker.md` — Detailed stage-by-stage tracker
- `reports/master_project/blocked_work_and_fallbacks.md` — Blocked work analysis with fallbacks

---

*End of Project Status and Execution Plan*