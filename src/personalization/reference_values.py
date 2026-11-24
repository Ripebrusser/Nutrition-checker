"""Reference Values - Nutritional reference standards and constants."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json


class ReferenceSource(Enum):
    """Source of reference values."""
    ICMR_NIN_2020 = "ICMR_NIN_2020"           # Indian Council of Medical Research, NIN 2020 RDA
    WHO_FAO_2004 = "WHO_FAO_2004"             # WHO/FAO/UNU 2004
    USDA_DRI_2019 = "USDA_DRI_2019"           # USDA Dietary Reference Intakes
    ICMR_2010 = "ICMR_2010"                   # ICMR 2010 RDA (older)
    CUSTOM = "CUSTOM"                         # User-defined


@dataclass
class NutrientReference:
    """Reference value for a single nutrient."""
    nutrient: str
    unit: str
    value: float
    source: ReferenceSource
    population_group: str  # e.g., "adult_male_19-50", "adult_female_19-50"
    condition: Optional[str] = None  # e.g., "pregnancy", "lactation"
    confidence: float = 1.0
    notes: str = ""


# ICMR-NIN 2020 RDA for Indians (per day)
# Source: Nutrient Requirements for Indians, ICMR-NIN, 2020
ICMR_2020_RDA = {
    # Energy (kcal/day) - varies by age, sex, activity; base values for sedentary
    "energy_kcal": {
        "adult_male_sedentary": 2100,
        "adult_male_moderate": 2700,
        "adult_male_heavy": 3400,
        "adult_female_sedentary": 1650,
        "adult_female_moderate": 2100,
        "adult_female_heavy": 2600,
    },
    # Protein (g/day) - 0.83 g/kg body weight for adults
    "protein_g": {
        "adult_male": 54,  # ~0.83 * 65kg
        "adult_female": 46,  # ~0.83 * 55kg
        "pregnant": 78,
        "lactating_0_6m": 74,
        "lactating_6_12m": 68,
    },
    # Fat (g/day) - 20-30% of energy
    "fat_g": {
        "adult": "20-30%E",  # percentage of energy
    },
    # Carbohydrate (g/day) - 50-65% of energy
    "carbohydrate_g": {
        "adult": "50-65%E",
    },
    # Fibre (g/day)
    "fibre_g": {
        "adult_male": 30,
        "adult_female": 25,
    },
    # Sodium (mg/day) - AI (adequate intake)
    "sodium_mg": {
        "adult": 2000,  # ~5g salt
    },
    # Potassium (mg/day)
    "potassium_mg": {
        "adult": 3500,
    },
    # Calcium (mg/day)
    "calcium_mg": {
        "adult": 1000,
        "postmenopausal_female": 1200,
    },
    # Iron (mg/day)
    "iron_mg": {
        "adult_male": 19,
        "adult_female": 29,  # menstruating
        "postmenopausal_female": 19,
        "pregnant": 27,
    },
    # Zinc (mg/day)
    "zinc_mg": {
        "adult_male": 12,
        "adult_female": 10,
    },
    # Vitamin A (mcg RAE/day)
    "vitamin_a_mcg": {
        "adult_male": 1000,
        "adult_female": 840,
    },
    # Vitamin D (IU/day) - 400 IU = 10 mcg
    "vitamin_d_iu": {
        "adult": 600,
        "elderly_70+": 800,
    },
    # Vitamin B12 (mcg/day)
    "vitamin_b12_mcg": {
        "adult": 2.2,
    },
    # Folate (mcg DFE/day)
    "folate_mcg": {
        "adult": 300,
        "pregnant": 570,
    },
}

# WHO/FAO 2004 reference values (for comparison)
WHO_FAO_2004 = {
    "protein_g_per_kg": 0.83,
    "fat_percentage_energy": (15, 30),
    "carb_percentage_energy": (55, 75),
    "fibre_g": 25,
    "sodium_mg": 2000,
}

# USDA DRI 2019 (for reference)
USDA_DRI_2019 = {
    "protein_g_per_kg": 0.8,
    "fat_percentage_energy": (20, 35),
    "carb_percentage_energy": (45, 65),
    "fibre_g": {"male": 38, "female": 25},
    "sodium_mg": 2300,
}


# Activity level factors (PAL - Physical Activity Level)
ACTIVITY_PAL_FACTORS = {
    "SEDENTARY": 1.40,
    "LIGHTLY_ACTIVE": 1.55,
    "MODERATELY_ACTIVE": 1.70,
    "VERY_ACTIVE": 1.90,
    "EXTREMELY_ACTIVE": 2.10,
}

# Mifflin-St Jeor BMR equation coefficients
MIFFLIN_ST_JEOR = {
    "male": {"weight": 10, "height": 6.25, "age": -5, "constant": 5},
    "female": {"weight": 10, "height": 6.25, "age": -5, "constant": -161},
}

# Harris-Benedict equation coefficients (older, less accurate)
HARRIS_BENEDICT = {
    "male": {"weight": 13.397, "height": 4.799, "age": -5.677, "constant": 88.362},
    "female": {"weight": 9.247, "height": 3.098, "age": -4.330, "constant": 447.593},
}


def get_icmr_rda(nutrient: str, group: str) -> Optional[float]:
    """Get ICMR 2020 RDA value for a nutrient and population group."""
    if nutrient in ICMR_2020_RDA:
        return ICMR_2020_RDA[nutrient].get(group)
    return None


def get_icmr_energy_target(sex: str, activity: str, age: int) -> Optional[int]:
    """Get ICMR energy target for sex, activity, and age group."""
    # ICMR uses age groups: 18-30, 30-60, 60+
    # For simplicity, use adult values
    key = f"adult_{sex.lower()}_{activity.lower()}"
    return ICMR_2020_RDA.get("energy_kcal", {}).get(key)


def get_icmr_protein_target(sex: str, weight_kg: float) -> float:
    """Calculate ICMR protein target based on body weight (0.83 g/kg)."""
    return round(0.83 * weight_kg, 1)


def get_icmr_fat_range(energy_kcal: float) -> tuple:
    """Get fat range in grams (20-30% of energy)."""
    min_fat = (energy_kcal * 0.20) / 9
    max_fat = (energy_kcal * 0.30) / 9
    return (round(min_fat, 1), round(max_fat, 1))


def get_icmr_carb_range(energy_kcal: float) -> tuple:
    """Get carb range in grams (50-65% of energy)."""
    min_carb = (energy_kcal * 0.50) / 4
    max_carb = (energy_kcal * 0.65) / 4
    return (round(min_carb, 1), round(max_carb, 1))


def get_icmr_fibre_target(sex: str) -> int:
    """Get ICMR fibre target."""
    return ICMR_2020_RDA.get("fibre_g", {}).get(f"adult_{sex.lower()}", 25)


# Nutrient density thresholds (per 100 kcal)
NUTRIENT_DENSITY_THRESHOLDS = {
    "protein_g_per_100kcal": 5.0,    # High protein: >5g/100kcal
    "fibre_g_per_100kcal": 1.5,      # High fibre: >1.5g/100kcal
    "sodium_mg_per_100kcal": 100,    # Low sodium: <100mg/100kcal
    "satfat_g_per_100kcal": 1.5,     # Low sat fat: <1.5g/100kcal
    "sugar_g_per_100kcal": 5.0,      # Low sugar: <5g/100kcal
}

# Indian food group servings (ICMR balanced diet)
INDIAN_FOOD_GROUP_SERVINGS = {
    "cereals_millets": {"servings": 8-11, "serving_g": 30},      # 240-330g
    "pulses_legumes": {"servings": 2-3, "serving_g": 30},       # 60-90g
    "milk_products": {"servings": 2-3, "serving_g": 100},       # 200-300ml
    "vegetables": {"servings": 4-5, "serving_g": 100},          # 400-500g
    "fruits": {"servings": 2-3, "serving_g": 100},              # 200-300g
    "nuts_seeds": {"servings": 1, "serving_g": 20},             # 20g
    "fats_oils": {"servings": 3-4, "serving_g": 5},             # 15-20g
}

# Meal energy distribution (fractions)
MEAL_ENERGY_DISTRIBUTION = {
    "3_meals": {"breakfast": 0.30, "lunch": 0.40, "dinner": 0.30},
    "4_meals": {"breakfast": 0.25, "lunch": 0.35, "snack": 0.15, "dinner": 0.25},
    "5_meals": {"breakfast": 0.25, "mid_morning": 0.10, "lunch": 0.35, "evening_snack": 0.10, "dinner": 0.20},
    "6_meals": {"breakfast": 0.20, "mid_morning": 0.10, "lunch": 0.30, "mid_afternoon": 0.10, "evening_snack": 0.10, "dinner": 0.20},
}

# Macro distribution ranges (percentage of energy)
MACRO_DISTRIBUTION_RANGES = {
    "protein_pct": (10, 20),      # ICMR: 10-15%, allowance up to 20%
    "fat_pct": (20, 30),          # ICMR: 20-30%
    "carb_pct": (50, 65),         # ICMR: 55-65%
}


def get_meal_distribution(meal_count) -> Dict[str, float]:
    """Get energy distribution for a meal count."""
    # Handle both int and MealFrequency enum
    if hasattr(meal_count, 'value'):
        meal_count = meal_count.value
    
    if meal_count == 3:
        return MEAL_ENERGY_DISTRIBUTION["3_meals"]
    elif meal_count == 4:
        return MEAL_ENERGY_DISTRIBUTION["4_meals"]
    elif meal_count == 5:
        return MEAL_ENERGY_DISTRIBUTION["5_meals"]
    elif meal_count >= 6:
        return MEAL_ENERGY_DISTRIBUTION["6_meals"]
    return MEAL_ENERGY_DISTRIBUTION["5_meals"]


# =====================================================================
# Documentation of reference sources and methodology
# =====================================================================

REFERENCE_DOCUMENTATION = """
NUTRITIONAL REFERENCE VALUES DOCUMENTATION
============================================

Primary Source: ICMR-NIN 2020 "Nutrient Requirements for Indians"
- Published by Indian Council of Medical Research - National Institute of Nutrition
- Replaces ICMR 2010 RDA
- Specific to Indian population, dietary patterns, and body composition

Energy Requirements (ICMR 2020):
--------------------------------
Based on factorial approach: BMR × PAL (Physical Activity Level)
- BMR: Mifflin-St Jeor equation (validated for Indians)
- PAL categories: Sedentary (1.40), Light (1.55), Moderate (1.70), Heavy (1.90), Very Heavy (2.10)
- Age groups: Adults 18-60 years, Elderly 60+ (10% reduction)

Protein:
--------
- RDA: 0.83 g/kg body weight/day (adults)
- Based on nitrogen balance studies in Indians
- Higher for pregnancy (+23g), lactation (+19g first 6mo, +13g 6-12mo)

Fat:
----
- 20-30% of total energy
- Visible fat (added oils): 20-30g/day
- Invisible fat (in foods): ~10-15g/day
- Emphasis on n-3 PUFA, limit saturated fat <10%E, avoid trans fat

Carbohydrate:
-------------
- 50-65% of total energy
- Prefer complex carbs, whole grains, millets
- Free sugars <10% of total energy (WHO conditional <5%)

Fibre:
------
- Adult male: 30g/day, Adult female: 25g/day
- From whole grains, pulses, vegetables, fruits
- Cereal fibre preferred for Indian context

Micronutrients:
---------------
- Sodium: 2000 mg/day (5g salt) - AI (adequate intake)
- Potassium: 3500 mg/day - from vegetables, fruits, legumes
- Calcium: 1000 mg/day (1200 postmenopausal)
- Iron: 19 mg (men), 29 mg (women 18-50), 27 mg (pregnant)
- Zinc: 12 mg (men), 10 mg (women)
- Vitamin D: 600 IU (15 mcg) - higher for elderly
- Vitamin B12: 2.2 mcg
- Folate: 300 mcg DFE (570 mcg pregnant)

Limitations:
------------
1. ICMR values are for HEALTHY populations; clinical conditions need adjustment
2. Energy requirements vary ±15% individually; use as starting point
3. Protein RDA is minimum; athletes/elderly may need 1.2-1.5 g/kg
4. Micronutrient bioavailability varies with Indian dietary patterns (phytates, tannins)
5. No specific RDA for Indians for: added sugars, cholesterol, saturated fat (use WHO limits)

Application in Phase 4:
----------------------
1. Energy: Mifflin-St Jeor BMR × ICMR PAL factor
2. Protein: max(0.83 g/kg, 10-15%E)
3. Fat: 20-30%E (individualize based on lipid profile)
4. Carb: 50-65%E (remainder)
5. Fibre: ICMR target (25-30g)
6. Micronutrients: ICMR RDA where available; WHO for others
"""


def print_reference_documentation():
    """Print the reference documentation."""
    print(REFERENCE_DOCUMENTATION)


if __name__ == "__main__":
    print_reference_documentation()