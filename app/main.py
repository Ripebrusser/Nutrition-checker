"""Main entry point for the Streamlit application."""

import streamlit as st
from app.config import settings
from app.database.session import init_db, init_recipe_data
from app.auth.dependencies import init_auth_state, is_authenticated, logout_user, get_user_profile

# Page configuration
st.set_page_config(
    page_title=settings.APP_NAME,
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Initialize database
init_db()
init_recipe_data()

# Initialize authentication state
from app.auth.dependencies import init_auth_state
init_auth_state()

# Custom CSS
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .stAlert {
        border-radius: 0.5rem;
    }
    .recipe-card {
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .meal-slot {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    .nutrition-complete { background-color: #d4edda; color: #155724; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.85em; }
    .nutrition-partial { background-color: #fff3cd; color: #856404; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.85em; }
    .nutrition-unavailable { background-color: #e2e3e5; color: #383d41; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.85em; }
    .nutrition-badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.85em; font-weight: 500; }
    .meal-slot-header { font-weight: 600; margin-bottom: 0.5rem; }
    .recipe-card { border: 1px solid #e0e0e0; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem; transition: box-shadow 0.2s; }
    .recipe-card:hover { box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# Initialize database
if 'db_initialized' not in st.session_state:
    init_db()
    init_recipe_data()
    st.session_state.db_initialized = True

# Page configuration
PAGES = {
    "home": {"title": "Home", "icon": "🏠", "path": "home", "auth_required": False},
    "login": {"title": "Login", "icon": "🔐", "path": "login", "auth_required": False},
    "register": {"title": "Register", "icon": "📝", "path": "register", "auth_required": False},
    "dashboard": {"title": "Dashboard", "icon": "📊", "path": "dashboard", "auth_required": True},
    "profile": {"title": "Profile", "icon": "👤", "path": "profile", "auth_required": True},
    "nutrition_targets": {"title": "Nutrition Targets", "icon": "🎯", "path": "nutrition_targets", "auth_required": True},
    "recipes": {"title": "Recipes", "icon": "🍲", "path": "recipes", "auth_required": True},
    "recipe_detail": {"title": "Recipe Detail", "icon": "📋", "path": "recipe_detail", "auth_required": True},
    "recommendations": {"title": "Recommendations", "icon": "✨", "path": "recommendations", "auth_required": True},
    "meal_planner": {"title": "Meal Planner", "icon": "📅", "path": "meal_planner", "auth_required": True},
    "meal_plan_detail": {"title": "Meal Plan", "icon": "📋", "path": "meal_plan_detail", "auth_required": True},
    "nutrition_breakdown": {"title": "Nutrition Breakdown", "icon": "🔬", "path": "nutrition_breakdown", "auth_required": True},
    "preferences": {"title": "Preferences", "icon": "⚙️", "path": "preferences", "auth_required": True},
    "history": {"title": "History", "icon": "📜", "path": "history", "auth_required": True},
}

def render_sidebar():
    """Render the sidebar navigation."""
    with st.sidebar:
        st.title("🥗 Indian Nutrition & Diet Planner")
        st.markdown("---")
        
        # Auth status
        from app.auth.dependencies import is_authenticated, get_user_id, logout_user
        if is_authenticated():
            st.success(f"👤 Logged in")
            if st.button("🚪 Logout", use_container_width=True):
                logout_user()
                st.rerun()
            st.markdown("---")
        else:
            st.info("🔒 Please log in")
            st.markdown("---")
        
        # Navigation
        st.subheader("Navigation")
        
        # Show pages based on auth status
        for key, page in PAGES.items():
            if page.get("auth_required", False) and not is_authenticated():
                continue
            if page["path"] == "login" and is_authenticated():
                continue
            if page["path"] == "register" and is_authenticated():
                continue
            
            if st.button(f"{page['icon']} {page['title']}", key=f"nav_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.rerun()
        
        st.markdown("---")
        
        # Quick stats if authenticated
        if is_authenticated():
            st.subheader("Quick Stats")
            from app.database.session import get_db
            from app.database.models import MealPlan, SavedRecipe, Recipe
            from app.auth.dependencies import get_user_id
            
            db = next(get_db())
            try:
                user_id = get_user_id()
                if user_id:
                    meal_plans_count = db.query(MealPlan).filter(
                        MealPlan.user_id == user_id
                    ).count()
                    saved_recipes_count = db.query(SavedRecipe).filter(
                        SavedRecipe.user_id == user_id
                    ).count()
                    
                    st.metric("Meal Plans", meal_plans_count)
                    st.metric("Saved Recipes", saved_recipes_count)
            finally:
                db.close()

def render_page(page_key: str):
    """Render the selected page."""
    page_map = {
        "home": "app.pages.home",
        "login": "app.pages.login",
        "register": "app.pages.register",
        "dashboard": "app.pages.dashboard",
        "profile": "app.pages.profile",
        "nutrition_targets": "app.pages.nutrition_targets",
        "recipes": "app.pages.recipes",
        "recipe_detail": "app.pages.recipe_detail",
        "recommendations": "app.pages.recommendations",
        "meal_planner": "app.pages.meal_planner",
        "meal_plan_detail": "app.pages.meal_plan_detail",
        "nutrition_breakdown": "app.pages.nutrition_breakdown",
        "preferences": "app.pages.preferences",
        "history": "app.pages.history",
    }
    
    if page_key not in page_map:
        st.error(f"Page '{page_key}' not found")
        return
    
    # Dynamic import
    module_name = page_map[page_key]
    module = __import__(module_name, fromlist=['render'])
    module.render()

def main():
    """Main application entry point."""
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    # Render sidebar
    render_sidebar()
    
    # Render current page
    current_page = st.session_state.current_page
    render_page(current_page)

if __name__ == "__main__":
    main()