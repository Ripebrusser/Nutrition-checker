"""Meal plans API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

from app.db.session import get_db
from app.db.models import User, MealPlan, MealPlanItem, MealSlot, MealPlanStatus, Recipe
from app.auth.dependencies import get_current_user
from app.services.meal_plan_service import MealPlanService, OptimizationUnavailable

router = APIRouter()


class MealPlanItemCreate(BaseModel):
    meal_slot: str
    day_index: int
    recipe_id: Optional[int] = None
    servings: float = 1.0


class MealPlanItemUpdate(BaseModel):
    recipe_id: Optional[int] = None
    servings: Optional[float] = None
    is_completed: Optional[bool] = None


class MealPlanItemResponse(BaseModel):
    id: int
    meal_slot: str
    day_index: int
    recipe_id: Optional[int]
    servings: float
    recipe: Optional[dict] = None
    is_completed: bool
    completed_at: Optional[datetime]

    @classmethod
    def from_item(cls, item: MealPlanItem) -> "MealPlanItemResponse":
        """Serialize a meal item, including its recipe summary when present."""
        recipe = item.recipe
        return cls(
            id=item.id,
            meal_slot=item.meal_slot.value if hasattr(item.meal_slot, "value") else str(item.meal_slot),
            day_index=item.day_index,
            recipe_id=item.recipe_id,
            servings=item.servings,
            recipe={
                "id": recipe.id,
                "recipe_name": recipe.recipe_name,
                "cuisine": recipe.cuisine,
                "course": recipe.course,
                "total_time_min": recipe.total_time_min,
                "servings": recipe.servings,
                "diet_labels": recipe.diet_labels,
                "recipe_type": recipe.recipe_type,
            } if recipe else None,
            is_completed=item.is_completed,
            completed_at=item.completed_at,
        )


class MealPlanCreate(BaseModel):
    name: Optional[str] = None
    start_date: date
    end_date: date


class MealPlanUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None


class MealPlanResponse(BaseModel):
    id: int
    user_id: int
    name: Optional[str]
    start_date: date
    end_date: date
    status: str
    items: List[MealPlanItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MealPlanListResponse(BaseModel):
    id: int
    name: Optional[str]
    start_date: date
    end_date: date
    status: str
    item_count: int
    completed_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=List[MealPlanListResponse])
async def get_meal_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all meal plans for current user."""
    meal_plans = db.query(MealPlan).filter(
        MealPlan.user_id == current_user.id
    ).order_by(MealPlan.created_at.desc()).all()

    result = []
    for plan in meal_plans:
        items = db.query(MealPlanItem).filter(MealPlanItem.meal_plan_id == plan.id).all()
        result.append(MealPlanListResponse(
            id=plan.id,
            name=plan.name,
            start_date=plan.start_date,
            end_date=plan.end_date,
            status=plan.status.value,
            item_count=len([i for i in items if i.recipe_id]),
            completed_count=len([i for i in items if i.is_completed]),
            created_at=plan.created_at,
            updated_at=plan.updated_at,
        ))
    return result


@router.get("/active", response_model=Optional[MealPlanResponse])
async def get_active_meal_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the active meal plan for current user."""
    meal_plan = db.query(MealPlan).filter(
        MealPlan.user_id == current_user.id,
        MealPlan.status == MealPlanStatus.ACTIVE
    ).first()
    if not meal_plan:
        return None

    items = db.query(MealPlanItem).filter(
        MealPlanItem.meal_plan_id == meal_plan.id
    ).order_by(MealPlanItem.day_index, MealPlanItem.meal_slot).all()

    return MealPlanResponse(
        id=meal_plan.id,
        user_id=meal_plan.user_id,
        name=meal_plan.name,
        start_date=meal_plan.start_date,
        end_date=meal_plan.end_date,
        status=meal_plan.status.value,
        items=[MealPlanItemResponse.from_item(item) for item in items],
        created_at=meal_plan.created_at,
        updated_at=meal_plan.updated_at,
    )


@router.get("/{meal_plan_id}", response_model=MealPlanResponse)
async def get_meal_plan(
    meal_plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific meal plan."""
    meal_plan = db.query(MealPlan).filter(
        MealPlan.id == meal_plan_id,
        MealPlan.user_id == current_user.id
    ).first()
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )

    items = db.query(MealPlanItem).filter(
        MealPlanItem.meal_plan_id == meal_plan.id
    ).order_by(MealPlanItem.day_index, MealPlanItem.meal_slot).all()

    return MealPlanResponse(
        id=meal_plan.id,
        user_id=meal_plan.user_id,
        name=meal_plan.name,
        start_date=meal_plan.start_date,
        end_date=meal_plan.end_date,
        status=meal_plan.status.value,
        items=[MealPlanItemResponse.from_item(item) for item in items],
        created_at=meal_plan.created_at,
        updated_at=meal_plan.updated_at,
    )


@router.post("", response_model=MealPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_meal_plan(
    plan_data: MealPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new meal plan."""
    # Deactivate any existing active plan
    db.query(MealPlan).filter(
        MealPlan.user_id == current_user.id,
        MealPlan.status == MealPlanStatus.ACTIVE
    ).update({"status": MealPlanStatus.DRAFT})

    meal_plan = MealPlan(
        user_id=current_user.id,
        name=plan_data.name,
        start_date=plan_data.start_date,
        end_date=plan_data.end_date,
        status=MealPlanStatus.ACTIVE,
    )
    db.add(meal_plan)
    db.commit()
    db.refresh(meal_plan)

    return MealPlanResponse(
        id=meal_plan.id,
        user_id=meal_plan.user_id,
        name=meal_plan.name,
        start_date=meal_plan.start_date,
        end_date=meal_plan.end_date,
        status=meal_plan.status.value,
        items=[],
        created_at=meal_plan.created_at,
        updated_at=meal_plan.updated_at,
    )


@router.patch("/{meal_plan_id}", response_model=MealPlanResponse)
async def update_meal_plan(
    meal_plan_id: int,
    plan_data: MealPlanUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a meal plan."""
    meal_plan = db.query(MealPlan).filter(
        MealPlan.id == meal_plan_id,
        MealPlan.user_id == current_user.id
    ).first()
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )

    update_data = plan_data.dict(exclude_unset=True)
    if "status" in update_data:
        update_data["status"] = MealPlanStatus(update_data["status"])

    for field, value in update_data.items():
        setattr(meal_plan, field, value)

    db.commit()
    db.refresh(meal_plan)

    items = db.query(MealPlanItem).filter(
        MealPlanItem.meal_plan_id == meal_plan.id
    ).order_by(MealPlanItem.day_index, MealPlanItem.meal_slot).all()

    return MealPlanResponse(
        id=meal_plan.id,
        user_id=meal_plan.user_id,
        name=meal_plan.name,
        start_date=meal_plan.start_date,
        end_date=meal_plan.end_date,
        status=meal_plan.status.value,
        items=[MealPlanItemResponse.from_item(item) for item in items],
        created_at=meal_plan.created_at,
        updated_at=meal_plan.updated_at,
    )


@router.delete("/{meal_plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal_plan(
    meal_plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a meal plan."""
    meal_plan = db.query(MealPlan).filter(
        MealPlan.id == meal_plan_id,
        MealPlan.user_id == current_user.id
    ).first()
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )

    db.delete(meal_plan)
    db.commit()


# Meal items endpoints
@router.post("/{meal_plan_id}/meals", response_model=MealPlanItemResponse, status_code=status.HTTP_201_CREATED)
async def add_meal(
    meal_plan_id: int,
    meal_data: MealPlanItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a meal to a meal plan."""
    meal_plan = db.query(MealPlan).filter(
        MealPlan.id == meal_plan_id,
        MealPlan.user_id == current_user.id
    ).first()
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )

    # Validate meal slot
    try:
        meal_slot = MealSlot(meal_data.meal_slot)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid meal slot. Must be one of: {[s.value for s in MealSlot]}",
        )

    # Check if slot already occupied
    existing = db.query(MealPlanItem).filter(
        MealPlanItem.meal_plan_id == meal_plan_id,
        MealPlanItem.day_index == meal_data.day_index,
        MealPlanItem.meal_slot == meal_slot
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meal slot already occupied. Use PUT to update.",
        )

    # Validate recipe exists if provided
    if meal_data.recipe_id:
        recipe = db.query(Recipe).filter(Recipe.id == meal_data.recipe_id).first()
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found",
            )

    meal_item = MealPlanItem(
        meal_plan_id=meal_plan_id,
        meal_slot=meal_slot,
        day_index=meal_data.day_index,
        recipe_id=meal_data.recipe_id,
        servings=meal_data.servings,
    )
    db.add(meal_item)
    db.commit()
    db.refresh(meal_item)

    return MealPlanItemResponse.from_item(meal_item)


@router.patch("/{meal_plan_id}/meals/{meal_id}", response_model=MealPlanItemResponse)
async def update_meal(
    meal_plan_id: int,
    meal_id: int,
    meal_data: MealPlanItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a meal in a meal plan."""
    meal_plan = db.query(MealPlan).filter(
        MealPlan.id == meal_plan_id,
        MealPlan.user_id == current_user.id
    ).first()
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )

    meal_item = db.query(MealPlanItem).filter(
        MealPlanItem.id == meal_id,
        MealPlanItem.meal_plan_id == meal_plan_id
    ).first()
    if not meal_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found",
        )

    update_data = meal_data.dict(exclude_unset=True)
    if "is_completed" in update_data and update_data["is_completed"] and not meal_item.is_completed:
        update_data["completed_at"] = datetime.utcnow()
    elif "is_completed" in update_data and not update_data["is_completed"]:
        update_data["completed_at"] = None

    for field, value in update_data.items():
        setattr(meal_item, field, value)

    db.commit()
    db.refresh(meal_item)

    return MealPlanItemResponse.from_item(meal_item)


@router.delete("/{meal_plan_id}/meals/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_meal(
    meal_plan_id: int,
    meal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a meal from a meal plan."""
    meal_plan = db.query(MealPlan).filter(
        MealPlan.id == meal_plan_id,
        MealPlan.user_id == current_user.id
    ).first()
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )

    meal_item = db.query(MealPlanItem).filter(
        MealPlanItem.id == meal_id,
        MealPlanItem.meal_plan_id == meal_plan_id
    ).first()
    if not meal_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found",
        )

    db.delete(meal_item)
    db.commit()


@router.post("/{meal_plan_id}/meals/{meal_id}/complete", response_model=MealPlanItemResponse)
async def complete_meal(
    meal_plan_id: int,
    meal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a meal as completed and add to history."""
    meal_plan = db.query(MealPlan).filter(
        MealPlan.id == meal_plan_id,
        MealPlan.user_id == current_user.id
    ).first()
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )

    meal_item = db.query(MealPlanItem).filter(
        MealPlanItem.id == meal_id,
        MealPlanItem.meal_plan_id == meal_plan_id
    ).first()
    if not meal_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found",
        )

    if not meal_item.recipe_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot complete meal without a recipe",
        )

    # Mark as completed
    meal_item.is_completed = True
    meal_item.completed_at = datetime.utcnow()

    # Add to history
    from app.db.models import MealHistory
    history = MealHistory(
        user_id=current_user.id,
        meal_plan_id=meal_plan_id,
        recipe_id=meal_item.recipe_id,
        meal_slot=meal_item.meal_slot,
        consumed_at=datetime.utcnow(),
        servings=meal_item.servings,
    )
    db.add(history)

    db.commit()
    db.refresh(meal_item)

    return MealPlanItemResponse.from_item(meal_item)


@router.post("/{meal_plan_id}/optimize", response_model=MealPlanResponse)
async def optimize_meal_plan(
    meal_plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Optimize a meal plan using the meal plan optimizer."""
    meal_plan = db.query(MealPlan).filter(
        MealPlan.id == meal_plan_id,
        MealPlan.user_id == current_user.id
    ).first()
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )

    service = MealPlanService(db)
    try:
        optimized = service.optimize_meal_plan(meal_plan_id)
    except OptimizationUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(exc),
        )
    
    items = db.query(MealPlanItem).filter(
        MealPlanItem.meal_plan_id == meal_plan_id
    ).order_by(MealPlanItem.day_index, MealPlanItem.meal_slot).all()

    return MealPlanResponse(
        id=optimized.id,
        user_id=optimized.user_id,
        name=optimized.name,
        start_date=optimized.start_date,
        end_date=optimized.end_date,
        status=optimized.status.value,
        items=[MealPlanItemResponse.from_item(item) for item in items],
        created_at=optimized.created_at,
        updated_at=optimized.updated_at,
    )