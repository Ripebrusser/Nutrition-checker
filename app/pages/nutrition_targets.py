"""Nutrition Targets page - Display calculated nutritional targets."""

import streamlit as st
from app.auth.dependencies import require_auth, get_user_profile
from app.nutrition_targets import NutritionTargetCalculator, calculate_weight_loss_targets, calculate_muscle_gain_targets
from app.profile_models import MacroDistributionMethod

def render():
    """Render the nutrition targets page."""
    user = require_auth()
    profile = get_user_profile()
    
    st.title("🎯 Nutrition Targets")
    st.markdown("---")
    
    # Check if profile has required data
    from app.profile_models import Anthropometrics, Sex, ActivityLevel
    anthro = Anthropometrics(
        height_cm=profile.get("height_cm"),
        weight_kg=profile.get("weight_kg"),
        age_years=profile.get("age_years"),
        sex=Sex(profile["sex"]) if profile.get("sex") else None
    )
    
    if not anthro.has_required_for_bmr():
        st.warning("⚠️ Please complete your profile (height, weight, age, sex) to calculate nutrition targets.")
        if st.button("Go to Profile", type="primary"):
            st.session_state.current_page = "profile"
            st.rerun()
        return
    
    # Calculate targets
    calculator = NutritionTargetCalculator()
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Your Targets", 
        "🥗 Meal Distribution", 
        "📊 Macro Breakdown", 
        "💊 Micronutrients"
    ])
    
    with tab1:
        st.subheader("Your Personalized Nutrition Targets")
        
        # Method selection
        col1, col2 = st.columns([1, 3])
        with col1:
            method = st.selectbox(
                "Calculation Method",
                ["ICMR_BALANCED", "HIGH_PROTEIN", "LOW_CARB", "KETOGENIC"],
                index=0,
                help="ICMR_BALANCED uses ICMR 2020 guidelines. HIGH_PROTEIN for weight loss/muscle."
            )
        
        with col2:
            st.info(f"""
            **Method:** {method}
            
            Based on your profile:
            - Height: {profile.get('height_cm', 'N/A')} cm
            - Weight: {profile.get('weight_kg', 'N/A')} kg
            - Age: {profile.get('age_years', 'N/A')} years
            - Sex: {profile.get('sex', 'N/A')}
            - Activity: {profile.get('activity_level', 'SEDENTARY')}
            - Goal: {profile.get('weight_goal', 'MAINTAIN')}
            """)
        
        # Calculate targets
        from app.nutrition_targets import calculate_user_nutrition_targets
        from app.profile_models import MacroDistributionMethod
        method_enum = MacroDistributionMethod(method)
        
        try:
            targets = calculate_user_nutrition_targets(
                profile, 
                macro_method=method_enum
            )
            
            # Display targets
            st.markdown("### Daily Nutrition Targets")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Energy", f"{targets.macros.energy_kcal:.0f} kcal")
            with col2:
                st.metric("Protein", f"{targets.macros.protein_g:.1f} g", 
                         f"{targets.macros.protein_pct:.0f}%")
            with col3:
                st.metric("Carbs", f"{targets.macros.carbohydrate_g:.1f} g",
                         f"{targets.macros.carbohydrate_pct:.0f}%")
            with col4:
                st.metric("Fat", f"{targets.macros.fat_g:.1f} g",
                         f"{targets.macros.fat_pct:.0f}%")
            with col5:
                st.metric("Fibre", f"{targets.macros.fibre_g:.1f} g")
            
            # Per-meal breakdown
            st.markdown("---")
            st.subheader("Per-Meal Targets")
            
            for meal, nutrients in targets.meal_targets.items():
                with st.expander(f"🍽️ {meal.replace('_', ' ').title()} ({nutrients.get('energy_kcal', 0):.0f} kcal)"):
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.metric("Energy", f"{nutrients.get('energy_kcal', 0):.0f} kcal")
                    with col2:
                        st.metric("Protein", f"{nutrients.get('protein_g', 0):.1f} g")
                    with col3:
                        st.metric("Carbs", f"{nutrients.get('carbohydrate_g', 0):.1f} g")
                    with col4:
                        st.metric("Fat", f"{nutrients.get('fat_g', 0):.1f} g")
                    with col5:
                        st.metric("Fibre", f"{nutrients.get('fibre_g', 0):.1f} g")
            
            # Warnings
            if targets.macros.warnings:
                st.warning("⚠️ " + "; ".join(targets.macros.warnings))
            
            if targets.macros.notes:
                st.info("ℹ️ " + "; ".join(targets.macros.notes))
                
        except Exception as e:
            st.error(f"Error calculating targets: {e}")
    
    with tab2:
        st.subheader("Meal Distribution")
        
        from app.reference_values import get_meal_distribution
        from app.profile_models import MealFrequency, get_meal_distribution
        
        freq = MealFrequency(profile.get("meal_frequency", 3))
        dist = get_meal_distribution(freq)
        
        st.write("**Energy Distribution by Meal**")
        for meal, pct in dist.items():
            if pct > 0:
                kcal = targets.macros.energy_kcal * pct
                st.progress(pct, text=f"{meal.replace('_', ' ').title()}: {pct:.0%} ({kcal:.0f} kcal)")
        
        st.markdown("---")
        st.info("""
        **Meal Frequency Guide:**
        - **3 meals**: Breakfast 30%, Lunch 40%, Dinner 30%
        - **4 meals**: Breakfast 25%, Lunch 35%, Snack 15%, Dinner 25%
        - **5 meals**: Breakfast 25%, Morning Snack 10%, Lunch 35%, Evening Snack 10%, Dinner 20%
        - **6 meals**: Breakfast 20%, Morning Snack 10%, Lunch 30%, Mid-Afternoon 10%, Evening Snack 10%, Dinner 20%
        """)
    
    with tab3:
        st.subheader("Macronutrient Breakdown")
        
        # Macro distribution chart
        import plotly.express as px
        
        macros = {
            "Protein": targets.macros.protein_pct,
            "Fat": targets.macros.fat_pct,
            "Carbohydrate": targets.macros.carbohydrate_pct
        }
        
        fig = px.pie(
            values=list(macros.values()),
            names=list(macros.keys()),
            title="Macronutrient Distribution",
            color_discrete_sequence=["#FF6B6B", "#4ECDC4", "#45B7D1"]
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # ICMR ranges
        st.subheader("ICMR 2020 Recommended Ranges")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Protein", "10-20%", f"{targets.macros.protein_pct:.1f}%")
        with col2:
            st.metric("Fat", "20-30%", f"{targets.macros.fat_pct:.1f}%")
        with col3:
            st.metric("Carbohydrate", "50-65%", f"{targets.macros.carbohydrate_pct:.1f}%")
        
        # Check if within ranges
        if not (10 <= targets.macros.protein_pct <= 20):
            st.warning("⚠️ Protein percentage outside ICMR range (10-20%)")
        if not (20 <= targets.macros.fat_pct <= 30):
            st.warning("⚠️ Fat percentage outside ICMR range (20-30%)")
        if not (50 <= targets.macros.carbohydrate_pct <= 65):
            st.warning("⚠️ Carbohydrate percentage outside ICMR range (50-65%)")
    
    with tab4:
        st.subheader("Micronutrient Targets (ICMR 2020 RDA)")
        
        micros = targets.micros
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Sodium", f"{micros.sodium_mg:.0f} mg")
            st.metric("Potassium", f"{micros.potassium_mg:.0f} mg")
            st.metric("Calcium", f"{micros.calcium_mg:.0f} mg")
            st.metric("Iron", f"{micros.iron_mg:.1f} mg")
        with col2:
            st.metric("Zinc", f"{micros.zinc_mg:.1f} mg")
            st.metric("Vitamin A", f"{micros.vitamin_a_mcg:.0f} mcg RAE")
            st.metric("Vitamin D", f"{micros.vitamin_d_iu:.0f} IU")
            st.metric("Vitamin B12", f"{micros.vitamin_b12_mcg:.1f} mcg")
            st.metric("Folate", f"{micros.folate_mcg:.0f} mcg DFE")
            st.metric("Vitamin C", f"{micros.vitamin_c_mcg/1000:.0f} mg")
        
        st.caption("Source: ICMR-NIN 2020 RDA for Indians. Values may vary based on age, sex, and physiological state.")

if __name__ == "__main__":
    render()