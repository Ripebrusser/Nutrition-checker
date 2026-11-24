# Data Dictionary

**Project:** AI for Nutrition & Diet Planning
**Phase:** 1 — Dataset Validation and Preprocessing
**Version:** 1.0
**Date:** 2026-11-15

---

## 1. Recipe Record (Processed Schema)

*Target table: `data/processed/recipes.parquet`*

| Field | Type | Required | Unit / Constraints | Missing Behaviour | Source Column | Transform |
|-------|------|----------|-------------------|-------------------|---------------|-----------|
| recipe_id | int64 | ✅ | 1–6871 (original Srno) | Error if missing | Srno | Pass through |
| recipe_name_original | string | ✅ | Non-empty | Error if missing | RecipeName | Strip whitespace |
| recipe_name_en | string | ✅ | Non-empty | Error if missing | TranslatedRecipeName | Strip whitespace |
| ingredients_raw | string | ❌ | Comma-separated, qty embedded | **Drop row from recommender corpus**; log to `data/interim/recipes_missing_ingredients.csv` | Ingredients | Preserve original |
| ingredients_en | string | ❌ | Comma-separated, qty embedded | Same as above | TranslatedIngredients | Preserve translated |
| ingredients_parsed | list[dict] | ❌ | Structured: `[{"name": str, "qty": float, "unit": str, "notes": str}]` | Empty list if parsing fails | ingredients_en | NLP parsing (Phase 2) |
| prep_time_min | int64 | ✅ | ≥ 0 | Error if missing | PrepTimeInMins | Validate ≥ 0 |
| cook_time_min | int64 | ✅ | ≥ 0 | Error if missing | CookTimeInMins | Validate ≥ 0 |
| total_time_min | int64 | ✅ | = prep + cook | Error if inconsistent | TotalTimeInMins | Verify = prep + cook |
| servings | int64 | ✅ | ≥ 1 | Error if missing | Servings | Flag if > 50 as condiment |
| recipe_type | string | ✅ | Enum: `main`, `condiment`, `prep`, `beverage`, `dessert` | Default `main` | Derived from Course + Servings | Rule-based |
| cuisine | string | ✅ | Controlled vocabulary (see §4.1) | Map polluted values; default `Indian` | Cuisine | Standardize (§3.1) |
| course | string | ✅ | Controlled vocabulary (see §4.2) | Map polluted values; default `Main Course` | Course | Standardize (§3.1) |
| diet_labels | list[string] | ✅ | Subset of controlled vocab (see §4.3) | Default `[]` | Diet | Split if multi-label (currently single) |
| instructions_raw | string | ❌ | Free text | Preserve | Instructions | Preserve original |
| instructions_en | string | ❌ | Free text | Preserve | TranslatedInstructions | Preserve translated |
| source_url | string | ✅ | Valid HTTP URL | Error if missing | URL | Validate URL format |
| source_domain | string | ✅ | `archanaskitchen.com` | Derived | URL | Extract domain |
| scraped_at | datetime | ❌ | ISO 8601 | Null if unknown | — | Not in source; leave null |
| created_at | datetime | ✅ | ISO 8601 | Pipeline timestamp | — | Pipeline metadata |
| updated_at | datetime | ✅ | ISO 8601 | Pipeline timestamp | — | Pipeline metadata |

### 1.1 Missing Ingredients Rows (Excluded from Recommender Corpus)

| recipe_id | recipe_name_en | Reason |
|-----------|----------------|--------|
| 306 | Pear And Walnut Salad Recipe | No ingredient text |
| 1413 | Spinach and Cottage Cheese Eggless Ravioli Recipe | No ingredient text |
| 2072 | Thai Jasmine Sticky Rice Recipe | No ingredient text |
| 2098 | Classic Pavakkai Stir Fry Recipe | No ingredient text |
| 7894 | Urulaikizhangu Puli Thokku Recipe | No ingredient text |
| 8388 | Mashed Peas Recipe | No ingredient text |

*Saved to: `data/interim/recipes_missing_ingredients.csv`*

---

## 2. Raw Food Composition Record (INDB)

*Target table: `data/processed/indb_foods.parquet`*

| Field | Type | Required | Unit / Constraints | Missing Behaviour | Source Column |
|-------|------|----------|-------------------|-------------------|---------------|
| food_code | string | ✅ | Primary key (e.g., `ASC001`) | Error if missing | food_code |
| food_name | string | ✅ | Non-empty | Error if missing | food_name |
| primary_source | string | ✅ | Enum: `asc_manual`, `fct_2017`, `ifct_2017`, `usda`, `calculated` | Default `unknown` | primarysource |
| energy_kcal_100g | float64 | ❌ | kcal/100g | Null if missing | energy_kcal |
| energy_kj_100g | float64 | ❌ | kJ/100g | Null if missing | energy_kj |
| carbohydrate_g_100g | float64 | ❌ | g/100g | Null if missing | carb_g |
| protein_g_100g | float64 | ❌ | g/100g | Null if missing | protein_g |
| fat_g_100g | float64 | ❌ | g/100g | Null if missing | fat_g |
| free_sugar_g_100g | float64 | ❌ | g/100g | Null if missing | freesugar_g |
| fibre_g_100g | float64 | ❌ | g/100g | Null if missing | fibre_g |
| sfa_mg_100g | float64 | ❌ | mg/100g | Null if missing | sfa_mg |
| mufa_mg_100g | float64 | ❌ | mg/100g | Null if missing | mufa_mg |
| pufa_mg_100g | float64 | ❌ | mg/100g | Null if missing | pufa_mg |
| cholesterol_mg_100g | float64 | ❌ | mg/100g | Null if missing | cholesterol_mg |
| calcium_mg_100g | float64 | ❌ | mg/100g | Null if missing | calcium_mg |
| phosphorus_mg_100g | float64 | ❌ | mg/100g | Null if missing | phosphorus_mg |
| magnesium_mg_100g | float64 | ❌ | mg/100g | Null if missing | magnesium_mg |
| sodium_mg_100g | float64 | ❌ | mg/100g | Null if missing | sodium_mg |
| potassium_mg_100g | float64 | ❌ | mg/100g | Null if missing | potassium_mg |
| iron_mg_100g | float64 | ❌ | mg/100g | Null if missing | iron_mg |
| copper_mg_100g | float64 | ❌ | mg/100g | Null if missing | copper_mg |
| selenium_ug_100g | float64 | ❌ | µg/100g | Null if missing | selenium_ug |
| chromium_mg_100g | float64 | ❌ | mg/100g | Null if missing | chromium_mg |
| manganese_mg_100g | float64 | ❌ | mg/100g | Null if missing | manganese_mg |
| molybdenum_mg_100g | float64 | ❌ | mg/100g | Null if missing | molybdenum_mg |
| zinc_mg_100g | float64 | ❌ | mg/100g | Null if missing | zinc_mg |
| vitamin_a_ug_100g | float64 | ❌ | µg/100g | Null if missing | vita_ug |
| vitamin_e_mg_100g | float64 | ❌ | mg/100g | Null if missing | vite_mg |
| vitamin_d2_ug_100g | float64 | ❌ | µg/100g | Null if missing | vitd2_ug |
| vitamin_d3_ug_100g | float64 | ❌ | µg/100g | Null if missing | vitd3_ug |
| vitamin_k1_ug_100g | float64 | ❌ | µg/100g | Null if missing | vitk1_ug |
| vitamin_k2_ug_100g | float64 | ❌ | µg/100g | Null if missing | vitk2_ug |
| folate_ug_100g | float64 | ❌ | µg/100g | Null if missing | folate_ug |
| vitamin_b1_mg_100g | float64 | ❌ | mg/100g | Null if missing | vitb1_mg |
| vitamin_b2_mg_100g | float64 | ❌ | mg/100g | Null if missing | vitb2_mg |
| vitamin_b3_mg_100g | float64 | ❌ | mg/100g | Null if missing | vitb3_mg |
| vitamin_b5_mg_100g | float64 | ❌ | mg/100g | Null if missing | vitb5_mg |
| vitamin_b6_mg_100g | float64 | ❌ | mg/100g | Null if missing | vitb6_mg |
| vitamin_b7_ug_100g | float64 | ❌ | µg/100g | Null if missing | vitb7_ug |
| vitamin_b9_ug_100g | float64 | ❌ | µg/100g | Null if missing | vitb9_ug |
| vitamin_c_mg_100g | float64 | ❌ | mg/100g | Null if missing | vitc_mg |
| carotenoids_ug_100g | float64 | ❌ | µg/100g | Null if missing | carotenoids_ug |
| serving_unit | string | ❌ | e.g., `tea cup`, `katori`, `piece` | Null if missing | servings_unit |
| serving_energy_kcal | float64 | ❌ | kcal/serving | Null if missing (82 rows) | unit_serving_energy_kcal |
| serving_protein_g | float64 | ❌ | g/serving | Null if missing | unit_serving_protein_g |
| serving_fat_g | float64 | ❌ | g/serving | Null if missing | unit_serving_fat_g |
| serving_carb_g | float64 | ❌ | g/serving | Null if missing | unit_serving_carb_g |
| ... (36 more per-serving nutrients) | float64 | ❌ | Per-unit matching above | Null if missing | unit_serving_* |

**Note:** Per-serving nutrients have 82 missing rows (8.1%) — same rows across all per-serving columns. Do not impute.

---

## 3. Ingredient Record (Normalized, Phase 2 Output)

*Target table: `data/processed/ingredients.parquet`*

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| ingredient_id | string | ✅ | UUID v4 |
| recipe_id | int64 | ✅ | FK → Recipe.recipe_id |
| position | int64 | ✅ | Order in ingredient list (1-indexed) |
| name_raw | string | ✅ | Original text segment (e.g., `"2 tablespoon Gram flour (besan)"`) |
| name_en | string | ✅ | Translated segment |
| name_canonical | string | ❌ | Normalized ingredient name (e.g., `"gram flour"`) |
| qty | float64 | ❌ | Numeric quantity (e.g., `2.0`) |
| unit | string | ❌ | Normalized unit (e.g., `tablespoon`) |
| unit_g_equiv | float64 | ❌ | Grams per unit (from portion data) |
| notes | string | ❌ | Parenthetical notes (e.g., `"besan"`) |
| food_code_indb | string | ❌ | FK → INDB.food_code (manual mapping) |
| fdc_id | int64 | ❌ | FK → USDA FDC (manual mapping, gap-fill only) |
| match_confidence | float64 | ❌ | 0.0–1.0 (mapping confidence) |
| match_method | string | ❌ | `exact`, `fuzzy`, `manual`, `llm` |

---

## 4. Nutrient Record (Computed per Recipe)

*Target table: `data/processed/recipe_nutrients.parquet`*

| Field | Type | Required | Unit | Description |
|-------|------|----------|------|-------------|
| recipe_id | int64 | ✅ | — | FK → Recipe |
| nutrient_id | string | ✅ | — | Controlled vocab (see §4.4) |
| amount_per_serving | float64 | ✅ | Per nutrient unit | Computed from ingredient weights × composition |
| amount_per_100g | float64 | ✅ | Per nutrient unit | Normalized to 100g edible portion |
| computation_method | string | ✅ | — | `sum_ingredients`, `usda_gapfill`, `indb_direct` |
| missing_ingredients | int64 | ✅ | — | Count of ingredients without composition data |
| confidence | float64 | ✅ | 0.0–1.0 | Based on coverage & mapping quality |

---

## 5. User Profile Record

*Target table: `data/processed/user_profiles.parquet` (application data, not in current datasets)*

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| user_id | string | ✅ | UUID v4 | Primary key |
| age_years | int64 | ✅ | 1–120 | |
| gender | string | ✅ | Enum: `male`, `female`, `other` | |
| height_cm | float64 | ✅ | 50–250 | |
| weight_kg | float64 | ✅ | 20–300 | |
| bmi | float64 | ❌ | 10–60 | Derived: weight / (height/100)² |
| activity_level | string | ✅ | Enum: `sedentary`, `light`, `moderate`, `active`, `very_active` | |
| diet_preference | string | ❌ | Subset of recipe diet labels | Vegetarian, Vegan, etc. |
| cuisine_preferences | list[string] | ❌ | Subset of cuisine vocab | |
| allergies | list[string] | ❌ | Free text / controlled | |
| medical_conditions | list[string] | ❌ | Controlled: `diabetes`, `hypertension`, `ckd`, `celiac`, ... | |
| target_calories | int64 | ❌ | 800–5000 | Computed or user-set |
| target_macros | dict | ❌ | `{"protein_g": ..., "fat_g": ..., "carb_g": ...}` | |
| target_micros | dict | ❌ | Nutrient → target | RDA-based |
| created_at | datetime | ✅ | ISO 8601 | |
| updated_at | datetime | ✅ | ISO 8601 | |

---

## 6. Recommendation Request Record

*Target table: `data/processed/recommendation_requests.parquet`*

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| request_id | string | ✅ | UUID v4 |
| user_id | string | ✅ | FK → UserProfile |
| meal_type | string | ✅ | Enum: `breakfast`, `lunch`, `snack`, `dinner` |
| num_options | int64 | ✅ | 1–20 |
| dietary_constraints | list[string] | ❌ | Override profile |
| cuisine_preference | string | ❌ | Single cuisine filter |
| max_prep_time_min | int64 | ❌ | |
| max_cook_time_min | int64 | ❌ | |
| exclude_ingredients | list[string] | ❌ | |
| required_nutrients | dict | ❌ | e.g., `{"protein_g": {"min": 20}}` |
| context | dict | ❌ | Free-form (time of day, occasion, etc.) |
| timestamp | datetime | ✅ | ISO 8601 |

---

## 7. Meal Plan Record

*Target table: `data/processed/meal_plans.parquet`*

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| plan_id | string | ✅ | UUID v4 |
| user_id | string | ✅ | FK → UserProfile |
| date | date | ✅ | ISO 8601 date |
| meals | list[dict] | ✅ | `[{"meal_type": "breakfast", "recipe_id": 123, "servings": 1.5, "nutrients": {...}}, ...]` |
| total_nutrients | dict | ✅ | Aggregated across meals |
| targets_met | dict | ✅ | `{"calories": true, "protein": false, ...}` |
| generated_at | datetime | ✅ | ISO 8601 |
| model_version | string | ✅ | Semantic version of recommender |

---

## 8. Controlled Vocabularies

### 8.1 Cuisine (Standardized)
*Source: Recipe dataset Cuisine column after cleaning*

| Value | Canonical | Notes |
|-------|-----------|-------|
| Indian | Indian | Generic |
| North Indian | North Indian | |
| South Indian | South Indian | |
| Andhra | Andhra | |
| Bengali | Bengali | |
| Chettinad | Chettinad | |
| Goan | Goan | |
| Gujarati | Gujarati | |
| Hyderabadi | Hyderabadi | |
| Karnataka | Karnataka | |
| Kashmiri | Kashmiri | |
| Kerala | Kerala | |
| Maharashtrian | Maharashtrian | |
| Mughlai | Mughlai | |
| Punjabi | Punjabi | |
| Rajasthani | Rajasthani | |
| Tamil Nadu | Tamil Nadu | |
| ... | ... | 60+ regional cuisines |
| Continental | Continental | Western generic |
| Italian | Italian | |
| Chinese | Chinese | |
| Mexican | Mexican | |
| Thai | Thai | |
| ... | ... | 15+ international |

**Polluted values to remap:** `Appetizer`→Course, `Snack`→Course, `Side Dish`→Course, `Dessert`→Course, `Dinner`→Course, `Lunch`→Course, `Brunch`→Course, `World Breakfast`→Course

### 8.2 Course (Standardized)
*Source: Recipe dataset Course column after cleaning*

| Value | Canonical | Notes |
|-------|-----------|-------|
| Breakfast | Breakfast | Includes `North Indian Breakfast`, `South Indian Breakfast`, `Indian Breakfast`, `World Breakfast` |
| Brunch | Brunch | |
| Lunch | Lunch | |
| Dinner | Dinner | |
| Main Course | Main Course | |
| Side Dish | Side Dish | |
| Snack | Snack | |
| Appetizer | Appetizer | |
| Dessert | Dessert | |
| One Pot Dish | One Pot Dish | Valid descriptive course |
| Beverage | Beverage | New category for drinks |

**Polluted values to remap (from Course→Diet):** `Vegetarian`→Diet, `High Protein Vegetarian`→Diet, `Vegan`→Diet, `Non Vegetarian`→Diet, `Eggetarian`→Diet, `No Onion No Garlic (Sattvic)`→Diet, `Sugar Free Diet`→Diet

### 8.3 Diet Labels (Standardized)
*Source: Recipe dataset Diet column*

| Value | Canonical | Description |
|-------|-----------|-------------|
| Vegetarian | vegetarian | No meat/fish/eggs |
| Vegan | vegan | No animal products |
| Eggetarian | eggetarian | Vegetarian + eggs |
| Non Vegetarian | non_vegetarian | Contains meat/fish |
| High Protein Vegetarian | high_protein_vegetarian | Vegetarian, protein-focused |
| High Protein Non Vegetarian | high_protein_non_vegetarian | Non-veg, protein-focused |
| Diabetic Friendly | diabetic_friendly | Lower GI, controlled carbs |
| No Onion No Garlic (Sattvic) | sattvic | Jain/sattvic compliant |
| Gluten Free | gluten_free | No gluten grains |
| Sugar Free Diet | sugar_free | No added sugar |

### 8.4 Nutrient Identifiers (Standardized)

| nutrient_id | Display Name | Unit | Per 100g / Per Serving |
|-------------|--------------|------|------------------------|
| energy_kcal | Energy | kcal | Both |
| energy_kj | Energy | kJ | Both |
| protein_g | Protein | g | Both |
| fat_g | Total Fat | g | Both |
| carbohydrate_g | Carbohydrate | g | Both |
| fibre_g | Dietary Fibre | g | Both |
| free_sugar_g | Free Sugars | g | Both |
| sfa_g | Saturated Fat | g | Both |
| mufa_g | Monounsaturated Fat | g | Both |
| pufa_g | Polyunsaturated Fat | g | Both |
| cholesterol_mg | Cholesterol | mg | Both |
| calcium_mg | Calcium | mg | Both |
| iron_mg | Iron | mg | Both |
| magnesium_mg | Magnesium | mg | Both |
| phosphorus_mg | Phosphorus | mg | Both |
| potassium_mg | Potassium | mg | Both |
| sodium_mg | Sodium | mg | Both |
| zinc_mg | Zinc | mg | Both |
| copper_mg | Copper | mg | Both |
| selenium_ug | Selenium | µg | Both |
| vitamin_a_ug | Vitamin A (RAE) | µg | Both |
| vitamin_d_ug | Vitamin D | µg | Both |
| vitamin_e_mg | Vitamin E | mg | Both |
| vitamin_k_ug | Vitamin K | µg | Both |
| vitamin_b1_mg | Thiamin (B1) | mg | Both |
| vitamin_b2_mg | Riboflavin (B2) | mg | Both |
| vitamin_b3_mg | Niacin (B3) | mg | Both |
| vitamin_b6_mg | Vitamin B6 | mg | Both |
| vitamin_b12_ug | Vitamin B12 | µg | Both |
| folate_ug | Folate (B9) | µg | Both |
| vitamin_c_mg | Vitamin C | mg | Both |

---

## 9. Missing Value Behaviour Summary

| Entity | Field | Behaviour |
|--------|-------|-----------|
| Recipe | ingredients_raw/en | **Drop row from recommender corpus**; archive separately |
| Recipe | cuisine/course/diet | Remap polluted values; default to most frequent |
| Recipe | servings > 50 | Flag `recipe_type=condiment`; exclude from meal recs |
| INDB | Per-serving nutrients | Keep as null; do not impute; document 8.1% missing |
| INDB | Trace micronutrients | Keep as null; sparse by nature |
| USDA FDC | food_category_id | Ignore (not used) |
| USDA FDC | portion_description | Ignore (gram_weight present) |
| All | Primary keys | Error if missing (data integrity) |

---

## 10. Version Metadata

| Artifact | Version | Source Hash | Generated At |
|----------|---------|-------------|--------------|
| Raw Recipe XLSX | 1.0 | 889aa76ce87ba485422edb365234898d | — |
| Raw Recipe CSV | 1.0 | 898b74b2000ad8e152afbb769fb6e9ce | — |
| Raw INDB | 1.0 | f4db8039b33a6de9d6f602ee372aebab | — |
| Processed Recipes | 1.0 | — | Pipeline run |
| Processed INDB | 1.0 | — | Pipeline run |
| Data Dictionary | 1.0 | — | 2026-11-15 |

---

*This data dictionary is the contract for all downstream processing. Changes require version bump and schema migration.*