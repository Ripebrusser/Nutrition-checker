"""User service for profile management."""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.database.models import User, UserProfile
from app.database.session import get_db
from app.auth.password import hash_password, verify_password, validate_password_change

class UserService:
    """Service for user and profile management."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        anthropometrics: Optional[Dict] = None,
        dietary_profile: Optional[Dict] = None,
        nutritional_goals: Optional[Dict] = None,
        lifestyle: Optional[Dict] = None,
    ) -> Optional[User]:
        """Create a new user with profile."""
        # Check if email exists
        if self.db.query(User).filter(User.email == email).first():
            return None
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user
        user = User(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role="USER",
            is_active=True
        )
        self.db.add(user)
        self.db.flush()  # Get user ID
        
        # Create profile
        profile = UserProfile(
            user_id=user.id,
            height_cm=anthropometrics.get("height_cm") if anthropometrics else None,
            weight_kg=anthropometrics.get("weight_kg") if anthropometrics else None,
            age_years=anthropometrics.get("age_years") if anthropometrics else None,
            sex=anthropometrics.get("sex") if anthropometrics else None,
            dietary_preference=dietary_profile.get("preference", "OMNIVORE") if dietary_profile else "OMNIVORE",
            allergies=dietary_profile.get("allergies", []) if dietary_profile else [],
            ingredient_exclusions=dietary_profile.get("ingredient_exclusions", []) if dietary_profile else [],
            cuisine_preferences=dietary_profile.get("cuisine_preferences", []) if dietary_profile else [],
            cuisine_exclusions=dietary_profile.get("cuisine_exclusions", []) if dietary_profile else [],
            disliked_ingredients=dietary_profile.get("disliked_ingredients", []) if dietary_profile else [],
            religious_restrictions=dietary_profile.get("religious_restrictions", []) if dietary_profile else [],
            medical_conditions=dietary_profile.get("medical_conditions", []) if dietary_profile else [],
            target_energy_kcal=nutritional_goals.get("target_energy_kcal") if nutritional_goals else None,
            target_protein_g=nutritional_goals.get("target_protein_g") if nutritional_goals else None,
            target_carbohydrate_g=nutritional_goals.get("target_carbohydrate_g") if nutritional_goals else None,
            target_fat_g=nutritional_goals.get("target_fat_g") if nutritional_goals else None,
            target_fibre_g=nutritional_goals.get("target_fibre_g") if nutritional_goals else None,
            target_sodium_mg=nutritional_goals.get("target_sodium_mg") if nutritional_goals else None,
            weight_goal=nutritional_goals.get("weight_goal", "MAINTAIN") if nutritional_goals else "MAINTAIN",
            weight_change_rate_kg_per_week=nutritional_goals.get("weight_change_rate_kg_per_week", 0.5) if nutritional_goals else 0.5,
            activity_level=lifestyle.get("activity_level", "SEDENTARY") if lifestyle else "SEDENTARY",
            meal_frequency=lifestyle.get("meal_frequency", 3) if lifestyle else 3,
            preferred_meal_times=lifestyle.get("preferred_meal_times", {}) if lifestyle else {},
            cooking_skill=lifestyle.get("cooking_skill", "INTERMEDIATE") if lifestyle else "INTERMEDIATE",
            budget_constraint=lifestyle.get("budget_constraint") if lifestyle else None,
            time_constraint_minutes=lifestyle.get("time_constraint_minutes") if lifestyle else None,
        )
        self.db.add(profile)
        self.db.commit()
        
        return user
    
    def get_user(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_profile(self, user_id: int) -> Optional[UserProfile]:
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    def update_profile(self, user_id: int, updates: Dict[str, Any]) -> bool:
        profile = self.get_profile(user_id)
        if not profile:
            return False
        
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        self.db.commit()
        return True
    
    def update_user(self, user_id: int, updates: Dict[str, Any]) -> bool:
        user = self.get_user(user_id)
        if not user:
            return False
        
        for key, value in updates.items():
            if hasattr(user, key) and key != "password_hash":
                setattr(user, key, value)
        
        self.db.commit()
        return True
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> tuple[bool, List[str]]:
        user = self.get_user(user_id)
        if not user:
            return False, ["User not found"]
        
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            return False, ["Current password is incorrect"]
        
        # Validate new password
        is_valid, errors = validate_password_change(current_password, new_password, user.password_hash)
        if not is_valid:
            return False, errors
        
        # Update password
        user.password_hash = hash_password(new_password)
        self.db.commit()
        return True, []
    
    def delete_user(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True
    
    def list_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        return self.db.query(User).limit(limit).offset(offset).all()
    
    def search_users(self, **filters) -> List[User]:
        query = self.db.query(User)
        
        if "dietary_preference" in filters:
            query = query.join(UserProfile).filter(
                UserProfile.dietary_preference == filters["dietary_preference"]
            )
        if "activity_level" in filters:
            query = query.join(UserProfile).filter(
                UserProfile.activity_level == filters["activity_level"]
            )
        if "age_min" in filters:
            query = query.join(UserProfile).filter(
                UserProfile.age_years >= filters["age_min"]
            )
        if "age_max" in filters:
            query = query.join(UserProfile).filter(
                UserProfile.age_years <= filters["age_max"]
            )
        if "weight_goal" in filters:
            query = query.join(UserProfile).filter(
                UserProfile.weight_goal == filters["weight_goal"]
            )
        if "has_allergies" in filters:
            query = query.join(UserProfile).filter(
                UserProfile.allergies != "[]"
            )
        
        return query.all()