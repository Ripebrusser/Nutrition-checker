"""Recipe Aggregator - Aggregate ingredient nutrition into recipe-level nutrition."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

from .nutrition_models import (
    RecipeNutritionOutput, IngredientNutritionOutput,
    RecipeCalculationStatus, NUTRIENT_NAMES, IngredientWeightInfo,
    CalculationStatus
)
from .nutrient_calculator import NutrientCalculator, KJ_TO_KCAL
from .ingredient_mapping import StrictMappingInterface, ApprovedMappingStore
from .edible_portion import EdiblePortionCalculator


@dataclass
class AggregationConfig:
    """Configuration for recipe aggregation."""
    min_mapped_ingredients: int = 1
    min_gram_weight_coverage: float = 0.0
    require_all_nutrients: bool = False
    completeness_threshold: float = 0.5


class RecipeAggregator:
    """Aggregate ingredient-level nutrition into recipe-level nutrition."""
    
    def __init__(
        self,
        calculator: NutrientCalculator,
        mapping_interface: StrictMappingInterface,
        edible_portion_calc: EdiblePortionCalculator,
        config: Optional[AggregationConfig] = None
    ):
        self.calculator = calculator
        self.mapping_interface = mapping_interface
        self.edible_portion_calc = edible_portion_calc
        self.config = config or AggregationConfig()
    
    def aggregate_recipe(
        self,
        recipe_id: int,
        weight_infos: List[IngredientWeightInfo]
    ) -> RecipeNutritionOutput:
        """
        Aggregate nutrition for a single recipe.
        
        Args:
            recipe_id: Recipe identifier
            weight_infos: List of ingredient weight information
            
        Returns:
            RecipeNutritionOutput with aggregated nutrition
        """
        # Create nutrition inputs from approved mappings and weights
        ingredient_inputs = []
        
        for weight_info in weight_infos:
            if weight_info.recipe_id != recipe_id:
                continue
            
            nutrition_input = self.mapping_interface.create_nutrition_input(
                recipe_id, weight_info.ingredient_record_id, weight_info
            )
            
            if nutrition_input:
                ingredient_inputs.append(nutrition_input)
        
        total_ingredients = len(weight_infos)
        
        if not ingredient_inputs:
            return RecipeNutritionOutput(
                recipe_id=recipe_id,
                calculation_status=RecipeCalculationStatus.NO_MAPPED_INGREDIENTS,
                total_ingredient_count=total_ingredients,
                unresolved_ingredient_count=total_ingredients,
                provenance={'reason': 'No approved mappings found for any ingredient'}
            )
        
        # Calculate recipe nutrition
        recipe_output = self.calculator.calculate_recipe_nutrition(ingredient_inputs)
        
        # Override total_ingredient_count and unresolved_ingredient_count with actual totals
        recipe_output.total_ingredient_count = total_ingredients
        recipe_output.unresolved_ingredient_count = total_ingredients - recipe_output.mapped_ingredient_count
        recipe_output.ingredient_mapping_coverage = recipe_output.mapped_ingredient_count / max(total_ingredients, 1)
        recipe_output.gram_weight_coverage = recipe_output.mapped_ingredient_count / max(total_ingredients, 1)
        
        # Recalculate status based on actual totals
        if recipe_output.mapped_ingredient_count == 0:
            recipe_output.calculation_status = RecipeCalculationStatus.NO_MAPPED_INGREDIENTS
        elif recipe_output.mapped_ingredient_count == total_ingredients and all(
            out.calculation_status == CalculationStatus.COMPLETE for out in recipe_output.ingredient_details
        ):
            recipe_output.calculation_status = RecipeCalculationStatus.COMPLETE
        elif recipe_output.mapped_ingredient_count > 0:
            recipe_output.calculation_status = RecipeCalculationStatus.PARTIAL
        else:
            recipe_output.calculation_status = RecipeCalculationStatus.INSUFFICIENT_DATA
        
        # Add kcal conversion
        recipe_output = self.calculator.add_kcal_to_recipe(recipe_output)
        
        # Update provenance
        recipe_output.provenance.update({
            'aggregator_config': self.config.__dict__,
            'total_ingredients_processed': total_ingredients,
            'ingredients_with_approved_mapping': len(ingredient_inputs),
        })
        
        return recipe_output
    
    def aggregate_recipes(
        self,
        recipe_ids: List[int],
        all_weight_infos: List[IngredientWeightInfo]
    ) -> List[RecipeNutritionOutput]:
        """
        Aggregate nutrition for multiple recipes.
        
        Args:
            recipe_ids: List of recipe IDs to process
            all_weight_infos: All ingredient weight infos (will be filtered by recipe_id)
            
        Returns:
            List of RecipeNutritionOutput
        """
        # Group weight infos by recipe
        by_recipe: Dict[int, List[IngredientWeightInfo]] = {}
        for wi in all_weight_infos:
            by_recipe.setdefault(wi.recipe_id, []).append(wi)
        
        results = []
        for recipe_id in recipe_ids:
            weight_infos = by_recipe.get(recipe_id, [])
            result = self.aggregate_recipe(recipe_id, weight_infos)
            results.append(result)
        
        return results
    
    def get_aggregation_summary(
        self,
        results: List[RecipeNutritionOutput]
    ) -> Dict[str, Any]:
        """Generate summary statistics for a batch of recipe aggregations."""
        if not results:
            return {'total_recipes': 0}
        
        status_counts = {}
        for status in RecipeCalculationStatus:
            status_counts[status.value] = sum(1 for r in results if r.calculation_status == status)
        
        total_recipes = len(results)
        recipes_with_nutrition = sum(1 for r in results if r.has_any_nutrition)
        
        avg_mapping_coverage = np.mean([r.ingredient_mapping_coverage for r in results])
        avg_gram_weight_coverage = np.mean([r.gram_weight_coverage for r in results])
        
        # Nutrient-specific coverage
        nutrient_coverage = {}
        for nutrient in NUTRIENT_NAMES:
            present = sum(1 for r in results if nutrient in r.total_nutrients)
            nutrient_coverage[nutrient] = present / total_recipes
        
        total_mapped_ingredients = sum(r.mapped_ingredient_count for r in results)
        total_ingredients = sum(r.total_ingredient_count for r in results)
        total_unresolved = sum(r.unresolved_ingredient_count for r in results)
        
        return {
            'total_recipes': total_recipes,
            'recipes_with_nutrition': recipes_with_nutrition,
            'recipes_without_nutrition': total_recipes - recipes_with_nutrition,
            'status_distribution': status_counts,
            'avg_mapping_coverage': avg_mapping_coverage,
            'avg_gram_weight_coverage': avg_gram_weight_coverage,
            'nutrient_coverage': nutrient_coverage,
            'total_mapped_ingredients': total_mapped_ingredients,
            'total_ingredients': total_ingredients,
            'total_unresolved_ingredients': total_unresolved,
            'overall_mapping_rate': total_mapped_ingredients / max(total_ingredients, 1),
        }


def create_weight_infos_from_parsed(
    parsed_df: pd.DataFrame,
    recipe_id: int
) -> List[IngredientWeightInfo]:
    """
    Create IngredientWeightInfo objects from parsed ingredient DataFrame.
    
    This is a helper to convert Phase 2 parsed data into the format
    needed by the nutrition engine.
    """
    weight_infos = []
    
    for idx, row in parsed_df.iterrows():
        if row['recipe_id'] != recipe_id:
            continue
        
        gram_weight = row.get('gram_weight')
        if pd.isna(gram_weight):
            gram_weight = None
        
        gram_weight_min = row.get('gram_weight_min')
        if pd.isna(gram_weight_min):
            gram_weight_min = None
            
        gram_weight_max = row.get('gram_weight_max')
        if pd.isna(gram_weight_max):
            gram_weight_max = None
        
        info = IngredientWeightInfo(
            recipe_id=int(row['recipe_id']),
            ingredient_record_id=str(idx),
            original_ingredient=row['original_ingredient'],
            normalized_ingredient=row['normalized_ingredient'],
            quantity=row.get('quantity'),
            unit=row.get('unit'),
            gram_weight=gram_weight,
            gram_weight_min=gram_weight_min,
            gram_weight_max=gram_weight_max,
            conversion_status=row.get('conversion_status', 'UNRESOLVED'),
            preparation_state=row.get('preparation', 'NOT_SPECIFIED'),
        )
        weight_infos.append(info)
    
    return weight_infos


def create_weight_infos_from_all_parsed(
    parsed_df: pd.DataFrame
) -> List[IngredientWeightInfo]:
    """Create IngredientWeightInfo objects for all parsed ingredients."""
    weight_infos = []
    
    for idx, row in parsed_df.iterrows():
        gram_weight = row.get('gram_weight')
        if pd.isna(gram_weight):
            gram_weight = None
        
        gram_weight_min = row.get('gram_weight_min')
        if pd.isna(gram_weight_min):
            gram_weight_min = None
            
        gram_weight_max = row.get('gram_weight_max')
        if pd.isna(gram_weight_max):
            gram_weight_max = None
        
        info = IngredientWeightInfo(
            recipe_id=int(row['recipe_id']),
            ingredient_record_id=str(idx),
            original_ingredient=row['original_ingredient'],
            normalized_ingredient=row['normalized_ingredient'],
            quantity=row.get('quantity'),
            unit=row.get('unit'),
            gram_weight=gram_weight,
            gram_weight_min=gram_weight_min,
            gram_weight_max=gram_weight_max,
            conversion_status=row.get('conversion_status', 'UNRESOLVED'),
            preparation_state=row.get('preparation', 'NOT_SPECIFIED'),
        )
        weight_infos.append(info)
    
    return weight_infos