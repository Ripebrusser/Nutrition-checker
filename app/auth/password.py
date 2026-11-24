"""Password hashing utilities."""

import bcrypt
import re
from typing import Set

# Common passwords to reject (top 100 most common)
COMMON_PASSWORDS: Set[str] = {
    "password", "123456", "12345678", "qwerty", "abc123", "password1", "123456789",
    "12345", "1234567", "letmein", "welcome", "admin", "monkey", "dragon",
    "sunshine", "shadow", "ashley", "bailey", "passw0rd", "superman", "michael",
    "football", "iloveyou", "princess", "rockyou", "abc123", "andrea", "jennifer",
    "nicole", "jessica", "hannah", "amanda", "katie", "emily", "samantha",
    "elizabeth", "stephanie", "rebecca", "laura", "amanda", "melissa", "michelle",
    "nicole", "katherine", "amber", "christina", "victoria", "alexis", "rachel",
    "sarah", "jennifer", "laura", "amanda", "ashley", "tiffany", "nicole",
    "angela", "kimberly", "katherine", "melissa", "rebecca", "lauren", "courtney",
    "danielle", "catherine", "sarah", "kelly", "lisa", "nancy", "betty", "helen",
    "sandra", "donna", "carol", "ruth", "sharon", "michelle", "laura", "emily",
    "katie", "jessica", "nicole", "heather", "jennifer", "ashley", "amanda",
    "tiffany", "samantha", "katherine", "stephanie", "rebecca", "laura", "amanda",
    "melissa", "nicole", "angela", "kimberly", "katherine", "melissa", "rebecca",
    "lauren", "courtney", "danielle", "catherine", "sarah", "kelly", "lisa", "nancy",
}

def hash_password(password: str) -> str:
    """Hash password with bcrypt (cost factor 12)."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    """Verify password against bcrypt hash."""
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength.
    Returns (is_valid, list_of_errors).
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if len(password) > 128:
        errors.append("Password must not exceed 128 characters")
    
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")
    
    if not any(not c.isalnum() for c in password):
        errors.append("Password must contain at least one special character")
    
    if password.lower() in COMMON_PASSWORDS:
        errors.append("Password is too common. Please choose a more unique password")
    
    # Check for sequential characters
    for i in range(len(password) - 2):
        if (ord(password[i+1]) == ord(password[i]) + 1 and 
            ord(password[i+2]) == ord(password[i]) + 2):
            errors.append("Password contains sequential characters")
            break
    
    return len(errors) == 0, errors


def validate_password_change(old_password: str, new_password: str, current_hash: str) -> tuple[bool, list[str]]:
    """Validate password change request."""
    errors = []
    
    if not verify_password(old_password, current_hash):
        errors.append("Current password is incorrect")
    
    if old_password == new_password:
        errors.append("New password must be different from current password")
    
    is_valid, errors = validate_password_strength(new_password)
    return len(errors) == 0, errors