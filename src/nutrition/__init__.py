"""Nutrition Calculation Package - Ingredient-level nutrition calculation engine."""

from .nutrition_models import (
    MappingStatus,
    CalculationStatus,
    RecipeCalculationStatus,
    IFCTNutrientRecord,
    ApprovedMapping,
    IngredientWeightInfo,
    IngredientNutritionInput,
    IngredientNutritionOutput,
    RecipeNutritionOutput,
    NutrientCalculationResult,
    NutrientValue,
    IngredientNutrition,
    NUTRIENT_NAMES,
    NUTRIENT_UNITS,
)

from .ingredient_mapping import (
    MappingDecision,
    MappingReviewRecord,
    ApprovedMappingStore,
    StrictMappingInterface,
    load_approved_mappings_from_jsonl,
    save_approved_mappings_to_jsonl,
)

from .edible_portion import (
    EdiblePortionStatus,
    EdiblePortionInfo,
    EdiblePortionCalculator,
    edible_portion_calculator,
)

from .nutrient_calculator import (
    NutrientCalculator,
    calculate_nutrient_contribution,
    KJ_TO_KCAL,
)

from .nutrient_validation import (
    ValidationSeverity,
    ValidationIssue,
    ValidationResult,
    NutrientValidator,
    validate_nutrient_dict,
    NUTRIENT_RANGES_PER_100G,
    ATWATER_FACTORS,
)

from .recipe_aggregator import (
    AggregationConfig,
    RecipeAggregator,
    create_weight_infos_from_parsed,
    create_weight_infos_from_all_parsed,
)

from .coverage_report import (
    CoverageReport,
    CoverageAnalyzer,
    generate_coverage_report,
)

__version__ = "1.0.0"

__all__ = [
    # Models
    "MappingStatus",
    "CalculationStatus", 
    "RecipeCalculationStatus",
    "IFCTNutrientRecord",
    "ApprovedMapping",
    "IngredientWeightInfo",
    "IngredientNutritionInput",
    "IngredientNutritionOutput",
    "RecipeNutritionOutput",
    "NutrientCalculationResult",
    "NUTRIENT_NAMES",
    "NUTRIENT_UNITS",
    
    # Mapping
    "MappingDecision",
    "MappingReviewRecord",
    "ApprovedMappingStore",
    "StrictMappingInterface",
    "load_approved_mappings_from_jsonl",
    "save_approved_mappings_to_jsonl",
    
    # Edible portion
    "EdiblePortionStatus",
    "EdiblePortionInfo",
    "EdiblePortionCalculator",
    "edible_portion_calculator",
    
    # Calculator
    "NutrientCalculator",
    "calculate_nutrient_contribution",
    "KJ_TO_KCAL",
    
    # Validation
    "ValidationSeverity",
    "ValidationIssue",
    "ValidationResult",
    "NutrientValidator",
    "validate_nutrient_dict",
    "NUTRIENT_RANGES_PER_100G",
    "ATWATER_FACTORS",
    
    # Aggregation
    "AggregationConfig",
    "RecipeAggregator",
    "create_weight_infos_from_parsed",
    "create_weight_infos_from_all_parsed",
    
    # Coverage
    "CoverageReport",
    "CoverageAnalyzer",
    "generate_coverage_report",
]