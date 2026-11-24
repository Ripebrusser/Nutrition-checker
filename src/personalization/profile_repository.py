"""Profile Repository - Persistence layer for user profiles."""

from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import threading
from datetime import datetime

from .profile_models import UserProfile
from .profile_validation import validate_profile, ValidationResult


class ProfileRepository:
    """
    Thread-safe repository for user profile persistence.
    
    Stores profiles as JSON files with atomic writes.
    Maintains an in-memory index for fast lookups.
    """
    
    def __init__(self, storage_dir: str = "data/personalization/profiles"):
        """
        Initialize repository.
        
        Args:
            storage_dir: Directory for profile JSON files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self._index: Dict[str, Path] = {}  # user_id -> file path
        self._lock = threading.RLock()
        self._rebuild_index()
    
    def _rebuild_index(self):
        """Rebuild in-memory index from storage directory."""
        with self._lock:
            self._index.clear()
            for file_path in self.storage_dir.glob("*.json"):
                user_id = file_path.stem
                self._index[user_id] = file_path
    
    def _get_file_path(self, user_id: str) -> Path:
        """Get file path for a user ID."""
        return self.storage_dir / f"{user_id}.json"
    
    def _atomic_write(self, file_path: Path, data: dict):
        """Atomically write JSON data to file."""
        temp_path = file_path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_path.replace(file_path)
    
    def save(self, profile: UserProfile, validate: bool = True) -> ValidationResult:
        """
        Save a user profile.
        
        Args:
            profile: UserProfile to save
            validate: Whether to validate before saving
            
        Returns:
            ValidationResult (check is_valid before using profile)
        """
        # Validate first
        validation_result = validate_profile(profile)
        if validate and not validation_result.is_valid:
            return validation_result
        
        # Update timestamp and version
        profile.updated_at = datetime.now().isoformat()
        profile.version += 1
        
        # Save to file
        file_path = self._get_file_path(profile.user_id)
        with self._lock:
            self._atomic_write(file_path, profile.to_dict())
            self._index[profile.user_id] = file_path
        
        return validation_result
    
    def load(self, user_id: str) -> Optional[UserProfile]:
        """
        Load a user profile by ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            UserProfile or None if not found
        """
        with self._lock:
            file_path = self._index.get(user_id)
            if file_path is None or not file_path.exists():
                return None
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return UserProfile.from_dict(data)
            except Exception as e:
                print(f"Error loading profile {user_id}: {e}")
                return None
    
    def delete(self, user_id: str) -> bool:
        """
        Delete a user profile.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            file_path = self._index.get(user_id)
            if file_path is None or not file_path.exists():
                return False
            
            file_path.unlink()
            del self._index[user_id]
            return True
    
    def exists(self, user_id: str) -> bool:
        """Check if a profile exists."""
        with self._lock:
            file_path = self._index.get(user_id)
            return file_path is not None and file_path.exists()
    
    def list_all(self) -> List[str]:
        """List all user IDs."""
        with self._lock:
            return list(self._index.keys())
    
    def count(self) -> int:
        """Get total profile count."""
        with self._lock:
            return len(self._index)
    
    def search(self, **filters) -> List[UserProfile]:
        """
        Search profiles by filters (loads all matching profiles).
        
        Note: This loads all profiles, so use sparingly.
        For production, consider a proper database.
        """
        results = []
        for user_id in self.list_all():
            profile = self.load(user_id)
            if profile is None:
                continue
            
            match = True
            for key, value in filters.items():
                if key == "dietary_preference":
                    if profile.dietary_profile.preference.value != value:
                        match = False
                        break
                elif key == "activity_level":
                    if profile.lifestyle.activity_level.value != value:
                        match = False
                        break
                elif key == "age_min":
                    if profile.anthropometrics.age_years is None or profile.anthropometrics.age_years < value:
                        match = False
                        break
                elif key == "age_max":
                    if profile.anthropometrics.age_years is None or profile.anthropometrics.age_years > value:
                        match = False
                        break
                elif key == "weight_goal":
                    if profile.nutritional_goals.weight_goal.value != value:
                        match = False
                        break
                elif key == "has_allergies":
                    has_allergies = len(profile.dietary_profile.allergies) > 0
                    if has_allergies != value:
                        match = False
                        break
            
            if match:
                results.append(profile)
        
        return results
    
    def backup(self, backup_dir: str) -> int:
        """
        Backup all profiles to a directory.
        
        Returns:
            Number of profiles backed up
        """
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_path / f"profiles_backup_{timestamp}.json"
        
        all_profiles = []
        for user_id in self.list_all():
            profile = self.load(user_id)
            if profile:
                all_profiles.append(profile.to_dict())
        
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(all_profiles, f, indent=2, ensure_ascii=False)
        
        return len(all_profiles)
    
    def restore_from_backup(self, backup_file: str) -> int:
        """
        Restore profiles from a backup file.
        
        Returns:
            Number of profiles restored
        """
        with open(backup_file, "r", encoding="utf-8") as f:
            all_profiles = json.load(f)
        
        count = 0
        for profile_data in all_profiles:
            profile = UserProfile.from_dict(profile_data)
            self.save(profile, validate=False)
            count += 1
        
        return count


# Global default repository instance
_default_repository: Optional[ProfileRepository] = None


def get_default_repository() -> ProfileRepository:
    """Get the global default profile repository."""
    global _default_repository
    if _default_repository is None:
        _default_repository = ProfileRepository()
    return _default_repository


def set_default_repository(repo: ProfileRepository):
    """Set the global default profile repository."""
    global _default_repository
    _default_repository = repo