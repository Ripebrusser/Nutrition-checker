"""Energy Requirements - Calculate daily energy needs using established equations."""

from typing import Dict, List, Optional, Tuple, Literal
from dataclasses import dataclass, field
from enum import Enum
import math

from .reference_values import (
    MIFFLIN_ST_JEOR, HARRIS_BENEDICT, ACTIVITY_PAL_FACTORS,
    get_icmr_energy_target, get_icmr_protein_target
)
from ..personalization.profile_models import Anthropometrics, Sex, ActivityLevel, WeightGoal


class EquationMethod(Enum):
    """BMR estimation equation."""
    MIFFLIN_ST_JEOR = "MIFFLIN_ST_JEOR"     # Recommended (more accurate for modern populations)
    HARRIS_BENEDICT = "HARRIS_BENEDICT"     # Original (tends to overestimate)
    ICMR_FACTORIAL = "ICMR_FACTORIAL"       # ICMR 2020 lookup table


@dataclass
class EnergyCalculationResult:
    """Result of energy requirement calculation."""
    bmr_kcal: float
    tdee_kcal: float                     # Total Daily Energy Expenditure
    target_energy_kcal: float            # Adjusted for weight goal
    equation_used: EquationMethod
    activity_level: ActivityLevel
    weight_goal: WeightGoal
    weight_change_kg_per_week: float
    adjustment_kcal: float
    components: Dict[str, float] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    method_details: str = ""

    def to_dict(self) -> Dict:
        return {
            "bmr_kcal": round(self.bmr_kcal, 1),
            "tdee_kcal": round(self.tdee_kcal, 1),
            "target_energy_kcal": round(self.target_energy_kcal, 1),
            "equation_used": self.equation_used.value,
            "activity_level": self.activity_level.value,
            "weight_goal": self.weight_goal.value,
            "weight_change_kg_per_week": self.weight_change_kg_per_week,
            "adjustment_kcal": round(self.adjustment_kcal, 1),
            "components": {k: round(v, 1) for k, v in self.components.items()},
            "warnings": self.warnings,
            "method_details": self.method_details,
        }


class EnergyCalculator:
    """
    Calculate daily energy requirements using multiple methods.
    
    Default: Mifflin-St Jeor BMR × ICMR PAL factors
    Fallback: ICMR 2020 lookup tables
    """
    
    # Energy equivalent of weight change (kcal/kg)
    # ~7700 kcal/kg for fat loss, but includes lean mass
    KCAL_PER_KG_WEIGHT_CHANGE = 7700
    
    # Maximum safe deficit/surplus as % of TDEE
    MAX_DEFICIT_PCT = 0.25   # 25% deficit max
    MAX_SURPLUS_PCT = 0.20   # 20% surplus max
    
    # Minimum safe calories
    MIN_CALORIES_MALE = 1500
    MIN_CALORIES_FEMALE = 1200
    
    def __init__(
        self,
        default_equation: EquationMethod = EquationMethod.MIFFLIN_ST_JEOR,
        weight_change_kcal_per_kg: float = KCAL_PER_KG_WEIGHT_CHANGE
    ):
        self.default_equation = default_equation
        self.weight_change_kcal_per_kg = weight_change_kcal_per_kg
    
    def calculate_bmr(
        self,
        anthropometrics: Anthropometrics,
        equation: Optional[EquationMethod] = None
    ) -> Tuple[float, EquationMethod, str]:
        """
        Calculate Basal Metabolic Rate.
        
        Returns:
            (bmr_kcal, equation_used, method_details)
        """
        eq = equation or self.default_equation
        
        if not anthropometrics.has_required_for_bmr():
            raise ValueError("Missing required anthropometrics: height_cm, weight_kg, age_years, sex")
        
        weight = anthropometrics.weight_kg
        height = anthropometrics.height_cm
        age = anthropometrics.age_years
        sex = anthropometrics.sex.value.lower()
        
        if eq == EquationMethod.MIFFLIN_ST_JEOR:
            coeff = MIFFLIN_ST_JEOR[sex]
            bmr = (coeff["weight"] * weight + 
                   coeff["height"] * height + 
                   coeff["age"] * age + 
                   coeff["constant"])
            details = (f"Mifflin-St Jeor: {coeff['weight']}×{weight} + "
                      f"{coeff['height']}×{height} + {coeff['age']}×{age} + {coeff['constant']}")
        
        elif eq == EquationMethod.HARRIS_BENEDICT:
            coeff = HARRIS_BENEDICT[sex]
            bmr = (coeff["weight"] * weight + 
                   coeff["height"] * height + 
                   coeff["age"] * age + 
                   coeff["constant"])
            details = (f"Harris-Benedict: {coeff['weight']}×{weight} + "
                      f"{coeff['height']}×{height} + {coeff['age']}×{age} + {coeff['constant']}")
        
        elif eq == EquationMethod.ICMR_FACTORIAL:
            # Use ICMR lookup table (approximate)
            icmr_energy = get_icmr_energy_target(sex, "sedentary", age)
            if icmr_energy:
                # Reverse-calculate BMR from TDEE assuming PAL=1.4
                bmr = icmr_energy / 1.4
            else:
                # Fallback to Mifflin-St Jeor
                coeff = MIFFLIN_ST_JEOR[sex]
                bmr = (coeff["weight"] * weight + 
                       coeff["height"] * height + 
                       coeff["age"] * age + 
                       coeff["constant"])
            details = f"ICMR 2020 factorial (reverse from TDEE/PAL)"
        
        else:
            raise ValueError(f"Unknown equation: {eq}")
        
        return round(bmr, 1), eq, details
    
    def calculate_tdee(
        self,
        bmr_kcal: float,
        activity_level: ActivityLevel
    ) -> float:
        """Calculate Total Daily Energy Expenditure from BMR and activity level."""
        pal = ACTIVITY_PAL_FACTORS.get(activity_level.value, 1.40)
        return round(bmr_kcal * pal, 1)
    
    def calculate_weight_adjustment(
        self,
        weight_goal: WeightGoal,
        weight_change_kg_per_week: float,
        tdee_kcal: float
    ) -> Tuple[float, float]:
        """
        Calculate calorie adjustment for weight goal.
        
        Returns:
            (adjustment_kcal, actual_weekly_change_kg)
        """
        if weight_goal == WeightGoal.MAINTAIN:
            return 0.0, 0.0
        
        # Calculate theoretical adjustment
        weekly_deficit = weight_change_kg_per_week * self.weight_change_kcal_per_kg
        daily_adjustment = weekly_deficit / 7.0
        
        if weight_goal == WeightGoal.LOSE:
            adjustment = -daily_adjustment
        elif weight_goal == WeightGoal.GAIN:
            adjustment = daily_adjustment
        else:
            adjustment = 0.0
        
        # Apply safety limits
        max_deficit = tdee_kcal * self.MAX_DEFICIT_PCT
        max_surplus = tdee_kcal * self.MAX_SURPLUS_PCT
        
        if adjustment < -max_deficit:
            adjustment = -max_deficit
            actual_weekly = (max_deficit * 7) / self.weight_change_kcal_per_kg
        elif adjustment > max_surplus:
            adjustment = max_surplus
            actual_weekly = (max_surplus * 7) / self.weight_change_kcal_per_kg
        else:
            actual_weekly = weight_change_kg_per_week
        
        return round(adjustment, 1), round(actual_weekly, 2)
    
    def apply_minimum_calories(
        self,
        target_kcal: float,
        sex: Sex
    ) -> Tuple[float, List[str]]:
        """Apply minimum safe calorie thresholds."""
        warnings = []
        min_cal = self.MIN_CALORIES_MALE if sex == Sex.MALE else self.MIN_CALORIES_FEMALE
        
        if target_kcal < min_cal:
            warnings.append(
                f"Target {target_kcal:.0f} kcal below minimum safe ({min_cal} kcal for {sex.value}). "
                f"Clamped to {min_cal} kcal. Consider slower weight loss or medical supervision."
            )
            target_kcal = min_cal
        
        return target_kcal, warnings
    
    def calculate(
        self,
        anthropometrics: Anthropometrics,
        activity_level: ActivityLevel,
        weight_goal: WeightGoal = WeightGoal.MAINTAIN,
        weight_change_kg_per_week: float = 0.5,
        equation: Optional[EquationMethod] = None
    ) -> EnergyCalculationResult:
        """
        Complete energy requirement calculation.
        
        Args:
            anthropometrics: Height, weight, age, sex
            activity_level: Physical activity level
            weight_goal: Weight management goal
            weight_change_kg_per_week: Desired rate (0.1-1.0 kg/week)
            equation: BMR equation to use (default: Mifflin-St Jeor)
            
        Returns:
            EnergyCalculationResult with all components
        """
        # Validate inputs
        if not anthropometrics.has_required_for_bmr():
            raise ValueError("Missing required anthropometrics for energy calculation")
        
        if weight_change_kg_per_week <= 0 or weight_change_kg_per_week > 1.0:
            raise ValueError("weight_change_kg_per_week must be between 0.1 and 1.0")
        
        # Step 1: Calculate BMR
        bmr_kcal, eq_used, bmr_details = self.calculate_bmr(anthropometrics, equation)
        
        # Step 2: Calculate TDEE
        tdee_kcal = self.calculate_tdee(bmr_kcal, activity_level)
        
        # Step 3: Calculate weight adjustment
        adjustment_kcal, actual_weekly = self.calculate_weight_adjustment(
            weight_goal, weight_change_kg_per_week, tdee_kcal
        )
        
        # Step 4: Calculate target
        target_energy = tdee_kcal + adjustment_kcal
        
        # Step 5: Apply minimum safety
        target_energy, min_warnings = self.apply_minimum_calories(target_energy, anthropometrics.sex)
        
        # Recalculate actual adjustment after clamping
        actual_adjustment = target_energy - tdee_kcal
        
        # Compile warnings
        warnings = []
        warnings.extend(min_warnings)
        
        if actual_weekly < weight_change_kg_per_week * 0.8:
            warnings.append(
                f"Weight change rate limited to {actual_weekly:.2f} kg/week "
                f"(requested {weight_change_kg_per_week} kg/week) for safety"
            )
        
        if equation and equation != EquationMethod.MIFFLIN_ST_JEOR:
            warnings.append(f"Using {equation.value} equation (Mifflin-St Jeor is recommended)")
        
        # Compare with ICMR reference if available
        icmr_target = get_icmr_energy_target(
            anthropometrics.sex.value.lower(), 
            activity_level.value.lower(), 
            anthropometrics.age_years
        )
        if icmr_target:
            icmr_diff = abs(target_energy - icmr_target) / icmr_target * 100
            if icmr_diff > 15:
                warnings.append(
                    f"Target ({target_energy:.0f} kcal) differs from ICMR 2020 reference "
                    f"({icmr_target} kcal) by {icmr_diff:.0f}%"
                )
        
        return EnergyCalculationResult(
            bmr_kcal=bmr_kcal,
            tdee_kcal=tdee_kcal,
            target_energy_kcal=round(target_energy, 1),
            equation_used=eq_used,
            activity_level=activity_level,
            weight_goal=weight_goal,
            weight_change_kg_per_week=actual_weekly,
            adjustment_kcal=round(actual_adjustment, 1),
            components={
                "bmr": bmr_kcal,
                "activity_factor": ACTIVITY_PAL_FACTORS[activity_level.value],
                "tdee": tdee_kcal,
                "weight_adjustment": actual_adjustment,
            },
            warnings=warnings,
            method_details=f"BMR: {bmr_details}; TDEE = BMR × {ACTIVITY_PAL_FACTORS[activity_level.value]} (PAL)"
        )
    
    def compare_equations(self, anthropometrics: Anthropometrics) -> Dict:
        """Compare BMR estimates from different equations."""
        if not anthropometrics.has_required_for_bmr():
            raise ValueError("Missing required anthropometrics")
        
        results = {}
        for eq in EquationMethod:
            bmr, _, details = self.calculate_bmr(anthropometrics, eq)
            results[eq.value] = {
                "bmr_kcal": bmr,
                "details": details
            }
        return results


def calculate_energy_requirements(
    height_cm: float,
    weight_kg: float,
    age_years: int,
    sex: str,
    activity_level: str,
    weight_goal: str = "MAINTAIN",
    weight_change_kg_per_week: float = 0.5
) -> EnergyCalculationResult:
    """Convenience function for quick energy calculation."""
    anthropometrics = Anthropometrics(
        height_cm=height_cm,
        weight_kg=weight_kg,
        age_years=age_years,
        sex=Sex(sex.upper())
    )
    calculator = EnergyCalculator()
    return calculator.calculate(
        anthropometrics=anthropometrics,
        activity_level=ActivityLevel(activity_level.upper()),
        weight_goal=WeightGoal(weight_goal.upper()),
        weight_change_kg_per_week=weight_change_kg_per_week
    )


def calculate_energy_only(
    height_cm: float,
    weight_kg: float,
    age_years: int,
    sex: str,
    activity_level: str,
    weight_goal: str = "MAINTAIN",
    weight_change_kg_per_week: float = 0.5
) -> EnergyCalculationResult:
    """Alias for calculate_energy_requirements for backwards compatibility."""
    return calculate_energy_requirements(
        height_cm=height_cm,
        weight_kg=weight_kg,
        age_years=age_years,
        sex=sex,
        activity_level=activity_level,
        weight_goal=weight_goal,
        weight_change_kg_per_week=weight_change_kg_per_week
    )