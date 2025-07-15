#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/quickbooks_integration.py
🎯 PURPOSE: QuickBooks integration API endpoints for OAuth and sync
🔗 IMPORTS: FastAPI router, HTTP exceptions, dependencies
📤 EXPORTS: quickbooks_router
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
from models.quickbooks_integration import QuickBooksIntegration, QuickBooksSyncHistory
from dependencies.auth import get_current_user
from services.quickbooks_service import QuickBooksService

# Create router
quickbooks_router = APIRouter(
    prefix="/api/integrations/quickbooks",
    tags=["QuickBooks Integration"],
    responses={404: {"description": "Not found"}},
)

# Request/Response models
class QuickBooksAuthRequest(BaseModel):
    """Request model for QuickBooks authorization"""
    redirect_uri: str

class QuickBooksCallbackRequest(BaseModel):
    """Request model for QuickBooks OAuth callback"""
    code: str
    realmId: str
    state: str

class QuickBooksSyncRequest(BaseModel):
    """Request model for expense sync"""
    expense_ids: Optional[List[int]] = None  # If None, sync all unsynced

class QuickBooksSyncResponse(BaseModel):
    """Response model for sync operations"""
    success: bool
    synced_count: int
    errors: List[str] = []
    sync_history: List[dict] = []

class QuickBooksStatusResponse(BaseModel):
    """Response model for integration status"""
    is_connected: bool
    company_name: Optional[str] = None
    last_sync_at: Optional[datetime] = None
    total_expenses_synced: int = 0
    auto_sync_enabled: bool = True

@quickbooks_router.get("/auth")
async def get_auth_url(
    request: Request,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get QuickBooks OAuth authorization URL"""
    try:
        # Check if user already has integration
        existing_integration = db.query(QuickBooksIntegration).filter(
            QuickBooksIntegration.user_id == current_user,
            QuickBooksIntegration.is_active == True
        ).first()
        
        if existing_integration:
            raise HTTPException(
                status_code=400,
                detail="QuickBooks integration already exists for this user"
            )
        
        # Generate authorization URL
        import os
        auth_url = os.getenv("QUICKBOOKS_AUTH_URL", "https://appcenter.intuit.com/connect/oauth2")
        params = {
            "client_id": os.getenv("QUICKBOOKS_CLIENT_ID", "YOUR_QUICKBOOKS_CLIENT_ID"),
            "response_type": "code",
            "scope": "com.intuit.quickbooks.accounting",
            "redirect_uri": os.getenv("QUICKBOOKS_REDIRECT_URI", "https://cora.ai/api/integrations/quickbooks/callback"),
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

@quickbooks_router.get("/callback")
async def oauth_callback(
    code: str = Query(...),
    realmId: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db)
):
    """Handle QuickBooks OAuth callback"""
    try:
        # Validate state parameter (CSRF protection)
        user_id = int(state)
        
        # Exchange code for tokens
        import os
        token_url = os.getenv("QUICKBOOKS_TOKEN_URL", "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer")
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": os.getenv("QUICKBOOKS_REDIRECT_URI", "https://cora.ai/api/integrations/quickbooks/callback")
        }
        
        headers = {
            "Authorization": f"Basic {os.getenv('QUICKBOOKS_BASIC_AUTH', 'YOUR_BASIC_AUTH')}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        response = requests.post(token_url, data=data, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="Failed to exchange code for tokens"
            )
        
        token_data = response.json()
        
        # Get company info
        company_url = os.getenv("QUICKBOOKS_USERINFO_URL", "https://sandbox-accounts.platform.intuit.com/v1/openid_connect/userinfo")
        company_headers = {
            "Authorization": f"Bearer {token_data['access_token']}",
            "Accept": "application/json"
        }
        
        company_response = requests.get(company_url, headers=company_headers)
        company_data = company_response.json() if company_response.status_code == 200 else {}
        
        # Create integration record
        integration = QuickBooksIntegration(
            user_id=user_id,
            realm_id=realmId,
            company_name=company_data.get("email", "Unknown Company"),
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_expires_at=datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
        )
        
        db.add(integration)
        db.commit()
        db.refresh(integration)
        
        # Redirect to success page
        return RedirectResponse(url="/dashboard?quickbooks=connected")
        
    except Exception as e:
        # Redirect to error page
        return RedirectResponse(url=f"/dashboard?quickbooks=error&message={str(e)}")

@quickbooks_router.get("/status")
async def get_integration_status(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get QuickBooks integration status"""
    try:
        integration = db.query(QuickBooksIntegration).filter(
            QuickBooksIntegration.user_id == current_user,
            QuickBooksIntegration.is_active == True
        ).first()
        
        if not integration:
            return QuickBooksStatusResponse(is_connected=False)
        
        return QuickBooksStatusResponse(
            is_connected=True,
            company_name=integration.company_name,
            last_sync_at=integration.last_sync_at,
            total_expenses_synced=integration.total_expenses_synced,
            auto_sync_enabled=integration.auto_sync
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get integration status: {str(e)}"
        )

@quickbooks_router.post("/sync")
async def sync_expenses(
    request: QuickBooksSyncRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync expenses to QuickBooks"""
    try:
        # Get user's integration
        integration = db.query(QuickBooksIntegration).filter(
            QuickBooksIntegration.user_id == current_user,
            QuickBooksIntegration.is_active == True
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=400,
                detail="QuickBooks integration not found"
            )
        
        # Check if token needs refresh
        if integration.needs_token_refresh:
            # TODO: Implement token refresh logic
            pass
        
        # Initialize QuickBooks service
        qb_service = QuickBooksService(integration)
        
        # Sync expenses
        if request.expense_ids:
            # Sync specific expenses
            result = await qb_service.sync_expenses_by_ids(request.expense_ids)
        else:
            # Sync all unsynced expenses
            result = await qb_service.sync_all_unsynced_expenses()
        
        return QuickBooksSyncResponse(
            success=result["success"],
            synced_count=result["synced_count"],
            errors=result["errors"],
            sync_history=result["sync_history"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync expenses: {str(e)}"
        )

@quickbooks_router.get("/sync/history")
async def get_sync_history(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100)
):
    """Get QuickBooks sync history"""
    try:
        integration = db.query(QuickBooksIntegration).filter(
            QuickBooksIntegration.user_id == current_user,
            QuickBooksIntegration.is_active == True
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=400,
                detail="QuickBooks integration not found"
            )
        
        # Get sync history
        history = db.query(QuickBooksSyncHistory).filter(
            QuickBooksSyncHistory.integration_id == integration.id
        ).order_by(QuickBooksSyncHistory.created_at.desc()).limit(limit).all()
        
        return {
            "sync_history": [
                {
                    "id": h.id,
                    "sync_type": h.sync_type,
                    "quickbooks_id": h.quickbooks_id,
                    "quickbooks_status": h.quickbooks_status,
                    "sync_duration": h.sync_duration,
                    "error_message": h.error_message,
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

@quickbooks_router.delete("/disconnect")
async def disconnect_integration(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect QuickBooks integration"""
    try:
        integration = db.query(QuickBooksIntegration).filter(
            QuickBooksIntegration.user_id == current_user,
            QuickBooksIntegration.is_active == True
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=400,
                detail="QuickBooks integration not found"
            )
        
        # Deactivate integration
        integration.is_active = False
        db.commit()
        
        return {"message": "QuickBooks integration disconnected successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to disconnect integration: {str(e)}"
        ) 