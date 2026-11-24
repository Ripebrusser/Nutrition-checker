# Phase 4: Nutritional Target Methodology Report

**Date:** 2026-11-19  
**Status:** Implementation Complete

---

## 1. Overview

The nutritional target calculation system (`src/personalization/`) computes personalized daily energy and nutrient requirements using established scientific methods with Indian population-specific reference values.

---

## 2. Energy Requirements (`energy_requirements.py`)

### 2.1 Methods Supported

| Method | Class | Description |
|--------|-------|-------------|
| Mifflin-St Jeor | `EquationMethod.MIFFLIN_ST_JEOR` | Recommended; validated for modern populations |
| Harris-Benedict | `EquationMethod.HARRIS_BENEDICT` | Original 1919/1984; tends to overestimate |
| ICMR Factorial | `EquationMethod.ICMR_FACTORIAL` | ICMR 2020 lookup tables |

### 2.2 Default: Mifflin-St Jeor

**Equation:**
```
BMR (kcal/day) = 10 × weight_kg + 6.25 × height_cm - 5 × age_years + s
s = +5 for males, -161 for females
```

**Source:** Mifflin MD, St Jeor ST, et al. "A new predictive equation for resting energy expenditure in healthy individuals." Am J Clin Nutr. 1990.

**Why Mifflin-St Jeor:**
- Validated across diverse populations including Indians
- More accurate than Harris-Benedict for modern (sedentary) lifestyles
- Recommended by Academy of Nutrition and Dietetics

### 2.3 Activity Level Factors (ICMR PAL)

| ActivityLevel | PAL Factor | Description |
|---------------|------------|-------------|
| SEDENTARY | 1.40 | Little or no exercise |
| LIGHTLY_ACTIVE | 1.55 | Light exercise 1-3 days/week |
| MODERATELY_ACTIVE | 1.70 | Moderate exercise 3-5 days/week |
| VERY_ACTIVE | 1.90 | Hard exercise 6-7 days/week |
| EXTREMELY_ACTIVE | 2.10 | Very hard exercise, physical job |

**Source:** ICMR-NIN 2020 "Nutrient Requirements for Indians" - factorial approach using PAL.

### 2.4 TDEE Calculation
```
TDEE = BMR × PAL
```

### 2.5 Weight Goal Adjustments

| WeightGoal | Adjustment |
|------------|------------|
| MAINTAIN | 0 kcal |
| LOSE | -7700 × kg/week ÷ 7 (negative) |
| GAIN | +7700 × kg/week ÷ 7 (positive) |

**Safety Limits:**
- Max deficit: 25% of TDEE
- Max surplus: 20% of TDEE
- Minimum calories: 1500 (male), 1200 (female)

**Energy equivalent:** 7700 kcal/kg weight change (accounts for lean mass)

### 2.6 ICMR 2020 Reference Values
Used for validation and comparison:
```python
# ICMR 2020 energy targets (sedentary adults)
adult_male_sedentary: 2100 kcal
adult_female_sedentary: 1650 kcal
# ... with PAL adjustments
```

**Source:** ICMR-NIN 2020 "Nutrient Requirements for Indians"

---

## 3. Macronutrient Targets (`macro_targets.py`)

### 3.1 Distribution Methods

| Method | Protein | Fat | Carb | Use Case |
|--------|---------|-----|------|----------|
| ICMR_BALANCED | 15% | 25% | 60% | General population (default) |
| HIGH_PROTEIN | 25% | 25% | 50% | Weight loss, muscle preservation |
| LOW_CARB | 20% | 40% | 40% | Diabetes, metabolic syndrome |
| KETOGENIC | 20% | 70% | 10% | Therapeutic ketosis |
| CUSTOM | User-defined | User-defined | User-defined | Medical prescription |

### 3.2 ICMR 2020 Ranges
| Nutrient | Range (% energy) | Source |
|----------|------------------|--------|
| Protein | 10-15% (up to 20%) | ICMR 2020 |
| Fat | 20-30% | ICMR 2020 |
| Carbohydrate | 55-65% | ICMR 2020 |

### 3.3 Protein Calculation

**ICMR RDA:** 0.83 g/kg body weight/day (adults)

**Method-specific:**
- ICMR_BALANCED: max(0.83 g/kg, 10-15% energy)
- HIGH_PROTEIN: max(ICMR, 1.6 g/kg for weight loss)
- LOW_CARB: max(ICMR, 1.5 g/kg)
- KETOGENIC: max(ICMR, 1.2 g/kg)

**Safety bounds:** 0.8-2.5 g/kg body weight

### 3.4 Fat Calculation
Fat = remaining energy after protein, distributed by method percentage.

### 3.5 Carbohydrate Calculation
Carb = remaining energy after protein and fat (by difference).

### 3.6 Fibre Calculation
- ICMR: 30g (male), 25g (female)
- Energy-based: 14g/1000 kcal
- **Target:** max(ICMR, energy-based)

### 3.7 ICMR Range Validation
Warnings generated if:
- Protein outside 10-20% (ICMR balanced)
- Fat outside 20-30%
- Carb outside 50-65%
- Fibre < 20g

---

## 4. Micronutrient Targets (`macro_targets.py`)

### 4.1 ICMR 2020 RDA Values

| Nutrient | Adult Male | Adult Female | Notes |
|----------|------------|--------------|-------|
| Sodium | 2000 mg | 2000 mg | AI (adequate intake) |
| Potassium | 3500 mg | 3500 mg | |
| Calcium | 1000 mg | 1000 mg (1200 postmenopausal) | |
| Iron | 19 mg | 29 mg (19 postmenopausal) | Higher for menstruating |
| Zinc | 12 mg | 10 mg | |
| Vitamin A | 1000 mcg | 840 mcg | RAE |
| Vitamin D | 600 IU | 600 IU (800 elderly) | |
| Vitamin B12 | 2.2 mcg | 2.2 mcg | |
| Folate | 300 mcg | 300 mcg (570 pregnant) | DFE |
| Vitamin C | 45 mg | 45 mg | WHO value |

**Source:** ICMR-NIN 2020 RDA tables

### 4.2 Special Populations
- Pregnancy: +23g protein, +19g lactation (0-6mo), +13g (6-12mo)
- Postmenopausal: Calcium 1200mg, Iron 19mg
- Elderly 70+: Vitamin D 800 IU

---

## 5. Complete Nutrition Targets (`nutrition_targets.py`)

### 5.1 NutritionTargetCalculator
Main orchestrator integrating energy, macro, and micronutrient calculations.

```python
calculator = NutritionTargetCalculator(default_macro_method=MacroDistributionMethod.ICMR_BALANCED)
targets = calculator.calculate_for_profile(profile)
```

### 5.2 Output: CompleteNutritionTargets
```python
@dataclass
class CompleteNutritionTargets:
    energy: EnergyCalculationResult
    macros: MacroTargets
    micros: MicronutrientTargets
    meal_targets: Dict[str, Dict[str, float]]
    profile_id: str
```

### 5.3 Per-Meal Targets
Distributed using `get_meal_distribution()` based on `MealFrequency`.

---

## 6. Reference Values Documentation (`reference_values.py`)

### 6.1 Key References
| Source | Year | Use |
|--------|------|-----|
| ICMR-NIN | 2020 | Primary (Indian population) |
| WHO/FAO/UNU | 2004 | Energy equations, cross-reference |
| USDA DRI | 2019 | Micronutrient cross-reference |

### 6.2 Documentation
Complete methodology documentation in `REFERENCE_DOCUMENTATION` string constant.

---

## 7. Calculation Examples

### 7.1 30yo Male, 170cm, 70kg, Lightly Active, Maintain
```
BMR (Mifflin-St Jeor): 10×70 + 6.25×170 - 5×30 + 5 = 1647 kcal
TDEE: 1647 × 1.55 = 2553 kcal
Target: 2553 kcal (maintain)

Protein: max(0.83×70, 15%) = 58g (9%)
Fat: 25% = 71g
Carb: remainder = 355g (56%)
Fibre: max(30, 2553×0.014) = 36g
```

### 7.2 35yo Female, 165cm, 85kg, Sedentary, Lose 0.5kg/wk
```
BMR: 10×85 + 6.25×165 - 5×35 - 161 = 1545 kcal
TDEE: 1545 × 1.40 = 2163 kcal
Deficit: -540 kcal (0.5 kg/week × 7700 ÷ 7)
Target: 1623 kcal

Protein: 0.83×85 = 70.5g (17%)
Fat: 25% = 45g
Carb: remainder = 234g (58%)
Fibre: max(25, 1623×0.014) = 25g
```

---

## 8. Specialized Presets

| Preset | Method | Use Case |
|--------|--------|----------|
| `calculate_weight_loss_targets` | HIGH_PROTEIN | Weight loss with muscle preservation |
| `calculate_muscle_gain_targets` | HIGH_PROTEIN | Resistance training |
| `calculate_maintenance_targets` | ICMR_BALANCED | General health |
| `calculate_diabetes_targets` | LOW_CARB | Glycemic control |
| `calculate_heart_health_targets` | ICMR_BALANCED | CVD prevention |

---

## 9. Validation & Safety

### 8.1 Minimum Calories
- Male: 1500 kcal
- Female: 1200 kcal

### 8.2 Maximum Deficit/Surplus
- Deficit: 25% of TDEE
- Surplus: 20% of TDEE

### 8.3 Weight Change Rate
- Range: 0.1-1.0 kg/week
- >1.0 kg/week → ERROR

### 8.4 Macro Distribution Warnings
- Protein outside 10-20% (balanced)
- Fat outside 20-30%
- Carb outside 50-65%

---

## 9. Files

| File | Purpose |
|------|---------|
| `src/personalization/energy_requirements.py` | BMR, TDEE, weight adjustment |
| `src/personalization/macro_targets.py` | Macro/micronutrient calculation |
| `src/personalization/nutrition_targets.py` | Orchestrator + presets |
| `src/personalization/reference_values.py` | ICMR 2020 tables, documentation |
| `tests/phase4/test_personalization.py::TestEnergyRequirements` | 5 tests |
| `tests/phase4/test_personalization.py::TestMacroTargets` | 5 tests |

---

## 10. Limitations

1. **Equations are estimates** - Individual variation ±15-20%
2. **ICMR values for healthy adults** - Clinical conditions need medical adjustment
3. **No body composition** - BMR equations don't account for muscle vs fat mass
4. **Indian population specific** - May not generalize to other ethnicities
5. **No adaptive thermogenesis** - Doesn't model metabolic adaptation to dieting
6. **Micronutrients from ICMR only** - Some values use WHO where ICMR lacks data

---

*End of Nutritional Target Methodology Report*