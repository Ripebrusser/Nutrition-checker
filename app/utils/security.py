"""Security utilities."""

import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
from app.config import settings

# Password hashing
def hash_password(password: str) -> str:
    """Hash password with bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    """Verify password against bcrypt hash."""
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

# JWT token handling
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    from app.auth.session import create_access_token
    return create_access_token(data, expires_delta)

def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token."""
    from app.auth.session import decode_token
    return decode_token(token)

def create_user_token(user_id: int, email: str, role: str = "USER") -> str:
    """Create a JWT token for a user."""
    from app.auth.session import create_user_token
    return create_user_token(user_id, email, role)

def decode_user_token(token: str) -> Optional[dict]:
    """Decode token and return user info."""
    from app.auth.session import decode_user_token
    return decode_user_token(token)

def is_token_expired(token: str) -> bool:
    """Check if token is expired."""
    from app.auth.session import is_token_expired
    return is_token_expired(token)