# Phase 4: User Profile Architecture Report

**Date:** 2026-11-19  
**Status:** Implementation Complete

---

## 1. Architecture Overview

The user profile system is implemented in `src/personalization/` with a modular design:

```
src/personalization/
├── profile_models.py        # Core data models (enums, dataclasses)
├── profile_validation.py    # Validation logic
├── profile_repository.py    # Persistence layer
├── user_profile.py          # High-level manager interface
└── __init__.py              # Package exports
```

---

## 2. Profile Data Model (`profile_models.py`)

### 2.1 Core Enums

| Enum | Values | Purpose |
|------|--------|---------|
| `Sex` | MALE, FEMALE | Biological sex for BMR equations |
| `ActivityLevel` | SEDENTARY, LIGHTLY_ACTIVE, MODERATELY_ACTIVE, VERY_ACTIVE, EXTREMELY_ACTIVE | PAL factor selection |
| `DietaryPreference` | VEGETARIAN, VEGAN, EGGETARIAN, NON_VEGETARIAN, JAIN, PESCATARIAN, FLEXITARIAN, OMNIVORE | Dietary classification |
| `WeightGoal` | MAINTAIN, LOSE, GAIN | Weight management objective |
| `MealFrequency` | 3, 4, 5, 6 | Meals per day |
| `MealSlot` | BREAKFAST, MORNING_SNACK, LUNCH, EVENING_SNACK, DINNER | Standard meal slots |

### 2.2 Core Dataclasses

#### Anthropometrics
```python
@dataclass
class Anthropometrics:
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    age_years: Optional[int] = None
    sex: Optional[Sex] = None
    
    def has_required_for_bmr(self) -> bool:
        return all(v is not None for v in [self.height_cm, self.weight_kg, self.age_years, self.sex])
```

#### DietaryProfile
```python
@dataclass
class DietaryProfile:
    preference: DietaryPreference = DietaryPreference.OMNIVORE
    allergies: List[str] = field(default_factory=list)
    ingredient_exclusions: List[str] = field(default_factory=list)
    cuisine_preferences: List[str] = field(default_factory=list)
    cuisine_exclusions: List[str] = field(default_factory=list)
    disliked_ingredients: List[str] = field(default_factory=list)
    religious_restrictions: List[str] = field(default_factory=list)
    medical_conditions: List[str] = field(default_factory=list)
```

#### NutritionalGoals
```python
@dataclass
class NutritionalGoals:
    target_energy_kcal: Optional[float] = None
    target_protein_g: Optional[float] = None
    target_carbohydrate_g: Optional[float] = None
    target_fat_g: Optional[float] = None
    target_fibre_g: Optional[float] = None
    target_sodium_mg: Optional[float] = None
    weight_goal: WeightGoal = WeightGoal.MAINTAIN
    weight_change_rate_kg_per_week: float = 0.5
```

#### LifestyleProfile
```python
@dataclass
class LifestyleProfile:
    activity_level: ActivityLevel = ActivityLevel.SEDENTARY
    meal_frequency: MealFrequency = MealFrequency.THREE
    preferred_meal_times: Dict[str, str] = field(default_factory=dict)
    cooking_skill: Literal["BEGINNER", "INTERMEDIATE", "ADVANCED"] = "INTERMEDIATE"
    budget_constraint: Optional[Literal["LOW", "MEDIUM", "HIGH"]] = None
    time_constraint_minutes: Optional[int] = None
```

#### UserProfile (Root)
```python
@dataclass
class UserProfile:
    user_id: str
    anthropometrics: Anthropometrics = field(default_factory=Anthropometrics)
    dietary_profile: DietaryProfile = field(default_factory=DietaryProfile)
    nutritional_goals: NutritionalGoals = field(default_factory=NutritionalGoals)
    lifestyle: LifestyleProfile = field(default_factory=LifestyleProfile)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def has_minimum_for_nutrition_calculation(self) -> bool:
        return self.anthropometrics.has_required_for_bmr()
```

---

## 3. Profile Validation (`profile_validation.py`)

### 3.1 Validation Severity Levels
| Severity | Behavior |
|----------|----------|
| ERROR | Blocks profile usage for nutrition calculation |
| WARNING | May affect results, but usable |
| INFO | Informational |

### 3.2 Validation Checks

| Component | Checks |
|-----------|--------|
| **Anthropometrics** | Height 50-250cm, Weight 2-300kg, Age 1-120, BMI 10-60, Sex required for BMR |
| **Dietary Profile** | Preference/exclusion conflicts, unknown allergens/cuisines, Jain compliance |
| **Nutritional Goals** | Energy 500-5000 kcal, Protein 10-300g, Carb 20-500g, Fat 10-200g, Fibre 5-100g, Weight change 0.1-1.0 kg/week, Macro consistency with energy |
| **Lifestyle** | Time constraint 5-180 min, Meal frequency consistency |
| **Cross-field** | Weight goal vs energy target, Vegetarian preference vs non-veg cuisines, Allergies vs exclusions, Activity level vs energy target |

### 3.3 ValidationResult Structure
```python
@dataclass
class ValidationResult:
    is_valid: bool
    issues: List[ValidationIssue]
    errors: List[ValidationIssue]
    warnings: List[ValidationIssue]
    info: List[ValidationIssue]
```

### 3.4 Strict Mode
When `strict_mode=True`, WARNINGs become ERRORs for profile usage blocking.

---

## 4. Profile Repository (`profile_repository.py`)

### 4.1 Storage
- JSON files in `data/personalization/profiles/{user_id}.json`
- Atomic writes via temp file + replace
- Thread-safe with `RLock`
- In-memory index for fast lookups

### 4.2 Operations
| Method | Description |
|--------|-------------|
| `save(profile, validate=True)` | Validate and persist |
| `load(user_id)` | Load profile by ID |
| `delete(user_id)` | Remove profile |
| `exists(user_id)` | Check existence |
| `list_all()` | List all user IDs |
| `search(**filters)` | Search by dietary_preference, activity_level, age range, etc. |
| `backup(backup_dir)` | Export all profiles |
| `restore_from_backup(backup_file)` | Restore from backup |

### 4.3 Thread Safety
- `RLock` for all operations
- Atomic file writes via temp file + `replace()`

---

## 5. User Profile Manager (`user_profile.py`)

### 5.1 High-Level Interface
```python
class UserProfileManager:
    def create_profile(user_id, anthropometrics, dietary_profile, 
                       nutritional_goals, lifestyle, metadata, save=True)
    def get_profile(user_id) -> Optional[UserProfile]
    def update_profile(user_id, anthropometrics, dietary_profile,
                       nutritional_goals, lifestyle, metadata, save=True)
    def delete_profile(user_id) -> bool
    def profile_exists(user_id) -> bool
    def list_profiles() -> List[str]
    def get_meal_slots(profile) -> List[MealSlot]
    def get_meal_energy_targets(profile, daily_energy_kcal) -> Dict[MealSlot, float]
    def validate_for_nutrition(user_id) -> ValidationResult
```

### 5.2 Convenience Functions
```python
create_profile_manager(storage_dir, strict_validation=False) -> UserProfileManager
create_sample_profile(user_id="sample_user") -> UserProfile
create_weight_loss_profile(user_id="weight_loss_user") -> UserProfile
```

---

## 6. Serialization & Deserialization

### 6.1 to_dict()
Handles both enum and string values:
```python
def to_dict(self) -> Dict[str, Any]:
    # Handles both enum and string values
    sex_val = self.anthropometrics.sex
    sex_str = sex_val.value if hasattr(sex_val, 'value') else sex_val
    # ... similar for all enums
```

### 6.2 from_dict()
```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "UserProfile":
    def to_enum(enum_cls, value, default):
        if value is None: return default
        if isinstance(value, enum_cls): return value
        try: return enum_cls(value)
        except: return default
    
    return cls(
        anthropometrics=Anthropometrics(sex=to_enum(Sex, anthro.get("sex"), None), ...),
        dietary_profile=DietaryProfile(preference=to_enum(DietaryPreference, ...), ...),
        # ...
    )
```

---

## 7. Meal Slot Definitions

### 7.1 Standard Slots
| Enum | Value |
|------|-------|
| `MealSlot.BREAKFAST` | "BREAKFAST" |
| `MealSlot.MORNING_SNACK` | "MORNING_SNACK" |
| `MealSlot.LUNCH` | "LUNCH" |
| `MealSlot.EVENING_SNACK` | "EVENING_SNACK" |
| `MealSlot.DINNER` | "DINNER" |

### 7.2 Energy Distribution
```python
DEFAULT_MEAL_ENERGY_DISTRIBUTION = {
    MealSlot.BREAKFAST: 0.25,
    MealSlot.MORNING_SNACK: 0.10,
    MealSlot.LUNCH: 0.35,
    MealSlot.EVENING_SNACK: 0.10,
    MealSlot.DINNER: 0.20,
}

THREE_MEAL_DISTRIBUTION = {BREAKFAST: 0.30, LUNCH: 0.40, DINNER: 0.30}
FOUR_MEAL_DISTRIBUTION = {BREAKFAST: 0.25, LUNCH: 0.35, EVENING_SNACK: 0.15, DINNER: 0.25}
```

### 7.3 get_meal_distribution()
Handles both `int` and `MealFrequency` enum:
```python
def get_meal_distribution(meal_count) -> Dict[str, float]:
    if hasattr(meal_count, 'value'):
        meal_count = meal_count.value
    # ... returns appropriate distribution
```

---

## 8. Sample Profiles

### 8.1 create_sample_profile()
Vegetarian maintenance profile:
- 30yo Male, 170cm, 70kg
- VEGETARIAN, peanut allergy, excludes onion/garlic
- Lightly active, 4 meals/day

### 8.2 create_weight_loss_profile()
Weight loss profile:
- 35yo Female, 165cm, 85kg
- OMNIVORE, no allergies
- Sedentary, 5 meals/day, 30min time constraint

---

## 8. Testing

### 8.1 Unit Tests (`tests/phase4/test_personalization.py`)
| Test Category | Tests |
|---------------|-------|
| Profile Models | 4 |
| Profile Validation | 4 |
| Energy Requirements | 5 |
| Macro Targets | 5 |
| Dietary Constraints | 9 |
| Integration | 5 |
| Explanation Engine | 2 |
| Validation | 2 |
| **Total** | **37** |

### 8.2 Test Results
```
============================= 37 passed in 20.36s =============================
```

---

## 9. Files Created

| File | Purpose |
|------|---------|
| `src/personalization/profile_models.py` | Core data models |
| `src/personalization/profile_validation.py` | Validation logic |
| `src/personalization/profile_repository.py` | Persistence layer |
| `src/personalization/user_profile.py` | Manager interface + convenience |
| `src/personalization/__init__.py` | Package exports |
| `tests/phase4/test_personalization.py` | 37 unit tests |

---

*End of User Profile Architecture Report*