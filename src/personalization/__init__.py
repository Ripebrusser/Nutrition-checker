"""Personalization Package - User profiling, nutrition targets, dietary constraints, and meal planning."""

from .profile_models import (
    UserProfile, Anthropometrics, DietaryProfile, NutritionalGoals, LifestyleProfile,
    Sex, ActivityLevel, DietaryPreference, WeightGoal, MealFrequency, MealSlot,
    DEFAULT_MEAL_SLOTS, DEFAULT_MEAL_ENERGY_DISTRIBUTION,
    THREE_MEAL_DISTRIBUTION, FOUR_MEAL_DISTRIBUTION,
    get_meal_distribution
)

from .profile_validation import (
    ProfileValidator, ValidationResult, ValidationSeverity, ValidationIssue, validate_profile
)

from .profile_repository import (
    ProfileRepository, get_default_repository, set_default_repository
)

from .user_profile import (
    UserProfileManager, create_profile_manager, create_sample_profile, create_weight_loss_profile
)

from .reference_values import (
    ReferenceSource, NutrientReference, ICMR_2020_RDA, WHO_FAO_2004, USDA_DRI_2019,
    ACTIVITY_PAL_FACTORS, MIFFLIN_ST_JEOR, HARRIS_BENEDICT,
    get_icmr_rda, get_icmr_energy_target, get_icmr_protein_target,
    get_icmr_fat_range, get_icmr_carb_range, get_icmr_fibre_target,
    get_meal_distribution, MEAL_ENERGY_DISTRIBUTION, INDIAN_FOOD_GROUP_SERVINGS,
    MACRO_DISTRIBUTION_RANGES, NUTRIENT_DENSITY_THRESHOLDS,
    REFERENCE_DOCUMENTATION, print_reference_documentation
)

from .energy_requirements import (
    EquationMethod, EnergyCalculationResult, EnergyCalculator, calculate_energy_requirements,
    calculate_energy_only
)

from .macro_targets import (
    MacroDistributionMethod, MacroTargets, MicronutrientTargets, CompleteNutritionTargets,
    MacroCalculator, MicronutrientCalculator, calculate_nutrition_targets
)

from .nutrition_targets import (
    NutritionTargetCalculator, calculate_user_nutrition_targets,
    calculate_weight_loss_targets, calculate_muscle_gain_targets,
    calculate_maintenance_targets, calculate_diabetes_targets, calculate_heart_health_targets
)

from .dietary_constraints import (
    ConstraintResult, ConstraintEvaluation, RecipeDietaryEvaluation,
    DietClassifier, AllergenFilter, IngredientExclusionFilter,
    DietaryPreferenceFilter, JainComplianceFilter, DietaryConstraintEngine,
    evaluate_recipe_dietary, filter_recipes_by_diet
)

from .recipe_profile import (
    NutritionCompleteness, RecipeNutritionProfile, RecipeProfileCollection,
    RecipeProfileBuilder, build_recipe_profiles, get_recipe_nutrition_summary
)

from .personalized_recommender import (
    RecommendationFilter, PersonalizedRecommendationResult, PersonalizedRecommenderConfig,
    PersonalizedRecommender, create_personalized_recommender
)

from .meal_planner import (
    MealPlanStatus, MealSlotPlan, DailyMealPlan, WeeklyMealPlan, MealPlanConfig,
    MealPlanner, create_meal_planner
)

from .meal_plan_optimizer import (
    OptimizationObjective, OptimizationConfig, OptimizationResult, MealPlanOptimizer,
    optimize_meal_plan
)

from .meal_plan_validation import (
    ValidationSeverity, ValidationIssue, ValidationResult, MealPlanValidator,
    validate_meal_plan, validate_daily_plan
)

from .meal_plan_models import (
    MealPlanStatus, MealSlotPlan, DailyMealPlan, WeeklyMealPlan, MealPlanConfig,
    ValidationSeverity, ValidationIssue, ValidationResult
)

from .explanation_engine import (
    ExplanationType, ExplanationSegment, RecommendationExplanation,
    MealPlanExplanation, ExplanationEngine,
    generate_recommendation_explanation, generate_meal_plan_explanation
)

from .personalization_evaluation import (
    EvaluationMetric, EvaluationResult, EvaluationSuite, PersonalizationEvaluator,
    evaluate_personalization_system, generate_evaluation_report
)

__version__ = "1.0.0"

__all__ = [
    # Profile models
    "UserProfile", "Anthropometrics", "DietaryProfile", "NutritionalGoals", "LifestyleProfile",
    "Sex", "ActivityLevel", "DietaryPreference", "WeightGoal", "MealFrequency", "MealSlot",
    "DEFAULT_MEAL_SLOTS", "DEFAULT_MEAL_ENERGY_DISTRIBUTION",
    "THREE_MEAL_DISTRIBUTION", "FOUR_MEAL_DISTRIBUTION", "get_meal_distribution",
    
    # Validation
    "ProfileValidator", "ValidationResult", "ValidationSeverity", "ValidationIssue", "validate_profile",
    
    # Repository
    "ProfileRepository", "get_default_repository", "set_default_repository",
    
    # Manager
    "UserProfileManager", "create_profile_manager", "create_sample_profile", "create_weight_loss_profile",
    
    # Reference values
    "ReferenceSource", "NutrientReference", "ICMR_2020_RDA", "WHO_FAO_2004", "USDA_DRI_2019",
    "ACTIVITY_PAL_FACTORS", "MIFFLIN_ST_JEOR", "HARRIS_BENEDICT",
    "get_icmr_rda", "get_icmr_energy_target", "get_icmr_protein_target",
    "get_icmr_fat_range", "get_icmr_carb_range", "get_icmr_fibre_target",
    "get_meal_distribution", "MEAL_ENERGY_DISTRIBUTION", "INDIAN_FOOD_GROUP_SERVINGS",
    "MACRO_DISTRIBUTION_RANGES", "NUTRIENT_DENSITY_THRESHOLDS",
    "REFERENCE_DOCUMENTATION", "print_reference_documentation",
    
    # Energy requirements
    "EquationMethod", "EnergyCalculationResult", "EnergyCalculator", "calculate_energy_requirements",
    
    # Macro targets
    "MacroDistributionMethod", "MacroTargets", "MicronutrientTargets", "CompleteNutritionTargets",
    "MacroCalculator", "MicronutrientCalculator", "calculate_nutrition_targets",
    "calculate_weight_loss_targets", "calculate_muscle_gain_targets",
    "calculate_maintenance_targets", "calculate_diabetes_targets", "calculate_heart_health_targets",
    
    # Nutrition targets
    "NutritionTargetCalculator", "calculate_user_nutrition_targets",
    
    # Dietary constraints
    "ConstraintResult", "ConstraintEvaluation", "RecipeDietaryEvaluation",
    "DietClassifier", "AllergenFilter", "IngredientExclusionFilter",
    "DietaryPreferenceFilter", "JainComplianceFilter", "DietaryConstraintEngine",
    "evaluate_recipe_dietary", "filter_recipes_by_diet",
    
    # Recipe profile
    "NutritionCompleteness", "RecipeNutritionProfile", "RecipeProfileCollection",
    "RecipeProfileBuilder", "build_recipe_profiles", "get_recipe_nutrition_summary",
    
    # Personalized recommender
    "RecommendationFilter", "PersonalizedRecommendationResult", "PersonalizedRecommenderConfig",
    "PersonalizedRecommender", "create_personalized_recommender",
    
    # Meal planner
    "MealPlanStatus", "MealSlotPlan", "DailyMealPlan", "WeeklyMealPlan", "MealPlanConfig",
    "MealPlanner", "create_meal_planner",
    
    # Meal plan optimizer
    "OptimizationObjective", "OptimizationConfig", "OptimizationResult", "MealPlanOptimizer",
    "optimize_meal_plan",
    
    # Meal plan validation
    "ValidationSeverity", "ValidationIssue", "ValidationResult", "MealPlanValidator",
    "validate_meal_plan", "validate_daily_plan",
    
    # Meal plan models
    "MealPlanStatus", "MealSlotPlan", "DailyMealPlan", "WeeklyMealPlan", "MealPlanConfig",
    "ValidationSeverity", "ValidationIssue", "ValidationResult",
    
    # Explanation engine
    "ExplanationType", "ExplanationSegment", "RecommendationExplanation",
    "MealPlanExplanation", "ExplanationEngine",
    "generate_recommendation_explanation", "generate_meal_plan_explanation",
    
    # Evaluation
    "EvaluationMetric", "EvaluationResult", "EvaluationSuite", "PersonalizationEvaluator",
    "evaluate_personalization_system", "generate_evaluation_report",
]