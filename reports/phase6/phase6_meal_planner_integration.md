# Phase 6: Meal Planner Integration Report

**Date:** 2026-11-19  
**Status:** Implementation Complete

---

## 1. Overview

The Meal Planner integrates personalized recommendations, nutrition targets, and dietary constraints to generate daily and weekly meal plans with full nutritional tracking.

---

## 2. Architecture

### 2.1 Core Components

| Module | Class | Purpose |
|--------|-------|---------|
| `meal_planner.py` | `MealPlanner` | Core plan generation |
| `meal_plan_optimizer.py` | `MealPlanOptimizer` | Local search optimization |
| `meal_plan_validation.py` | `MealPlanValidator` | QA validation |
| `meal_plan_models.py` | Data models | Shared data structures |

### 2.2 Data Models

```python
@dataclass
class MealSlotPlan:
    meal_slot: str
    recipe_id: Optional[int]
    recipe_name: str
    servings: float
    nutrients: Dict[str, float]
    nutrition_completeness: float
    dietary_evaluation: Dict
    recommendation_score: float
    explanation: str

@dataclass
class DailyMealPlan:
    date: str
    slots: Dict[str, MealSlotPlan]
    total_nutrients: Dict[str, float]
    target_nutrients: Dict[str, float]
    nutrient_achievement: Dict[str, float]
    status: str
    notes: List[str]

@dataclass
class WeeklyMealPlan:
    start_date: str
    days: List[DailyMealPlan]
    weekly_totals: Dict[str, float]
    weekly_targets: Dict[str, float]
    weekly_achievement: Dict[str, float]
    status: str
    notes: List[str]
    generated_at: str
```

---

## 3. Meal Plan Generation

### 3.1 Generation Flow
```
User Profile + Nutrition Targets
         │
         ▼
MealPlanner.generate_weekly_plan()
         │
         ▼
For each day (1-7):
    │
    ▼
For each meal slot (B/L/D + snacks):
    │
    ▼
Calculate meal targets (energy fraction)
         │
         ▼
PersonalizedRecommender.recommend_for_meal_slot()
         │
         ▼
Select top recommendation
         │
         ▼
Deduct from daily remaining targets
         │
         ▼
Build DailyMealPlan
         │
         ▼
Build WeeklyMealPlan
```

### 3.2 Meal Energy Distribution

| Meals | Breakfast | Morning Snack | Lunch | Evening Snack | Dinner |
|-------|-----------|---------------|-------|---------------|--------|
| 3 | 30% | - | 40% | - | 30% |
| 4 | 25% | - | 35% | 15% | 25% |
| 5 | 25% | 10% | 35% | 10% | 20% |
| 6 | 20% | 10% | 30% | 10% | 20% |

### 3.3 Meal Slot → Course Mapping
| Meal Slot | Appropriate Courses |
|-----------|---------------------|
| BREAKFAST | breakfast, snack, beverage |
| MORNING_SNACK | snack, beverage, dessert |
| LUNCH | main course, lunch, rice, bread, curry, dal |
| EVENING_SNACK | snack, beverage, dessert, street food |
| DINNER | main course, dinner, rice, bread, curry, dal |

---

## 4. MealPlanner Class

### 4.1 Configuration
```python
@dataclass
class MealPlanConfig:
    days: int = 7
    meal_frequency: int = 4  # 3, 4, 5, 6
    allow_recipe_repetition: bool = False
    max_recipe_repeats_per_week: int = 2
    
    daily_energy_tolerance_pct: float = 10.0
    protein_min_achievement: float = 0.9
    nutrient_balance_weight: float = 0.3
    
    cuisine_diversity_weight: float = 0.2
    max_same_cuisine_per_day: int = 2
    max_same_cuisine_per_week: int = 4
    max_recipe_repeats_per_week: int = 2
    
    max_prep_time_min: Optional[int] = None
    max_cook_time_min: Optional[int] = None
    budget_tier: Optional[str] = None
    
    min_nutrition_completeness: float = 0.0
    min_recommendation_score: float = 0.0
    prefer_nutrition_completeness: bool = True
    allow_unverified_dietary: bool = False
    
    track_recipe_history: bool = True
    max_consecutive_days_same_recipe: int = 1
```

### 3.3 Generation Methods

```python
class MealPlanner:
    def generate_weekly_plan(
        self,
        user_profile,
        start_date=None,
        nutrition_targets=None,
        config=None
    ) -> WeeklyMealPlan:
        """Generate 7-day meal plan."""
        
    def generate_daily_plan(
        self,
        user_profile,
        date,
        nutrition_targets=None,
        config=None
    ) -> DailyMealPlan:
        """Generate single day meal plan."""
```

---

## 4. Tracking & Variety Controls

### 4.1 Recipe History Tracking
```python
def _update_tracking(self, daily_plan, date_str):
    for slot, slot_plan in daily_plan.slots.items():
        if slot_plan.recipe_id:
            rid = slot_plan.recipe_id
            self._recipe_history[rid].append(date_str)
            
            # Cuisine tracking
            profile = self.recipe_collection.get(rid)
            if profile:
                self._cuisine_counts[cuisine] += 1
                self._daily_cuisine_counts[date_str][cuisine] += 1
```

### 4.2 Variety Constraints (Hard)
| Constraint | Limit | Enforcement |
|------------|-------|-------------|
| Max same cuisine/day | 2 | Filter during recommendation |
| Max same cuisine/week | 4 | Filter during recommendation |
| Max recipe repeats/week | 2 | Exclude from candidates |
| Consecutive days same recipe | 1 | Exclude from candidates |

### 4.3 Variety Scoring (Optimizer)
```python
def _variety_score(plan):
    cuisines = set()
    recipes = set()
    for day in plan.days:
        for slot in day.slots.values():
            if slot.recipe_id:
                recipes.add(slot.recipe_id)
                profile = recipe_collection.get(slot.recipe_id)
                if profile: cuisines.add(profile.cuisine)
    
    cuisine_variety = len(cuisines) / len(plan.days)
    recipe_variety = len(recipes) / filled_slots
    return (cuisine_variety + recipe_variety) / 2
```

---

## 5. Meal Plan Optimizer

### 5.1 Optimization Algorithm
```python
class MealPlanOptimizer:
    def optimize(self, user_profile, initial_plan, nutrition_targets):
        current_plan = deepcopy(initial_plan)
        current_value = self._evaluate_plan(current_plan)
        best_plan = deepcopy(current_plan)
        best_value = current_value
        
        for iteration in range(max_iterations):
            neighbors = self._generate_neighbors(current_plan)
            
            for neighbor in neighbors:
                if not self._satisfies_hard_constraints(neighbor):
                    continue
                
                neighbor_value = self._evaluate_plan(neighbor)
                if neighbor_value > current_value:
                    current_plan = neighbor
                    current_value = neighbor_value
                    
                    if current_value > best_value:
                        best_plan = deepcopy(neighbor)
                        best_value = current_value
            
            if not improved:
                # Random restart
                if random.random() < 0.1:
                    random_plan = self.meal_planner.generate_weekly_plan(...)
                    ...
        
        return OptimizationResult(
            optimized_plan=best_plan,
            objective_value=best_value,
            constraint_violations=violations,
            iterations=iteration,
            converged=len(violations) == 0
        )
```

### 5.2 Neighbor Generation
| Neighbor Type | Description |
|---------------|-------------|
| **Replace** | Swap slot with similar recipe (same cuisine) |
| **Swap** | Exchange two slots (same day or different days) |
| **Random** | New random plan (10% chance) |

### 5.3 Evaluation Function
```python
def _evaluate_plan(plan):
    score = 0
    score += 0.4 * nutrient_balance_score(plan)
    score += 0.2 * variety_score(plan)
    score += 0.2 * preference_match(plan)
    score += 0.1 * completeness_score(plan)
    score += 0.1 * prep_time_score(plan)
    score -= penalties
    return max(0, score)
```

### 5.3 Hard Constraints (Must Satisfy)
| Constraint | Check |
|------------|-------|
| min_energy_achievement ≥ 0.85 | Weekly energy ≥ 85% target |
| max_energy_achievement ≤ 1.20 | Weekly energy ≤ 120% target |
| min_protein_achievement ≥ 0.90 | Weekly protein ≥ 90% target |
| max_same_cuisine_per_day ≤ 2 | No cuisine > 2x/day |
| max_same_cuisine_per_week ≤ 4 | No cuisine > 4x/week |
| max_recipe_repeats_per_week ≤ 2 | No recipe > 2x/week |
| min_nutrition_completeness ≥ 0.5 | Slots ≥ 50% complete |

### 5.4 Soft Constraints (Penalties)
| Penalty | Weight |
|---------|--------|
| Cuisine diversity | 0.1 × (1 - variety_score) |
| Recipe repetition | 0.05 × repeat_count |
| Prep time | 0.001 × minutes |
| Nutrition gap | 0.2 × |1 - achievement| |

---

## 5. MealPlanValidator

### 5.1 Validation Checks

| Category | Checks |
|----------|--------|
| **Structure** | Days exist, slots exist, recipes assigned |
| **Nutritional** | Weekly/daily achievement ≥ min thresholds |
| **Safety** | Min calories (1500M/1200F), max deficit 25% |
| **Daily Balance** | No slot <5% or >50% of daily energy |
| **Variety** | Recipe repeats ≤2, cuisine ≤40%/week |
| **Completeness** | ≥50% slots with ≥90% nutrition data |
| **Practicality** | Prep time vs constraint, skill level |

### 5.2 Validation Result
```python
@dataclass
class ValidationResult:
    is_valid: bool
    is_safe: bool
    issues: List[ValidationIssue]  # ERROR/WARNING/INFO
    summary: Dict
```

---

## 6. Current Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **Zero approved mappings** | Nutrition = UNAVAILABLE | Engine handles gracefully |
| **1.4% weight coverage** | Most slots = PARTIAL | Track completeness |
| **No recipe cost data** | Budget constraint N/A | Documented |
| **Static recommender** | No learning | Phase 5.4 will add |
| **Heuristic meal-slot** | Course-based | Documented |
| **No portion optimization** | Fixed 1.0 servings | Future work |
| **No meal-prep logic** | Independent meals | Future work |

---

## 7. Files

| File | Purpose |
|------|---------|
| `app/personalization/meal_planner.py` | Core generator |
| `app/personalization/meal_plan_optimizer.py` | Local search optimizer |
| `app/personalization/meal_plan_validation.py` | QA validator |
| `app/personalization/meal_plan_models.py` | Shared data models |
| `app/pages/meal_planner.py` | Create/List UI |
| `app/pages/meal_plan_detail.py` | Detail/Edit UI |

---

*End of Meal Planner Integration Report*