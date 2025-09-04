#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/user_settings.py
🎯 PURPOSE: User settings API endpoints (timezone and currency)
🔗 IMPORTS: FastAPI, pydantic, models, dependencies
📤 EXPORTS: user_settings_router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Literal
from pydantic import BaseModel, field_validator
from zoneinfo import ZoneInfo
import logging

from models import get_db, User
from dependencies.auth import get_current_user

logger = logging.getLogger(__name__)

# User settings schemas
class UserSettingsIn(BaseModel):
    """Input model for updating user settings"""
    timezone: Optional[str] = None
    currency: Optional[Literal["USD", "CAD"]] = None
    
    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, v: Optional[str]) -> Optional[str]:
        """Validate timezone is a known IANA timezone"""
        if v is None:
            return v
        try:
            ZoneInfo(v)
            return v
        except Exception:
            raise ValueError(f"Invalid timezone: {v}")


class UserSettingsOut(BaseModel):
    """Output model for user settings"""
    timezone: str
    currency: Literal["USD", "CAD"]


# Create router with the exact prefix needed
user_settings_router = APIRouter(
    prefix="/api/user",
    tags=["User Settings"],
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "Not found"}
    },
)


@user_settings_router.get("/settings", response_model=UserSettingsOut)
async def get_user_settings(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's settings (timezone and currency).
    
    Returns:
        UserSettingsOut: Current user settings
    """
    return UserSettingsOut(
        timezone=current_user.timezone or "UTC",
        currency=current_user.currency or "USD"  # type: ignore
    )


@user_settings_router.patch("/settings", response_model=UserSettingsOut)
async def update_user_settings(
    settings: UserSettingsIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's settings (timezone and/or currency).
    
    Args:
        settings: New settings values
        current_user: Authenticated user
        db: Database session
        
    Returns:
        UserSettingsOut: Updated user settings
    """
    try:
        # Update only provided fields
        if settings.timezone is not None:
            current_user.timezone = settings.timezone
        if settings.currency is not None:
            current_user.currency = settings.currency
        
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"Updated settings for user {current_user.email}: "
                   f"timezone={settings.timezone}, currency={settings.currency}")
        
        return UserSettingsOut(
            timezone=current_user.timezone or "UTC",
            currency=current_user.currency or "USD"  # type: ignore
        )
        
    except Exception as e:
        logger.error(f"Error updating settings for user {current_user.email}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to update user settings"
        )