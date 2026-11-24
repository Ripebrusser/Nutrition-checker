"""Authentication package."""

from app.auth.password import hash_password, verify_password, validate_password_strength
from app.auth.session import (
    create_access_token, 
    decode_token, 
    create_user_token, 
    decode_user_token,
    is_token_expired
)
from app.auth.session_manager import SessionManager
from app.auth.dependencies import (
    init_auth_state,
    get_current_user,
    require_auth,
    login_user,
    logout_user,
    get_access_token,
    is_authenticated,
    get_user_id,
    get_user_profile,
    login_user,
)

__all__ = [
    # Password
    "hash_password",
    "verify_password",
    "validate_password_strength",
    "validate_password_change",
    # Session
    "create_access_token",
    "decode_token",
    "create_user_token",
    "decode_user_token",
    "is_token_expired",
    # Session Manager
    "SessionManager",
    # Dependencies
    "init_auth_state",
    "get_current_user",
    "require_auth",
    "login_user",
    "logout_user",
    "get_access_token",
    "is_authenticated",
    "get_user_id",
    "get_user_profile",
]