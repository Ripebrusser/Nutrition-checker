"""Reusable form components."""

import streamlit as st
from typing import List, Optional, Dict, Any
from datetime import date


def profile_form(profile_data: dict, readonly: bool = False) -> dict:
    """Render profile form and return updated data."""
    col1, col2 = st.columns(2)
    
    with col1:
        height = st.number_input(
            "Height (cm)", 
            min_value=50.0, 
            max_value=250.0, 
            value=profile_data.get("height_cm") or 0.0,
            disabled=readonly, 
            step=0.1,
            format="%.1f"
        )
        weight = st.number_input(
            "Weight (kg)", 
            min_value=2.0, 
            max_value=300.0,
            value=profile_data.get("weight_kg") or 0.0,
            disabled=readonly, 
            step=0.1,
            format="%.1f"
        )
        age = st.number_input(
            "Age (years)", 
            min_value=1, 
            max_value=120,
            value=profile_data.get("age_years") or 0,
            disabled=readonly
        )
        sex = st.selectbox(
            "Sex", 
            ["MALE", "FEMALE"],
            index=["MALE", "FEMALE"].index(profile_data.get("sex", "MALE")) if profile_data.get("sex") else 0,
            disabled=readonly
        )
    
    with col2:
        activity = st.selectbox(
            "Activity Level",
            ["SEDENTARY", "LIGHTLY_ACTIVE", "MODERATELY_ACTIVE", "VERY_ACTIVE", "EXTREMELY_ACTIVE"],
            index=["SEDENTARY", "LIGHTLY_ACTIVE", "MODERATELY_ACTIVE", "VERY_ACTIVE", "EXTREMELY_ACTIVE"]
                .index(profile_data.get("activity_level", "SEDENTARY")),
            disabled=readonly
        )
        meal_freq = st.selectbox(
            "Meals per Day", 
            [3, 4, 5, 6],
            index=[3, 4, 5, 6].index(profile_data.get("meal_frequency", 3)),
            disabled=readonly
        )
        cooking_skill = st.selectbox(
            "Cooking Skill",
            ["BEGINNER", "INTERMEDIATE", "ADVANCED"],
            index=["BEGINNER", "INTERMEDIATE", "ADVANCED"].index(profile_data.get("cooking_skill", "INTERMEDIATE")),
            disabled=readonly
        )
        time_constraint = st.number_input(
            "Max Prep+Cook Time (min)", 
            min_value=5, 
            max_value=180,
            value=profile_data.get("time_constraint_minutes") or 30,
            disabled=readonly
        )
    
    return {
        "height_cm": height if height > 0 else None,
        "weight_kg": weight if weight > 0 else None,
        "age_years": age if age > 0 else None,
        "sex": sex,
        "activity_level": activity,
        "meal_frequency": meal_freq,
        "cooking_skill": cooking_skill,
        "time_constraint_minutes": time_constraint if time_constraint > 0 else None,
    }


def dietary_preferences_form(profile_data: dict, readonly: bool = False) -> dict:
    """Render dietary preferences form."""
    preference = st.selectbox(
        "Dietary Preference",
        ["OMNIVORE", "VEGETARIAN", "VEGAN", "EGGETARIAN", "JAIN", "PESCATARIAN", "FLEXITARIAN"],
        index=["OMNIVORE", "VEGETARIAN", "VEGAN", "EGGETARIAN", "JAIN", "PESCATARIAN", "FLEXITARIAN"]
            .index(profile_data.get("dietary_preference", "OMNIVORE")) if profile_data.get("dietary_preference") else 0,
        disabled=readonly
    )
    
    st.markdown("**Allergies**")
    allergies = st_tags_input(
        "Allergies",
        value=profile_data.get("allergies", []),
        suggestions=["peanut", "tree_nut", "milk", "egg", "wheat", "soy", "fish", "shellfish", "sesame", "mustard", "celery"],
        disabled=readonly
    )
    
    st.markdown("**Ingredient Exclusions**")
    exclusions = st_tags_input(
        "Ingredient Exclusions",
        value=profile_data.get("ingredient_exclusions", []),
        disabled=readonly
    )
    
    st.markdown("**Preferred Cuisines**")
    cuisine_prefs = st_tags_input(
        "Preferred Cuisines",
        value=profile_data.get("cuisine_preferences", []),
        suggestions=["north indian", "south indian", "gujarati", "maharashtrian", "punjabi", "bengali", "rajasthani", "kashmiri", "kerala", "andhra", "tamil", "karnataka", "goan", "chettinad", "hyderabadi", "awadhi", "muglai"],
        disabled=readonly
    )
    
    st.markdown("**Cuisine Exclusions**")
    cuisine_exclusions = st_tags_input(
        "Cuisine Exclusions",
        value=profile_data.get("cuisine_exclusions", []),
        disabled=readonly
    )
    
    st.markdown("**Disliked Ingredients**")
    disliked = st_tags_input(
        "Disliked Ingredients",
        value=profile_data.get("disliked_ingredients", []),
        disabled=readonly
    )
    
    st.markdown("**Religious Restrictions**")
    religious = st_tags_input(
        "Religious Restrictions",
        value=profile_data.get("religious_restrictions", []),
        suggestions=["jain", "halal", "kosher", "fasting"],
        disabled=readonly
    )
    
    st.markdown("**Medical Conditions**")
    medical = st_tags_input(
        "Medical Conditions",
        value=profile_data.get("medical_conditions", []),
        suggestions=["diabetes", "hypertension", "heart disease", "kidney disease", "celiac", "lactose intolerance"],
        disabled=readonly
    )
    
    return {
        "dietary_preference": preference,
        "allergies": allergies,
        "ingredient_exclusions": exclusions,
        "cuisine_preferences": cuisine_prefs,
        "cuisine_exclusions": cuisine_exclusions,
        "disliked_ingredients": disliked,
        "religious_restrictions": religious,
        "medical_conditions": medical,
    }


def nutritional_goals_form(profile_data: dict, readonly: bool = False) -> dict:
    """Render nutritional goals form."""
    st.markdown("**Weight Goal**")
    weight_goal = st.selectbox(
        "Weight Goal",
        ["MAINTAIN", "LOSE", "GAIN"],
        index=["MAINTAIN", "LOSE", "GAIN"].index(profile_data.get("weight_goal", "MAINTAIN")),
        disabled=readonly
    )
    
    if profile_data.get("weight_goal") == "LOSE" or profile_data.get("weight_goal") == "GAIN":
        weight_change = st.number_input(
            "Weekly Weight Change (kg)",
            min_value=0.1,
            max_value=1.0,
            value=profile_data.get("weight_change_rate_kg_per_week") or 0.5,
            step=0.1,
            disabled=readonly,
            help="Safe range: 0.1-1.0 kg/week"
        )
    else:
        weight_change = 0.5
    
    st.markdown("**Custom Nutritional Targets (Optional)**")
    col1, col2 = st.columns(2)
    with col1:
        energy = st.number_input(
            "Energy (kcal/day)", 
            min_value=500, 
            max_value=5000, 
            value=profile_data.get("target_energy_kcal") or 0,
            disabled=readonly,
            help="Leave blank to auto-calculate"
        )
        protein = st.number_input(
            "Protein (g/day)", 
            min_value=10, 
            max_value=300, 
            value=profile_data.get("target_protein_g") or 0,
            disabled=readonly
        )
        carbs = st.number_input(
            "Carbohydrates (g/day)", 
            min_value=20, 
            max_value=500, 
            value=profile_data.get("target_carbohydrate_g") or 0,
            disabled=readonly
        )
    with col2:
        fat = st.number_input(
            "Fat (g/day)", 
            min_value=10, 
            max_value=200, 
            value=profile_data.get("target_fat_g") or 0,
            disabled=readonly
        )
        fibre = st.number_input(
            "Fibre (g/day)", 
            min_value=5, 
            max_value=100, 
            value=profile_data.get("target_fibre_g") or 0,
            disabled=readonly
        )
        sodium = st.number_input(
            "Sodium (mg/day)", 
            min_value=500, 
            max_value=5000, 
            value=profile_data.get("target_sodium_mg") or 0,
            disabled=readonly
        )
    
    return {
        "weight_goal": weight_goal,
        "weight_change_rate_kg_per_week": weight_change if profile_data.get("weight_goal") in ["LOSE", "GAIN"] else 0.5,
        "target_energy_kcal": energy if energy > 0 else None,
        "target_protein_g": protein if protein > 0 else None,
        "target_carbohydrate_g": carbs if carbs > 0 else None,
        "target_fat_g": fat if fat > 0 else None,
        "target_fibre_g": fibre if fibre > 0 else None,
        "target_sodium_mg": sodium if sodium > 0 else None,
    }


def st_tags_input(
    label: str,
    value: List[str],
    suggestions: List[str] = None,
    disabled: bool = False,
    key: str = None
) -> List[str]:
    """Custom tags input component for Streamlit."""
    if key is None:
        key = f"tags_{label.lower().replace(' ', '_')}"
    
    # Initialize session state for tags
    state_key = f"{key}_tags"
    if state_key not in st.session_state:
        st.session_state[state_key] = value.copy()
    
    tags = st.session_state[state_key]
    
    # Display current tags
    if tags:
        cols = st.columns([0.7, 0.3])
        with cols[0]:
            st.write("Current: " + ", ".join(tags))
        with cols[1]:
            if not disabled:
                if st.button("Clear All", key=f"{key}_clear", use_container_width=True):
                    st.session_state[state_key] = []
                    st.rerun()
    
    # Add new tag
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        if suggestions:
            new_tag = st.selectbox(
                f"Add {label}",
                [""] + [s for s in suggestions if s not in st.session_state[state_key]],
                key=f"{key}_select",
                disabled=disabled
            )
        else:
            new_tag = st.text_input(
                f"Add {label}",
                key=f"{key}_input",
                disabled=disabled
            )
    
    with col2:
        if st.button("Add", key=f"{key}_add", use_container_width=True, disabled=disabled):
            if new_tag and new_tag not in st.session_state[state_key]:
                st.session_state[state_key].append(new_tag)
                st.rerun()
    
    # Display current tags as removable chips
    if tags:
        st.caption("Current tags (click to remove):")
        cols = st.columns(min(len(tags), 4))
        for i, tag in enumerate(tags):
            with cols[i % 4]:
                if st.button(f"✕ {tag}", key=f"{key}_remove_{i}", disabled=disabled, use_container_width=True):
                    st.session_state[state_key].remove(tag)
                    st.rerun()
    
    return st.session_state[state_key]


def nutritional_goals_form(profile_data: dict, readonly: bool = False) -> dict:
    """Render nutritional goals form."""
    st.markdown("**Weight Goal**")
    weight_goal = st.selectbox(
        "Weight Goal",
        ["MAINTAIN", "LOSE", "GAIN"],
        index=["MAINTAIN", "LOSE", "GAIN"].index(profile_data.get("weight_goal", "MAINTAIN")),
        disabled=readonly
    )
    
    weight_change = 0.5
    if profile_data.get("weight_goal") in ["LOSE", "GAIN"]:
        weight_change = st.number_input(
            "Weekly Weight Change (kg)",
            min_value=0.1,
            max_value=1.0,
            value=profile_data.get("weight_change_rate_kg_per_week") or 0.5,
            step=0.1,
            disabled=readonly,
            help="Safe range: 0.1-1.0 kg/week"
        )
    
    st.markdown("**Custom Nutritional Targets (Optional)**")
    col1, col2 = st.columns(2)
    with col1:
        energy = st.number_input(
            "Energy (kcal/day)", 
            min_value=500, 
            max_value=5000, 
            value=profile_data.get("target_energy_kcal") or 0,
            disabled=readonly,
            help="Leave blank to auto-calculate"
        )
        protein = st.number_input(
            "Protein (g/day)", 
            min_value=10, 
            max_value=300, 
            value=profile_data.get("target_protein_g") or 0,
            disabled=readonly
        )
        carbs = st.number_input(
            "Carbohydrates (g/day)", 
            min_value=20, 
            max_value=500, 
            value=profile_data.get("target_carbohydrate_g") or 0,
            disabled=readonly
        )
    with col2:
        fat = st.number_input(
            "Fat (g/day)", 
            min_value=10, 
            max_value=200, 
            value=profile_data.get("target_fat_g") or 0,
            disabled=readonly
        )
        fibre = st.number_input(
            "Fibre (g/day)", 
            min_value=5, 
            max_value=100, 
            value=profile_data.get("target_fibre_g") or 0,
            disabled=readonly
        )
        sodium = st.number_input(
            "Sodium (mg/day)", 
            min_value=500, 
            max_value=5000, 
            value=profile_data.get("target_sodium_mg") or 0,
            disabled=readonly
        )
    
    return {
        "weight_goal": weight_goal,
        "weight_change_rate_kg_per_week": weight_change if profile_data.get("weight_goal") in ["LOSE", "GAIN"] else 0.5,
        "target_energy_kcal": energy if energy > 0 else None,
        "target_protein_g": protein if protein > 0 else None,
        "target_carbohydrate_g": carbs if carbs > 0 else None,
        "target_fat_g": fat if fat > 0 else None,
        "target_fibre_g": fibre if fibre > 0 else None,
        "target_sodium_mg": sodium if sodium > 0 else None,
    }


def recipe_card(recipe: dict, show_nutrition: bool = True, on_click=None) -> None:
    """Render a recipe card."""
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            # Placeholder for recipe image
            st.markdown("🍲")
        with col2:
            st.subheader(recipe.get("recipe_name", "Unknown Recipe"))
            st.caption(f"🍽️ {recipe.get('cuisine', 'Unknown')} • 🍽️ {recipe.get('course', 'Unknown')}")
            
            if show_nutrition and recipe.get("per_serving_nutrients"):
                nuts = recipe["per_serving_nutrients"]
                cols = st.columns(4)
                if "energy_kcal" in nuts:
                    cols[0].metric("Calories", f"{nuts['energy_kcal']:.0f} kcal")
                if "protein_g" in nuts:
                    cols[1].metric("Protein", f"{nuts['protein_g']:.1f} g")
                if "carb_available_g" in nuts:
                    cols[2].metric("Carbs", f"{nuts['carb_available_g']:.1f} g")
                if "fat_g" in nuts:
                    cols[3].metric("Fat", f"{nuts['fat_g']:.1f} g")
            
            if on_click and st.button("View Details", key=f"view_{recipe.get('id')}", use_container_width=True):
                on_click(recipe)


def nutrition_status_badge(status: str) -> None:
    """Display nutrition status badge."""
    colors = {
        "COMPLETE": "green",
        "PARTIAL": "orange",
        "UNAVAILABLE": "gray",
        "NO_MAPPED_INGREDIENTS": "red",
    }
    color = colors.get(status, "gray")
    st.markdown(
        f'<span style="background-color: {color}; color: white; padding: 2px 8px; '
        f'border-radius: 12px; font-size: 0.8em;">{status}</span>',
        unsafe_allow_html=True
    )


def nutrient_metric_card(label: str, value: float, unit: str, target: float = None, color: str = "blue") -> None:
    """Display a nutrient metric card."""
    delta = None
    if target and target > 0:
        delta = f"{((value / target - 1) * 100):+.1f}%"
    
    st.metric(
        label=f"{label} ({unit})",
        value=f"{value:.1f}",
        delta=delta,
        delta_color="normal" if target and value <= target else "inverse"
    )


def dietary_compliance_badge(result: str) -> None:
    """Display dietary compliance badge."""
    colors = {
        "PASS": "green",
        "FAIL": "red",
        "UNVERIFIED": "orange",
    }
    color = colors.get(result, "gray")
    st.markdown(
        f'<span style="background-color: {color}; color: white; padding: 2px 8px; '
        f'border-radius: 12px; font-size: 0.8em;">{result}</span>',
        unsafe_allow_html=True
    )


def meal_slot_badge(slot: str) -> None:
    """Display meal slot badge."""
    icons = {
        "BREAKFAST": "🌅",
        "MORNING_SNACK": "☕",
        "LUNCH": "🌞",
        "EVENING_SNACK": "🌅",
        "DINNER": "🌙",
    }
    icon = icons.get(slot, "🍽️")
    st.markdown(f"{icon} **{slot.replace('_', ' ').title()}**")