"""Nutrition Targets - Main interface for calculating user nutrition targets."""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from .profile_models import UserProfile, Anthropometrics, Sex, ActivityLevel, WeightGoal, MealFrequency
from .energy_requirements import EnergyCalculator, EnergyCalculationResult, calculate_energy_requirements
from .macro_targets import (
    MacroCalculator, MicronutrientCalculator, MacroDistributionMethod,
    MacroTargets, MicronutrientTargets, CompleteNutritionTargets,
    calculate_nutrition_targets
)
from .reference_values import get_meal_distribution
from .profile_validation import ValidationResult, ValidationIssue, ValidationSeverity


class NutritionTargetCalculator:
    """
    Main calculator for user nutrition targets.
    
    Integrates energy requirements, macro targets, and micronutrient targets.
    """
    
    def __init__(
        self,
        default_macro_method: MacroDistributionMethod = MacroDistributionMethod.ICMR_BALANCED
    ):
        self.energy_calculator = EnergyCalculator()
        self.macro_calculator = MacroCalculator()
        self.micro_calculator = MicronutrientCalculator()
        self.default_macro_method = default_macro_method
    
    def calculate_for_profile(
        self,
        profile: UserProfile,
        macro_method: Optional[MacroDistributionMethod] = None,
        use_profile_meal_distribution: bool = True
    ) -> CompleteNutritionTargets:
        """
        Calculate complete nutrition targets for a user profile.
        
        Args:
            profile: Validated UserProfile
            macro_method: Macro distribution method (uses profile default if None)
            use_profile_meal_distribution: Use profile's meal frequency for per-meal targets
            
        Returns:
            CompleteNutritionTargets with all calculations
        """
        # Use profile's macro method if not specified
        method = macro_method or self.default_macro_method
        
        # Get meal distribution from profile
        meal_dist = None
        if use_profile_meal_distribution:
            meal_dist = get_meal_distribution(profile.lifestyle.meal_frequency)
        
        # Calculate energy requirements
        energy_result = self.energy_calculator.calculate(
            anthropometrics=profile.anthropometrics,
            activity_level=profile.lifestyle.activity_level,
            weight_goal=profile.nutritional_goals.weight_goal,
            weight_change_kg_per_week=profile.nutritional_goals.weight_change_rate_kg_per_week
        )
        
        # Calculate macro targets
        macro_targets = self.macro_calculator.calculate(
            energy_result=energy_result,
            anthropometrics=profile.anthropometrics,
            weight_goal=profile.nutritional_goals.weight_goal,
            method=method,
            meal_distribution=meal_dist
        )
        
        # Calculate micronutrient targets
        micro_targets = self.micro_calculator.calculate(
            profile.anthropometrics,
            profile.nutritional_goals.weight_goal
        )
        
        # Build complete targets
        targets = CompleteNutritionTargets(
            energy=energy_result,
            macros=macro_targets,
            micros=micro_targets,
            meal_targets=macro_targets.per_meal,
            profile_id=profile.user_id
        )
        
        return targets
    
    def calculate_with_overrides(
        self,
        profile: UserProfile,
        target_energy_kcal: Optional[float] = None,
        target_protein_g: Optional[float] = None,
        target_fat_g: Optional[float] = None,
        target_carb_g: Optional[float] = None,
        macro_method: Optional[MacroDistributionMethod] = None
    ) -> CompleteNutritionTargets:
        """
        Calculate nutrition targets with manual overrides.
        
        Useful when user has specific targets from healthcare provider.
        """
        # This would require modifying the calculators to accept overrides
        # For now, calculate standard and note overrides in warnings
        targets = self.calculate_for_profile(profile, macro_method)
        
        warnings = list(targets.macros.warnings)
        if target_energy_kcal is not None:
            warnings.append(f"Manual energy target: {target_energy_kcal} kcal (calculated: {targets.energy.target_energy_kcal})")
        if target_protein_g is not None:
            warnings.append(f"Manual protein target: {target_protein_g}g (calculated: {targets.macros.protein_g})")
        if target_fat_g is not None:
            warnings.append(f"Manual fat target: {target_fat_g}g (calculated: {targets.macros.fat_g})")
        if target_carb_g is not None:
            warnings.append(f"Manual carb target: {target_carb_g}g (calculated: {targets.macros.carbohydrate_g})")
        
        targets.macros.warnings = warnings
        return targets
    
    def validate_targets(self, targets: CompleteNutritionTargets) -> ValidationResult:
        """Validate calculated nutrition targets for consistency."""
        result = ValidationResult(is_valid=True)
        
        # Energy validation
        energy = targets.energy
        if energy.target_energy_kcal < 800:
            result.add_issue(ValidationIssue(
                field="energy.target_energy_kcal",
                severity=ValidationSeverity.ERROR,
                message=f"Target energy {energy.target_energy_kcal:.0f} kcal dangerously low",
                suggestion="Minimum 800 kcal requires medical supervision"
            ))
        elif energy.target_energy_kcal < 1200:
            result.add_issue(ValidationIssue(
                field="energy.target_energy_kcal",
                severity=ValidationSeverity.WARNING,
                message=f"Target energy {energy.target_energy_kcal:.0f} kcal very low",
                suggestion="Consider slower weight loss or medical supervision"
            ))
        
        # Macro validation
        macros = targets.macros
        if macros.macro_total_pct < 95 or macros.macro_total_pct > 105:
            result.add_issue(ValidationIssue(
                field="macros.distribution",
                severity=ValidationSeverity.WARNING,
                message=f"Macro percentages sum to {macros.macro_total_pct:.1f}% (should be ~100%)",
                suggestion="Check protein, fat, carb calculations"
            ))
        
        # Protein per kg check
        if targets.energy.bmr_kcal > 0 and targets.macros.protein_g > 0:
            # Need weight for this - would need profile
            pass
        
        # Fibre check
        if macros.fibre_g < 15:
            result.add_issue(ValidationIssue(
                field="macros.fibre_g",
                severity=ValidationSeverity.WARNING,
                message=f"Fibre target {macros.fibre_g:.1f}g below recommended minimum (20g)",
                suggestion="Increase whole grains, pulses, vegetables"
            ))
        
        # Micronutrient checks
        micros = targets.micros
        if micros.sodium_mg and micros.sodium_mg > 2300:
            result.add_issue(ValidationIssue(
                field="micros.sodium_mg",
                severity=ValidationSeverity.WARNING,
                message=f"Sodium target {micros.sodium_mg:.0f}mg exceeds WHO limit (2000mg)",
                suggestion="Reduce salt in meal planning"
            ))
        
        return result
    
    def get_daily_summary(self, targets: CompleteNutritionTargets) -> Dict:
        """Get a human-readable daily nutrition summary."""
        return {
            "energy_kcal": round(targets.energy.target_energy_kcal),
            "protein_g": round(targets.macros.protein_g),
            "carbohydrate_g": round(targets.macros.carbohydrate_g),
            "fat_g": round(targets.macros.fat_g),
            "fibre_g": round(targets.macros.fibre_g),
            "macro_distribution": {
                "protein_pct": targets.macros.protein_pct,
                "carb_pct": targets.macros.carbohydrate_pct,
                "fat_pct": targets.macros.fat_pct,
            },
            "micronutrients": {
                "sodium_mg": targets.micros.sodium_mg,
                "potassium_mg": targets.micros.potassium_mg,
                "calcium_mg": targets.micros.calcium_mg,
                "iron_mg": targets.micros.iron_mg,
                "fibre_g": targets.macros.fibre_g,
            },
            "per_meal": targets.meal_targets,
            "warnings": targets.macros.warnings,
        }


def calculate_user_nutrition_targets(
    profile: UserProfile,
    macro_method: Optional[MacroDistributionMethod] = None
) -> CompleteNutritionTargets:
    """
    Convenience function to calculate complete nutrition targets for a profile.
    
    This is the main entry point for nutrition target calculation.
    """
    calculator = NutritionTargetCalculator()
    return calculator.calculate_for_profile(profile, macro_method)


def calculate_energy_only(
    height_cm: float,
    weight_kg: float,
    age_years: int,
    sex: str,
    activity_level: str,
    weight_goal: str = "MAINTAIN",
    weight_change_kg_per_week: float = 0.5
) -> EnergyCalculationResult:
    """Quick energy calculation without full profile."""
    return calculate_energy_requirements(
        height_cm=height_cm,
        weight_kg=weight_kg,
        age_years=age_years,
        sex=Sex(sex.upper()),
        activity_level=ActivityLevel(activity_level.upper()),
        weight_goal=WeightGoal(weight_goal.upper()),
        weight_change_kg_per_week=weight_change_kg_per_week
    )


# Preset calculators for common scenarios
def calculate_weight_loss_targets(profile: UserProfile) -> CompleteNutritionTargets:
    """Calculate targets optimized for weight loss."""
    calculator = NutritionTargetCalculator(default_macro_method=MacroDistributionMethod.HIGH_PROTEIN)
    return calculator.calculate_for_profile(profile, MacroDistributionMethod.HIGH_PROTEIN)


def calculate_muscle_gain_targets(profile: UserProfile) -> CompleteNutritionTargets:
    """Calculate targets optimized for muscle gain."""
    calculator = NutritionTargetCalculator(default_macro_method=MacroDistributionMethod.HIGH_PROTEIN)
    return calculator.calculate_for_profile(profile, MacroDistributionMethod.HIGH_PROTEIN)


def calculate_maintenance_targets(profile: UserProfile) -> CompleteNutritionTargets:
    """Calculate targets for weight maintenance."""
    calculator = NutritionTargetCalculator(default_macro_method=MacroDistributionMethod.ICMR_BALANCED)
    return calculator.calculate_for_profile(profile, MacroDistributionMethod.ICMR_BALANCED)


def calculate_diabetes_targets(profile: UserProfile) -> CompleteNutritionTargets:
    """Calculate targets suitable for diabetes management (lower carb)."""
    calculator = NutritionTargetCalculator(default_macro_method=MacroDistributionMethod.LOW_CARB)
    return calculator.calculate_for_profile(profile, MacroDistributionMethod.LOW_CARB)


def calculate_heart_health_targets(profile: UserProfile) -> CompleteNutritionTargets:
    """Calculate targets for cardiovascular health (Mediterranean-style)."""
    calculator = NutritionTargetCalculator(default_macro_method=MacroDistributionMethod.ICMR_BALANCED)
    return calculator.calculate_for_profile(profile, MacroDistributionMethod.ICMR_BALANCED)