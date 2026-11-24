"""Meal Planner page."""

import streamlit as st
from datetime import date, timedelta
from app.auth.dependencies import require_auth, get_user_id
from app.database.session import get_db
from app.database.models import MealPlan, MealPlanItem, Recipe, MealSlot, MealPlanStatus
from app.components.forms import meal_slot_badge

def render():
    """Render the meal planner page."""
    user = require_auth()
    user_id = get_user_id()
    
    st.title("📅 Meal Planner")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📅 Create Plan", "📋 My Plans", "📊 Weekly View"])
    
    db = next(get_db())
    
    try:
        with tab1:
            st.subheader("Create New Meal Plan")
            
            with st.form("create_plan_form"):
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start Date", value=date.today())
                    days = st.number_input("Number of Days", min_value=1, max_value=14, value=7)
                with col2:
                    meal_frequency = st.selectbox("Meals per Day", [3, 4, 5, 6], index=1)
                    name = st.text_input("Plan Name (optional)", placeholder="e.g., Weekly Weight Loss Plan")
                
                st.markdown("**Meal Slots**")
                meal_slots = []
                if meal_frequency >= 3:
                    meal_slots.append("BREAKFAST")
                if meal_frequency >= 4:
                    meal_slots.append("MORNING_SNACK")
                meal_slots.append("LUNCH")
                if meal_frequency >= 5:
                    meal_slots.append("EVENING_SNACK")
                meal_slots.append("DINNER")
                
                st.write(f"Meal slots: {', '.join(meal_slots)}")
                
                submitted = st.form_submit_button("🎯 Generate Meal Plan", type="primary")
                
                if submitted:
                    end_date = start_date + timedelta(days=days - 1)
                    
                    # Create meal plan
                    plan = MealPlan(
                        user_id=st.session_state.user_id,
                        start_date=start_date,
                        end_date=end_date,
                        status=MealPlanStatus.ACTIVE.value,
                        notes=name or ""
                    )
                    db.add(plan)
                    db.flush()
                    
                    # Generate meal plan items
                    meal_slots_list = ["BREAKFAST", "LUNCH", "DINNER"]
                    if meal_frequency >= 4:
                        meal_slots_list.insert(1, "MORNING_SNACK")
                    if meal_frequency >= 5:
                        meal_slots_list.insert(3, "EVENING_SNACK")
                    if meal_frequency >= 6:
                        meal_slots_list.insert(4, "MORNING_SNACK")
                        meal_slots_list.insert(5, "EVENING_SNACK")
                    
                    for day_idx in range(days):
                        for slot in meal_slots_list:
                            # For now, create empty slots - would use recommender in real impl
                            item = MealPlanItem(
                                meal_plan_id=db.query(type(None)).filter(False).first().id if False else None,
                                recipe_id=None,
                                meal_slot=slot,
                                day_index=day_idx,
                                servings=1.0
                            )
                            db.add(item)
                    
                    db.commit()
                    st.success(f"✅ Created {days}-day meal plan!")
                    st.session_state.current_page = "meal_plan_detail"
                    st.rerun()
        
        with tab2:
            st.subheader("Your Meal Plans")
            
            plans = db.query(MealPlan).filter(
                MealPlan.user_id == st.session_state.user_id
            ).order_by(MealPlan.created_at.desc()).all()
            
            if not plans:
                st.info("No meal plans yet. Create your first plan!")
            else:
                for plan in plans:
                    with st.expander(f"📅 {plan.name or 'Unnamed'} • {plan.start_date} to {plan.end_date} • {plan.status}"):
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.write(f"**Duration:** {(plan.end_date - plan.start_date).days + 1} days")
                            st.write(f"**Status:** {plan.status}")
                        with col2:
                            if st.button("📋 View", key=f"view_{plan.id}", use_container_width=True):
                                st.session_state.selected_plan_id = plan.id
                                st.session_state.current_page = "meal_plan_detail"
                                st.rerun()
                        with col3:
                            if plan.status == "ACTIVE" and st.button("⏹️ Complete", key=f"complete_{plan.id}", use_container_width=True):
                                plan.status = "COMPLETED"
                                db.commit()
                                st.rerun()
        
        with tab3:
            st.subheader("Weekly Overview")
            
            # Get active plan
            active_plan = db.query(MealPlan).filter(
                MealPlan.user_id == st.session_state.user_id,
                MealPlan.status == "ACTIVE",
                MealPlan.start_date <= date.today(),
                MealPlan.end_date >= date.today()
            ).first()
            
            if active_plan:
                st.write(f"**Active Plan:** {active_plan.name or 'Unnamed'} ({active_plan.start_date} to {active_plan.end_date})")
                
                # Weekly grid
                meal_slots = ["BREAKFAST", "MORNING_SNACK", "LUNCH", "EVENING_SNACK", "DINNER"]
                
                # Get items for this plan
                items = db.query(MealPlanItem).filter(
                    MealPlanItem.meal_plan_id == active_plan.id
                ).all()
                
                # Create grid
                days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                meal_slots = ["BREAKFAST", "MORNING_SNACK", "LUNCH", "EVENING_SNACK", "DINNER"]
                
                for day_idx in range(7):
                    with st.expander(f"{days[day_idx]} (Day {day_idx + 1})", expanded=day_idx == date.today().weekday()):
                        cols = st.columns(len(meal_slots))
                        for i, slot in enumerate(meal_slots):
                            with cols[i]:
                                meal_slot_badge(slot)
                                slot_items = [item for item in items if item.day_index == day_idx and item.meal_slot == slot]
                                if slot_items:
                                    for item in slot_items:
                                        if item.recipe_id:
                                            recipe = db.query(Recipe).filter(Recipe.id == item.recipe_id).first()
                                            if recipe:
                                                st.write(f"**{recipe.recipe_name}**")
                                                if item.is_completed:
                                                    st.success("✅ Done")
                                                else:
                                                    if st.button("✅", key=f"done_{item.id}", use_container_width=True):
                                        st.rerun()
                                else:
                                    st.info("Empty")
    
    finally:
        db.close()

if __name__ == "__main__":
    render()