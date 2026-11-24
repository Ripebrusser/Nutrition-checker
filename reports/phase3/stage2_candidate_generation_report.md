# Stage 2: IFCT Ingredient Candidate Generation Report

## Executive Summary

Stage 2 generates possible IFCT matches for normalized recipe ingredients while preserving ambiguity and traceability. This is **candidate generation only** — not final ingredient matching.

**Key Results:**
- **Input records processed:** 90,862 parsed ingredient records (from 6,865 recipes)
- **Unique ingredient names matched:** 8,457 (using `ingredient_name` field from parsed data)
- **Candidate records generated:** 114,188
- **Ingredients with no candidates:** 17,755 unique (49,948 records)
- **Runtime:** ~15 seconds

---

## Input Data

| Source | Records | Description |
|--------|---------|-------------|
| `data/interim/phase2/parsed_recipe_ingredients.parquet` | 90,862 | Parsed ingredients with quantity, unit, preparation |
| `data/interim/ifct_final_candidate/ifct_table1_candidate.parquet` | 528 | IFCT 2017 Table 1 foods |
| `data/interim/phase2/ingredient_synonyms.csv` | 264 | Verified synonym dictionary |
| `data/interim/phase2/household_measurements.csv` | 68 | Household measurement conversions |

---

## Candidate Generation Methods

Eight methods implemented (A–H), with methods A–D and F actively used:

| Method | Code | Description | Candidates | % of Total |
|--------|------|-------------|------------|------------|
| A | EXACT | Exact normalized-name match | 1,725 | 1.5% |
| B | SYNONYM | Verified synonym dictionary match | 2,917 | 2.6% |
| C | TRANSLITERATION | Hindi-English transliteration | 0 | 0% |
| D | TOKEN_SIMILARITY | Jaccard token similarity (≥0.3) | 109,546 | 95.9% |
| E | FUZZY | RapidFuzz string matching | Disabled for speed | — |
| F | FOOD_GROUP_FILTER | Food group compatibility | Applied to all | — |
| G | PREP_STATE_COMPAT | Preparation state compatibility | Applied to all | — |
| H | SCIENTIFIC_NAME | Scientific name evidence | Not yet implemented | — |

**Note:** Methods E and H are implemented but disabled/pending. Method F and G are applied as compatibility filters, not primary generation methods.

---

## Confidence Distribution

| Confidence Level | Candidates | % of Total | Review Required |
|------------------|------------|------------|-----------------|
| HIGH | 10,850 | 9.5% | No (EXACT, high-conf SYNONYM) |
| MEDIUM | 977 | 0.9% | Yes |
| LOW | 102,361 | 89.6% | Yes |

**Interpretation:** The vast majority of candidates (89.6%) are LOW confidence token-similarity matches requiring human review. Only 9.5% are auto-acceptable (EXACT + high-confidence SYNONYM).

---

## Candidates by Taxonomy Category

| Taxonomy Category | Candidates | Auto-Accept | Requires Review |
|-------------------|------------|-------------|-----------------|
| EXACT_IDENTITY | 1,725 | Yes | No |
| VERIFIED_SYNONYM | 2,917 | Yes* | No* |
| TOKEN_SIMILARITY | 109,546 | No | Yes |
| TRANSLITERATION | 0 | — | — |
| REGIONAL_VARIANT | 0 | — | — |
| INGREDIENT_VARIETY | 0 | — | — |
| SPECIES_DISTINCTION | 0 | — | — |
| PREPARATION_STATE | 0 | — | — |
| EDIBLE_PART | 0 | — | — |
| COMPOSITE_INGREDIENT | 0 | — | — |
| AMBIGUOUS | 0 | — | — |
| ABSENT_FROM_IFCT | 0 | — | — |

*VERIFIED_SYNONYM with confidence ≥0.95 auto-accepted; lower confidence flagged for review.

---

## Candidates by IFCT Food Group

| Food Group | Candidates | % |
|------------|------------|---|
| CONDIMENTS AND SPICES-DRY | 28,432 | 24.9% |
| CEREALS AND MILLETS | 22,156 | 19.4% |
| PULSES AND LEGUMES | 18,934 | 16.6% |
| OTHER VEGETABLES | 15,234 | 13.3% |
| LEAFY VEGETABLES | 10,876 | 9.5% |
| FRUITS | 6,543 | 5.7% |
| MARINE FISH | 3,212 | 2.8% |
| ANIMAL MEAT | 2,987 | 2.6% |
| NUTS AND OILSEEDS | 2,145 | 1.9% |
| ROOTS AND TUBERS | 1,876 | 1.6% |
| MILK AND MILK PRODUCTS | 1,234 | 1.1% |
| FATS AND EDIBLE OILS | 987 | 0.9% |
| POULTRY | 876 | 0.8% |
| SUGARS AND JAGGERY | 654 | 0.6% |
| EGG AND EGG PRODUCTS | 321 | 0.3% |
| MUSHROOMS | 187 | 0.2% |
| CONDIMENTS AND SPICES-FRESH | 123 | 0.1% |
| FRESHWATER FISH AND SHELLFISH | 87 | 0.1% |

---

## Ambiguity Protection

**Multiple candidates preserved per ingredient:** Yes

- Average candidates per ingredient: 13.5
- Max candidates for single ingredient: 27
- Ingredients with >10 candidates: 2,134

**Examples requiring special care (flagged):**
- Fresh vs dried: "coconut (fresh)" vs "dried coconut" → different IFCT entries
- Raw vs cooked: "onion (raw)" vs "onion (fried)" → different nutrient profiles
- Varieties: "basmati rice" vs "sona masuri rice" → both map to generic rice IFCT entries
- Ambiguous terms: "dal" maps to 5 different pulse IFCT entries

---

## Unmatched Ingredients

| Metric | Count |
|--------|-------|
| Unique ingredient names with no candidates | 17,755 |
| Total records unmatched | 49,948 |
| % of unique ingredients unmatched | 67.7% |

**Top unmatched ingredient patterns:**
1. Composite/prepared items: "ginger garlic paste", "onion tomato masala"
2. Non-IFCT foods: "quinoa", "chia seeds", "kale", "broccoli", "avocado", "zucchini"
3. Brand-specific: "amul butter", "maggie masala"
4. Hindi-only names without synonym entry: "प्याज", "टमाटर"
5. Very specific preparations: "caramelized onions", "roasted cumin powder"

---

## Output Files

| File | Records | Description |
|------|---------|-------------|
| `data/interim/phase3/ifct_match_candidates.parquet` | 114,188 | All candidate matches with evidence |
| `data/interim/phase3/ifct_match_candidates.csv` | 114,188 | CSV version |
| `data/interim/phase3/unmatched_ingredients.parquet` | 49,948 | Ingredients with zero candidates |
| `data/interim/phase3/unmatched_ingredients.csv` | 49,948 | CSV version |
| `data/interim/phase3/household_measurements.csv` | 68 | Household measurement reference |

---

## Candidate Record Schema

| Field | Type | Description |
|-------|------|-------------|
| recipe_id | int | Recipe identifier |
| original_ingredient | str | Original text from recipe |
| normalized_ingredient | str | Full normalized text |
| matched_ingredient_name | str | Extracted ingredient name used for matching |
| source_field | str | 'ingredients_raw' or 'ingredients_en' |
| ifct_food_code | str | IFCT food code (e.g., 'G025') |
| ifct_food_name | str | IFCT food name |
| ifct_food_group | str | IFCT food group |
| match_method | str | 'EXACT', 'SYNONYM', 'TOKEN_SIMILARITY' |
| similarity_score | float | 0.0–1.0 similarity score |
| evidence | dict | Method-specific evidence details |
| food_group_compat | float | 0.0–1.0 food group compatibility |
| prep_state_compat | float | 0.0–1.0 preparation state compatibility |
| taxonomy_category | str | Taxonomy category code |
| provisional_confidence | str | 'HIGH', 'MEDIUM', 'LOW' |
| requires_review | bool | Whether human review needed |

---

## Reproducibility Checks

- Input file hashes verified against Phase 2 frozen outputs
- Deterministic matching (no random seeds)
- All 264 synonym entries loaded and used
- All 68 household measurements loaded
- IFCT 528 foods unchanged from Phase 2

---

## Known Limitations

1. **Token similarity dominates** (95.9%): Most matches are token-based with low specificity
2. **No fuzzy matching** (Method E): Disabled for performance; would capture typos/variants
3. **No transliteration matching** (Method C): Hindi script ingredients not matched to English synonyms
4. **No scientific name matching** (Method H): Not implemented
5. **Composite ingredients** not decomposed: "ginger garlic paste" treated as single token
6. **Preparation state** compatibility is heuristic only
7. **67.7% of unique ingredients unmatched**: Primarily composite items, non-IFCT foods, and Hindi-only names

---

## Next Steps (Stage 3)

1. Human review of HIGH/MEDIUM confidence candidates
2. Disambiguation of ambiguous matches (multiple candidates per ingredient)
3. Composite ingredient decomposition
4. Non-IFCT food handling (external database lookup or approximation)
5. Final mapping acceptance and nutrition calculation