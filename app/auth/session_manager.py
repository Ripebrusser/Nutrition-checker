"""Session management with database persistence."""

import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.auth.session import create_access_token, decode_token, is_token_expired
from app.database.models import Session as SessionModel, User
from app.database.session import SessionLocal


class SessionManager:
    """Manage user sessions with database persistence."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_session(self, user: 'User', expires_delta: Optional[timedelta] = None) -> str:
        """Create a new session for a user."""
        if expires_delta is None:
            expires_delta = timedelta(minutes=60 * 24 * 7)  # 7 days
        
        # Create JWT token
        token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": "USER"},
            expires_delta=expires_delta
        )
        
        # Store session in database
        session = SessionModel(
            id=str(uuid.uuid4()),
            user_id=user.id,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=60 * 24 * 7),
            is_active=True
        )
        self.db.add(session)
        self.db.commit()
        
        return token
    
    def validate_session(self, token: str) -> Optional['User']:
        """Validate a session token and return the user if valid."""
        payload = decode_token(token)
        if not payload:
            return None
        
        user_id = int(payload.get("sub", 0))
        if not user_id:
            return None
        
        # Check database for active session
        session = self.db.query(SessionModel).filter(
            SessionModel.id == payload.get("session_id", ""),
            SessionModel.user_id == user_id,
            SessionModel.is_active == True,
            SessionModel.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            return None
        
        # Get user
        user = self.db.query(User).filter(User.id == user_id).first()
        return user
    
    def invalidate_session(self, token: str) -> bool:
        """Invalidate a session (logout)."""
        payload = decode_token(token)
        if not payload:
            return False
        
        session_id = payload.get("session_id")
        if not session_id:
            return False
        
        session = self.db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()
        
        if session:
            session.is_active = False
            self.db.commit()
            return True
        
        return False
    
    def invalidate_all_user_sessions(self, user_id: int) -> int:
        """Invalidate all sessions for a user (e.g., on password change)."""
        count = self.db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.is_active == True
        ).update({"is_active": False})
        self.db.commit()
        return count
    
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions from database."""
        count = self.db.query(SessionModel).filter(
            SessionModel.expires_at < datetime.utcnow(),
            SessionModel.is_active == True
        ).update({"is_active": False})
        self.db.commit()
        return count


def get_current_user_from_token(token: str) -> Optional[int]:
    """Extract user ID from token without database lookup."""
    payload = decode_token(token)
    if not payload:
        return None
    try:
        return int(payload.get("sub", 0))
    except (ValueError, TypeError):
        return None