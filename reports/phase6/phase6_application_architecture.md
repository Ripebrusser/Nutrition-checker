# Phase 6: Application Architecture Report

**Date:** 2026-11-19  
**Status:** Architecture Defined — Ready for Implementation

---

## 1. Architecture Overview

### 1.1 Design Principles

| Principle | Application |
|-----------|-------------|
| **Separation of Concerns** | Clear boundaries between UI, API, business logic, ML services |
| **Reuse Over Rebuild** | Integrate Phase 3–5 modules; no reimplementation |
| **Defensive Programming** | Never fabricate nutrition data; always show completeness |
| **Security First** | Password hashing, session management, input validation |
| **Modularity** | Each feature in its own module with clear interfaces |

### 1.2 Technology Stack

| Layer | Technology | Justification |
|-------|------------|---------------|
| **Frontend** | Streamlit | Consistent with existing review app; rapid development |
| **Backend** | Python 3.11+ | Existing codebase is Python; rich ML ecosystem |
| **Data Storage** | SQLite + Parquet | SQLite for user data; Parquet for frozen datasets |
| **Authentication** | bcrypt + JWT | Secure password hashing; stateless sessions |
| **Caching** | Streamlit `@st.cache_data` | Built-in; leverages existing patterns |
| **Configuration** | YAML + Environment Variables | Flexible; secrets in env vars |

### 1.3 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit Frontend                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │  Pages   │ │Components│ │  Forms   │ │  Charts  │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │   Auth   │ │  Profile │ │ Recipe   │ │  Meal    │        │
│  │ Service  │ │ Service  │ │ Service  │ │ Planner  │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                      │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐  │
│  │ Personal-  │ │  Dietary   │ │ Nutrition  │ │  Meal    │  │
│  │  ized Rec  │ │ Constraints│ │ Targets    │ │ Planner  │  │
│  └────────────┘ └────────────┘ └────────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Core Services Layer                     │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐  │
│  │ Nutrition  │ │  Content-  │ │  Dietary   │ │  Profile │  │
│  │ Calculator │ │ Based Rec  │ │  Engine    │ │ Manager  │  │
│  └────────────┘ └────────────┘ └────────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ SQLite   │ │ Parquet  │ │   CSV    │ │  JSON    │        │
│  │ (Users)  │ │ (Frozen) │ │ (Refs)   │ │ (Config) │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Directory Structure

```
app/
├── __init__.py
├── main.py                      # Entry point
├── config.py                    # Configuration management
├── auth/
│   ├── __init__.py
│   ├── models.py                # User, Session models
│   ├── password.py              # bcrypt hashing
│   ├── session.py               # JWT/session management
│   └── dependencies.py          # FastAPI/Streamlit dependencies
├── auth_streamlit.py            # Streamlit auth wrapper
├── components/
│   ├── __init__.py
│   ├── forms.py                 # Reusable form components
│   ├── cards.py                 # Recipe/profile cards
│   ├── charts.py                # Nutrition charts
│   ├── tables.py                # Data tables
│   └── alerts.py                # Alerts/notifications
├── pages/
│   ├── __init__.py
│   ├── home.py                  # Landing page
│   ├── login.py                 # Login page
│   ├── register.py              # Registration page
│   ├── dashboard.py             # User dashboard
│   ├── profile.py               # Profile management
│   ├── nutrition_targets.py     # Nutritional targets
│   ├── recipes.py               # Recipe discovery
│   ├── recipe_detail.py         # Recipe detail page
│   ├── recommendations.py       # Personalized recommendations
│   ├── meal_planner.py          # Meal planner
│   ├── meal_plan_detail.py      # Meal plan detail
│   ├── nutrition_breakdown.py   # Nutrition breakdown
│   ├── preferences.py           # User preferences
│   └── history.py               # History/completed meals
├── services/
│   ├── __init__.py
│   ├── user_service.py          # User/profile management
│   ├── recipe_service.py        # Recipe search/filter
│   ├── nutrition_service.py     # Nutrition calculations
│   ├── recommendation_service.py # Personalized recommendations
│   ├── meal_plan_service.py     # Meal plan generation
│   ├── explanation_service.py   # Explanation generation
│   └── validation_service.py    # Input validation
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # /api/auth/*
│   │   ├── profile.py           # /api/profile/*
│   │   ├── recipes.py           # /api/recipes/*
│   │   ├── recommendations.py   # /api/recommendations/*
│   │   ├── meal_plans.py        # /api/meal-plans/*
│   │   └── nutrition.py         # /api/nutrition/*
│   └── dependencies.py          # FastAPI dependencies
├── database/
│   ├── __init__.py
│   ├── models.py                # SQLAlchemy models
│   ├── session.py               # Session management
│   ├── init_db.py               # Database initialization
│   └── migrations/              # Alembic migrations
├── models/                      # Shared Pydantic models
│   ├── __init__.py
│   ├── user.py
│   ├── recipe.py
│   ├── nutrition.py
│   ├── meal_plan.py
│   └── common.py
├── utils/
│   ├── __init__.py
│   ├── security.py              # Hashing, tokens
│   ├── formatting.py            # Display formatting
│   └── validation.py            # Input validation
└── static/
    ├── css/
    │   └── custom.css
    └── js/
        └── custom.js
```

---

## 3. Data Models

### 3.1 Database Models (SQLAlchemy)

```python
# database/models.py

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum, JSON, Float, Date
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    USER = "USER"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    meal_plans = relationship("MealPlan", back_populates="user")
    saved_recipes = relationship("SavedRecipe", back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Anthropometrics
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    age_years = Column(Integer, nullable=True)
    sex = Column(String(10), nullable=True)  # MALE, FEMALE
    
    # Dietary Profile
    dietary_preference = Column(String(50), default="OMNIVORE")
    allergies = Column(JSON, default=list)
    ingredient_exclusions = Column(JSON, default=list)
    cuisine_preferences = Column(JSON, default=list)
    cuisine_exclusions = Column(JSON, default=list)
    disliked_ingredients = Column(JSON, default=list)
    religious_restrictions = Column(JSON, default=list)
    medical_conditions = Column(JSON, default=list)
    
    # Nutritional Goals
    target_energy_kcal = Column(Float, nullable=True)
    target_protein_g = Column(Float, nullable=True)
    target_carbohydrate_g = Column(Float, nullable=True)
    target_fat_g = Column(Float, nullable=True)
    target_fibre_g = Column(Float, nullable=True)
    target_sodium_mg = Column(Float, nullable=True)
    weight_goal = Column(String(20), default="MAINTAIN")
    weight_change_rate_kg_per_week = Column(Float, default=0.5)
    
    # Lifestyle
    activity_level = Column(String(30), default="SEDENTARY")
    meal_frequency = Column(Integer, default=3)
    preferred_meal_times = Column(JSON, default=dict)
    cooking_skill = Column(String(20), default="INTERMEDIATE")
    budget_constraint = Column(String(20), nullable=True)
    time_constraint_minutes = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="profile")

class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, unique=True, nullable=False, index=True)  # Original recipe_id
    recipe_name = Column(String(255), nullable=False)
    cuisine = Column(String(100), index=True)
    course = Column(String(50), index=True)
    diet_labels = Column(JSON, default=list)
    recipe_type = Column(String(20))
    prep_time_min = Column(Integer, default=0)
    cook_time_min = Column(Integer, default=0)
    total_time_min = Column(Integer, default=0)
    servings = Column(Integer, default=4)
    ingredients_raw = Column(Text)
    instructions_raw = Column(Text)
    instructions_en = Column(Text)
    source_url = Column(String(500))
    source_domain = Column(String(100))
    
    # Phase 3 nutrition data
    nutrition_status = Column(String(30), default="UNAVAILABLE")  # COMPLETE, PARTIAL, UNAVAILABLE, NO_MAPPED_INGREDIENTS
    total_nutrients = Column(JSON, default=dict)
    per_serving_nutrients = Column(JSON, default=dict)
    nutrient_completeness = Column(JSON, default=dict)
    mapping_coverage = Column(Float, default=0.0)
    weight_coverage = Column(Float, default=0.0)
    mapped_ingredient_count = Column(Integer, default=0)
    total_ingredient_count = Column(Integer, default=0)
    missing_nutrients = Column(JSON, default=list)
    nutrition_provenance = Column(JSON, default=dict)
    
    # Dietary classification
    diet_classification = Column(JSON, default=dict)
    
    saved_by = relationship("SavedRecipe", back_populates="recipe")
    meal_plan_items = relationship("MealPlanItem", back_populates="recipe")

class MealPlan(Base):
    __tablename__ = "meal_plans"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(20), default="DRAFT")  # DRAFT, ACTIVE, COMPLETED, ARCHIVED
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="meal_plans")
    items = relationship("MealPlanItem", back_populates="meal_plan", cascade="all, delete-orphan")

class MealPlanItem(Base):
    __tablename__ = "meal_plan_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    meal_plan_id = Column(Integer, ForeignKey("meal_plans.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    meal_slot = Column(String(20), nullable=False)  # BREAKFAST, LUNCH, DINNER, MORNING_SNACK, EVENING_SNACK
    day_index = Column(Integer, nullable=False)  # 0-6 for weekly
    servings = Column(Float, default=1.0)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    notes = Column(Text)
    
    meal_plan = relationship("MealPlan", back_populates="items")
    recipe = relationship("Recipe", back_populates="meal_plan_items")

class SavedRecipe(Base):
    __tablename__ = "saved_recipes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    saved_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    user = relationship("User", back_populates="saved_recipes")
    recipe = relationship("Recipe", back_populates="saved_by")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String(64), primary_key=True)  # JWT token or session ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User")
```

---

## 4. API Design

### 4.1 REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | User registration |
| `/api/auth/login` | POST | User login |
| `/api/auth/logout` | POST | User logout |
| `/api/auth/me` | GET | Current user info |
| `/api/profile` | GET | Get user profile |
| `/api/profile` | PUT | Update profile |
| `/api/profile/nutrition-targets` | GET | Calculated nutrition targets |
| `/api/recipes/search` | GET | Search recipes |
| `/api/recipes/{id}` | GET | Recipe detail |
| `/api/recipes/{id}/nutrition` | GET | Recipe nutrition breakdown |
| `/api/recipes/{id}/dietary` | GET | Dietary classification |
| `/api/recommendations` | GET | Personalized recommendations |
| `/api/recommendations/meal-slot/{slot}` | GET | Meal-slot specific recommendations |
| `/api/meal-plans` | GET/POST | List/create meal plans |
| `/api/meal-plans/{id}` | GET/PUT/DELETE | Meal plan CRUD |
| `/api/meal-plans/{id}/items` | GET/POST | Meal plan items |
| `/api/meal-plans/{id}/items/{item_id}` | PUT/DELETE | Update/delete item |
| `/api/meal-plans/{id}/complete` | POST | Mark meal completed |
| `/api/meal-plans/{id}/nutrition` | GET | Meal plan nutrition summary |
| `/api/saved-recipes` | GET/POST | Saved recipes |
| `/api/saved-recipes/{id}` | DELETE | Remove saved recipe |
| `/api/preferences` | GET/PUT | User preferences |
| `/api/history/meals` | GET | Meal completion history |

---

## 5. Streamlit Page Structure

### 5.1 Page Definitions

```python
# app/pages/__init__.py

PAGES = {
    "home": {"title": "Home", "icon": "🏠", "order": 0},
    "login": {"title": "Login", "icon": "🔐", "order": 1},
    "register": {"title": "Register", "icon": "📝", "order": 2},
    "dashboard": {"title": "Dashboard", "icon": "📊", "order": 10, "auth_required": True},
    "profile": {"title": "Profile", "icon": "👤", "order": 20, "auth_required": True},
    "nutrition_targets": {"title": "Nutrition Targets", "icon": "🎯", "order": 30, "auth_required": True},
    "recipes": {"title": "Recipes", "icon": "🍲", "order": 40, "auth_required": True},
    "recipe_detail": {"title": "Recipe Detail", "icon": "📋", "order": 41, "auth_required": True},
    "recommendations": {"title": "Recommendations", "icon": "✨", "order": 50, "auth_required": True},
    "meal_planner": {"title": "Meal Planner", "icon": "📅", "order": 60, "auth_required": True},
    "meal_plan_detail": {"title": "Meal Plan", "icon": "📋", "order": 61, "auth_required": True},
    "nutrition_breakdown": {"title": "Nutrition Breakdown", "icon": "🔬", "order": 70, "auth_required": True},
    "preferences": {"title": "Preferences", "icon": "⚙️", "order": 80, "auth_required": True},
    "history": {"title": "History", "icon": "📜", "order": 90, "auth_required": True},
}
```

---

## 6. Authentication Flow

```python
# auth/session.py

import jwt
from datetime import datetime, timedelta
from typing import Optional
from app.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
```

---

## 6. Configuration Management

```python
# config.py

from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Indian Nutrition & Diet Planner"
    DEBUG: bool = False
    SECRET_KEY: str = "dev-secret-change-in-production"
    
    # Database
    DATABASE_URL: str = "sqlite:///data/app.db"
    
    # JWT
    SECRET_KEY: str = "dev-secret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Data paths
    RECIPES_PATH: str = "data/processed/recipes.parquet"
    PARSED_INGREDIENTS_PATH: str = "data/interim/phase2/parsed_recipe_ingredients.parquet"
    IFCT_PATH: str = "data/interim/ifct_final_candidate/ifct_table1_candidate.parquet"
    
    # Streamlit
    STREAMLIT_PORT: int = 8501
    STREAMLIT_ADDRESS: str = "0.0.0.0"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

---

## 7. Component Architecture

### 7.1 Reusable UI Components

```python
# app/components/forms.py

import streamlit as st
from typing import List, Optional, Any, Dict
from datetime import date

def profile_form(profile_data: dict, readonly: bool = False) -> dict:
    """Render profile form and return updated data."""
    col1, col2 = st.columns(2)
    
    with col1:
        height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, 
                                 value=profile_data.get("height_cm") or 0.0,
                                 disabled=readonly, step=0.1)
        weight = st.number_input("Weight (kg)", min_value=2.0, max_value=300.0,
                                 value=profile_data.get("weight_kg") or 0.0,
                                 disabled=readonly, step=0.1)
        age = st.number_input("Age (years)", min_value=1, max_value=120,
                              value=profile_data.get("age_years") or 0,
                              disabled=readonly)
        sex = st.selectbox("Sex", ["MALE", "FEMALE"],
                           index=["MALE", "FEMALE"].index(profile_data.get("sex", "MALE")),
                           disabled=readonly)
    
    with col2:
        activity = st.selectbox("Activity Level",
            ["SEDENTARY", "LIGHTLY_ACTIVE", "MODERATELY_ACTIVE", "VERY_ACTIVE", "EXTREMELY_ACTIVE"],
            index=["SEDENTARY", "LIGHTLY_ACTIVE", "MODERATELY_ACTIVE", "VERY_ACTIVE", "EXTREMELY_ACTIVE"]
                .index(profile_data.get("activity_level", "SEDENTARY")),
            disabled=readonly)
        meal_freq = st.selectbox("Meals per Day", [3, 4, 5, 6],
                                 index=[3, 4, 5, 6].index(profile_data.get("meal_frequency", 3)),
                                 disabled=readonly)
        cooking_skill = st.selectbox("Cooking Skill",
            ["BEGINNER", "INTERMEDIATE", "ADVANCED"],
            index=["BEGINNER", "INTERMEDIATE", "ADVANCED"].index(profile_data.get("cooking_skill", "INTERMEDIATE")),
            disabled=readonly)
        time_constraint = st.number_input("Max Prep+Cook Time (min)", min_value=5, max_value=180,
                                          value=profile_data.get("time_constraint_minutes") or 30,
                                          disabled=readonly)
    
    return {
        "height_cm": height if height > 0 else None,
        "weight_kg": weight if weight > 0 else None,
        "age_years": age if age > 0 else None,
        "sex": sex,
        "activity_level": activity,
        "meal_frequency": meal_freq,
        "cooking_skill": cooking_skill,
        "time_constraint_minutes": time_constraint if time_constraint > 0 else None,
    }

def dietary_preferences_form(profile_data: dict, readonly: bool = False) -> dict:
    """Render dietary preferences form."""
    preference = st.selectbox("Dietary Preference",
        ["OMNIVORE", "VEGETARIAN", "VEGAN", "EGGETARIAN", "JAIN", "PESCATARIAN", "FLEXITARIAN"],
        index=["OMNIVORE", "VEGETARIAN", "VEGAN", "EGGETARIAN", "JAIN", "PESCATARIAN", "FLEXITARIAN"]
            .index(profile_data.get("dietary_preference", "OMNIVORE")),
        disabled=readonly)
    
    allergies = st_tags_input("Allergies", 
                              value=profile_data.get("allergies", []),
                              suggestions=["peanut", "tree_nut", "milk", "egg", "wheat", "soy", "fish", "shellfish"],
                              disabled=readonly)
    
    exclusions = st_tags_input("Ingredient Exclusions",
                               value=profile_data.get("ingredient_exclusions", []),
                               disabled=readonly)
    
    cuisine_prefs = st_tags_input("Preferred Cuisines",
                                  value=profile_data.get("cuisine_preferences", []),
                                  suggestions=["north indian", "south indian", "gujarati", "maharashtrian", "punjabi", "bengali"],
                                  disabled=readonly)
    
    return {
        "dietary_preference": preference,
        "allergies": allergies,
        "ingredient_exclusions": exclusions,
        "cuisine_preferences": cuisine_prefs,
    }

def recipe_card(recipe: dict, show_nutrition: bool = True, on_click=None) -> None:
    """Render a recipe card."""
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            if recipe.get("image_url"):
                st.image(recipe["image_url"], width=150)
            else:
                st.markdown("🍲")
        with col2:
            st.subheader(recipe.get("recipe_name", "Unknown"))
            st.caption(f"🍽️ {recipe.get('cuisine', 'Unknown')} • 🍽️ {recipe.get('course', 'Unknown')}")
            
            if show_nutrition and "per_serving_nutrients" in recipe:
                nuts = recipe["per_serving_nutrients"]
                cols = st.columns(4)
                if "energy_kcal" in nuts:
                    cols[0].metric("Calories", f"{nuts['energy_kcal']:.0f} kcal")
                if "protein_g" in nuts:
                    cols[1].metric("Protein", f"{nuts['protein_g']:.1f} g")
                if "carbohydrate_g" in nuts:
                    cols[2].metric("Carbs", f"{nuts['carbohydrate_g']:.1f} g")
                if "fat_g" in nuts:
                    cols[3].metric("Fat", f"{nuts['fat_g']:.1f} g")
            
            if on_click and st.button("View Details", key=f"view_{recipe.get('id')}"):
                on_click(recipe)
```

---

## 8. Service Layer Integration

### 8.1 Service Initialization

```python
# app/services/__init__.py

from app.services.user_service import UserService
from app.services.recipe_service import RecipeService
from app.services.nutrition_service import NutritionService
from app.services.recommendation_service import RecommendationService
from app.services.meal_plan_service import MealPlanService
from app.services.explanation_service import ExplanationService
from app.services.validation_service import ValidationService

def get_services(db_session) -> dict:
    """Initialize all services with database session."""
    return {
        "user_service": UserService(db_session),
        "recipe_service": RecipeService(db_session),
        "nutrition_service": NutritionService(),
        "recommendation_service": RecommendationService(),
        "meal_plan_service": MealPlanService(),
        "explanation_service": ExplanationService(),
        "validation_service": ValidationService(),
    }
```

---

## 9. Configuration Files

### 9.1 requirements.txt

```txt
# Core
streamlit>=1.28.0
fastapi>=0.104.0
uvicorn>=0.24.0
sqlalchemy>=2.0.0
alembic>=1.12.0
pydantic>=2.5.0
pydantic-settings>=2.1.0

# Data
pandas>=2.1.0
numpy>=1.24.0
scikit-learn>=1.3.0

# Auth
bcrypt>=4.0.0
python-jose>=3.3.0
python-multipart>=0.0.6

# Database
sqlite3  # built-in

# Utils
python-dotenv>=1.0.0
pyyaml>=6.0.1
python-dateutil>=2.8.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.25.0
```

---

## 10. Deployment Configuration

### 9.1 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 9.2 docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./reports:/app/reports
    environment:
      - DATABASE_URL=sqlite:///data/app.db
      - SECRET_KEY=${SECRET_KEY}
    restart: unless-stopped
```

---

## 10. Migration Strategy

Since the project has existing frozen Parquet datasets, the application will:
1. **Read-only** access to frozen Parquet/CSV files in `data/`
2. **Read-write** SQLite database for user data (`data/app.db`)
3. **No modifications** to frozen datasets
4. **Migrations** via Alembic for user database schema

---

*End of Application Architecture Report*