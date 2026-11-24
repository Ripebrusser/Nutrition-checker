"""History page - User's meal completion history and saved recipes."""

import streamlit as st
from datetime import date, timedelta
from app.auth.dependencies import require_auth, get_user_id
from app.database.session import get_db
from app.database.models import MealPlan, MealPlanItem, Recipe, SavedRecipe

def render():
    """Render the history page."""
    require_auth()
    user_id = get_user_id()
    
    st.title("📜 History")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📅 Meal History", "💾 Saved Recipes", "📊 Analytics"])
    
    db = next(get_db())
    
    try:
        with tab1:
            st.subheader("📅 Meal Completion History")
            
            # Date filter
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("From", value=date.today() - timedelta(days=30))
            with col2:
                end_date = st.date_input("To", value=date.today())
            
            # Get completed meals
            items = db.query(MealPlanItem).join(MealPlan).filter(
                MealPlan.user_id == st.session_state.user_id,
                MealPlanItem.is_completed == True,
                MealPlanItem.completed_at >= start_date,
                MealPlanItem.completed_at <= end_date + timedelta(days=1)
            ).order_by(MealPlanItem.completed_at.desc()).all()
            
            if items:
                st.write(f"**{len(items)} completed meals** in this period")
                
                # Group by date
                from collections import defaultdict
                meals_by_date = defaultdict(list)
                for item in items:
                    if item.completed_at:
                        d = item.completed_at.date()
                        meals_by_date[d].append(item)
                
                for meal_date in sorted(meals_by_date.keys(), reverse=True):
                    with st.expander(f"📅 {meal_date} ({len(meals_by_date[meal_date])} meals)"):
                        for item in meals_by_date[meal_date]:
                            if item.recipe_id:
                                recipe = db.query(Recipe).filter(Recipe.id == item.recipe_id).first()
                                if recipe:
                                    col1, col2, col3 = st.columns([3, 1, 1])
                                    with col1:
                                        st.write(f"**{recipe.recipe_name}** ({item.meal_slot})")
                                    with col2:
                                        if item.completed_at:
                                            st.caption(item.completed_at.strftime("%H:%M"))
                                    with col3:
                                        if item.is_completed:
                                            st.success("✅ Done")
            else:
                st.info("No completed meals in this period.")
        
        with tab2:
            st.subheader("💾 Saved Recipes")
            
            saved = db.query(SavedRecipe).filter(
                SavedRecipe.user_id == st.session_state.user_id
            ).order_by(SavedRecipe.saved_at.desc()).all()
            
            if saved:
                st.write(f"**{len(saved)} saved recipes**")
                
                for save in saved:
                    recipe = db.query(Recipe).filter(Recipe.id == save.recipe_id).first()
                    if recipe:
                        with st.expander(f"💾 {recipe.recipe_name} ({recipe.cuisine})"):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"**Cuisine:** {recipe.cuisine}")
                                st.write(f"**Course:** {recipe.course}")
                                st.write(f"**Type:** {recipe.recipe_type}")
                            with col2:
                                st.write(f"Saved: {save.saved_at.strftime('%b %d, %Y')}")
                                if save.notes:
                                    st.write(f"Notes: {save.notes}")
                                if st.button("🗑️ Remove", key=f"remove_{save.id}"):
                                    db.delete(save)
                                    db.commit()
                                    st.rerun()
                                if st.button("📋 View Details", key=f"view_{save.id}"):
                                    st.session_state.selected_recipe_id = recipe.id
                                    st.session_state.current_page = "recipe_detail"
                                    st.rerun()
            else:
                st.info("No saved recipes yet. Browse recipes and save your favorites!")
        
        with tab3:
            st.subheader("📊 Your Analytics")
            
            # Overall stats
            total_plans = db.query(MealPlan).filter(MealPlan.user_id == st.session_state.user_id).count()
            completed_plans = db.query(MealPlan).filter(
                MealPlan.user_id == st.session_state.user_id,
                MealPlan.status == "COMPLETED"
            ).count()
            
            total_saved = db.query(SavedRecipe).filter(SavedRecipe.user_id == st.session_state.user_id).count()
            
            completed_meals = db.query(MealPlanItem).join(MealPlan).filter(
                MealPlan.user_id == st.session_state.user_id,
                MealPlanItem.is_completed == True
            ).count()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Plans", total_plans)
            with col2:
                st.metric("Completed Plans", completed_plans)
            with col3:
                st.metric("Saved Recipes", total_saved)
            with col4:
                st.metric("Meals Completed", completed_meals)
            
            st.markdown("---")
            
            # Cuisine diversity
            st.subheader("🍽️ Cuisine Diversity")
            
            # Get cuisines from saved recipes
            saved_recipes = db.query(Recipe).join(SavedRecipe).filter(
                SavedRecipe.user_id == st.session_state.user_id
            ).all()
            
            if saved_recipes:
                from collections import Counter
                cuisine_counts = Counter(r.cuisine for r in saved_recipes)
                
                import plotly.express as px
                fig = px.pie(
                    values=list(cuisine_counts.values()),
                    names=list(cuisine_counts.keys()),
                    title="Saved Recipes by Cuisine"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Meal completion over time
            st.subheader("📈 Completion Trend")
            
            # Last 30 days completion
            end = date.today()
            start = end - timedelta(days=30)
            
            daily_completion = {}
            for i in range(31):
                d = start + timedelta(days=i)
                count = db.query(MealPlanItem).join(MealPlan).filter(
                    MealPlan.user_id == st.session_state.user_id,
                    MealPlanItem.is_completed == True,
                    MealPlanItem.completed_at >= d,
                    MealPlanItem.completed_at < d + timedelta(days=1)
                ).count()
                daily_completion[d] = count
            
            import plotly.express as px
            fig = px.line(
                x=list(daily_completion.keys()),
                y=list(daily_completion.values()),
                labels={'x': 'Date', 'y': 'Meals Completed'},
                title="Meals Completed (Last 30 Days)"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    finally:
        db.close()

if __name__ == "__main__":
    render()