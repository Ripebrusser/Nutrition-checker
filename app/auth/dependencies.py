"""Authentication dependencies for Streamlit."""

import streamlit as st
from typing import Optional
from app.database.models import User
from app.database.session import get_db
from app.auth.session_manager import SessionManager
from app.auth.session import decode_token


def init_auth_state():
    """Initialize authentication state in session."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None


def get_current_user() -> Optional[User]:
    """Get current authenticated user from session state."""
    init_auth_state()
    
    if not st.session_state.authenticated or not st.session_state.user_id:
        return None
    
    db = next(get_db())
    try:
        user = db.query(User).filter(User.id == st.session_state.user_id).first()
        return user
    finally:
        db.close()


def require_auth() -> User:
    """Require authentication - raises error if not authenticated."""
    user = get_current_user()
    if not user:
        st.error("🔒 Please log in to access this page")
        st.stop()
    return user


def login_user(user_id: int, email: str, token: str) -> None:
    """Log in a user by setting session state."""
    st.session_state.authenticated = True
    st.session_state.user_id = user_id
    st.session_state.user_email = email
    st.session_state.access_token = token
    st.session_state.authenticated = True
    
    # Load user profile
    db = next(get_db())
    try:
        from app.database.models import UserProfile
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if profile:
            st.session_state.user_profile = {
                "height_cm": profile.height_cm,
                "weight_kg": profile.weight_kg,
                "age_years": profile.age_years,
                "sex": profile.sex,
                "dietary_preference": profile.dietary_preference,
                "allergies": profile.allergies or [],
                "ingredient_exclusions": profile.ingredient_exclusions or [],
                "cuisine_preferences": profile.cuisine_preferences or [],
                "cuisine_exclusions": profile.cuisine_exclusions or [],
                "disliked_ingredients": profile.disliked_ingredients or [],
                "religious_restrictions": profile.religious_restrictions or [],
                "medical_conditions": profile.medical_conditions or [],
                "target_energy_kcal": profile.target_energy_kcal,
                "target_protein_g": profile.target_protein_g,
                "target_carbohydrate_g": profile.target_carbohydrate_g,
                "target_fat_g": profile.target_fat_g,
                "target_fibre_g": profile.target_fibre_g,
                "target_sodium_mg": profile.target_sodium_mg,
                "weight_goal": profile.weight_goal,
                "weight_change_rate_kg_per_week": profile.weight_change_rate_kg_per_week,
                "activity_level": profile.activity_level,
                "meal_frequency": profile.meal_frequency,
                "preferred_meal_times": profile.preferred_meal_times or {},
                "cooking_skill": profile.cooking_skill,
                "budget_constraint": profile.budget_constraint,
                "time_constraint_minutes": profile.time_constraint_minutes,
            }
    finally:
        db.close()


def logout_user() -> None:
    """Log out the current user."""
    # Invalidate token in database
    if st.session_state.get("access_token"):
        from app.auth.session import decode_token
        from app.database.session import get_db
        from app.database.models import Session as SessionModel
        
        token = st.session_state.access_token
        payload = decode_token(token)
        if payload:
            session_id = payload.get("session_id")
            if session_id:
                db = next(get_db())
                try:
                    session = db.query(SessionModel).filter(
                        SessionModel.id == session_id
                    ).first()
                    if session:
                        session.is_active = False
                        db.commit()
                finally:
                    db.close()
    
    # Clear session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def get_access_token() -> Optional[str]:
    """Get current access token."""
    init_auth_state()
    return st.session_state.get("access_token")


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    init_auth_state()
    return st.session_state.get("authenticated", False)


def get_user_id() -> Optional[int]:
    """Get current user ID."""
    init_auth_state()
    return st.session_state.get("user_id")


def get_user_profile() -> Optional[dict]:
    """Get current user profile from session state."""
    init_auth_state()
    return st.session_state.get("user_profile")