#!/usr/bin/env python3
"""
Example: Upgrading dashboard_routes.py to use Smart Error Handler
This shows how the route would look with better error handling
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import or_
from sqlalchemy.orm import Session
from  import date
from typing import Dict, Any

from models import get_db, User
from dependencies.auth import get_current_user
from utils.smart_error_handler import error_handler, log_info, log_warning

# Create router
dashboard_router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
    responses={404: {"description": "Not found"}},
)

@dashboard_router.get("/plaid-data")
@error_handler.safe_route  # Automatic error handling!
async def get_plaid_dashboard_data(
    request: Request,  # Added for error context
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real Plaid data for dashboard - WITH SMART ERROR HANDLING"""
    
    # Log the request with context
    log_info("Fetching Plaid data", user=current_user, endpoint="plaid-data")
    
    from models.plaid_integration import PlaidIntegration, PlaidAccount
    from services.plaid_service import PlaidService
    
    # Fetch integration
    integration = db.query(PlaidIntegration).filter(
        PlaidIntegration.user_id == current_user,
        PlaidIntegration.is_active == True
    ).first()
    
    if not integration:
        log_info("No Plaid integration found", user=current_user)
        return {
            "connected": False,
            "message": "No bank account connected",
            "accounts": [],
            "transactions": [],
            "summary": {
                "total_balance": 0,
                "total_spending_30d": 0,
                "total_income_30d": 0,
                "transaction_count": 0
            }
        }
    
    # Fetch live balances from Plaid
    plaid_service = PlaidService(integration)
    live_data = await plaid_service.get_balances()
    
    if "error" in live_data:
        # Log warning but don't fail - use cached data
        log_warning(
            "Plaid API error, using cached data",
            user=current_user,
            error=live_data["error"]
        )
        accounts = db.query(PlaidAccount).filter(
            PlaidAccount.integration_id == integration.id
        ).all()
    else:
        # Update balances logic here...
        accounts = process_live_data(live_data, db, integration)
    
    # Calculate metrics
    metrics = calculate_dashboard_metrics(accounts)
    
    log_info(
        "Plaid data fetched successfully",
        user=current_user,
        accounts_count=len(accounts),
        transactions_count=metrics["transaction_count"]
    )
    
    return {
        "connected": True,
        "institution": integration.institution_name,
        "last_sync": integration.last_sync_at.isoformat() if integration.last_sync_at else None,
        "accounts": format_accounts(accounts),
        "transactions": format_transactions(metrics["transactions"]),
        "summary": metrics["summary"]
    }
    # Any exception is automatically caught and handled with context!


# ============================================
# BENEFITS OF THIS APPROACH
# ============================================
"""
1. No more generic try/except blocks
2. Automatic error context capture
3. Structured logging with context
4. Better error messages for users
5. Easier debugging for Sonnet
6. Consistent error responses for GPT-5's frontend
7. Error statistics tracking for monitoring

Example error response if Plaid fails:
{
    "error": {
        "message": "External service unavailable",
        "type": "ConnectionError",
        "suggestion": "External service unavailable - check network/service status"
    }
}

In development, also includes:
- Full traceback
- Request details
- User context
- Timestamp
"""