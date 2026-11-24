# Stage 2 Documentation Corrections

**Purpose:** Correct numerical errors in Stage 2 reports without overwriting historical documents.

**Original Reports:**
- `reports/phase3/stage2_candidate_generation_report.md`
- `reports/phase3/stage2_matching_method_report.md`
- `reports/phase3/stage2_negative_control_report.md`

---

## Correction 1: Unique Ingredient Count Definitions

**File:** `stage2_candidate_generation_report.md`  
**Section:** Executive Summary / Key Results  

**Original:**
> - Unique ingredient names processed: 8,457
> - Ingredients with no candidates: 17,755 unique

**Corrected:**
> - Unique `normalized_ingredient` expressions with candidates: 8,457
> - Unique `normalized_ingredient` expressions without candidates: 17,755
> - Unique `ingredient_name` expressions with candidates: 2,835
> - Unique `ingredient_name` expressions without candidates: 10,216

**Reason:** The terms "ingredient names" was ambiguous. The 8,457/17,755 figures refer to `normalized_ingredient` (full text including quantities/preparation), not `ingredient_name` (parsed name only).

---

## Correction 2: Unmatched Percentage

**File:** `stage2_candidate_generation_report.md`  
**Section:** Unmatched Ingredients  

**Original:**
> | % of unique ingredients unmatched | 67.7% |

**Corrected:**
> | Metric | Unmatched | Total | Percentage |
> |--------|-----------|-------|------------|
> | Ingredient records | 49,948 | 90,862 | **55.0%** |
> | Unique `ingredient_name` | 10,216 | 13,049 | **78.3%** |
> | Unique `normalized_ingredient` | 17,755 | 26,210 | **67.7%** |

**Reason:** The 67.7% figure is correct only for `normalized_ingredient` denominator. Record-level unmatched is 55.0%; parsed-name-level is 78.3%. All three must be reported with explicit denominators.

---

## Correction 3: Confidence Classification — Auto-Accept Status

**File:** `stage2_candidate_generation_report.md`  
**Section:** Confidence Distribution / Candidates by Taxonomy Category  

**Original:**
> | Confidence Level | Candidates | % of Total | Review Required |
> |------------------|------------|------------|-----------------|
> | HIGH | 10,850 | 9.5% | No (EXACT, high-conf SYNONYM) |
> | MEDIUM | 977 | 0.9% | Yes |
> | LOW | 102,361 | 89.6% | Yes |

**Corrected:**
> | Confidence Level | Candidates | % of Total | `requires_review=False` | `requires_review=True` |
> |------------------|------------|------------|-------------------------|------------------------|
> | HIGH | 10,850 | 9.5% | 3,839 | 7,011 |
> | MEDIUM | 977 | 0.9% | 0 | 977 |
> | LOW | 102,361 | 89.6% | 0 | 102,361 |
> | **Total** | **114,188** | **100%** | **3,839 (3.4%)** | **110,349 (96.6%)** |

**Breakdown of `requires_review=False` (3,839):**
- EXACT matches: 1,725 (all HIGH)
- SYNONYM matches with confidence ≥0.95: 2,114 (all HIGH, but **still require review due to code defect**)

**Critical Note:** The design specifies "SYNONYM confidence ≥0.95 auto-accept", but the implementation forces `requires_review=True` for all non-EXACT methods (line 520 in candidate_generator.py). **No SYNONYM candidates are currently auto-accepted.**

---

## Correction 4: Taxonomy Category Auto-Accept Status

**File:** `stage2_candidate_generation_report.md`  
**Section:** Candidates by Taxonomy Category  

**Original:**
> | Taxonomy Category | Candidates | Auto-Accept | Requires Review |
> |-------------------|------------|-------------|-----------------|
> | EXACT_IDENTITY | 1,725 | Yes | No |
> | VERIFIED_SYNONYM | 2,917 | Yes* | No* |
> | TOKEN_SIMILARITY | 109,546 | No | Yes |

**Corrected:**
> | Taxonomy Category | Candidates | `requires_review=False` | `requires_review=True` | Notes |
> |-------------------|------------|-------------------------|------------------------|-------|
> | EXACT_IDENTITY | 1,725 | 1,725 | 0 | True auto-accept |
> | VERIFIED_SYNONYM | 2,917 | 0 | 2,917 | **Design says Yes*; code says No** |
> | TOKEN_SIMILARITY | 109,546 | 0 | 109,546 | Includes 7,011 with Jaccard=1.0 misclassified as HIGH |

**Reason:** The `*` footnote "VERIFIED_SYNONYM with confidence ≥0.95 auto-accepted" describes the **design intent**, not the **actual implementation**. Currently 0 SYNONYM candidates have `requires_review=False`.

---

## Correction 5: TOKEN_SIMILARITY HIGH Confidence Misclassification

**File:** `stage2_candidate_generation_report.md` / `stage2_matching_method_report.md`  

**Original (implied):** HIGH confidence TOKEN_SIMILARITY candidates are valid high-confidence matches.

**Correction:** **7,011 TOKEN_SIMILARITY candidates have Jaccard similarity = 1.0 and are marked HIGH confidence.** These are exact token-set matches that should have been caught by the EXACT method but weren't due to normalization differences (e.g., parentheses in IFCT food names). They are **not** true high-confidence fuzzy matches — they are exact matches misclassified.

**Impact:** These 7,011 candidates inflate the HIGH confidence count from 3,839 (true auto-accept) to 10,850.

---

## Correction 6: Negative Control Pass Rate

**File:** `stage2_negative_control_report.md`  
**Section:** Negative Control Summary  

**Original:**
> Overall: 36/40 test cases behave correctly (90%)

**Corrected:**
> Overall: 31/40 test cases behave correctly (**77.5%**)
> - 9 cases show limitations (4 "neutral" due to IFCT gaps, 1 canonical override error, 1 paneer actually exists, 3 duplicate counts)

**Reason:** The 90% figure counted "neutral" results (where IFCT lacks preparation variants) as passes. True passes = correct rejection/flagging. The 4 "neutral" fresh/dried and 2 "neutral" raw/cooked cases are IFCT coverage gaps, not system successes.

---

## Correction 7: Test Counts

**File:** Various  

**Original Claims:**
- "All 80 Phase 1+2 tests pass"
- "119 passed"

**Corrected:**
| Suite | Tests | Passed | Failed |
|-------|-------|--------|--------|
| Phase 1 (`test_phase1.py`) | 44 | 44 | 0 |
| Phase 2 Normalization | 14 | 14 | 0 |
| Phase 2 Quantity Parsing | 22 | 22 | 0 |
| IFCT Extraction (`test_ifct_extraction.py`) | 46 | 39 | 7 |
| **Total** | **126** | **119** | **7** |

**The 7 failures are IFCT extraction gaps** (missing food groups/codes in parsed PDF data), not Phase 1/2 regressions. They are "legacy" in the sense of "known since IFCT extraction phase" but not "pre-existing and documented as acceptable."

---

## Correction 8: Candidate Method Overlap

**File:** `stage2_matching_method_report.md`  
**Section:** Method Comparison Summary  

**Original:** Implied methods might overlap.

**Corrected:** **Methods are mutually exclusive per (recipe_id, ingredient_name) pair.** 0 overlaps found in 40,105 recipe-ingredient pairs. Pipeline applies: EXACT → SYNONYM → TOKEN_SIMILARITY, deduplicating by IFCT code.

---

## Correction 9: Candidates Per Ingredient

**File:** `stage2_candidate_generation_report.md`  
**Section:** Ambiguity Protection  

**Original:**
> - Average candidates per ingredient: 13.5
> - Max candidates for single ingredient: 27

**Corrected:**
> - Mean **unique IFCT codes** per unique `ingredient_name`: 2.5
> - Max unique IFCT codes per `ingredient_name`: 19
> - Mean candidate **records** per recipe-ingredient pair: 2.8
> - Max candidate records for single `ingredient_name` across all recipes: 12,824 (for "red chilli" appearing in ~1,832 recipes × 7 IFCT codes)

**Reason:** The original "13.5 average" conflated candidate records (114,188) with unique ingredients (8,457). The "max 27" was incorrect; max unique IFCT codes per ingredient is 19.

---

## Summary of Critical Corrections

| # | Metric | Originally Reported | Corrected Value |
|---|--------|---------------------|-----------------|
| 1 | Unmatched % | 67.7% | 55.0% (records) / 78.3% (ingredient_name) / 67.7% (normalized_ingredient) |
| 2 | Auto-accept candidates | ~10,850 (HIGH) | 3,839 (EXACT only) |
| 3 | SYNONYM auto-accept | Yes* (2,917) | No (0 implemented) |
| 4 | TOKEN_SIMILARITY HIGH | Valid high-confidence | 7,011 are Jaccard=1.0 misclassified |
| 5 | Negative control pass | 90% | 77.5% |
| 6 | Test count | 80 / 119 | 126 total (119 pass, 7 fail) |
| 7 | Avg candidates/ingredient | 13.5 | 2.5 unique IFCT codes |
| 8 | Max candidates/ingredient | 27 | 19 unique IFCT codes |

---

## Required Actions Before Stage 3

1. [ ] Update all Stage 2 reports with corrected numbers (or add correction addenda)
2. [ ] Fix SYNONYM auto-accept logic in candidate_generator.py line 520
3. [ ] Fix EXACT vs TOKEN_SIMILARITY classification for Jaccard=1.0 cases
4. [ ] Document that HIGH confidence ≠ auto-accept in all reports
5. [ ] Re-run Stage 2 after fixes (or apply corrections in Stage 3 mapping)

**Do not proceed to Stage 3 until Corrections 2, 3, and 4 are resolved in the mapping logic.**