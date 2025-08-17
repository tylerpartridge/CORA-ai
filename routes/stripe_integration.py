#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/stripe_integration.py
🎯 PURPOSE: Stripe integration API endpoints for OAuth and transaction sync
🔗 IMPORTS: FastAPI router, HTTP exceptions, dependencies
📤 EXPORTS: stripe_router
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import requests
import json
from datetime import datetime, timedelta

from models import get_db
from models.stripe_integration import StripeIntegration, StripeSyncHistory
from dependencies.auth import get_current_user
from services.stripe_service import StripeService

# Create router
stripe_router = APIRouter(
    prefix="/api/integrations/stripe",
    tags=["Stripe Integration"],
    responses={404: {"description": "Not found"}},
)

# Request/Response models
class StripeAuthRequest(BaseModel):
    """Request model for Stripe authorization"""
    redirect_uri: str

class StripeCallbackRequest(BaseModel):
    """Request model for Stripe OAuth callback"""
    code: str
    state: str

class StripeSyncRequest(BaseModel):
    """Request model for transaction sync"""
    limit: Optional[int] = 100

class StripeSyncResponse(BaseModel):
    """Response model for sync operations"""
    success: bool
    synced_count: int
    errors: List[str] = []
    sync_history: List[dict] = []

class StripeStatusResponse(BaseModel):
    """Response model for integration status"""
    is_connected: bool
    business_name: Optional[str] = None
    last_sync_at: Optional[datetime] = None
    total_transactions_synced: int = 0
    total_amount_synced: float = 0.0
    auto_sync_enabled: bool = True

@stripe_router.get("/auth")
async def get_auth_url(
    request: Request,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Stripe OAuth authorization URL"""
    try:
        import os
        # Check if user already has integration
        existing_integration = db.query(StripeIntegration).filter(
            StripeIntegration.user_id == current_user,
            StripeIntegration.is_active == True
        ).first()
        
        if existing_integration:
            raise HTTPException(
                status_code=400,
                detail="Stripe integration already exists for this user"
            )
        
        # Import centralized config
        from config import config
        
        # Generate authorization URL
        auth_url = "https://connect.stripe.com/oauth/authorize"
        params = {
            "client_id": config.STRIPE_API_KEY,
            "response_type": "code",
            "scope": "read_write",
            "redirect_uri": f"{config.BASE_URL}/api/integrations/stripe/callback",
            "state": str(current_user)  # CSRF protection
        }
        
        # Build URL with parameters
        from urllib.parse import urlencode
        full_url = f"{auth_url}?{urlencode(params)}"
        
        return {"auth_url": full_url}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate auth URL: {str(e)}"
        )

@stripe_router.get("/callback")
async def oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db)
):
    """Handle Stripe OAuth callback"""
    try:
        import os
        # Validate state parameter (CSRF protection)
        user_id = int(state)
        
        # Import centralized config
        from config import config
        
        # Exchange code for tokens
        token_url = "https://connect.stripe.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_secret": config.STRIPE_API_KEY
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="Failed to exchange code for tokens"
            )
        
        token_data = response.json()
        
        # Get account info
        stripe_service = StripeService(None)  # Temporary for account info
        stripe_service.integration = type('obj', (object,), {
            'access_token': token_data["access_token"]
        })()
        
        account_info = stripe_service.get_account_info()
        
        if "error" in account_info:
            raise HTTPException(
                status_code=400,
                detail="Failed to get account info"
            )
        
        # Create integration record
        integration = StripeIntegration(
            user_id=user_id,
            stripe_account_id=account_info["id"],
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            token_expires_at=datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600)),
            business_name=account_info.get("business_name"),
            business_type=account_info.get("business_type"),
            country=account_info.get("country"),
            email=account_info.get("email")
        )
        
        db.add(integration)
        db.commit()
        db.refresh(integration)
        
        # Redirect to success page
        return RedirectResponse(url="/dashboard?stripe=connected")
        
    except Exception as e:
        # Redirect to error page
        return RedirectResponse(url=f"/dashboard?stripe=error&message={str(e)}")

@stripe_router.get("/status")
async def get_integration_status(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Stripe integration status"""
    try:
        integration = db.query(StripeIntegration).filter(
            StripeIntegration.user_id == current_user,
            StripeIntegration.is_active == True
        ).first()
        
        if not integration:
            return StripeStatusResponse(is_connected=False)
        
        return StripeStatusResponse(
            is_connected=True,
            business_name=integration.business_name,
            last_sync_at=integration.last_sync_at,
            total_transactions_synced=integration.total_transactions_synced,
            total_amount_synced=integration.total_amount_synced,
            auto_sync_enabled=integration.auto_sync
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get integration status: {str(e)}"
        )

@stripe_router.post("/sync")
async def sync_transactions(
    request: StripeSyncRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync transactions from Stripe"""
    try:
        # Get user's integration
        integration = db.query(StripeIntegration).filter(
            StripeIntegration.user_id == current_user,
            StripeIntegration.is_active == True
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=400,
                detail="Stripe integration not found"
            )
        
        # Initialize Stripe service
        stripe_service = StripeService(integration)
        
        # Sync transactions
        result = await stripe_service.sync_all_transactions(db, limit=request.limit or 100)
        
        return StripeSyncResponse(
            success=result["success"],
            synced_count=result["synced_count"],
            errors=result["errors"],
            sync_history=result["sync_history"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync transactions: {str(e)}"
        )

@stripe_router.get("/sync/history")
async def get_sync_history(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100)
):
    """Get Stripe sync history"""
    try:
        integration = db.query(StripeIntegration).filter(
            StripeIntegration.user_id == current_user,
            StripeIntegration.is_active == True
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=400,
                detail="Stripe integration not found"
            )
        
        # Get sync history
        history = db.query(StripeSyncHistory).filter(
            StripeSyncHistory.integration_id == integration.id
        ).order_by(StripeSyncHistory.created_at.desc()).limit(limit).all()
        
        return {
            "sync_history": [
                {
                    "id": h.id,
                    "sync_type": h.sync_type,
                    "stripe_transaction_id": h.stripe_transaction_id,
                    "stripe_status": h.stripe_status,
                    "sync_duration": h.sync_duration,
                    "error_message": h.error_message,
                    "amount": h.amount,
                    "currency": h.currency,
                    "description": h.description,
                    "category": h.category,
                    "created_at": h.created_at
                }
                for h in history
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sync history: {str(e)}"
        )

@stripe_router.get("/transactions")
async def get_transactions(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100)
):
    """Get recent Stripe transactions"""
    try:
        integration = db.query(StripeIntegration).filter(
            StripeIntegration.user_id == current_user,
            StripeIntegration.is_active == True
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=400,
                detail="Stripe integration not found"
            )
        
        # Initialize Stripe service
        stripe_service = StripeService(integration)
        
        # Get transactions
        transactions = stripe_service.get_transactions(limit=limit)
        
        return {
            "transactions": transactions,
            "count": len(transactions)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get transactions: {str(e)}"
        )

@stripe_router.delete("/disconnect")
async def disconnect_integration(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect Stripe integration"""
    try:
        integration = db.query(StripeIntegration).filter(
            StripeIntegration.user_id == current_user,
            StripeIntegration.is_active == True
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=400,
                detail="Stripe integration not found"
            )
        
        # Deactivate integration
        integration.is_active = False
        db.commit()
        
        return {"message": "Stripe integration disconnected successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to disconnect integration: {str(e)}"
        ) 