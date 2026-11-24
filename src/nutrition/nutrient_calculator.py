"""Nutrient Calculator - Calculate ingredient nutrient contributions from IFCT data."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import pandas as pd
import numpy as np

from .nutrition_models import (
    IngredientNutritionInput,
    IngredientNutritionOutput, CalculationStatus, MappingStatus,
    NUTRIENT_NAMES, NUTRIENT_UNITS, IFCTNutrientRecord
)
from .edible_portion import EdiblePortionCalculator, edible_portion_calculator
from .nutrient_validation import NutrientValidator, ValidationSeverity


KJ_TO_KCAL = 4.184


class NutrientCalculator:
    """Calculate nutrient contributions from verified ingredient mappings and weights."""
    
    def __init__(
        self,
        ifct_data: pd.DataFrame,
        edible_portion_calc: Optional[EdiblePortionCalculator] = None,
        validator: Optional[NutrientValidator] = None
    ):
        self.ifct_data = ifct_data
        self.edible_portion_calc = edible_portion_calc or edible_portion_calculator
        self.validator = validator or NutrientValidator()
        self._ifct_index = self._build_ifct_index()
    
    def _build_ifct_index(self) -> Dict[str, IFCTNutrientRecord]:
        """Build lookup index for IFCT records."""
        index = {}
        for _, row in self.ifct_data.iterrows():
            record = IFCTNutrientRecord(
                food_code=row['food_code'],
                food_name=row['food_name'],
                food_group=row['food_group'],
                moisture_g=self._parse_nutrient(row.get('moisture_g')),
                protein_g=self._parse_nutrient(row.get('protein_g')),
                ash_g=self._parse_nutrient(row.get('ash_g')),
                fat_g=self._parse_nutrient(row.get('fat_g')),
                fibre_total_g=self._parse_nutrient(row.get('fibre_total_g')),
                fibre_insoluble_g=self._parse_nutrient(row.get('fibre_insoluble_g')),
                fibre_soluble_g=self._parse_nutrient(row.get('fibre_soluble_g')),
                carb_available_g=self._parse_nutrient(row.get('carb_available_g')),
                energy_kj=self._parse_nutrient(row.get('energy_kj')),
                source_page=row.get('source_page'),
                source_table=row.get('source_table'),
                verification_status=row.get('verification_status', ''),
            )
            index[row['food_code']] = record
        return index
    
    def _parse_nutrient(self, value: Any) -> Optional[float]:
        """Parse nutrient value from string (may contain ± notation)."""
        if value is None or pd.isna(value):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Handle "61.46±0.60" format - take the mean value
            if '±' in value:
                try:
                    return float(value.split('±')[0].strip())
                except ValueError:
                    return None
            try:
                return float(value)
            except ValueError:
                return None
        return None
    
    def get_ifct_record(self, food_code: str) -> Optional[IFCTNutrientRecord]:
        """Get IFCT nutrient record by food code."""
        return self._ifct_index.get(food_code)
    
    def calculate_ingredient_nutrition(
        self,
        input_data: IngredientNutritionInput
    ) -> IngredientNutritionOutput:
        """
        Calculate nutrient contributions for a single ingredient.
        
        Formula: nutrient_contribution = nutrient_per_100g_edible × edible_weight_g / 100
        """
        # Initialize output
        output = IngredientNutritionOutput(
            recipe_id=input_data.recipe_id,
            ingredient_record_id=input_data.ingredient_record_id,
            ifct_food_code=input_data.ifct_food_code,
            ifct_food_name=input_data.ifct_food_name,
            ifct_food_group=input_data.ifct_food_group,
            edible_weight_g=input_data.edible_weight_g,
            mapping_status=input_data.mapping_status,
            calculation_status=CalculationStatus.INVALID_INPUT,
            provenance={'source': input_data.source_provenance}
        )
        
        # Validate mapping status
        if input_data.mapping_status != MappingStatus.APPROVED:
            output.calculation_status = CalculationStatus.MISSING_MAPPING
            output.provenance['error'] = f"Mapping not approved: {input_data.mapping_status.value}"
            return output
        
        # Validate edible weight
        if input_data.edible_weight_g is None or pd.isna(input_data.edible_weight_g):
            output.calculation_status = CalculationStatus.MISSING_WEIGHT
            output.provenance['error'] = "No edible weight available"
            return output
        
        if input_data.edible_weight_g <= 0:
            output.calculation_status = CalculationStatus.INVALID_INPUT
            output.provenance['error'] = f"Invalid edible weight: {input_data.edible_weight_g}"
            return output
        
        # Get IFCT record
        ifct_record = self.get_ifct_record(input_data.ifct_food_code)
        if ifct_record is None:
            output.calculation_status = CalculationStatus.INVALID_INPUT
            output.provenance['error'] = f"IFCT record not found: {input_data.ifct_food_code}"
            return output
        
        # Calculate nutrients
        calculated = {}
        missing = []
        
        weight_factor = input_data.edible_weight_g / 100.0
        
        # Determine which nutrients to calculate
        if input_data.nutrient_values is not None and len(input_data.nutrient_values) > 0:
            # Use only explicitly provided nutrient values
            expected_nutrients = set(input_data.nutrient_values.keys())
            for nutrient in expected_nutrients:
                per_100g = input_data.nutrient_values[nutrient]
                if per_100g is not None and not pd.isna(per_100g):
                    contribution = per_100g * weight_factor
                    calculated[nutrient] = round(contribution, 4)
                else:
                    missing.append(nutrient)
        elif input_data.nutrient_values is not None and len(input_data.nutrient_values) == 0:
            # Explicitly provided empty dict - no nutrients to calculate
            expected_nutrients = set()
            # No calculation performed
        else:
            # No nutrient_values provided (None) - fall back to IFCT record, expect all standard nutrients
            expected_nutrients = set(NUTRIENT_NAMES)
            for nutrient in expected_nutrients:
                per_100g = ifct_record.get_nutrient(nutrient)
                if per_100g is not None and not pd.isna(per_100g):
                    contribution = per_100g * weight_factor
                    calculated[nutrient] = round(contribution, 4)
                else:
                    missing.append(nutrient)
        
        # Validate calculated nutrients
        validation_result = self.validator.validate_ingredient_nutrients(
            calculated, input_data.edible_weight_g, input_data.ifct_food_code
        )
        
        if not validation_result.is_valid:
            output.provenance['validation_errors'] = [str(e) for e in validation_result.errors]
        
        output.calculated_nutrients = calculated
        output.missing_nutrients = missing
        output.provenance['ifct_verification'] = ifct_record.verification_status
        output.provenance['weight_factor'] = weight_factor
        output.provenance['validation'] = {
            'is_valid': validation_result.is_valid,
            'warnings': [str(w) for w in validation_result.warnings],
        }
        
        # Determine calculation status
        if len(calculated) == 0:
            output.calculation_status = CalculationStatus.MISSING_NUTRIENTS
        elif len(missing) > 0:
            output.calculation_status = CalculationStatus.PARTIAL
        else:
            output.calculation_status = CalculationStatus.COMPLETE
        
        return output
    
    def calculate_recipe_nutrition(
        self,
        ingredient_inputs: List[IngredientNutritionInput]
    ) -> 'RecipeNutritionOutput':
        """
        Aggregate ingredient nutrition into recipe-level nutrition.
        
        Only aggregates valid ingredient contributions.
        Preserves missingness and tracks coverage.
        """
        from .nutrition_models import RecipeNutritionOutput, RecipeCalculationStatus
        
        if not ingredient_inputs:
            return RecipeNutritionOutput(
                recipe_id=ingredient_inputs[0].recipe_id if ingredient_inputs else 0,
                calculation_status=RecipeCalculationStatus.NO_MAPPED_INGREDIENTS
            )
        
        recipe_id = ingredient_inputs[0].recipe_id
        ingredient_outputs = []
        total_nutrients: Dict[str, float] = {}
        nutrient_ingredient_counts: Dict[str, int] = {n: 0 for n in NUTRIENT_NAMES}
        
        mapped_count = 0
        total_count = len(ingredient_inputs)
        unresolved_count = 0
        
        for input_data in ingredient_inputs:
            output = self.calculate_ingredient_nutrition(input_data)
            ingredient_outputs.append(output)
            
            if output.calculation_status in (CalculationStatus.COMPLETE, CalculationStatus.PARTIAL):
                mapped_count += 1
                for nutrient, value in output.calculated_nutrients.items():
                    total_nutrients[nutrient] = total_nutrients.get(nutrient, 0) + value
                    nutrient_ingredient_counts[nutrient] += 1
            else:
                unresolved_count += 1
        
        # Calculate completeness per nutrient
        nutrient_completeness = {}
        for nutrient in NUTRIENT_NAMES:
            if nutrient_ingredient_counts[nutrient] > 0:
                # Completeness = ingredients with this nutrient / mapped ingredients
                # This represents the proportion of mapped ingredients contributing to this nutrient
                nutrient_completeness[nutrient] = nutrient_ingredient_counts[nutrient] / max(mapped_count, 1)
            else:
                nutrient_completeness[nutrient] = 0.0
        
        # Determine overall recipe calculation status
        if mapped_count == 0:
            calc_status = RecipeCalculationStatus.NO_MAPPED_INGREDIENTS
        elif mapped_count == total_count and all(
            out.calculation_status == CalculationStatus.COMPLETE for out in ingredient_outputs
        ):
            calc_status = RecipeCalculationStatus.COMPLETE
        elif mapped_count > 0:
            calc_status = RecipeCalculationStatus.PARTIAL
        else:
            calc_status = RecipeCalculationStatus.INSUFFICIENT_DATA
        
        # Calculate ingredient mapping coverage and gram weight coverage
        # These would ideally come from the full ingredient list
        mapping_coverage = mapped_count / max(total_count, 1)
        
        # For gram weight coverage, we'd need the full ingredient list with weight info
        # Here we use a proxy: ingredients with complete/partial calculation
        gram_weight_coverage = mapped_count / max(total_count, 1)
        
        return RecipeNutritionOutput(
            recipe_id=recipe_id,
            total_nutrients=total_nutrients,
            nutrient_completeness=nutrient_completeness,
            ingredient_mapping_coverage=mapping_coverage,
            gram_weight_coverage=gram_weight_coverage,
            mapped_ingredient_count=mapped_count,
            total_ingredient_count=total_count,
            unresolved_ingredient_count=unresolved_count,
            calculation_status=calc_status,
            ingredient_details=ingredient_outputs,
            provenance={
                'calculator_version': '1.0',
                'kj_to_kcal_factor': KJ_TO_KCAL,
            }
        )
    
    def convert_energy_kj_to_kcal(self, energy_kj: float) -> float:
        """Convert energy from kJ to kcal."""
        return round(energy_kj / KJ_TO_KCAL, 2)
    
    def add_kcal_to_output(self, output: IngredientNutritionOutput) -> IngredientNutritionOutput:
        """Add energy_kcal to calculated nutrients if energy_kj present."""
        if 'energy_kj' in output.calculated_nutrients:
            output.calculated_nutrients['energy_kcal'] = self.convert_energy_kj_to_kcal(
                output.calculated_nutrients['energy_kj']
            )
        return output
    
    def add_kcal_to_recipe(self, output: 'RecipeNutritionOutput') -> 'RecipeNutritionOutput':
        """Add energy_kcal to recipe total nutrients if energy_kj present."""
        if 'energy_kj' in output.total_nutrients:
            output.total_nutrients['energy_kcal'] = self.convert_energy_kj_to_kcal(
                output.total_nutrients['energy_kj']
            )
        return output


# Convenience function for direct calculation
def calculate_nutrient_contribution(
    nutrient_per_100g: float,
    edible_weight_g: float
) -> float:
    """
    Calculate nutrient contribution.
    
    Formula: nutrient = nutrient_per_100g_edible × edible_weight_g / 100
    """
    if nutrient_per_100g is None or edible_weight_g is None:
        return np.nan
    if edible_weight_g <= 0:
        raise ValueError("Edible weight must be positive")
    return nutrient_per_100g * edible_weight_g / 100.0