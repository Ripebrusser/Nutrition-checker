"""Validation service for input validation and data integrity."""

from typing import Optional, List, Dict, Any, Tuple
from datetime import date, datetime
from app.utils.validation import (
    validate_email,
    validate_positive_number,
    validate_range,
    validate_meal_frequency,
    validate_cooking_skill,
    validate_dietary_preference,
    validate_activity_level,
    validate_sex,
    validate_weight_goal,
    validate_weight_change_rate,
    validate_meal_frequency,
    validate_time_constraint,
)
from app.auth.password import validate_password_strength, validate_password_change

class ValidationService:
    """Service for input validation and data integrity checks."""
    
    def __init__(self):
        pass
    
    # User validation
    def validate_user_registration(self, email: str, password: str, full_name: str = None) -> Tuple[bool, List[str]]:
        """Validate user registration data."""
        errors = []
        
        if not email or not validate_email(email):
            errors.append("Invalid email format")
        
        is_valid, errors = validate_password_strength(password)
        if not is_valid:
            errors.extend(errors)
        
        if full_name and len(full_name) > 255:
            errors.append("Full name too long (max 255 characters)")
        
        return len(errors) == 0, errors
    
    def validate_profile(self, data: dict) -> Tuple[bool, List[str]]:
        """Validate profile data."""
        errors = []
        
        # Anthropometrics
        if "height_cm" in data and data["height_cm"] is not None:
            if not validate_range(data["height_cm"], 50, 250):
                errors.append("Height must be between 50 and 250 cm")
        
        if "weight_kg" in data and data["weight_kg"] is not None:
            if not validate_range(data["weight_kg"], 2, 300):
                errors.append("Weight must be between 2 and 300 kg")
        
        if "age_years" in data and data["age_years"] is not None:
            if not validate_range(data["age_years"], 1, 120):
                errors.append("Age must be between 1 and 120")
        
        if "sex" in data and data["sex"] is not None:
            if not validate_sex(data["sex"]):
                errors.append("Sex must be MALE or FEMALE")
        
        # Dietary
        if "dietary_preference" in data and data["dietary_preference"]:
            if not validate_dietary_preference(data["dietary_preference"]):
                errors.append("Invalid dietary preference")
        
        if "allergies" in data and data["allergies"]:
            # Could validate against known allergens
            pass
        
        # Nutritional goals
        if "target_energy_kcal" in data and data["target_energy_kcal"] is not None:
            if not validate_range(data["target_energy_kcal"], 500, 5000):
                errors.append("Energy target must be between 500 and 5000 kcal")
        
        if "target_protein_g" in data and data["target_protein_g"] is not None:
            if not validate_range(data["target_protein_g"], 10, 300):
                errors.append("Protein target must be between 10 and 300 g")
        
        if "target_fat_g" in data and data["target_fat_g"] is not None:
            if not validate_range(data["target_fat_g"], 10, 200):
                errors.append("Fat target must be between 10 and 200 g")
        
        if "target_carbohydrate_g" in data and data["target_carbohydrate_g"] is not None:
            if not validate_range(data["target_carbohydrate_g"], 20, 500):
                errors.append("Carb target must be between 20 and 500 g")
        
        if "target_fibre_g" in data and data["target_fibre_g"] is not None:
            if not validate_range(data["target_fibre_g"], 5, 100):
                errors.append("Fibre target must be between 5 and 100 g")
        
        if "weight_goal" in data and data["weight_goal"]:
            if not validate_weight_goal(data["weight_goal"]):
                errors.append("Invalid weight goal")
        
        if "weight_change_rate_kg_per_week" in data and data["weight_change_rate_kg_per_week"] is not None:
            if not validate_weight_change_rate(data["weight_change_rate_kg_per_week"]):
                errors.append("Weight change rate must be between 0.1 and 1.0 kg/week")
        
        # Lifestyle
        if "activity_level" in data and data["activity_level"]:
            if not validate_activity_level(data["activity_level"]):
                errors.append("Invalid activity level")
        
        if "meal_frequency" in data and data["meal_frequency"] is not None:
            if not validate_meal_frequency(data["meal_frequency"]):
                errors.append("Meal frequency must be 3, 4, 5, or 6")
        
        if "cooking_skill" in data and data["cooking_skill"]:
            if not validate_cooking_skill(data["cooking_skill"]):
                errors.append("Invalid cooking skill")
        
        if "time_constraint_minutes" in data and data["time_constraint_minutes"] is not None:
            if not validate_time_constraint(data["time_constraint_minutes"]):
                errors.append("Time constraint must be between 5 and 180 minutes")
        
        return len(errors) == 0, errors
    
    # Password validation
    def validate_password_change(
        self,
        current_password: str,
        new_password: str,
        current_hash: str
    ) -> Tuple[bool, List[str]]:
        return validate_password_change(current_password, new_password, current_hash)
    
    def validate_new_password(self, password: str) -> Tuple[bool, List[str]]:
        return validate_password_strength(password)
    
    # Meal plan validation
    def validate_meal_plan(self, plan_data: dict) -> Tuple[bool, List[str]]:
        errors = []
        
        if "start_date" in plan_data and plan_data["start_date"]:
            try:
                from datetime import date
                if isinstance(plan_data["start_date"], str):
                    from datetime import datetime
                    start_date = datetime.strptime(plan_data["start_date"], "%Y-%m-%d").date()
                else:
                    start_date = plan_data["start_date"]
                
                if start_date < date.today():
                    errors.append("Start date cannot be in the past")
            except:
                errors.append("Invalid start date format")
        
        if "days" in plan_data and plan_data["days"] is not None:
            if not isinstance(plan_data["days"], int) or plan_data["days"] < 1 or plan_data["days"] > 14:
                errors.append("Days must be between 1 and 14")
        
        if "meal_frequency" in plan_data and plan_data["meal_frequency"] is not None:
            if plan_data["meal_frequency"] not in [3, 4, 5, 6]:
                errors.append("Meal frequency must be 3, 4, 5, or 6")
        
        return len(errors) == 0, errors
    
    def validate_meal_plan_item(self, item_data: dict) -> Tuple[bool, List[str]]:
        errors = []
        
        if "day_index" in item_data and item_data["day_index"] is not None:
            if not isinstance(item_data["day_index"], int) or item_data["day_index"] < 0:
                errors.append("Day index must be a non-negative integer")
        
        if "meal_slot" in item_data and item_data["meal_slot"]:
            valid_slots = ["BREAKFAST", "MORNING_SNACK", "LUNCH", "EVENING_SNACK", "DINNER"]
            if item_data["meal_slot"] not in valid_slots:
                errors.append(f"Meal slot must be one of: {', '.join(valid_slots)}")
        
        if "recipe_id" in item_data and item_data["recipe_id"] is not None:
            if not isinstance(item_data["recipe_id"], int) or item_data["recipe_id"] <= 0:
                errors.append("Recipe ID must be a positive integer")
        
        if "servings" in item_data and item_data["servings"] is not None:
            if not isinstance(item_data["servings"], (int, float)) or item_data["servings"] <= 0:
                errors.append("Servings must be a positive number")
        
        return len(errors) == 0, errors
    
    # Recipe validation
    def validate_recipe_search(self, params: dict) -> Tuple[bool, List[str]]:
        errors = []
        
        if "limit" in params and params["limit"] is not None:
            if not isinstance(params["limit"], int) or params["limit"] < 1 or params["limit"] > 100:
                errors.append("Limit must be between 1 and 100")
        
        if "offset" in params and params["offset"] is not None:
            if not isinstance(params["offset"], int) or params["offset"] < 0:
                errors.append("Offset must be a non-negative integer")
        
        if "max_time" in params and params["max_time"] is not None:
            if not isinstance(params["max_time"], int) or params["max_time"] < 0:
                errors.append("Max time must be a non-negative integer")
        
        return len(errors) == 0, errors
    
    def validate_recommendation_request(self, params: dict) -> Tuple[bool, List[str]]:
        errors = []
        
        if "k" in params and params["k"] is not None:
            if not isinstance(params["k"], int) or params["k"] < 1 or params["k"] > 50:
                errors.append("k must be between 1 and 50")
        
        if "min_nutrition_completeness" in params and params["min_nutrition_completeness"] is not None:
            if not isinstance(params["min_nutrition_completeness"], (int, float)) or \
               params["min_nutrition_completeness"] < 0 or params["min_nutrition_completeness"] > 1:
                errors.append("Min nutrition completeness must be between 0 and 1")
        
        return len(errors) == 0, errors
    
    def validate_energy_request(self, data: dict) -> Tuple[bool, List[str]]:
        errors = []
        
        required = ["height_cm", "weight_kg", "age_years", "sex", "activity_level"]
        for field in required:
            if field not in data or data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        if "height_cm" in data and data["height_cm"] is not None:
            if not isinstance(data["height_cm"], (int, float)) or data["height_cm"] < 50 or data["height_cm"] > 250:
                errors.append("Height must be between 50 and 250 cm")
        
        if "weight_kg" in data and data["weight_kg"] is not None:
            if not isinstance(data["weight_kg"], (int, float)) or data["weight_kg"] < 2 or data["weight_kg"] > 300:
                errors.append("Weight must be between 2 and 300 kg")
        
        if "age_years" in data and data["age_years"] is not None:
            if not isinstance(data["age_years"], int) or data["age_years"] < 1 or data["age_years"] > 120:
                errors.append("Age must be between 1 and 120")
        
        if "sex" in data and data["sex"]:
            if data["sex"] not in ["MALE", "FEMALE", "male", "female"]:
                errors.append("Sex must be MALE or FEMALE")
        
        if "activity_level" in data and data["activity_level"]:
            if not self.validate_activity_level(data["activity_level"]):
                errors.append("Invalid activity level")
        
        if "weight_goal" in data and data["weight_goal"]:
            if data["weight_goal"] not in ["MAINTAIN", "LOSE", "GAIN"]:
                errors.append("Weight goal must be MAINTAIN, LOSE, or GAIN")
        
        if "weight_change_kg_per_week" in data and data["weight_change_kg_per_week"] is not None:
            if not isinstance(data["weight_change_kg_per_week"], (int, float)) or \
               data["weight_change_kg_per_week"] < 0.1 or data["weight_change_kg_per_week"] > 1.0:
                errors.append("Weight change rate must be between 0.1 and 1.0 kg/week")
        
        return len(errors) == 0, errors
    
    def validate_meal_slot(self, slot: str) -> bool:
        valid_slots = ["BREAKFAST", "MORNING_SNACK", "LUNCH", "EVENING_SNACK", "DINNER"]
        return slot in valid_slots
    
    def validate_cuisine(self, cuisine: str, valid_cuisines: List[str]) -> bool:
        return cuisine in valid_cuisines
    
    def validate_course(self, course: str, valid_courses: List[str]) -> bool:
        return course in valid_courses
    
    def validate_ingredient_list(self, ingredients: List[str]) -> Tuple[bool, List[str]]:
        errors = []
        if not isinstance(ingredients, list):
            errors.append("Ingredients must be a list")
            return False, errors
        
        if len(ingredients) == 0:
            errors.append("At least one ingredient required")
        
        for ing in ingredients:
            if not isinstance(ing, str) or not ing.strip():
                errors.append("All ingredients must be non-empty strings")
        
        return len(errors) == 0, errors
    
    def validate_nutrient_value(self, nutrient: str, value: float) -> Tuple[bool, List[str]]:
        errors = []
        
        ranges = {
            "energy_kcal": (0, 5000),
            "protein_g": (0, 300),
            "fat_g": (0, 200),
            "carbohydrate_g": (0, 500),
            "fibre_g": (0, 100),
            "sodium_mg": (0, 5000),
            "moisture_g": (0, 100),
            "ash_g": (0, 20),
            "fibre_total_g": (0, 50),
            "fibre_insoluble_g": (0, 50),
            "fibre_soluble_g": (0, 30),
            "carb_available_g": (0, 100),
        }
        
        if nutrient in ranges:
            min_val, max_val = ranges[nutrient]
            if value < min_val or value > max_val:
                errors.append(f"{nutrient} must be between {min_val} and {max_val}")
        
        return len(errors) == 0, errors