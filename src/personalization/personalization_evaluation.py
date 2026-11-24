"""Personalization Evaluation - Evaluate recommendation and meal planning quality."""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import date, timedelta
import numpy as np
import random

from .personalized_recommender import PersonalizedRecommendationResult
from .meal_planner import WeeklyMealPlan, DailyMealPlan, MealSlotPlan
from .nutrition_targets import CompleteNutritionTargets
from .recipe_profile import RecipeProfileCollection, RecipeNutritionProfile
from ..personalization.profile_models import UserProfile


class EvaluationMetric(Enum):
    """Evaluation metric types."""
    # Recommendation metrics
    PRECISION_AT_K = "PRECISION_AT_K"
    RECALL_AT_K = "RECALL_AT_K"
    NDCG_AT_K = "NDCG_AT_K"
    MAP_AT_K = "MAP_AT_K"
    COVERAGE = "COVERAGE"
    DIVERSITY = "DIVERSITY"
    NOVELTY = "NOVELTY"
    
    # Dietary constraint metrics
    CONSTRAINT_VIOLATION_RATE = "CONSTRAINT_VIOLATION_RATE"
    UNVERIFIED_RESTRICTION_RATE = "UNVERIFIED_RESTRICTION_RATE"
    CORRECT_EXCLUSION_RATE = "CORRECT_EXCLUSION_RATE"
    
    # Nutritional planning metrics
    ENERGY_TARGET_DEVIATION = "ENERGY_TARGET_DEVIATION"
    PROTEIN_TARGET_DEVIATION = "PROTEIN_TARGET_DEVIATION"
    MACRO_BALANCE_SCORE = "MACRO_BALANCE_SCORE"
    NUTRIENT_COMPLETENESS = "NUTRIENT_COMPLETENESS"
    MEAL_PLAN_FEASIBILITY = "MEAL_PLAN_FEASIBILITY"
    DAILY_BALANCE_SCORE = "DAILY_BALANCE_SCORE"
    
    # Meal plan quality
    RECIPE_REPETITION_RATE = "RECIPE_REPETITION_RATE"
    CUISINE_DIVERSITY = "CUISINE_DIVERSITY"
    MEAL_SLOT_COMPLETION_RATE = "MEAL_SLOT_COMPLETION_RATE"
    NUTRITIONAL_ADEQUACY = "NUTRITIONAL_ADEQUACY"


@dataclass
class EvaluationResult:
    """Result of a single evaluation."""
    metric: EvaluationMetric
    value: float
    details: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    notes: str = ""


@dataclass
class EvaluationSuite:
    """Complete evaluation suite results."""
    recommendation_metrics: Dict[EvaluationMetric, EvaluationResult] = field(default_factory=dict)
    meal_plan_metrics: Dict[EvaluationMetric, EvaluationResult] = field(default_factory=dict)
    dietary_metrics: Dict[EvaluationMetric, EvaluationResult] = field(default_factory=dict)
    nutritional_metrics: Dict[EvaluationMetric, EvaluationResult] = field(default_factory=dict)
    overall_score: float = 0.0
    limitations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "recommendation_metrics": {k.value: v.__dict__ for k, v in self.recommendation_metrics.items()},
            "meal_plan_metrics": {k.value: v.__dict__ for k, v in self.meal_plan_metrics.items()},
            "dietary_metrics": {k.value: v.__dict__ for k, v in self.dietary_metrics.items()},
            "nutritional_metrics": {k.value: v.__dict__ for k, v in self.nutritional_metrics.items()},
            "overall_score": self.overall_score,
            "limitations": self.limitations,
        }


class PersonalizationEvaluator:
    """
    Evaluate personalization system quality.
    
    IMPORTANT: No genuine user interaction data exists.
    All metrics are proxy/functional correctness metrics.
    Do not claim real user personalization accuracy.
    """
    
    def __init__(self):
        pass
    
    def evaluate_recommendations(
        self,
        recommendations: List[PersonalizedRecommendationResult],
        ground_truth_relevant: Optional[List[int]] = None,
        k_values: List[int] = [5, 10, 20],
        recipe_collection: Optional[Any] = None
    ) -> Dict[EvaluationMetric, EvaluationResult]:
        """
        Evaluate recommendation quality.
        
        Note: Without genuine user relevance data, these are proxy metrics.
        """
        results = {}
        
        if not recommendations:
            return {m: EvaluationResult(metric=m, value=0.0, notes="No recommendations") 
                     for m in EvaluationMetric if m in [
                         EvaluationMetric.PRECISION_AT_K, EvaluationMetric.RECALL_AT_K,
                         EvaluationMetric.COVERAGE, EvaluationMetric.DIVERSITY
                     ]}
        
        # Coverage: proportion of recipe catalog recommended
        if hasattr(self, '_catalog_size') and self._catalog_size > 0:
            unique_recs = len(set(r.recipe_id for r in recommendations))
            coverage = unique_recs / self._catalog_size
            results[EvaluationMetric.COVERAGE] = EvaluationResult(
                metric=EvaluationMetric.COVERAGE,
                value=coverage,
                details={"unique_recommended": unique_recs, "catalog_size": self._catalog_size},
                notes="Proxy metric - catalog coverage"
            )
        
        # Diversity: intra-list diversity
        if len(recommendations) > 1:
            diversity = self._calculate_diversity(recommendations)
            results[EvaluationMetric.DIVERSITY] = EvaluationResult(
                metric=EvaluationMetric.DIVERSITY,
                value=diversity,
                details={"num_recommendations": len(recommendations)},
                notes="Intra-list diversity (proxy for variety)"
            )
        
        # Precision/Recall (if ground truth available)
        if ground_truth_relevant:
            for k in [5, 10, 20]:
                if len(recommendations) >= k:
                    top_k = recommendations[:k]
                    retrieved = set(r.recipe_id for r in top_k)
                    relevant = set(ground_truth_relevant)
                    
                    precision = len(retrieved & relevant) / k
                    recall = len(retrieved & relevant) / len(relevant) if relevant else 0
                    
                    results[EvaluationMetric.PRECISION_AT_K] = EvaluationResult(
                        metric=EvaluationMetric.PRECISION_AT_K,
                        value=precision,
                        details={"k": k, "retrieved": len(retrieved), "relevant": len(relevant)}
                    )
                    results[EvaluationMetric.RECALL_AT_K] = EvaluationResult(
                        metric=EvaluationMetric.RECALL_AT_K,
                        value=recall,
                        details={"k": k, "retrieved": len(retrieved), "relevant": len(relevant)}
                    )
        
        return results
    
    def _calculate_diversity(self, recommendations: List[PersonalizedRecommendationResult]) -> float:
        """Calculate intra-list diversity (average pairwise dissimilarity)."""
        n = len(recommendations)
        if n < 2:
            return 0.0
        
        # Use cuisine and course diversity as proxy
        cuisines = [r.cuisine for r in recommendations]
        courses = [r.course for r in recommendations]
        
        cuisine_diversity = len(set(cuisines)) / len(cuisines) if cuisines else 0
        course_diversity = len(set(courses)) / len(courses) if courses else 0
        
        # Also check ingredient overlap diversity
        avg_overlap = np.mean([r.component_scores.get("ingredient_jaccard", 0) for r in recommendations])
        ingredient_diversity = 1 - avg_overlap
        
        return (cuisine_diversity + course_diversity + ingredient_diversity) / 3
    
    def evaluate_meal_plan(
        self,
        plan: Any,  # WeeklyMealPlan
        nutrition_targets: Optional[Any] = None,
        recipe_collection: Optional[Any] = None,
        user_profile: Optional[Any] = None
    ) -> Dict[EvaluationMetric, EvaluationResult]:
        """
        Evaluate meal plan quality.
        """
        results = {}
        
        if not plan.days:
            return {m: EvaluationResult(metric=m, value=0.0, notes="Empty plan") 
                     for m in EvaluationMetric}
        
        # Meal slot completion rate
        total_slots = sum(len(day.slots) for day in plan.days)
        filled_slots = sum(1 for day in plan.days for s in day.slots.values() if s.recipe_id)
        completion_rate = filled_slots / total_slots if total_slots > 0 else 0
        
        results[EvaluationMetric.MEAL_SLOT_COMPLETION_RATE] = EvaluationResult(
            metric=EvaluationMetric.MEAL_SLOT_COMPLETION_RATE,
            value=completion_rate,
            details={"total_slots": total_slots, "filled": filled_slots},
            notes="Proportion of meal slots with assigned recipes"
        )
        
        # Nutritional adequacy
        if nutrition_targets:
            adequacy = self._calculate_nutritional_adequacy(plan, nutrition_targets)
            results[EvaluationMetric.NUTRITIONAL_ADEQUACY] = EvaluationResult(
                metric=EvaluationMetric.NUTRITIONAL_ADEQUACY,
                value=adequacy,
                details={"weekly_achievement": plan.weekly_achievement},
                notes="Proportion of nutrient targets met"
            )
            
            # Energy target deviation
            energy_ach = plan.weekly_achievement.get("energy_kcal", 0)
            energy_dev = abs(1.0 - energy_ach)
            results[EvaluationMetric.ENERGY_TARGET_DEVIATION] = EvaluationResult(
                metric=EvaluationMetric.ENERGY_TARGET_DEVIATION,
                value=energy_dev,
                details={"weekly_energy_achievement": energy_ach},
                notes="Absolute deviation from 100% energy target"
            )
            
            # Protein target deviation
            protein_ach = plan.weekly_achievement.get("protein_g", 0)
            protein_dev = abs(1.0 - protein_ach)
            results[EvaluationMetric.PROTEIN_TARGET_DEVIATION] = EvaluationResult(
                metric=EvaluationMetric.PROTEIN_TARGET_DEVIATION,
                value=protein_dev,
                details={"weekly_protein_achievement": protein_ach},
                notes="Absolute deviation from 100% protein target"
            )
            
            # Macro balance score
            macro_balance = self._calculate_macro_balance(plan, nutrition_targets)
            results[EvaluationMetric.MACRO_BALANCE_SCORE] = EvaluationResult(
                metric=EvaluationMetric.MACRO_BALANCE_SCORE,
                value=macro_balance,
                details={},
                notes="Balance of macro achievement across energy, protein, carb, fat"
            )
        
        # Recipe repetition rate
        recipe_counts = {}
        for day in plan.days:
            for slot in day.slots.values():
                if slot.recipe_id:
                    recipe_counts[slot.recipe_id] = recipe_counts.get(slot.recipe_id, 0) + 1
        
        total_recipe_slots = sum(recipe_counts.values())
        repeated_slots = sum(1 for c in recipe_counts.values() if c > 1)
        repetition_rate = repeated_slots / total_recipe_slots if total_recipe_slots > 0 else 0
        
        results[EvaluationMetric.RECIPE_REPETITION_RATE] = EvaluationResult(
            metric=EvaluationMetric.RECIPE_REPETITION_RATE,
            value=repetition_rate,
            details={"total_recipe_slots": total_recipe_slots, "repeated": repeated_slots},
            notes="Proportion of meal slots with repeated recipes"
        )
        
        # Cuisine diversity
        cuisines = set()
        for day in plan.days:
            for slot in day.slots.values():
                if slot.recipe_id and self.recipe_collection:
                    profile = self.recipe_collection.get(slot.recipe_id)
                    if profile:
                        cuisines.add(profile.cuisine)
        
        cuisine_diversity = len(cuisines) / len(plan.days) if plan.days else 0
        results[EvaluationMetric.CUISINE_DIVERSITY] = EvaluationResult(
            metric=EvaluationMetric.CUISINE_DIVERSITY,
            value=cuisine_diversity,
            details={"unique_cuisines": len(cuisines), "total_days": len(plan.days)},
            notes="Average unique cuisines per day"
        )
        
        # Daily balance score
        balance_score = self._calculate_daily_balance(plan)
        results[EvaluationMetric.DAILY_BALANCE_SCORE] = EvaluationResult(
            metric=EvaluationMetric.DAILY_BALANCE_SCORE,
            value=balance_score,
            details={},
            notes="Energy distribution balance across meal slots per day"
        )
        
        # Nutrition completeness
        if plan.days:
            total_slots = sum(len(day.slots) for day in plan.days)
            complete_slots = sum(1 for day in plan.days for s in day.slots.values() 
                               if s.recipe_id and s.nutrition_completeness >= 0.9)
            completeness = complete_slots / sum(len(day.slots) for day in plan.days) if plan.days else 0
            
            results[EvaluationMetric.NUTRIENT_COMPLETENESS] = EvaluationResult(
                metric=EvaluationMetric.NUTRIENT_COMPLETENESS,
                value=completeness,
                details={"complete_slots": complete_slots, "total_slots": sum(len(d.slots) for d in plan.days)},
                notes="Proportion of meal slots with >=90% nutrition completeness"
            )
        
        # Meal plan feasibility
        feasibility = self._calculate_feasibility(plan, nutrition_targets)
        results[EvaluationMetric.MEAL_PLAN_FEASIBILITY] = EvaluationResult(
            metric=EvaluationMetric.MEAL_PLAN_FEASIBILITY,
            value=feasibility,
            details={},
            notes="Composite feasibility score"
        )
        
        return results
    
    def _calculate_nutritional_adequacy(self, plan: Any, targets: Any) -> float:
        """Calculate overall nutritional adequacy score."""
        if not plan.weekly_achievement:
            return 0.0
        
        scores = []
        for nutrient, target in targets.macros.__dict__.items():
            if target and nutrient in plan.weekly_achievement:
                ach = plan.weekly_achievement.get(nutrient, 0)
                # Score: 1.0 at 1.0, linear down to 0.0 at 0.5 and 1.5
                if 0.9 <= ach <= 1.1:
                    scores.append(1.0)
                elif 0.8 <= ach <= 1.2:
                    scores.append(0.8)
                elif 0.7 <= ach <= 1.3:
                    scores.append(0.5)
                else:
                    scores.append(0.2)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _calculate_macro_balance(self, plan: Any, targets: Any) -> float:
        """Calculate macro balance score."""
        if not plan.weekly_achievement:
            return 0.0
        
        # Score based on how balanced the macro achievements are
        achievements = []
        for nutrient in ["energy_kcal", "protein_g", "carbohydrate_g", "fat_g"]:
            if nutrient in plan.weekly_achievement:
                achievements.append(plan.weekly_achievement[nutrient])
        
        if not achievements:
            return 0.0
        
        # Balance = 1 - coefficient of variation
        mean_ach = sum(achievements) / len(achievements)
        if mean_ach == 0:
            return 0.0
        
        cv = np.std(achievements) / mean_ach
        balance = max(0, 1 - cv)
        return balance
    
    def _calculate_daily_balance(self, plan: Any) -> float:
        """Calculate daily energy balance score."""
        if not plan.days:
            return 0.0
        
        daily_scores = []
        for day in plan.days:
            slot_energies = {}
            for slot_name, slot in day.slots.items():
                if slot.recipe_id and "energy_kcal" in slot.nutrients:
                    slot_energies[slot_name] = slot.nutrients["energy_kcal"]
            
            if not slot_energies:
                continue
            
            total = sum(slot_energies.values())
            if total == 0:
                continue
            
            # Check if distribution is reasonable (no slot > 50% or < 5%)
            scores = []
            for energy in slot_energies.values():
                pct = energy / total
                if 0.1 <= pct <= 0.5:
                    scores.append(1.0)
                elif 0.05 <= pct <= 0.6:
                    scores.append(0.5)
                else:
                    scores.append(0.0)
            
            daily_scores.append(sum(scores) / len(scores) if scores else 0)
        
        return sum(daily_scores) / len(daily_scores) if daily_scores else 0.0
    
    def _calculate_feasibility(self, plan: Any, targets: Any) -> float:
        """Calculate overall feasibility score."""
        if not plan.days:
            return 0.0
        
        scores = []
        
        # Completion rate
        total = sum(len(day.slots) for day in plan.days)
        filled = sum(1 for day in plan.days for s in day.slots.values() if s.recipe_id)
        scores.append(filled / total if total > 0 else 0)
        
        # Nutritional adequacy
        if targets:
            scores.append(self._calculate_nutritional_adequacy(plan, targets))
        
        # Variety
        recipes = set()
        for day in plan.days:
            for slot in day.slots.values():
                if slot.recipe_id:
                    recipes.add(slot.recipe_id)
        variety_score = len(recipes) / filled if filled > 0 else 0
        scores.append(variety_score)
        
        # Daily completeness
        complete_days = sum(1 for day in plan.days if day.is_complete)
        scores.append(complete_days / len(plan.days))
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def evaluate_dietary_constraints(
        self,
        plan: Any,
        user_profile: Any,
        dietary_engine: Any
    ) -> Dict[EvaluationMetric, EvaluationResult]:
        """
        Evaluate dietary constraint compliance.
        
        Note: Requires actual dietary evaluations per slot.
        """
        results = {}
        
        # This would evaluate each slot's dietary evaluation
        # For now, return placeholder
        results[EvaluationMetric.CONSTRAINT_VIOLATION_RATE] = EvaluationResult(
            metric=EvaluationMetric.CONSTRAINT_VIOLATION_RATE,
            value=0.0,
            details={},
            notes="Not implemented - requires per-slot dietary evaluations"
        )
        
        results[EvaluationMetric.UNVERIFIED_RESTRICTION_RATE] = EvaluationResult(
            metric=EvaluationMetric.UNVERIFIED_RESTRICTION_RATE,
            value=0.0,
            details={},
            notes="Not implemented"
        )
        
        results[EvaluationMetric.CORRECT_EXCLUSION_RATE] = EvaluationResult(
            metric=EvaluationMetric.CORRECT_EXCLUSION_RATE,
            value=0.0,
            details={},
            notes="Not implemented"
        )
        
        return results
    
    def run_full_evaluation(
        self,
        recommendations: List[PersonalizedRecommendationResult],
        meal_plan: Any,
        nutrition_targets: Optional[Any] = None,
        recipe_collection: Optional[Any] = None,
        user_profile: Optional[Any] = None,
        ground_truth_relevant: Optional[List[int]] = None
    ) -> EvaluationSuite:
        """Run complete evaluation suite."""
        
        # Set catalog size for coverage
        if recipe_collection:
            self._catalog_size = len(recipe_collection.profiles)
        
        # Run all evaluations
        rec_metrics = self.evaluate_recommendations(
            recommendations=recommendations,
            ground_truth_relevant=ground_truth_relevant,
            recipe_collection=recipe_collection
        )
        
        meal_metrics = self.evaluate_meal_plan(
            plan=meal_plan,
            nutrition_targets=nutrition_targets,
            recipe_collection=recipe_collection
        )
        
        dietary_metrics = self.evaluate_dietary_constraints(
            plan=meal_plan,
            user_profile=None,
            dietary_engine=None
        )
        
        # Calculate overall score (weighted average)
        all_metrics = {**rec_metrics, **meal_metrics}
        weights = {
            EvaluationMetric.PRECISION_AT_K: 0.1,
            EvaluationMetric.RECALL_AT_K: 0.1,
            EvaluationMetric.COVERAGE: 0.1,
            EvaluationMetric.DIVERSITY: 0.1,
            EvaluationMetric.MEAL_SLOT_COMPLETION_RATE: 0.15,
            EvaluationMetric.NUTRITIONAL_ADEQUACY: 0.15,
            EvaluationMetric.MACRO_BALANCE_SCORE: 0.1,
            EvaluationMetric.RECIPE_REPETITION_RATE: 0.05,
            EvaluationMetric.CUISINE_DIVERSITY: 0.05,
            EvaluationMetric.DAILY_BALANCE_SCORE: 0.05,
            EvaluationMetric.NUTRIENT_COMPLETENESS: 0.05,
            EvaluationMetric.MEAL_PLAN_FEASIBILITY: 0.05,
        }
        
        total_weight = 0
        weighted_sum = 0
        for metric, result in all_metrics.items():
            weight = weights.get(metric, 0)
            if weight > 0:
                weighted_sum += result.value * weight
                total_weight += weight
        
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0
        
        # Limitations
        limitations = [
            "No genuine user interaction data - all metrics are proxy/functional",
            "No ground truth relevance for recommendation metrics",
            "Dietary constraint evaluation not fully implemented",
            "Proxy metrics used for nutritional adequacy",
            "No clinical validation of nutrition targets",
            "Meal plan feasibility is simulated, not tested with real users"
        ]
        
        return EvaluationSuite(
            recommendation_metrics=rec_metrics,
            meal_plan_metrics=meal_metrics,
            dietary_metrics={},
            nutritional_metrics={k: v for k, v in meal_metrics.items() if k in [
                EvaluationMetric.NUTRITIONAL_ADEQUACY,
                EvaluationMetric.ENERGY_TARGET_DEVIATION,
                EvaluationMetric.PROTEIN_TARGET_DEVIATION,
                EvaluationMetric.MACRO_BALANCE_SCORE,
                EvaluationMetric.NUTRIENT_COMPLETENESS,
                EvaluationMetric.MEAL_PLAN_FEASIBILITY,
            ]},
            overall_score=overall_score,
            limitations=limitations
        )


def evaluate_personalization_system(
    recommendations: List[PersonalizedRecommendationResult],
    meal_plan: Any,
    nutrition_targets: Optional[Any] = None,
    recipe_collection: Optional[Any] = None,
    user_profile: Optional[Any] = None,
    ground_truth_relevant: Optional[List[int]] = None
) -> EvaluationSuite:
    """Convenience function to run full evaluation."""
    evaluator = PersonalizationEvaluator()
    return evaluator.run_full_evaluation(
        recommendations=recommendations,
        meal_plan=meal_plan,
        nutrition_targets=nutrition_targets,
        recipe_collection=recipe_collection,
        user_profile=user_profile,
        ground_truth_relevant=ground_truth_relevant
    )


def generate_evaluation_report(suite: EvaluationSuite) -> str:
    """Generate human-readable evaluation report."""
    lines = [
        "PERSONALIZATION SYSTEM EVALUATION REPORT",
        "=" * 50,
        f"Overall Score: {suite.overall_score:.3f}",
        "",
        "RECOMMENDATION METRICS:",
        "-" * 30,
    ]
    
    for metric, result in suite.recommendation_metrics.items():
        lines.append(f"  {metric.value}: {result.value:.4f} ({result.notes})")
    
    lines.append("")
    lines.append("MEAL PLAN METRICS:")
    lines.append("-" * 30)
    
    for metric, result in suite.meal_plan_metrics.items():
        lines.append(f"  {metric.value}: {result.value:.4f} ({result.notes})")
    
    lines.append("")
    lines.append("LIMITATIONS:")
    lines.append("-" * 30)
    for lim in suite.limitations:
        lines.append(f"  • {lim}")
    
    return "\n".join(lines)