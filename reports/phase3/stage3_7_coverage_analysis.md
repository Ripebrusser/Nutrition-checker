# Stage 3.7: Coverage Analysis Report

**Date:** 2026-11-19  
**Status:** Analysis Complete — Based on Current Data State (Zero Approved Mappings)

---

## 1. Executive Summary

This report analyzes the theoretical and projected coverage of the nutrition calculation engine. **No approved mappings exist**, so all measured coverage is currently zero. Projections are provided for post-pilot scenarios.

**Critical Distinction**: This report distinguishes between:
- **Measured coverage** (current state, zero mappings)
- **Projected coverage** (post-pilot estimates, clearly labeled)

---

## 2. Current Measured Coverage (Zero Mappings)

| Metric | Value | Denominator |
|--------|-------|-------------|
| Total recipes | 6,865 | — |
| Recipes with ≥1 approved mapping | **0** | 6,865 |
| Recipes with all ingredients mapped | **0** | 6,865 |
| Recipes with usable ingredient weights | **0** | 6,865 |
| Recipes with complete energy estimates | **0** | 6,865 |
| Recipes with complete protein estimates | **0** | 6,865 |
| Recipes with complete carbohydrate estimates | **0** | 6,865 |
| Recipes with complete fat estimates | **0** | 6,865 |
| Recipes with complete fibre estimates | **0** | 6,865 |
| Recipes with partial nutrition | **0** | 6,865 |
| Recipes with unavailable nutrition | **6,865** | 6,865 |

**All coverage metrics are 0% because zero approved mappings exist.**

---

## 3. Ingredient-Level Coverage (Current State)

### 3.1 Parsed Ingredient Records (Phase 2)
| Status | Count | Percentage |
|--------|-------|------------|
| Total ingredient records | 90,862 | 100% |
| RESOLVED (gram weight) | 1,299 | **1.4%** |
| RESOLVED_HOUSEHOLD | 1,337 | 1.5% |
| UNRESOLVED | 89,525 | 98.5% |

### 3.2 Review Units (Stage 2.3 Candidates)
| Metric | Value |
|--------|-------|
| Total review units (corrected key) | 7,992 |
| Auto-accepted (unverified) | 3 |
| Requiring human review | 7,989 |
| Approved mappings | 0 |

### 3.3 IFCT Nutrient Coverage
| Nutrient | Foods with Value | Missing | Coverage |
|----------|------------------|---------|----------|
| moisture_g | 528 | 0 | 100% |
| protein_g | 528 | 0 | 100% |
| ash_g | 528 | 0 | 100% |
| fat_g | 528 | 0 | 100% |
| fibre_total_g | 306 | 222 | 58% |
| fibre_insoluble_g | 306 | 222 | 58% |
| fibre_soluble_g | 306 | 222 | 58% |
| carb_available_g | 306 | 222 | 58% |
| energy_kj | 528 | 0 | 100% |

### 3.4 Edible Portion Factor Coverage
| Category | IFCT Codes Covered | Total IFCT Codes | Coverage |
|----------|-------------------|------------------|----------|
| All foods | ~180 | 528 | **34%** |

---

## 4. Projected Coverage Scenarios

### Scenario A: Post-Pilot (50 Units Reviewed)
| Metric | Projected |
|--------|-----------|
| Approved mappings | 50 |
| Recipes with ≥1 mapping | ~30-40 |
| Recipe mapping coverage | ~0.5% |
| Weight coverage (of mapped) | ~1.4% |

### Scenario B: Full Review Completion (7,992 Units)
| Metric | Projected (Optimistic) | Projected (Conservative) |
|--------|------------------------|--------------------------|
| Approved mappings | ~5,150 (65% accept rate) | ~3,200 (40% accept rate) |
| Unique ingredients mapped | ~1,800 | ~1,200 |
| Recipes with ≥1 mapping | ~5,500 (80%) | ~4,000 (58%) |
| Recipes with all ingredients mapped | ~2,500 (36%) | ~1,200 (17%) |
| Mapping coverage (ingredients) | ~65% | ~40% |

### Scenario C: Full Review + Weight Expansion
| Intervention | Weight Coverage | Recipe Nutrition Coverage |
|--------------|----------------|--------------------------|
| Current (1.4%) | 1.4% | <1% |
| +200 household conversions | ~5% | ~3% |
| +500 household conversions | ~12% | ~8% |
| +1,000 household conversions | ~25% | ~18% |
| +Piece weight database | ~40% | ~30% |

---

## 5. Nutrient-Specific Coverage Projections

### Post-Full-Review (Optimistic: 5,150 approved mappings)

| Nutrient | IFCT Coverage | Weight Coverage | Effective Coverage |
|----------|---------------|-----------------|-------------------|
| Energy | 100% | 1.4% | **1.4%** |
| Protein | 100% | 1.4% | **1.4%** |
| Fat | 100% | 1.4% | **1.4%** |
| Carbohydrate | 58% | 1.4% | **0.8%** |
| Total Fibre | 58% | 1.4% | **0.8%** |
| Moisture | 100% | 1.4% | **1.4%** |
| Ash | 100% | 1.4% | **1.4%** |

**Effective Coverage = IFCT Coverage × Weight Coverage**

**The 1.4% gram weight coverage is the primary bottleneck** — even with 100% mapping, only 1.4% of ingredients have resolved weights.

---

## 6. Coverage by Denominator

### 6.1 Ingredient-Level Coverage
| Denominator | Mapped | Coverage |
|-------------|--------|----------|
| Total ingredient records (90,862) | 0 | 0% |
| Review units (7,992) | 0 | 0% |
| Unique primary ingredients (2,725) | 0 | 0% |

### 6.2 Recipe-Level Coverage
| Denominator | With ≥1 Mapping | Fully Mapped | Coverage |
|-------------|-----------------|--------------|----------|
| Total recipes (6,865) | 0 | 0 | 0% |
| Recipes with ≥1 ingredient (6,865) | 0 | 0 | 0% |

### 6.3 Nutrient-Level Coverage (Per-Recipe)
| Nutrient | Recipes Complete | Recipes Partial | Recipes Unavailable |
|----------|-----------------|-----------------|---------------------|
| Energy | 0 | 0 | 6,865 |
| Protein | 0 | 0 | 6,865 |
| Fat | 0 | 0 | 6,865 |
| Carbohydrate | 0 | 0 | 6,865 |
| Fibre | 0 | 0 | 6,865 |

---

## 7. Bottleneck Analysis

| Bottleneck | Current | Impact | Mitigation |
|------------|---------|--------|------------|
| **Gram weight coverage** | 1.4% | **Primary** — limits all nutrient calculations | Expand household conversions (68 → 500+); piece weight DB |
| **IFCT nutrient gaps** | 42% missing fibre/carb | Secondary — limits carb/fibre completeness | Supplement with USDA SR Legacy |
| **Edible portion DB** | 34% of IFCT codes | Tertiary — requires factor for as-purchased weights | Expand from USDA/FAO; default 100% for dry goods |
| **Preparation state** | 88% NOT_SPECIFIED | Tertiary — compatibility unknown | Capture prep state in review; default "possibly compatible" |

---

## 8. Comparison: Mapping Coverage vs. Weight Coverage

| Stage | Mapping Coverage | Weight Coverage | Effective Nutrition Coverage |
|-------|-----------------|-----------------|------------------------------|
| Current | 0% | 1.4% | 0% |
| Post-Pilot (50) | ~0.5% | 1.4% | <0.1% |
| Full Review (Optimistic) | 65% | 1.4% | **1.4%** |
| Full Review + Weight Expansion | 65% | 25% | **16%** |

**Key Insight**: Mapping coverage alone is insufficient. Weight coverage must expand in parallel.

---

## 9. Coverage Definitions

| Metric | Definition | Denominator |
|--------|------------|-------------|
| **Ingredient Mapping Coverage** | Ingredients with approved mapping / Total ingredient records | 90,862 |
| **Recipe Mapping Coverage** | Recipes with ≥1 approved mapping / Total recipes | 6,865 |
| **Full Recipe Mapping Coverage** | Recipes with ALL ingredients mapped / Total recipes | 6,865 |
| **Gram Weight Coverage** | Ingredients with resolved gram weight / Total ingredient records | 90,862 |
| **Nutrient Completeness (per recipe)** | Ingredients contributing to nutrient / Mapped ingredients in recipe | Mapped ingredients |
| **Overall Recipe Completeness** | Mean nutrient completeness across 9 nutrients | — |

---

## 10. Limitations

1. **Projections are not measurements** — Based on acceptance rate assumptions, not actual review outcomes
2. **Weight coverage is the hard constraint** — Even perfect mapping yields ≤1.4% nutrition coverage without weight expansion
3. **IFCT gaps are structural** — 42% of foods lack fibre/carb; requires external supplementation
4. **NOT_SPECIFIED prep state** — 88% of units; compatibility assumed but not verified
5. **No cooked IFCT entries** — Cooked preparations cannot be matched

---

## 11. Conclusion

**Current measured coverage: 0% across all metrics** (zero approved mappings).

**Projected best-case after full review: 1.4% effective nutrition coverage** (limited by 1.4% gram weight coverage).

**To achieve meaningful nutrition coverage (>50%):**
1. Complete mapping review (~8,000 units)
2. Expand household conversions from 68 to 1,000+ ingredients
3. Build piece weight database for count-based quantities
4. Supplement IFCT fibre/carb gaps with USDA data

---

*End of Coverage Analysis Report*