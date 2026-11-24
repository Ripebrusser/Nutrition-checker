"""Nutrition Breakdown page - Detailed nutrition analysis."""

import streamlit as st
import pandas as pd
from app.auth.dependencies import require_auth
from app.database.session import get_db
from app.database.models import Recipe

def render():
    """Render the nutrition breakdown page."""
    require_auth()
    
    st.title("🔬 Nutrition Breakdown")
    st.markdown("---")
    
    st.info("""
    **Nutrition Data Availability**
    
    Currently, there are **0 approved ingredient mappings** (Gate C authorization pending).
    Therefore, detailed nutrition calculations are unavailable for all recipes.
    
    This interface is ready and will display nutrition data once approved mappings are available.
    """)
    
    st.markdown("---")
    
    db = next(get_db())
    
    try:
        # Nutrition status overview
        st.subheader("📊 Nutrition Data Coverage")
        
        total = db.query(Recipe).count()
        complete = db.query(Recipe).filter(Recipe.nutrition_status == "COMPLETE").count()
        partial = db.query(Recipe).filter(Recipe.nutrition_status == "PARTIAL").count()
        unavailable = db.query(Recipe).filter(Recipe.nutrition_status == "UNAVAILABLE").count()
        no_mapped = db.query(Recipe).filter(Recipe.nutrition_status == "NO_MAPPED_INGREDIENTS").count()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Complete", complete, f"{complete/total*100:.1f}%")
        with col2:
            st.metric("Partial", partial, f"{partial/total*100:.1f}%")
        with col3:
            st.metric("Unavailable", unavailable, f"{unavailable/total*100:.1f}%")
        with col4:
            st.metric("No Mappings", no_mapped, f"{no_mapped/total*100:.1f}%")
        
        st.markdown("---")
        
        # Nutrient availability
        st.subheader("🧪 Nutrient Availability in IFCT Data")
        
        # IFCT nutrient coverage
        nutrient_info = {
            "Moisture": {"available": 528, "total": 528, "unit": "g"},
            "Protein": {"available": 528, "total": 528, "unit": "g"},
            "Ash": {"available": 528, "total": 528, "unit": "g"},
            "Fat": {"available": 528, "total": 528, "unit": "g"},
            "Total Fibre": {"available": 306, "total": 528, "unit": "g"},
            "Insoluble Fibre": {"available": 306, "total": 528, "unit": "g"},
            "Soluble Fibre": {"available": 306, "total": 528, "unit": "g"},
            "Available Carb": {"available": 306, "total": 528, "unit": "g"},
            "Energy (kJ)": {"available": 528, "total": 528, "unit": "kJ"},
        }
        
        df = pd.DataFrame([
            {"Nutrient": k, "Available": v["available"], "Total": v["total"], 
             "Coverage": f"{v['available']/v['total']*100:.0f}%", "Unit": v["unit"]}
            for k, v in nutrient_info.items()
        ])
        
        st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
        
        # Edible portion coverage
        st.subheader("🥬 Edible Portion Factor Coverage")
        
        st.info("""
        **Edible Portion Factors** convert as-purchased weight to edible weight.
        
        Currently **~180/528 IFCT codes (34%)** have documented edible portion factors.
        
        Categories with good coverage:
        - Cereals & pulses (100% - fully edible)
        - Fats & oils (100%)
        - Sugars (100%)
        - Spices (100% - used in small amounts)
        
        Categories with gaps:
        - Vegetables (especially leafy) - trimming losses vary
        - Fruits - peeling/seeding losses
        - Animal foods - bone/waste removal
        """)
        
        # Weight coverage
        st.subheader("⚖️ Gram Weight Coverage")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Resolved (grams)", "1,299", "1.4%")
        with col2:
            st.metric("Household Conversions", "1,337", "1.5%")
        with col3:
            st.metric("Unresolved", "89,525", "98.5%")
        
        st.markdown("---")
        
        # How nutrition calculation works
        st.subheader("🧮 How Nutrition Calculation Works")
        
        st.markdown("""
        ### Calculation Formula
        
        For each ingredient with an approved IFCT mapping:
        
        **nutrient_contribution = IFCT_value_per_100g × edible_weight_g / 100**
        
        ### Steps:
        1. **Approved Mapping** → Get IFCT food code
        2. **Edible Weight** → Resolved grams × edible portion factor (if as-purchased)
        3. **Nutrient Calculation** → IFCT per-100g × edible_weight / 100
        4. **Aggregation** → Sum across all ingredients
        5. **Per Serving** → Total ÷ servings
        
        ### Energy Conversion
        - IFCT stores energy in **kJ**
        - Displayed as **kcal** using: `kcal = kJ / 4.184`
        
        ### Missing Values
        - **Never zero-imputed** - shown as "missing"
        - **Per-nutrient completeness** tracked
        - **Recipe status**: COMPLETE / PARTIAL / UNAVAILABLE
        """)
        
        st.markdown("---")
        
        # Demo: What nutrition display will look like
        st.subheader("📋 Example: Nutrition Display (When Data Available)")
        
        st.markdown("""
        **Recipe: Dal Tadka (Per Serving)**
        
        | Nutrient | Value | Unit | Completeness |
        |----------|-------|------|--------------|
        | Energy | 245.3 | kcal | ✅ 100% |
        | Protein | 12.4 | g | ✅ 100% |
        | Fat | 8.2 | g | ✅ 100% |
        | Carbohydrates | 32.1 | g | ✅ 100% |
        | Total Fibre | 6.8 | g | ⚠️ 58% |
        | Sodium | 420 | mg | ⚠️ 58% |
        | Iron | 3.2 | mg | ❌ 0% |
        
        **Status:** PARTIAL (6/9 nutrients available)
        
        **Provenance:** 4/6 ingredients mapped • 2/6 weight resolved • 1/6 edible portion applied
        """)

if __name__ == "__main__":
    render()