"""Profile Validation - Validate user profiles for completeness and consistency."""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re

from .profile_models import (
    UserProfile, Anthropometrics, DietaryProfile, NutritionalGoals, LifestyleProfile,
    Sex, ActivityLevel, DietaryPreference, WeightGoal, MealFrequency, MealSlot
)


class ValidationSeverity(Enum):
    """Validation issue severity."""
    ERROR = "ERROR"       # Blocks profile usage
    WARNING = "WARNING"   # May affect results, but usable
    INFO = "INFO"         # Informational


@dataclass
class ValidationIssue:
    """Single validation issue."""
    field: str
    severity: ValidationSeverity
    message: str
    expected: Optional[str] = None
    actual: Optional[Any] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of profile validation."""
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    errors: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    info: List[ValidationIssue] = field(default_factory=list)

    def add_issue(self, issue: ValidationIssue):
        self.issues.append(issue)
        if issue.severity == ValidationSeverity.ERROR:
            self.errors.append(issue)
            self.is_valid = False
        elif issue.severity == ValidationSeverity.WARNING:
            self.warnings.append(issue)
        elif issue.severity == ValidationSeverity.INFO:
            self.info.append(issue)

    def has_errors(self) -> bool:
        return len(self.errors) > 0


class ProfileValidator:
    """Validate user profiles for completeness and consistency."""

    # Valid ranges
    HEIGHT_CM_RANGE = (50.0, 250.0)
    WEIGHT_KG_RANGE = (2.0, 300.0)
    AGE_YEARS_RANGE = (1, 120)
    BMI_RANGE = (10.0, 60.0)
    ENERGY_KCAL_RANGE = (500, 5000)
    PROTEIN_G_RANGE = (10, 300)
    CARB_G_RANGE = (20, 500)
    FAT_G_RANGE = (10, 200)
    FIBRE_G_RANGE = (5, 100)
    WEIGHT_CHANGE_RATE_RANGE = (0.1, 1.0)  # kg/week
    TIME_CONSTRAINT_RANGE = (5, 180)  # minutes

    # Known Indian cuisines (from recipe dataset)
    KNOWN_CUISINES = {
        "north indian", "south indian", "gujarati", "maharashtrian", "punjabi",
        "bengali", "rajasthani", "kashmiri", "kerala", "andhra", "tamil",
        "karnataka", "goan", "chettinad", "hyderabadi", "awadhi", "muglai",
        "street food", "chaat", "beverages", "desserts", "snacks", "breakfast",
        "pickles", "preserves", "festive", "fasting", "jain", "satvik"
    }

    # Common allergens
    KNOWN_ALLERGENS = {
        "peanut", "tree nut", "milk", "egg", "wheat", "soy", "fish", "shellfish",
        "sesame", "mustard", "celery", "lupin", "mollusc", "sulphite"
    }

    def __init__(self, strict_mode: bool = False):
        """
        Initialize validator.
        
        Args:
            strict_mode: If True, warnings become errors for profile usage
        """
        self.strict_mode = strict_mode

    def validate(self, profile: UserProfile) -> ValidationResult:
        """Validate a complete user profile."""
        result = ValidationResult(is_valid=True)
        
        # Validate each component
        self._validate_anthropometrics(profile.anthropometrics, result)
        self._validate_dietary_profile(profile.dietary_profile, result)
        self._validate_nutritional_goals(profile.nutritional_goals, profile.anthropometrics, result)
        self._validate_lifestyle(profile.lifestyle, result)
        
        # Cross-field validation
        self._validate_cross_field_consistency(profile, result)
        
        # In strict mode, warnings become errors
        if self.strict_mode:
            for warning in result.warnings:
                result.add_issue(ValidationIssue(
                    field=warning.field,
                    severity=ValidationSeverity.ERROR,
                    message=f"[STRICT] {warning.message}",
                    expected=warning.expected,
                    actual=warning.actual,
                    suggestion=warning.suggestion,
                ))
        
        return result

    def _validate_anthropometrics(self, anthro: Anthropometrics, result: ValidationResult):
        """Validate physical measurements."""
        # Height
        if anthro.height_cm is not None:
            min_h, max_h = self.HEIGHT_CM_RANGE
            if not (min_h <= anthro.height_cm <= max_h):
                result.add_issue(ValidationIssue(
                    field="anthropometrics.height_cm",
                    severity=ValidationSeverity.ERROR,
                    message=f"Height {anthro.height_cm} cm outside valid range [{min_h}, {max_h}]",
                    expected=f"{min_h}-{max_h} cm",
                    actual=f"{anthro.height_cm} cm",
                    suggestion="Enter height in centimeters (e.g., 170)"
                ))
        else:
            result.add_issue(ValidationIssue(
                field="anthropometrics.height_cm",
                severity=ValidationSeverity.WARNING,
                message="Height not provided - required for BMR calculation",
                suggestion="Provide height in cm for accurate energy calculations"
            ))

        # Weight
        if anthro.weight_kg is not None:
            min_w, max_w = self.WEIGHT_KG_RANGE
            if not (min_w <= anthro.weight_kg <= max_w):
                result.add_issue(ValidationIssue(
                    field="anthropometrics.weight_kg",
                    severity=ValidationSeverity.ERROR,
                    message=f"Weight {anthro.weight_kg} kg outside valid range [{min_w}, {max_w}]",
                    expected=f"{min_w}-{max_w} kg",
                    actual=f"{anthro.weight_kg} kg",
                    suggestion="Enter weight in kilograms (e.g., 70)"
                ))
        else:
            result.add_issue(ValidationIssue(
                field="anthropometrics.weight_kg",
                severity=ValidationSeverity.WARNING,
                message="Weight not provided - required for BMR calculation",
                suggestion="Provide weight in kg for accurate energy calculations"
            ))

        # Age
        if anthro.age_years is not None:
            min_a, max_a = self.AGE_YEARS_RANGE
            if not (min_a <= anthro.age_years <= max_a):
                result.add_issue(ValidationIssue(
                    field="anthropometrics.age_years",
                    severity=ValidationSeverity.ERROR,
                    message=f"Age {anthro.age_years} outside valid range [{min_a}, {max_a}]",
                    expected=f"{min_a}-{max_a} years",
                    actual=f"{anthro.age_years} years",
                    suggestion="Enter age in years"
                ))
        else:
            result.add_issue(ValidationIssue(
                field="anthropometrics.age_years",
                severity=ValidationSeverity.WARNING,
                message="Age not provided - required for BMR calculation",
                suggestion="Provide age in years for accurate energy calculations"
            ))

        # Sex
        if anthro.sex is None:
            result.add_issue(ValidationIssue(
                field="anthropometrics.sex",
                severity=ValidationSeverity.WARNING,
                message="Sex not provided - required for BMR calculation (Mifflin-St Jeor uses sex)",
                suggestion="Provide sex (MALE/FEMALE) for accurate energy calculations"
            ))

        # BMI check (if both height and weight present)
        if anthro.height_cm and anthro.weight_kg:
            height_m = anthro.height_cm / 100.0
            bmi = anthro.weight_kg / (height_m * height_m)
            min_bmi, max_bmi = self.BMI_RANGE
            if not (min_bmi <= bmi <= max_bmi):
                result.add_issue(ValidationIssue(
                    field="anthropometrics.bmi",
                    severity=ValidationSeverity.WARNING,
                    message=f"Calculated BMI {bmi:.1f} outside typical range [{min_bmi}, {max_bmi}]",
                    expected=f"{min_bmi}-{max_bmi}",
                    actual=f"{bmi:.1f}",
                    suggestion="Verify height and weight entries"
                ))

    def _validate_dietary_profile(self, dietary: DietaryProfile, result: ValidationResult):
        """Validate dietary preferences and restrictions."""
        # Check for conflicts between preference and exclusions
        if dietary.preference == DietaryPreference.VEGAN:
            non_vegan_exclusions = [ing for ing in dietary.ingredient_exclusions 
                                   if ing.lower() in ["tofu", "tempeh", "legumes", "lentils", "beans", "chickpeas"]]
            if non_vegan_exclusions:
                result.add_issue(ValidationIssue(
                    field="dietary_profile.ingredient_exclusions",
                    severity=ValidationSeverity.WARNING,
                    message=f"Vegan preference with plant-protein exclusions: {non_vegan_exclusions}",
                    suggestion="Verify these exclusions are intentional"
                ))

        # Check allergens against known list
        unknown_allergens = []
        for allergen in dietary.allergies:
            if allergen.lower() not in [a.lower() for a in self.KNOWN_ALLERGENS]:
                unknown_allergens.append(allergen)
        if unknown_allergens:
            result.add_issue(ValidationIssue(
                field="dietary_profile.allergies",
                severity=ValidationSeverity.INFO,
                message=f"Unrecognized allergens (may need manual verification): {unknown_allergens}",
                suggestion="Ensure allergen names match ingredient database entries"
            ))

        # Check cuisine preferences against known
        unknown_cuisines = []
        for cuisine in dietary.cuisine_preferences:
            if cuisine.lower() not in self.KNOWN_CUISINES:
                unknown_cuisines.append(cuisine)
        if unknown_cuisines:
            result.add_issue(ValidationIssue(
                field="dietary_profile.cuisine_preferences",
                severity=ValidationSeverity.INFO,
                message=f"Cuisines not in known dataset: {unknown_cuisines}",
                suggestion="May limit recipe matches; verify spelling"
            ))

        # Jain compatibility check
        if dietary.preference == DietaryPreference.JAIN:
            # Jain diet excludes root vegetables, certain fermented foods
            root_veggies = ["onion", "garlic", "potato", "carrot", "radish", "beetroot", "ginger", "turmeric"]
            conflicts = [v for v in root_veggies if v not in dietary.ingredient_exclusions]
            if conflicts:
                result.add_issue(ValidationIssue(
                    field="dietary_profile.ingredient_exclusions",
                    severity=ValidationSeverity.WARNING,
                    message=f"Jain preference but root vegetables not excluded: {conflicts}",
                    suggestion="Add root vegetables to ingredient_exclusions for strict Jain compliance"
                ))

    def _validate_nutritional_goals(self, goals: NutritionalGoals, anthro: Anthropometrics, result: ValidationResult):
        """Validate nutritional goals."""
        # Energy target
        if goals.target_energy_kcal is not None:
            min_e, max_e = self.ENERGY_KCAL_RANGE
            if not (min_e <= goals.target_energy_kcal <= max_e):
                result.add_issue(ValidationIssue(
                    field="nutritional_goals.target_energy_kcal",
                    severity=ValidationSeverity.ERROR,
                    message=f"Target energy {goals.target_energy_kcal} kcal outside safe range [{min_e}, {max_e}]",
                    expected=f"{min_e}-{max_e} kcal",
                    actual=f"{goals.target_energy_kcal} kcal",
                    suggestion="Consult a healthcare professional for extreme calorie targets"
                ))

        # Protein target
        if goals.target_protein_g is not None:
            min_p, max_p = self.PROTEIN_G_RANGE
            if not (min_p <= goals.target_protein_g <= max_p):
                result.add_issue(ValidationIssue(
                    field="nutritional_goals.target_protein_g",
                    severity=ValidationSeverity.ERROR,
                    message=f"Target protein {goals.target_protein_g} g outside safe range [{min_p}, {max_p}]",
                    expected=f"{min_p}-{max_p} g",
                    actual=f"{goals.target_protein_g} g",
                    suggestion="Protein above 2g/kg body weight may stress kidneys"
                ))
            # Check against body weight if available
            if anthro.weight_kg:
                protein_per_kg = goals.target_protein_g / anthro.weight_kg
                if protein_per_kg > 2.5:
                    result.add_issue(ValidationIssue(
                        field="nutritional_goals.target_protein_g",
                        severity=ValidationSeverity.WARNING,
                        message=f"Protein target {goals.target_protein_g}g = {protein_per_kg:.1f}g/kg body weight",
                        suggestion="Protein above 2.5g/kg may not provide additional benefit"
                    ))

        # Carbohydrate target
        if goals.target_carbohydrate_g is not None:
            min_c, max_c = self.CARB_G_RANGE
            if not (min_c <= goals.target_carbohydrate_g <= max_c):
                result.add_issue(ValidationIssue(
                    field="nutritional_goals.target_carbohydrate_g",
                    severity=ValidationSeverity.ERROR,
                    message=f"Target carbohydrate {goals.target_carbohydrate_g} g outside range [{min_c}, {max_c}]",
                    expected=f"{min_c}-{max_c} g",
                    actual=f"{goals.target_carbohydrate_g} g"
                ))

        # Fat target
        if goals.target_fat_g is not None:
            min_f, max_f = self.FAT_G_RANGE
            if not (min_f <= goals.target_fat_g <= max_f):
                result.add_issue(ValidationIssue(
                    field="nutritional_goals.target_fat_g",
                    severity=ValidationSeverity.ERROR,
                    message=f"Target fat {goals.target_fat_g} g outside range [{min_f}, {max_f}]",
                    expected=f"{min_f}-{max_f} g",
                    actual=f"{goals.target_fat_g} g"
                ))

        # Fibre target
        if goals.target_fibre_g is not None:
            min_f, max_f = self.FIBRE_G_RANGE
            if not (min_f <= goals.target_fibre_g <= max_f):
                result.add_issue(ValidationIssue(
                    field="nutritional_goals.target_fibre_g",
                    severity=ValidationSeverity.ERROR,
                    message=f"Target fibre {goals.target_fibre_g} g outside range [{min_f}, {max_f}]",
                    expected=f"{min_f}-{max_f} g",
                    actual=f"{goals.target_fibre_g} g"
                ))

        # Weight change rate
        min_wc, max_wc = self.WEIGHT_CHANGE_RATE_RANGE
        if not (min_wc <= goals.weight_change_rate_kg_per_week <= max_wc):
            result.add_issue(ValidationIssue(
                field="nutritional_goals.weight_change_rate_kg_per_week",
                severity=ValidationSeverity.ERROR if goals.weight_change_rate_kg_per_week > 1.0 else ValidationSeverity.WARNING,
                message=f"Weight change rate {goals.weight_change_rate_kg_per_week} kg/week outside recommended range [{min_wc}, {max_wc}]",
                expected=f"{min_wc}-{max_wc} kg/week",
                actual=f"{goals.weight_change_rate_kg_per_week} kg/week",
                suggestion="Rapid weight loss (>1 kg/week) may cause muscle loss and nutrient deficiencies"
            ))

        # Check macro distribution if all provided
        if all(v is not None for v in [goals.target_protein_g, goals.target_carbohydrate_g, goals.target_fat_g]):
            if goals.target_energy_kcal:
                protein_kcal = goals.target_protein_g * 4
                carb_kcal = goals.target_carbohydrate_g * 4
                fat_kcal = goals.target_fat_g * 9
                total_calc = protein_kcal + carb_kcal + fat_kcal
                diff_pct = abs(total_calc - goals.target_energy_kcal) / goals.target_energy_kcal * 100
                if diff_pct > 10:
                    result.add_issue(ValidationIssue(
                        field="nutritional_goals.macro_consistency",
                        severity=ValidationSeverity.WARNING,
                        message=f"Macro calories ({total_calc:.0f}) differ from energy target ({goals.target_energy_kcal}) by {diff_pct:.1f}%",
                        suggestion="Check macro targets consistency with energy target"
                    ))

    def _validate_lifestyle(self, lifestyle: LifestyleProfile, result: ValidationResult):
        """Validate lifestyle profile."""
        # Time constraint
        if lifestyle.time_constraint_minutes is not None:
            min_t, max_t = self.TIME_CONSTRAINT_RANGE
            if not (min_t <= lifestyle.time_constraint_minutes <= max_t):
                result.add_issue(ValidationIssue(
                    field="lifestyle.time_constraint_minutes",
                    severity=ValidationSeverity.WARNING,
                    message=f"Time constraint {lifestyle.time_constraint_minutes} min outside typical range [{min_t}, {max_t}]",
                    expected=f"{min_t}-{max_t} minutes",
                    actual=f"{lifestyle.time_constraint_minutes} minutes"
                ))

        # Meal frequency vs distribution
        if lifestyle.meal_frequency == MealFrequency.THREE:
            result.add_issue(ValidationIssue(
                field="lifestyle.meal_frequency",
                severity=ValidationSeverity.INFO,
                message="3 meals/day - snacks will not be planned",
                suggestion="Consider 4-5 meals for better nutrient distribution"
            ))

    def _validate_cross_field_consistency(self, profile: UserProfile, result: ValidationResult):
        """Validate cross-field consistency."""
        anthro = profile.anthropometrics
        goals = profile.nutritional_goals
        dietary = profile.dietary_profile
        lifestyle = profile.lifestyle

        # Weight goal vs energy target consistency
        if goals.target_energy_kcal is not None and anthro.weight_kg is not None:
            # Rough check: maintenance calories should be around BMR * activity_factor
            if goals.weight_goal == WeightGoal.MAINTAIN:
                pass  # No specific check needed
            elif goals.weight_goal == WeightGoal.LOSE:
                if goals.target_energy_kcal > 2500:
                    result.add_issue(ValidationIssue(
                        field="nutritional_goals.target_energy_kcal",
                        severity=ValidationSeverity.WARNING,
                        message=f"Weight loss target with {goals.target_energy_kcal} kcal may be too high",
                        suggestion="Typical weight loss diets are 1200-1800 kcal depending on body size"
                    ))
            elif goals.weight_goal == WeightGoal.GAIN:
                if goals.target_energy_kcal < 2000:
                    result.add_issue(ValidationIssue(
                        field="nutritional_goals.target_energy_kcal",
                        severity=ValidationSeverity.WARNING,
                        message=f"Weight gain target with {goals.target_energy_kcal} kcal may be too low",
                        suggestion="Weight gain typically requires surplus of 300-500 kcal above maintenance"
                    ))

        # Vegetarian preference vs non-veg cuisine preferences
        if dietary.preference in (DietaryPreference.VEGETARIAN, DietaryPreference.VEGAN, DietaryPreference.JAIN):
            non_veg_cuisines = ["mughlai", "awadhi", "chettinad", "hyderabadi"]  # Often meat-heavy
            conflicts = [c for c in dietary.cuisine_preferences if c.lower() in non_veg_cuisines]
            if conflicts:
                result.add_issue(ValidationIssue(
                    field="dietary_profile.cuisine_preferences",
                    severity=ValidationSeverity.WARNING,
                    message=f"Vegetarian preference with meat-heavy cuisine preferences: {conflicts}",
                    suggestion="These cuisines may have limited vegetarian options"
                ))

        # Allergies vs ingredient exclusions overlap
        allergy_ingredients = set(a.lower() for a in dietary.allergies)
        excluded_ingredients = set(e.lower() for e in dietary.ingredient_exclusions)
        if not allergy_ingredients.issubset(excluded_ingredients):
            missing = allergy_ingredients - excluded_ingredients
            result.add_issue(ValidationIssue(
                field="dietary_profile.ingredient_exclusions",
                severity=ValidationSeverity.WARNING,
                message=f"Allergens not in ingredient_exclusions: {missing}",
                suggestion="Add allergens to ingredient_exclusions for automatic filtering"
            ))

        # Activity level vs energy target
        if anthro.has_required_for_bmr() and goals.target_energy_kcal:
            # Rough BMR estimate
            if anthro.sex == Sex.MALE:
                bmr = 10 * anthro.weight_kg + 6.25 * anthro.height_cm - 5 * anthro.age_years + 5
            else:
                bmr = 10 * anthro.weight_kg + 6.25 * anthro.height_cm - 5 * anthro.age_years - 161
            
            activity_factors = {
                ActivityLevel.SEDENTARY: 1.2,
                ActivityLevel.LIGHTLY_ACTIVE: 1.375,
                ActivityLevel.MODERATELY_ACTIVE: 1.55,
                ActivityLevel.VERY_ACTIVE: 1.725,
                ActivityLevel.EXTREMELY_ACTIVE: 1.9,
            }
            tdee = bmr * activity_factors.get(lifestyle.activity_level, 1.2)
            
            diff_pct = abs(goals.target_energy_kcal - tdee) / tdee * 100
            if diff_pct > 30:
                result.add_issue(ValidationIssue(
                    field="nutritional_goals.target_energy_kcal",
                    severity=ValidationSeverity.WARNING,
                    message=f"Target energy ({goals.target_energy_kcal}) differs from estimated TDEE ({tdee:.0f}) by {diff_pct:.0f}%",
                    expected=f"~{tdee:.0f} kcal (estimated)",
                    actual=f"{goals.target_energy_kcal} kcal",
                    suggestion="Large discrepancy may indicate incorrect activity level or target"
                ))

    def validate_for_nutrition_calculation(self, profile: UserProfile) -> ValidationResult:
        """Quick validation for minimum requirements for nutrition calculation."""
        result = ValidationResult(is_valid=True)
        
        if not profile.has_minimum_for_nutrition_calculation():
            missing = []
            anthro = profile.anthropometrics
            if anthro.height_cm is None: missing.append("height_cm")
            if anthro.weight_kg is None: missing.append("weight_kg")
            if anthro.age_years is None: missing.append("age_years")
            if anthro.sex is None: missing.append("sex")
            
            result.add_issue(ValidationIssue(
                field="anthropometrics",
                severity=ValidationSeverity.ERROR,
                message=f"Missing required fields for nutrition calculation: {', '.join(missing)}",
                suggestion="Provide height, weight, age, and sex for BMR calculation"
            ))
        
        return result


def validate_profile(profile: UserProfile, strict: bool = False) -> ValidationResult:
    """Convenience function to validate a profile."""
    validator = ProfileValidator(strict_mode=strict)
    return validator.validate(profile)