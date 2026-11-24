# Phase 6: Nutrition Display Report

**Date:** 2026-11-19  
**Status:** Implementation Complete (Data Unavailable)

---

## 1. Overview

The Nutrition Display system presents recipe and meal plan nutrition information with full transparency about data completeness, provenance, and limitations.

**Current Status:** Zero approved ingredient mappings → All recipes show `UNAVAILABLE` nutrition status.

---

## 2. Display Components

### 2.1 Recipe Nutrition Card (Recipe List)
```
┌─────────────────────────────────────────────┐
│ Recipe Name                    [PARTIAL]    │
│ 🍽️ Cuisine  •  🍽️ Course                  │
│                                             │
│ Energy: 245 kcal    Protein: 12.4 g        │
│ Carbs: 32.1 g         Fat: 8.2 g           │
└─────────────────────────────────────────────┘
```

| Element | Source | Fallback |
|---------|--------|----------|
| Status Badge | `nutrition_status` | "UNAVAILABLE" |
| Energy | `per_serving_nutrients.energy_kcal` | "N/A" |
| Protein | `per_serving_nutrients.protein_g` | "N/A" |
| Carbs | `per_serving_nutrients.carb_available_g` | "N/A" |
| Fat | `per_serving_nutrients.fat_g` | "N/A" |

### 2.2 Status Badge Colors
| Status | Color | Meaning |
|--------|-------|---------|
| COMPLETE | Green | All 9 nutrients available |
| PARTIAL | Orange | Some nutrients available |
| UNAVAILABLE | Gray | No approved mappings |
| NO_MAPPED_INGREDIENTS | Red | No ingredient mappings |

---

## 2. Recipe Detail Page

### 2.1 Nutrition Tab Layout
```
┌─────────────────────────────────────────────────────────────┐
│ Nutrition Breakdown (Per Serving)              [PARTIAL]    │
├─────────────────────────────────────────────────────────────┤
│ Macronutrients                                              │
│ ┌─────────┬─────────┬─────────┬─────────┬─────────┐         │
│ │ Energy  │ Protein │  Carbs  │   Fat   │ Fibre   │         │
│ │ 245 kcal│ 12.4 g  │  32.1 g │  8.2 g  │  6.8 g  │         │
│ └─────────┴─────────┴─────────┴─────────┴─────────┘         │
│                                                             │
│ Micronutrients                                              │
│ ┌────────┬────────┬────────┬────────┐                        │
│ │Sodium  │Potassium│Calcium  │  Iron  │                        │
│ │ 420mg  │  350mg  │  85mg   │  3.2mg │                        │
│ └────────┴────────┴────────┴────────┘                        │
│                                                             │
│ Completeness: ████████░░ 6/9 nutrients (67%)                │
│                                                             │
│ Provenance: [Expand ▼]                                      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Completeness Visualization
| Element | Implementation |
|---------|----------------|
| **Progress Bars** | `st.progress(completeness, text=f"{nutrient}: {pct:.0%}")` |
| **Missing List** | "Missing: Fibre, Iron, Vitamin D" |
| **Status Summary** | "PARTIAL (6/9 nutrients available)" |

---

## 2. Meal Plan Nutrition

### 2.1 Daily Summary
```
┌─────────────────────────────────────────────────────────────┐
│ 📅 Monday, 2026-11-19                    Status: PARTIAL    │
├─────────────────────────────────────────────────────────────┤
│ 🌅 BREAKFAST: Idli Sambar          ✅ 320 kcal              │
│ ☕ MORNING_SNACK: Banana            ✅ 105 kcal              │
│ 🌞 LUNCH: Rice, Dal, Sabzi          ✅ 520 kcal              │
│ 🌅 EVENING_SNACK: Chai + Biscuit    ✅ 150 kcal              │
│ 🌙 DINNER: Roti, Paneer, Salad      ✅ 380 kcal              │
├─────────────────────────────────────────────────────────────┤
│ TOTAL: 1,475 kcal  |  Target: 2,000 kcal  |  74%           │
│ Protein: 52g/65g (80%)  Carbs: 180g/250g (72%)  Fat: 45g/70g (64%)  │
│ Fibre: 18g/25g (72%)                                                         │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Achievement Visualization
| Nutrient | Target | Actual | Achievement | Status |
|----------|--------|--------|-------------|--------|
| Energy | 2000 kcal | 1475 kcal | 74% | 🟡 Low |
| Protein | 65g | 52g | 80% | 🟡 Low |
| Carbs | 250g | 180g | 72% | 🟡 Low |
| Fat | 70g | 45g | 64% | 🟢 OK |
| Fibre | 25g | 18g | 72% | 🟡 Low |

---

## 3. Weekly Nutrition Summary

### 3.1 Weekly Achievement Table
| Nutrient | Target (Weekly) | Actual | Achievement | Status |
|----------|-----------------|--------|-------------|--------|
| Energy | 14,000 kcal | 13,200 kcal | 94% | 🟢 |
| Protein | 455 g | 410 g | 90% | 🟢 |
| Carbs | 1,750 g | 1,580 g | 90% | 🟢 |
| Fat | 490 g | 420 g | 86% | 🟡 |
| Fibre | 175 g | 140 g | 80% | 🟡 |

### 3.2 Visual Indicators
| Achievement | Color | Icon |
|-------------|-------|------|
| ≥ 95% | Green | ✅ |
| 90-95% | Green | ✅ |
| 80-90% | Yellow | ⚠️ |
| < 80% | Red | ❌ |

---

## 4. Nutrient Completeness Tracking

### 4.1 Per-Recipe Completeness
```python
recipe.nutrient_completeness = {
    "energy_kcal": 1.0,
    "protein_g": 1.0,
    "fat_g": 1.0,
    "carbohydrate_g": 1.0,
    "fibre_total_g": 0.58,  # 58% of recipes have this
    "moisture_g": 1.0,
    "ash_g": 1.0,
}
```

### 4.2 Display
| Nutrient | Available | Completeness | Bar |
|----------|-----------|--------------|-----|
| Energy | ✅ | 100% | ████████████████████ |
| Protein | ✅ | 100% | ████████████████████ |
| Fibre | ⚠️ | 58% | ████████████░░░░░░ |
| Iron | ❌ | 0% | ░░░░░░░░░░░░░░░░░░ |

---

## 3. Missing Value Handling

### 3.1 Display Rules
| Scenario | Display |
|----------|---------|
| Value available | `12.4 g` |
| Missing in IFCT | `N/A` (never `0 g`) |
| Recipe status UNAVAILABLE | "Nutrition data unavailable" |
| Recipe status PARTIAL | Show available, list missing |
| Per-serving calculation | Only if all ingredients mapped |

### 3.2 Never Do
| Anti-Pattern | Forbidden |
|--------------|-----------|
| Show `0 g` for missing | ❌ |
| Impute from averages | ❌ |
| Hide missing indicator | ❌ |
| Present partial as complete | ❌ |

---

## 4. Provenance & Traceability

### 4.1 Recipe Nutrition Provenance
```json
{
  "mapping_decisions": [
    {"ingredient": "rice", "ifct_code": "A001", "reviewer": "reviewer1", "timestamp": "2026-01-15"}
  ],
  "weight_sources": [
    {"ingredient": "rice", "source": "household_conversion", "confidence": 0.95}
  ],
  "edible_portion_factors": [
    {"ingredient": "spinach", "factor": 0.85, "source": "IFCT"}
  ],
  "calculation_timestamp": "2026-11-19T14:30:00"
}
```

### 4.2 Display
| Element | UI |
|---------|----|
| **Mapping** | "4/6 ingredients mapped" |
| **Weights** | "3/6 weights resolved" |
| **Edible Portion** | "2/6 factors applied" |
| **Timestamp** | "Calculated 2026-11-19 14:30" |
| **Details** | Expandable JSON viewer |

---

## 5. Missing Data Transparency

### 5.1 Recipe-Level Warnings
| Scenario | Message |
|----------|---------|
| UNAVAILABLE | "Nutrition data unavailable. Requires approved ingredient mappings." |
| PARTIAL (missing fibre) | "Fibre data unavailable for 2 of 6 ingredients" |
| Low completeness | "Only 58% of nutrients available for this recipe" |

### 5.2 Meal Plan Warnings
| Scenario | Message |
|----------|---------|
| Low completeness | "Only 45% of meal slots have complete nutrition data" |
| Low protein achievement | "Weekly protein target only 78% met" |
| High sodium | "Weekly sodium 1.3x target. Consider lower-sodium recipes." |

---

## 5. Unit Conversion Display

### 5.1 Energy
| Internal | Display |
|----------|---------|
| kJ (IFCT) | "350 kJ (83.7 kcal)" |
| kcal (targets) | "2,000 kcal" |

### 5.2 Conversion
```python
KJ_TO_KCAL = 4.184
kcal = round(kj / KJ_TO_KCAL, 1)
```

### 5.3 Display Format
| Nutrient | Display Format |
|----------|----------------|
| Energy | `245.3 kcal (1,026 kJ)` |
| Macros | `12.4 g` (1 decimal) |
| Micros | `3.2 mg` or `85 mcg` |
| Percentages | `85%` (integer) |

---

## 6. Nutrition Data Availability Matrix

| Nutrient | IFCT Coverage | Display if Missing |
|----------|---------------|-------------------|
| Energy (kJ) | 100% | Never missing |
| Protein | 100% | Never missing |
| Fat | 100% | Never missing |
| Carbohydrate | 58% | "N/A" |
| Total Fibre | 58% | "N/A" |
| Insoluble Fibre | 58% | "N/A" |
| Soluble Fibre | 58% | "N/A" |
| Moisture | 100% | Never missing |
| Ash | 100% | Never missing |

---

## 7. Current Limitations (Honest Disclosure)

| Limitation | Display Impact |
|------------|----------------|
| **0 approved mappings** | All recipes = UNAVAILABLE |
| **1.4% weight coverage** | Most weights = unresolved |
| **42% nutrient gaps** | Fibre/carb often N/A |
| **34% edible portion DB** | As-purchased weights unresolved |
| **No cooked IFCT entries** | Cooked prep = UNVERIFIED |

### 7.1 UI Disclosure
```markdown
> ⚠️ **Current Limitation**: No ingredient mappings have been approved yet 
> (Gate C authorization pending). All recipes show "UNAVAILABLE" nutrition. 
> Once human review completes, nutrition data will populate automatically.
```

---

*End of Nutrition Display Report*