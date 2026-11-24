"""Recipe service for recipe search and retrieval."""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.database.models import Recipe
from sqlalchemy import or_, and_

class RecipeService:
    """Service for recipe search and retrieval."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_recipe(self, recipe_id: int) -> Optional[Recipe]:
        """Get recipe by internal ID."""
        return self.db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    def get_recipe_by_recipe_id(self, recipe_id: int) -> Optional[Recipe]:
        """Get recipe by original recipe_id."""
        return self.db.query(Recipe).filter(Recipe.recipe_id == recipe_id).first()
    
    def search_recipes(
        self,
        query: Optional[str] = None,
        cuisine: Optional[str] = None,
        course: Optional[str] = None,
        diet_type: Optional[str] = None,
        max_time: Optional[int] = None,
        min_nutrition_completeness: float = 0.0,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Recipe]:
        """Search recipes with filters."""
        query = self.db.query(Recipe)
        
        if query:
            # Text search on recipe name and ingredients
            search_term = f"%{query.lower()}%"
            query = query.filter(
                or_(
                    Recipe.recipe_name.ilike(search_term),
                    Recipe.ingredients_en.ilike(search_term)
                )
            )
        
        if cuisine:
            query = query.filter(Recipe.cuisine == cuisine)
        
        if course:
            query = query.filter(Recipe.course == course)
        
        if diet_type:
            query = query.filter(Recipe.recipe_type == diet_type)
        
        if max_time:
            query = query.filter(Recipe.total_time_min <= max_time)
        
        # Nutrition completeness filter
        if min_nutrition_completeness > 0:
            query = query.filter(Recipe.nutrition_status.in_(["COMPLETE", "PARTIAL"]))
        
        return query.order_by(Recipe.recipe_name).offset(offset).limit(limit).all()
    
    def get_recipes_by_ids(self, recipe_ids: List[int]) -> List[Recipe]:
        """Get multiple recipes by IDs."""
        return self.db.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()
    
    def get_recipes_by_cuisine(self, cuisine: str, limit: int = 20) -> List[Recipe]:
        return self.db.query(Recipe).filter(Recipe.cuisine == cuisine).limit(limit).all()
    
    def get_recipes_by_course(self, course: str, limit: int = 20) -> List[Recipe]:
        return self.db.query(Recipe).filter(Recipe.course == course).limit(limit).all()
    
    def get_recipes_by_diet(self, diet_type: str, limit: int = 20) -> List[Recipe]:
        return self.db.query(Recipe).filter(Recipe.recipe_type == diet_type).limit(limit).all()
    
    def get_cuisines(self) -> List[str]:
        cuisines = self.db.query(Recipe.cuisine).distinct().all()
        return sorted([c[0] for c in cuisines if c[0]])
    
    def get_courses(self) -> List[str]:
        courses = self.db.query(Recipe.course).distinct().all()
        return sorted([c[0] for c in courses if c[0]])
    
    def get_diet_types(self) -> List[str]:
        return ["VEGAN", "VEGETARIAN", "EGGETARIAN", "NON_VEGETARIAN", "JAIN"]
    
    def get_nutrition_stats(self) -> dict:
        """Get nutrition data statistics."""
        from sqlalchemy import func
        total = self.db.query(func.count(Recipe.id)).scalar()
        complete = self.db.query(func.count(Recipe.id)).filter(Recipe.nutrition_status == "COMPLETE").scalar()
        partial = self.db.query(func.count(Recipe.id)).filter(Recipe.nutrition_status == "PARTIAL").scalar()
        unavailable = self.db.query(func.count(Recipe.id)).filter(Recipe.nutrition_status == "UNAVAILABLE").scalar()
        
        return {
            "total": total,
            "complete": complete,
            "partial": partial,
            "unavailable": unavailable,
            "coverage_pct": round((complete + partial) / total * 100, 1) if total > 0 else 0
        }
    
    def get_recipe_nutrition(self, recipe_id: int) -> Optional[Dict]:
        """Get nutrition info for a recipe."""
        recipe = self.get_recipe(recipe_id)
        if not recipe:
            return None
        
        return {
            "recipe_id": recipe.recipe_id,
            "recipe_name": recipe.recipe_name,
            "nutrition_status": recipe.nutrition_status,
            "total_nutrients": recipe.total_nutrients,
            "per_serving_nutrients": recipe.per_serving_nutrients,
            "nutrient_completeness": recipe.nutrient_completeness,
            "mapping_coverage": recipe.mapping_coverage,
            "weight_coverage": recipe.weight_coverage,
            "missing_nutrients": recipe.missing_nutrients,
            "nutrition_provenance": recipe.nutrition_provenance,
        }
    
    def get_recipes_by_nutrient_range(
        self,
        nutrient: str,
        min_val: float = None,
        max_val: float = None,
        limit: int = 20
    ) -> List[Recipe]:
        """Get recipes with nutrient in range (per serving)."""
        query = self.db.query(Recipe).filter(
            Recipe.per_serving_nutrients.isnot(None)
        )
        
        if min_val is not None:
            # JSON extraction for numeric comparison
            query = query.filter(
                Recipe.per_serving_nutrients[nutrient].astext.cast(float) >= min_val
            )
        if max_val is not None:
            query = query.filter(
                Recipe.per_serving_nutrients[nutrient].astext.cast(float) <= max_val
            )
        
        return query.limit(limit).all()