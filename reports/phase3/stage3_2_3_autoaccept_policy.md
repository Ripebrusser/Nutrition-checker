# Stage 3.2.3: Auto-Accept Policy (Corrected)

**Date:** 2026-11-18  
**Status:** Authoritative — replaces all previous auto-accept specifications

---

## 1. Auto-Accept Policy (Corrected)

### 1.1 Mandatory Conditions for Auto-Acceptance

A candidate mapping is **automatically accepted** if and only if **ALL** of the following conditions are met:

| # | Condition | Rationale |
|---|-----------|-----------|
| 1 | Match method = **EXACT** | Canonical name equality after normalization |
| 2 | Preparation state = **FRESH** or **RAW** | IFCT Table 1 is raw-food basis; only FRESH/RAW are compatible without additional evidence |
| 3 | Similarity score = **1.0** | Exact token-set match after normalization |
| 4 | **Single** IFCT food code matched | No multi-code ambiguity |
| 5 | Evidence references complete | All 15 mandatory fields populated |

**Any failure → candidate requires manual review (REVIEW_REQUIRED).**

---

## 2. Explicit Prohibitions

### 2.1 NOT_SPECIFIED Preparation State

**NOT_SPECIFIED preparation state is NEVER eligible for auto-acceptance.**

- Rationale: NOT_SPECIFIED means preparation information is missing, not that the ingredient is raw
- Stage 2.3 gate: NOT_SPECIFIED requires explicit evidence (explicit reviewer confirmation)
- Auto-accept gate: preparation_state must be FRESH or RAW

### 2.2 Other Prohibited Auto-Accept Scenarios

| Scenario | Reason |
|----------|--------|
| SYNONYM match (any confidence) | Requires reviewer verification of synonym validity |
| TOKEN_EQUIVALENT (Jaccard = 1.0) | Token equivalence ≠ canonical identity; preparation/edible part may differ |
| TOKEN_SIMILARITY (any score) | Insufficient for identity confirmation |
| FUZZY match | Insufficient for identity confirmation |
| Multiple IFCT codes matched | Ambiguity requires human resolution |
| Evidence references incomplete | All 15 mandatory fields required for ACCEPTED |

---

## 3. Auto-Accept Record (Authoritative)

### 3.1 Stage 2.3 Auto-Accepted Candidates (Frozen)

| Recipe ID | Primary Ingredient | IFCT Code | Match Method | Prep State | Similarity |
|-----------|-------------------|-----------|--------------|------------|------------|
| 866 | lemon juice | E033 | EXACT | FRESH | 1.0 |
| 2457 | coriander leaves | G009 | EXACT | FRESH | 1.0 |
| 3063 | pineapple | E053 | EXACT | FRESH | 1.0 |
| 10544 | coriander leaves | G009 | EXACT | FRESH | 1.0 |

### 3.2 Reconciliation

| Metric | Count |
|--------|-------|
| Total auto-accepted candidates | 4 |
| Unique (primary, IFCT) pairs | 3 |
| Unique (primary, prep, IFCT) triples | 3 |
| Auto-accepted review units (flawed key) | 3 |
| Auto-accepted review units (corrected key) | **3** (not 6) |
| Methods | EXACT: 4 |
| Prep states | FRESH: 4 |
| NOT_SPECIFIED auto-accepted | **0** |

> **Correction:** Previous reports claimed 6 auto-accepted review units with corrected key. Actual count is **3** (same as flawed key). The "6" claim arose from counting the same ingredient-IFCT pair across multiple preparation states (FRESH + NOT_SPECIFIED), but the NOT_SPECIFIED variants were **not auto-accepted** — they were artifacts of the corrected key splitting.

---

## 4. Revised Auto-Accept Gate Logic

### 4.1 Pseudocode

```python
def evaluate_auto_accept(candidate, disambiguated, ifct_ref):
    """
    Returns (auto_accept: bool, reason: str, evidence: dict)
    """
    # 1. Match method must be EXACT
    if candidate.match_method != 'EXACT':
        return False, 'MATCH_METHOD_NOT_EXACT', {}
    
    # 2. Preparation state must be FRESH or RAW
    prep_state = disambiguated.get_preparation_state(candidate)
    if prep_state not in {'FRESH', 'RAW'}:
        return False, f'PREP_STATE_NOT_RAW_OR_FRESH ({prep_state})', {}
    
    # 3. Similarity must be exactly 1.0
    if candidate.similarity_score != 1.0:
        return False, 'SIMILARITY_NOT_EXACT', {}
    
    # 4. Single IFCT code matched
    matched_codes = get_matched_ifct_codes(candidate)
    if len(matched_codes) != 1:
        return False, 'MULTIPLE_IFCT_CODES', {}
    
    # 5. Evidence completeness
    evidence = build_evidence(candidate, disambiguated, ifct_ref)
    if not evidence_complete(evidence):
        return False, 'EVIDENCE_INCOMPLETE', evidence
    
    # All checks passed
    return True, 'AUTO_ACCEPT', evidence
```

### 4.2 Evidence Completeness Check

```python
def evidence_complete(evidence):
    required = [
        'ifct_food_code', 'ifct_food_name', 'ifct_food_group',
        'ifct_source_page', 'ifct_table_number',
        'match_method', 'similarity_score',
        'preparation_state', 'preparation_confidence',
        'prep_state_compat', 'extracted_aliases',
        'ambiguity_flags', 'ifct_source_page',
        'ifct_table_number', 'species_verification',
        'edible_part_verification', 'prep_compatibility_evidence'
    ]
    return all(field in evidence and evidence[field] for field in required)
```

---

## 4. Evidence Requirements for ACCEPTED

Every ACCEPTED decision must include **all 15 mandatory evidence fields**:

| # | Field | Description |
|---|-------|-------------|
| 1 | `ifct_food_code` | IFCT code (e.g., G009) |
| 2 | `ifct_food_name` | Official IFCT food name |
| 3 | `ifct_food_group` | IFCT food group |
| 4 | `ifct_source_page` | IFCT 2017 page number |
| 5 | `ifct_table_number` | IFCT table number |
| 6 | `match_method` | EXACT/SYNONYM/etc |
| 6 | `similarity_score` | 0.0–1.0 |
| 7 | `preparation_state` | RAW/FRESH/DRIED/etc |
| 8 | `preparation_confidence` | 0.0–1.0 |
| 9 | `prep_state_compat` | 0.0/0.5/1.0 |
| 10 | `extracted_aliases` | JSON array |
| 11 | `ambiguity_flags` | JSON array |
| 12 | `ifct_source_page` | Page reference |
| 13 | `ifct_table_number` | Table reference |
| 14 | `species_verification` | Scientific name match |
| 15 | `edible_part_verification` | Edible part match |
| 16 | `prep_compatibility_evidence` | How prep state matches IFCT basis |

**All 16 fields mandatory for ACCEPTED.** Missing any → REVIEW_REQUIRED.

---

## 5. NOT_SPECIFIED Handling

### 5.1 Policy

| Preparation State | Auto-Accept Eligible? | Requires |
|-------------------|----------------------|----------|
| FRESH | ✅ Yes | — |
| RAW | ✅ Yes | — |
| NOT_SPECIFIED | ❌ **Never** | Explicit reviewer evidence |
| DRIED/POWDERED/GROUND | ❌ No | Evidence + prep compatibility check |
| ROASTED/FRIED/BOILED/COOKED | ❌ No | Evidence + nutrient adjustment |
| SOAKED/SPROUTED/FERMENTED/PICKLED | ❌ No | Evidence + nutrient adjustment |

### 4.2 NOT_SPECIFIED Review Path

1. Reviewer must explicitly confirm: "This ingredient is used raw/fresh in this recipe"
2. Record evidence: `prep_state_evidence: "recipe_context_implies_raw"`
3. Update preparation_state to FRESH or RAW
3. Re-evaluate auto-accept gate

---

## 6. Auto-Accept Audit Trail

Every auto-accept decision must log:

```json
{
  "auto_accept": true,
  "reason": "EXACT_MATCH_FRESH_RAW",
  "evidence": {
    "match_method": "EXACT",
    "similarity_score": 1.0,
    "preparation_state": "FRESH",
    "ifct_food_code": "G009",
    "ifct_food_name": "Coriander leaves (Coriandrum sativum)",
    "ifct_source_page": "142",
    "ifct_table_number": "Table 1",
    "species_verification": "Coriandrum sativum",
    "edible_part_verification": "leaves",
    "prep_compatibility_evidence": "FRESH matches IFCT raw basis"
  }
}
```

---

## 7. Prohibited Auto-Accept Scenarios

| Scenario | Action |
|----------|--------|
| Match method ≠ EXACT | → REVIEW_REQUIRED |
| Preparation state ≠ FRESH/RAW | → REVIEW_REQUIRED |
| Similarity < 1.0 | → REVIEW_REQUIRED |
| Multiple IFCT codes matched | → AMBIGUOUS |
| Evidence incomplete | → REVIEW_REQUIRED |
| NOT_SPECIFIED preparation | → REVIEW_REQUIRED |
| DRIED/POWDERED/ROASTED/FRIED/BOILED/COOKED/GROUND/PICKLED/FERMENTED/SPROUTED | → REVIEW_REQUIRED |

---

## 7. Audit Trail

Every auto-accept decision logs:

```json
{
  "auto_accept": true,
  "reason": "EXACT_MATCH_FRESH_RAW",
  "evidence": {
    "ifct_food_code": "G009",
    "ifct_food_name": "Coriander leaves (Coriandrum sativum)",
    "ifct_source_page": "142",
    "ifct_table_number": "Table 1",
    "species_verification": "Coriandrum sativum",
    "edible_part_verification": "leaves",
    "prep_compatibility_evidence": "FRESH matches IFCT raw basis"
  },
  "reviewer_id": "auto_gate",
  "timestamp": "2026-11-18T...",
  "decision_id": "uuid"
}
```

---

## 8. Summary of Changes from Previous Policy

| Aspect | Previous | **Corrected** |
|--------|----------|---------------|
| NOT_SPECIFIED auto-accept | Allowed | **Prohibited** |
| Auto-accept count (corrected key) | 6 units | **3 units** |
| Evidence requirements | 50-char rationale | **15 mandatory fields** |
| NOT_SPECIFIED handling | Auto-accepted | **Prohibited** |
| FRESH auto-accept | Allowed | **Allowed (with evidence)** |
| RAW auto-accept | Not addressed | **Allowed** |

---

## 9. Enforcement

- **Stage 2.3 gate:** Enforces NOT_SPECIFIED exclusion at candidate generation
- **Stage 3 review:** Validates all 16 evidence fields for ACCEPTED
- **Audit sampling:** 100% of auto-accepted units audited
- **Regression test:** 4 auto-accepted candidates must remain stable

---

*End of Auto-Accept Policy (Corrected)*