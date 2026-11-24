"""Recipe detail page."""

import streamlit as st
from app.auth.dependencies import require_auth
from app.database.session import get_db
from app.database.models import Recipe
from app.components.forms import nutrition_status_badge, dietary_compliance_badge

def render():
    """Render the recipe detail page."""
    require_auth()
    
    recipe_id = st.session_state.get("selected_recipe_id")
    if not recipe_id:
        st.error("No recipe selected")
        if st.button("Back to Recipes"):
            st.session_state.current_page = "recipes"
            st.rerun()
        return
    
    db = next(get_db())
    
    try:
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        
        if not recipe:
            st.error("Recipe not found")
            if st.button("Back to Recipes"):
                st.session_state.current_page = "recipes"
                st.rerun()
            return
        
        # Header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title(recipe.recipe_name)
        with col2:
            if st.button("← Back to Recipes", use_container_width=True):
                st.session_state.current_page = "recipes"
                st.rerun()
        
        st.markdown("---")
        
        # Metadata badges
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Cuisine", recipe.cuisine)
        with col2:
            st.metric("Course", recipe.course)
        with col3:
            st.metric("Type", recipe.recipe_type)
        with col3:
            st.metric("Servings", recipe.servings)
        
        st.markdown("---")
        
        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 Ingredients & Instructions",
            "🔬 Nutrition Breakdown",
            "🛡️ Dietary Classification",
            "📝 Notes"
        ])
        
        with tab1:
            st.subheader("Ingredients")
            if recipe.ingredients_en:
                ingredients = [i.strip() for i in recipe.ingredients_en.split(',') if i.strip()]
                for ing in ingredients:
                    st.write(f"• {ing}")
            else:
                st.write(recipe.ingredients_raw or "No ingredients listed")
            
            st.markdown("---")
            
            st.subheader("Instructions")
            if recipe.instructions_en:
                steps = [s.strip() for s in recipe.instructions_en.split('.') if s.strip()]
                for i, step in enumerate(steps, 1):
                    st.write(f"{i}. {step}")
            else:
                st.write(recipe.instructions_raw or "No instructions available")
            
            if recipe.total_time_min:
                st.info(f"⏱️ Total Time: {recipe.total_time_min} minutes "
                       f"(Prep: {recipe.prep_time_min} min, Cook: {recipe.cook_time_min} min)")
            
            if recipe.source_url:
                st.link_button("View Original Source", recipe.source_url)
        
        with tab2:
            st.subheader("Nutrition Breakdown (Per Serving)")
            
            status_colors = {
                "COMPLETE": "green",
                "PARTIAL": "orange",
                "UNAVAILABLE": "gray",
                "NO_MAPPED_INGREDIENTS": "red",
            }
            color = status_colors.get(recipe.nutrition_status, "gray")
            st.markdown(
                f'<span style="background-color: {color}; color: white; padding: 4px 12px; '
                f'border-radius: 12px; font-weight: bold;">Nutrition: {recipe.nutrition_status}</span>',
                unsafe_allow_html=True
            )
            
            if recipe.per_serving_nutrients:
                nuts = recipe.per_serving_nutrients
                
                # Macronutrients
                st.subheader("Macronutrients")
                col1, col2, col3, col4, col5 = st.columns(5)
                if "energy_kcal" in nuts:
                    with col1:
                        st.metric("Energy", f"{nuts['energy_kcal']:.0f} kcal")
                if "protein_g" in nuts:
                    with col2:
                        st.metric("Protein", f"{nuts['protein_g']:.1f} g")
                if "fat_g" in nuts:
                    with col3:
                        st.metric("Fat", f"{nuts['fat_g']:.1f} g")
                if "carb_available_g" in nuts:
                    with col4:
                        st.metric("Carbs", f"{nuts['carb_available_g']:.1f} g")
                if "fibre_total_g" in nuts:
                    with col5:
                        st.metric("Fibre", f"{nuts['fibre_total_g']:.1f} g")
                
                # Micronutrients
                st.subheader("Micronutrients")
                col1, col2, col3, col4 = st.columns(4)
                micronutrients = [
                    ("Moisture", "moisture_g", "g"),
                    ("Ash", "ash_g", "g"),
                    ("Total Fibre", "fibre_total_g", "g"),
                    ("Insoluble Fibre", "fibre_insoluble_g", "g"),
                    ("Soluble Fibre", "fibre_soluble_g", "g"),
                    ("Available Carb", "carb_available_g", "g"),
                ]
                
                for i, (label, key, unit) in enumerate(micronutrients):
                    col = [col1, col2, col3, col4][i % 4]
                    with col:
                        if key in nuts:
                            st.metric(label, f"{nuts[key]:.1f} {unit}")
                
                # Energy in kJ
                if "energy_kj" in nuts:
                    st.metric("Energy (kJ)", f"{nuts['energy_kj']:.1f} kJ")
                
                # Completeness
                if recipe.nutrient_completeness:
                    st.subheader("Nutrient Completeness")
                    for nutrient, completeness in recipe.nutrient_completeness.items():
                        st.progress(completeness, text=f"{nutrient}: {completeness:.0%}")
                
                # Provenance
                if recipe.nutrition_provenance:
                    with st.expander("📋 Calculation Provenance"):
                        st.json(recipe.nutrition_provenance)
            else:
                st.warning("No nutrition data available for this recipe.")
                st.info("Nutrition calculations require approved ingredient-to-IFCT mappings. "
                       "Currently, no mappings have been approved (Gate C authorization pending).")
        
        with tab3:
            st.subheader("Dietary Classification")
            
            if recipe.diet_classification:
                dc = recipe.diet_classification
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Diet Type", dc.get("diet_type", "UNKNOWN"))
                    st.write(f"**Vegetarian:** {dc.get('is_vegetarian', False)}")
                    st.write(f"**Vegan:** {dc.get('is_vegan', False)}")
                    st.write(f"**Eggetarian:** {dc.get('is_eggetarian', False)}")
                with col2:
                    st.write(f"**Non-Vegetarian:** {dc.get('is_non_veg', False)}")
                    if dc.get("non_veg_ingredients"):
                        st.write(f"**Non-veg ingredients:** {', '.join(dc['non_veg_ingredients'])}")
                    if dc.get("dairy_ingredients"):
                        st.write(f"**Dairy ingredients:** {', '.join(dc['dairy_ingredients'])}")
                    if dc.get("egg_ingredients"):
                        st.write(f"**Egg ingredients:** {', '.join(dc['egg_ingredients'])}")
                    st.write(f"**Jain Compliant:** {dc.get('jain_compliant', False)}")
                    if dc.get("jain_restricted_ingredients"):
                        st.write(f"**Jain-restricted:** {', '.join(dc['jain_restricted_ingredients'])}")
            else:
                st.info("Dietary classification not available")
        
        with tab4:
            st.subheader("Your Notes")
            notes = st.text_area("Add your personal notes about this recipe", height=150)
            if st.button("Save Notes"):
                st.success("Notes saved!")
        
        # Action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💾 Save Recipe", use_container_width=True):
                st.success("Recipe saved!")
        with col2:
            if st.button("📅 Add to Meal Plan", use_container_width=True):
                st.session_state.current_page = "meal_planner"
                st.rerun()
        with col3:
            if st.button("✨ Get Similar Recipes", use_container_width=True):
                st.session_state.current_page = "recommendations"
                st.rerun()
    
    finally:
        db.close()

if __name__ == "__main__":
    render()