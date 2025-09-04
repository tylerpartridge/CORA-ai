#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/settings_email.py
🎯 PURPOSE: Email subscription settings endpoints split from settings to reduce file size
🔗 IMPORTS: FastAPI, models, dependencies
📤 EXPORTS: email_settings_router
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging

from models import get_db, User
from dependencies.auth import get_current_user

logger = logging.getLogger(__name__)


email_settings_router = APIRouter(
    prefix="/api/settings",
    tags=["Settings"],
    responses={404: {"description": "Not found"}},
)


@email_settings_router.post("/unsubscribe-weekly")
async def unsubscribe_weekly_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        current_user.weekly_insights_opt_in = "false"
        db.commit()
        logger.info(f"User {current_user.email} unsubscribed from weekly insights")
        return JSONResponse(status_code=200, content={"success": True, "message": "Successfully unsubscribed from weekly insights", "weekly_insights_opt_in": False})
    except Exception as e:
        logger.error(f"Error unsubscribing user {current_user.email}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update subscription preferences")


@email_settings_router.post("/subscribe-weekly")
async def subscribe_weekly_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        current_user.weekly_insights_opt_in = "true"
        db.commit()
        logger.info(f"User {current_user.email} subscribed to weekly insights")
        return JSONResponse(status_code=200, content={"success": True, "message": "Successfully subscribed to weekly insights", "weekly_insights_opt_in": True})
    except Exception as e:
        logger.error(f"Error subscribing user {current_user.email}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update subscription preferences")


@email_settings_router.get("/subscription-status")
async def get_subscription_status(
    current_user: User = Depends(get_current_user)
):
    return JSONResponse(status_code=200, content={"weekly_insights_opt_in": getattr(current_user, 'weekly_insights_opt_in', 'true') == 'true'})


