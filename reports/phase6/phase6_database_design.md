# Phase 6: Database Design Report

**Date:** 2026-11-19  
**Status:** Design Complete

---

## 1. Database Overview

### 1.1 Database Strategy

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **Primary DB** | SQLite | Simple, file-based, no server needed; suitable for academic demo |
| **Frozen Data** | Parquet/CSV (read-only) | Preserves frozen dataset integrity; no DB load |
| **User Data** | SQLite (separate file) | Isolated from frozen data; supports transactions |
| **ORM** | SQLAlchemy 2.0 | Modern, type-safe, async-ready |
| **Migrations** | Alembic | Version-controlled schema evolution |

### 1.2 Database Files

| File | Purpose | Access |
|------|---------|--------|
| `data/app.db` | User accounts, profiles, meal plans, preferences | Read/Write |
| `data/processed/recipes.parquet` | Frozen recipe dataset | Read-only |
| `data/interim/phase2/parsed_recipe_ingredients.parquet` | Parsed ingredients | Read-only |
| `data/interim/ifct_final_candidate/ifct_table1_candidate.parquet` | IFCT nutrition data | Read-only |
| `data/interim/phase3/stage2_3/ifct_match_candidates.parquet` | Match candidates | Read-only |
| `data/processed/phase3/approved_mappings.jsonl` | Approved mappings | Read/Write (via review app) |

---

## 2. Schema Design

### 2.1 Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────────┐       ┌─────────────┐
│    users    │       │  user_profiles   │       │   recipes   │
├─────────────┤       ├──────────────────┤       ├─────────────┤
│ id (PK)     │◄──────│ user_id (FK, UK) │       │ id (PK)     │
│ email       │       │ height_cm        │       │ recipe_id   │
│ password_h  │       │ weight_kg        │       │ name        │
│ full_name   │       │ age_years        │       │ cuisine     │
│ role        │       │ sex              │       │ course      │
│ is_active   │       │ dietary_pref     │       │ diet_labels │
│ created_at  │       │ allergies (JSON) │       │ prep_time   │
│ updated_at  │       │ exclusions (JSON)│       │ servings    │
│ last_login  │       │ cuisine_prefs    │       │ ingredients │
└─────────────┘       │ activity_level   │       │ nutrition_* │
                      │ meal_frequency   │       │ diet_class  │
                      └────────┬─────────┘       └──────┬──────┘
                               │                       │
                               ▼                       ▼
                    ┌──────────────────┐       ┌──────────────────┐
                    │   meal_plans     │       │  saved_recipes   │
                    ├──────────────────┤       ├──────────────────┤
                    │ id (PK)          │       │ id (PK)          │
                    │ user_id (FK)     │       │ user_id (FK)     │
                    │ start_date       │       │ recipe_id (FK)   │
                    │ end_date         │       │ saved_at         │
                    │ status           │       │ notes            │
                    └────────┬─────────┘       └──────────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ meal_plan_items  │
                    ├──────────────────┤
                    │ id (PK)          │
                    │ meal_plan_id(FK) │
                    │ recipe_id (FK)   │
                    │ meal_slot        │
                    │ day_index        │
                    │ servings         │
                    │ is_completed     │
                    └──────────────────┘
```

---

## 2. Table Definitions

### 2.1 users

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Primary key |
| email | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | Login email |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hash |
| full_name | VARCHAR(255) | | Display name |
| role | ENUM('USER') | DEFAULT 'USER' | Authorization |
| is_active | BOOLEAN | DEFAULT TRUE | Soft delete |
| created_at | DATETIME | DEFAULT NOW() | Record creation |
| updated_at | DATETIME | DEFAULT NOW(), ON UPDATE | Last update |
| last_login | DATETIME | NULLABLE | Last authentication |

### 2.2 user_profiles

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Primary key |
| user_id | INTEGER | FK(users.id), UNIQUE, NOT NULL | Owner |
| height_cm | FLOAT | NULLABLE | Height in cm |
| weight_kg | FLOAT | NULLABLE | Weight in kg |
| age_years | INTEGER | NULLABLE | Age |
| sex | VARCHAR(10) | NULLABLE | MALE/FEMALE |
| dietary_preference | VARCHAR(50) | DEFAULT 'OMNIVORE' | VEGAN, VEGETARIAN, etc. |
| allergies | JSON | DEFAULT [] | Allergen list |
| ingredient_exclusions | JSON | DEFAULT [] | Excluded ingredients |
| cuisine_preferences | JSON | DEFAULT [] | Preferred cuisines |
| cuisine_exclusions | JSON | DEFAULT [] | Excluded cuisines |
| disliked_ingredients | JSON | DEFAULT [] | Disliked ingredients |
| religious_restrictions | JSON | DEFAULT [] | Religious dietary rules |
| medical_conditions | JSON | DEFAULT [] | Health conditions |
| target_energy_kcal | FLOAT | NULLABLE | Energy target |
| target_protein_g | FLOAT | NULLABLE | Protein target |
| target_carbohydrate_g | FLOAT | NULLABLE | Carb target |
| target_fat_g | FLOAT | NULLABLE | Fat target |
| target_fibre_g | FLOAT | NULLABLE | Fibre target |
| target_sodium_mg | FLOAT | NULLABLE | Sodium target |
| weight_goal | VARCHAR(20) | DEFAULT 'MAINTAIN' | MAINTAIN/LOSE/GAIN |
| weight_change_rate_kg_per_week | FLOAT | DEFAULT 0.5 | Weekly weight change |
| activity_level | VARCHAR(30) | DEFAULT 'SEDENTARY' | PAL level |
| meal_frequency | INTEGER | DEFAULT 3 | Meals per day |
| preferred_meal_times | JSON | DEFAULT {} | Meal timing preferences |
| cooking_skill | VARCHAR(20) | DEFAULT 'INTERMEDIATE' | Skill level |
| budget_constraint | VARCHAR(20) | NULLABLE | LOW/MEDIUM/HIGH |
| time_constraint_minutes | INTEGER | NULLABLE | Max prep+cook time |

### 2.3 recipes

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Internal PK |
| recipe_id | INTEGER | UNIQUE, NOT NULL, INDEX | Original recipe_id (1-6865) |
| recipe_name | VARCHAR(255) | NOT NULL | English name |
| cuisine | VARCHAR(100) | INDEX | Cuisine type |
| course | VARCHAR(50) | INDEX | Course type |
| diet_labels | JSON | DEFAULT [] | Diet tags (pipe-separated in source) |
| recipe_type | VARCHAR(20) | | veg/non-veg/eggetarian |
| prep_time_min | INTEGER | DEFAULT 0 | Prep time |
| cook_time_min | INTEGER | DEFAULT 0 | Cook time |
| total_time_min | INTEGER | DEFAULT 0 | Total time |
| servings | INTEGER | DEFAULT 4 | Number of servings |
| ingredients_raw | TEXT | | Original ingredient text |
| ingredients_en | TEXT | | Normalized ingredients |
| instructions_raw | TEXT | | Original instructions |
| instructions_en | TEXT | | English instructions |
| source_url | VARCHAR(500) | | Source URL |
| source_domain | VARCHAR(100) | | Source domain |

**Nutrition Columns (Phase 3.6):**
| Column | Type | Default | Description |
|--------|------|---------|-------------|
| nutrition_status | VARCHAR(30) | 'UNAVAILABLE' | COMPLETE/PARTIAL/UNAVAILABLE/NO_MAPPED_INGREDIENTS |
| total_nutrients | JSON | {} | Total recipe nutrients |
| per_serving_nutrients | JSON | {} | Per-serving nutrients |
| nutrient_completeness | JSON | {} | Per-nutrient completeness |
| mapping_coverage | FLOAT | 0.0 | Ingredient mapping coverage |
| weight_coverage | FLOAT | 0.0 | Gram weight coverage |
| mapped_ingredient_count | INTEGER | 0 | Mapped ingredients |
| total_ingredient_count | INTEGER | 0 | Total ingredients |
| missing_nutrients | JSON | [] | Missing nutrient list |
| nutrition_provenance | JSON | {} | Calculation provenance |

**Dietary Classification:**
| Column | Type | Default | Description |
|--------|------|---------|-------------|
| diet_classification | JSON | {} | Diet type, non-veg ingredients, etc. |

### 2.4 meal_plans

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Primary key |
| user_id | INTEGER | FK(users.id), NOT NULL | Owner |
| start_date | DATE | NOT NULL | Plan start |
| end_date | DATE | NOT NULL | Plan end |
| status | VARCHAR(20) | DEFAULT 'DRAFT' | DRAFT/ACTIVE/COMPLETED/ARCHIVED |
| notes | TEXT | | Plan notes |
| created_at | DATETIME | DEFAULT NOW() | Creation time |
| updated_at | DATETIME | DEFAULT NOW(), ON UPDATE | Last update |

### 2.5 meal_plan_items

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Primary key |
| meal_plan_id | INTEGER | FK(meal_plans.id), NOT NULL | Parent plan |
| recipe_id | INTEGER | FK(recipes.id), NOT NULL | Recipe |
| meal_slot | VARCHAR(20) | NOT NULL | BREAKFAST/LUNCH/DINNER/MORNING_SNACK/EVENING_SNACK |
| day_index | INTEGER | NOT NULL | 0-6 for weekly |
| servings | FLOAT | DEFAULT 1.0 | Number of servings |
| is_completed | BOOLEAN | DEFAULT FALSE | Completion status |
| completed_at | DATETIME | NULLABLE | Completion timestamp |
| notes | TEXT | | Item notes |

### 2.6 saved_recipes

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Primary key |
| user_id | INTEGER | FK(users.id), NOT NULL | Owner |
| recipe_id | INTEGER | FK(recipes.id), NOT NULL | Saved recipe |
| saved_at | DATETIME | DEFAULT NOW() | Save timestamp |
| notes | TEXT | | Personal notes |

### 2.6 sessions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(64) | PK | JWT token / session ID |
| user_id | INTEGER | FK(users.id), NOT NULL | Owner |
| created_at | DATETIME | DEFAULT NOW() | Creation time |
| expires_at | DATETIME | NOT NULL | Expiration |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |

---

## 3. Indexes

| Table | Index | Columns | Purpose |
|-------|-------|---------|---------|
| users | idx_email | email | Login lookup |
| users | idx_active | is_active | Active user queries |
| user_profiles | idx_user_id | user_id | Profile lookup |
| recipes | idx_recipe_id | recipe_id | Recipe lookup |
| recipes | idx_cuisine | cuisine | Cuisine filtering |
| recipes | idx_course | course | Course filtering |
| recipes | idx_diet_labels | diet_labels | Diet filtering (GIN) |
| recipes | idx_nutrition_status | nutrition_status | Nutrition availability |
| meal_plans | idx_user_dates | user_id, start_date | User plan queries |
| meal_plan_items | idx_plan_slot | meal_plan_id, meal_slot | Slot queries |
| meal_plan_items | idx_recipe | recipe_id | Recipe usage |
| saved_recipes | idx_user_recipe | user_id, recipe_id | Duplicate prevention |
| sessions | idx_user_active | user_id, is_active | Session lookup |
| sessions | idx_expires | expires_at | Cleanup queries |

---

## 3. JSON Column Schemas

### 3.1 user_profiles.dietary_preference enum values
```json
["OMNIVORE", "VEGETARIAN", "VEGAN", "EGGETARIAN", "JAIN", "PESCATARIAN", "FLEXITARIAN"]
```

### 3.2 user_profiles.allergies
```json
["peanut", "tree_nut", "milk", "egg", "wheat", "soy", "fish", "shellfish", "sesame", "mustard", "celery"]
```

### 3.3 recipes.diet_labels
```json
["vegetarian", "vegan", "eggetarian", "non-vegetarian", "jain"]
```

### 3.4 recipes.diet_classification
```json
{
  "diet_type": "VEGETARIAN",
  "is_vegetarian": true,
  "is_vegan": false,
  "is_eggetarian": false,
  "is_non_veg": false,
  "non_veg_ingredients": [],
  "dairy_ingredients": ["ghee", "paneer"],
  "egg_ingredients": [],
  "jain_compliant": false,
  "jain_restricted_ingredients": ["onion", "garlic"]
}
```

### 3.5 recipes.nutrition_provenance
```json
{
  "mapping_decisions": [
    {"ingredient": "rice", "ifct_code": "A001", "reviewer": "primary_reviewer", "timestamp": "2026-01-15T10:30:00"}
  ],
  "weight_sources": [
    {"ingredient": "rice", "source": "household_conversion", "confidence": 0.95}
  ],
  "edible_portion_factors": [
    {"ingredient": "spinach", "factor": 0.85, "source": "IFCT"}
  ],
  "calculation_timestamp": "2026-11-19T14:30:00"
}
```

### 3.6 meal_plan_items.meal_slot enum
```json
["BREAKFAST", "MORNING_SNACK", "LUNCH", "EVENING_SNACK", "DINNER"]
```

### 3.7 meal_plans.status enum
```json
["DRAFT", "ACTIVE", "COMPLETED", "ARCHIVED"]
```

---

## 4. Data Access Patterns

### 4.1 Common Queries

| Operation | Tables | Index Used |
|-----------|--------|------------|
| User login | users | idx_email |
| Profile load | user_profiles | idx_user_id |
| Recipe search | recipes | idx_cuisine, idx_course, idx_diet_labels |
| Recipe detail | recipes | idx_recipe_id |
| User meal plans | meal_plans | idx_user_dates |
| Daily meal plan | meal_plan_items | idx_plan_slot |
| Recipe nutrition | recipes | idx_recipe_id, idx_nutrition_status |
| User saved recipes | saved_recipes | idx_user_recipe |
| Session validation | sessions | idx_user_active, idx_expires |

### 4.2 Recipe Search Query (Typical)
```sql
SELECT r.* FROM recipes r
WHERE 
  (:cuisine IS NULL OR r.cuisine = :cuisine)
  AND (:course IS NULL OR r.course = :course)
  AND (:diet_labels IS NULL OR r.diet_labels @> :diet_labels)
  AND (:max_time IS NULL OR r.total_time_min <= :max_time)
ORDER BY r.recipe_name
LIMIT :limit OFFSET :offset
```

### 4.3 Meal Plan with Items (Eager Load)
```sql
SELECT mp.*, mpi.*, r.* 
FROM meal_plans mp
JOIN meal_plan_items mpi ON mp.id = mpi.meal_plan_id
JOIN recipes r ON mpi.recipe_id = r.id
WHERE mp.user_id = :user_id AND mp.start_date = :date
ORDER BY mpi.day_index, 
  CASE mpi.meal_slot 
    WHEN 'BREAKFAST' THEN 1
    WHEN 'MORNING_SNACK' THEN 2
    WHEN 'LUNCH' THEN 3
    WHEN 'EVENING_SNACK' THEN 4
    WHEN 'DINNER' THEN 5
  END
```

---

## 5. Migration Strategy

### 5.1 Initial Migration (Alembic)

```python
# migrations/versions/001_initial.py
"""Initial migration"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

def upgrade():
    # users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('role', sa.Enum('USER', name='userrole'), default='USER'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('last_login', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_email', 'users', ['email'], unique=True)
    op.create_index('idx_active', 'users', ['is_active'])
    
    # ... other tables
    
def downgrade():
    op.drop_table('users')
    # ... drop other tables
```

### 5.2 Recipe Data Import (One-time)

```python
# scripts/import_recipes.py
import pandas as pd
from sqlalchemy.orm import Session
from app.database.models import Recipe, Base
from app.database.session import engine

def import_recipes():
    df = pd.read_parquet("data/processed/recipes.parquet")
    
    with Session(engine) as session:
        for _, row in df.iterrows():
            # Parse diet_labels
            diet_labels = []
            if row.get('diet_labels'):
                diet_labels = [d.strip() for d in row['diet_labels'].split('|') if d.strip()]
            
            recipe = Recipe(
                recipe_id=int(row['recipe_id']),
                recipe_name=row['recipe_name_en'],
                cuisine=row['cuisine'],
                course=row['course'],
                diet_labels=diet_labels,
                recipe_type=row['recipe_type'],
                prep_time_min=int(row['prep_time_min']) if pd.notna(row['prep_time_min']) else 0,
                cook_time_min=int(row['cook_time_min']) if pd.notna(row['cook_time_min']) else 0,
                total_time_min=int(row['total_time_min']) if pd.notna(row['total_time_min']) else 0,
                servings=int(row['servings']) if pd.notna(row['servings']) else 4,
                ingredients_raw=row['ingredients_raw'],
                ingredients_en=row['ingredients_en'],
                instructions_raw=row['instructions_raw'],
                instructions_en=row['instructions_en'],
                source_url=row['source_url'],
                source_domain=row['source_domain'],
                nutrition_status='UNAVAILABLE',  # No approved mappings yet
            )
            session.add(recipe)
        session.commit()
```

---

## 6. Backup & Recovery

### 6.1 Backup Strategy
| Data | Frequency | Method |
|------|-----------|--------|
| SQLite DB | Daily | File copy + compression |
| Parquet datasets | Never (frozen) | N/A |
| Uploaded files | On change | Incremental |

### 6.2 Recovery Procedure
1. Stop application
2. Restore `data/app.db` from latest backup
3. Verify schema with `alembic current`
4. Restart application

---

*End of Database Design Report*