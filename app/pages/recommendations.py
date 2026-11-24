"""Recommendations page - Personalized recipe recommendations."""

import streamlit as st
from app.auth.dependencies import require_auth, get_user_profile, get_user_id
from app.database.session import get_db
from app.database.models import Recipe
from app.components.forms import recipe_card

def render():
    """Render the personalized recommendations page."""
    user = require_auth()
    profile = get_user_profile()
    user_id = get_user_id()
    
    st.title("✨ Personalized Recommendations")
    st.markdown("---")
    
    # Options
    col1, col2, col3 = st.columns(3)
    with col1:
        rec_type = st.selectbox(
            "Recommendation Type",
            ["Similar to a Recipe", "By Ingredients", "For a Meal Slot", "Diverse Discovery"]
        )
    with col2:
        k = st.slider("Number of Recommendations", 5, 20, 10)
    with col3:
        min_nutrition = st.selectbox(
            "Min Nutrition Completeness",
            [0.0, 0.3, 0.5, 0.7, 0.9],
            format_func=lambda x: f"{int(x*100)}%" if x > 0 else "Any"
        )
    
    # Input based on recommendation type
    query_recipe_id = None
    query_ingredients = None
    meal_slot = None
    
    if rec_type == "Similar to a Recipe":
        db = next(get_db())
        try:
            recipes = db.query(Recipe).order_by(Recipe.recipe_name).all()
            recipe_names = {r.recipe_id: f"{r.recipe_name} ({r.cuisine})" for r in recipes}
            selected = st.selectbox("Select a Recipe", options=list(recipe_names.keys()),
                                  format_func=lambda x: recipe_names[x])
            query_recipe_id = selected
        finally:
            db.close()
    
    elif rec_type == "By Ingredients":
        ingredients_input = st.text_area(
            "Enter Ingredients (comma-separated)",
            placeholder="rice, dal, onion, tomato, turmeric"
        )
        if ingredients_input:
            query_ingredients = [i.strip() for i in ingredients_input.split(',') if i.strip()]
    
    elif rec_type == "For a Meal Slot":
        meal_slot = st.selectbox(
            "Meal Slot",
            ["BREAKFAST", "MORNING_SNACK", "LUNCH", "EVENING_SNACK", "DINNER"]
        )
    
    # Filters
    st.markdown("---")
    with st.expander("🔍 Advanced Filters"):
        db = next(get_db())
        try:
            cuisines = db.query(Recipe.cuisine).distinct().all()
            cuisine_options = ["Any"] + sorted([c[0] for c in cuisines if c[0]])
            selected_cuisine = st.selectbox("Cuisine", cuisine_options)
            
            courses = db.query(Recipe.course).distinct().all()
            course_options = ["Any"] + sorted([c[0] for c in courses if c[0]])
            selected_course = st.selectbox("Course", course_options)
            
            diet_options = ["Any", "VEGAN", "VEGETARIAN", "EGGETARIAN", "NON_VEGETARIAN", "JAIN"]
            selected_diet = st.selectbox("Diet Type", diet_options)
            
            max_time = st.slider("Max Prep+Cook Time (min)", 0, 180, 180)
        finally:
            db.close()
    
    # Generate recommendations
    if st.button("🔍 Get Recommendations", type="primary", use_container_width=True):
        # In a real implementation, this would call the personalized recommender
        # For now, we'll show a placeholder with actual recipe data
        
        db = next(get_db())
        try:
            query = db.query(Recipe)
            
            # Apply filters based on user profile
            from app.personalization.dietary_constraints import DietaryConstraintEngine
            engine = DietaryConstraintEngine()
            
            # Get user dietary constraints
            profile = get_user_profile()
            user_pref = profile.get("dietary_preference", "OMNIVORE")
            user_allergies = profile.get("allergies", [])
            user_exclusions = profile.get("ingredient_exclusions", [])
            
            # Simple filtering for demo
            if user_pref == "VEGETARIAN":
                query = db.query(Recipe).filter(Recipe.recipe_type.in_(["VEGETARIAN", "VEGAN", "EGGETARIAN"]))
            elif user_pref == "VEGAN":
                query = db.query(Recipe).filter(Recipe.recipe_type == "VEGAN")
            elif user_pref == "EGGETARIAN":
                query = db.query(Recipe).filter(Recipe.recipe_type.in_(["VEGETARIAN", "VEGAN", "EGGETARIAN"]))
            else:
                query = db.query(Recipe)
            
            # Apply filters
            if 'selected_cuisine' in locals() and selected_cuisine != "Any":
                query = query.filter(Recipe.cuisine == selected_cuisine)
            if 'selected_course' in locals() and selected_course != "Any":
                query = query.filter(Recipe.course == selected_course)
            if 'selected_diet' in locals() and selected_diet != "Any":
                query = query.filter(Recipe.recipe_type == selected_diet)
            if 'max_time' in locals():
                query = query.filter(Recipe.total_time_min <= max_time)
            
            # Get recommendations
            recipes = query.limit(k).all()
            
            if recipes:
                st.subheader(f"🎯 Top {len(recipes)} Recommendations for You")
                
                for recipe in recipes:
                    # Check dietary compliance
                    from app.personalization.dietary_constraints import DietaryConstraintEngine
                    engine = DietaryConstraintEngine()
                    ingredients = []  # Would get from recipe
                    eval_result = engine.evaluate_recipe(
                        recipe_id=recipe.id,
                        recipe_name=recipe.recipe_name,
                        ingredients=[],
                        user_preference=user_pref,
                        user_allergies=user_allergies,
                        user_exclusions=user_exclusions
                    )
                    
                    from app.components.forms import recipe_card
                    recipe_card(
                        {
                            "id": recipe.id,
                            "recipe_name": recipe.recipe_name,
                            "cuisine": recipe.cuisine,
                            "course": recipe.course,
                            "diet_labels": recipe.diet_labels,
                            "per_serving_nutrients": recipe.per_serving_nutrients,
                            "nutrition_status": recipe.nutrition_status,
                            "shared_ingredients": [],
                            "explanation": f"Recommended for your {user_pref} diet",
                            "component_scores": {},
                            "dietary_evaluation": eval_result.to_dict() if hasattr(eval_result, 'to_dict') else {},
                            "nutrition_match_score": 0.8,
                            "nutrition_completeness": 1.0 if recipe.nutrition_status == "COMPLETE" else 0.5,
                            "meets_nutritional_targets": {},
                        }
                    )
            else:
                st.info("No recipes match your criteria. Try adjusting your filters.")
        finally:
            db.close()

if __name__ == "__main__":
    render()