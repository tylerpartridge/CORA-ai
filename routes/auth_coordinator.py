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
    UserAlreadyExistsError, ValidationError
)
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