"""Recipe discovery and search API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from math import ceil

from app.db.session import get_db
from app.db.models import Recipe
from app.auth.dependencies import get_current_user, get_optional_user

router = APIRouter()


class RecipeResponse(BaseModel):
    id: int
    recipe_id: int
    recipe_name: str
    cuisine: str
    course: str
    diet_labels: str
    recipe_type: str
    prep_time_min: int
    cook_time_min: int
    total_time_min: int
    servings: int
    ingredients: str
    instructions: str
    image_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    recipes: List[RecipeResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


@router.get("", response_model=SearchResponse)
async def search_recipes(
    query: Optional[str] = Query(None, description="Search query for recipe name or ingredients"),
    cuisine: Optional[str] = Query(None, description="Filter by cuisine"),
    course: Optional[str] = Query(None, description="Filter by course"),
    diet_labels: Optional[List[str]] = Query(None, description="Filter by diet labels"),
    recipe_type: Optional[str] = Query(None, description="Filter by recipe type (veg, non-veg, eggetarian)"),
    max_prep_time: Optional[int] = Query(None, description="Maximum prep time in minutes"),
    max_cook_time: Optional[int] = Query(None, description="Maximum cook time in minutes"),
    max_total_time: Optional[int] = Query(None, description="Maximum total time in minutes"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(12, ge=1, le=50, description="Items per page"),
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user),
):
    """Search recipes with filters and pagination."""
    q = db.query(Recipe)

    # Text search
    if query:
        search_term = f"%{query.lower()}%"
        q = q.filter(
            or_(
                func.lower(Recipe.recipe_name).like(search_term),
                func.lower(Recipe.ingredients).like(search_term),
                func.lower(Recipe.cuisine).like(search_term),
            )
        )

    # Filters
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

    # Diet labels filter (pipe-separated in DB)
    if diet_labels:
        for label in diet_labels:
            q = q.filter(Recipe.diet_labels.like(f"%{label}%"))

    # Get total count
    total = q.count()

    # Apply pagination
    offset = (page - 1) * per_page
    recipes = q.order_by(Recipe.recipe_name).offset(offset).limit(per_page).all()

    return SearchResponse(
        recipes=recipes,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=ceil(total / per_page) if total > 0 else 0,
    )


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user),
):
    """Get recipe by ID."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )
    return recipe


@router.get("/meta/cuisines")
async def get_cuisines(db: Session = Depends(get_db)):
    """Get all unique cuisines."""
    cuisines = db.query(Recipe.cuisine).distinct().filter(Recipe.cuisine.isnot(None)).all()
    return sorted([c[0] for c in cuisines if c[0]])


@router.get("/meta/courses")
async def get_courses(db: Session = Depends(get_db)):
    """Get all unique courses."""
    courses = db.query(Recipe.course).distinct().filter(Recipe.course.isnot(None)).all()
    return sorted([c[0] for c in courses if c[0]])


@router.get("/meta/diet-labels")
async def get_diet_labels(db: Session = Depends(get_db)):
    """Get all unique diet labels."""
    # This is a bit tricky since diet_labels are pipe-separated
    # We'll return common known labels
    return [
        "vegetarian", "vegan", "eggetarian", "gluten-free", "dairy-free", "nut-free",
        "low-carb", "high-protein", "low-fat", "diabetic-friendly", "heart-healthy",
        "jain", "keto", "paleo", "mediterranean"
    ]


@router.get("/meta/recipe-types")
async def get_recipe_types(db: Session = Depends(get_db)):
    """Get all unique recipe types."""
    types = db.query(Recipe.recipe_type).distinct().filter(Recipe.recipe_type.isnot(None)).all()
    return sorted([t[0] for t in types if t[0]])