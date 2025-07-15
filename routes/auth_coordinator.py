#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/auth_coordinator.py
🎯 PURPOSE: Authentication routes stub - minimal safe implementation
🔗 IMPORTS: FastAPI router
📤 EXPORTS: auth_router
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from models import get_db, UserPreference
from services.auth_service import (
    authenticate_user, create_access_token, create_user,
    ACCESS_TOKEN_EXPIRE_MINUTES, validate_user_input,
    AuthenticationError, InvalidCredentialsError, 
    UserAlreadyExistsError, ValidationError, PasswordResetError,
    create_password_reset_token, validate_password_reset_token, reset_password_with_token
)
from services.email_service import send_password_reset_email, send_welcome_email
from typing import List, Optional
from dependencies.auth import get_current_user

# Create router
auth_router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)

# Request models
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    confirm_password: str

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str

class PreferenceRequest(BaseModel):
    key: str
    value: str

class PreferenceResponse(BaseModel):
    id: int
    key: str
    value: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class PreferenceBulkUpdate(BaseModel):
    preferences: List[PreferenceRequest]

@auth_router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint with comprehensive error handling"""
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds
        }
        
    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={"errors": e.errors, "message": "Validation failed"}
        )
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e)
        )
    except Exception as e:
        # Log unexpected errors but don't expose details
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )

@auth_router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register endpoint with full error handling"""
    try:
        # Validate input
        validate_user_input(request.email, request.password, request.confirm_password)
        
        # Create user
        user = create_user(db, request.email, request.password)
        
        # Send welcome email
        try:
            send_welcome_email(user.email)
        except Exception as e:
            # Log email failure but don't fail registration
            print(f"Failed to send welcome email to {user.email}: {str(e)}")
        
        # Generate token for immediate login
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return {
            "message": "User registered successfully",
            "email": user.email,
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={"errors": e.errors, "message": "Validation failed"}
        )
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e)
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Registration failed"
        )

@auth_router.post("/logout")
async def logout():
    """Logout endpoint - stub for now"""
    return {"message": "Logged out successfully"}

# User preferences endpoints
@auth_router.get("/preferences", response_model=List[PreferenceResponse])
async def get_preferences(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all preferences for the current user"""
    preferences = db.query(UserPreference).filter(
        UserPreference.user_email == current_user
    ).all()
    return preferences

@auth_router.get("/preferences/{key}", response_model=PreferenceResponse)
async def get_preference(
    key: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific preference by key"""
    preference = db.query(UserPreference).filter(
        UserPreference.user_email == current_user,
        UserPreference.key == key
    ).first()
    
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    
    return preference

@auth_router.put("/preferences/{key}", response_model=PreferenceResponse)
async def update_preference(
    key: str,
    request: PreferenceRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update a preference"""
    # Validate preference key
    allowed_keys = [
        "theme", "language", "timezone", "date_format", 
        "currency", "notifications_email", "notifications_push",
        "dashboard_layout", "expense_view", "report_frequency"
    ]
    
    if key not in allowed_keys:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid preference key. Allowed keys: {', '.join(allowed_keys)}"
        )
    
    # Check if preference exists
    preference = db.query(UserPreference).filter(
        UserPreference.user_email == current_user,
        UserPreference.key == key
    ).first()
    
    if preference:
        # Update existing
        preference.value = request.value
    else:
        # Create new
        preference = UserPreference(
            user_email=current_user,
            key=key,
            value=request.value
        )
        db.add(preference)
    
    db.commit()
    db.refresh(preference)
    return preference

@auth_router.post("/preferences/bulk", response_model=List[PreferenceResponse])
async def bulk_update_preferences(
    request: PreferenceBulkUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update multiple preferences at once"""
    allowed_keys = [
        "theme", "language", "timezone", "date_format", 
        "currency", "notifications_email", "notifications_push",
        "dashboard_layout", "expense_view", "report_frequency"
    ]
    
    updated_preferences = []
    
    for pref in request.preferences:
        if pref.key not in allowed_keys:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid preference key: {pref.key}"
            )
        
        # Check if exists
        existing = db.query(UserPreference).filter(
            UserPreference.user_email == current_user,
            UserPreference.key == pref.key
        ).first()
        
        if existing:
            existing.value = pref.value
            updated_preferences.append(existing)
        else:
            new_pref = UserPreference(
                user_email=current_user,
                key=pref.key,
                value=pref.value
            )
            db.add(new_pref)
            updated_preferences.append(new_pref)
    
    db.commit()
    
    # Refresh all preferences
    for pref in updated_preferences:
        db.refresh(pref)
    
    return updated_preferences

@auth_router.delete("/preferences/{key}")
async def delete_preference(
    key: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a preference"""
    preference = db.query(UserPreference).filter(
        UserPreference.user_email == current_user,
        UserPreference.key == key
    ).first()
    
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    
    db.delete(preference)
    db.commit()
    
    return {"message": f"Preference '{key}' deleted successfully"}

@auth_router.post("/request-password-reset")
async def request_password_reset(
    request: PasswordResetRequest, 
    db: Session = Depends(get_db)
):
    """Request a password reset token"""
    try:
        # Create password reset token
        token = create_password_reset_token(db, request.email)
        
        # Send password reset email if token was created
        if token:
            reset_url = f"https://coraai.tech/reset-password?token={token}"
            try:
                send_password_reset_email(request.email, token, reset_url)
            except Exception as e:
                print(f"Failed to send password reset email to {request.email}: {str(e)}")
        
        # Always return success to prevent email enumeration
        return {
            "message": "If an account with this email exists, a password reset link has been sent",
            "email": request.email
        }
        
    except PasswordResetError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to process password reset request"
        )

@auth_router.post("/reset-password")
async def reset_password(
    request: PasswordResetConfirmRequest,
    db: Session = Depends(get_db)
):
    """Reset password using a valid token"""
    try:
        # Validate new password (we'll get email from token validation)
        validate_user_input("temp@example.com", request.new_password, request.confirm_password)
        
        # Reset password
        success = reset_password_with_token(db, request.token, request.new_password)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired reset token"
            )
        
        # Get email from token for response
        email = validate_password_reset_token(db, request.token)
        
        return {
            "message": "Password reset successfully",
            "email": email if email else "unknown"
        }
        
    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={"errors": e.errors, "message": "Validation failed"}
        )
    except PasswordResetError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to reset password"
        )

@auth_router.get("/validate-reset-token/{token}")
async def validate_reset_token(
    token: str,
    db: Session = Depends(get_db)
):
    """Validate a password reset token"""
    try:
        email = validate_password_reset_token(db, token)
        
        if not email:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired reset token"
            )
        
        return {
            "valid": True,
            "email": email
        }
        
    except PasswordResetError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to validate reset token"
        )