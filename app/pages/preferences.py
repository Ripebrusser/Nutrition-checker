"""Preferences page - User settings and preferences."""

import streamlit as st
from app.auth.dependencies import require_auth, get_user_profile, get_user_id
from app.database.session import get_db
from app.database.models import User, UserProfile
from app.components.forms import profile_form, dietary_preferences_form, nutritional_goals_form
from app.auth.password import validate_password_change, hash_password

def render():
    """Render the preferences page."""
    user = require_auth()
    profile = get_user_profile()
    user_id = get_user_id()
    
    st.title("⚙️ Preferences & Settings")
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 Profile", 
        "🥗 Dietary", 
        "🎯 Nutrition", 
        "🔐 Security"
    ])
    
    db = next(get_db())
    
    try:
        db_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        with tab1:
            st.subheader("Profile Information")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write(f"**Name:** {st.session_state.get('user_email', '').split('@')[0]}")
                st.write(f"**Email:** {st.session_state.user_email}")
            
            with col2:
                if st.button("📝 Edit Profile"):
                    st.session_state.editing_profile = True
                    st.rerun()
            
            if st.session_state.get("editing_profile", False):
                with st.form("profile_form"):
                    updated = profile_form(profile)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Save"):
                            db_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
                            if db_profile:
                                for key, value in updated.items():
                                    setattr(db_profile, key, value)
                                db.commit()
                                st.success("✅ Profile updated!")
                                st.session_state.editing_profile = False
                                st.rerun()
                    with col2:
                        if st.form_submit_button("Cancel"):
                            st.session_state.editing_profile = False
                            st.rerun()
        
        with tab2:
            st.subheader("Dietary Preferences")
            
            if st.button("📝 Edit Dietary Preferences"):
                st.session_state.editing_dietary = True
                st.rerun()
            
            if st.session_state.get("editing_dietary", False):
                with st.form("dietary_form"):
                    updated = dietary_preferences_form(profile)
                    if st.form_submit_button("💾 Save"):
                        db_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
                        if db_profile:
                            for key, value in updated.items():
                                setattr(db_profile, key, value)
                            db.commit()
                            st.success("✅ Dietary preferences updated!")
                            st.session_state.editing_dietary = False
                            st.rerun()
            
            # Display current
            st.markdown("**Current Preferences**")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Dietary Preference:** {profile.get('dietary_preference', 'OMNIVORE')}")
                st.write(f"**Allergies:** {', '.join(profile.get('allergies', [])) or 'None'}")
                st.write(f"**Exclusions:** {', '.join(profile.get('ingredient_exclusions', [])) or 'None'}")
            with col2:
                st.write(f"**Preferred Cuisines:** {', '.join(profile.get('cuisine_preferences', [])) or 'None'}")
                st.write(f"**Disliked:** {', '.join(profile.get('disliked_ingredients', [])) or 'None'}")
        
        with tab3:
            st.subheader("Nutrition Goals")
            
            if st.button("📝 Edit Nutrition Goals"):
                st.session_state.editing_nutrition = True
                st.rerun()
            
            if st.session_state.get("editing_nutrition", False):
                with st.form("nutrition_form"):
                    updated = nutritional_goals_form(profile)
                    if st.form_submit_button("💾 Save"):
                        db_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
                        if db_profile:
                            for key, value in updated.items():
                                setattr(db_profile, key, value)
                            db.commit()
                            st.success("✅ Nutrition goals updated!")
                            st.session_state.editing_nutrition = False
                            st.rerun()
            
            # Current goals display
            st.markdown("**Current Goals**")
            goals = profile.get('nutritional_goals', {})
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Weight Goal:** {goals.get('weight_goal', 'MAINTAIN')}")
                if goals.get('weight_goal') in ['LOSE', 'GAIN']:
                    st.write(f"Weekly Change: {goals.get('weight_change_rate_kg_per_week', 0.5)} kg")
            with col2:
                if goals.get('target_energy_kcal'):
                    st.write(f"Target Energy: {goals['target_energy_kcal']:.0f} kcal")
                if goals.get('target_protein_g'):
                    st.write(f"Target Protein: {goals['target_protein_g']:.1f} g")
        
        with tab4:
            st.subheader("Security Settings")
            
            st.markdown("### Change Password")
            with st.form("password_form"):
                current = st.text_input("Current Password", type="password")
                new = st.text_input("New Password", type="password")
                confirm = st.text_input("Confirm New Password", type="password")
                
                if st.form_submit_button("🔐 Update Password"):
                    if new != confirm:
                        st.error("Passwords do not match")
                    else:
                        from app.auth.password import validate_password_change, hash_password
                        db_user = db.query(User).filter(User.id == user_id).first()
                        is_valid, errors = validate_password_change(current, new, db_user.password_hash)
                        if not is_valid:
                            for e in errors:
                                st.error(e)
                        else:
                            user.password_hash = hash_password(new)
                            db.commit()
                            st.success("✅ Password updated!")
            
            st.markdown("---")
            
            st.markdown("### Data Management")
            st.warning("⚠️ Deleting your account will permanently remove all your data.")
            
            if st.button("🗑️ Request Account Deletion"):
                st.session_state.confirm_delete = True
            
            if st.session_state.get("confirm_delete"):
                st.error("This is permanent. Type 'DELETE' to confirm.")
                confirm = st.text_input("Type DELETE to confirm")
                if st.button("Confirm Deletion", type="primary"):
                    if confirm == "DELETE":
                        db.delete(st.session_state.get('user'))
                        db.commit()
                        st.success("Account deleted")
                        from app.auth.dependencies import logout_user
                        logout_user()
                        st.rerun()
    
    finally:
        db.close()

if __name__ == "__main__":
    render()