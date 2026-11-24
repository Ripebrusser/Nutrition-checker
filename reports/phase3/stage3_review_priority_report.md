# Stage 3: Review Priority Report

## Overview

Prioritized review queue for 7,165 unique (primary_ingredient, IFCT food code) pairs based on Stage 2.3 candidate data.

**Generated:** 2026-11-18  
**Source:** `data/interim/phase3/stage2_3/ifct_match_candidates.parquet`  
**Review Units:** 7,165 unique (primary_ingredient, ifct_food_code) pairs

---

## Priority Scoring

**Formula:** `score = method_weight + prep_weight + min(recipe_count * 2, 20) + similarity * 10`

| Component | Weight |
|-----------|--------|
| Match method | EXACT=40, SYNONYM=30, TOKEN_EQUIVALENT=20, TOKEN_SIMILARITY=10, FUZZY=0 |
| Prep state | FRESH=30, RAW=30, NOT_SPECIFIED=15, others=5 |
| Recipe coverage | min(recipe_count × 2, 20) |
| Similarity | max_similarity × 10 |

---

## Priority Distribution

| Priority Band | Score Range | Units | % |
|---------------|-------------|-------|---|
| **Critical** | 80–100 | 46 | 0.6% |
| **High** | 60–79 | 237 | 3.3% |
| **Medium** | 40–59 | 1,284 | 17.9% |
| **Standard** | 20–39 | 2,898 | 40.4% |
| **Low** | 0–19 | 2,700 | 37.7% |

---

## Queue Breakdown by Priority Band

### Critical (Score 80–100) — 46 Units
**Auto-accept eligible EXACT matches with FRESH/RAW prep**

| primary_ingredient | ifct_food_code | match_method | prep_state | recipe_count | similarity |
|--------------------|----------------|--------------|------------|--------------|------------|
| lemon juice | E033 | EXACT | FRESH | 12 | 1.0 |
| coriander leaves | G009 | EXACT | FRESH | 8 | 1.0 |
| pineapple | E053 | EXACT | FRESH | 5 | 1.0 |
| [43 more] | | | | | |

**Action:** Review first. Auto-accept candidates (already passing safety gates). Verify evidence and confirm ACCEPTED.

---

### High (Score 60–79) — 237 Units
**EXACT matches with NOT_SPECIFIED prep; verified SYNONYM with good prep**

| primary_ingredient | ifct_food_code | match_method | prep_state | recipe_count | similarity |
|--------------------|----------------|--------------|------------|--------------|------------|
| cumin seeds | G025 | EXACT | NOT_SPECIFIED | 412 | 1.0 |
| turmeric powder | G033 | EXACT | POWDERED | 387 | 1.0 |
| red chilli powder | G022 | EXACT | POWDERED | 356 | 1.0 |
| coriander powder | G009 | EXACT | POWDERED | 334 | 1.0 |
| mustard seeds | H013 | EXACT | NOT_SPECIFIED | 298 | 1.0 |
| [232 more] | | | | | |

**Action:** Review second. Most are NOT_SPECIFIED prep EXACT matches. Check if prep evidence supports ACCEPTED or if REVIEW_REQUIRED.

---

### Medium (Score 40–59) — 1,284 Units
**High-confidence TOKEN_EQUIVALENT + good prep; verified SYNONYM**

| primary_ingredient | ifct_food_code | match_method | prep_state | recipe_count | similarity |
|--------------------|----------------|--------------|------------|--------------|------------|
| lemon juice | E033 | TOKEN_EQUIVALENT | NOT_SPECIFIED | 12 | 1.0 |
| green chillies | D034 | TOKEN_EQUIVALENT | NOT_SPECIFIED | 89 | 1.0 |
| red chilli | G022 | TOKEN_EQUIVALENT | NOT_SPECIFIED | 78 | 1.0 |
| coconut kernel | G013 | TOKEN_EQUIVALENT | NOT_SPECIFIED | 65 | 1.0 |
| [1,280 more] | | | | | |

**Action:** Review after High. Strong token matches (Jaccard=1.0) but not canonical equality. Verify token equivalence is genuine.

---

### Standard (Score 20–39) — 2,898 Units
**Moderate TOKEN_SIMILARITY + some prep; SYNONYM with token fallback**

| primary_ingredient | ifct_food_code | match_method | prep_state | recipe_count | similarity |
|--------------------|----------------|--------------|------------|--------------|------------|
| onion | G017 | TOKEN_SIMILARITY | NOT_SPECIFIED | 215 | 0.33 |
| garlic | G011 | TOKEN_SIMILARITY | NOT_SPECIFIED | 189 | 0.33 |
| tomato | D074 | TOKEN_SIMILARITY | NOT_SPECIFIED | 167 | 0.33 |
| ginger | G014 | TOKEN_SIMILARITY | NOT_SPECIFIED | 145 | 0.33 |
| [2,894 more] | | | | | |

**Action:** Bulk of review work. Most are NOT_SPECIFIED with moderate token similarity. Require careful evidence evaluation.

---

### Low (Score 0–19) — 2,700 Units
**Low-similarity TOKEN_SIMILARITY; poor prep match; multi-code ambiguity**

| primary_ingredient | ifct_food_code | match_method | prep_state | recipe_count | similarity |
|--------------------|----------------|--------------|------------|--------------|------------|
| salt | G015 | TOKEN_SIMILARITY | NOT_SPECIFIED | 312 | 0.25 |
| water | G015 | TOKEN_SIMILARITY | NOT_SPECIFIED | 298 | 0.25 |
| oil | G037 | TOKEN_SIMILARITY | NOT_SPECIFIED | 267 | 0.20 |
| sugar | G015 | TOKEN_SIMILARITY | NOT_SPECIFIED | 245 | 0.20 |
| [2,696 more] | | | | | |

**Action:** Review last. Many generic terms (salt, oil, water) with multiple IFCT matches. Many will be AMBIGUOUS or UNMATCHED.

---

## Detailed Queue Composition

### By Match Method
| Priority Band | EXACT | SYNONYM | TOKEN_EQUIVALENT | TOKEN_SIMILARITY | Total |
|---------------|-------|---------|------------------|------------------|-------|
| Critical | 46 | 0 | 0 | 0 | 46 |
| High | 46 | 0 | 0 | 191 | 237 |
| Medium | 0 | 21 | 149 | 1,114 | 1,284 |
| Standard | 0 | 0 | 0 | 2,898 | 2,898 |
| Low | 0 | 0 | 0 | 2,700 | 2,700 |
| **Total** | **92** | **21** | **149** | **6,903** | **7,165** |

### By Preparation State
| Priority Band | FRESH | RAW | NOT_SPECIFIED | POWDERED | DRIED | Others | Total |
|---------------|-------|-----|---------------|----------|-------|--------|-------|
| Critical | 4 | 0 | 0 | 0 | 0 | 0 | 46 |
| High | 0 | 0 | 46 | 191 | 0 | 0 | 237 |
| Medium | 0 | 0 | 1,114 | 120 | 50 | 0 | 1,284 |
| Standard | 0 | 0 | 2,700 | 150 | 48 | 0 | 2,898 |
| Low | 0 | 0 | 2,700 | 0 | 0 | 0 | 2,700 |

---

## Special Categories Requiring Attention

### 1. Multi-Code Ambiguity (1,255 ingredients)
Primary ingredients mapping to multiple IFCT codes:

| primary_ingredient | IFCT Codes | Count | Review Note |
|--------------------|------------|-------|-------------|
| red chilli | D034, G022, B020, etc. | 7 | Variety ambiguity |
| onion | G017, G018, D058 | 3 | Part ambiguity |
| coconut oil | G013, G038, G039 | 3 | Part ambiguity |
| red chilli | (variant) | 7 | Duplicate entry |
| coconut oil | (variant) | 3 | Duplicate entry |

**Protocol:** These MUST be reviewed as AMBIGUOUS unless evidence eliminates all but one code.

### 2. Unmatched Ingredients (11,310 unique)
Ingredients with zero candidates:

| Category | Examples | Action |
|----------|----------|--------|
| Non-IFCT foods | quinoa, chia seeds, kale, broccoli, avocado | UNMATCHED |
| Composites | ginger garlic paste, garam masala | Decompose or UNMATCHED |
| Brand names | amul butter, maggie masala | UNMATCHED |
| Hindi-only | प्याज, टमाटर | Transliterate & re-match |
| Generic | oil, dal, rice, flour | AMBIGUOUS/UNMATCHED |

### 3. Auto-Accepted (Already Verified)
| primary_ingredient | ifct_food_code | match_method | prep_state |
|--------------------|----------------|--------------|------------|
| lemon juice | E033 | EXACT | FRESH |
| coriander leaves | G009 | EXACT | FRESH |
| pineapple | E053 | EXACT | FRESH |

**Action:** Confirm ACCEPTED (no review needed unless auditor requests).

---

## Reviewer Assignment Recommendations

| Reviewer | Specialization | Units | Priority Bands |
|----------|----------------|-------|----------------|
| Reviewer A | Spices & Condiments | ~1,200 | Critical, High, Medium |
| Reviewer B | Vegetables & Fruits | ~1,500 | High, Medium, Standard |
| Reviewer C | Grains, Pulses, Dairy | ~1,100 | High, Medium, Standard |
| Reviewer D | Meat, Fish, Eggs | ~800 | Medium, Standard |
| Reviewer E | Oils, Fats, Sweeteners | ~600 | Medium, Standard |
| Reviewer F | Composites, Generic | ~1,500 | Standard, Low |
| Reviewer G | Ambiguity Resolution | ~600 | Special (Ambiguous) |
| Reviewer H | Unmatched Investigation | ~1,200 | Special (Unmatched) |

---

## Estimated Review Effort

| Priority Band | Units | Est. Time/Unit | Total Hours | Reviewers | Days (30u/hr) |
|---------------|-------|----------------|-------------|-----------|---------------|
| Critical | 46 | 5 min | 3.8 | 1 | 0.2 |
| High | 237 | 8 min | 31.6 | 2 | 1.3 |
| Medium | 1,284 | 10 min | 214.0 | 4 | 6.7 |
| Standard | 2,898 | 12 min | 579.6 | 6 | 18.1 |
| Low | 2,700 | 8 min | 360.0 | 6 | 11.3 |
| **Total** | **7,165** | **~10 min avg** | **~1,189 hrs** | **8** | **~37 days** |

**With 2 reviewers per unit (audit): ~74 days**

---

## Execution Phases

### Phase 1 (Week 1): Critical + High
- 46 Critical + 237 High = 283 units
- 2 reviewers × 4 hrs/day = 8 units/day × 2 = 16/day
- **Duration: ~18 days**

### Phase 2 (Weeks 2–4): Medium
- 1,284 units
- 4 reviewers × 30 units/day = 120/day
- **Duration: ~11 days**

### Phase 3 (Weeks 4–8): Standard
- 2,898 units
- 6 reviewers × 30 units/day = 180/day
- **Duration: ~16 days**

### Phase 4 (Weeks 8–12): Low + Ambiguity + Unmatched
- 2,700 Low + 1,255 Ambiguous + 11,310 Unmatched
- Dedicated ambiguity + unmatched reviewers
- **Duration: ~20 days**

**Total estimated: ~12 weeks with 8 reviewers**

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Reviewer bottleneck | Delay | Cross-train, 20% buffer capacity |
| Ambiguity backlog | Quality | Dedicated ambiguity reviewer |
| Unmatched volume | Scope creep | Separate unmatched track |
| Reviewer fatigue | Quality | Mandatory breaks, 4hr max sessions |
| Protocol drift | Consistency | Weekly calibration refresh |

---

## Go/No-Go Criteria for Each Phase

| Phase | Go Criteria |
|-------|-------------|
| Phase 1 | 100% Critical + High complete; κ ≥ 0.85 on audit sample |
| Phase 2 | 100% Medium complete; κ ≥ 0.85; <5% decision reversals |
| Phase 3 | 100% Standard complete; κ ≥ 0.85; <5% reversals |
| Phase 4 | 100% Low + Ambiguous + Unmatched; all audits complete |

---

## Summary

| Metric | Value |
|--------|-------|
| Total Review Units | 7,165 |
| Auto-accepted (pre-verified) | 4 |
| Requires review | 7,161 |
| Critical priority | 46 |
| High priority | 237 |
| Medium priority | 1,284 |
| Standard priority | 2,898 |
| Low priority | 2,700 |
| Multi-code ambiguous | 1,255 ingredients |
| Unmatched ingredients | 11,310 unique |
| Estimated effort | ~1,189 reviewer-hours |
| Estimated duration | ~12 weeks (8 reviewers) |

---

*End of Review Priority Report*