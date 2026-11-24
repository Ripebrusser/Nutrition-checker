"""Saved recipes API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.db.session import get_db
from app.db.models import User, SavedRecipe, Recipe
from app.auth.dependencies import get_current_user

router = APIRouter()


class SavedRecipeCreate(BaseModel):
    recipe_id: int


class SavedRecipeResponse(BaseModel):
    id: int
    user_id: int
    recipe_id: int
    saved_at: datetime
    recipe: Optional[dict] = None

    class Config:
        from_attributes = True


@router.get("", response_model=List[SavedRecipeResponse])
async def get_saved_recipes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all saved recipes for current user."""
    saved = db.query(SavedRecipe).filter(
        SavedRecipe.user_id == current_user.id
    ).order_by(SavedRecipe.saved_at.desc()).all()

    result = []
    for s in saved:
        recipe = db.query(Recipe).filter(Recipe.id == s.recipe_id).first()
        result.append(SavedRecipeResponse(
            id=s.id,
            user_id=s.user_id,
            recipe_id=s.recipe_id,
            saved_at=s.saved_at,
            recipe={
                "id": recipe.id,
                "recipe_id": recipe.recipe_id,
                "recipe_name": recipe.recipe_name,
                "cuisine": recipe.cuisine,
                "course": recipe.course,
                "recipe_type": recipe.recipe_type,
                "total_time_min": recipe.total_time_min,
                "servings": recipe.servings,
                "image_url": recipe.image_url,
                "diet_labels": recipe.diet_labels,
            } if recipe else None
        ))
    return result


@router.post("", response_model=SavedRecipeResponse, status_code=status.HTTP_201_CREATED)
async def save_recipe(
    payload: SavedRecipeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save a recipe. The client posts {"recipe_id": <id>}."""
    recipe_id = payload.recipe_id
    # Check recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # Check if already saved
    existing = db.query(SavedRecipe).filter(
        SavedRecipe.user_id == current_user.id,
        SavedRecipe.recipe_id == recipe_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recipe already saved",
        )

    saved = SavedRecipe(
        user_id=current_user.id,
        recipe_id=recipe_id,
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)

    return SavedRecipeResponse(
        id=saved.id,
        user_id=saved.user_id,
        recipe_id=saved.recipe_id,
        saved_at=saved.saved_at,
        recipe={
            "id": recipe.id,
            "recipe_id": recipe.recipe_id,
            "recipe_name": recipe.recipe_name,
            "cuisine": recipe.cuisine,
            "course": recipe.course,
            "recipe_type": recipe.recipe_type,
            "total_time_min": recipe.total_time_min,
            "servings": recipe.servings,
            "image_url": recipe.image_url,
            "diet_labels": recipe.diet_labels,
        }
    )


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unsave_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a saved recipe."""
    saved = db.query(SavedRecipe).filter(
        SavedRecipe.user_id == current_user.id,
        SavedRecipe.recipe_id == recipe_id
    ).first()
    if not saved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved recipe not found",
        )

    db.delete(saved)
    db.commit()


@router.get("/{recipe_id}/check")
async def check_saved(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check if a recipe is saved by the current user."""
    saved = db.query(SavedRecipe).filter(
        SavedRecipe.user_id == current_user.id,
        SavedRecipe.recipe_id == recipe_id
    ).first()
    return {"saved": saved is not None}