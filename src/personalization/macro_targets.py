"""Macro Targets - Calculate macronutrient and micronutrient targets."""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

from .reference_values import (
    MACRO_DISTRIBUTION_RANGES, get_icmr_protein_target, get_icmr_fat_range,
    get_icmr_carb_range, get_icmr_fibre_target, NUTRIENT_DENSITY_THRESHOLDS,
    ICMR_2020_RDA
)
from .energy_requirements import EnergyCalculationResult
from ..personalization.profile_models import Anthropometrics, Sex, WeightGoal


class MacroDistributionMethod(Enum):
    """Method for macro distribution."""
    ICMR_BALANCED = "ICMR_BALANCED"       # ICMR 2020 ranges
    HIGH_PROTEIN = "HIGH_PROTEIN"         # Higher protein for weight loss/muscle
    LOW_CARB = "LOW_CARB"                 # Lower carb, higher fat
    KETOGENIC = "KETOGENIC"               # Very low carb (<50g)
    CUSTOM = "CUSTOM"                     # User-specified percentages


@dataclass
class MacroTargets:
    """Calculated macronutrient targets."""
    energy_kcal: float
    protein_g: float
    carbohydrate_g: float
    fat_g: float
    fibre_g: float
    
    # Percentages
    protein_pct: float
    carbohydrate_pct: float
    fat_pct: float
    
    # Method
    method: MacroDistributionMethod
    equation_used: str
    
    # Per-meal breakdown (optional)
    per_meal: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Warnings and notes
    warnings: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "energy_kcal": round(self.energy_kcal, 1),
            "protein_g": round(self.protein_g, 1),
            "carbohydrate_g": round(self.carbohydrate_g, 1),
            "fat_g": round(self.fat_g, 1),
            "fibre_g": round(self.fibre_g, 1),
            "protein_pct": round(self.protein_pct, 1),
            "carbohydrate_pct": round(self.carbohydrate_pct, 1),
            "fat_pct": round(self.fat_pct, 1),
            "method": self.method.value,
            "equation_used": self.equation_used,
            "per_meal": {k: {kk: round(vv, 1) for kk, vv in v.items()} for k, v in self.per_meal.items()},
            "warnings": self.warnings,
            "notes": self.notes,
        }
    
    @property
    def macro_total_pct(self) -> float:
        return self.protein_pct + self.carbohydrate_pct + self.fat_pct


@dataclass
class MicronutrientTargets:
    """Calculated micronutrient targets."""
    sodium_mg: Optional[float] = None
    potassium_mg: Optional[float] = None
    calcium_mg: Optional[float] = None
    iron_mg: Optional[float] = None
    zinc_mg: Optional[float] = None
    vitamin_a_mcg: Optional[float] = None
    vitamin_d_iu: Optional[float] = None
    vitamin_b12_mcg: Optional[float] = None
    folate_mcg: Optional[float] = None
    vitamin_c_mg: Optional[float] = None
    
    source: str = "ICMR_2020"
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {k: round(v, 1) if isinstance(v, float) else v 
                for k, v in self.__dict__.items() if not k.startswith('_')}


@dataclass
class CompleteNutritionTargets:
    """Complete nutrition targets including energy, macros, micros."""
    energy: EnergyCalculationResult
    macros: MacroTargets
    micros: MicronutrientTargets
    meal_targets: Dict[str, Dict[str, float]] = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: __import__('datetime').datetime.now().isoformat())
    profile_id: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "energy": self.energy.to_dict(),
            "macros": self.macros.to_dict(),
            "micros": self.micros.to_dict(),
            "meal_targets": {k: {kk: round(vv, 1) for kk, vv in v.items()} for k, v in self.meal_targets.items()},
            "generated_at": self.generated_at,
            "profile_id": self.profile_id,
        }


class MacroCalculator:
    """
    Calculate macronutrient targets based on energy requirements and goals.
    
    Uses ICMR 2020 guidelines as primary reference.
    """
    
    # Default macro percentages for different methods
    DEFAULT_DISTRIBUTIONS = {
        MacroDistributionMethod.ICMR_BALANCED: {"protein": 15, "fat": 25, "carb": 60},
        MacroDistributionMethod.HIGH_PROTEIN: {"protein": 25, "fat": 25, "carb": 50},
        MacroDistributionMethod.LOW_CARB: {"protein": 20, "fat": 40, "carb": 40},
        MacroDistributionMethod.KETOGENIC: {"protein": 20, "fat": 70, "carb": 10},
    }
    
    # ICMR ranges
    ICMR_PROTEIN_RANGE = (10, 15)   # % of energy
    ICMR_FAT_RANGE = (20, 30)
    ICMR_CARB_RANGE = (55, 65)
    
    def __init__(self):
        pass
    
    def calculate_protein_target(
        self,
        energy_kcal: float,
        anthropometrics: Anthropometrics,
        weight_goal: WeightGoal,
        method: MacroDistributionMethod = MacroDistributionMethod.ICMR_BALANCED
    ) -> Tuple[float, str]:
        """
        Calculate protein target in grams.
        
        Returns:
            (protein_g, rationale)
        """
        # ICMR: 0.83 g/kg body weight minimum
        if anthropometrics.weight_kg:
            icmr_protein = get_icmr_protein_target(anthropometrics.sex.value.lower(), anthropometrics.weight_kg)
        else:
            icmr_protein = energy_kcal * 0.10 / 4  # 10% of energy fallback
        
        # Method-specific adjustments
        if method == MacroDistributionMethod.HIGH_PROTEIN:
            # 1.6-2.2 g/kg for weight loss/muscle preservation
            if anthropometrics.weight_kg:
                target = max(icmr_protein, anthropometrics.weight_kg * 1.6)
                rationale = f"High protein: max(ICMR {icmr_protein:.1f}g, 1.6×{anthropometrics.weight_kg}kg) = {target:.1f}g"
            else:
                target = energy_kcal * 0.25 / 4  # 25% of energy
                rationale = f"High protein: 25% of {energy_kcal} kcal = {target:.1f}g"
        
        elif method == MacroDistributionMethod.KETOGENIC:
            # Moderate protein: 1.2-1.5 g/kg
            if anthropometrics.weight_kg:
                target = max(icmr_protein, anthropometrics.weight_kg * 1.2)
                rationale = f"Ketogenic protein: max(ICMR {icmr_protein:.1f}g, 1.2×{anthropometrics.weight_kg}kg) = {target:.1f}g"
            else:
                target = energy_kcal * 0.20 / 4
                rationale = f"Ketogenic protein: 20% of {energy_kcal} kcal = {target:.1f}g"
        
        elif method == MacroDistributionMethod.LOW_CARB:
            # Moderate-high protein: 1.5 g/kg
            if anthropometrics.weight_kg:
                target = max(icmr_protein, anthropometrics.weight_kg * 1.5)
                rationale = f"Low carb protein: max(ICMR {icmr_protein:.1f}g, 1.5×{anthropometrics.weight_kg}kg) = {target:.1f}g"
            else:
                target = energy_kcal * 0.20 / 4
                rationale = f"Low carb protein: 20% of {energy_kcal} kcal = {target:.1f}g"
        
        else:  # ICMR_BALANCED
            # Use ICMR body weight based target
            target = icmr_protein
            rationale = f"ICMR RDA: 0.83 g/kg × {anthropometrics.weight_kg}kg = {target:.1f}g" if anthropometrics.weight_kg else f"ICMR: 10-15% of energy"
        
        # Safety bounds: 0.8-2.5 g/kg
        if anthropometrics.weight_kg:
            min_protein = anthropometrics.weight_kg * 0.8
            max_protein = anthropometrics.weight_kg * 2.5
            target = max(min_protein, min(target, max_protein))
        
        return round(target, 1), rationale
    
    def calculate_fat_target(
        self,
        energy_kcal: float,
        protein_g: float,
        method: MacroDistributionMethod = MacroDistributionMethod.ICMR_BALANCED
    ) -> Tuple[float, str]:
        """Calculate fat target in grams."""
        protein_kcal = protein_g * 4
        remaining_kcal = energy_kcal - protein_kcal
        
        if method == MacroDistributionMethod.KETOGENIC:
            # 70% of energy from fat
            fat_pct = 0.70
            rationale = "Ketogenic: 70% of energy from fat"
        elif method == MacroDistributionMethod.LOW_CARB:
            # 40% of energy from fat
            fat_pct = 0.40
            rationale = "Low carb: 40% of energy from fat"
        elif method == MacroDistributionMethod.HIGH_PROTEIN:
            # 25% of energy from fat
            fat_pct = 0.25
            rationale = "High protein: 25% of energy from fat"
        else:
            # ICMR balanced: 25% of energy (mid-range 20-30%)
            fat_pct = 0.25
            rationale = "ICMR balanced: 25% of energy from fat (range 20-30%)"
        
        fat_kcal = remaining_kcal * fat_pct / (1 - (protein_g * 4 / energy_kcal))
        fat_g = fat_kcal / 9
        
        return round(fat_g, 1), rationale
    
    def calculate_carb_target(
        self,
        energy_kcal: float,
        protein_g: float,
        fat_g: float
    ) -> Tuple[float, str]:
        """Calculate carbohydrate target by difference."""
        protein_kcal = protein_g * 4
        fat_kcal = fat_g * 9
        carb_kcal = energy_kcal - protein_kcal - fat_kcal
        
        if carb_kcal < 0:
            carb_kcal = 0
        
        carb_g = carb_kcal / 4
        carb_pct = (carb_kcal / energy_kcal) * 100 if energy_kcal > 0 else 0
        
        rationale = f"Remainder after protein ({protein_g}g) and fat ({fat_g}g): {carb_pct:.0f}% of energy"
        return round(carb_g, 1), rationale
    
    def calculate_fibre_target(
        self,
        anthropometrics: Anthropometrics,
        energy_kcal: float
    ) -> Tuple[float, str]:
        """Calculate fibre target."""
        # ICMR: 30g (male), 25g (female)
        icmr_fibre = get_icmr_fibre_target(anthropometrics.sex.value.lower())
        
        # Also consider energy-based: ~14g/1000 kcal
        energy_based = energy_kcal * 0.014
        
        # Use higher of the two
        target = max(icmr_fibre, energy_based)
        
        rationale = f"ICMR: {icmr_fibre}g ({anthropometrics.sex.value}), energy-based: {energy_based:.0f}g"
        return round(target, 1), rationale
    
    def calculate(
        self,
        energy_result: EnergyCalculationResult,
        anthropometrics: Anthropometrics,
        weight_goal: WeightGoal,
        method: MacroDistributionMethod = MacroDistributionMethod.ICMR_BALANCED,
        custom_distribution: Optional[Dict[str, float]] = None,
        meal_distribution: Optional[Dict[str, float]] = None
    ) -> MacroTargets:
        """
        Calculate complete macro targets.
        
        Args:
            energy_result: EnergyCalculationResult from EnergyCalculator
            anthropometrics: User anthropometrics
            weight_goal: Weight management goal
            method: Distribution method
            custom_distribution: Optional custom percentages (protein, fat, carb)
            meal_distribution: Optional per-meal energy fractions
            
        Returns:
            MacroTargets with all values
        """
        energy_kcal = energy_result.target_energy_kcal
        warnings = []
        notes = []
        
        # Step 1: Protein
        protein_g, protein_rationale = self.calculate_protein_target(
            energy_kcal, anthropometrics, weight_goal, method
        )
        notes.append(f"Protein: {protein_rationale}")
        
        # Step 2: Fat
        fat_g, fat_rationale = self.calculate_fat_target(energy_kcal, protein_g, method)
        notes.append(f"Fat: {fat_rationale}")
        
        # Step 3: Carbohydrate (by difference)
        carb_g, carb_rationale = self.calculate_carb_target(energy_kcal, protein_g, fat_g)
        notes.append(f"Carbohydrate: {carb_rationale}")
        
        # Step 4: Fibre
        fibre_g, fibre_rationale = self.calculate_fibre_target(anthropometrics, energy_kcal)
        notes.append(f"Fibre: {fibre_rationale}")
        
        # Calculate percentages
        protein_pct = (protein_g * 4 / energy_kcal) * 100 if energy_kcal > 0 else 0
        fat_pct = (fat_g * 9 / energy_kcal) * 100 if energy_kcal > 0 else 0
        carb_pct = (carb_g * 4 / energy_kcal) * 100 if energy_kcal > 0 else 0
        
        # Validate macro distribution
        if method == MacroDistributionMethod.ICMR_BALANCED:
            if not (10 <= protein_pct <= 20):
                warnings.append(f"Protein {protein_pct:.1f}% outside ICMR range (10-20%)")
            if not (20 <= fat_pct <= 30):
                warnings.append(f"Fat {fat_pct:.1f}% outside ICMR range (20-30%)")
            if not (50 <= carb_pct <= 65):
                warnings.append(f"Carbohydrate {carb_pct:.1f}% outside ICMR range (50-65%)")
        
        # Check fibre adequacy
        if fibre_g < 20:
            warnings.append(f"Fibre target {fibre_g}g may be low (ICMR recommends 25-30g)")
        
        # Per-meal breakdown
        per_meal = {}
        if meal_distribution:
            for meal, fraction in meal_distribution.items():
                per_meal[meal] = {
                    "energy_kcal": round(energy_kcal * fraction, 1),
                    "protein_g": round(protein_g * fraction, 1),
                    "carbohydrate_g": round(carb_g * fraction, 1),
                    "fat_g": round(fat_g * fraction, 1),
                    "fibre_g": round(fibre_g * fraction, 1),
                }
        
        return MacroTargets(
            energy_kcal=energy_kcal,
            protein_g=protein_g,
            carbohydrate_g=carb_g,
            fat_g=fat_g,
            fibre_g=fibre_g,
            protein_pct=round(protein_pct, 1),
            carbohydrate_pct=round(carb_pct, 1),
            fat_pct=round(fat_pct, 1),
            method=method,
            equation_used=energy_result.equation_used.value,
            per_meal=per_meal,
            warnings=warnings,
            notes=notes
        )


class MicronutrientCalculator:
    """Calculate micronutrient targets based on ICMR 2020 RDA."""
    
    def calculate(
        self,
        anthropometrics: Anthropometrics,
        weight_goal: WeightGoal = WeightGoal.MAINTAIN
    ) -> MicronutrientTargets:
        """Calculate micronutrient targets from ICMR 2020 RDA."""
        sex = anthropometrics.sex.value.lower()
        age = anthropometrics.age_years or 30
        
        # ICMR 2020 RDA values
        micros = MicronutrientTargets()
        
        # Sodium
        micros.sodium_mg = ICMR_2020_RDA.get("sodium_mg", {}).get("adult", 2000)
        
        # Potassium
        micros.potassium_mg = ICMR_2020_RDA.get("potassium_mg", {}).get("adult", 3500)
        
        # Calcium
        if sex == "female" and age >= 50:
            micros.calcium_mg = ICMR_2020_RDA.get("calcium_mg", {}).get("postmenopausal_female", 1200)
        else:
            micros.calcium_mg = ICMR_2020_RDA.get("calcium_mg", {}).get("adult", 1000)
        
        # Iron
        if sex == "female" and age < 50:
            micros.iron_mg = ICMR_2020_RDA.get("iron_mg", {}).get("adult_female", 29)
        elif sex == "female" and age >= 50:
            micros.iron_mg = ICMR_2020_RDA.get("iron_mg", {}).get("postmenopausal_female", 19)
        else:
            micros.iron_mg = ICMR_2020_RDA.get("iron_mg", {}).get("adult_male", 19)
        
        # Zinc
        micros.zinc_mg = ICMR_2020_RDA.get("zinc_mg", {}).get(f"adult_{sex}", 10)
        
        # Vitamin A
        micros.vitamin_a_mcg = ICMR_2020_RDA.get("vitamin_a_mcg", {}).get(f"adult_{sex}", 840)
        
        # Vitamin D
        if age >= 70:
            micros.vitamin_d_iu = ICMR_2020_RDA.get("vitamin_d_iu", {}).get("elderly_70+", 800)
        else:
            micros.vitamin_d_iu = ICMR_2020_RDA.get("vitamin_d_iu", {}).get("adult", 600)
        
        # Vitamin B12
        micros.vitamin_b12_mcg = ICMR_2020_RDA.get("vitamin_b12_mcg", {}).get("adult", 2.2)
        
        # Folate
        micros.folate_mcg = ICMR_2020_RDA.get("folate_mcg", {}).get("adult", 300)
        
        # Vitamin C (not in ICMR table, use WHO 45mg)
        micros.vitamin_c_mcg = 45000  # 45mg in mcg
        
        return micros


def calculate_nutrition_targets(
    energy_result: EnergyCalculationResult,
    anthropometrics: Anthropometrics,
    weight_goal: WeightGoal,
    method: MacroDistributionMethod = MacroDistributionMethod.ICMR_BALANCED,
    meal_distribution: Optional[Dict[str, float]] = None
) -> CompleteNutritionTargets:
    """
    Calculate complete nutrition targets (energy, macros, micros).
    
    Main entry point for nutrition target calculation.
    """
    macro_calc = MacroCalculator()
    micro_calc = MicronutrientCalculator()
    
    macros = macro_calc.calculate(
        energy_result=energy_result,
        anthropometrics=anthropometrics,
        weight_goal=weight_goal,
        method=method,
        meal_distribution=meal_distribution
    )
    
    micros = micro_calc.calculate(anthropometrics, weight_goal)
    
    return CompleteNutritionTargets(
        energy=energy_result,
        macros=macros,
        micros=micros,
        meal_targets=macros.per_meal,
        profile_id=""  # Set by caller
    )