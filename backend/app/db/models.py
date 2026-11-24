"""Database models using SQLAlchemy 2.0 for FastAPI backend."""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum,
    JSON, Float, Date, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


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
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    meal_plans = relationship("MealPlan", back_populates="user", cascade="all, delete-orphan")
    saved_recipes = relationship("SavedRecipe", back_populates="user", cascade="all, delete-orphan")
    meal_history = relationship("MealHistory", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    height_cm = Column(Float)
    weight_kg = Column(Float)
    age_years = Column(Integer)
    sex = Column(String(10))  # MALE, FEMALE
    dietary_preference = Column(String(50), default="NON_VEGETARIAN")
    allergies = Column(JSON, default=list)
    ingredient_exclusions = Column(JSON, default=list)
    cuisine_preferences = Column(JSON, default=list)
    cuisine_exclusions = Column(JSON, default=list)
    disliked_ingredients = Column(JSON, default=list)
    religious_restrictions = Column(JSON, default=list)
    medical_conditions = Column(JSON, default=list)
    target_energy_kcal = Column(Float)
    target_protein_g = Column(Float)
    target_carbohydrate_g = Column(Float)
    target_fat_g = Column(Float)
    target_fibre_g = Column(Float)
    target_sodium_mg = Column(Float)
    weight_goal = Column(String(20), default="MAINTAIN")  # MAINTAIN, LOSE, GAIN
    weight_change_rate_kg_per_week = Column(Float, default=0.5)
    activity_level = Column(String(30), default="SEDENTARY")
    meal_frequency = Column(Integer, default=3)
    preferred_meal_times = Column(JSON, default=dict)
    cooking_skill = Column(String(20), default="INTERMEDIATE")
    budget_constraint = Column(String(20))
    time_constraint_minutes = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="profile")


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, unique=True, nullable=False, index=True)
    recipe_name = Column(String(500), nullable=False)
    cuisine = Column(String(100))
    course = Column(String(100))
    diet_labels = Column(Text)  # Pipe-separated
    recipe_type = Column(String(20))  # veg, non-veg, eggetarian
    prep_time_min = Column(Integer, default=0)
    cook_time_min = Column(Integer, default=0)
    total_time_min = Column(Integer, default=0)
    servings = Column(Integer, default=1)
    ingredients = Column(Text)  # Newline-separated
    instructions = Column(Text)
    image_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    meal_plan_items = relationship("MealPlanItem", back_populates="recipe")
    saved_recipes = relationship("SavedRecipe", back_populates="recipe")
    meal_history = relationship("MealHistory", back_populates="recipe")


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(SQLEnum(MealPlanStatus), default=MealPlanStatus.DRAFT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="meal_plans")
    items = relationship("MealPlanItem", back_populates="meal_plan", cascade="all, delete-orphan", order_by="MealPlanItem.day_index, MealPlanItem.meal_slot")


class MealPlanItem(Base):
    __tablename__ = "meal_plan_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    meal_plan_id = Column(Integer, ForeignKey("meal_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    meal_slot = Column(SQLEnum(MealSlot), nullable=False)
    day_index = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="SET NULL"), nullable=True)
    servings = Column(Float, default=1.0)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    meal_plan = relationship("MealPlan", back_populates="items")
    recipe = relationship("Recipe", back_populates="meal_plan_items")

    # Constraints
    __table_args__ = (
        UniqueConstraint("meal_plan_id", "meal_slot", "day_index", name="unique_meal_per_slot_per_day"),
        Index("idx_meal_plan_day_slot", "meal_plan_id", "day_index", "meal_slot"),
    )


class SavedRecipe(Base):
    __tablename__ = "saved_recipes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    saved_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="saved_recipes")
    recipe = relationship("Recipe", back_populates="saved_recipes")

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "recipe_id", name="unique_user_recipe"),
    )


class MealHistory(Base):
    __tablename__ = "meal_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    meal_plan_id = Column(Integer, ForeignKey("meal_plans.id", ondelete="SET NULL"), nullable=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="SET NULL"), nullable=True)
    meal_slot = Column(SQLEnum(MealSlot), nullable=False)
    consumed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    servings = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="meal_history")
    recipe = relationship("Recipe", back_populates="meal_history")