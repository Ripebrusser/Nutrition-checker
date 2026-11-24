"""Profile page - User profile management."""

import streamlit as st
from datetime import date
from app.auth.dependencies import require_auth, get_user_profile
from app.database.session import get_db
from app.database.models import User, UserProfile
from app.components.forms import profile_form, dietary_preferences_form, nutritional_goals_form
from app.auth.password import validate_password_change, hash_password

def render():
    """Render the profile page."""
    user = require_auth()
    profile = get_user_profile()
    
    st.title("👤 My Profile")
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Basic Info", 
        "🥗 Dietary Preferences", 
        "🎯 Nutrition Goals", 
        "🔐 Security", 
        "📊 Summary"
    ])
    
    db = next(get_db())
    
    try:
        # Get full profile from DB
        db_profile = db.query(UserProfile).filter(UserProfile.user_id == st.session_state.user_id).first()
        
        with tab1:
            st.subheader("Basic Information")
            
            # Display current info
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write(f"**Name:** {st.session_state.get('user_email', '').split('@')[0]}")
                st.write(f"**Email:** {st.session_state.user_email}")
            
            with col2:
                if st.button("📝 Edit Basic Info"):
                    st.session_state.editing_basic = True
                    st.rerun()
            
            if st.session_state.get("editing_basic", False):
                with st.form("basic_info_form"):
                    updated = profile_form(profile)
                    if st.form_submit_button("💾 Save Changes"):
                        # Update database
                        db_profile = db.query(UserProfile).filter(UserProfile.user_id == st.session_state.user_id).first()
                        if db_profile:
                            for key, value in updated.items():
                                setattr(db_profile, key, value)
                            db.commit()
                            st.success("✅ Basic info updated!")
                            st.session_state.editing_basic = False
                            st.rerun()
                        if st.form_submit_button("Cancel"):
                            st.session_state.editing_basic = False
                            st.rerun()
        
        with tab2:
            st.subheader("Dietary Preferences & Restrictions")
            
            if st.button("📝 Edit Dietary Preferences"):
                st.session_state.editing_dietary = True
                st.rerun()
            
            if st.session_state.get("editing_dietary", False):
                with st.form("dietary_form"):
                    updated = dietary_preferences_form(profile)
                    if st.form_submit_button("💾 Save Dietary Preferences"):
                        db_profile = db.query(UserProfile).filter(UserProfile.user_id == st.session_state.user_id).first()
                        if db_profile:
                            for key, value in updated.items():
                                setattr(db_profile, key, value)
                            db.commit()
                            st.success("✅ Dietary preferences updated!")
                            st.session_state.editing_dietary = False
                            st.rerun()
            
            # Display current preferences
            st.markdown("**Current Preferences**")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Dietary Preference:** {profile.get('dietary_preference', 'OMNIVORE')}")
                st.write(f"**Allergies:** {', '.join(profile.get('allergies', [])) or 'None'}")
                st.write(f"**Exclusions:** {', '.join(profile.get('ingredient_exclusions', [])) or 'None'}")
            with col2:
                st.write(f"**Preferred Cuisines:** {', '.join(profile.get('cuisine_preferences', [])) or 'None'}")
                st.write(f"**Disliked Ingredients:** {', '.join(profile.get('disliked_ingredients', [])) or 'None'}")
        
        with tab3:
            st.subheader("Nutritional Goals")
            
            if st.button("📝 Edit Nutrition Goals"):
                st.session_state.editing_nutrition = True
                st.rerun()
            
            if st.session_state.get("editing_nutrition", False):
                with st.form("nutrition_form"):
                    updated = nutritional_goals_form(profile)
                    if st.form_submit_button("💾 Save Nutrition Goals"):
                        db_profile = db.query(UserProfile).filter(UserProfile.user_id == st.session_state.user_id).first()
                        if db_profile:
                            for key, value in updated.items():
                                setattr(db_profile, key, value)
                            db.commit()
                            st.success("✅ Nutrition goals updated!")
                            st.session_state.editing_nutrition = False
                            st.rerun()
            
            # Display current goals
            st.markdown("**Current Goals**")
            goals = profile.get('nutritional_goals', {})
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Weight Goal:** {goals.get('weight_goal', 'MAINTAIN')}")
                if goals.get('weight_goal') in ['LOSE', 'GAIN']:
                    st.write(f"**Weekly Change:** {goals.get('weight_change_rate_kg_per_week', 0.5)} kg")
            with col2:
                if goals.get('target_energy_kcal'):
                    st.write(f"**Target Energy:** {goals['target_energy_kcal']:.0f} kcal")
                if goals.get('target_protein_g'):
                    st.write(f"**Target Protein:** {goals['target_protein_g']:.1f} g")
        
        with tab4:
            st.subheader("Security Settings")
            
            st.markdown("### Change Password")
            with st.form("password_form"):
                current_password = st.text_input("Current Password", type="password")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                
                if st.form_submit_button("🔐 Update Password"):
                    if not new_password or new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        is_valid, errors = validate_password_change(
                            current_password, new_password, 
                            db.query(User).filter(User.id == st.session_state.user_id).first().password_hash
                        )
                        if not is_valid:
                            for error in errors:
                                st.error(error)
                        else:
                            from app.auth.password import hash_password
                            user = db.query(User).filter(User.id == st.session_state.user_id).first()
                            user.password_hash = hash_password(new_password)
                            db.commit()
                            st.success("✅ Password updated!")
            
            st.markdown("---")
            
            st.markdown("### Danger Zone")
            st.warning("⚠️ Deleting your account will permanently remove all your data including profiles, meal plans, saved recipes, and history.")
            
            if st.button("🗑️ Delete Account", type="secondary"):
                st.session_state.confirm_delete = True
            
            if st.session_state.get("confirm_delete"):
                st.error("This action cannot be undone. Type 'DELETE' to confirm.")
                confirm = st.text_input("Type DELETE to confirm")
                if st.button("Confirm Delete", type="primary"):
                    if confirm == "DELETE":
                        db.delete(st.session_state.user)
                        db.commit()
                        st.success("Account deleted")
                        logout_user()
                        st.rerun()
                    else:
                        st.error("Confirmation text does not match")
        
        with tab5:
            st.subheader("Profile Summary")
            
            # Profile completion
            completion = 0
            fields = [
                ("Height", profile.get("height_cm")),
                ("Weight", profile.get("weight_kg")),
                ("Age", profile.get("age_years")),
                ("Sex", profile.get("sex")),
                ("Activity Level", profile.get("activity_level")),
                ("Dietary Preference", profile.get("dietary_preference")),
            ]
            
            completed = sum(1 for _, v in fields if v is not None)
            total = len(fields)
            completion_pct = (completed / total) * 100
            
            st.progress(completion_pct / 100)
            st.write(f"Profile Completion: {completion_pct:.0f}% ({completed}/{total} fields)")
            
            # Nutritional readiness
            from app.auth.dependencies import validate_for_nutrition
            from app.profile_models import UserProfile as UPModel
            
            if st.session_state.get("user_profile"):
                from app.profile_models import Anthropometrics, Sex, ActivityLevel
                anthro = Anthropometrics(
                    height_cm=profile.get("height_cm"),
                    weight_kg=profile.get("weight_kg"),
                    age_years=profile.get("age_years"),
                    sex=Sex(profile["sex"]) if profile.get("sex") else None
                )
                if anthro.has_required_for_bmr():
                    st.success("✅ Ready for nutrition calculations")
                else:
                    st.warning("⚠️ Complete anthropometrics for nutrition calculations")
            
            st.markdown("---")
            st.caption("Data is stored securely and never shared without your consent.")
    
    finally:
        db.close()

if __name__ == "__main__":
    render()