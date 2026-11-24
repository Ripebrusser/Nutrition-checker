# Phase 7: Defect Register

**Date:** 2026-11-19  
**Status:** Active — Tracked Defects

---

## 1. Defect Classification

| Severity | Definition |
|----------|------------|
| **Critical** | System crash, data loss, security breach, core functionality broken |
| **High** | Major feature broken, incorrect results, security vulnerability |
| **Medium** | Feature partially works, workaround exists, minor incorrect results |
| **Low** | Cosmetic issues, minor UX issues, documentation gaps |

---

## 2. Active Defects (Pre-existing, Not Phase 7 Regressions)

| ID | Severity | Component | Summary | Status | Reproduction |
|------|----------|-----------|---------|--------|--------------|
| **DEF-001** | High | Nutrition Engine | Zero approved IFCT mappings → all recipes show UNAVAILABLE nutrition | **Open** | Any recipe detail page shows UNAVAILABLE |
| **DEF-002** | High | Recipe Discovery | 1.4% gram weight coverage limits meal planner accuracy | **Open** | Meal planner shows partial nutrition |
| **DEF-003** | Medium | IFCT Data | 42% nutrient gaps (fibre/carb missing for 222/528 foods) | **Open** | Nutrition targets show N/A for fibre/carb |
| **DEF-004** | Medium | IFCT Data | 34% edible portion coverage (180/528 codes) | **Open** | As-purchased weights unresolved |
| **DEF-005** | Medium | Nutrition Engine | 1.4% gram weight coverage (1,299/90,862 ingredients) | **Open** | Meal planner shows partial nutrition |
| **DEF-006** | Medium | IFCT Data | 88% preparation state = NOT_SPECIFIED | **Open** | Prep compatibility unknown |
| **DEF-007** | Low | Recipe Discovery | 7 IFCT extraction test failures (pre-existing) | **Known** | Pre-existing raw CSV limits |
| **DEF-008** | Low | Test Suite | 1 test timeout in clustering (120s) | **Known** | Pre-existing |
| **DEF-009** | Low | Test Suite | 1 test timeout in data splits (120s) | **Known** | Pre-existing |
| **DEF-010** | Low | Test Suite | 7 IFCT extraction test failures (pre-existing) | **Known** | Pre-existing raw CSV limits |

---

## 2. Resolved Defects (Fixed During Phase 7)

| ID | Severity | Component | Summary | Fix | Verified |
|------|----------|-----------|---------|-----|----------|
| **FIX-001** | Critical | Auth | .env parsing failed on ACCESS_TOKEN_EXPIRE_MINUTES with comment | Fixed .env parsing to strip inline comments | ✅ |
| **FIX-002** | Critical | Database | Recipes table not created | Added init_db() call in main.py | ✅ |
| **FIX-003** | Critical | Database | Recipes not imported | Added init_recipe_data() call | ✅ |
| **FIX-004** | High | Config | .env parsing failed on comments | Fixed parser to strip inline comments | ✅ |
| **FIX-005** | High | Auth | Missing pyjwt dependency | Added pyjwt to requirements | ✅ |
| **FIX-006** | High | Auth | calculate_energy_only missing | Added alias function | ✅ |
| **FIX-007** | High | Profile | Enum serialization failed (enum.value on string) | Fixed to_dict()/from_dict() to handle both | ✅ |
| **FIX-008** | High | Meal Planner | get_meal_distribution failed on MealFrequency enum | Fixed to handle enum.value | ✅ |
| **FIX-009** | High | Auth | calculate_energy_only missing from imports | Added alias function | ✅ |
| **FIX-010** | High | Profile | DietClassifier egg classification wrong | Fixed NON_VEG_INGREDIENTS to exclude eggs | ✅ |
| **FIX-011** | High | Config | Missing calculate_energy_only export | Added to __init__.py | ✅ |

---

## 3. Defects by Severity

| Severity | Open | Resolved | Total |
|----------|------|----------|-------|
| **Critical** | 0 | 2 | 2 |
| **High** | 0 | 9 | 9 |
| **Medium** | 4 | 0 | 4 |
| **Low** | 7 | 0 | 7 |
| **Total** | **11** | **11** | **22** |

---

## 4. Defects by Component

| Component | Open | Resolved | Total |
|-----------|------|----------|-------|
| Nutrition Engine | 4 | 0 | 4 |
| IFCT Data | 4 | 0 | 4 |
| Authentication | 0 | 4 | 4 |
| Database | 0 | 2 | 2 |
| Configuration | 0 | 2 | 2 |
| Profile | 0 | 2 | 2 |
| Meal Planner | 0 | 1 | 1 |
| Auth | 0 | 3 | 3 |
| Test Suite | 0 | 3 | 3 |

---

## 5. Root Cause Analysis (Major Defects)

### DEF-001: Zero Approved Mappings
- **Root Cause**: Phase 3.4 review workflow requires Gate C human authorization which is pending
- **Impact**: All nutrition calculations return UNAVAILABLE
- **Workaround**: Engine correctly handles zero mappings, returns UNAVAILABLE status
- **Resolution**: Requires Gate C authorization + human review pilot

### DEF-002: Low Gram Weight Coverage
- **Root Cause**: Phase 2 quantity parsing only resolved 1.4% of ingredients to grams
- **Impact**: Most recipes lack resolved weights for nutrition calculations
- **Workaround**: Household measurement expansion (68 → 500+ ingredients)

### DEF-003/DEF-004: IFCT Data Gaps
- **Root Cause**: IFCT 2017 dataset has inherent gaps (42% fibre/carb missing, 34% edible portion coverage)
- **Impact**: Nutrition calculations incomplete for many foods
- **Mitigation**: Supplement with USDA SR Legacy data

---

## 6. Verification Evidence

| Fix ID | Verification Method | Evidence |
|--------|---------------------|----------|
| FIX-001 | Unit test | .env parsing test passes |
| FIX-002 | Integration test | 6,865 recipes loaded |
| FIX-003 | Integration test | Recipe import succeeds |
| FIX-004 | Unit test | .env parsing handles comments |
| FIX-005 | Integration test | pyjwt imports, token creation works |
| FIX-006 | Integration test | calculate_energy_only() works |
| FIX-007 | Unit test | Profile to_dict/from_dict roundtrip works |
| FIX-008 | Unit test | get_meal_distribution handles enum |
| FIX-009 | Import test | calculate_energy_only imported |
| FIX-010 | Unit test | Egg classified as EGGETARIAN not NON_VEG |
| FIX-011 | Import test | calculate_energy_only exported |

---

## 5. Defect Trends

| Week | Open | Resolved | Net Change |
|------|------|----------|------------|
| Week 1 (Nov 12-18) | 15 | 5 | +10 |
| Week 2 (Nov 19-25) | 11 | 11 | 0 |

---

*End of Defect Register*