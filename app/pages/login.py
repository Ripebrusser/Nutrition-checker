"""Login page."""

import streamlit as st
from app.auth.dependencies import login_user
from app.auth.password import verify_password
from app.database.session import get_db
from app.database.models import User

def render():
    """Render the login page."""
    st.title("🔐 Login")
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
        ### Welcome Back
        
        Sign in to access your personalized nutrition dashboard, 
        meal plans, and recipe recommendations.
        
        Don't have an account? [Register here](#) 
        (navigate to the Register page).
        """)
        
        st.image("https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=400",
                 caption="Healthy Indian Meals")
    
    with col2:
        st.markdown("### Sign In")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            
            submitted = st.form_submit_button("🔐 Sign In", type="primary", use_container_width=True)
            
            if submitted:
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    # Authenticate user
                    db = next(get_db())
                    try:
                        user = db.query(User).filter(User.email == email).first()
                        
                        if user and verify_password(password, user.password_hash):
                            # Login successful
                            from app.auth.session import create_user_token
                            token = create_user_token(user.id, user.email, "USER")
                            
                            from app.auth.dependencies import login_user
                            login_user(user.id, user.email, token)
                            
                            st.success("✅ Login successful!")
                            st.session_state.current_page = "dashboard"
                            st.rerun()
                        else:
                            st.error("❌ Invalid email or password")
                    finally:
                        db.close()
            
            st.markdown("---")
            st.caption("Demo credentials: Use any registered email/password")

if __name__ == "__main__":
    render()