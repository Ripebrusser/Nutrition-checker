# Stage 3.5.3: Protocol Package for Controlled 50-Unit Pilot

**Date:** 2026-11-18  
**Status:** Draft — Awaiting QA Lead and Project Lead Approval

---

## Overview

This document consolidates the five required protocols for Gate C authorization of the controlled 50-unit ingredient-matching pilot. Each protocol is derived from existing approved material (Stage 3.3.1, 3.3.2, 3.4, 3.5.1, 3.5.2) and adapted for the controlled pilot scope.

**Scope:** These protocols govern the 50-unit controlled pilot only. They do not authorize full-scale review.

**Authority:** QA Lead + Project Lead sign-off required before pilot execution.

---

## Protocol 1: Pilot Protocol — End-to-End Procedure

**Purpose:** Define the complete end-to-end pilot workflow, roles, timeline, and deliverables.

**Scope:** 50-unit controlled pilot using the Stage 3.5.2.2 workbench with enforced blind-review isolation.

### 1.1 Roles and Responsibilities

| Role | Count | Responsibility |
|------|-------|----------------|
| Primary Reviewer | 1 | Review all 50 units; record decision, rationale (≥50 chars), evidence references, confidence (1-5) |
| Quality Auditor | 1 | Blind review of 10 units (20% stratified sample); sees ONLY ingredient + candidates + evidence |
| Domain Expert 1 | 1 | Adjudication panel member; 48h SLA; binding resolution of disagreements |
| Domain Expert 2 | 1 | Adjudication panel member; 48h SLA; binding resolution of disagreements |

### 1.2 Timeline

| Phase | Duration | Activities |
|-------|----------|------------|
| Calibration | 0.5 days | Both primary + auditor complete 5-unit set independently; consensus required |
| Primary Review | 1-2 weeks | Primary reviewer completes all 50 units |
| Audit Sample Selection | 0.5 days | Random 20% (10 units), stratified, seed=42 |
| Auditor Blind Review | 1 week | Auditor completes 10 units blind |
| Agreement Analysis | 0.5 days | Raw agreement rate; disagreement categorization |
| Adjudication | 1-2 days | Panel resolves disagreements; 48h SLA per case |
| Reporting | 1 week | Produce all 5 pilot deliverables |

**Total estimated calendar time:** 2-3 weeks

### 1.3 Procedure Sequence

```
1. PRE-PILOT
   ├─ Verify 8 frozen input hashes
   ├─ Verify Stage 2.3 candidate data integrity
   ├─ Verify IFCT final candidate integrity
   ├─ Verify review schema version (v1.1)
   ├─ Verify reviewer workspace separation
   ├─ Confirm no prior pilot decisions exist
   └─ Confirm no unadjudicated mappings treated as accepted

2. CALIBRATION
   ├─ Primary completes 5-unit set independently
   ├─ Auditor completes 5-unit set independently
   ├─ Compare decisions; document discrepancies
   ├─ Resolve discrepancies; achieve consensus
   └─ Record calibration consensus

3. PRIMARY REVIEW
   ├─ Primary reviewer logs in (PRIMARY role)
   ├─ Reviews all 50 units in assigned order
   ├─ Records: decision, rationale (≥50 chars), evidence refs, confidence (1-5)
   └─ Submits each decision → state advances

4. AUDIT SAMPLE SELECTION
   ├─ Random 20% (10 units) from 50, stratified by stratum
   ├─ Seed = 42 (reproducible)
   └─ Assign to auditor

5. AUDITOR BLIND REVIEW
   ├─ Auditor logs in (AUDITOR role, blind mode enforced)
   ├─ Reviews assigned 10 units
   ├─ Sees ONLY: ingredient expression, IFCT candidates, evidence panel
   ├─ Does NOT see: primary decision, rationale, confidence, reviewer ID
   └─ Submits each decision → state advances

6. AGREEMENT ANALYSIS
   ├─ Calculate raw agreement rate on 10 units
   ├─ Categorize disagreements by type
   └─ Prepare disagreement log

7. ADJUDICATION
   ├─ Domain expert panel reviews each disagreement
   ├─ 48h SLA per case
   ├─ Binding resolution with written rationale
   └─ State → ADJUDICATED

8. REPORTING
   ├─ Pilot Results Report
   ├─ Disagreement Analysis
   ├─ Calibration Report
   ├─ Adjudication Log
   └─ Pilot Gate Recommendation (A/B/C)
```

### 1.4 Handling Special Cases

| Case | Procedure |
|------|-----------|
| Ambiguous ingredient (multiple plausible IFCT codes) | Primary marks AMBIGUOUS; auditor independently evaluates; if both AMBIGUOUS → adjudication |
| Unmatched ingredient (no IFCT candidates) | Primary marks NO_IFCT_EQUIVALENT or UNMATCHED; auditor verifies |
| Conflicting evidence | Primary marks CONFLICT with alternative IFCT code + detailed rationale; adjudication required |
| Auto-accepted units (3 units) | Primary manually verifies all 5 criteria; auditor included in sample if selected |
| NOT_SPECIFIED preparation | Never auto-accepted; requires explicit reviewer evidence |

### 1.5 Acceptance Criteria

- All 50 units reviewed by primary
- 10 units (20%) reviewed by auditor blind
- Calibration consensus achieved on all 5 units
- All disagreements adjudicated with written rationale
- All 5 pilot deliverables produced
- No unadjudicated mapping treated as accepted

---

## Protocol 2: Blind Audit Procedure

**Purpose:** Define how the auditor conducts blind review of the 10-unit sample without exposure to primary reviewer decisions.

**Scope:** Auditor workflow for the 10-unit stratified sample (20% of 50).

### 2.1 Preconditions

- Primary review of all 50 units complete
- Submission states for sampled units = PRIMARY_SUBMITTED
- Auditor has completed calibration with consensus
- Auditor has signed commitment and understands blind protocol

### 2.2 Auditor Workspace Access

1. Auditor logs in with assigned reviewer ID → AUDITOR role enforced
2. Workbench loads only auditor's decision file (`data/interim/phase3/decisions/auditor/`)
3. Primary decisions stored in separate file (`data/interim/phase3/decisions/primary/`) — not loaded
4. Blind mode automatically active (cannot be disabled in AUDITOR role)

### 2.3 Blind Review Constraints

| Auditor Sees | Auditor Does NOT See |
|--------------|---------------------|
| Original ingredient expression | Primary reviewer's decision |
| Normalized ingredient | Primary reviewer's rationale |
| Primary ingredient | Primary reviewer's confidence |
| Preparation state | Primary reviewer's ID |
| Parsed quantity/unit | Any dashboard metrics from primary |
| All IFCT candidate records | |
| Full nutrient profiles | |
| Match method, similarity, confidence | |
| Evidence panel (15 fields) | |

### 2.4 Audit Review Procedure

1. Navigate to assigned unit (Jump to unit #)
2. Review candidate comparison panel
3. Review evidence panel
4. Make independent decision:
   - Select mapping decision (ACCEPTED/REJECTED/AMBIGUOUS/UNMATCHED/NO_IFCT_EQUIVALENT/CONFLICT)
   - Enter rationale (≥50 chars)
   - Enter evidence references (15 mandatory for ACCEPTED)
   - Enter confidence (1-5)
   - Submit
5. System records decision in auditor's isolated parquet file
6. Submission state advances: PRIMARY_SUBMITTED → BOTH_SUBMITTED

### 2.5 Blind Status Indicator

When auditor views a unit where primary has already submitted:
> 🔒 **Blind Review Active**: The other reviewer has submitted their decision. Their decision and rationale are hidden from you.

### 2.6 Post-Audit

- Auditor decisions stored in `data/interim/phase3/decisions/auditor/review_decisions.parquet`
- History in `data/interim/phase3/decisions/auditor/review_decisions_history.parquet`
- Submission state advances to BOTH_SUBMITTED
- Adjudication becomes available for units with disagreements

### 2.7 Acceptance Criteria

- All 10 assigned units reviewed
- No primary decision/rationale/confidence visible at any point
- All decisions recorded with auditor_id, timestamp, rationale, evidence, confidence
- Submission states correctly advanced

---

## Protocol 3: Adjudication Protocol

**Purpose:** Define the disagreement resolution process for the controlled pilot.

**Scope:** All disagreements between primary and auditor on the 10-unit audit sample.

### 3.1 Trigger Conditions

Adjudication is triggered when, for any of the 10 audit sample units:
- Primary and auditor mapping decisions differ, OR
- Primary and auditor both mark AMBIGUOUS but with different candidate sets, OR
- Either reviewer marks CONFLICT, OR
- Evidence completeness differs materially

### 3.2 Adjudication Panel

| Member | Role | Authority |
|--------|------|-----------|
| Domain Expert 1 | Panel Chair | Binding resolution; 48h SLA |
| Domain Expert 2 | Panel Member | Binding resolution; 48h SLA |

**Quorum:** Both experts required. If one unavailable, designated alternate (pre-identified) steps in.

### 3.3 Adjudication Process

1. **Trigger:** System detects disagreement → state = READY_FOR_ADJUDICATION
2. **Notification:** Both experts notified (email/log)
3. **Review:** Experts independently review:
   - Original ingredient + candidates
   - Primary decision + rationale + evidence
   - Auditor decision + rationale + evidence
   - IFCT reference data
4. **Deliberation:** Experts confer (synchronous or asynchronous)
5. **Resolution:** Panel issues binding decision with:
   - Final mapping decision
   - Written rationale citing specific evidence
   - Any amendments to evidence requirements
6. **Recording:** Adjudication decision recorded in `data/interim/phase3/decisions/adjudication/`
7. **State Update:** Submission state → ADJUDICATED

### 3.4 Adjudication Decision Criteria

| Disagreement Type | Resolution Approach |
|-------------------|---------------------|
| Different IFCT code selected | Evaluate evidence for each code; select best-supported |
| ACCEPTED vs REJECTED | Apply 15-field evidence test; if primary lacks evidence → REJECTED |
| AMBIGUOUS vs definitive | If ≥2 equally plausible codes → AMBIGUOUS; else select best-supported |
| CONFLICT vs other | CONFLICT takes precedence; adjudication resolves conflict |
| Evidence completeness | ACCEPTED requires all 15 fields; missing → cannot be ACCEPTED |

### 3.5 SLA and Documentation

| Metric | Target |
|--------|--------|
| Time to first response | 24 hours |
| Time to resolution | 48 hours |
| Documentation | Written rationale per case, signed by both experts |

### 3.6 Acceptance Criteria

- All disagreements resolved within 48h SLA
- Each resolution has written rationale signed by both experts
- Final decisions recorded in adjudication history
- Submission state = ADJUDICATED for all adjudicated units

---

## Protocol 4: Evidence Checklist

**Purpose:** Define the 15 mandatory evidence fields for ACCEPTED decisions with definitions and examples.

**Scope:** All ACCEPTED decisions in the pilot (primary, auditor, adjudication).

### 4.1 The 15 Mandatory Evidence Fields

| # | Field | Definition | Example |
|---|-------|------------|---------|
| 1 | `ifct_food_code` | IFCT food code assigned | `G033` |
| 2 | `ifct_food_name` | Official IFCT food name | `Turmeric powder (Curcuma domestica)` |
| 3 | `ifct_food_group` | IFCT food group classification | `CONDIMENTS AND SPICES-DRY` |
| 4 | `ifct_source_page` | IFCT 2017 page number | `142` |
| 5 | `ifct_table_number` | IFCT table number | `Table 1` |
| 6 | `match_method` | Matching method used | `EXACT` |
| 7 | `similarity_score` | Similarity score (0.0-1.0) | `1.0` |
| 8 | `preparation_state` | Ingredient preparation state | `FRESH` |
| 9 | `preparation_confidence` | Confidence in prep state (0.0-1.0) | `0.95` |
| 10 | `prep_state_compat` | Prep state compatibility with IFCT raw basis | `0.9` |
| 11 | `extracted_aliases` | JSON array of extracted aliases | `["haldi", "turmeric"]` |
| 12 | `ambiguity_flags` | JSON array of ambiguity flags | `[]` |
| 13 | `species_verification` | Scientific name match confirmation | `Curcuma domestica` |
| 14 | `edible_part_verification` | Edible part match confirmation | `rhizome` |
| 15 | `prep_compatibility_evidence` | How prep state matches IFCT raw basis | `FRESH matches IFCT raw basis for spices` |

### 4.2 Validation Rules

- **ACCEPTED decisions:** All 15 fields MUST be present in `evidence_references`
- **Other decisions:** Rationale + at least 3 evidence references required
- **Empty placeholders NOT allowed:** Fields must have substantive content
- **Format:** Comma-separated list in evidence_references field

### 4.3 Examples

**ACCEPTED (Turmeric powder):**
```
ifct_food_code, ifct_food_name, ifct_food_group, ifct_source_page, ifct_table_number, match_method, similarity_score, preparation_state, preparation_confidence, prep_state_compat, extracted_aliases, ambiguity_flags, species_verification, edible_part_verification, prep_compatibility_evidence
```

**REJECTED (Coriander powder - NOT_SPECIFIED):**
```
match_method, similarity_score, preparation_state, species_verification
```

### 4.4 Acceptance Criteria

- All ACCEPTED decisions have 15/15 evidence fields
- No ACCEPTED decision accepted with missing fields
- Evidence checklist used during review and audit

---

## Protocol 5: Auto-Accept Verification Procedure

**Purpose:** Define the manual verification procedure for the 3 auto-accepted units to ensure they meet all 5 auto-accept criteria.

**Scope:** The 3 review units that were auto-accepted in Stage 2.3 candidate generation.

### 5.1 The 3 Auto-Accepted Units

| Review Unit | Primary Ingredient | IFCT Code | Match Method | Prep State | Similarity |
|-------------|-------------------|-----------|--------------|------------|------------|
| RU_004536 | lemon juice | E033 | EXACT | FRESH | 1.0 |
| RU_001643 | coriander leaves | G009 | EXACT | FRESH | 1.0 |
| RU_005709 | pineapple | E053 | EXACT | FRESH | 1.0 |

### 5.2 Auto-Accept Criteria (All 5 Required)

1. **Match method = EXACT** — Canonical name equality after normalization
2. **Preparation state = FRESH or RAW** — NOT_SPECIFIED excluded
3. **Similarity score = 1.0** — Exact match
4. **Single IFCT code per review unit** — No multi-code ambiguity
5. **Full evidence available** — All 15 mandatory fields satisfied

### 5.3 Verification Procedure

For each of the 3 units:

1. **Primary Reviewer** manually verifies all 5 criteria during review
2. **Records verification** in rationale: "Auto-accept verified: EXACT match, FRESH prep, sim=1.0, single IFCT code, 15-field evidence complete"
3. **Auditor** independently verifies if unit in audit sample
4. **Adjudication panel** resolves any dispute

### 5.4 Verification Checklist (Per Unit)

| Criterion | Check | Pass/Fail |
|-----------|-------|-----------|
| Match method = EXACT | ☐ | ☐ |
| Preparation state = FRESH/RAW | ☐ | ☐ |
| Similarity score = 1.0 | ☐ | ☐ |
| Single IFCT code | ☐ | ☐ |
| 15 evidence fields complete | ☐ | ☐ |

### 5.5 Acceptance Criteria

- All 3 auto-accepted units manually verified by primary reviewer
- If in audit sample, auditor independently verifies
- Any failure → unit reclassified as REVIEW_REQUIRED
- Verification recorded in decision rationale

---

## Protocol Cross-Reference

| Protocol | Related Blockers | Related Protocols |
|----------|------------------|-------------------|
| 1. Pilot Protocol | All | 2, 3, 4, 5 |
| 2. Blind Audit Procedure | BLK-017 | 1, 3 |
| 3. Adjudication Protocol | BLK-018 | 1, 2 |
| 4. Evidence Checklist | BLK-015 | 1, 2, 3, 5 |
| 5. Auto-Accept Verification | BLK-003, 008 | 1, 4 |

---

## Document Control

| Version | Date | Author | Status |
|---------|------|--------|--------|
| 1.0 | 2026-11-18 | QA Lead | Draft for Review |

**Approval Required:** QA Lead + Project Lead before pilot execution.

---

*End of Protocol Package*