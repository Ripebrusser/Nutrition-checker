"""Database models using SQLAlchemy 2.0."""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum,
    JSON, Float, Date, Index, UniqueConstraint, Text
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    USER = "USER"


class MealPlanStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class MealSlot(str, enum.Enum):
    BREAKFAST = "BREAKFAST"
    MORNING_SNACK = "MORNING_SNACK"
    LUNCH = "LUNCH"
    EVENING_SNACK = "EVENING_SNACK"
    DINNER = "DINNER"


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
    sessions = relationship("Session", back_populates="user")


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
    recipe_id = Column(Integer, unique=True, nullable=False, index=True)  # Original recipe_id (1-6865)
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
    ingredients_en = Column(Text)
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
    
    id = Column(String(64), primary_key=True)  # JWT token / session ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User")


# Indexes
Index("idx_user_email", User.email, unique=True)
Index("idx_user_active", User.is_active)
Index("idx_profile_user_id", UserProfile.user_id, unique=True)
Index("idx_recipe_recipe_id", Recipe.recipe_id, unique=True)
Index("idx_recipe_cuisine", Recipe.cuisine)
Index("idx_recipe_course", Recipe.course)
Index("idx_recipe_nutrition_status", Recipe.nutrition_status)
Index("idx_meal_plan_user_dates", MealPlan.user_id, MealPlan.start_date)
Index("idx_meal_plan_item_plan_slot", MealPlanItem.meal_plan_id, MealPlanItem.meal_slot)
Index("idx_meal_plan_item_recipe", MealPlanItem.recipe_id)
Index("idx_saved_recipe_user_recipe", SavedRecipe.user_id, SavedRecipe.recipe_id, unique=True)
Index("idx_session_user_active", Session.user_id, Session.is_active)
Index("idx_session_expires", Session.expires_at)