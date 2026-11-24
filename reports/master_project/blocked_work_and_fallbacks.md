# Blocked Work and Fallbacks

**Date:** 2026-11-18  
**Project:** AI for Nutrition & Diet Planning

---

## Blocked Stage Analysis

### Stage 3.5.4: Controlled 50-Unit Pilot

| Field | Detail |
|-------|--------|
| **Stage** | 3.5.4 — Controlled 50-Unit Pilot |
| **Status** | ❌ **BLOCKED** |
| **Direct Blocker** | Gate C authorization not obtained |
| **Gate C Requirements** | 8 conditions; 4 met, 4 pending |
| **Pending Conditions** | 1. 4 written reviewer commitments<br>2. 5 protocol documents approved<br>3. Calibration consensus achieved<br>4. Pre-pilot hash verification |
| **Root Cause** | Governance commitments not secured; no actual reviewers identified |
| **Impacted Stages** | 3.5.5 (Pilot Evaluation), 3.6 (Nutrition Calculation), 3.7 (Aggregation), 3.8 (Validation), Phase 4, Phase 6.2+, Phase 7, Phase 8.3+ |

#### Attempts Made:
1. ✅ All 5 workbench safeguards implemented and tested (30/30 tests pass)
2. ✅ Blind-review isolation implemented (architectural, not convention)
3. ✅ 5 protocol documents drafted (`stage3_5_3_protocol_package.md`)
4. ✅ 4 reviewer commitment templates created (`stage3_5_3_reviewer_commitment_templates.md`)
5. ✅ Calibration consensus record template created (`stage3_5_3_calibration_consensus_record.md`)
5. ✅ 71-item pre-pilot integrity checklist created (`stage3_5_3_pre_pilot_integrity_checklist.md`)
6. ✅ Gate C authorization package prepared (`stage3_5_3_gate_c_authorization_package.md`)
7. ❌ No actual reviewers identified or commitments secured
7. ❌ No protocol documents formally approved
8. ❌ No calibration conducted (requires committed reviewers)
9. ❌ No hash verification executed

#### Why It Remains Blocked:
- Gate C requires **actual signed commitments** from 4 named individuals
- Requires **formal QA + Project Lead approval** of 5 protocols
- Requires **actual calibration consensus** between 2 reviewers
- Requires **formal QA execution** of 71-item integrity checklist
- **All are governance/actions, not technical defects**

#### Can Independent Work Continue?
**YES — The following are completely independent:**
- Phase 5 (ML Experiments) — all 8 stages
- Phase 6.1 (Application Architecture)
- Phase 8.1 (Literature Review)
- Phase 8.2 (Methodology drafting)
- Phase 3.6 preparatory design (interfaces, data models)

#### Alternative Approach (Fallback):
**If Gate C cannot be authorized within reasonable timeframe:**

| Fallback | Description | Trade-off |
|----------|-------------|-----------|
| **Subset Manual Mapping** | Manually verify 200–500 high-priority mappings using workbench | Smaller mapping set; no inter-reviewer agreement; no pilot evaluation metrics |
| **Synthetic Pilot** | Use workbench with simulated reviewer decisions for engine testing | No human validation; only tests engine logic |
| **Deferred Pilot** | Postpone pilot; proceed with nutrition engine using provisional mappings | Delays human validation; provisional mappings may have errors |
| **Single-Reviewer Mapping** | One expert maps 500–1000 units using workbench | No blind audit; no inter-reviewer agreement; higher bias risk |

**Recommended Fallback:** **Subset Manual Mapping (200–500 units)** by a single domain expert using the workbench. This provides:
- Validated mappings for nutrition engine (3.6)
- Real human decisions with evidence
- Workbench validation at scale
- Can be completed in 1–2 weeks by one expert

**Impact on Research Claims:**
- Cannot claim inter-reviewer agreement (no second reviewer)
- Cannot claim pilot evaluation metrics (no pilot)
- Can claim: "Workbench validated for decision recording; mappings verified by domain expert"
- Must clearly state: "No inter-reviewer reliability measured; mappings not independently audited"

---

### Stage 3.5.5: Pilot Evaluation

| Field | Detail |
|-------|--------|
| **Stage** | 3.5.5 — Pilot Evaluation |
| **Status** | ❌ BLOCKED |
| **Depends On** | Stage 3.5.4 completion |
| **Fallback** | Not applicable — evaluation requires pilot |

---

### Stage 3.6: Ingredient-Level Nutrition Calculation

| Field | Detail |
|-------|--------|
| **Stage** | 3.6 — Ingredient-Level Nutrition Calculation |
| **Status** | ⚠️ DEPENDS ON 3.5.5 (but can start with subset) |
| **Direct Dependency** | Requires validated ingredient→IFCT mappings |
| **Current Mappings Available** | 7,992 review units; 3 auto-accepted; ~1,900 high-priority (Critical+High+Medium) |
| **Fallback** | Use manually verified subset (200–500 mappings) |
| **Impact if Delayed** | Blocks 3.7, 3.8, Phase 4, Phase 6.2+ |

#### Can Start With Subset:
**YES** — Can begin implementation with:
- 3 auto-accepted units (verified)
- 200–500 manually verified high-priority mappings
- Provisional mappings for remaining (flagged as unverified)

**Design Work Can Start Now:**
- `src/nutrition/nutrient_calculator.py` interfaces
- Edible portion handling logic (`edible_portion.py` exists as stub)
- Recipe-level aggregation design
- Missing nutrient propagation logic
- Provenance tracking schema

---

### Stage 3.7: Recipe-Level Nutrition Aggregation

| Field | Detail |
|-------|--------|
| **Stage** | 3.7 — Recipe-Level Nutrition Aggregation |
| **Status** | ⚠️ DEPENDS ON 3.6 |
| **Fallback** | None — requires 3.6 output |

---

### Stage 3.8: Nutrition Engine Validation

| Field | Detail |
|-------|--------|
| **Stage** | 3.8 — Nutrition Engine Validation |
| **Status** | ⚠️ DEPENDS ON 3.7 |
| **Fallback** | None — requires 3.7 output |

---

### Phase 4: Personalization & Diet Planning

| Field | Detail |
|-------|--------|
| **Phase** | 4 — Personalization & Diet Planning |
| **Status** | ⚠️ DEPENDS ON 3.6+ |
| **Fallback** | Can design schemas and preference handling now; implementation requires 3.6 |

---

### Phase 6.2–6.5: Application UI/Backend

| Field | Detail |
|-------|--------|
| **Stages** | 6.2 UI, 6.3 Backend, 6.4 Integration, 6.5 Testing |
| **Status** | ⚠️ DEPENDS ON 3.6, 5.7 |
| **6.1 Architecture** | CAN START NOW |
| **Fallback** | Develop with mock nutrition data; integrate real engine later |

---

### Phase 7: System Integration

| Field | Detail |
|-------|--------|
| **Phase** | 7 — System Integration |
| **Status** | ⚠️ DEPENDS ON PHASES 3–6 |
| **Fallback** | None — final integration |

---

### Phase 8.3–8.7: Paper & Final Submission

| Field | Detail |
|-------|--------|
| **Stages** | 8.3 Results, 8.4 Paper, 8.5 Poster, 8.6 Presentation, 8.7 Repo |
| **Status** | ⚠️ DEPENDS ON PHASES 3–7 |
| **8.1 Literature Review** | CAN START NOW |
| **8.2 Methodology** | CAN START NOW (draft) |
| **Fallback** | Paper can reference subset mappings and provisional results if clearly labeled |

---

## Summary: Blocked Work Dependency Graph

```
BLOCKED (Gate C)
    │
    ├─→ 3.5.4 Pilot (BLOCKED)
    │     └─→ 3.5.5 Evaluation (BLOCKED)
    │           └─→ 3.6 Nutrition (DEPENDS) ──→ 3.7 Aggregation (DEPENDS) ──→ 3.8 Validation (DEPENDS)
    │                 └─→ Phase 4 (DEPENDS) ──→ 6.2+ UI (DEPENDS)
    │                       └─→ 7 Integration (DEPENDS) ──→ 8.3+ Paper (DEPENDS)
    │
    └─→ INDEPENDENT WORKSTREAMS (CAN START NOW):
          ├─→ Phase 5 ML (all 8 stages)
          ├─→ Phase 6.1 Architecture
          └─→ Phase 8.1 Literature Review, 8.2 Methodology (draft)
```

---

## Fallback Decision Matrix

| Scenario | Trigger | Action | Research Impact |
|----------|---------|--------|-----------------|
| **Gate C authorized within 2 weeks** | Commitments + protocols secured | Proceed with 50-unit pilot | Full pilot evaluation; inter-reviewer agreement; full claims |
| **Gate C delayed >2 weeks, reviewers available** | Commitments secured, protocols pending | Begin single-reviewer subset mapping (500 units) | No inter-reviewer agreement; validated mappings for engine |
| **Gate C delayed >2 weeks, no reviewers** | No commitments possible | Use auto-accepted (3) + high-confidence algorithmic mappings | No human validation for most; provisional engine only |
| **Gate C impossible** | Project constraints | Document as limitation; proceed with algorithmic mappings only | No human validation; algorithmic mappings only; clear limitations stated |

---

## Recommended Immediate Actions

1. **Project Lead:** Begin securing 4 commitments TODAY (parallel with other work)
2. **Technical Lead:** Begin Phase 5.1 (ML Problem Definition) and Phase 6.1 (App Architecture) IMMEDIATELY
3. **QA Lead:** Begin Phase 8.1 Literature Review IMMEDIATELY
4. **All Leads:** Weekly sync on Gate C progress; pivot to fallback if >2 weeks

---

## Acceptance Criteria for Fallback Activation

**Fallback Activated When:**
- [ ] Gate C not authorized by [TARGET DATE: 2026-12-02]
- [ ] Project Lead confirms commitments cannot be secured in reasonable time
- [ ] Technical Lead confirms nutrition engine design ready for subset mappings

**Fallback Deliverables:**
- [ ] Manually verified mapping subset (200–500 units) with evidence
- [ ] Nutrition engine implemented with subset + provisional flags
- [ ] Clear documentation of limitations in all reports
- [ ] Research paper explicitly states validation scope

---

*End of Blocked Work and Fallbacks*