"""Meal Plan Validation - Validate meal plans for nutritional adequacy and safety."""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import date, timedelta

from .meal_planner import WeeklyMealPlan, DailyMealPlan, MealSlotPlan, MealPlanConfig
from .nutrition_targets import CompleteNutritionTargets
from .recipe_profile import RecipeProfileCollection, RecipeNutritionProfile
from ..personalization.profile_models import UserProfile


class ValidationSeverity(Enum):
    """Validation issue severity."""
    ERROR = "ERROR"       # Plan should not be used
    WARNING = "WARNING"   # May affect outcomes, review recommended
    INFO = "INFO"         # Informational


@dataclass
class ValidationIssue:
    """Single validation issue."""
    category: str
    severity: ValidationSeverity
    message: str
    affected_slots: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    recommendation: str = ""


@dataclass
class ValidationResult:
    """Result of meal plan validation."""
    is_valid: bool
    is_safe: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    errors: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    info: List[ValidationIssue] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    
    def add_issue(self, issue: ValidationIssue):
        self.issues.append(issue)
        if issue.severity == ValidationSeverity.ERROR:
            self.errors.append(issue)
            self.is_valid = False
            self.is_safe = False
        elif issue.severity == ValidationSeverity.WARNING:
            self.warnings.append(issue)
            if self.is_valid:  # Only invalidate on ERROR
                self.is_valid = True  # Warnings don't invalidate
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0


class MealPlanValidator:
    """
    Validate meal plans for nutritional adequacy, safety, and quality.
    
    Checks:
    - Nutritional adequacy vs targets
    - Safety (allergens, contraindications)
    - Dietary compliance
    - Variety and balance
    - Practicality (prep time, servings)
    """
    
    # Minimum safe calorie levels
    MIN_CALORIES = {"male": 1500, "female": 1200}
    
    # Maximum safe calorie deficit
    MAX_DEFICIT_PCT = 0.25
    
    # Nutrient RDA minimums (as % of target)
    MIN_NUTRIENT_ACHIEVEMENT = {
        "energy_kcal": 0.85,
        "protein_g": 0.90,
        "carbohydrate_g": 0.80,
        "fat_g": 0.80,
        "fibre_g": 0.70,
    }
    
    # Maximum safe nutrient levels (as % of target)
    MAX_NUTRIENT_ACHIEVEMENT = {
        "energy_kcal": 1.30,
        "protein_g": 2.00,
        "fat_g": 1.50,
        "sodium_mg": 1.50,
    }
    
    def __init__(
        self,
        recipe_collection: Optional[Any] = None,  # RecipeProfileCollection
        user_profile: Optional[UserProfile] = None,
        nutrition_targets: Optional[CompleteNutritionTargets] = None
    ):
        self.recipe_collection = recipe_collection
        self.user_profile = user_profile
        self.nutrition_targets = nutrition_targets
    
    def validate_weekly_plan(
        self,
        plan: Any,  # WeeklyMealPlan
        user_profile: Optional[UserProfile] = None,
        nutrition_targets: Optional[CompleteNutritionTargets] = None
    ) -> ValidationResult:
        """
        Validate a weekly meal plan.
        
        Args:
            plan: WeeklyMealPlan to validate
            user_profile: UserProfile for personalized checks
            nutrition_targets: CompleteNutritionTargets for target comparison
            
        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True, is_safe=True)
        
        profile = user_profile or self.user_profile
        targets = nutrition_targets or self.nutrition_targets
        
        # 1. Basic structure validation
        self._validate_structure(plan, result)
        
        # 2. Nutritional adequacy
        if targets:
            self._validate_nutritional_adequacy(plan, targets, result)
        
        # 3. Safety checks
        if profile:
            self._validate_safety(plan, profile, result)
        
        # 4. Daily balance
        self._validate_daily_balance(plan, result)
        
        # 5. Variety and repetition
        self._validate_variety(plan, result)
        
        # 5. Completeness
        self._validate_completeness(plan, result)
        
        # 6. Practicality
        if profile:
            self._validate_practicality(plan, profile, result)
        
        # Generate summary
        result.summary = self._generate_summary(plan, profile, targets, result)
        
        return result
    
    def _validate_structure(self, plan: Any, result: ValidationResult):
        """Validate basic plan structure."""
        if not plan.days:
            result.add_issue(ValidationIssue(
                category="structure",
                severity=ValidationSeverity.ERROR,
                message="Weekly plan has no days",
                recommendation="Ensure plan has at least 1 day"
            ))
            return
        
        for day in plan.days:
            if not day.slots:
                result.add_issue(ValidationIssue(
                    category="structure",
                    severity=ValidationSeverity.WARNING,
                    message=f"Day {day.date} has no meal slots",
                    affected_slots=[day.date],
                    recommendation="Add meal slots for each day"
                ))
            
            for slot_name, slot in day.slots.items():
                if slot.recipe_id is None:
                    result.add_issue(ValidationIssue(
                        category="structure",
                        severity=ValidationSeverity.WARNING,
                        message=f"Day {day.date} {slot_name}: No recipe assigned",
                        affected_slots=[f"{day.date}:{slot_name}"],
                        recommendation="Assign a recipe or mark slot as intentionally empty"
                    ))
    
    def _validate_nutritional_adequacy(
        self,
        plan: Any,
        targets: CompleteNutritionTargets,
        result: ValidationResult
    ):
        """Validate weekly and daily nutrient achievement."""
        macros = targets.macros
        
        # Weekly targets
        weekly_targets = {
            "energy_kcal": macros.energy_kcal * len(plan.days),
            "protein_g": macros.protein_g * len(plan.days),
            "carbohydrate_g": macros.carbohydrate_g * len(plan.days),
            "fat_g": macros.fat_g * len(plan.days),
            "fibre_g": macros.fibre_g * len(plan.days),
        }
        
        # Check weekly achievement
        for nutrient, target in weekly_targets.items():
            actual = plan.weekly_totals.get(nutrient, 0)
            if target == 0:
                continue
            
            ratio = actual / target
            
            # Check minimum
            min_ach = self.MIN_NUTRIENT_ACHIEVEMENT.get(nutrient, 0.80)
            if ratio < min_ach:
                result.add_issue(ValidationIssue(
                    category="nutrition",
                    severity=ValidationSeverity.ERROR if ratio < min_ach * 0.8 else ValidationSeverity.WARNING,
                    message=f"Weekly {nutrient} achievement {ratio:.1%} below minimum {min_ach:.0%}",
                    details={"target": target, "actual": actual, "ratio": ratio},
                    recommendation=f"Increase {nutrient.replace('_', ' ')} in meal plan"
                ))
            
            # Check maximum
            max_ach = self.MAX_NUTRIENT_ACHIEVEMENT.get(nutrient)
            if max_ach and ratio > max_ach:
                result.add_issue(ValidationIssue(
                    category="nutrition",
                    severity=ValidationSeverity.WARNING,
                    message=f"Weekly {nutrient} achievement {ratio:.1%} exceeds recommended maximum {max_ach:.0%}",
                    details={"target": target, "actual": actual, "ratio": ratio},
                    recommendation=f"Reduce {nutrient.replace('_', ' ')} in meal plan"
                ))
        
        # Daily achievement (check each day)
        for day in plan.days:
            self._validate_daily_nutrients(day, result)
    
    def _validate_daily_nutrients(self, day: DailyMealPlan, result: ValidationResult):
        """Validate daily nutrient targets."""
        # Daily targets from nutrition targets
        daily_targets = {
            "energy_kcal": day.target_nutrients.get("energy_kcal", 0),
            "protein_g": day.target_nutrients.get("protein_g", 0),
            "carbohydrate_g": day.target_nutrients.get("carbohydrate_g", 0),
            "fat_g": day.target_nutrients.get("fat_g", 0),
            "fibre_g": day.target_nutrients.get("fibre_g", 0),
        }
        
        for nutrient, target in daily_targets.items():
            if target == 0:
                continue
            
            actual = day.total_nutrients.get(nutrient, 0)
            ratio = actual / target if target > 0 else 1.0
            
            min_ach = self.MIN_NUTRIENT_ACHIEVEMENT.get(nutrient, 0.70)
            if ratio < min_ach:
                result.add_issue(ValidationIssue(
                    category="nutrition",
                    severity=ValidationSeverity.WARNING,
                    message=f"Day {day.date} {nutrient} achievement {ratio:.1%} below daily minimum {min_ach:.0%}",
                    affected_slots=[day.date],
                    details={"target": target, "actual": actual, "ratio": ratio},
                    recommendation=f"Adjust {day.date} meals to increase {nutrient.replace('_', ' ')}"
                ))
            
            max_ach = self.MAX_NUTRIENT_ACHIEVEMENT.get(nutrient)
            if max_ach and actual / target > max_ach:
                result.add_issue(ValidationIssue(
                    category="nutrition",
                    severity=ValidationSeverity.INFO,
                    message=f"Day {day.date} {nutrient} {actual/target:.1%} of target",
                    affected_slots=[day.date],
                    details={"target": target, "actual": actual}
                ))
    
    def _validate_safety(
        self,
        plan: Any,
        profile: Any,
        result: ValidationResult
    ):
        """Validate safety constraints."""
        anthro = profile.anthropometrics
        
        # Check minimum calories
        if anthro.sex:
            sex = anthro.sex.value.lower()
            min_cal = self.MIN_CALORIES.get(sex, 1200)
            
            for day in plan.days:
                energy = day.total_nutrients.get("energy_kcal", 0)
                if energy < min_cal:
                    result.add_issue(ValidationIssue(
                        category="safety",
                        severity=ValidationSeverity.ERROR,
                        message=f"Day {day.date} energy ({energy:.0f} kcal) below minimum safe ({min_cal} kcal for {sex})",
                        affected_slots=[day.date],
                        recommendation="Increase portions or add calorie-dense foods; consult healthcare provider"
                    ))
        
        # Check for rapid weight loss
        if self.nutrition_targets and self.nutrition_targets.energy:
            target = self.nutrition_targets.energy.target_energy_kcal
            if hasattr(profile, 'nutritional_goals'):
                weight_goal = profile.nutritional_goals.weight_goal
                if weight_goal and weight_goal.value == "LOSE":
                    # Already validated in energy calculation, but double-check
                    pass
    
    def _validate_daily_balance(self, plan: Any, result: ValidationResult):
        """Validate meal distribution within each day."""
        for day in plan.days:
            # Check meal distribution
            energy_by_slot = {}
            for slot_name, slot in day.slots.items():
                if slot.recipe_id and "energy_kcal" in slot.nutrients:
                    energy_by_slot[slot_name] = slot.nutrients["energy_kcal"]
            
            if not energy_by_slot:
                continue
            
            total = sum(energy_by_slot.values())
            if total == 0:
                continue
            
            # Check distribution
            for slot, energy in energy_by_slot.items():
                pct = energy / total
                # No slot should be <5% or >50% of daily energy
                if pct < 0.05:
                    result.add_issue(ValidationIssue(
                        category="balance",
                        severity=ValidationSeverity.INFO,
                        message=f"Day {day.date} {slot} only {pct:.1%} of daily energy",
                        affected_slots=[f"{day.date}:{slot}"],
                        recommendation="Consider redistributing energy across meals"
                    ))
                elif pct > 0.50:
                    result.add_issue(ValidationIssue(
                        category="balance",
                        severity=ValidationSeverity.WARNING,
                        message=f"Day {day.date} {slot} provides {pct:.1%} of daily energy (>50%)",
                        affected_slots=[f"{day.date}:{slot}"],
                        recommendation="Redistribute energy more evenly across meals"
                    ))
    
    def _validate_variety(self, plan: Any, result: ValidationResult):
        """Validate recipe and cuisine variety."""
        recipe_counts = {}
        cuisine_counts = {}
        cuisine_per_day = {}
        
        for day in plan.days:
            daily_cuisines = {}
            for slot_name, slot in day.slots.items():
                if slot.recipe_id:
                    recipe_counts[slot.recipe_id] = recipe_counts.get(slot.recipe_id, 0) + 1
                    
                    if self.recipe_collection:
                        profile = self.recipe_collection.get(slot.recipe_id)
                        if profile:
                            cuisine = profile.cuisine
                            cuisine_counts[cuisine] = cuisine_counts.get(cuisine, 0) + 1
                            daily_cuisines[cuisine] = daily_cuisines.get(cuisine, 0) + 1
            
            cuisine_per_day[day.date] = daily_cuisines
        
        # Check recipe repetition
        for recipe_id, count in recipe_counts.items():
            if count > 2:
                profile = self.recipe_collection.get(recipe_id) if self.recipe_collection else None
                name = profile.recipe_name if profile else f"Recipe {recipe_id}"
                result.add_issue(ValidationIssue(
                    category="variety",
                    severity=ValidationSeverity.WARNING if count <= 3 else ValidationSeverity.ERROR,
                    message=f"Recipe '{name}' appears {count} times in week",
                    details={"recipe_id": recipe_id, "count": count},
                    recommendation="Use different recipes for variety"
                ))
        
        # Check cuisine diversity
        if cuisine_counts:
            total_cuisine = sum(cuisine_counts.values())
            for cuisine, count in cuisine_counts.items():
                pct = count / total_cuisine
                if pct > 0.4:  # >40% single cuisine
                    result.add_issue(ValidationIssue(
                        category="variety",
                        severity=ValidationSeverity.WARNING,
                        message=f"Cuisine '{cuisine}' is {pct:.0%} of weekly meals",
                        details={"cuisine": cuisine, "percentage": pct},
                        recommendation="Include more diverse cuisines"
                    ))
        
        # Check per-day cuisine variety
        for date_str, daily_cuisines in cuisine_per_day.items():
            if len(daily_cuisines) == 1 and sum(daily_cuisines.values()) > 1:
                cuisine = list(daily_cuisines.keys())[0]
                result.add_issue(ValidationIssue(
                    category="variety",
                    severity=ValidationSeverity.INFO,
                    message=f"Day {date_str}: All meals from same cuisine ({cuisine})",
                    affected_slots=[date_str],
                    recommendation="Mix cuisines within each day for variety"
                ))
    
    def _validate_completeness(self, plan: Any, result: ValidationResult):
        """Validate nutrition data completeness."""
        total_slots = 0
        complete_slots = 0
        partial_slots = 0
        
        for day in plan.days:
            for slot_name, slot in day.slots.items():
                if slot.recipe_id is None:
                    continue
                
                total_slots += 1
                
                if slot.nutrition_completeness >= 0.9:
                    complete_slots += 1
                elif slot.nutrition_completeness >= 0.5:
                    partial_slots += 1
                else:
                    result.add_issue(ValidationIssue(
                        category="completeness",
                        severity=ValidationSeverity.WARNING,
                        message=f"Day {day.date} {slot_name}: Low nutrition completeness ({slot.nutrition_completeness:.0%})",
                        affected_slots=[f"{day.date}:{slot_name}"],
                        details={"completeness": slot.nutrition_completeness},
                        recommendation="Verify nutrition data or use recipe with better coverage"
                    ))
        
        if total_slots > 0:
            completeness_rate = complete_slots / total_slots
            if completeness_rate < 0.5:
                result.add_issue(ValidationIssue(
                    category="completeness",
                    severity=ValidationSeverity.WARNING,
                    message=f"Only {completeness_rate:.0%} of meal slots have complete nutrition data",
                    details={"complete": complete_slots, "partial": partial_slots, "total": total_slots},
                    recommendation="Improve ingredient mapping coverage"
                ))
    
    def _validate_practicality(
        self,
        plan: Any,
        profile: Any,
        result: ValidationResult
    ):
        """Validate practical considerations."""
        lifestyle = profile.lifestyle
        
        # Check time constraints
        if lifestyle.time_constraint_minutes:
            for day in plan.days:
                for slot_name, slot in day.slots.items():
                    if slot.recipe_id and self.recipe_collection:
                        profile = self.recipe_collection.get(slot.recipe_id)
                        if profile:
                            total_time = profile.prep_time_min + profile.cook_time_min
                            if total_time > lifestyle.time_constraint_minutes:
                                result.add_issue(ValidationIssue(
                                    category="practicality",
                                    severity=ValidationSeverity.WARNING,
                                    message=f"Day {day.date} {slot_name}: {total_time} min exceeds {lifestyle.time_constraint_minutes} min limit",
                                    affected_slots=[f"{day.date}:{slot_name}"],
                                    details={"prep_time": profile.prep_time_min, "cook_time": profile.cook_time_min},
                                    recommendation="Choose quicker recipes or increase time budget"
                                ))
        
        # Check cooking skill
        if lifestyle.cooking_skill == "BEGINNER":
            for day in plan.days:
                for slot_name, slot in day.slots.items():
                    if slot.recipe_id and self.recipe_collection:
                        profile = self.recipe_collection.get(slot.recipe_id)
                        if profile and (profile.prep_time_min + profile.cook_time_min) > 45:
                            result.add_issue(ValidationIssue(
                                category="practicality",
                                severity=ValidationSeverity.INFO,
                                message=f"Day {day.date} {slot_name}: {profile.prep_time_min + profile.cook_time_min} min may be challenging for beginner",
                                affected_slots=[f"{day.date}:{slot_name}"],
                                recommendation="Consider simpler recipes or meal prep"
                            ))
        
        # Check budget (placeholder - would need recipe cost data)
        if lifestyle.budget_constraint:
            result.add_issue(ValidationIssue(
                category="practicality",
                severity=ValidationSeverity.INFO,
                message="Budget constraint checking not implemented (requires recipe cost data)",
                recommendation="Add recipe cost estimation for budget validation"
            ))
    
    def _generate_summary(
        self,
        plan: Any,
        profile: Optional[Any],
        targets: Optional[CompleteNutritionTargets],
        result: ValidationResult
    ) -> Dict[str, Any]:
        """Generate validation summary."""
        return {
            "plan_days": len(plan.days),
            "total_meal_slots": sum(len(day.slots) for day in plan.days),
            "filled_meal_slots": sum(1 for day in plan.days for s in day.slots.values() if s.recipe_id),
            "unique_recipes": len(set(
                s.recipe_id for day in plan.days for s in day.slots.values() if s.recipe_id
            )),
            "unique_cuisines": len(set(
                self.recipe_collection.get(s.recipe_id).cuisine 
                for day in plan.days for s in day.slots.values() 
                if s.recipe_id and self.recipe_collection and self.recipe_collection.get(s.recipe_id)
            )),
            "errors": len(result.errors),
            "warnings": len(result.warnings),
            "info": len(result.info),
            "is_valid": result.is_valid,
            "is_safe": result.is_safe,
            "weekly_energy_achievement": plan.weekly_achievement.get("energy_kcal", 0),
            "weekly_protein_achievement": plan.weekly_achievement.get("protein_g", 0),
        }


def validate_meal_plan(
    plan: Any,
    recipe_collection: Optional[Any] = None,
    user_profile: Optional[UserProfile] = None,
    nutrition_targets: Optional[CompleteNutritionTargets] = None
) -> ValidationResult:
    """Convenience function to validate a meal plan."""
    validator = MealPlanValidator(
        recipe_collection=recipe_collection,
        user_profile=user_profile,
        nutrition_targets=nutrition_targets
    )
    return validator.validate_weekly_plan(plan, user_profile, nutrition_targets)


def validate_daily_plan(
    plan: DailyMealPlan,
    recipe_collection: Optional[Any] = None,
    user_profile: Optional[UserProfile] = None,
    nutrition_targets: Optional[CompleteNutritionTargets] = None
) -> ValidationResult:
    """Validate a single day meal plan."""
    # Create a temporary weekly plan with just this day
    from .meal_planner import WeeklyMealPlan
    weekly = WeeklyMealPlan(start_date=plan.date, days=[plan])
    
    validator = MealPlanValidator(
        recipe_collection=recipe_collection,
        user_profile=user_profile,
        nutrition_targets=nutrition_targets
    )
    return validator.validate_weekly_plan(weekly, user_profile, nutrition_targets)