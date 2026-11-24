"""FastAPI application for Indian Nutrition & Diet Planner."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.db.session import init_db, init_recipe_data
from app.api import auth, profile, nutrition, recipes, recommendations, meal_plans, saved_recipes, history, nutrition_breakdown


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    init_recipe_data()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Indian Nutrition & Diet Planner API",
    description="API for personalized Indian meal recommendations using health metrics and ingredient-level nutrition analysis",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(nutrition.router, prefix="/api/nutrition", tags=["Nutrition"])
app.include_router(recipes.router, prefix="/api/recipes", tags=["Recipes"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(meal_plans.router, prefix="/api/meal-plans", tags=["Meal Plans"])
app.include_router(saved_recipes.router, prefix="/api/saved-recipes", tags=["Saved Recipes"])
app.include_router(history.router, prefix="/api/history", tags=["Meal History"])
app.include_router(nutrition_breakdown.router, prefix="/api/nutrition", tags=["Nutrition Breakdown"])


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Indian Nutrition & Diet Planner API"}


@app.get("/api/meta/cuisines")
async def get_cuisines():
    from app.services.recipe_service import RecipeService
    from app.db.session import get_db
    db = next(get_db())
    service = RecipeService(db)
    return service.get_cuisines()


@app.get("/api/meta/courses")
async def get_courses():
    from app.services.recipe_service import RecipeService
    from app.db.session import get_db
    db = next(get_db())
    service = RecipeService(db)
    return service.get_courses()


@app.get("/api/meta/diet-labels")
async def get_diet_labels():
    from app.services.recipe_service import RecipeService
    from app.db.session import get_db
    db = next(get_db())
    service = RecipeService(db)
    return service.get_diet_labels()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)