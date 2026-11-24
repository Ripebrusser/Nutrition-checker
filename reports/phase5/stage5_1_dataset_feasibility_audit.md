# Phase 5.1: Dataset Feasibility Audit

**Date:** 2026-11-18  
**Objective:** Audit existing datasets for ML feasibility

---

## 1. Dataset Inventory

| Dataset | Records | Key Features | Usability for ML |
|---------|---------|--------------|------------------|
| `recipes.parquet` | 6,865 recipes | recipe_id, name, cuisine (75 types), course (10 types), diet_labels (20 types), times, servings, ingredients_raw/en, instructions | High - structured metadata, cuisine/course labels |
| `indb_foods.parquet` | 1,014 foods | food_code, food_name, 50+ nutrient columns per 100g & per serving | High - complete nutrient profiles |
| `ifct_table1_candidate.parquet` | 528 foods | food_code, food_name, food_group (18 groups), 9 core nutrients (str format), moisture/protein/fat/ash/fibre/carb/energy | High - authoritative IFCT nutrient source |
| `normalized_ingredients.parquet` | 168,602 lines | recipe_id, source_ingredient, normalized_ingredient, synonym_applied, confidence, flags | Medium - ingredient normalization pipeline output |
| `parsed_recipe_ingredients.parquet` | 90,862 lines | recipe_id, ingredient_name, quantity, unit, preparation, gram_weight (sparse), parse_status, conversion_status | Medium-High - parsed quantities but 98.5% UNRESOLVED gram weights |
| `ifct_match_candidates.parquet` | 119,474 candidates | primary_ingredient, ifct_food_code, match_method, similarity_score, prep_state, food_group_compat, prep_state_compat, provisional_confidence | High - ingredient→IFCT mapping with confidence scores |
| `disambiguated_ingredients.parquet` | 90,862 rows | primary_ingredient, preparation_state, extracted_aliases, ambiguity_flags | Medium - ingredient disambiguation output |
| `unmatched_ingredients.parquet` | 63,244 lines | Ingredients with no IFCT match | Low - negative examples |

---

## 2. Data Quality Assessment

### 2.1 Completeness

| Dataset | Completeness | Key Gaps |
|---------|--------------|----------|
| Recipes | 100% (no nulls in 19 columns) | None |
| INDB Foods | High (serving_unit 97 nulls) | Serving data missing for ~10% |
| IFCT Final | High (fibre/carb 42% missing) | Fibre/carb only for foods with full table |
| Normalized Ingredients | High (synonym fields 55% null) | No synonym = no match found |
| Parsed Ingredients | Medium | gram_weight 98.5% null (UNRESOLVED) |
| IFCT Match Candidates | 100% (no nulls in 23 cols) | None |
| Disambiguated Ingredients | 100% | None |

### 2.2 Key Statistics

| Metric | Value |
|--------|-------|
| Recipes | 6,865 |
| Unique cuisines | 75 (Indian 1,157, Continental 1,020, North Indian 936, South Indian 681) |
| Unique courses | 10 (Lunch 1,764, Side Dish 993, Snack 877, Dinner 781, Breakfast 748) |
| Diet labels | 20 types (Vegetarian 4,696, High Protein Veg 699, Non-Veg 425) |
| Parsed ingredient lines | 90,862 (13.2 avg/recipe) |
| Unique ingredient names (parsed) | 13,049 |
| Gram weight coverage | 1.4% (1,299 / 90,862) |
| IFCT match candidates | 119,474 (7,992 unique review units) |
| IFCT food codes matched | 340 / 528 (64.4%) |
| Unmatched ingredients | 63,244 lines |

### 2.3 Match Quality Distribution

| Match Method | Count | % | Auto-accept eligible |
|--------------|-------|---|----------------------|
| EXACT | 7,583 | 6.3% | 4 candidates (3 review units) |
| SYNONYM | 5,035 | 4.2% | 0 |
| TOKEN_EQUIVALENT | 6,198 | 5.2% | 0 |
| TOKEN_SIMILARITY | 100,658 | 84.2% | 0 |
| **Total** | **119,474** | **100%** | **4 candidates (3 units)** |

**Auto-accept rate:** 0.003% (4 candidates, 3 unique review units)

---

## 3. Data Leakage and Invalid Assumptions Audit

### 3.1 Missing Labels (Critical for Supervised Learning)

| Required Label | Available? | Notes |
|----------------|------------|-------|
| User ratings (1-5 stars) | ❌ NO | No user interaction data |
| User meal selections/history | ❌ NO | No user behavior data |
| Verified portion sizes (grams) | ❌ 98.5% missing | Only 1,299 / 90,862 have gram_weight |
| Verified ingredient substitutions | ❌ NO | No substitution labels |
| User preference profiles | ❌ NO | No user data at all |
| Recipe health scores | ❌ NO | Diet labels exist but not validated nutrition |
| Portion size targets (grams) | ❌ NO | Servings only, no gram targets |

### 3.2 Data Leakage Risks

| Risk | Present? | Mitigation |
|------|----------|------------|
| Recipe ID in train/test split | Yes | Must split by recipe_id, not ingredient lines |
| Cuisine/course leakage | Yes | Stratify by cuisine/course |
| Ingredient overlap | High (13,049 unique names) | Recipe-level split mandatory |
| IFCT match info leakage | Yes | Match features derived from target mapping |
| Nutrition values as features + targets | Yes | Must not use IFCT nutrients to predict IFCT nutrients |

### 3.3 Invalid Assumptions to Avoid

| Assumption | Reality | Correction |
|------------|---------|------------|
| "We have user ratings" | No user data exists | Cannot do collaborative filtering |
| "Gram weights are available" | 98.5% missing | Must estimate or use household conversions |
| "IFCT mappings are ground truth" | 99.997% require review | Only 3 units auto-accepted; human review needed |
| "Portion sizes in grams exist" | Servings only, no grams | Must estimate from household measures |
| "User preferences exist" | No user data | Cannot personalize without user data |
| "Nutrient values are complete" | Fibre/carb 42% missing in IFCT | Must handle missing nutrients |

---

## 4. Nutrient Coverage Analysis

### IFCT Nutrient Availability (528 foods)

| Nutrient | Available | Missing | Notes |
|----------|-----------|---------|-------|
| energy_kj | 528 (100%) | 0 | Complete |
| protein_g | 528 (100%) | 0 | Complete |
| fat_g | 528 (100%) | 0 | Complete |
| moisture_g | 528 (100%) | 0 | Complete |
| ash_g | 528 (100%) | 0 | Complete |
| fibre_total_g | 306 (58%) | 222 (42%) | Only foods with full table |
| fibre_insoluble_g | 306 (58%) | 222 (42%) | Subset of fibre |
| fibre_soluble_g | 306 (58%) | 222 (42%) | Subset of fibre |
| carb_available_g | 306 (58%) | 222 (42%) | Subset of carb |

**Implication:** Cannot reliably train models on fibre/carb targets for all foods.

---

## 4. Summary: Dataset Feasibility Conclusion

| Aspect | Verdict |
|--------|---------|
| **Supervised learning with user labels** | ❌ NOT FEASIBLE - No user data |
| **Supervised learning with recipe labels** | ⚠️ PARTIAL - Cuisine/course/diet labels available |
| **Content-based recommendation** | ✅ FEASIBLE - Recipe + ingredient features available |
| **Nutritional constraint optimization** | ⚠️ PARTIAL - Nutrients available but gram weights missing |
| **Ingredient substitution** | ⚠️ PARTIAL - No substitution labels; can use similarity |
| **Recipe clustering** | ✅ FEASIBLE - Rich ingredient/cuisine features |
| **Portion prediction** | ❌ NOT FEASIBLE - No gram weight targets |
| **Personalized recommendation** | ❌ NOT FEASIBLE - No user data |

---

*End of Dataset Feasibility Audit*