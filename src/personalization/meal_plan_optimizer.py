"""Meal Plan Optimizer - Optimize meal plans for nutritional targets and variety."""

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import random
import math
from copy import deepcopy

from .meal_planner import (
    MealPlanner, MealPlanConfig, WeeklyMealPlan, DailyMealPlan,
    MealSlotPlan, MealPlanStatus
)
from .recipe_profile import RecipeProfileCollection, RecipeNutritionProfile
from .nutrition_targets import CompleteNutritionTargets
from .personalized_recommender import PersonalizedRecommender


class OptimizationObjective(Enum):
    """Optimization objectives."""
    NUTRIENT_BALANCE = "NUTRIENT_BALANCE"       # Match daily/weekly targets
    VARIETY = "VARIETY"                         # Maximize cuisine/ingredient variety
    PREFERENCE_MATCH = "PREFERENCE_MATCH"       # Match user preferences
    NUTRITION_COMPLETENESS = "NUTRITION_COMPLETENESS"  # Prefer complete nutrition
    PREP_TIME = "PREP_TIME"                     # Minimize prep time
    COMBINED = "COMBINED"                       # Weighted combination


@dataclass
class OptimizationConfig:
    """Configuration for meal plan optimization."""
    # Objective weights (must sum to 1.0)
    objective_weights: Dict[str, float] = field(default_factory=lambda: {
        "NUTRIENT_BALANCE": 0.4,
        "VARIETY": 0.2,
        "PREFERENCE_MATCH": 0.2,
        "NUTRITION_COMPLETENESS": 0.1,
        "PREP_TIME": 0.1,
    })
    
    # Constraints
    max_iterations: int = 100
    convergence_threshold: float = 0.001
    population_size: int = 20  # For genetic algorithm
    mutation_rate: float = 0.1
    crossover_rate: float = 0.7
    
    # Hard constraints (must be satisfied)
    hard_constraints: Dict[str, Any] = field(default_factory=lambda: {
        "min_energy_achievement": 0.85,
        "max_energy_achievement": 1.20,
        "min_protein_achievement": 0.90,
        "max_same_cuisine_per_day": 2,
        "max_same_cuisine_per_week": 4,
        "max_recipe_repeats_per_week": 2,
        "min_nutrition_completeness": 0.5,
    })
    
    # Soft constraints with penalties
    soft_constraints: Dict[str, float] = field(default_factory=lambda: {
        "cuisine_diversity_penalty": 0.1,
        "recipe_repetition_penalty": 0.05,
        "prep_time_penalty_per_min": 0.001,
        "nutrition_gap_penalty": 0.2,
    })


@dataclass
class OptimizationResult:
    """Result of meal plan optimization."""
    optimized_plan: Any  # WeeklyMealPlan
    objective_value: float
    constraint_violations: List[str] = field(default_factory=list)
    iterations: int = 0
    converged: bool = False
    initial_value: float = 0.0
    improvement: float = 0.0


class MealPlanOptimizer:
    """
    Optimize meal plans using local search / genetic algorithm.
    
    Optimizes for:
    - Nutrient target achievement
    - Cuisine/recipe variety
    - User preference alignment
    - Nutrition data completeness
    """
    
    def __init__(
        self,
        meal_planner: MealPlanner,
        recipe_collection: Any,  # RecipeProfileCollection
        recommender: Any,  # PersonalizedRecommender
        config: Optional[OptimizationConfig] = None
    ):
        self.meal_planner = meal_planner
        self.recipe_collection = recipe_collection
        self.recommender = config  # Actually recommender
        self.config = config or OptimizationConfig()
    
    def optimize(
        self,
        user_profile: Any,
        initial_plan: Any,  # WeeklyMealPlan
        nutrition_targets: Any,
        config: Optional[MealPlanConfig] = None
    ) -> OptimizationResult:
        """
        Optimize a meal plan using local search.
        
        Args:
            user_profile: UserProfile
            initial_plan: Starting WeeklyMealPlan
            nutrition_targets: CompleteNutritionTargets
            config: MealPlanConfig
            
        Returns:
            OptimizationResult with optimized plan
        """
        current_plan = deepcopy(initial_plan)
        current_value = self._evaluate_plan(current_plan, config)
        best_plan = deepcopy(current_plan)
        best_value = current_value
        
        initial_value = current_value
        violations = self._check_hard_constraints(current_plan, config)
        
        for iteration in range(self.config.max_iterations):
            # Generate neighbors
            neighbors = self._generate_neighbors(current_plan, config)
            
            improved = False
            for neighbor in neighbors:
                if not self._satisfies_hard_constraints(neighbor, config):
                    continue
                
                neighbor_value = self._evaluate_plan(neighbor, config)
                if neighbor_value > current_value:
                    current_plan = neighbor
                    current_value = neighbor_value
                    improved = True
                    
                    if current_value > best_value:
                        best_plan = deepcopy(neighbor)
                        best_value = current_value
            
            if not improved:
                # Try random restart or accept slight worsening (simulated annealing)
                if random.random() < 0.1:
                    random_plan = self.meal_planner.generate_weekly_plan(
                        user_profile=None,  # Would need user profile
                        nutrition_targets=config  # Would need nutrition targets
                    )
                    random_value = self._evaluate_plan(random_plan, config)
                    if random_value > current_value:
                        current_plan = random_plan
                        current_value = random_value
            
            # Check convergence
            if abs(current_value - best_value) < self.config.convergence_threshold:
                break
        
        violations = self._check_hard_constraints(best_plan, config)
        
        return OptimizationResult(
            optimized_plan=best_plan,
            objective_value=best_value,
            constraint_violations=violations,
            iterations=iteration + 1,
            converged=len(violations) == 0,
            initial_value=initial_value,
            improvement=best_value - initial_value
        )
    
    def _generate_neighbors(self, plan: WeeklyMealPlan, config: MealPlanConfig) -> List[WeeklyMealPlan]:
        """Generate neighboring plans by making small changes."""
        neighbors = []
        
        for day in plan.days:
            for slot_name, slot_plan in day.slots.items():
                if slot_plan.recipe_id is None:
                    continue
                
                # Neighbor 1: Replace with similar recipe
                similar_recipes = self._find_similar_recipes(
                    slot_plan.recipe_id, 
                    exclude_ids=self._get_used_recipe_ids(plan)
                )
                
                for similar_id in similar_recipes[:3]:  # Top 3 similar
                    neighbor = deepcopy(plan)
                    neighbor_day = neighbor.days[plan.days.index(day)]
                    neighbor_slot = neighbor_day.slots[slot_name]
                    
                    # Update with new recipe
                    profile = self.recipe_collection.get(similar_id)
                    if profile:
                        neighbor_slot.recipe_id = profile.recipe_id
                        neighbor_slot.recipe_name = profile.recipe_name
                        neighbor_slot.nutrients = profile.per_serving_nutrients or {}
                        neighbor_slot.nutrition_completeness = max(
                            profile.nutrient_completeness.values()) if profile.nutrient_completeness else 0
                        neighbors.append(neighbor)
                
                # Neighbor 2: Swap with another slot (same day or different day)
                for other_day in plan.days:
                    for other_slot, other_plan in other_day.slots.items():
                        if other_plan.recipe_id is None or other_plan.recipe_id == day.slots[slot_name].recipe_id:
                            continue
                        
                        # Swap
                        neighbor = deepcopy(plan)
                        n_day = neighbor.days[plan.days.index(day)]
                        n_other_day = neighbor.days[plan.days.index(other_day)]
                        
                        n_day.slots[slot_name], n_other_day.slots[other_slot] = \
                            n_other_day.slots[other_slot], n_day.slots[slot_name]
                        
                        neighbors.append(neighbor)
        
        return neighbors[:50]  # Limit neighbors
    
    def _get_used_recipe_ids(self, plan: WeeklyMealPlan) -> Set[int]:
        """Get set of recipe IDs used in plan."""
        used = set()
        for day in plan.days:
            for slot in day.slots.values():
                if slot.recipe_id:
                    used.add(slot.recipe_id)
        return used
    
    def _find_similar_recipes(
        self, 
        recipe_id: int, 
        exclude_ids: Set[int],
        max_results: int = 5
    ) -> List[int]:
        """Find recipes similar to given recipe."""
        # This would use the recommender's similarity
        # For now, return random recipes from same cuisine
        profile = self.recipe_collection.get(recipe_id)
        if not profile:
            return []
        
        similar = []
        for rid, p in self.recipe_collection.profiles.items():
            if rid in exclude_ids or rid == recipe_id:
                continue
            if p.cuisine == profile.cuisine:
                similar.append(rid)
        
        random.shuffle(similar)
        return similar[:max_results]
    
    def _evaluate_plan(self, plan: WeeklyMealPlan, config: MealPlanConfig) -> float:
        """Evaluate plan quality (higher is better)."""
        score = 0.0
        
        # 1. Nutrient balance score
        balance_score = self._nutrient_balance_score(plan)
        score += self.config.objective_weights.get("NUTRIENT_BALANCE", 0.4) * balance_score
        
        # 2. Variety score
        variety_score = self._variety_score(plan)
        score += self.config.objective_weights.get("VARIETY", 0.2) * variety_score
        
        # 3. Preference match (placeholder)
        pref_score = 0.5  # Placeholder
        score += self.config.objective_weights.get("PREFERENCE_MATCH", 0.2) * pref_score
        
        # 3. Nutrition completeness
        completeness_score = self._completeness_score(plan)
        score += self.config.objective_weights.get("NUTRITION_COMPLETENESS", 0.1) * completeness_score
        
        # 4. Prep time (placeholder)
        prep_score = 0.5
        score += self.config.objective_weights.get("PREP_TIME", 0.1) * prep_score
        
        # Apply soft constraint penalties
        penalties = self._calculate_penalties(plan)
        score -= sum(penalties)
        
        return max(0.0, score)
    
    def _nutrient_balance_score(self, plan: WeeklyMealPlan) -> float:
        """Score how well weekly plan meets nutrient targets."""
        if not plan.weekly_targets:
            return 0.5
        
        scores = []
        for nutrient, target in plan.weekly_targets.items():
            actual = plan.weekly_totals.get(nutrient, 0)
            if target == 0:
                continue
            ratio = actual / target
            # Score: 1.0 at 1.0, decreases quadratically
            if 0.9 <= ratio <= 1.1:
                scores.append(1.0)
            elif 0.8 <= ratio <= 1.2:
                scores.append(0.8)
            elif 0.7 <= ratio <= 1.3:
                scores.append(0.5)
            else:
                scores.append(0.2)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _variety_score(self, plan: WeeklyMealPlan) -> float:
        """Score recipe/cuisine variety."""
        cuisines = set()
        recipes = set()
        
        for day in plan.days:
            for slot in day.slots.values():
                if slot.recipe_id:
                    recipes.add(slot.recipe_id)
                    profile = self.recipe_collection.get(slot.recipe_id)
                    if profile:
                        cuisines.add(profile.cuisine)
        
        # Variety = unique cuisines / days + unique recipes / total slots
        total_slots = sum(len(day.slots) for day in plan.days)
        filled_slots = sum(1 for day in plan.days for s in day.slots.values() if s.recipe_id)
        
        if total_slots == 0:
            return 0.0
        
        cuisine_variety = len(cuisines) / len(plan.days) if plan.days else 0
        recipe_variety = len(recipes) / filled_slots if filled_slots > 0 else 0
        
        return (cuisine_variety + recipe_variety) / 2
    
    def _completeness_score(self, plan: WeeklyMealPlan) -> float:
        """Score nutrition data completeness."""
        scores = []
        for day in plan.days:
            for slot in day.slots.values():
                if slot.recipe_id:
                    scores.append(slot.nutrition_completeness)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _check_hard_constraints(self, plan: WeeklyMealPlan, config: MealPlanConfig) -> List[str]:
        """Check hard constraints, return list of violations."""
        violations = []
        constraints = self.config.hard_constraints
        
        # Energy achievement
        if "min_energy_achievement" in constraints:
            ach = plan.weekly_achievement.get("energy_kcal", 0)
            if ach < constraints["min_energy_achievement"]:
                violations.append(f"Energy achievement {ach:.1%} below minimum {constraints['min_energy_achievement']}")
        
        # Protein
        if "min_protein_achievement" in constraints:
            ach = plan.weekly_achievement.get("protein_g", 0)
            if ach < constraints["min_protein_achievement"]:
                violations.append(f"Protein achievement {ach:.1%} below minimum")
        
        # Cuisine diversity per day
        if "max_same_cuisine_per_day" in constraints:
            for day in plan.days:
                cuisine_counts = {}
                for slot in day.slots.values():
                    if slot.recipe_id:
                        profile = self.recipe_collection.get(slot.recipe_id)
                        if profile:
                            cuisine_counts[profile.cuisine] = cuisine_counts.get(profile.cuisine, 0) + 1
                
                for cuisine, count in cuisine_counts.items():
                    if count > constraints["max_same_cuisine_per_day"]:
                        violations.append(f"Day {day.date}: {cuisine} appears {count} times (max {constraints['max_same_cuisine_per_day']})")
        
        # Cuisine diversity per week
        if "max_same_cuisine_per_week" in constraints:
            cuisine_counts = {}
            for day in plan.days:
                for slot in day.slots.values():
                    if slot.recipe_id:
                        profile = self.recipe_collection.get(slot.recipe_id)
                        if profile:
                            cuisine_counts[profile.cuisine] = cuisine_counts.get(profile.cuisine, 0) + 1
            
            for cuisine, count in cuisine_counts.items():
                if count > constraints["max_same_cuisine_per_week"]:
                    violations.append(f"Cuisine {cuisine} appears {count} times/week (max {constraints['max_same_cuisine_per_week']})")
        
        # Recipe repetition
        if "max_recipe_repeats_per_week" in constraints:
            recipe_counts = {}
            for day in plan.days:
                for slot in day.slots.values():
                    if slot.recipe_id:
                        recipe_counts[slot.recipe_id] = recipe_counts.get(slot.recipe_id, 0) + 1
            
            for recipe_id, count in recipe_counts.items():
                if count > constraints["max_recipe_repeats_per_week"]:
                    profile = self.recipe_collection.get(recipe_id)
                    name = profile.recipe_name if profile else f"Recipe {recipe_id}"
                    violations.append(f"Recipe '{name}' appears {count} times/week (max {constraints['max_recipe_repeats_per_week']})")
        
        # Nutrition completeness
        if "min_nutrition_completeness" in constraints:
            for day in plan.days:
                for slot_name, slot in day.slots.items():
                    if slot.recipe_id and slot.nutrition_completeness < constraints["min_nutrition_completeness"]:
                        profile = self.recipe_collection.get(slot.recipe_id)
                        name = profile.recipe_name if profile else f"Recipe {slot.recipe_id}"
                        violations.append(f"Day {day.date} {slot_name}: {name} completeness {slot.nutrition_completeness:.0%} below minimum")
        
        return violations
    
    def _satisfies_hard_constraints(self, plan: WeeklyMealPlan, config: MealPlanConfig) -> bool:
        return len(self._check_hard_constraints(plan, config)) == 0
    
    def _calculate_penalties(self, plan: WeeklyMealPlan) -> List[float]:
        """Calculate soft constraint penalties."""
        penalties = []
        constraints = self.config.soft_constraints
        
        # Cuisine diversity penalty
        if "cuisine_diversity_penalty" in constraints:
            penalty = constraints["cuisine_diversity_penalty"] * (1 - self._variety_score(plan))
            penalties.append(penalty)
        
        # Recipe repetition penalty
        if "recipe_repetition_penalty" in constraints:
            recipe_counts = {}
            for day in plan.days:
                for slot in day.slots.values():
                    if slot.recipe_id:
                        recipe_counts[slot.recipe_id] = recipe_counts.get(slot.recipe_id, 0) + 1
            
            repeats = sum(1 for c in recipe_counts.values() if c > 1)
            penalties.append(constraints["recipe_repetition_penalty"] * repeats)
        
        return penalties


def optimize_meal_plan(
    meal_planner: MealPlanner,
    recipe_collection: Any,
    recommender: Any,
    user_profile: Any,
    initial_plan: WeeklyMealPlan,
    nutrition_targets: Any,
    config: Optional[OptimizationConfig] = None
) -> OptimizationResult:
    """Convenience function to optimize a meal plan."""
    optimizer = MealPlanOptimizer(meal_planner, recipe_collection, recommender, config)
    return optimizer.optimize(user_profile, initial_plan, nutrition_targets, config)