"""User Profile Management - Main interface for profile operations."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .profile_models import (
    UserProfile, Anthropometrics, DietaryProfile, NutritionalGoals, LifestyleProfile,
    Sex, ActivityLevel, DietaryPreference, WeightGoal, MealFrequency, MealSlot,
    DEFAULT_MEAL_SLOTS, DEFAULT_MEAL_ENERGY_DISTRIBUTION,
    THREE_MEAL_DISTRIBUTION, FOUR_MEAL_DISTRIBUTION,
    get_meal_distribution
)
from .profile_validation import ProfileValidator, ValidationResult, ValidationSeverity, ValidationIssue, validate_profile
from .profile_repository import ProfileRepository, get_default_repository, set_default_repository


class UserProfileManager:
    """
    High-level interface for user profile operations.
    
    Combines validation, persistence, and profile lifecycle management.
    """
    
    def __init__(
        self,
        repository: Optional[ProfileRepository] = None,
        validator: Optional[ProfileValidator] = None,
        strict_validation: bool = False
    ):
        """
        Initialize profile manager.
        
        Args:
            repository: ProfileRepository instance (uses default if None)
            validator: ProfileValidator instance (creates new if None)
            strict_validation: If True, warnings block profile operations
        """
        self.repository = repository or get_default_repository()
        self.validator = validator or ProfileValidator(strict_mode=strict_validation)
        self.strict_validation = strict_validation
    
    def create_profile(
        self,
        user_id: str,
        anthropometrics: Optional[Dict] = None,
        dietary_profile: Optional[Dict] = None,
        nutritional_goals: Optional[Dict] = None,
        lifestyle: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        save: bool = True
    ) -> ValidationResult:
        """
        Create a new user profile.
        
        Args:
            user_id: Unique identifier
            anthropometrics: Dict with height_cm, weight_kg, age_years, sex
            dietary_profile: Dict with preference, allergies, exclusions, etc.
            nutritional_goals: Dict with target_energy_kcal, macros, weight_goal
            lifestyle: Dict with activity_level, meal_frequency, etc.
            metadata: Additional metadata
            save: Whether to persist immediately
            
        Returns:
            ValidationResult (check is_valid)
        """
        # Check if already exists
        if self.repository.exists(user_id):
            return ValidationResult(
                is_valid=False,
                issues=[ValidationIssue(
                    field="user_id",
                    severity=ValidationSeverity.ERROR,
                    message=f"Profile with user_id '{user_id}' already exists",
                    suggestion="Use update_profile() to modify existing profile"
                )]
            )
        
        # Build profile
        anthro = Anthropometrics(**(anthropometrics or {}))
        dietary = DietaryProfile(**(dietary_profile or {}))
        goals = NutritionalGoals(**(nutritional_goals or {}))
        lifestyle = LifestyleProfile(**(lifestyle or {}))
        
        profile = UserProfile(
            user_id=user_id,
            anthropometrics=anthro,
            dietary_profile=dietary,
            nutritional_goals=goals,
            lifestyle=lifestyle,
            metadata=metadata or {}
        )
        
        # Validate
        result = self.validator.validate(profile)
        if not result.is_valid:
            return result
        
        # Save if requested
        if save:
            save_result = self.repository.save(profile, validate=False)
            result.issues.extend(save_result.issues)
            result.errors.extend(save_result.errors)
            result.warnings.extend(save_result.warnings)
            result.is_valid = result.is_valid and save_result.is_valid
        
        return result
    
    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Load a profile by ID."""
        return self.repository.load(user_id)
    
    def update_profile(
        self,
        user_id: str,
        anthropometrics: Optional[Dict] = None,
        dietary_profile: Optional[Dict] = None,
        nutritional_goals: Optional[Dict] = None,
        lifestyle: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        save: bool = True
    ) -> ValidationResult:
        """
        Update an existing profile.
        
        Args:
            user_id: User identifier
            ... (same as create_profile, but partial updates)
            save: Whether to persist immediately
            
        Returns:
            ValidationResult
        """
        profile = self.repository.load(user_id)
        if profile is None:
            return ValidationResult(
                is_valid=False,
                issues=[ValidationIssue(
                    field="user_id",
                    severity=ValidationSeverity.ERROR,
                    message=f"Profile with user_id '{user_id}' not found",
                    suggestion="Use create_profile() for new profiles"
                )]
            )
        
        # Apply partial updates
        if anthropometrics is not None:
            for key, value in anthropometrics.items():
                setattr(profile.anthropometrics, key, value)
        
        if dietary_profile is not None:
            for key, value in dietary_profile.items():
                setattr(profile.dietary_profile, key, value)
        
        if nutritional_goals is not None:
            for key, value in nutritional_goals.items():
                setattr(profile.nutritional_goals, key, value)
        
        if lifestyle is not None:
            for key, value in lifestyle.items():
                setattr(profile.lifestyle, key, value)
        
        if metadata is not None:
            profile.metadata.update(metadata)
        
        # Validate
        result = self.validator.validate(profile)
        if not result.is_valid:
            return result
        
        # Save if requested
        if save:
            save_result = self.repository.save(profile, validate=False)
            result.issues.extend(save_result.issues)
            result.errors.extend(save_result.errors)
            result.warnings.extend(save_result.warnings)
            result.is_valid = result.is_valid and save_result.is_valid
        
        return result
    
    def delete_profile(self, user_id: str) -> bool:
        """Delete a profile."""
        return self.repository.delete(user_id)
    
    def profile_exists(self, user_id: str) -> bool:
        """Check if profile exists."""
        return self.repository.exists(user_id)
    
    def list_profiles(self) -> List[str]:
        """List all user IDs."""
        return self.repository.list_all()
    
    def get_meal_slots(self, profile: UserProfile) -> List[MealSlot]:
        """Get meal slots for a profile based on meal frequency."""
        distribution = get_meal_distribution(profile.lifestyle.meal_frequency)
        return [slot for slot, fraction in distribution.items() if fraction > 0]
    
    def get_meal_energy_targets(self, profile: UserProfile, daily_energy_kcal: float) -> Dict[MealSlot, float]:
        """Get per-meal energy targets based on daily total and meal frequency."""
        distribution = get_meal_distribution(profile.lifestyle.meal_frequency)
        return {slot: round(daily_energy_kcal * fraction, 1) 
                for slot, fraction in distribution.items() if fraction > 0}
    
    def validate_for_nutrition(self, user_id: str) -> ValidationResult:
        """Quick validation for nutrition calculation readiness."""
        profile = self.repository.load(user_id)
        if profile is None:
            return ValidationResult(
                is_valid=False,
                issues=[ValidationIssue(
                    field="user_id",
                    severity=ValidationSeverity.ERROR,
                    message=f"Profile '{user_id}' not found"
                )]
            )
        return self.validator.validate_for_nutrition_calculation(profile)


def create_profile_manager(
    storage_dir: str = "data/personalization/profiles",
    strict_validation: bool = False
) -> UserProfileManager:
    """Factory function to create a profile manager with default components."""
    repository = ProfileRepository(storage_dir)
    validator = ProfileValidator(strict_mode=strict_validation)
    return UserProfileManager(repository=repository, validator=validator, strict_validation=strict_validation)


# Convenience functions for quick profile creation
def create_sample_profile(user_id: str = "sample_user") -> UserProfile:
    """Create a sample profile for testing."""
    return UserProfile(
        user_id=user_id,
        anthropometrics=Anthropometrics(
            height_cm=170.0,
            weight_kg=70.0,
            age_years=30,
            sex=Sex.MALE
        ),
        dietary_profile=DietaryProfile(
            preference=DietaryPreference.VEGETARIAN,
            allergies=["peanut"],
            ingredient_exclusions=["onion", "garlic"],
            cuisine_preferences=["north indian", "south indian", "gujarati"],
        ),
        nutritional_goals=NutritionalGoals(
            weight_goal=WeightGoal.MAINTAIN,
            weight_change_rate_kg_per_week=0.5
        ),
        lifestyle=LifestyleProfile(
            activity_level=ActivityLevel.LIGHTLY_ACTIVE,
            meal_frequency=MealFrequency.FOUR,
            cooking_skill="INTERMEDIATE",
        )
    )


def create_weight_loss_profile(user_id: str = "weight_loss_user") -> UserProfile:
    """Create a sample weight loss profile."""
    return UserProfile(
        user_id=user_id,
        anthropometrics=Anthropometrics(
            height_cm=165.0,
            weight_kg=85.0,
            age_years=35,
            sex=Sex.FEMALE
        ),
        dietary_profile=DietaryProfile(
            preference=DietaryPreference.OMNIVORE,
            allergies=[],
            ingredient_exclusions=[],
            cuisine_preferences=["north indian", "south indian"],
        ),
        nutritional_goals=NutritionalGoals(
            weight_goal=WeightGoal.LOSE,
            weight_change_rate_kg_per_week=0.5,
        ),
        lifestyle=LifestyleProfile(
            activity_level=ActivityLevel.SEDENTARY,
            meal_frequency=MealFrequency.FIVE,
            cooking_skill="BEGINNER",
            time_constraint_minutes=30,
        )
    )