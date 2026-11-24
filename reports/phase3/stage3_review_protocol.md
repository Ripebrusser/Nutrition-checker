# Stage 3: Manual Verification Review Protocol

## Purpose

Standardized procedure for reviewers to evaluate candidate ingredient → IFCT food code mappings.

**Mandatory:** Every reviewer must follow this protocol exactly. Deviations invalidate the review.

---

## 1. Reviewer Onboarding

### Prerequisites
- Access to Stage 3 review workbench
- Completed calibration exercise (5 test units)
- Signed protocol acknowledgment

### Calibration Exercise
Review 5 pre-selected units with known correct decisions:
1. EXACT + FRESH → ACCEPTED
2. EXACT + POWDERED → REJECTED (prep mismatch)
3. SYNONYM (confidence 0.99) + matching prep → ACCEPTED
4. TOKEN_EQUIVALENT → REVIEW_REQUIRED
4. Multi-code ambiguity → AMBIGUOUS

Must achieve 100% on calibration before reviewing production units.

---

## 2. Review Session Protocol

### Session Setup
1. Log into workbench
2. Request batch (max 50 units)
3. Verify session lock acquired
4. Confirm evidence panel loads correctly

### Per-Unit Review Steps (Mandatory Order)

#### Step 1: Evidence Panel Review (Minimum 60 seconds)
- [ ] Read source ingredient (original, normalized, primary)
- [ ] Read parenthetical text & extracted aliases
- [ ] Read preparation state & confidence
- [ ] Read IFCT food name, group, full nutrient profile
- [ ] Review all candidate ranks for this ingredient
- [ ] Read sample recipe lines (5 lines minimum)
- [ ] Read Stage 2.3 acceptance evidence
- [ ] Check multi-code ambiguity warning

**Do not proceed until all items checked.**

#### Step 2: Identity Verification
Compare **source ingredient identity** with **IFCT food identity**:

| Check | Question | Evidence |
|-------|----------|----------|
| Core identity | Do the core food items match? (e.g., "cumin seeds" vs "Cumin seeds") | Primary ingredient vs IFCT food name |
| Species | Same biological species? (e.g., Cuminum cyminum) | Scientific name in IFCT name |
| Variety | Same cultivar? (e.g., basmati vs sona masuri) | Variety keywords in both |
| Edible part | Same edible portion? (bulb, leaf, seed, fruit) | Edible part keywords / IFCT group |
| Preparation | Compatible prep states? | Prep state vs IFCT basis (raw) |

**If any core identity check fails → REJECTED.**

#### Step 3: Preparation-State Compatibility
| Source Prep | IFCT Basis | Action |
|-------------|------------|--------|
| RAW / FRESH | Raw | ✅ Compatible |
| NOT_SPECIFIED | Raw | ⚠️ Requires explicit evidence |
| DRIED / POWDERED / GROUND | Raw | ❌ Incompatible (nutrient concentration) |
| ROASTED / FRIED / BOILED / COOKED | Raw | ❌ Incompatible (nutrient loss/change) |
| FERMENTED / PICKLED | Raw | ❌ Incompatible (new compounds) |
| SPROUTED | Raw | ❌ Incompatible (nutrient change) |
| SOAKED | Raw | ⚠️ Reverts toward raw — needs evidence |

**If incompatible and no compensating evidence → REJECTED or REVIEW_REQUIRED.**

#### Step 4: Evidence Evaluation
Rate each evidence dimension (1-5):

| Dimension | 5 (Strong) | 3 (Moderate) | 1 (Weak) |
|-----------|------------|--------------|----------|
| Name match | EXACT canonical | SYNONYM (conf≥0.95) | TOKEN_SIMILARITY (<0.7) |
| Species match | Scientific name matches | Genus matches | Different genus |
| Prep compatibility | RAW/FRESH + raw IFCT | NOT_SPECIFIED + evidence | Incompatible prep |
| Alias support | HINDI_NAME / verified synonym | Explanatory alias | Unclassified |
| Food group | Same group | Related group | Different group |

**Composite evidence score < 3 → REVIEW_REQUIRED minimum.**

#### Step 5: Multi-Code Ambiguity Check
If ingredient maps to multiple IFCT codes:
- [ ] Can any be eliminated by evidence?
- [ ] Is one clearly better supported?
- [ ] Do remaining codes represent meaningfully different foods?

If >1 code remains plausible → **AMBIGUOUS** (do not pick one).

#### Step 6: Decision & Rationale

**Decision Matrix:**

| Status | When to Use | Required Evidence |
|--------|-------------|-------------------|
| **ACCEPTED** | Identity + prep + species all confirmed; evidence score ≥4 | Explicit rationale citing specific evidence fields |
| **REVIEW_REQUIRED** | Plausible but gap in one dimension; evidence score 3 | What specific gap remains |
| **REJECTED** | Core identity mismatch OR prep incompatible without evidence | Which check failed |
| **UNMATCHED** | No candidate survives scrutiny | Why all candidates failed |
| **AMBIGUOUS** | >1 IFCT code equally plausible after full review | Which codes and why indistinguishable |

**Rationale Requirements:**
- Minimum 50 characters
- Must cite specific evidence fields (e.g., "preparation_state=FRESH matches IFCT raw basis; match_method=EXACT confirms identity")
- No vague statements ("looks good", "seems right")
- If REJECTED/AMBIGUOUS: must explain why other statuses don't apply

#### Step 7: Confidence Rating (1-5)
| Rating | Meaning |
|--------|---------|
| 5 | Certain — would stake professional reputation |
| 4 | Confident — minor uncertainty only |
| 3 | Moderate — one dimension uncertain |
| 2 | Low — multiple gaps |
| 1 | Guess — insufficient evidence |

**Confidence < 3 → Status cannot be ACCEPTED.**

#### Step 8: Submit & Next
- Click "Submit Decision"
- Verify lock released
- Next unit auto-loads

---

## 3. Special Cases

### Multi-Code Ambiguity
**Protocol:**
1. List all candidate IFCT codes
2. Apply evidence evaluation to each
3. Eliminate codes with clear evidence against
4. If ≥2 remain equally plausible → **AMBIGUOUS**
5. Do NOT pick "best" — flag for domain expert

**Example:** "red chilli" → 7 IFCT codes (green-1 through green-7, red)
- All are Capsicum annuum, different varieties
- No recipe evidence distinguishes variety
- → **AMBIGUOUS**

### Unmatched Ingredients
**Protocol:**
1. Review all candidate rejections
2. Check if any candidate was incorrectly rejected
3. If all correctly rejected → **UNMATCHED**
4. Note: "No IFCT equivalent found" with reason (e.g., "quinoa not in IFCT 2017")

### Conflicting Evidence
**Protocol:**
1. Document all conflicting evidence
2. Weight by reliability (EXACT > SYNONYM > TOKEN_EQUIVALENT > TOKEN_SIMILARITY)
3. If conflict unresolved → REVIEW_REQUIRED
4. Document why conflict unresolved

### Recipe Context Contradiction
**Same ingredient, different recipes, different prep states:**
- Each recipe occurrence reviewed in context
- Same ingredient can map to different IFCT codes if prep differs
- Document each mapping separately

---

## 4. Reviewer Conduct Rules

### Must Do
- [ ] Complete calibration before first session
- [ ] Follow step order exactly
- [ ] Spend ≥60 seconds on evidence panel
- [ ] Write rationale ≥50 chars
- [ ] Rate confidence honestly
- [ ] Report technical issues immediately

### Must Not Do
- [ ] Skip evidence panel steps
- [ ] Decide based on similarity score alone
- [ ] Force a choice in AMBIGUOUS cases
- [ ] Copy-paste rationales
- [ ] Review while distracted
- [ ] Exceed 4-hour session without break

### Break Requirements
- Mandatory 10-min break every 60 minutes
- Maximum 4 hours continuous reviewing
- Mandatory 30-min break after 4 hours

---

## 5. Escalation Paths

| Situation | Escalate To | Timeline |
|-----------|-------------|----------|
| Technical issue | Platform admin | Immediate |
| Unclear protocol | Protocol owner | Same session |
| Ethical concern | Project lead | Same day |
| Reviewer fatigue | Session manager | Immediate |
| Disagreement with protocol | Protocol owner | Before next session |

---

## 5. Session Closeout

### End of Session
1. Release all locks
2. Confirm all decisions saved
- [ ] No pending drafts
- [ ] All locks released
3. Log session duration & units reviewed

### End of Day
1. Export session log
2. Confirm audit trail complete
3. Report units reviewed, time, issues

---

## 6. Reference: Decision Quick-Reference Card

```
ACCEPTED        → Identity ✓ + Prep ✓ + Species ✓ + Evidence ≥4 + Conf ≥4
REVIEW_REQUIRED → Plausible but gap in ONE dimension; Evidence=3; Conf=3
REJECTED        → Core identity mismatch OR Prep incompatible (no evidence)
UNMATCHED       → No candidate survives scrutiny
AMBIGUOUS       → >1 IFCT code equally plausible after full review

CONFIDENCE < 3  → CANNOT be ACCEPTED
RATIONALE < 50 chars → INVALID
EVIDENCE SCORE < 3 → CANNOT be ACCEPTED
```

---

## 6. Appendix: Evidence Field Reference

| Field | Location | Meaning |
|-------|----------|---------|
| `match_method` | Candidate | EXACT/SYNONYM/TOKEN_EQUIVALENT/TOKEN_SIMILARITY/FUZZY |
| `similarity_score` | Candidate | 0.0–1.0 |
| `match_method=EXACT` | Candidate | Canonical name equality |
| `match_method=SYNONYM` | Candidate | Verified synonym (conf≥0.95) |
| `match_source` | Evidence | canonical_mapping / exact_canonical / token_match |
| `preparation_state` | Disambiguated | RAW/FRESH/DRIED/POWDERED/etc |
| `preparation_confidence` | Disambiguated | 0.0–1.0 |
| `prep_state_compat` | Candidate | 0.0/0.5/1.0 |
| `extracted_aliases` | Disambiguated | JSON array of {text, type, confidence} |
| `ambiguity_flags` | Disambiguated | JSON array of flags |
| `acceptance_decision` | Evidence | Stage 2.3 gate decision |
| `ifct_food_name` | Candidate | Full IFCT name with scientific name |
| `ifct_food_group` | Candidate | IFCT food group |
| `recipe_id` | Candidate | Links to provenance |
| `original_ingredient` | Candidate | Original recipe text |
| `normalized_ingredient` | Candidate | Full normalized text |
| `primary_ingredient` | Candidate | Cleaned name for matching |