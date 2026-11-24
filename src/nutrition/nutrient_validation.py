"""Nutrient Validation - Validate calculated nutrient values."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import numpy as np


class ValidationSeverity(Enum):
    """Validation severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ValidationIssue:
    """Validation issue found during nutrient validation."""
    severity: ValidationSeverity
    field: str
    message: str
    expected_range: Optional[Tuple[float, float]] = None
    actual_value: Any = None
    suggestion: str = ""
    
    def __str__(self) -> str:
        return f"[{self.severity.value}] {self.field}: {self.message}"


@dataclass
class ValidationResult:
    """Result of nutrient validation."""
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    errors: List[ValidationIssue] = field(default_factory=list)
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    @property
    def has_critical(self) -> bool:
        return any(i.severity == ValidationSeverity.CRITICAL for i in self.issues)
    
    def add_issue(self, issue: ValidationIssue):
        self.issues.append(issue)
        if issue.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL):
            self.errors.append(issue)
            self.is_valid = False
        elif issue.severity == ValidationSeverity.WARNING:
            self.warnings.append(issue)


# Nutrient validation ranges (per 100g edible portion)
# Based on IFCT 2017 and general food composition knowledge
NUTRIENT_RANGES_PER_100G = {
    'moisture_g': (0, 100),
    'protein_g': (0, 40),
    'ash_g': (0, 10),
    'fat_g': (0, 100),
    'fibre_total_g': (0, 50),
    'fibre_insoluble_g': (0, 50),
    'fibre_soluble_g': (0, 30),
    'carb_available_g': (0, 100),
    'energy_kj': (0, 3500),  # ~837 kcal max for pure fat
}

# Atwater factors for energy validation
ATWATER_FACTORS = {
    'protein_g': 17,    # kJ/g
    'fat_g': 37,        # kJ/g
    'carb_available_g': 17,  # kJ/g
    'fibre_total_g': 8,  # kJ/g (fermentable fibre)
}


class NutrientValidator:
    """Validate nutrient values for consistency and reasonableness."""
    
    def __init__(
        self,
        ranges: Optional[Dict[str, Tuple[float, float]]] = None,
        atwater_factors: Optional[Dict[str, float]] = None,
        energy_tolerance_pct: float = 20.0  # Allow 20% difference
    ):
        self.ranges = ranges or NUTRIENT_RANGES_PER_100G
        self.atwater_factors = atwater_factors or ATWATER_FACTORS
        self.energy_tolerance_pct = energy_tolerance_pct
    
    def validate_per_100g_nutrients(self, nutrients: Dict[str, float]) -> ValidationResult:
        """Validate nutrient values per 100g edible portion."""
        result = ValidationResult(is_valid=True)
        
        for nutrient, value in nutrients.items():
            if value is None or np.isnan(value):
                continue
            
            # Range check
            if nutrient in self.ranges:
                min_val, max_val = self.ranges[nutrient]
                if value < min_val or value > max_val:
                    result.add_issue(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        field=nutrient,
                        message=f"Value {value} outside typical range [{min_val}, {max_val}]",
                        expected_range=(min_val, max_val),
                        actual_value=value,
                        suggestion="Verify IFCT source data"
                    ))
        
        # Energy consistency check using Atwater factors
        energy_kj = nutrients.get('energy_kj')
        if energy_kj is not None and not np.isnan(energy_kj):
            calculated_energy = self._calculate_atwater_energy(nutrients)
            if calculated_energy > 0:
                diff_pct = abs(energy_kj - calculated_energy) / energy_kj * 100
                if diff_pct > self.energy_tolerance_pct:
                    result.add_issue(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        field='energy_kj',
                        message=f"Reported energy {energy_kj} kJ differs from Atwater "
                                f"calculated {calculated_energy:.1f} kJ by {diff_pct:.1f}%",
                        expected_range=(calculated_energy * 0.8, calculated_energy * 1.2),
                        actual_value=energy_kj,
                        suggestion="Check IFCT energy value or macronutrient values"
                    ))
        
        # Macronutrient sum check (should not exceed 100g)
        macro_sum = sum(nutrients.get(n, 0) for n in 
                       ['moisture_g', 'protein_g', 'ash_g', 'fat_g', 'carb_available_g', 'fibre_total_g'])
        if macro_sum > 105:  # Allow small margin for rounding
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                field='macronutrient_sum',
                message=f"Sum of major components ({macro_sum:.1f}g) exceeds 100g per 100g",
                actual_value=macro_sum,
                suggestion="Verify component values - may include overlapping fibre/carb measures"
            ))
        
        return result
    
    def validate_ingredient_nutrients(
        self,
        calculated_nutrients: Dict[str, float],
        edible_weight_g: float,
        ifct_food_code: str
    ) -> ValidationResult:
        """Validate calculated ingredient nutrient contributions."""
        result = ValidationResult(is_valid=True)
        
        if edible_weight_g <= 0:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                field='edible_weight_g',
                message=f"Invalid edible weight: {edible_weight_g}",
                actual_value=edible_weight_g,
                suggestion="Weight must be positive"
            ))
            return result
        
        # Check for negative contributions (should not happen with valid inputs)
        for nutrient, value in calculated_nutrients.items():
            if value < 0:
                result.add_issue(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    field=nutrient,
                    message=f"Negative nutrient contribution: {value}",
                    actual_value=value,
                    suggestion="Check input nutrient values and weight"
                ))
        
        # Validate per-100g equivalents
        if edible_weight_g > 0:
            per_100g = {k: v * 100 / edible_weight_g for k, v in calculated_nutrients.items()}
            per_100g_result = self.validate_per_100g_nutrients(per_100g)
            result.issues.extend(per_100g_result.issues)
            result.warnings.extend(per_100g_result.warnings)
            result.errors.extend(per_100g_result.errors)
            result.is_valid = result.is_valid and per_100g_result.is_valid
        
        return result
    
    def validate_recipe_nutrients(
        self,
        total_nutrients: Dict[str, float],
        ingredient_details: List[Any],
        total_edible_weight_g: float
    ) -> ValidationResult:
        """Validate aggregated recipe nutrient values."""
        result = ValidationResult(is_valid=True)
        
        if total_edible_weight_g <= 0:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                field='total_edible_weight_g',
                message=f"Total edible weight is zero or negative: {total_edible_weight_g}",
                actual_value=total_edible_weight_g
            ))
            return result
        
        # Check per-100g equivalents
        per_100g = {k: v * 100 / total_edible_weight_g for k, v in total_nutrients.items()}
        per_100g_result = self.validate_per_100g_nutrients(per_100g)
        result.issues.extend(per_100g_result.issues)
        result.warnings.extend(per_100g_result.warnings)
        result.errors.extend(per_100g_result.errors)
        result.is_valid = result.is_valid and per_100g_result.is_valid
        
        # Cross-check with ingredient details
        if ingredient_details:
            summed_nutrients = {}
            for detail in ingredient_details:
                if hasattr(detail, 'calculated_nutrients'):
                    for n, v in detail.calculated_nutrients.items():
                        summed_nutrients[n] = summed_nutrients.get(n, 0) + v
            
            for nutrient, total in total_nutrients.items():
                if nutrient in summed_nutrients:
                    diff = abs(total - summed_nutrients[nutrient])
                    if diff > 0.01:  # Allow tiny rounding differences
                        result.add_issue(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            field=nutrient,
                            message=f"Recipe total {total} differs from ingredient sum {summed_nutrients[nutrient]}",
                            actual_value=total,
                            suggestion="Check aggregation logic"
                        ))
        
        return result
    
    def _calculate_atwater_energy(self, nutrients: Dict[str, float]) -> float:
        """Calculate energy using Atwater factors."""
        energy = 0.0
        for nutrient, factor in self.atwater_factors.items():
            val = nutrients.get(nutrient)
            if val is not None and not np.isnan(val):
                energy += val * factor
        return energy
    
    def validate_completeness(
        self,
        nutrient_completeness: Dict[str, float],
        threshold: float = 0.5
    ) -> ValidationResult:
        """Validate nutrient completeness meets threshold."""
        result = ValidationResult(is_valid=True)
        
        for nutrient, completeness in nutrient_completeness.items():
            if completeness < threshold:
                result.add_issue(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    field=nutrient,
                    message=f"Nutrient completeness {completeness:.1%} below threshold {threshold:.1%}",
                    actual_value=completeness,
                    suggestion=f"Consider reporting as PARTIAL for {nutrient}"
                ))
        
        return result


def validate_nutrient_dict(
    nutrients: Dict[str, float],
    ranges: Optional[Dict[str, Tuple[float, float]]] = None
) -> ValidationResult:
    """Convenience function to validate a nutrient dictionary."""
    validator = NutrientValidator(ranges=ranges)
    return validator.validate_per_100g_nutrients(nutrients)