# Phase 4: Meal Planning Architecture Report

**Date:** 2026-11-19  
**Status:** Implementation Complete

---

## 1. Overview

The Meal Planning system (`src/personalization/meal_planner.py`, `meal_plan_optimizer.py`, `meal_plan_validation.py`) generates personalized meal plans with nutritional validation, variety controls, and practical constraints.

---

## 2. Architecture

### 2.1 Core Components

| Module | Class | Purpose |
|--------|-------|---------|
| `meal_planner.py` | `MealPlanner` | Generate daily/weekly meal plans |
| `meal_plan_optimizer.py` | `MealPlanOptimizer` | Optimize plans via local search |
| `meal_plan_validation.py` | `MealPlanValidator` | Validate nutritional adequacy & safety |
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
    dietary_evaluation: Optional[Dict]
    recommendation_score: float
    explanation: str

@dataclass
class DailyMealPlan:
    date: str
    slots: Dict[str, MealSlotPlan]
    total_nutrients: Dict[str, float]
    target_nutrients: Dict[str, float]
    nutrient_achievement: Dict[str, float]
    status: str  # COMPLETE/PARTIAL/FAILED
    notes: List[str]

@dataclass
class WeeklyMealPlan:
    start_date: str
    days: List[DailyMealPlan]
    weekly_totals: Dict[str, float]
    weekly_targets: Dict[str, float]
    weekly_achievement: Dict[str, float]
    status: str  # SUCCESS/PARTIAL/FAILED
    notes: List[str]
    generated_at: str
```

---

## 2. Configuration

```python
@dataclass
class MealPlanConfig:
    # Meal planning
    days: int = 7
    meal_frequency: int = 4  # 3, 4, 5, 6
    allow_recipe_repetition: bool = False
    max_recipe_repeats_per_week: int = 2
    
    # Nutritional targets
    daily_energy_tolerance_pct: float = 10.0
    protein_min_achievement: float = 0.9
    nutrient_balance_weight: float = 0.3
    
    # Variety
    cuisine_diversity_weight: float = 0.2
    max_same_cuisine_per_day: int = 2
    max_same_cuisine_per_week: int = 4
    require_cuisine_variety: bool = True
    
    # Constraints
    max_prep_time_min: Optional[int] = None
    max_cook_time_min: Optional[int] = None
    max_total_time_min: Optional[int] = None
    budget_tier: Optional[str] = None
    
    # Recipe selection
    min_nutrition_completeness: float = 0.0
    min_recommendation_score: float = 0.0
    prefer_nutrition_completeness: bool = True
    allow_unverified_dietary: bool = False
    
    # Repetition control
    track_recipe_history: bool = True
    max_consecutive_days_same_recipe: int = 1
```

---

## 3. MealPlanner (Core Generator)

### 3.1 Initialization
```python
planner = MealPlanner(
    personalized_recommender,  # PersonalizedRecommender
    nutrition_targets,          # CompleteNutritionTargets
    recipe_profile_collection,  # RecipeProfileCollection
    config=MealPlanConfig()
)
```

### 3.2 Weekly Plan Generation
```python
def generate_weekly_plan(
    user_profile,
    start_date=None,
    nutrition_targets=None,
    config=None
) -> WeeklyMealPlan:
    # 1. Determine meal slots from user profile
    # 2. Get daily targets from nutrition_targets
    # 3. Generate each day sequentially
    # 4. Track recipe/cuisine history
    # 5. Calculate weekly totals
```

### 3.3 Daily Plan Generation
```python
def _generate_daily_plan(
    user_profile,
    date_str,
    meal_slots,
    daily_targets,
    config,
    day_index
) -> DailyMealPlan:
    # 1. Get meal energy distribution
    # 2. For each slot:
    #    - Calculate meal targets (fraction of daily)
    #    - Build filters (course, exclude recent recipes)
    #    - Get recommendation from personalized recommender
    #    - Deduct from remaining targets
    # 3. Calculate totals & achievement
    # 4. Determine status (COMPLETE/PARTIAL/FAILED)
```

### 3.4 Meal Energy Distribution
| Meals | Distribution |
|-------|--------------|
| 3 | B: 30%, L: 40%, D: 30% |
| 4 | B: 25%, L: 35%, S: 15%, D: 25% |
| 5 | B: 25%, M: 10%, L: 35%, E: 10%, D: 20% |
| 6 | B: 20%, M: 10%, L: 30%, A: 10%, E: 10%, D: 20% |

### 3.5 Tracking & Variety Controls
```python
def _update_tracking(daily_plan, date_str):
    # Update recipe history (prevent 3-day repeat)
    # Update cuisine counts (daily/weekly limits)
```

---

## 4. MealPlanOptimizer (Local Search)

### 4.1 OptimizationConfig
```python
@dataclass
class OptimizationConfig:
    objective_weights: Dict = {
        "NUTRIENT_BALANCE": 0.4,
        "VARIETY": 0.2,
        "PREFERENCE_MATCH": 0.2,
        "NUTRITION_COMPLETENESS": 0.1,
        "PREP_TIME": 0.1,
    }
    
    hard_constraints: Dict = {
        "min_energy_achievement": 0.85,
        "max_energy_achievement": 1.20,
        "min_protein_achievement": 0.90,
        "max_same_cuisine_per_day": 2,
        "max_same_cuisine_per_week": 4,
        "max_recipe_repeats_per_week": 2,
        "min_nutrition_completeness": 0.5,
    }
    
    max_iterations: int = 100
    convergence_threshold: float = 0.001
```

### 4.2 Local Search Algorithm
```python
def optimize(user_profile, initial_plan, nutrition_targets, config):
    current_plan = deepcopy(initial_plan)
    best_plan = deepcopy(current_plan)
    
    for iteration in range(max_iterations):
        neighbors = _generate_neighbors(current_plan)
        
        for neighbor in neighbors:
            if not _satisfies_hard_constraints(neighbor):
                continue
            if _evaluate_plan(neighbor) > current_value:
                current_plan = neighbor
                if current_value > best_value:
                    best_plan = deepcopy(neighbor)
        
        if converged: break
    
    return OptimizationResult(optimized_plan=best_plan, ...)
```

### 4.3 Neighbor Generation
1. **Replace with similar recipe** - Same cuisine, similar ingredients
2. **Swap slots** - Within day or across days

### 4.4 Evaluation Function
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

---

## 5. MealPlanValidator (Quality Assurance)

### 5.1 ValidationSeverity
```python
class ValidationSeverity(Enum):
    ERROR = "ERROR"       # Plan should not be used
    WARNING = "WARNING"   # May affect outcomes
    INFO = "INFO"         # Informational
```

### 5.2 Validation Checks

| Category | Checks |
|----------|--------|
| **Structure** | Days exist, slots exist, recipes assigned |
| **Nutritional Adequacy** | Weekly/daily achievement vs targets (min/max) |
| **Safety** | Min calories (1500M/1200F), max deficit 25% |
| **Daily Balance** | No slot <5% or >50% of daily energy |
| **Variety** | Recipe repetition ≤2/week, cuisine ≤40%/week, ≤2/day |
| **Completeness** | ≥50% slots with ≥90% nutrition data |
| **Practicality** | Prep time vs user constraint, skill level |

### 5.3 Validation Result
```python
@dataclass
class ValidationResult:
    is_valid: bool
    is_safe: bool
    issues: List[ValidationIssue]
    errors: List[ValidationIssue]
    warnings: List[ValidationIssue]
    info: List[ValidationIssue]
    summary: Dict
```

---

## 6. Plan Generation Flow

```
UserProfile + NutritionTargets
         │
         ▼
MealPlanner.generate_weekly_plan()
         │
         ▼
For each day (7):
    For each meal slot:
        1. Calculate meal targets
        2. Build filters (course, exclude recent)
        2. PersonalizedRecommender.recommend()
        3. Select top recommendation
        4. Deduct from remaining targets
    5. Validate daily plan
    6. Update tracking
         │
         ▼
WeeklyMealPlan + tracking data
         │
         ▼
MealPlanOptimizer.optimize()  (optional)
         │
         ▼
MealPlanValidator.validate_weekly_plan()
         │
         ▼
Final WeeklyMealPlan + ValidationResult
```

---

## 7. Current Limitations

| Limitation | Impact |
|------------|--------|
| **Zero approved mappings** | Nutrition completeness = 0%; optimizer/validator limited |
| **No recipe cost data** | Budget constraint not implemented |
| **Static recommender** | No learning from user feedback |
| **Heuristic meal-slot courses** | Course labels may not match actual meal timing |
| **No portion optimization** | Servings fixed at 1.0 |
| **No leftover/meal-prep logic** | Each meal independent |
| **Optimizer needs recommender** | Circular dependency in current design |

---

## 8. Files

| File | Purpose |
|------|---------|
| `src/personalization/meal_planner.py` | Core generator |
| `src/personalization/meal_plan_optimizer.py` | Local search optimizer |
| `src/personalization/meal_plan_validation.py` | QA validator |
| `src/personalization/meal_plan_models.py` | Shared data models |
| `tests/phase4/test_personalization.py` | Integration tests |

---

## 9. Configuration Example

```python
# Weight loss, 5 meals, 30min max prep, beginner
config = MealPlanConfig(
    days=7,
    meal_frequency=5,
    max_total_time_min=30,
    allow_recipe_repetition=True,
    max_recipe_repeats_per_week=2,
    max_same_cuisine_per_day=2,
    require_cuisine_variety=True,
    min_nutrition_completeness=0.0,
    prefer_nutrition_completeness=True,
)
```

---

*End of Meal Planning Architecture Report*