# Dataset Suitability Decision

**Project:** AI for Nutrition & Diet Planning
**Phase:** 1 — Dataset Validation and Preprocessing
**Date:** 2026-11-15
**Decision Authority:** Lead Data Engineer

---

## Executive Summary

| Dataset | Decision | Rationale |
|---------|----------|-----------|
| IndianFoodDatasetXLS/CSV | ✅ **USE** — Primary recipe corpus | 6,865 valid recipes after cleaning; rich ingredient text, diet/course/cuisine labels, source URLs |
| Anuvaad_INDB_2024.11 | ✅ **USE** — Primary composition source | 1,014 Indian foods with 39 per-100g nutrients; 8.1% missing per-serving data documented |
| USDA FDC (5 files) | ⚠️ **CONDITIONAL** — Gap-fill only | US foods only; require manual ingredient↔FDC mapping; never auto-join |
| NHANES (5 files) | ❌ **EXCLUDE** from core pipeline | US population survey data; not recipes; keep separate for external validation |
| diet_recommendations_dataset.csv | ❌ **EXCLUDE** — Not present / Target leakage | Derived disease→diet targets; would leak labels into training |

---

## Detailed Decisions

### 1. Indian Food Recipe Dataset (IndianFoodDatasetXLS.xlsx / CSV)

**Decision: USE as primary recipe corpus**

**Supporting Evidence:**
- 6,871 raw records → 6,865 after removing 6 missing ingredient rows
- All recipes have unique Srno (PK) and unique source URLs
- Time consistency verified: TotalTime = PrepTime + CookTime for all records
- Rich multilingual content: original (Hindi/English) + translated fields preserved separately
- 82 cuisine labels (after cleaning), 11 course labels, 10 diet labels
- 27 duplicate TranslatedRecipeName pairs — distinct recipes, kept with original Srno

**Required Transformations (Applied):**
- Removed 6 recipes with missing ingredient text → archived to `data/interim/recipes_missing_ingredients.csv`
- Fixed label pollution: 15 cuisine values were actually courses; 62 course values were actually diets
- Classified 35 condiment/prep recipes (servings > 50 or "how to"/batter/masala patterns) → flagged as `recipe_type=condiment|prep`, archived to `data/interim/recipes_condiments.csv`
- Standardized taxonomies to controlled vocabularies (see Data Dictionary §4)

**Limitations:**
- Ingredient quantities embedded in free text — requires NLP parsing (Phase 2)
- No explicit ingredient weights — cannot compute exact nutrition without mapping to composition data
- Cuisine labels include many international cuisines; "Indian" is generic catch-all
- Source licence unclear (scraped from archanaskitchen.com) — academic use only

---

### 2. Anuvaad INDB 2024.11 (Indian Food Composition Database)

**Decision: USE as primary ingredient-level nutrition source**

**Supporting Evidence:**
- 1,014 unique foods (food_code PK verified)
- 39 per-100g nutrients covering macros, fatty acids, minerals, vitamins
- Per-serving nutrients for 92.9% of foods (82 rows missing — documented, not imputed)
- Primary source tracking: `asc_manual`, `fct_2017`, `ifct_2017`, `usda`, `calculated`
- Serving units recorded (tea cup, katori, piece, etc.)
- No negative nutrient values
- Indian context — foods relevant to recipe ingredients

**Required Transformations (Applied):**
- Renamed columns to standardized schema (see Data Dictionary §2)
- Flagged 82 rows with missing per-serving data (`missing_serving_data=true`)
- Computed `nutrient_completeness_100g` per food
- Preserved all original values — no imputation

**Limitations:**
- Only 1,014 foods — many recipe ingredients will not have direct matches
- Per-serving data missing for 8.1% — must fall back to per-100g with serving size estimation
- Some trace nutrients sparse (chromium, molybdenum, vitamin D, K, B7, B9)
- No cooked/prepared dish compositions — only raw ingredients and minimal preparations
- Licence terms for redistribution unclear — academic use assumed

---

### 3. USDA FoodData Central (FDC)

**Decision: CONDITIONAL USE — Manual gap-fill only**

**Conditions for Use:**
1. Only for ingredients **absent from INDB** after exhaustive mapping
2. **Manual curated mapping** required: recipe ingredient → FDC food_code (fdc_id)
3. **Never** automatic name-based or fuzzy matching
4. Document every mapping with confidence score and method
5. Nutrient units must be verified compatible (USDA uses same SI units)

**Rationale:**
- 87,990 US foods — comprehensive but wrong population context
- Different food varieties, fortification practices, nutrient profiles
- Composition database, not recipe database
- Public domain licence — no legal barrier

---

### 4. NHANES 2019-2020

**Decision: EXCLUDE from core recommendation pipeline**

**Rationale:**
- US civilian non-institutionalized population — not generalizable to Indian users
- Dietary recall data (DR1TOT) ≠ recipes; measures consumed nutrients, not dish compositions
- Health metrics (BMI, diabetes status) from different demographic/epidemiological context
- Survey weights and complex sampling design require specialized analysis

**Permitted Uses (Future Phases):**
- External validation of nutrient target ranges
- Epidemiological baseline comparison (with explicit caveats)
- Transfer learning experiments (Phase 4+) with domain adaptation

---

### 5. diet_recommendations_dataset.csv (Referenced in Requirements)

**Decision: EXCLUDE — Not in current dataset folder / Target leakage risk**

**Rationale:**
- Target variable derived from disease categories (e.g., "diabetes → diabetic diet")
- Using this for supervised training would leak disease labels into meal recommendations
- Circular reasoning: disease → diet label → recommend diet for disease
- Not a recipe dataset; no ingredient or nutrition composition data

**If Found Later:** Document and exclude with same rationale.

---

## Data Contracts Established

The following schemas are defined and validated (see Data Dictionary):

1. **Recipe Record** — `data/processed/recipes.parquet` (6,865 rows)
2. **Raw Food Composition Record** — `data/processed/indb_foods.parquet` (1,014 rows)
3. **Ingredient Record** — Schema defined for Phase 2 output
4. **Nutrient Record** — Schema defined for Phase 2 computed output
5. **User Profile** — Application schema (Phase 3)
6. **Recommendation Request** — Application schema (Phase 3)
7. **Meal Plan** — Application schema (Phase 3)

Controlled vocabularies established for: Cuisine (60+), Course (11), Diet (10), Nutrient IDs (30+).

---

## Reproducibility Artifacts Created

| Artifact | Location | Purpose |
|----------|----------|---------|
| Raw file hashes (MD5) | `docs/dataset_documentation/dataset_inventory.md` | Immutable raw data verification |
| Validation reports (JSON) | `data/interim/validation_reports/` | Automated quality gates |
| Preprocessing logs (JSON) | `data/interim/` | Full transformation audit trail |
| Excluded data archives | `data/interim/recipes_missing_ingredients.csv`, `recipes_condiments.csv` | No silent deletions |
| Processed datasets (Parquet + CSV) | `data/processed/` | Analysis-ready, schema-validated |
| Unit tests | `tests/test_phase1.py` | 44 tests covering all quality criteria |

---

## Unresolved Issues / Risks for Phase 2

| Issue | Impact | Mitigation |
|-------|--------|------------|
| Ingredient parsing from free text | High — needed for nutrition computation | Phase 2: NLP + rule-based parser; manual review of high-frequency ingredients |
| Recipe ingredient ↔ INDB food mapping | High — core linkage | Phase 2: Semi-automated mapping tool with human-in-the-loop |
| 35 condiment/prep recipes excluded from meal recs | Medium — loss of variety | Documented; available for ingredient substitution suggestions |
| 82 INDB foods missing per-serving data | Low — fallback to per-100g | Use serving_unit + typical portion estimation |
| INDB coverage gaps for recipe ingredients | High — many ingredients unmapped | Phase 2: Gap analysis; USDA conditional gap-fill; literature values |
| No licence for recipe source | Legal — redistribution risk | Academic capstone use; do not publish processed recipes publicly |

---

## Phase 1 Completion Criteria Met

✅ Dataset inventory with provenance, hashes, row/column counts
✅ Dataset quality report with per-column analysis
✅ Data dictionary with schemas, units, missing-value behaviour
✅ Data validation scripts (4 datasets, JSON reports)
✅ Reproducible preprocessing pipelines (2 datasets, logged)
✅ Unit tests (44 tests, all passing)
✅ Dataset suitability decisions documented
✅ No raw data modified; all exclusions archived with reason
✅ No missing values imputed; no fabricated data

---

## Approval for Phase 2

**Phase 1 Complete.** Ready to proceed to Phase 2: Ingredient Parsing & Nutrition Mapping.

**Next Phase Prerequisites:**
1. Ingredient NLP parser design (spaCy + custom rules)
2. Recipe ingredient ↔ INDB food mapping interface
3. Nutrition computation engine (ingredient weights → per-serving nutrients)
4. Baseline meal recommender design (content-based filtering on diet/course/cuisine)

---

*Signed: Lead Data Engineer*
*Date: 2026-11-15*