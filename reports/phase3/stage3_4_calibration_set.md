# Stage 3.4: Calibration Set

**Date:** 2026-11-18  
**Status:** Approved for use in workbench calibration

---

## Overview

This calibration set contains 5 carefully selected ingredient-IFCT mapping examples that cover the range of matching scenarios reviewers will encounter. Each example includes the ingredient expression, candidate IFCT records, correct review considerations, relevant evidence, expected decision, and detailed explanation.

These examples are for **calibration and training purposes only**. They are not ground truth for production mappings.

---

## Calibration Examples

---

### Calibration Unit 1: Straightforward EXACT Match (FRESH)

| Field | Value |
|-------|-------|
| **Original Expression** | `2 teaspoons turmeric powder (haldi)` |
| **Normalized** | `2 teaspoons turmeric powder (haldi)` |
| **Primary Ingredient** | `turmeric powder` |
| **Parenthetical** | `haldi` |
| **Preparation State** | `FRESH` |
| **Parsed Quantity** | 2 tsp |
| **Parsed Unit** | `teaspoon` |

**IFCT Candidates:**

| Code | Food Name | Group | Match Method | Similarity | Evidence |
|------|-----------|-------|--------------|------------|----------|
| **G033** | Turmeric powder (Curcuma domestica) | CONDIMENTS AND SPICES-DRY | EXACT | 1.0 | Exact canonical name match after normalization |
| G032 | Turmeric (fresh) (Curcuma domestica) | CONDIMENTS AND SPICES-FRESH | TOKEN_SIMILARITY | 0.67 | Different prep state |

**Correct Decision:** **ACCEPTED** (G033 - Turmeric powder)

**Evidence:**
- Match method: EXACT (canonical name equality after normalization)
- Preparation state: FRESH (compatible with IFCT raw basis)
- Similarity: 1.0 (exact match)
- IFCT food name: "Turmeric powder (Curcuma domestica)"
- IFCT code: G033
- Species: Curcuma domestica
- Edible part: rhizome (implied by "powder")
- IFCT source: Table 1, Page 142 (Condiments and Spices - Dry)
- Preparation compatibility: FRESH matches IFCT raw basis

**Expected Decision:** `ACCEPTED` with high confidence (5)

**Rationale:** The ingredient "turmeric powder (haldi)" exactly matches IFCT entry "Turmeric powder (Curcuma domestica)" (G033) with similarity 1.0. The preparation state is FRESH, which is compatible with IFCT's raw-food basis. All 15 mandatory evidence fields are satisfied.

---

### Calibration Unit 2: Exact Match with NOT_SPECIFIED Prep (Requires Review)

| Field | Value |
|-------|-------|
| **Original Expression** | `1 tablespoon coriander powder (dhania)` |
| **Normalized** | `1 tablespoon coriander powder (dhania)` |
| **Primary Ingredient** | `coriander powder` |
| **Parenthetical** | `dhania` |
| **Preparation State** | `NOT_SPECIFIED` |
| **Parsed Quantity** | 1 tbsp |
| **Parsed Unit** | `tablespoon` |

**IFCT Candidates:**

| Code | Food Name | Group | Match Method | Similarity | Evidence |
|------|-----------|-------|--------------|------------|----------|
| **G009** | Coriander powder (Coriandrum sativum) | CONDIMENTS AND SPICES-DRY | SYNONYM | 0.95 | Synonym "dhania" → canonical "coriander powder" |
| G008 | Coriander seeds (Coriandrum sativum) | CONDIMENTS AND SPICES-DRY | TOKEN_SIMILARITY | 0.67 | Token overlap only |

**Correct Decision:** **REVIEW_REQUIRED** (G009 - Coriander powder)

**Evidence:**
- Match method: SYNONYM (via "dhania" → "coriander powder" with confidence 0.95)
- Preparation state: NOT_SPECIFIED (requires explicit reviewer evidence per policy)
- Similarity: 0.95 (synonym confidence)
- IFCT food name: "Coriander powder (Coriandrum sativum)"
- IFCT code: G009
- Species: Coriandrum sativum
- Edible part: seeds (implied by "powder")
- IFCT source: Table 1, Page 141 (Condiments and Spices - Dry)

**Expected Decision:** **REVIEW_REQUIRED** (NOT_SPECIFIED prep requires explicit reviewer evidence per policy)

**Rationale:** Although the synonym match is strong (0.95), the preparation state is NOT_SPECIFIED. Per the auto-accept policy, NOT_SPECIFIED preparation states are NEVER auto-accepted and require explicit reviewer evidence that the ingredient is used raw/fresh in the recipe.

---

### Calibration Unit 3: Token Equivalent (Jaccard = 1.0) but Not Canonical Exact

| Field | Value |
|-------|-------|
| **Original Expression** | `lemon juice` |
| **Normalized** | `lemon juice` |
| **Primary Ingredient** | `lemon juice` |
| **Preparation State** | `NOT_SPECIFIED` |

**IFCT Candidates:**

| Code | Food Name | Group | Match Method | Similarity | Evidence |
|------|-----------|-------|--------------|------------|----------|
| **E033** | Lemon, juice (Citrus limon) | FRUITS | TOKEN_EQUIVALENT | 1.0 | Token sets identical: {lemon, juice} |
| E032 | Lemon (Citrus limon) | FRUITS | TOKEN_SIMILARITY | 0.5 | Partial token match |

**Correct Decision:** **REVIEW_REQUIRED** (E033 - Lemon, juice)

**Evidence:**
- Match method: TOKEN_EQUIVALENT (Jaccard = 1.0)
- Token sets identical: {lemon, juice} = {lemon, juice}
- But NOT canonical exact match (IFCT name is "Lemon, juice (Citrus limon)")
- Preparation state: NOT_SPECIFIED
- IFCT food name: "Lemon, juice (Citrus limon)"
- IFCT code: E033
- Species: Citrus limon
- Edible part: juice

**Expected Decision:** **REVIEW_REQUIRED**

**Rationale:** Although the Jaccard similarity is 1.0 (identical token sets), this is classified as TOKEN_EQUIVALENT, not EXACT. The canonical IFCT name "Lemon, juice (Citrus limon)" differs from "lemon juice" (parentheses removed in canonical normalization). Per policy, TOKEN_EQUIVALENT matches are NEVER auto-accepted and require reviewer verification. Additionally, preparation state is NOT_SPECIFIED.

---

### Calibration Unit 4: Multi-Code Ambiguity (Red Chilli)

| Field | Value |
|-------|-------|
| **Original Expression** | `1 tablespoon red chilli powder` |
| **Normalized** | `1 tablespoon red chilli powder` |
| **Primary Ingredient** | `red chilli powder` |
| **Preparation State** | `POWDERED` |

**IFCT Candidates (7 matches):**

| Code | Food Name | Group | Match Method | Similarity |
|------|-----------|-------|--------------|------------|
| G022 | Chillies, red (Capsicum annuum) | CONDIMENTS AND SPICES-DRY | TOKEN_SIMILARITY | 0.33 |
| B020 | Red gram, whole (Cajanus cajan) | PULSES AND LEGUMES | TOKEN_SIMILARITY | 0.33 |
| D034 | Red chilli, fresh | FRUITS | TOKEN_SIMILARITY | 0.33 |
| E014 | Red chilli, dry | CONDIMENTS AND SPICES-DRY | TOKEN_SIMILARITY | 0.33 |
| B020 | Red gram, whole (Cajanus cajan) | PULSES AND LEGUMES | TOKEN_SIMILARITY | 0.33 |
| P065 | Red snapper | MARINE FISH | TOKEN_SIMILARITY | 0.33 |
| F003 | Red chilli, dry | CONDIMENTS AND SPICES-DRY | TOKEN_SIMILARITY | 0.33 |

**Correct Decision:** **AMBIGUOUS** (multiple equally plausible IFCT codes)

**Evidence:**
- 7 candidate IFCT codes with identical similarity (0.33)
- Different food groups: Condiments, Pulses, Fruits, Marine Fish
- Different species: Capsicum annuum vs Cajanus cajan
- Different edible parts: fruit vs seed vs whole
- Preparation: POWDERED (incompatible with IFCT raw basis)

**Expected Decision:** **AMBIGUOUS**

**Rationale:** Seven equally plausible IFCT codes with identical similarity scores. No single candidate can be justified over others without additional recipe context. Must be escalated for expert review.

---

### Calibration Unit 5: Unmatched Ingredient (Quinoa)

| Field | Value |
|-------|-------|
| **Original Expression** | `1 cup quinoa` |
| **Normalized** | `1 cup quinoa` |
| **Primary Ingredient** | `quinoa` |
| **Preparation State** | `NOT_SPECIFIED` |

**IFCT Candidates:** None (quinoa not in IFCT 2017)

**Correct Decision:** **NO_IFCT_EQUIVALENT** (UNMATCHED)

**Evidence:**
- No candidate IFCT matches found (similarity = 0)
- Quinoa (Chenopodium quinoa) not in IFCT 2017 Table 1
- Preparation state: NOT_SPECIFIED
- No candidate IFCT codes

**Expected Decision:** **NO_IFCT_EQUIVALENT** (UNMATCHED)

**Rationale:** Quinoa is not present in IFCT 2017 Table 1. No candidate mappings exist. Ingredient is genuinely absent from the reference database.

---

## Summary of Calibration Decisions

| Unit | Ingredient | Expected Decision | Key Reason |
|------|------------|-------------------|------------|
| 1 | Turmeric powder (haldi) | **ACCEPTED** | EXACT + FRESH + sim=1.0 |
| 2 | Coriander powder (dhania) | **REVIEW_REQUIRED** | NOT_SPECIFIED prep requires evidence |
| 3 | Lemon juice | **REVIEW_REQUIRED** | TOKEN_EQUIVALENT (not EXACT) + NOT_SPECIFIED |
| 4 | Red chilli powder | **AMBIGUOUS** | 7 equally plausible IFCT codes |
| 5 | Quinoa | **NO_IFCT_EQUIVALENT** | Not in IFCT 2017 |

---

## Usage Instructions

1. Load the calibration set in the workbench before starting reviews
2. Review each unit independently
3. Compare your decision with the expected decision
3. Discuss any discrepancies with the calibration coordinator
4. Only proceed to production review after achieving consistency on all 5 units

---

*End of Calibration Set*