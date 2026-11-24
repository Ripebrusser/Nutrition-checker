# Phase 6: Authentication and Security Report

**Date:** 2026-11-19  
**Status:** Design Complete

---

## 1. Authentication Architecture

### 1.1 Authentication Flow

```
┌─────────┐     ┌─────────────┐     ┌──────────────┐     ┌────────────┐
│ Client  │────▶│  /login POST  │────▶│ Verify creds │────▶│ Issue JWT  │
│ Browser │     │  email/pass   │     │ bcrypt check │     │ (HS256)    │
└─────────┘     └─────────────┘     └──────────────┘     └────────────┘
       │                                    │                    │
       │         ┌──────────────────────────┘                    │
       │         ▼                                                 ▼
       │  ┌─────────────┐                                ┌─────────────┐
       │  │ Set cookie  │                                │  Return     │
       │  │ (HttpOnly,  │                                │  {token,    │
       │  │ Secure,     │                                │   user}     │
       │  │ SameSite)   │                                └─────────────┘
       │  └─────────────┘
       │
       ▼
┌─────────────────┐
│ Subsequent      │
│ Requests        │
└─────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Authorization Header: Bearer <token>│
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Middleware:                         │
│ 1. Extract token                    │
│ 2. Verify signature (HS256)         │
│ 3. Check expiration                 │
│ 4. Load user from DB                │
│ 5. Attach to request.state          │
└─────────────────────────────────────┘
```

### 1.2 Token Specification

| Property | Value |
|----------|-------|
| Algorithm | HS256 |
| Payload | `{sub: user_id, email, role, exp, iat}` |
| Expiration | 7 days (configurable) |
| Refresh | Not implemented (extend on activity) |
| Storage | HttpOnly, Secure, SameSite=Lax cookie |

---

## 2. Password Security

### 2.1 Hashing

```python
# app/auth/password.py
import bcrypt

def hash_password(password: str) -> str:
    """Hash password with bcrypt (cost factor 12)."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode()

def verify_password(plain: str, hashed: str) -> bool:
    """Verify password against bcrypt hash."""
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
```

### 2.2 Password Policy

| Rule | Requirement |
|------|-------------|
| Minimum length | 8 characters |
| Maximum length | 128 characters |
| Complexity | At least 1 uppercase, 1 lowercase, 1 digit |
| Common passwords | Rejected (check against top 1000) |
| History | Prevent reuse of last 5 passwords |

---

## 3. Session Management

### 3.1 JWT Claims

```json
{
  "sub": "123",
  "email": "user@example.com",
  "role": "USER",
  "iat": 1700000000,
  "exp": 1700604800
}
```

### 3.2 Token Lifecycle

| Event | Action |
|-------|--------|
| Login | Issue new access token (7 days) |
| Request | Verify signature, check exp, load user |
| Activity | Extend exp if >50% elapsed (sliding window) |
| Logout | Add token to blocklist (optional) |
| Password change | Invalidate all user sessions |

### 3.3 Cookie Configuration

```python
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,        # No JS access
    secure=True,          # HTTPS only (production)
    samesite="lax",       # CSRF protection
    max_age=60*60*24*7,   # 7 days
    path="/"
)
```

---

## 4. Authorization

### 4.1 Role-Based Access Control

| Role | Permissions |
|------|-------------|
| USER | Own profile, meal plans, recipes, recommendations |
| ADMIN | All user data, system config, audit logs (future) |

### 4.2 Resource-Based Access

| Resource | Owner Check | Admin Override |
|----------|-------------|----------------|
| Profile | user_id == current_user.id | Yes |
| Meal Plan | meal_plan.user_id == current_user.id | Yes |
| Saved Recipe | saved_recipe.user_id == current_user.id | Yes |
| Meal Completion | meal_plan_item.meal_plan.user_id == current_user.id | Yes |

### 4.3 Dependency Injection (FastAPI/Streamlit)

```python
# app/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if not payload:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user or not user.is_active:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

---

## 4. Input Validation & Sanitization

### 4.1 Request Validation (Pydantic)

```python
# app/models/user.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import date

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=255)
    
    @validator('password')
    def password_complexity(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ProfileUpdate(BaseModel):
    height_cm: Optional[float] = Field(None, ge=50, le=250)
    weight_kg: Optional[float] = Field(None, ge=2, le=300)
    age_years: Optional[int] = Field(None, ge=1, le=120)
    sex: Optional[str] = Field(None, pattern="^(MALE|FEMALE)$")
    dietary_preference: Optional[str] = Field(None, pattern="^(OMNIVORE|VEGETARIAN|VEGAN|EGGETARIAN|JAIN|PESCATARIAN|FLEXITARIAN)$")
    allergies: Optional[List[str]] = None
    ingredient_exclusions: Optional[List[str]] = None
    # ... other fields
```

### 4.2 SQL Injection Prevention

- **ORM Only**: All queries through SQLAlchemy ORM
- **Parameterized Queries**: No string interpolation in SQL
- **Input Sanitization**: Pydantic validators on all inputs

### 4.3 XSS Prevention

```python
# Streamlit auto-escapes by default
# For custom HTML:
import html
safe_content = html.escape(user_input)
st.markdown(safe_content)  # Not st.markdown(unsafe_allow_html=True)
```

---

## 5. Secure Headers (Streamlit Config)

```python
# app/main.py
import streamlit as st

st.set_page_config(
    page_title="Indian Nutrition & Diet Planner",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Add security headers via custom component or middleware
# Note: Streamlit has limited header control; use reverse proxy in production
```

---

## 6. Data Protection

### 6.1 Sensitive Data Handling

| Data | Protection |
|------|------------|
| Passwords | bcrypt hash (never logged) |
| JWT Tokens | HttpOnly cookies; not in localStorage |
| Health Data | Encrypted at rest (future); access-controlled |
| PII (email, name) | Minimal collection; user-controlled deletion |
| Session Tokens | HttpOnly, Secure, SameSite cookies |

### 6.2 Data Retention

| Data Type | Retention | Deletion Trigger |
|-----------|-----------|------------------|
| User account | Indefinite | User deletion request |
| Session tokens | 7 days | Expiration / logout |
| Meal plans | Indefinite | User deletion / manual archive |
| Recipe interactions | 2 years | Automatic cleanup |
| Audit logs | 1 year | Automatic rotation |

### 6.3 Right to Deletion

```python
# app/services/user_service.py
def delete_user(user_id: int, db: Session) -> bool:
    """Cascade delete user and all associated data."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    
    # Cascade deletes handled by SQLAlchemy relationships
    db.delete(user)
    db.commit()
    return True
```

---

## 7. Security Limitations (Academic Deployment)

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **No HTTPS in dev** | Tokens sent in cleartext locally | Document; use HTTPS in production |
| **Single-server sessions** | No distributed session store | Acceptable for demo |
| **No rate limiting** | Brute-force possible on login | Add in production |
| **No CSP headers** | XSS risk if HTML injected | Streamlit auto-escapes; no custom HTML |
| **SQLite file permissions** | Local file access | OS-level permissions |
| **No audit logging** | No trail of sensitive actions | Add in production |

### 7.1 Production Hardening Checklist

- [ ] Enable HTTPS (TLS 1.3)
- [ ] Configure reverse proxy (nginx) with security headers
- [ ] Implement rate limiting (login, API)
- [ ] Add Content Security Policy headers
- [ ] Enable audit logging for sensitive actions
- [ ] Implement refresh token rotation
- [ ] Add 2FA support
- [ ] Regular security scanning
- [ ] Penetration testing
- [ ] Data encryption at rest (SQLCipher or PostgreSQL + pgcrypto)

---

*End of Authentication and Security Report*