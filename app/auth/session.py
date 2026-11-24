"""Session management with JWT."""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.config import settings

# JWT Configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def create_user_token(user_id: int, email: str, role: str = "USER") -> str:
    """Create a JWT token for a user."""
    data = {
        "sub": str(user_id),
        "email": email,
        "role": role,
    }
    return create_access_token(data)


def decode_user_token(token: str) -> Optional[dict]:
    """Decode token and return user info if valid."""
    payload = decode_token(token)
    if not payload:
        return None
    
    try:
        return {
            "user_id": int(payload.get("sub", 0)),
            "email": payload.get("email"),
            "role": payload.get("role", "USER"),
        }
    except (ValueError, TypeError):
        return None


def is_token_expired(token: str) -> bool:
    """Check if token is expired without raising exception."""
    payload = decode_token(token)
    if not payload:
        return True
    exp = payload.get("exp")
    if not exp:
        return True
    return datetime.utcnow() > datetime.fromtimestamp(exp)