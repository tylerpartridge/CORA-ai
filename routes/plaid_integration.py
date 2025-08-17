#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/plaid_integration.py
🎯 PURPOSE: Plaid integration API endpoints for bank account connection and transaction sync
🔗 IMPORTS: FastAPI router, HTTP exceptions, dependencies
📤 EXPORTS: plaid_router
"""

import logging
import traceback
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json
from datetime import datetime

from models import get_db
from models.plaid_integration import PlaidIntegration, PlaidAccount, PlaidTransaction, PlaidSyncHistory
from dependencies.auth import get_current_user
from services.plaid_service import PlaidService
from config import config as app_config
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid.api import plaid_api

# Create router
plaid_router = APIRouter(
    prefix="/api/integrations/plaid",
    tags=["Plaid Integration"],
    responses={404: {"description": "Not found"}},
)

def format_phone_for_plaid(phone: str) -> str:
    """
    Intelligently format phone number for Plaid's requirements.
    Plaid typically expects: 10 digits (no country code, no formatting)
    """
    # Remove all non-digit characters
    digits_only = ''.join(filter(str.isdigit, phone))
    
    # Handle different input formats
    if len(digits_only) == 11 and digits_only.startswith('1'):
        # US number with country code: 1-415-555-2671 -> 4155552671
        return digits_only[1:]
    elif len(digits_only) == 10:
        # Already correct format: 4155552671
        return digits_only
    elif len(digits_only) == 7:
        # Local number, assume 415 area code for sandbox
        return f"415{digits_only}"
    else:
        # For sandbox testing, return the standard test number
        return "4155552671"

def create_plaid_link_token(client_user_id: str) -> str:
    """
    Create a Plaid link token
    """
    try:
        # Initialize Plaid client
        configuration = Configuration(
            host="https://sandbox.plaid.com" if app_config.PLAID_ENV == "sandbox" else "https://production.plaid.com",
            api_key={
                'clientId': app_config.PLAID_CLIENT_ID,
                'secret': app_config.PLAID_SECRET,
            }
        )
        
        api_client = ApiClient(configuration)
        api_instance = plaid_api.PlaidApi(api_client)
        
        # Create link token request
        link_token_request = LinkTokenCreateRequest(
            products=[Products("transactions")],
            client_name="CORA AI",
            country_codes=[CountryCode("US"), CountryCode("CA")],  # Support both US and Canadian banks
            language="en",
            user=LinkTokenCreateRequestUser(
                client_user_id=client_user_id
            )
        )
        
        # Create link token
        response = api_instance.link_token_create(link_token_request)
        return response.link_token
        
    except Exception as e:
        logging.error(f"Failed to create link token: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to create link token: {str(e)}")

# Request/Response models
class PlaidLinkTokenRequest(BaseModel):
    """Request model for creating Plaid link token"""
    user_id: int

class PlaidAccessTokenRequest(BaseModel):
    """Request model for exchanging public token"""
    public_token: str
    metadata: Optional[dict] = None

class PlaidSyncRequest(BaseModel):
    """Request model for transaction sync"""
    days_back: Optional[int] = 30

class PlaidSyncResponse(BaseModel):
    """Response model for sync operations"""
    success: bool
    synced_count: int
    errors: List[str] = []
    sync_history: List[dict] = []

class PlaidStatusResponse(BaseModel):
    """Response model for integration status"""
    is_connected: bool
    institution_name: Optional[str] = None
    last_sync_at: Optional[datetime] = None
    total_transactions_synced: int = 0
    total_amount_synced: float = 0.0
    auto_sync_enabled: bool = True
    account_count: int = 0

@plaid_router.post("/link-token")
async def create_link_token(
    request: Request,
    db: Session = Depends(get_db)
):
    """Create Plaid link token for connecting bank account"""
    try:
        import os
        import plaid
        from plaid.api import plaid_api
        from plaid.model.link_token_create_request import LinkTokenCreateRequest
        from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
        from plaid.model.products import Products
        from plaid.model.country_code import CountryCode
        
        # Get request body
        body = await request.json()
        client_user_id = body.get('client_user_id', 'test-user')
        
        # Initialize Plaid client
        from plaid.configuration import Configuration
        
        configuration = Configuration(
            host="https://sandbox.plaid.com" if app_config.PLAID_ENV == "sandbox" else "https://production.plaid.com",
            api_key={
                'clientId': app_config.PLAID_CLIENT_ID,
                'secret': app_config.PLAID_SECRET,
            }
        )
        
        from plaid.api_client import ApiClient
        api_client = ApiClient(configuration)
        plaid_api_client = plaid_api.PlaidApi(api_client)
        
        # Create link token request
        link_token_request = LinkTokenCreateRequest(
            products=[Products("transactions")],
            client_name="CORA AI",
            country_codes=[CountryCode("US")],
            language="en",
            user=LinkTokenCreateRequestUser(
                client_user_id=client_user_id
            )
        )
        
        # Create link token
        response = plaid_api_client.link_token_create(link_token_request)
        
        return {
            "link_token": response.link_token,
            "expiration": response.expiration.isoformat() if response.expiration else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create link token: {str(e)}"
        )

@plaid_router.post("/exchange-token")
async def exchange_public_token(
    request: Request,
    db: Session = Depends(get_db)
):
    """Exchange public token for access token"""
    try:
        # Get request body
        body = await request.json()
        public_token = body.get('public_token')
        metadata = body.get('metadata', {})
        
        # Initialize Plaid client
        configuration = Configuration(
            host="https://sandbox.plaid.com" if app_config.PLAID_ENV == "sandbox" else "https://production.plaid.com",
            api_key={
                'clientId': app_config.PLAID_CLIENT_ID,
                'secret': app_config.PLAID_SECRET,
            }
        )
        
        api_client = ApiClient(configuration)
        api_instance = plaid_api.PlaidApi(api_client)
        
        # Exchange public token
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        
        response = api_instance.item_public_token_exchange(exchange_request)
        
        # Import necessary models
        from plaid.model.item_get_request import ItemGetRequest
        from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
        from plaid.model.institutions_get_by_id_request_options import InstitutionsGetByIdRequestOptions
        
        # Get item info
        item_request = ItemGetRequest(
            access_token=response.access_token
        )
        
        item_response = api_instance.item_get(item_request)
        
        # Get institution info
        institution_request = InstitutionsGetByIdRequest(
            institution_id=item_response.item.institution_id,
            country_codes=[CountryCode("US")],
            options=InstitutionsGetByIdRequestOptions(
                include_optional_metadata=True
            )
        )
        
        institution_response = api_instance.institutions_get_by_id(institution_request)
        institution = institution_response.institution
        
        # Create integration record (using test user for now)
        integration = PlaidIntegration(
            user_id=1,  # Using test user ID
            access_token=response.access_token,
            item_id=response.item_id,
            institution_id=item_response.item.institution_id,
            institution_name=institution.name,
            institution_logo=institution.logo if institution.logo else None,
            institution_primary_color=institution.primary_color if institution.primary_color else None
        )
        
        db.add(integration)
        db.commit()
        db.refresh(integration)
        
        # Sync accounts
        plaid_service = PlaidService(integration)
        account_sync_result = plaid_service.sync_accounts_to_cora(db)
        
        # Also sync transactions for the last 90 days
        transaction_sync_result = plaid_service.sync_transactions_to_cora(db, days_back=90)
        
        return {
            "success": True,
            "integration_id": integration.id,
            "institution_name": integration.institution_name,
            "accounts_synced": account_sync_result.get("synced_count", 0),
            "transactions_synced": transaction_sync_result.get("synced_count", 0),
            "message": f"Connected {integration.institution_name} and synced {transaction_sync_result.get('synced_count', 0)} transactions"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to exchange token: {str(e)}"
        )

@plaid_router.get("/status")
async def get_integration_status(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Plaid integration status"""
    try:
        integration = db.query(PlaidIntegration).filter(
            PlaidIntegration.user_id == current_user,
            PlaidIntegration.is_active == True
        ).first()
        
        if not integration:
            return PlaidStatusResponse(is_connected=False)
        
        # Get account count
        account_count = db.query(PlaidAccount).filter(
            PlaidAccount.integration_id == integration.id
        ).count()
        
        return PlaidStatusResponse(
            is_connected=True,
            institution_name=integration.institution_name,
            last_sync_at=integration.last_sync_at,
            total_transactions_synced=integration.total_transactions_synced,
            total_amount_synced=integration.total_amount_synced,
            auto_sync_enabled=integration.auto_sync,
            account_count=account_count
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get integration status: {str(e)}"
        )

@plaid_router.get("/accounts")
async def get_accounts(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get connected bank accounts"""
    try:
        integration = db.query(PlaidIntegration).filter(
            PlaidIntegration.user_id == current_user,
            PlaidIntegration.is_active == True
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=400,
                detail="Plaid integration not found"
            )
        
        accounts = db.query(PlaidAccount).filter(
            PlaidAccount.integration_id == integration.id
        ).all()
        
        return {
            "accounts": [
                {
                    "id": account.id,
                    "name": account.display_name,
                    "type": account.account_type,
                    "subtype": account.account_subtype,
                    "current_balance": account.current_balance,
                    "available_balance": account.available_balance,
                    "currency": account.iso_currency_code,
                    "verification_status": account.verification_status,
                    "last_sync_at": account.last_sync_at,
                    "is_sync_enabled": account.is_sync_enabled
                }
                for account in accounts
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get accounts: {str(e)}"
        )

@plaid_router.post("/sync")
async def sync_transactions(
    request: PlaidSyncRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync transactions from Plaid"""
    try:
        # Get user's integration
        integration = db.query(PlaidIntegration).filter(
            PlaidIntegration.user_id == current_user,
            PlaidIntegration.is_active == True
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=400,
                detail="Plaid integration not found"
            )
        
        # Initialize Plaid service
        plaid_service = PlaidService(integration)
        
        # Sync transactions
        result = plaid_service.sync_transactions_to_cora(db, days_back=request.days_back or 30)
        
        return PlaidSyncResponse(
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

@plaid_router.get("/sync/history")
async def get_sync_history(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100)
):
    """Get Plaid sync history"""
    try:
        integration = db.query(PlaidIntegration).filter(
            PlaidIntegration.user_id == current_user,
            PlaidIntegration.is_active == True
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=400,
                detail="Plaid integration not found"
            )
        
        # Get sync history
        history = db.query(PlaidSyncHistory).filter(
            PlaidSyncHistory.integration_id == integration.id
        ).order_by(PlaidSyncHistory.created_at.desc()).limit(limit).all()
        
        return {
            "sync_history": [
                {
                    "id": h.id,
                    "sync_type": h.sync_type,
                    "plaid_transaction_id": h.plaid_transaction_id,
                    "sync_status": h.sync_status,
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

@plaid_router.get("/transactions")
async def get_transactions(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    account_id: Optional[int] = Query(None)
):
    """Get recent Plaid transactions"""
    try:
        integration = db.query(PlaidIntegration).filter(
            PlaidIntegration.user_id == current_user,
            PlaidIntegration.is_active == True
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=400,
                detail="Plaid integration not found"
            )
        
        # Build query
        query = db.query(PlaidTransaction).join(PlaidAccount).filter(
            PlaidAccount.integration_id == integration.id
        )
        
        if account_id:
            query = query.filter(PlaidAccount.id == account_id)
        
        transactions = query.order_by(PlaidTransaction.date.desc()).limit(limit).all()
        
        return {
            "transactions": [
                {
                    "id": t.id,
                    "plaid_transaction_id": t.plaid_transaction_id,
                    "amount": t.amount,
                    "currency": t.currency,
                    "date": t.date,
                    "name": t.name,
                    "merchant_name": t.merchant_name,
                    "category": t.display_category,
                    "pending": t.pending,
                    "is_expense": t.is_expense,
                    "is_synced_to_cora": t.is_synced_to_cora,
                    "account_name": t.account.display_name
                }
                for t in transactions
            ],
            "count": len(transactions)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get transactions: {str(e)}"
        )

@plaid_router.delete("/disconnect")
async def disconnect_integration(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect Plaid integration"""
    try:
        integration = db.query(PlaidIntegration).filter(
            PlaidIntegration.user_id == current_user,
            PlaidIntegration.is_active == True
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=400,
                detail="Plaid integration not found"
            )
        
        # Deactivate integration
        integration.is_active = False
        db.commit()
        
        return {"message": "Plaid integration disconnected successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to disconnect integration: {str(e)}"
        ) 