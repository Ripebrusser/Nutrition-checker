# Phase 9: Preflight Report

**Date:** 2026-11-20  
**Status:** Preflight Complete — Ready for Phase 9 Execution

---

## 1. Repository State Summary

### 1.1 Existing Application Structure

The project already has a fully functional Streamlit application with a comprehensive backend:

| Component | Location | Status |
|-----------|----------|--------|
| **Streamlit App** | `app/main.py` | Complete (12 pages) |
| **Nutrition Engine** | `src/nutrition/` | Phase 3.6 Complete |
| **Review Workflow** | `src/review/`, `app/ingredient_review_app.py` | Phase 3.4 Complete |
| **Recommendation Engine** | `src/recommendation/` | Phase 5.1–5.3 Complete |
| **Personalization** | `src/personalization/` | Phase 4 Complete |
| **Data Preprocessing** | `src/preprocessing/`, `src/ingredients/` | Phase 1–2 Complete |

### 1.2 Existing Pages (Streamlit)

| Page | Path | Auth Required |
|------|------|---------------|
| Home | `/` | No |
| Login | `/login` | No |
| Register | `/register` | No |
| Dashboard | `/dashboard` | Yes |
| Profile | `/profile` | Yes |
| Nutrition Targets | `/nutrition_targets` | Yes |
| Recipes | `/recipes` | Yes |
| Recipe Detail | `/recipe_detail` | Yes |
| Recommendations | `/recommendations` | Yes |
| Meal Planner | `/meal_planner` | Yes |
| Meal Plan Detail | `/meal_plan_detail` | Yes |
| Nutrition Breakdown | `/nutrition_breakdown` | Yes |
| Preferences | `/preferences` | Yes |
| History | `/history` | Yes |

---

## 2. Dataset Inventory (Frozen, Hash-Verified)

| # | File | SHA-256 | Records | Status |
|---|------|---------|---------|--------|
| 1 | `normalized_ingredients.parquet` | `08710983213938c3fecafd20991ab7d3d7fe51b179303bbe4dc93b2ac1b1b6e5` | 90,862 | ✅ |
| 2 | `parsed_recipe_ingredients.parquet` | `e17b668b208dac4a7240cbfb27d78caac6123bc2b29b34a70aeb38964b9e86d9` | 90,862 | ✅ |
| 3 | `ingredient_synonyms.csv` | `22b8aace1ef29ea271051004a0e5a79ac8a8bfb5d80b8f796abe0db1f2ee4b31` | 1,200+ | ✅ |
| 4 | `household_measurements.csv` | `451fb9c6d5135e0684bd5e6445aeaadfafa2951db6ae7fd939b96faad1e16b47` | 68 | ✅ |
| 5 | `ifct_table1_candidate.parquet` | `294c6fc4d095a47e13fbe02e8e3c1c0c8175752966275a3415f9a7df04774f35` | 528 | ✅ |
| 6 | `ifct_match_candidates.parquet` | `2bb9f0d7770f7669ad3cd30f49d2a15f820f572e53690678f58891229336740f` | 119,474 | ✅ |
| 7 | `unmatched_ingredients.parquet` | `4d4e2b84e3b3323552c600bf90eefba81c5e44ee8f455298f331c190ced08102` | 63,244 | ✅ |
| 8 | `household_measurements.csv (S2.3)` | `4c169cba077c49f384e699129e9051929ad130dda2221ac2692cf9c34e04567e` | 68 | ✅ |

**All 8 frozen dataset hashes match. ✅**

---

## 3. Existing Backend Services

### 3.1 Nutrition Engine (`src/nutrition/`)
- **NutrientCalculator** — Core calculation engine
- **StrictMappingInterface** — Only approved IFCT mappings
- **RecipeAggregator** — Recipe-level nutrient aggregation
- **EdiblePortionCalculator** — ~180 IFCT codes with edible portion factors
- **CoverageAnalyzer** — Nutrient coverage reporting

### 3.2 Personalization (`src/personalization/`)
| Module | Purpose |
|--------|---------|
| `profile_models.py` | User profile data models |
| `profile_validation.py` | Profile validation logic |
| `profile_repository.py` | Profile persistence |
| `user_profile.py` | High-level profile management |
| `reference_values.py` | ICMR 2020 RDA, PAL factors, etc. |
| `energy_requirements.py` | BMR/TDEE calculations (Mifflin-St Jeor) |
| `macro_targets.py` | Macro distribution (ICMR, High Protein, Low Carb, Keto) |
| `nutrition_targets.py` | Orchestration layer |
| `dietary_constraints.py` | Dietary classification, allergen filtering |
| `recipe_profile.py` | Recipe nutrition profiles |
| `personalized_recommender.py` | Personalized recommendation engine |
| `meal_planner.py` | Meal planning engine |
| `meal_plan_optimizer.py` | Local search optimizer |
| `meal_plan_validation.py` | Validation engine |
| `meal_plan_models.py` | Meal plan data models |
| `explanation_engine.py` | Explanation generation |

### 3.3 Recommendation Engine (`src/recommendation/`)
| Component | Purpose |
|-----------|---------|
| `ContentBasedRecipeRecommender` | TF-IDF + metadata similarity |
| `RecipePreprocessor` | Data loading & preprocessing |
| `RecipeFeatureExtractor` | TF-IDF + metadata encoding |
| `baseline_recommenders` | Cuisine, Jaccard, Random baselines |
| `evaluation` | Precision, Recall, Diversity, Coverage |
| `clustering_features` | Clustering for diversity |

---

## 4. Dataset Inventory

### 4.1 Recipe Dataset
| Metric | Value |
|--------|-------|
| Total recipes | 6,865 |
| Columns | 19 (recipe_id, recipe_name_en, cuisine, course, diet_labels, prep/cook times, servings, etc.) |
| Cuisine types | 75 |
| Course types | 10 |
| Diet labels | 20 (pipe-separated) |
| Recipe types | 3 (veg, non-veg, eggetarian) |

### 4.2 Ingredient Data
| Metric | Value |
|--------|-------|
| Canonical ingredient records | 90,862 |
| Unique primary ingredients | 2,725 |
| Gram weight coverage | 1.4% (1,299/90,862) |
| Household conversion coverage | 1.5% (1,337/90,862) |
| Unresolved | 98.5% (89,525/90,862) |

### 4.3 IFCT Nutrition Data
| Metric | Value |
|--------|-------|
| Food records | 528 |
| Food groups | 18 |
| Nutrients per 100g edible | 9 (moisture, protein, ash, fat, fibre_total, fibre_insoluble, fibre_soluble, carb_available, energy_kJ) |
| Missing nutrients (fibre/carb) | 42% (222/528) |
| Edible portion factors | ~180/528 codes (34%) |

### 4.4 Mapping Status
| Metric | Value |
|--------|-------|
| Review units (corrected key) | 7,992 |
| Auto-accepted (unverified) | 3 |
| Requiring human review | 7,989 |
| **Approved mappings** | **0** |
| Gate C authorization | **PENDING** |

---

## 3. Existing Interface Contracts

### 3.1 Nutrition Engine (`src/nutrition/`)
**Key Input:**
```python
IngredientNutritionInput(
    recipe_id, ingredient_record_id, original_ingredient, normalized_ingredient,
    ifct_food_code, ifct_food_name, ifct_food_group,
    mapping_status=MappingStatus.APPROVED,  # ONLY approved mappings
    preparation_state, edible_weight_g, nutrient_values, source_provenance
)
```

**Key Output:**
```python
IngredientNutritionOutput(
    calculated_nutrients: Dict[str, float],
    missing_nutrients: List[str],
    calculation_status: CalculationStatus,    # COMPLETE/PARTIAL/MISSING_*
    provenance: Dict
)
```

### 3.2 Recommendation Engine (`src/recommendation/`)
**ContentBasedRecipeRecommender:**
- `fit(recipe_ingredients, recipe_metadata)`
- `recommend(query_recipe_id, k, filters)` — filters: cuisine, course, diet_labels
- `recommend_by_ingredients(ingredients, k, filters)`
- Returns `RecommendationResult` with component_scores, explanation, shared_ingredients

**RecipePreprocessor:**
- `get_recipe_ingredient_mapping()` → Dict[recipe_id, List[normalized_ingredient]]
- `get_recipe_metadata_mapping()` → Dict[recipe_id, Dict[cuisine, course, diet_labels, ...]]

### 3.3 Personalization (`src/personalization/`)
- `PersonalizedRecommender` — wraps base recommender with dietary constraints + nutrition targets
- `DietaryConstraintEngine` — VEGAN, VEGETARIAN, EGGETARIAN, JAIN, allergens, exclusions
- `MealPlanner` — Daily/weekly meal plans with variety controls
- `MealPlanOptimizer` — Local search optimizer
- `MealPlanValidator` — Safety, adequacy, variety checks
- `ExplanationEngine` — Traceable explanations with provenance

---

## 5. Current Limitations (Must Not Be Concealed)

| Limitation | Impact on Phase 9 |
|------------|-------------------|
| **Zero approved mappings** | Nutrition engine returns `UNAVAILABLE` for all recipes; UI must show UNAVAILABLE states |
| **1.4% gram weight coverage** | Most recipes lack resolved weights; meal planner shows partial nutrition |
| **42% IFCT nutrient gaps** | Fibre/carb missing for 222/528 foods |
| **34% edible portion coverage** | ~180/528 IFCT codes have factors |
| **No user auth in current app** | Need to implement registration/login |
| **Gate C PENDING** | No approved mappings until human review completes |

---

## 6. Test Baseline (Pre-Phase 9)

| Test Suite | Tests | Status |
|------------|-------|--------|
| Phase 3 Review (`test_review_app.py`) | 30 | ✅ PASS |
| Phase 3 Nutrition (`test_nutrition_calculator.py`) | 42 | ✅ PASS |
| Phase 2 Regression | 54 | ✅ PASS |
| Phase 5 Recommendation | 127 | 126 PASS, 1 timeout (pre-existing) |
| Phase 4 Personalization | 37 | ✅ PASS |
| Phase 3 Nutrition Engine | 42 | ✅ PASS |
| Phase 3 Review Workflow | 30 | ✅ PASS |
| **Total Independent** | **72** | **72 PASS** |

---

## 6. Implementation Plan for Phase 9

### Phase 9.1: Project Setup & Configuration
- [ ] Create frontend project (React + Vite + TypeScript + Tailwind)
- [ ] Create FastAPI backend structure
- [ ] Configure development environment
- [ ] Set up database models (SQLAlchemy + SQLite)

### Phase 9.2: Backend API Development
- [ ] Authentication API (register, login, logout, JWT)
- [ ] User profile CRUD API
- [ ] Nutrition targets API
- [ ] Recipe search & discovery API
- [ ] Personalized recommendations API
- [ ] Meal planner CRUD API
- [ ] Saved recipes API
- [ ] Meal plan CRUD API
- [ ] Nutrition breakdown API

### Phase 9.3: Frontend Development
- [ ] Project setup (React + Vite + TypeScript + Tailwind)
- [ ] Authentication pages (Login, Register)
- [ ] Dashboard page
- [ ] Profile management page
- [ ] Nutrition targets page
- [ ] Recipe discovery & search
- [ ] Recipe detail page
- [ ] Personalized recommendations page
- [ ] Meal planner (daily/weekly)
- [ ] Meal plan detail view
- [ ] Nutrition breakdown page
- [ ] Preferences/settings page
- [ ] History page
- [ ] Saved recipes page

### Phase 9.4: Integration & Testing
- [ ] Connect frontend to backend API
- [ ] End-to-end user journey testing
- [ ] Regression testing
- [ ] Performance testing

### Phase 9.5: Documentation & Deployment
- [ ] Create Phase 9 reports
- [ ] Create deployment guide
- [ ] Update main README

---

## 6. Key Limitations (Must Not Be Concealed)

| Limitation | Impact on Phase 9 |
|------------|-------------------|
| **Zero approved mappings** | Nutrition engine returns `UNAVAILABLE` for all recipes; UI must show UNAVAILABLE states |
| **1.4% gram weight coverage** | Most recipes lack resolved weights; meal planner shows partial nutrition |
| **42% IFCT nutrient gaps** | Fibre/carb missing for 222/528 foods |
| **34% edible portion coverage** | ~180/528 IFCT codes have factors |
| **No user auth in current app** | Need to implement registration/login |
| **Gate C PENDING** | No approved mappings until human review completes |

---

## 7. Technology Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.x | UI framework |
| Vite | 5.x | Build tool |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 3.x | Styling |
| Recharts | 2.x | Charts |
| Lucide React | Latest | Icons |
| React Router | 6.x | Routing |
| TanStack Query | 5.x | Data fetching |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Runtime |
| FastAPI | 0.109+ | API framework |
| SQLAlchemy | 2.0 | ORM |
| SQLite | 3.x | Local database |
| Pydantic | 2.x | Validation |
| bcrypt | 4.x | Password hashing |
| python-jose | 3.3 | JWT tokens |

---

## 6. Integration Boundaries

| Phase 9 Component | Consumes From | Provides To |
|-------------------|---------------|-------------|
| Frontend | Backend API | User interactions |
| Backend API | Phase 3 Nutrition, Phase 4 Personalization, Phase 5 Recs | API responses |
| Phase 3 Nutrition | IFCT data | Nutrient calculations |
| Phase 4 Personalization | User profiles, nutrition targets | Dietary constraints, meal plans |
| Phase 5 Recommendations | Recipe features, TF-IDF | Recommendations |
| Phase 3.4 Review | IFCT mappings | Approved mappings |

---

## 7. Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Zero approved mappings | Nutrition unavailable | High | High | Document clearly; Gate C path |
| Low weight coverage | Incomplete meal nutrition | High | High | Document; plan household expansion |
| No approved mappings | Nutrition engine returns UNAVAILABLE | High | High | Clear UI messaging |
| No existing auth | Must build from scratch | High | Medium | Use proven libraries |
| Data persistence | SQLite reliability | Low | Low | SQLite WAL mode |

---

## 7. Files Created/Modified

### New Files to Create
| File | Purpose |
|------|---------|
| `frontend/` | React + Vite project |
| `backend/` | FastAPI application |
| `reports/phase9/phase9_preflight_report.md` | This report |
| `reports/phase9/phase9_architecture_report.md` | Architecture document |
| `reports/phase9/phase9_frontend_report.md` | Frontend implementation report |
| `reports/phase9/phase9_backend_report.md` | Backend implementation report |
| `reports/phase9/phase9_local_storage_report.md` | Local storage design |
| `reports/phase9/phase9_testing_report.md` | Testing results |
| `reports/phase9/phase9_final_validation.md` | Final validation report |
| `start_website.bat` | Windows startup script |
| `README.md` | Updated with new instructions |

### Existing Files to Reuse (No Modification)
| File | Purpose |
|------|---------|
| `src/nutrition/*` | Nutrition engine (reuse) |
| `src/personalization/*` | Personalization engine (reuse) |
| `src/recommendation/*` | Recommendation engine (reuse) |
| `src/nutrition/*` | Nutrition engine (reuse) |
| `src/review/` | Review workflow (reuse) |
| `src/preprocessing/*` | Data preprocessing (reuse) |
| `src/ingredients/*` | Ingredient processing (reuse) |
| `src/matching/*` | Ingredient matching (reuse) |
| `data/` | All frozen datasets (read-only) |

---

## 7. Acceptance Criteria

Phase 9 is complete only when:

1. ✅ Website builds successfully
2. ✅ Backend starts successfully
3. ✅ Frontend connects to backend
3. ✅ All main pages work (10 pages)
4. ✅ Existing Python ML functionality is reused
4. ✅ User data persists locally (SQLite)
5. ✅ Meal plans persist after restart
6. ✅ Recipe discovery uses actual 6,865-recipe dataset
7. ✅ Dietary restrictions are enforced (hard constraints)
8. ✅ Nutrition limitations displayed honestly
9. ✅ Responsive design (desktop + mobile)
9. ✅ No critical errors

---

## 8. Final Verdict

**Phase 9 Preflight: ✅ COMPLETE — Ready for Implementation**

All prerequisites verified. Existing Python ML/nutrition stack is reusable. Phase 9 implementation can proceed.

---

*End of Preflight Report*