"""Dashboard page - User's main dashboard."""

import streamlit as st
from app.auth.dependencies import require_auth, get_user_profile, get_user_id
from app.database.session import get_db
from app.database.models import MealPlan, SavedRecipe, Recipe
from app.components.forms import meal_slot_badge, nutrition_status_badge

def render():
    """Render the dashboard page."""
    user = require_auth()
    profile = get_user_profile()
    user_id = get_user_id()
    
    st.title("📊 Dashboard")
    st.markdown(f"Welcome back, **{user.full_name or user.email.split('@')[0]}**!")
    st.markdown("---")
    
    db = next(get_db())
    
    try:
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            meal_plans_count = db.query(MealPlan).filter(MealPlan.user_id == user.id).count()
            st.metric("Meal Plans", meal_plans_count)
        
        with col2:
            saved_recipes_count = db.query(SavedRecipe).filter(SavedRecipe.user_id == user.id).count()
            st.metric("Saved Recipes", saved_recipes_count)
        
        with col3:
            # Meals completed this week
            from datetime import date, timedelta
            week_start = date.today() - timedelta(days=date.today().weekday())
            week_end = week_start + timedelta(days=6)
            
            completed_meals = 0  # Would need MealPlanItem join
            st.metric("Meals This Week", completed_meals)
        
        with col4:
            # Nutrition completeness
            total_recipes = db.query(Recipe).count()
            available_nutrition = db.query(Recipe).filter(Recipe.nutrition_status.in_(["COMPLETE", "PARTIAL"])).count()
            nutrition_pct = (available_nutrition / total_recipes * 100) if total_recipes > 0 else 0
            st.metric("Nutrition Coverage", f"{nutrition_pct:.0f}%")
        
        st.markdown("---")
        
        # Today's meal plan
        st.subheader("📅 Today's Meal Plan")
        today = date.today()
        
        today_plan = db.query(MealPlan).filter(
            MealPlan.user_id == user.id,
            MealPlan.start_date <= date.today(),
            MealPlan.end_date >= date.today(),
            MealPlan.status == "ACTIVE"
        ).first()
        
        if today_plan:
            from app.components.forms import meal_slot_badge
            from app.database.models import MealPlanItem, MealSlot
            
            items = db.query(MealPlanItem).filter(
                MealPlanItem.meal_plan_id == today_plan.id
            ).order_by(
                MealPlanItem.day_index,
                MealPlanItem.meal_slot
            ).all()
            
            if items:
                cols = st.columns(5)
                slot_order = ["BREAKFAST", "MORNING_SNACK", "LUNCH", "EVENING_SNACK", "DINNER"]
                
                for i, slot in enumerate(slot_order):
                    with cols[i]:
                        meal_slot_badge(slot)
                        slot_items = [item for item in items if item.meal_slot == slot]
                        if slot_items:
                            for item in slot_items:
                                recipe = db.query(Recipe).filter(Recipe.id == item.recipe_id).first()
                                if recipe:
                                    st.write(f"**{recipe.recipe_name}**")
                                    if item.is_completed:
                                        st.success("✅ Completed")
                                    else:
                                        if st.button(f"Mark Done", key=f"complete_{item.id}", use_container_width=True):
                                            item.is_completed = True
                                            item.completed_at = datetime.utcnow()
                                            db.commit()
                                            st.rerun()
                                else:
                                    st.info("No meal planned")
            else:
                st.info("No active meal plan for today. [Create one](#meal-planner)")
        else:
            st.info("No active meal plan for today. [Create one](#meal-planner)")
        
        st.markdown("---")
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🍽️ Browse Recipes", use_container_width=True):
                st.session_state.current_page = "recipes"
                st.rerun()
        
        with col2:
            if st.button("✨ Get Recommendations", use_container_width=True):
                st.session_state.current_page = "recommendations"
                st.rerun()
        
        with col3:
            if st.button("📅 Create Meal Plan", use_container_width=True):
                st.session_state.current_page = "meal_planner"
                st.rerun()
        
        with col4:
            if st.button("🎯 View Nutrition Targets", use_container_width=True):
                st.session_state.current_page = "nutrition_targets"
                st.rerun()
        
        st.markdown("---")
        
        # Recent activity
        st.subheader("📜 Recent Activity")
        
        # Recent saved recipes
        recent_saves = db.query(SavedRecipe).filter(
            SavedRecipe.user_id == user.id
        ).order_by(SavedRecipe.saved_at.desc()).limit(5).all()
        
        if recent_saves:
            st.write("**Recently Saved Recipes**")
            for save in recent_saves:
                recipe = db.query(Recipe).filter(Recipe.id == save.recipe_id).first()
                if recipe:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"💾 {recipe.recipe_name}")
                    with col2:
                        st.caption(save.saved_at.strftime("%b %d, %Y"))
        else:
            st.info("No saved recipes yet. Browse recipes to save favorites!")
        
    finally:
        db.close()

if __name__ == "__main__":
    render()