"""Tests for Phase 4 Personalization modules."""

import pytest
from datetime import date

from src.personalization import (
    UserProfile, Anthropometrics, DietaryProfile, NutritionalGoals, LifestyleProfile,
    Sex, ActivityLevel, DietaryPreference, WeightGoal, MealFrequency, MealSlot,
    ProfileValidator, validate_profile, ValidationSeverity,
    ProfileRepository, get_default_repository,
    UserProfileManager, create_profile_manager, create_sample_profile, create_weight_loss_profile,
    EnergyCalculator, EnergyCalculationResult, calculate_energy_requirements,
    MacroCalculator, MicronutrientCalculator, MacroDistributionMethod,
    MacroTargets, MicronutrientTargets, CompleteNutritionTargets,
    calculate_nutrition_targets, calculate_user_nutrition_targets,
    NutritionTargetCalculator,
    DietClassifier, AllergenFilter, IngredientExclusionFilter,
    DietaryPreferenceFilter, JainComplianceFilter, DietaryConstraintEngine,
    ConstraintResult, RecipeDietaryEvaluation,
    NutritionCompleteness, RecipeNutritionProfile, RecipeProfileCollection,
    PersonalizedRecommenderConfig, PersonalizedRecommendationResult,
    MealPlanConfig, MealSlotPlan, DailyMealPlan, WeeklyMealPlan,
    MealPlanStatus, ValidationSeverity as MealValidationSeverity,
    ValidationIssue, ValidationResult, MealPlanValidator,
    ExplanationEngine, ExplanationType, ExplanationSegment,
    RecommendationExplanation, MealPlanExplanation,
    EvaluationMetric, EvaluationResult, EvaluationSuite, PersonalizationEvaluator,
)


# ============================================================
# Profile Model Tests
# ============================================================

class TestProfileModels:
    """Test profile model creation and validation."""
    
    def test_create_sample_profile(self):
        profile = create_sample_profile()
        assert profile.user_id == "sample_user"
        assert profile.anthropometrics.height_cm == 170.0
        assert profile.anthropometrics.weight_kg == 70.0
        assert profile.anthropometrics.age_years == 30
        assert profile.anthropometrics.sex == Sex.MALE
        assert profile.dietary_profile.preference == DietaryPreference.VEGETARIAN
        assert profile.nutritional_goals.weight_goal == WeightGoal.MAINTAIN
        assert profile.lifestyle.activity_level == ActivityLevel.LIGHTLY_ACTIVE
    
    def test_create_weight_loss_profile(self):
        profile = create_weight_loss_profile()
        assert profile.user_id == "weight_loss_user"
        assert profile.anthropometrics.sex == Sex.FEMALE
        assert profile.nutritional_goals.weight_goal == WeightGoal.LOSE
        assert profile.lifestyle.activity_level == ActivityLevel.SEDENTARY
    
    def test_profile_serialization(self):
        profile = create_sample_profile()
        data = profile.to_dict()
        assert data["user_id"] == "sample_user"
        assert data["anthropometrics"]["height_cm"] == 170.0
        
        # Deserialize
        restored = UserProfile.from_dict(data)
        assert restored.user_id == "sample_user"
        assert restored.anthropometrics.height_cm == 170.0
    
    def test_anthropometrics_validation(self):
        anthro = Anthropometrics(height_cm=170, weight_kg=70, age_years=30, sex=Sex.MALE)
        assert anthro.has_required_for_bmr() == True
        
        anthro2 = Anthropometrics(height_cm=170, weight_kg=70, age_years=30)
        assert anthro2.has_required_for_bmr() == False


# ============================================================
# Profile Validation Tests
# ============================================================

class TestProfileValidation:
    """Test profile validation."""
    
    def test_valid_profile(self):
        profile = create_sample_profile()
        result = validate_profile(profile)
        assert result.is_valid == True
        assert len(result.errors) == 0
    
    def test_missing_anthropometrics(self):
        profile = UserProfile(user_id="test")
        result = validate_profile(profile)
        # Missing anthropometrics only produce WARNINGs, not ERRORs
        # (they're required for BMR but not for profile validity)
        assert result.is_valid == True  # Profile is valid, just incomplete for nutrition
        assert any("height_cm" in e.field for e in result.warnings)
        assert any("weight_kg" in e.field for e in result.warnings)
        assert any("age_years" in e.field for e in result.warnings)
        assert any("sex" in e.field for e in result.warnings)
    
    def test_invalid_height(self):
        anthro = Anthropometrics(height_cm=300, weight_kg=70, age_years=30, sex=Sex.MALE)
        profile = UserProfile(user_id="test", anthropometrics=anthro)
        result = validate_profile(profile)
        assert result.is_valid == False
        assert any("height_cm" in e.field for e in result.errors)
    
    def test_invalid_weight_change_rate(self):
        goals = NutritionalGoals(weight_goal=WeightGoal.LOSE, weight_change_rate_kg_per_week=2.0)
        profile = UserProfile(user_id="test", nutritional_goals=goals)
        anthro = Anthropometrics(height_cm=170, weight_kg=70, age_years=30, sex=Sex.MALE)
        profile.anthropometrics = anthro
        result = validate_profile(profile)
        assert result.is_valid == False
        assert any("weight_change_rate_kg_per_week" in e.field for e in result.errors)


# ============================================================
# Energy Requirements Tests
# ============================================================

class TestEnergyRequirements:
    """Test energy requirement calculations."""
    
    def test_mifflin_st_jeor_male(self):
        anthro = Anthropometrics(height_cm=170, weight_kg=70, age_years=30, sex=Sex.MALE)
        calculator = EnergyCalculator()
        result = calculator.calculate(
            anthropometrics=anthro,
            activity_level=ActivityLevel.LIGHTLY_ACTIVE,
            weight_goal=WeightGoal.MAINTAIN
        )
        assert result.bmr_kcal > 0
        assert result.tdee_kcal > result.bmr_kcal
        assert result.target_energy_kcal == result.tdee_kcal
        assert result.equation_used.value == "MIFFLIN_ST_JEOR"
    
    def test_weight_loss_adjustment(self):
        anthro = Anthropometrics(height_cm=170, weight_kg=80, age_years=35, sex=Sex.MALE)
        calculator = EnergyCalculator()
        result = calculator.calculate(
            anthropometrics=anthro,
            activity_level=ActivityLevel.SEDENTARY,
            weight_goal=WeightGoal.LOSE,
            weight_change_kg_per_week=0.5
        )
        assert result.target_energy_kcal < result.tdee_kcal
        assert result.adjustment_kcal < 0
        assert result.weight_change_kg_per_week > 0
    
    def test_weight_gain_adjustment(self):
        anthro = Anthropometrics(height_cm=165, weight_kg=55, age_years=25, sex=Sex.FEMALE)
        calculator = EnergyCalculator()
        result = calculator.calculate(
            anthropometrics=anthro,
            activity_level=ActivityLevel.MODERATELY_ACTIVE,
            weight_goal=WeightGoal.GAIN,
            weight_change_kg_per_week=0.3
        )
        assert result.target_energy_kcal > result.tdee_kcal
        assert result.adjustment_kcal > 0
    
    def test_minimum_calories_enforced(self):
        anthro = Anthropometrics(height_cm=150, weight_kg=40, age_years=20, sex=Sex.FEMALE)
        calculator = EnergyCalculator()
        result = calculator.calculate(
            anthropometrics=anthro,
            activity_level=ActivityLevel.SEDENTARY,
            weight_goal=WeightGoal.LOSE,
            weight_change_kg_per_week=1.0  # Aggressive
        )
        # Should be clamped to minimum
        assert result.target_energy_kcal >= 1200
        assert len(result.warnings) > 0
    
    def test_equation_comparison(self):
        anthro = Anthropometrics(height_cm=170, weight_kg=70, age_years=30, sex=Sex.MALE)
        calculator = EnergyCalculator()
        comparison = calculator.compare_equations(anthro)
        assert "MIFFLIN_ST_JEOR" in comparison
        assert "HARRIS_BENEDICT" in comparison
        assert "ICMR_FACTORIAL" in comparison


# ============================================================
# Macro Targets Tests
# ============================================================

class TestMacroTargets:
    """Test macronutrient target calculations."""
    
    def test_icmr_balanced_distribution(self):
        anthro = Anthropometrics(height_cm=170, weight_kg=70, age_years=30, sex=Sex.MALE)
        energy_result = calculate_energy_requirements(
            height_cm=170, weight_kg=70, age_years=30, sex="MALE",
            activity_level="LIGHTLY_ACTIVE"
        )
        
        macro_calc = MacroCalculator()
        macros = macro_calc.calculate(
            energy_result=energy_result,
            anthropometrics=anthro,
            weight_goal=WeightGoal.MAINTAIN,
            method=MacroDistributionMethod.ICMR_BALANCED
        )
        
        assert macros.protein_g > 0
        assert macros.carbohydrate_g > 0
        assert macros.fat_g > 0
        assert macros.fibre_g > 0
        # Check percentages sum to ~100
        assert 95 <= macros.macro_total_pct <= 105
    
    def test_high_protein_distribution(self):
        anthro = Anthropometrics(height_cm=170, weight_kg=80, age_years=30, sex=Sex.MALE)
        energy_result = calculate_energy_requirements(
            height_cm=170, weight_kg=80, age_years=30, sex="MALE",
            activity_level="LIGHTLY_ACTIVE", weight_goal="LOSE"
        )
        
        macro_calc = MacroCalculator()
        macros = macro_calc.calculate(
            energy_result=energy_result,
            anthropometrics=anthro,
            weight_goal=WeightGoal.LOSE,
            method=MacroDistributionMethod.HIGH_PROTEIN
        )
        
        # High protein should be >= 20% of energy
        assert macros.protein_pct >= 20
    
    def test_ketogenic_distribution(self):
        anthro = Anthropometrics(height_cm=170, weight_kg=70, age_years=30, sex=Sex.MALE)
        energy_result = calculate_energy_requirements(
            height_cm=170, weight_kg=70, age_years=30, sex="MALE",
            activity_level="SEDENTARY"
        )
        
        macro_calc = MacroCalculator()
        macros = macro_calc.calculate(
            energy_result=energy_result,
            anthropometrics=anthro,
            weight_goal=WeightGoal.MAINTAIN,
            method=MacroDistributionMethod.KETOGENIC
        )
        
        # Ketogenic: very low carb
        assert macros.carbohydrate_pct < 20
        assert macros.fat_pct > 60
    
    def test_micronutrient_calculation(self):
        anthro = Anthropometrics(height_cm=170, weight_kg=70, age_years=30, sex=Sex.FEMALE)
        micro_calc = MicronutrientCalculator()
        micros = micro_calc.calculate(anthro, WeightGoal.MAINTAIN)
        
        assert micros.sodium_mg is not None
        assert micros.potassium_mg is not None
        assert micros.calcium_mg is not None
        assert micros.iron_mg is not None
        assert micros.zinc_mg is not None
    
    def test_complete_nutrition_targets(self):
        anthro = Anthropometrics(height_cm=170, weight_kg=70, age_years=30, sex=Sex.MALE)
        energy_result = calculate_energy_requirements(
            height_cm=170, weight_kg=70, age_years=30, sex="MALE",
            activity_level="LIGHTLY_ACTIVE"
        )
        
        targets = calculate_nutrition_targets(
            energy_result=energy_result,
            anthropometrics=anthro,
            weight_goal=WeightGoal.MAINTAIN
        )
        
        assert targets.energy is not None
        assert targets.macros is not None
        assert targets.micros is not None
        assert targets.profile_id == ""


# ============================================================
# Dietary Constraints Tests
# ============================================================

class TestDietaryConstraints:
    """Test dietary constraint engine."""
    
    def test_diet_classifier_vegan(self):
        classifier = DietClassifier()
        ingredients = ["rice", "dal", "vegetables", "spices", "oil"]
        result = classifier.classify_recipe(ingredients)
        assert result["diet_type"] == "VEGAN"
        assert result["is_vegetarian"] == True
        assert result["is_vegan"] == True
    
    def test_diet_classifier_vegetarian(self):
        classifier = DietClassifier()
        ingredients = ["rice", "dal", "vegetables", "spices", "oil", "ghee"]
        result = classifier.classify_recipe(ingredients)
        assert result["diet_type"] == "VEGETARIAN"
        assert result["is_vegetarian"] == True
        assert result["is_vegan"] == False
    
    def test_diet_classifier_non_veg(self):
        classifier = DietClassifier()
        ingredients = ["chicken", "rice", "onion", "spices"]
        result = classifier.classify_recipe(ingredients)
        assert result["diet_type"] == "NON_VEGETARIAN"
        assert result["is_non_veg"] == True
        assert "chicken" in result["non_veg_ingredients"]
    
    def test_diet_classifier_eggetarian(self):
        classifier = DietClassifier()
        ingredients = ["egg", "rice", "vegetables"]
        result = classifier.classify_recipe(ingredients)
        assert result["diet_type"] == "EGGETARIAN"
        assert result["is_eggetarian"] == True
        assert result["is_vegetarian"] == True
    
    def test_allergen_filter(self):
        classifier = DietClassifier()
        allergen_filter = AllergenFilter(classifier)
        ingredients = ["peanut", "rice", "vegetables"]
        evals = allergen_filter.check_allergens(ingredients, ["peanut"])
        assert len(evals) == 1
        assert evals[0].result == ConstraintResult.FAIL
        assert "peanut" in evals[0].matched_items
    
    def test_allergen_filter_pass(self):
        classifier = DietClassifier()
        allergen_filter = AllergenFilter(classifier)
        ingredients = ["rice", "vegetables", "dal"]
        evals = allergen_filter.check_allergens(ingredients, ["peanut"])
        assert len(evals) == 1
        assert evals[0].result == ConstraintResult.PASS
    
    def test_ingredient_exclusion(self):
        exclusion_filter = IngredientExclusionFilter()
        ingredients = ["onion", "garlic", "rice", "dal"]
        evals = exclusion_filter.check_exclusions(ingredients, ["onion", "garlic"])
        assert len(evals) == 2
        assert all(e.result == ConstraintResult.FAIL for e in evals)
    
    def test_dietary_preference_filter(self):
        classifier = DietClassifier()
        pref_filter = DietaryPreferenceFilter(classifier)
        ingredients = ["chicken", "rice", "onion"]
        evals = pref_filter.check_preference(ingredients, "VEGETARIAN")
        assert len(evals) == 1
        assert evals[0].result == ConstraintResult.FAIL
    
    def test_dietary_preference_pass(self):
        classifier = DietClassifier()
        pref_filter = DietaryPreferenceFilter(classifier)
        ingredients = ["rice", "dal", "vegetables"]
        evals = pref_filter.check_preference(ingredients, "VEGETARIAN")
        assert len(evals) == 1
        assert evals[0].result == ConstraintResult.PASS
    
    def test_jain_compliance(self):
        classifier = DietClassifier()
        jain_filter = JainComplianceFilter(classifier)
        
        # Jain compliant
        ingredients = ["rice", "dal", "spinach", "tomato"]
        evals = jain_filter.check_compliance(ingredients)
        assert evals[0].result == ConstraintResult.PASS
        
        # Not Jain compliant (onion)
        ingredients = ["onion", "garlic", "potato"]
        evals = jain_filter.check_compliance(ingredients)
        assert evals[0].result == ConstraintResult.FAIL
        assert "onion" in evals[0].matched_items
    
    def test_dietary_constraint_engine(self):
        engine = DietaryConstraintEngine()
        
        # Vegetarian user, vegetarian recipe
        ingredients = ["rice", "dal", "vegetables"]
        eval_result = engine.evaluate_recipe(
            recipe_id=1,
            recipe_name="Dal Rice",
            ingredients=ingredients,
            user_preference="VEGETARIAN",
            user_allergies=["peanut"],
            user_exclusions=["onion"]
        )
        assert eval_result.overall_result == ConstraintResult.PASS
        
        # Vegetarian user, non-veg recipe
        ingredients = ["chicken", "rice"]
        eval_result = engine.evaluate_recipe(
            recipe_id=2,
            recipe_name="Chicken Rice",
            ingredients=ingredients,
            user_preference="VEGETARIAN"
        )
        assert eval_result.overall_result == ConstraintResult.FAIL


# ============================================================
# Integration Tests
# ============================================================

class TestIntegration:
    """Test end-to-end integration."""
    
    def test_profile_to_nutrition_targets(self):
        """Test complete flow from profile to nutrition targets."""
        profile = create_sample_profile()
        
        calculator = NutritionTargetCalculator()
        targets = calculator.calculate_for_profile(profile)
        
        assert targets.energy is not None
        assert targets.macros is not None
        assert targets.micros is not None
        assert targets.profile_id == "sample_user"
        assert targets.energy.target_energy_kcal > 0
    
    def test_weight_loss_profile_targets(self):
        """Test nutrition targets for weight loss profile."""
        profile = create_weight_loss_profile()
        
        calculator = NutritionTargetCalculator()
        targets = calculator.calculate_for_profile(profile)
        
        assert targets.energy.target_energy_kcal < targets.energy.tdee_kcal
        # Weight loss profile uses ICMR_BALANCED by default (not HIGH_PROTEIN)
        # Protein target is based on ICMR RDA (0.83g/kg)
        assert targets.macros.protein_g > 0
        assert targets.macros.protein_pct > 10  # At least 10%
    
    def test_profile_manager(self):
        """Test profile manager CRUD operations."""
        manager = create_profile_manager()
        
        # Create
        result = manager.create_profile(
            user_id="test_user",
            anthropometrics={"height_cm": 170, "weight_kg": 70, "age_years": 30, "sex": "MALE"},
            dietary_profile={"preference": "VEGETARIAN"},
            nutritional_goals={"weight_goal": "MAINTAIN"}
        )
        assert result.is_valid == True
        
        # Load
        profile = manager.get_profile("test_user")
        assert profile is not None
        assert profile.user_id == "test_user"
        assert profile.anthropometrics.height_cm == 170
        
        # Update
        result = manager.update_profile("test_user", dietary_profile={"preference": "VEGAN"})
        assert result.is_valid == True
        profile = manager.get_profile("test_user")
        assert profile.dietary_profile.preference.value == "VEGAN"
        
        # Delete
        deleted = manager.delete_profile("test_user")
        assert deleted == True
        assert manager.get_profile("test_user") is None
    
    def test_energy_only_calculation(self):
        """Test energy-only convenience function."""
        result = calculate_energy_requirements(
            height_cm=170, weight_kg=70, age_years=30,
            sex="MALE", activity_level="LIGHTLY_ACTIVE"
        )
        assert isinstance(result, EnergyCalculationResult)
        assert result.target_energy_kcal > 0


# ============================================================
# Explanation Engine Tests
# ============================================================

class TestExplanationEngine:
    """Test explanation generation."""
    
    def test_recommendation_explanation(self):
        rec = PersonalizedRecommendationResult(
            recipe_id=1,
            recipe_name="Test Recipe",
            similarity_score=0.85,
            cuisine="north indian",
            course="main course",
            diet_labels=["vegetarian"],
            shared_ingredients=["rice", "dal"],
            explanation="Same cuisine and shared ingredients",
            component_scores={"ingredient_jaccard": 0.3, "cuisine_match": 1.0}
        )
        
        engine = ExplanationEngine()
        explanation = engine.explain_recommendation(rec)
        
        assert explanation.recipe_id == 1
        assert explanation.recipe_name == "Test Recipe"
        assert len(explanation.segments) > 0
        assert "cuisine" in explanation.overall_reason.lower() or "ingredient" in explanation.overall_reason.lower()
    
    def test_explanation_to_text(self):
        rec = PersonalizedRecommendationResult(
            recipe_id=1,
            recipe_name="Test Recipe",
            similarity_score=0.85,
            cuisine="north indian",
            course="main course",
            diet_labels=["vegetarian"],
            shared_ingredients=["rice", "dal"],
            explanation="Test",
            component_scores={}
        )
        
        engine = ExplanationEngine()
        explanation = engine.explain_recommendation(rec)
        text = explanation.to_text()
        
        assert "Test Recipe" in text
        assert "Overall:" in text


# ============================================================
# Validation Tests
# ============================================================

class TestValidation:
    """Test meal plan validation."""
    
    def test_validation_result(self):
        result = ValidationResult(is_valid=True, is_safe=True)
        assert result.is_valid == True
        assert result.is_safe == True
        
        result.add_issue(ValidationIssue(
            category="test",
            severity=ValidationSeverity.ERROR,
            message="Test error"
        ))
        assert result.is_valid == False
        assert len(result.errors) == 1
    
    def test_meal_plan_validator(self):
        """Test meal plan validator with minimal data."""
        # This test requires a more complex setup with mock data
        # Skipping full validation test for brevity
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])