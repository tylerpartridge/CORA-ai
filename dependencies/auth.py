#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/dependencies/auth.py
🎯 PURPOSE: Authentication dependencies for protected routes
🔗 IMPORTS: FastAPI, services, models
📤 EXPORTS: get_current_user, get_current_active_user
"""

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from models import User, get_db
from services.auth_service import verify_token, get_user_by_email
from config import config

def _get_bearer_token(request: Request) -> str | None:
    """Return token from Authorization header or access_token cookie (fallback)."""
    h = request.headers.get("Authorization")
    if h and h.lower().startswith("bearer "):
        return h.split(" ", 1)[1].strip()
    c = request.cookies.get("access_token")
    if c:
        return c.strip()
    return None

# JWT settings
SECRET_KEY = config.SECRET_KEY or config.get_secure_fallback("SECRET_KEY")
ALGORITHM = config.JWT_ALGORITHM

def decode_token(token: str) -> dict:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise ValueError("Invalid token payload")
        return {"email": email, "payload": payload}
    except JWTError:
        raise ValueError("Invalid token")

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token in cookie"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Get token from header or cookie
    token = _get_bearer_token(request)
    if not token:
        raise credentials_exception
    
    # Verify token and get email
    email = verify_token(token)
    if email is None:
        raise credentials_exception
    
    # Get user from database
    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if current_user.is_active != "true":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require admin privileges for protected routes"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def create_unsubscribe_token(user_id: int) -> str:
    """Create a JWT token for unsubscribe links"""
    from datetime import datetime, timedelta, timezone
    expire = datetime.now(timezone.utc) + timedelta(days=7)  # Token valid for 7 days
    payload = {
        "sub": str(user_id),
        "type": "unsubscribe",
        "exp": expire
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_unsubscribe_token(token: str) -> int:
    """Verify and decode unsubscribe token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "unsubscribe":
            raise ValueError("Invalid token type")
        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("Invalid token payload")
        return int(user_id)
    except JWTError:
        raise ValueError("Invalid or expired token")