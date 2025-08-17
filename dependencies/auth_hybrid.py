#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/dependencies/auth_hybrid.py
🎯 PURPOSE: Hybrid authentication that supports both cookies and headers
🔗 IMPORTS: FastAPI, services, models
📤 EXPORTS: get_current_user_hybrid
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from models import User, get_db
from services.auth_service import verify_token, get_user_by_email

# OAuth2 scheme (optional=True allows it to work without header)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

async def get_current_user_hybrid(
    request: Request,
    token_from_header: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token (cookie or header)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Try to get token from header first
    token = token_from_header
    
    # If no header token, try cookie
    if not token:
        token = request.cookies.get("access_token")
    
    # If still no token, raise exception
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