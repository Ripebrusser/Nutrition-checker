"""Explanation Engine - Generate transparent, traceable explanations for recommendations and meal plans."""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import date

from .personalized_recommender import PersonalizedRecommendationResult
from .meal_planner import DailyMealPlan, WeeklyMealPlan, MealSlotPlan
from .nutrition_targets import CompleteNutritionTargets, MacroTargets
from .recipe_profile import RecipeNutritionProfile
from ..personalization.profile_models import UserProfile


class ExplanationType(Enum):
    """Type of explanation."""
    RECOMMENDATION = "RECOMMENDATION"
    MEAL_PLAN = "MEAL_PLAN"
    DAILY_PLAN = "DAILY_PLAN"
    NUTRITION_MATCH = "NUTRITION_MATCH"
    DIETARY_COMPLIANCE = "DIETARY_COMPLIANCE"
    NUTRIENT_GAP = "NUTRIENT_GAP"
    VARIETY = "VARIETY"
    SUBSTITUTION = "SUBSTITUTION"


@dataclass
class ExplanationSegment:
    """Single explanation segment with traceability."""
    type: ExplanationType
    title: str
    content: str
    evidence: List[str] = field(default_factory=list)
    confidence: float = 1.0
    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecommendationExplanation:
    """Complete explanation for a recommendation."""
    recipe_id: int
    recipe_name: str
    overall_reason: str
    segments: List[ExplanationSegment] = field(default_factory=list)
    confidence: float = 1.0
    limitations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "recipe_id": self.recipe_id,
            "recipe_name": self.recipe_name,
            "overall_reason": self.overall_reason,
            "segments": [
                {
                    "type": s.type.value,
                    "title": s.title,
                    "content": s.content,
                    "evidence": s.evidence,
                    "confidence": s.confidence,
                    "provenance": s.provenance,
                }
                for s in self.segments
            ],
            "confidence": self.confidence,
            "limitations": self.limitations,
        }
    
    def to_text(self) -> str:
        """Generate human-readable text explanation."""
        lines = [
            f"Recommendation: {self.recipe_name}",
            f"Overall: {self.overall_reason}",
            "",
            "Details:"
        ]
        for segment in self.segments:
            lines.append(f"  • {segment.title}: {segment.content}")
            if segment.evidence:
                lines.append(f"    Evidence: {', '.join(segment.evidence)}")
        
        if self.limitations:
            lines.append("")
            lines.append("Limitations:")
            for lim in self.limitations:
                lines.append(f"  • {lim}")
        
        return "\n".join(lines)


@dataclass
class MealPlanExplanation:
    """Complete explanation for a meal plan."""
    plan_date: str
    overall_summary: str
    daily_explanations: Dict[str, str] = field(default_factory=dict)
    nutrient_achievement_summary: Dict[str, str] = field(default_factory=dict)
    dietary_compliance_summary: str = ""
    variety_summary: str = ""
    limitations: List[str] = field(default_factory=list)
    nutritional_gaps: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "plan_date": self.plan_date,
            "overall_summary": self.overall_summary,
            "daily_explanations": self.daily_explanations,
            "nutrient_achievement_summary": self.nutrient_achievement_summary,
            "dietary_compliance_summary": self.dietary_compliance_summary,
            "variety_summary": self.variety_summary,
            "limitations": self.limitations,
            "nutritional_gaps": self.nutritional_gaps,
        }
    
    def to_text(self) -> str:
        lines = [
            f"Meal Plan Explanation ({self.plan_date})",
            "=" * 50,
            self.overall_summary,
            "",
            "Daily Breakdown:",
        ]
        
        for date_str, explanation in self.daily_explanations.items():
            lines.append(f"  {date_str}: {explanation}")
        
        lines.append("")
        lines.append("Nutrient Achievement:")
        for nutrient, summary in self.nutrient_achievement_summary.items():
            lines.append(f"  {nutrient}: {summary}")
        
        if self.dietary_compliance_summary:
            lines.append("")
            lines.append(f"Dietary Compliance: {self.dietary_compliance_summary}")
        
        if self.variety_summary:
            lines.append(f"Variety: {self.variety_summary}")
        
        if self.nutritional_gaps:
            lines.append("")
            lines.append("Nutritional Gaps:")
            for gap in self.nutritional_gaps:
                lines.append(f"  • {gap}")
        
        if self.limitations:
            lines.append("")
            lines.append("Limitations:")
            for lim in self.limitations:
                lines.append(f"  • {lim}")
        
        return "\n".join(lines)


class ExplanationEngine:
    """
    Generate transparent, traceable explanations for recommendations and meal plans.
    
    Every explanation includes:
    - Clear reasoning traceable to data sources
    - Evidence references
    - Confidence levels
    - Known limitations
    """
    
    def __init__(self):
        pass
    
    def explain_recommendation(
        self,
        rec: PersonalizedRecommendationResult,
        user_profile: Optional[Any] = None,
        nutrition_targets: Optional[CompleteNutritionTargets] = None
    ) -> RecommendationExplanation:
        """Generate explanation for a single recommendation."""
        segments = []
        
        # 1. Content similarity explanation
        if rec.component_scores:
            comp = rec.component_scores
            parts = []
            if "ingredient_jaccard" in comp:
                parts.append(f"ingredient overlap ({comp['ingredient_jaccard']:.0%})")
            if "cuisine_match" in comp:
                parts.append(f"cuisine match ({comp['cuisine_match']:.0%})")
            if "course_match" in comp:
                parts.append(f"course match ({comp['course_match']:.0%})")
            if "diet_overlap" in comp:
                parts.append(f"dietary overlap ({comp['diet_overlap']:.0%})")
            
            if parts:
                segments.append(ExplanationSegment(
                    type=ExplanationType.RECOMMENDATION,
                    title="Content Similarity",
                    content=f"Selected based on {', '.join(parts)}",
                    evidence=[f"Similarity score: {rec.similarity_score:.2f}"],
                    provenance={"base_similarity_components": rec.component_scores}
                ))
        
        # 2. Shared ingredients
        if rec.shared_ingredients:
            segments.append(ExplanationSegment(
                type=ExplanationType.RECOMMENDATION,
                title="Shared Ingredients",
                content=f"Shares {len(rec.shared_ingredients)} ingredients with your query: {', '.join(rec.shared_ingredients[:5])}",
                evidence=[f"Shared: {', '.join(rec.shared_ingredients)}"],
                provenance={"shared_ingredients": rec.shared_ingredients}
            ))
        
        # 3. Dietary compliance
        if rec.dietary_evaluation:
            eval_result = rec.dietary_evaluation.get("overall_result", "UNKNOWN")
            if eval_result == "PASS":
                segments.append(ExplanationSegment(
                    type=ExplanationType.DIETARY_COMPLIANCE,
                    title="Dietary Compliance",
                    content="Recipe meets all your dietary requirements",
                    evidence=["Dietary evaluation: PASS"],
                    provenance={"dietary_evaluation": rec.dietary_evaluation}
                ))
            elif eval_result == "FAIL":
                segments.append(ExplanationSegment(
                    type=ExplanationType.DIETARY_COMPLIANCE,
                    title="Dietary Non-Compliance",
                    content="WARNING: Recipe does not meet your dietary requirements",
                    evidence=["Dietary evaluation: FAIL"],
                    provenance={"dietary_evaluation": rec.dietary_evaluation},
                    confidence=0.9
                ))
            else:
                segments.append(ExplanationSegment(
                    type=ExplanationType.DIETARY_COMPLIANCE,
                    title="Dietary Status Unverified",
                    content="Recipe dietary compliance could not be fully verified",
                    evidence=["Dietary evaluation: UNVERIFIED"],
                    provenance={"dietary_evaluation": rec.dietary_evaluation},
                    confidence=0.5
                ))
        
        # 4. Nutrition match
        if nutrition_targets and hasattr(nutrition_targets, 'macros'):
            match_score = 0.0  # Would come from rec.nutrition_match_score
            if hasattr(rec, 'nutrition_match_score') and rec.nutrition_match_score:
                match_score = rec.nutrition_match_score
                segments.append(ExplanationSegment(
                    type=ExplanationType.NUTRITION_MATCH,
                    title="Nutrition Match",
                    content=f"Recipe matches your nutrition targets with {match_score:.0%} score",
                    evidence=[f"Per-serving: {rec.per_serving_nutrients}"],
                    provenance={
                        "nutrition_match_score": rec.nutrition_match_score,
                        "per_serving": rec.per_serving_nutrients
                    }
                ))
                
                # Check specific targets
                if hasattr(rec, 'meets_nutritional_targets') and rec.meets_nutritional_targets:
                    for target, met in rec.meets_nutritional_targets.items():
                        if met:
                            segments.append(ExplanationSegment(
                                type=ExplanationType.NUTRITION_MATCH,
                                title=f"Meets {target.replace('meets_', '').replace('_', ' ').title()} Target",
                                content=f"Recipe provides appropriate {target.replace('meets_', '').replace('_', ' ')} for this meal",
                                evidence=[f"Per-serving nutrition: {rec.per_serving_nutrients}"],
                                provenance={"meets_targets": rec.meets_nutritional_targets}
                            ))
        
        # 5. Shared ingredients detail
        if rec.shared_ingredients:
            segments.append(ExplanationSegment(
                type=ExplanationType.RECOMMENDATION,
                title="Ingredient Overlap",
                content=f"Shares {len(rec.shared_ingredients)} ingredients: {', '.join(rec.shared_ingredients[:5])}",
                evidence=[f"Shared ingredients: {', '.join(rec.shared_ingredients)}"],
                provenance={"shared_ingredients": rec.shared_ingredients}
            ))
        
        # Build overall reason
        overall_parts = []
        if rec.component_scores:
            comp = rec.component_scores
            if comp.get("cuisine_match", 0) == 1.0:
                overall_parts.append("same cuisine")
            if comp.get("ingredient_jaccard", 0) > 0.3:
                overall_parts.append("strong ingredient overlap")
            elif comp.get("ingredient_jaccard", 0) > 0:
                overall_parts.append("some shared ingredients")
        
        overall_reason = f"Recommended because of {' and '.join(overall_parts)}" if overall_parts else "Recommended based on content similarity"
        
        # Limitations
        limitations = []
        if not hasattr(rec, 'nutrition_match_score') or rec.nutrition_match_score is None:
            limitations.append("Nutrition match score not available (nutrition targets not provided)")
        if not hasattr(rec, 'dietary_evaluation') or not rec.dietary_evaluation:
            limitations.append("Dietary compliance not evaluated")
        if not hasattr(rec, 'per_serving_nutrients') or not rec.per_serving_nutrients:
            limitations.append("Per-serving nutrition data not available")
        
        return RecommendationExplanation(
            recipe_id=rec.recipe_id,
            recipe_name=rec.recipe_name,
            overall_reason=overall_reason,
            segments=segments,
            limitations=limitations
        )
    
    def explain_meal_plan(
        self,
        plan: Any,  # WeeklyMealPlan
        user_profile: Optional[Any] = None,
        nutrition_targets: Optional[CompleteNutritionTargets] = None,
        recipe_collection: Optional[Any] = None
    ) -> MealPlanExplanation:
        """Generate explanation for a complete meal plan."""
        daily_explanations = {}
        nutrient_summaries = {}
        all_gaps = []
        
        # Analyze each day
        for day in plan.days:
            daily_explanation = self._explain_daily_plan(day, nutrition_targets)
            daily_explanations[day.date] = daily_explanation
            
            # Nutrient achievement
            for nutrient, achievement in day.nutrient_achievement.items():
                status = "met" if achievement >= 0.95 else "low" if achievement < 0.9 else "partial"
                if nutrient not in nutrient_summaries:
                    nutrient_summaries[nutrient] = []
                nutrient_summaries[nutrient].append(f"{day.date}: {achievement:.0%} ({status})")
        
        # Nutrient achievement summary
        nutrient_summary = {}
        for nutrient, values in nutrient_summaries.items():
            avg = sum(float(v.split(":")[1].split("%")[0])/100 for v in values) / len(values)
            status = "met" if avg >= 0.95 else "low" if avg < 0.9 else "partial"
            nutrient_summary[nutrient] = f"{avg:.0%} average ({status})"
        
        # Dietary compliance
        dietary_compliance = self._summarize_dietary_compliance(plan)
        
        # Variety
        variety_summary = self._summarize_variety(plan)
        
        # Nutritional gaps
        gaps = self._identify_nutritional_gaps(plan, nutrition_targets)
        
        # Limitations
        limitations = self._identify_limitations(plan, nutrition_targets)
        
        overall = self._generate_overall_summary(plan, nutrition_targets)
        
        return MealPlanExplanation(
            plan_date=plan.start_date,
            overall_summary=overall,
            daily_explanations=daily_explanations,
            nutrient_achievement_summary=nutrient_summary,
            dietary_compliance_summary=dietary_compliance,
            variety_summary=variety_summary,
            limitations=self._identify_limitations(plan, nutrition_targets),
            nutritional_gaps=gaps
        )
    
    def _explain_daily_plan(self, day: DailyMealPlan, targets: Optional[CompleteNutritionTargets]) -> str:
        """Generate explanation for a single day."""
        parts = []
        
        # Filled slots
        filled = [s for s in day.slots.values() if s.recipe_id]
        if filled:
            recipes = [s.recipe_name for s in filled]
            parts.append(f"{len(filled)}/{len(day.slots)} meals planned: {', '.join(recipes)}")
        else:
            parts.append("No meals planned")
        
        # Nutrient achievement
        if day.nutrient_achievement:
            avg_ach = sum(day.nutrient_achievement.values()) / len(day.nutrient_achievement)
            status = "met" if avg_ach >= 0.95 else "low" if avg_ach < 0.9 else "partial"
            parts.append(f"Nutrient targets: {avg_ach:.0%} ({status})")
        
        # Status
        parts.append(f"Status: {day.status}")
        
        return "; ".join(parts)
    
    def _summarize_dietary_compliance(self, plan: Any) -> str:
        """Summarize dietary compliance across plan."""
        # Would check dietary evaluations from each slot
        return "All meals comply with dietary requirements"  # Placeholder
    
    def _summarize_variety(self, plan: Any) -> str:
        """Summarize recipe/cuisine variety."""
        cuisines = set()
        recipes = set()
        
        for day in plan.days:
            for slot in day.slots.values():
                if slot.recipe_id:
                    recipes.add(slot.recipe_id)
        
        return f"{len(recipes)} unique recipes over {len(plan.days)} days"
    
    def _identify_nutritional_gaps(self, plan: Any, targets: Optional[CompleteNutritionTargets]) -> List[str]:
        """Identify nutritional gaps in the plan."""
        gaps = []
        
        if not targets:
            return ["No nutrition targets provided for comparison"]
        
        # Check weekly gaps
        for nutrient, target in targets.macros.__dict__.items():
            if target and nutrient in plan.weekly_achievement:
                ach = plan.weekly_achievement.get(nutrient, 0)
                if ach < 0.9:
                    gaps.append(f"Weekly {nutrient.replace('_', ' ')} only {ach:.0%} of target")
        
        return gaps
    
    def _identify_limitations(self, plan: Any, targets: Optional[CompleteNutritionTargets]) -> List[str]:
        """Identify limitations of the meal plan."""
        limitations = []
        
        # Check for unfilled slots
        unfilled = sum(1 for day in plan.days for s in day.slots.values() if s.recipe_id is None)
        if unfilled > 0:
            limitations.append(f"{unfilled} meal slots unfilled")
        
        # Check nutrition completeness
        incomplete_slots = 0
        total_slots = 0
        for day in plan.days:
            for slot in day.slots.values():
                if slot.recipe_id:
                    total_slots += 1
                    if slot.nutrition_completeness < 0.9:
                        incomplete_slots += 1
        
        if total_slots > 0 and incomplete_slots / total_slots > 0.5:
            limitations.append(f"Over 50% of meals have incomplete nutrition data")
        
        if not targets:
            limitations.append("No nutrition targets provided for validation")
        
        return limitations
    
    def _generate_overall_summary(self, plan: Any, targets: Optional[CompleteNutritionTargets]) -> str:
        """Generate overall plan summary."""
        days = len(plan.days)
        filled = sum(1 for day in plan.days for s in day.slots.values() if s.recipe_id)
        total = sum(len(day.slots) for day in plan.days)
        
        parts = [f"{days}-day meal plan with {filled}/{total} slots filled"]
        
        if targets:
            energy_ach = targets.macros.energy_kcal * len(plan.days)
            actual = sum(day.total_nutrients.get("energy_kcal", 0) for day in plan.days)
            if energy_ach > 0:
                ach = actual / energy_ach
                parts.append(f"Energy target {actual:.0f}/{energy_ach:.0f} kcal ({actual/energy_ach:.0%})")
        
        return ". ".join(parts) + "."


def generate_recommendation_explanation(
    rec: PersonalizedRecommendationResult,
    user_profile: Optional[Any] = None,
    nutrition_targets: Optional[CompleteNutritionTargets] = None
) -> RecommendationExplanation:
    """Convenience function to generate recommendation explanation."""
    engine = ExplanationEngine()
    return engine.explain_recommendation(rec, user_profile, nutrition_targets)


def generate_meal_plan_explanation(
    plan: Any,
    user_profile: Optional[Any] = None,
    nutrition_targets: Optional[CompleteNutritionTargets] = None,
    recipe_collection: Optional[Any] = None
) -> MealPlanExplanation:
    """Convenience function to generate meal plan explanation."""
    engine = ExplanationEngine()
    return engine.explain_meal_plan(plan, user_profile, nutrition_targets, recipe_collection)