"""Registration page."""

import streamlit as st
from app.auth.password import hash_password, validate_password_strength
from app.database.session import get_db
from app.database.models import User
from app.auth.session import create_user_token
from app.auth.dependencies import login_user

def render():
    """Render the registration page."""
    st.title("📝 Create Account")
    st.markdown("---")
    
    # Check if already authenticated
    from app.auth.dependencies import is_authenticated
    if is_authenticated():
        st.info("You are already logged in.")
        if st.button("Go to Dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### Join Indian Nutrition & Diet Planner
        
        Create your personalized nutrition profile to get:
        
        🎯 **Personalized Nutrition Targets** - Calories, protein, carbs, fat, fibre
        
        🍽️ **Personalized Recipe Recommendations** - Based on your preferences
        
        📅 **Smart Meal Planning** - Daily & weekly meal plans
        
        🔬 **Evidence-Based Nutrition** - ICMR 2020 guidelines & IFCT data
        
        🛡️ **Dietary Safety** - Allergen & restriction filtering
        """)
        
        st.image("https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=400",
                 caption="Start Your Nutrition Journey")
    
    with col2:
        st.markdown("### Create Your Account")
        
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name", placeholder="John")
            with col2:
                last_name = st.text_input("Last Name", placeholder="Doe")
            
            email = st.text_input("Email", placeholder="your@email.com")
            
            col1, col2 = st.columns(2)
            with col1:
                password = st.text_input("Password", type="password", 
                                        help="Min 8 chars, upper, lower, digit, special char")
            with col2:
                confirm_password = st.text_input("Confirm Password", type="password")
            
            st.markdown("---")
            
            # Quick profile setup (optional)
            st.markdown("**Quick Profile Setup (Optional)**")
            col1, col2 = st.columns(2)
            with col1:
                height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.1)
                weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.1)
            with col2:
                age = st.number_input("Age", min_value=1, max_value=120, value=30)
                sex = st.selectbox("Sex", ["MALE", "FEMALE"])
            
            dietary_pref = st.selectbox(
                "Dietary Preference",
                ["OMNIVORE", "VEGETARIAN", "VEGAN", "EGGETARIAN", "JAIN", "PESCATARIAN", "FLEXITARIAN"],
                index=0
            )
            
            activity = st.selectbox(
                "Activity Level",
                ["SEDENTARY", "LIGHTLY_ACTIVE", "MODERATELY_ACTIVE", "VERY_ACTIVE", "EXTREMELY_ACTIVE"],
                index=0,
                help="SEDENTARY: Little/no exercise | LIGHTLY: 1-3 days/week | MODERATELY: 3-5 days/week | VERY: 6-7 days/week | EXTREME: Physical job/hard exercise"
            )
            
            submitted = st.form_submit_button("🚀 Create Account", type="primary", use_container_width=True)
            
            if submitted:
                # Validation
                errors = []
                if not first_name or not last_name:
                    errors.append("First and last name are required")
                if not email:
                    errors.append("Email is required")
                if not password:
                    errors.append("Password is required")
                elif password != confirm_password:
                    errors.append("Passwords do not match")
                else:
                    is_valid, errors = validate_password_strength(password)
                    if not is_valid:
                        errors.extend(errors)
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Create user
                    db = next(get_db())
                    try:
                        # Check if email exists
                        existing = db.query(User).filter(User.email == email).first()
                        if existing:
                            st.error("Email already registered. Please login or use a different email.")
                        else:
                            # Create user
                            password_hash = hash_password(password)
                            user = User(
                                email=email,
                                password_hash=password_hash,
                                full_name=f"{first_name} {last_name}".strip(),
                                role="USER",
                                is_active=True
                            )
                            db.add(user)
                            db.flush()  # Get user ID
                            
                            # Create profile
                            from app.database.models import UserProfile, Sex, ActivityLevel, DietaryPreference, WeightGoal, MealFrequency
                            profile = UserProfile(
                                user_id=user.id,
                                height_cm=height,
                                weight_kg=weight,
                                age_years=age,
                                sex=Sex(sex),
                                dietary_profile={"preference": dietary_pref},
                                nutritional_goals={"weight_goal": "MAINTAIN"},
                                lifestyle={
                                    "activity_level": ActivityLevel(activity),
                                    "meal_frequency": 3,
                                    "cooking_skill": "INTERMEDIATE"
                                }
                            )
                            db.add(profile)
                            db.commit()
                            
                            # Create token and login
                            from app.auth.session import create_user_token
                            token = create_user_token(user.id, user.email, "USER")
                            login_user(user.id, user.email, token)
                            
                            st.success("🎉 Account created successfully!")
                            st.session_state.current_page = "dashboard"
                            st.rerun()
                            
                    except Exception as e:
                        db.rollback()
                        st.error(f"Registration failed: {str(e)}")
                    finally:
                        db.close()

if __name__ == "__main__":
    render()