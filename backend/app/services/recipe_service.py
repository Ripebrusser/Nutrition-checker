"""Recipe service for data access and search."""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import pandas as pd
from pathlib import Path

from app.db.models import Recipe


class RecipeService:
    """Service for recipe data operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_cuisines(self) -> List[str]:
        """Get all unique cuisines."""
        cuisines = self.db.query(Recipe.cuisine).distinct().filter(Recipe.cuisine.isnot(None)).all()
        return sorted([c[0] for c in cuisines if c[0]])

    def get_courses(self) -> List[str]:
        """Get all unique courses."""
        courses = self.db.query(Recipe.course).distinct().filter(Recipe.course.isnot(None)).all()
        return sorted([c[0] for c in courses if c[0]])

    def get_recipe_types(self) -> List[str]:
        """Get all unique recipe types."""
        types = self.db.query(Recipe.recipe_type).distinct().filter(Recipe.recipe_type.isnot(None)).all()
        return sorted([t[0] for t in types if t[0]])

    def search_recipes(
        self,
        query: Optional[str] = None,
        cuisine: Optional[str] = None,
        course: Optional[str] = None,
        diet_labels: Optional[List[str]] = None,
        recipe_type: Optional[str] = None,
        max_prep_time: Optional[int] = None,
        max_cook_time: Optional[int] = None,
        max_total_time: Optional[int] = None,
        page: int = 1,
        per_page: int = 12,
    ):
        """Search recipes with filters."""
        q = self.db.query(Recipe)

        if query:
            search_term = f"%{query.lower()}%"
            q = q.filter(
                Recipe.recipe_name.ilike(search_term) |
                Recipe.ingredients.ilike(search_term) |
                Recipe.cuisine.ilike(search_term)
            )

        if cuisine:
            q = q.filter(Recipe.cuisine == cuisine)
        if course:
            q = q.filter(Recipe.course == course)
        if recipe_type:
            q = q.filter(Recipe.recipe_type == recipe_type)
        if max_prep_time is not None:
            q = q.filter(Recipe.prep_time_min <= max_prep_time)
        if max_cook_time is not None:
            q = q.filter(Recipe.cook_time_min <= max_cook_time)
        if max_total_time is not None:
            q = q.filter(Recipe.total_time_min <= max_total_time)

        if diet_labels:
            for label in diet_labels:
                q = q.filter(Recipe.diet_labels.like(f"%{label}%"))

        total = q.count()
        offset = (page - 1) * per_page
        recipes = q.order_by(Recipe.recipe_name).offset(offset).limit(per_page).all()

        return {
            "recipes": recipes,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page if total > 0 else 0,
        }