"""Recipes page - Recipe discovery and search."""

import streamlit as st
from app.auth.dependencies import require_auth
from app.database.session import get_db
from app.database.models import Recipe
from app.components.forms import recipe_card, nutrition_status_badge

def render():
    """Render the recipes discovery page."""
    require_auth()
    
    st.title("🍲 Discover Recipes")
    st.markdown("---")
    
    db = next(get_db())
    
    try:
        # Filters sidebar
        with st.sidebar:
            st.subheader("🔍 Filters")
            
            # Cuisine filter
            cuisines = db.query(Recipe.cuisine).distinct().all()
            cuisine_options = sorted([c[0] for c in cuisines if c[0]])
            selected_cuisine = st.selectbox("Cuisine", ["All"] + cuisine_options)
            
            # Course filter
            courses = db.query(Recipe.course).distinct().all()
            course_options = sorted([c[0] for c in courses if c[0]])
            selected_course = st.selectbox("Course", ["All"] + course_options)
            
            # Diet filter
            diet_options = ["All", "VEGAN", "VEGETARIAN", "EGGETARIAN", "NON_VEGETARIAN", "JAIN"]
            selected_diet = st.selectbox("Diet Type", diet_options)
            
            # Nutrition availability
            nutrition_options = ["All", "COMPLETE", "PARTIAL", "UNAVAILABLE"]
            selected_nutrition = st.selectbox("Nutrition Data", nutrition_options)
            
            # Time constraints
            max_time = st.slider("Max Total Time (min)", 0, 180, 180, step=5)
            
            # Sort
            sort_by = st.selectbox("Sort By", ["Name", "Cuisine", "Course", "Total Time"])
            sort_order = st.radio("Order", ["Ascending", "Descending"], horizontal=True)
        
        # Build query
        query = db.query(Recipe)
        
        if selected_cuisine != "All":
            query = query.filter(Recipe.cuisine == selected_cuisine)
        if selected_course != "All":
            query = query.filter(Recipe.course == selected_course)
        if selected_diet != "All":
            query = query.filter(Recipe.recipe_type == selected_diet)
        if selected_nutrition != "All":
            query = query.filter(Recipe.nutrition_status == selected_nutrition)
        if max_time < 180:
            query = query.filter(Recipe.total_time_min <= max_time)
        
        # Sorting
        if sort_by == "Name":
            query = query.order_by(Recipe.recipe_name.asc() if sort_order == "Ascending" else Recipe.recipe_name.desc())
        elif sort_by == "Cuisine":
            query = query.order_by(Recipe.cuisine.asc() if sort_order == "Ascending" else Recipe.cuisine.desc())
        elif sort_by == "Course":
            query = query.order_by(Recipe.course.asc() if sort_order == "Ascending" else Recipe.course.desc())
        elif sort_by == "Total Time":
            query = query.order_by(Recipe.total_time_min.asc() if sort_order == "Ascending" else Recipe.total_time_min.desc())
        
        # Pagination
        page_size = 20
        total = query.count()
        total_pages = (total + page_size - 1) // page_size
        
        if 'recipe_page' not in st.session_state:
            st.session_state.recipe_page = 1
        
        page = st.session_state.recipe_page
        offset = (page - 1) * page_size
        
        recipes = query.offset(offset).limit(page_size).all()
        
        # Display results
        st.markdown(f"**Found {total} recipes** (Page {page}/{total_pages})")
        
        if not recipes:
            st.info("No recipes match your filters. Try adjusting your filters.")
        else:
            # Display recipes in grid
            cols = st.columns(2)
            for i, recipe in enumerate(recipes):
                with cols[i % 2]:
                    with st.container():
                        st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.markdown("🍲")
                        with col2:
                            st.subheader(recipe.recipe_name)
                            st.caption(f"🍽️ {recipe.cuisine} • 🍽️ {recipe.course}")
                            
                            # Nutrition status badge
                            status_colors = {
                                "COMPLETE": "green",
                                "PARTIAL": "orange",
                                "UNAVAILABLE": "gray",
                                "NO_MAPPED_INGREDIENTS": "red"
                            }
                            color = status_colors.get(recipe.nutrition_status, "gray")
                            st.markdown(
                                f'<span style="background-color: {color}; color: white; '
                                f'padding: 2px 8px; border-radius: 12px; font-size: 0.8em;">'
                                f'{recipe.nutrition_status}</span>',
                                unsafe_allow_html=True
                            )
                            
                            if recipe.per_serving_nutrients:
                                nuts = recipe.per_serving_nutrients
                                cols = st.columns(4)
                                if "energy_kcal" in recipe.per_serving_nutrients:
                                    cols[0].metric("Calories", f"{recipe.per_serving_nutrients['energy_kcal']:.0f} kcal")
                                if "protein_g" in recipe.per_serving_nutrients:
                                    cols[1].metric("Protein", f"{recipe.per_serving_nutrients['protein_g']:.1f} g")
                                if "carb_available_g" in recipe.per_serving_nutrients:
                                    cols[2].metric("Carbs", f"{recipe.per_serving_nutrients['carb_available_g']:.1f} g")
                                if "fat_g" in recipe.per_serving_nutrients:
                                    cols[3].metric("Fat", f"{recipe.per_serving_nutrients['fat_g']:.1f} g")
                            
                            if st.button("View Details", key=f"view_{recipe.id}", use_container_width=True):
                                st.session_state.selected_recipe_id = recipe.id
                                st.session_state.current_page = "recipe_detail"
                                st.rerun()
                        
                        st.markdown('</div>', unsafe_allow_html=True)
            
            # Pagination
            if total > 20:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    if page > 1 and st.button("⬅️ Previous", use_container_width=True):
                        st.session_state.recipe_page -= 1
                        st.rerun()
                with col2:
                    st.write(f"Page {page} of {total_pages}")
                with col3:
                    if page < total_pages and st.button("Next ➡️", use_container_width=True):
                        st.session_state.recipe_page += 1
                        st.rerun()
    
    finally:
        db.close()

if __name__ == "__main__":
    render()