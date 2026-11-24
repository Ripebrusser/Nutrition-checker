"""Home page - Landing page."""

import streamlit as st

def render():
    """Render the home/landing page."""
    st.title("🥗 Indian Nutrition & Diet Planner")
    st.markdown("---")
    
    # Hero section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## Personalized Indian Meal Planning with Scientific Nutrition
        
        Discover healthy Indian recipes tailored to your unique nutritional needs, 
        dietary preferences, and health goals. Our platform combines:
        
        🍽️ **6,865+ Authentic Indian Recipes** - Curated from diverse regional cuisines
        
        🧬 **Science-Based Nutrition** - ICMR 2020 dietary guidelines & Mifflin-St Jeor equations
        
        🌱 **Dietary Intelligence** - Vegan, Vegetarian, Jain, Jain, Allergen-aware filtering
        
        📊 **Smart Meal Planning** - Daily & weekly plans with nutritional optimization
        
        🔬 **Evidence-Based** - Built on IFCT 2017 food composition data
        """)
        
        if st.button("🚀 Get Started - Create Your Profile", type="primary", use_container_width=True):
            st.session_state.current_page = "register"
            st.rerun()
        
        st.markdown("---")
        st.markdown("""
        ### How It Works
        
        1. **Create Profile** - Enter your health metrics, dietary preferences & goals
        2. **Get Nutrition Targets** - Personalized calorie, protein, carb & fat targets
        3. **Discover Recipes** - Browse 6,865+ Indian recipes with dietary filters
        4. **Get Recommendations** - AI-powered personalized recipe suggestions
        5. **Build Meal Plans** - Daily & weekly plans with nutritional tracking
        6. **Track Progress** - Monitor meals completed & nutritional intake
        """)
    
    with col2:
        st.image("https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400", 
                 caption="Healthy Indian Cuisine")
        
        st.markdown("---")
        
        # Quick stats
        st.metric("Recipes", "6,865+")
        st.metric("Cuisines", "75")
        st.metric("Nutrients Tracked", "9")
        st.metric("IFCT Foods", "528")
        
        st.markdown("---")
        
        # Features
        st.markdown("""
        ### ✨ Key Features
        
        **🍽️ Recipe Discovery**
        - Search by ingredients, cuisine, course, diet
        - Filter by prep time, dietary needs
        - View ingredient lists & instructions
        
        **🎯 Personalized Recommendations**
        - TF-IDF content-based similarity
        - Dietary constraint enforcement
        - Meal-slot appropriate suggestions
        
        **📅 Smart Meal Planning**
        - Daily & weekly plans
        - Nutritional target tracking
        - Variety & repetition controls
        
        **🔬 Nutrition Science**
        - IFCT 2017 food composition data
        - 9 nutrients per 100g edible portion
        - Edible portion adjustments
        - Missing value transparency
        """)
        
        st.info("""
        ⚠️ **Current Status**: Nutrition calculations require approved ingredient mappings. 
        Currently 0 approved mappings (Gate C authorization pending). 
        The interface is fully functional - nutrition data will appear once mappings are approved.
        """)

if __name__ == "__main__":
    render()