"""Authentication API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from datetime import timedelta

from app.db.session import get_db
from app.db.models import User
from app.auth.password import hash_password, verify_password
from app.auth.session import create_access_token, create_token_pair
from app.auth.dependencies import get_current_user

router = APIRouter()


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        if not any(c in "!@#$%^&*(),.?\":{}|<>" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    hashed_password = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        role="USER",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create access token
    token_data = create_token_pair(user.id, user.email)

    return TokenResponse(
        access_token=token_data["access_token"],
        token_type=token_data["token_type"],
        user={"id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role},
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Login user and return access token."""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled",
        )

    # Create access token
    token_data = create_token_pair(user.id, user.email)

    # Set HttpOnly cookie for additional security
    response.set_cookie(
        key="access_token",
        value=token_data["access_token"],
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=60 * 60 * 24 * 7,  # 7 days
    )

    return TokenResponse(
        access_token=token_data["access_token"],
        token_type=token_data["token_type"],
        user={"id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role},
    )


@router.post("/logout")
async def logout(response: Response):
    """Logout user by clearing cookie."""
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh access token."""
    token_data = create_token_pair(current_user.id, current_user.email)
    return TokenResponse(
        access_token=token_data["access_token"],
        token_type=token_data["token_type"],
        user={"id": current_user.id, "email": current_user.email, "full_name": current_user.full_name, "role": current_user.role},
    )