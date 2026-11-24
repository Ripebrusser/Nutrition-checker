"""Meal Plan Detail page."""

import streamlit as st
from datetime import date, timedelta
from app.auth.dependencies import require_auth
from app.database.session import get_db
from app.database.models import MealPlan, MealPlanItem, Recipe, MealSlot
from app.components.forms import meal_slot_badge

def render():
    """Render the meal plan detail page."""
    require_auth()
    
    plan_id = st.session_state.get("selected_plan_id")
    if not plan_id:
        st.error("No meal plan selected")
        if st.button("Back to Meal Planner"):
            st.session_state.current_page = "meal_planner"
            st.rerun()
        return
    
    db = next(get_db())
    
    try:
        plan = db.query(MealPlan).filter(MealPlan.id == plan_id).first()
        
        if not plan:
            st.error("Meal plan not found")
            if st.button("Back to Meal Planner"):
                st.session_state.current_page = "meal_planner"
                st.rerun()
            return
        
        # Header
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.title(f"📋 {plan.name or 'Unnamed Plan'}")
        with col2:
            st.metric("Duration", f"{(plan.end_date - plan.start_date).days + 1} days")
        with col3:
            st.metric("Status", plan.status)
        
        st.caption(f"{plan.start_date} to {plan.end_date}")
        if plan.notes:
            st.info(plan.notes)
        
        st.markdown("---")
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if plan.status == "ACTIVE" and st.button("⏹️ Complete Plan", use_container_width=True):
                plan.status = "COMPLETED"
                db.commit()
                st.rerun()
        with col2:
            if plan.status == "DRAFT" and st.button("▶️ Activate", use_container_width=True):
                plan.status = "ACTIVE"
                db.commit()
                st.rerun()
        with col3:
            if st.button("✏️ Edit Plan", use_container_width=True):
                st.session_state.editing_plan = True
                st.rerun()
        with col4:
            if st.button("🗑️ Delete", type="secondary", use_container_width=True):
                st.session_state.confirm_delete_plan = True
        
        if st.session_state.get("confirm_delete_plan"):
            st.error("This will permanently delete the meal plan. Type 'DELETE' to confirm.")
            confirm = st.text_input("Type DELETE to confirm")
            if st.button("Confirm Delete", type="primary"):
                if confirm == "DELETE":
                    db.delete(plan)
                    db.commit()
                    st.success("Plan deleted")
                    st.session_state.current_page = "meal_planner"
                    st.rerun()
        
        st.markdown("---")
        
        # Plan editing
        if st.session_state.get("editing_plan"):
            with st.form("edit_plan_form"):
                new_name = st.text_input("Plan Name", value=plan.name or "")
                new_notes = st.text_area("Notes", value=plan.notes or "")
                if st.form_submit_button("💾 Save Changes"):
                    plan.name = new_name
                    plan.notes = new_notes
                    db.commit()
                    st.session_state.editing_plan = False
                    st.rerun()
                if st.form_submit_button("Cancel"):
                    st.session_state.editing_plan = False
                    st.rerun()
        
        st.markdown("---")
        
        # Weekly view
        days_count = (plan.end_date - plan.start_date).days + 1
        meal_slots = ["BREAKFAST", "MORNING_SNACK", "LUNCH", "EVENING_SNACK", "DINNER"]
        
        # Get all items for this plan
        items = db.query(MealPlanItem).filter(
            MealPlanItem.meal_plan_id == plan.id
        ).all()
        
        # Create lookup
        items_by_day_slot = {}
        for item in items:
            key = (item.day_index, item.meal_slot)
            if key not in items_by_day_slot:
                items_by_day_slot[key] = []
            items_by_day_slot[key].append(item)
        
        # Day tabs
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        tabs = st.tabs([f"{days[i % 7]} (Day {i+1})" for i in range(days_count)])
        
        for day_idx, tab in enumerate(tabs):
            with tab:
                st.markdown(f"### Day {day_idx + 1}")
                
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
                                            st.success("✅ Completed")
                                        else:
                                            if st.button("✅ Mark Done", key=f"done_{item.id}", use_container_width=True):
                                                item.is_completed = True
                                                item.completed_at = datetime.utcnow()
                                                db.commit()
                                                st.rerun()
                                            
                                            if st.button("🔄 Replace", key=f"replace_{item.id}", use_container_width=True):
                                                st.session_state.replacing_item_id = item.id
                                                st.session_state.current_page = "recipes"
                                                st.rerun()
                                            
                                            if st.button("🗑️ Remove", key=f"remove_{item.id}", use_container_width=True):
                                                db.delete(item)
                                                db.commit()
                                                st.rerun()
                                        else:
                                            st.write("Empty slot")
                        else:
                            st.info("Empty")
                            
                            # Add recipe button
                            if st.button("➕ Add Recipe", key=f"add_{day_idx}_{slot}", use_container_width=True):
                                st.session_state.adding_to_day = day_idx
                                st.session_state.adding_to_slot = slot
                                st.session_state.current_page = "recipes"
                                st.rerun()
        
        st.markdown("---")
        
        # Summary
        st.subheader("📊 Plan Summary")
        
        total_slots = days_count * len(meal_slots)
        filled_slots = sum(1 for item in items if item.recipe_id is not None)
        completed_slots = sum(1 for item in items if item.is_completed)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Slots", total_slots)
        with col2:
            st.metric("Filled", f"{filled_slots}/{total_slots}")
        with col3:
            st.metric("Completed", f"{completed_slots}/{filled_slots}" if filled_slots else "0/0")
        with col4:
            st.metric("Completion", f"{(completed_slots/filled_slots*100):.0f}%" if filled_slots else "0%")
        
        # Navigation
        st.markdown("---")
        if st.button("← Back to Meal Planner", use_container_width=True):
            st.session_state.current_page = "meal_planner"
            st.rerun()
    
    finally:
        db.close()

if __name__ == "__main__":
    render()