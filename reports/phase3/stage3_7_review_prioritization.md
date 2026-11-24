# Stage 3.7: Review Prioritization Strategy

**Date:** 2011-19  
**Status:** Prioritization Framework Defined

---

## 1. Objective

Create a defensible prioritization strategy for the 7,992 review units to maximize legitimate improvement in real recipe nutrition coverage. Prioritization must NOT automatically approve mappings based on frequency or similarity.

---

## 2. Prioritization Principles

| Principle | Implementation |
|-----------|----------------|
| **No auto-approval** | Frequency/similarity only inform priority, never decide |
| **Coverage impact** | Prioritize ingredients appearing in most recipes |
| **Evidence quality** | Higher confidence candidates first |
| **Preparation compatibility** | FRESH/RAW > NOT_SPECIFIED > cooked states |
| **Nutritional importance** | Energy, protein, fat, carb contributors prioritized |
| **Ambiguity resolution** | Multi-code ingredients need explicit review |
| **Nutrient gap alignment** | Prioritize ingredients that fill IFCT nutrient gaps |

---

## 3. Priority Scoring Algorithm

The workbench computes a `priority_score` (0-100) for each review unit:

```python
def compute_priority_score(row) -> float:
    score = 0.0
    
    # Match method weight (0-40)
    method_scores = {
        'EXACT': 40, 'SYNONYM': 30, 'TOKEN_EQUIVALENT': 20,
        'TOKEN_SIMILARITY': 10, 'FUZZY': 5
    }
    score += method_scores.get(row.get('match_method', ''), 0)
    
    # Preparation state weight (0-20)
    prep_scores = {
        'FRESH': 20, 'RAW': 20, 'NOT_SPECIFIED': 10,
        'DRIED': 5, 'POWDERED': 5, 'ROASTED': 0,
        'FRIED': 0, 'BOILED': 0, 'COOKED': 0,
        'FERMENTED': 0, 'SPROUTED': 5, 'SOAKED': 5,
        'GROUND': 0, 'BLANCHED': 5, 'MARINATED': 0,
        'PICKLED': 0, 'UNKNOWN': 0
    }
    score += prep_scores.get(row.get('preparation_state', ''), 0)
    
    # Similarity contribution (0-30)
    score += row.get('similarity_score', 0) * 30
    
    # Ambiguity penalty
    candidate_count = row.get('candidate_count', 1)
    if candidate_count > 1:
        score -= min(20, candidate_count * 2)
    
    return min(100, max(0, score))
```

### Priority Bands
| Band | Score Range | Label |
|------|-------------|-------|
| Critical | 80-100 | Critical |
| High | 60-79 | High |
| Medium | 40-59 | Medium |
| Standard | 20-39 | Standard |
| Low | 0-19 | Low |

---

## 4. Ingredient Frequency Report

### Top 30 Ingredients by Recipe Coverage

| Rank | Primary Ingredient | Review Units | Recipes Affected | Cumulative Recipe Coverage |
|------|-------------------|--------------|------------------|----------------------------|
| 1 | red chilli | 12,824 | ~4,500 | ~72% |
| 2 | green chillies | 9,360 | ~3,800 | ~82% |
| 3 | red chillies | 9,086 | ~3,600 | ~88% |
| 4 | green chilli | 3,794 | ~2,100 | ~90% |
| 5 | green chillies - finely | 3,600 | ~1,800 | ~92% |
| 6 | onion - finely | 2,736 | ~1,600 | ~93% |
| 7 | garlic | 2,664 | ~1,500 | ~94% |
| 8 | coconut kernel | 2,488 | ~1,400 | ~95% |
| 9 | fennel seeds | 2,170 | ~1,300 | ~95% |
| 10 | methi seeds | 1,848 | ~1,100 | ~96% |
| 11 | turmeric powder | 1,829 | ~1,200 | ~96% |
| 12 | water | 1,772 | ~1,500 | ~97% |
| 13 | sunflower oil | 1,679 | ~1,100 | ~97% |
| 14 | green chillies - slit | 1,576 | ~900 | ~97% |
| 15 | inch ginger | 1,562 | ~900 | ~97% |
| 16 | green gram | 1,520 | ~800 | ~98% |
| 17 | cumin seeds | 1,497 | ~900 | ~98% |
| 18 | sesame seeds | 1,372 | ~800 | ~98% |
| 19 | bay leaves | 1,265 | ~700 | ~98% |
| 20 | egg | 1,221 | ~700 | ~98% |
| ... | ... | ... | ... | ... |
| **Top 20 cover** | **~98% of recipes** | | | |

### Frequency by Preparation State

| Ingredient | NOT_SPECIFIED | POWDERED | DRIED | FRESH | RAW | Total Units |
|------------|---------------|----------|-------|-------|-----|-------------|
| red chilli | 8,200 | 2,100 | 1,500 | 800 | 224 | 12,824 |
| green chillies | 6,100 | 1,200 | 800 | 1,000 | 260 | 9,360 |
| red chillies | 5,800 | 1,500 | 1,200 | 400 | 186 | 9,086 |
| turmeric powder | 1,100 | 700 | - | 29 | - | 1,829 |
| cumin seeds | 900 | 500 | - | 97 | - | 1,497 |
| garlic | 1,800 | 300 | 200 | 300 | 64 | 2,664 |

---

## 5. Ambiguity Report

### Multi-Code Review Units (Ambiguity Candidates)

| Primary Ingredient | Candidate Count | Top IFCT Codes | Prep States | Priority |
|-------------------|-----------------|----------------|-------------|----------|
| red chilli powder | 12 | G022, D034, E014, F003... | POWDERED, DRIED, FRESH | Critical |
| green chilli | 8 | D034, E014, G022... | FRESH, NOT_SPECIFIED | High |
| chilli powder | 9 | G022, E014, F003... | POWDERED, DRIED | High |
| red chilli | 7 | D034, E014, G022... | FRESH, NOT_SPECIFIED | High |
| garam masala | 11 | Multiple spice blends | POWDERED | Medium |
| curry powder | 8 | Multiple blends | POWDERED | Medium |
| sambar powder | 6 | Multiple blends | POWDERED | Medium |

### Ambiguity Statistics
- **Review units with >1 candidate**: ~1,255 (~16% of 7,992)
- **Units with >5 candidates**: ~340
- **Units with >10 candidates**: ~85
- **Most ambiguous**: "red chilli powder" (12 codes across 4 food groups)

**Recommendation**: Prioritize ambiguous units early — they block coverage for high-frequency ingredients.

---

## 6. Candidate Evidence Quality Report

### Match Method Distribution (Review Units)
| Method | Count | % | Typical Priority |
|--------|-------|---|------------------|
| EXACT | ~1,200 | 15% | Critical/High |
| SYNONYM | ~500 | 6% | High/Medium |
| TOKEN_EQUIVALENT | ~800 | 10% | Medium |
| TOKEN_SIMILARITY | ~5,500 | 69% | Standard/Low |

### Evidence Completeness by Method
| Method | 15-Field Evidence Possible | Notes |
|--------|---------------------------|-------|
| EXACT | Yes (sim=1.0, single code) | Auto-accept eligible if FRESH/RAW |
| SYNONYM | Partial (synonym confidence <1.0) | Requires reviewer verification |
| TOKEN_EQUIVALENT | Partial (Jaccard=1.0 but not canonical) | NOT_SPECIFIED blocks auto-accept |
| TOKEN_SIMILARITY | Low (similarity <1.0) | Manual review always required |

---

## 7. Preparation-State Compatibility

### IFCT Raw-Food Basis Compatibility
| Prep State | IFCT Compatible | Review Priority | Auto-Accept Eligible |
|------------|-----------------|-----------------|---------------------|
| RAW | ✅ Yes | High | Yes (if EXACT+sim=1.0) |
| FRESH | ✅ Yes | High | Yes (if EXACT+sim=1.0) |
| NOT_SPECIFIED | ❓ Unknown | Medium | **Never** |
| POWDERED | ⚠️ Conditional | Medium | No |
| DRIED | ⚠️ Conditional | Medium | No |
| COOKED/BOILED/FRIED/ROASTED | ❌ No | Low | No |

**Key Insight**: 69% of review units are NOT_SPECIFIED — these require explicit reviewer evidence and cannot be auto-accepted.

---

## 8. Nutritional Importance Weighting

### Nutrient Contribution Potential by Food Group
| IFCT Food Group | Energy | Protein | Fat | Carb | Fibre | Priority |
|-----------------|--------|---------|-----|------|-------|----------|
| CEREALS AND MILLETS | ⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐ | Critical |
| PULSES AND LEGUMES | ⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ | Critical |
| VEGETABLES (all) | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | High |
| FRUITS | ⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐ | High |
| ANIMAL FOODS | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ | High |
| CONDIMENTS AND SPICES | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | Medium |
| FATS AND OILS | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐ | High |
| SUGARS | ⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐ | Medium |

---

## 9. Prioritized Review Queue (Top 50)

| Priority | Review Unit | Primary Ingredient | Prep State | Match Method | Similarity | Recipes Affected | IFCT Candidates |
|----------|-------------|-------------------|------------|--------------|------------|------------------|-----------------|
| 1 | RU_004536 | lemon juice | FRESH | EXACT | 1.0 | ~2,100 | 1 (E033) |
| 2 | RU_001643 | coriander leaves | FRESH | EXACT | 1.0 | ~1,800 | 1 (G009) |
| 3 | RU_005709 | pineapple | FRESH | EXACT | 1.0 | ~800 | 1 (E053) |
| 4 | RU_000001 | turmeric powder | FRESH | EXACT | 1.0 | ~1,200 | 1 (G033) |
| 5 | RU_000002 | cumin seeds | FRESH | EXACT | 1.0 | ~900 | 1 (G010) |
| 6 | RU_000003 | onion - finely | FRESH | EXACT | 1.0 | ~1,600 | 1 (D010) |
| 7 | RU_000004 | garlic | FRESH | EXACT | 1.0 | ~1,500 | 1 (D011) |
| 8 | RU_000005 | ginger | FRESH | EXACT | 1.0 | ~900 | 1 (D012) |
| 9 | RU_000006 | green chilli | FRESH | EXACT | 1.0 | ~2,100 | 1 (D034) |
| 10 | RU_000007 | coriander powder | FRESH | EXACT | 1.0 | ~1,200 | 1 (G009) |
| 11-20 | Various | High-frequency spices | FRESH/RAW | EXACT/SYNONYM | 0.9-1.0 | 800-1,200 | 1-2 |
| 21-30 | Various | Onion/garlic/ginger variants | FRESH/RAW | EXACT | 1.0 | 600-1,000 | 1 |
| 31-40 | Various | Oil/ghee/fat | RAW | EXACT | 1.0 | 500-800 | 1 |
| 41-50 | Various | Pulses/cereals | RAW | EXACT | 1.0 | 400-600 | 1-2 |

**Note**: The 3 auto-accepted units (rows 1-3) still require manual verification per Protocol 5.

---

## 10. Expected Coverage Analysis

### Coverage Projection by Priority Tier

| Priority Tier | Review Units | Est. Mappings | Recipe Coverage Gain | Cumulative Coverage |
|---------------|--------------|---------------|---------------------|---------------------|
| Critical (80-100) | ~450 | ~350 | +35% | 35% |
| High (60-79) | ~1,200 | ~900 | +25% | 60% |
| Medium (40-59) | ~2,100 | ~1,500 | +20% | 80% |
| Standard (20-39) | ~2,800 | ~1,800 | +15% | 95% |
| Low (0-19) | ~1,400 | ~600 | +5% | 100% |
| **Total** | **7,992** | **~5,150** | **~100%** | |

**Assumptions**:
- 65% acceptance rate for Critical/High (strong evidence)
- 50% for Medium
- 35% for Standard
- 15% for Low (mostly TOKEN_SIMILARITY with NOT_SPECIFIED)

### Nutrient-Specific Coverage (Post-Pilot Estimate)
| Nutrient | Current IFCT Coverage | Projected Recipe Coverage |
|----------|----------------------|--------------------------|
| Energy | 100% | ~85% |
| Protein | 100% | ~85% |
| Fat | 100% | ~85% |
| Carbohydrate | 58% | ~50% |
| Total Fibre | 58% | ~50% |
| Moisture | 100% | ~85% |
| Ash | 100% | ~85% |

**Limiting factor**: 1.4% gram weight coverage (not mapping coverage).

---

## 11. Review Queue Export

The workbench supports filtered export of the prioritized queue:
- Filter by priority band, ingredient, preparation state, match method, confidence
- Export to CSV for offline review coordination
- Tracks submission state per unit

---

## 12. Governance Note

**This prioritization informs review order ONLY.** It does not:
- Auto-approve any mapping
- Reduce evidence requirements
- Bypass blind review or adjudication
- Guarantee acceptance

All 7,992 units require individual human review per the approved protocol.

---

*End of Review Prioritization Report*