#!/usr/bin/env python3
"""
[LOCATION] LOCATION: /CORA/tests/test_quickbooks_integration.py
[TARGET] PURPOSE: Test QuickBooks integration OAuth flow and API interactions
[LINK] IMPORTS: pytest, requests, os
[EXPORT] EXPORTS: Test functions for QuickBooks integration
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths


import pytest
import requests
import os
import json
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Test environment setup
def test_environment_variables():
    """Test that required QuickBooks environment variables are set"""
    required_vars = [
        "QUICKBOOKS_CLIENT_ID",
        "QUICKBOOKS_CLIENT_SECRET", 
        "QUICKBOOKS_BASIC_AUTH",
        "QUICKBOOKS_REDIRECT_URI"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        pytest.skip(f"Missing environment variables: {missing_vars}")
    
    assert True, "All required environment variables are set"

def test_oauth_auth_url_generation():
    """Test OAuth authorization URL generation"""
    from routes.quickbooks_integration import get_auth_url
    
    # Mock dependencies
    mock_request = Mock()
    mock_current_user = "test_user_123"
    mock_db = Mock()
    
    # Mock database query
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    with patch('routes.quickbooks_integration.get_current_user', return_value=mock_current_user):
        with patch('routes.quickbooks_integration.get_db', return_value=mock_db):
            result = get_auth_url(mock_request, mock_current_user, mock_db)
    
    assert "auth_url" in result
    assert "appcenter.intuit.com" in result["auth_url"]
    assert "client_id=" in result["auth_url"]
    assert "response_type=code" in result["auth_url"]
    assert "scope=" in result["auth_url"]

def test_oauth_callback_token_exchange():
    """Test OAuth callback token exchange"""
    from routes.quickbooks_integration import oauth_callback
    
    # Mock OAuth response
    mock_token_response = {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token", 
        "expires_in": 3600
    }
    
    # Mock company info response
    mock_company_response = {
        "email": "test@company.com",
        "given_name": "Test",
        "family_name": "Company"
    }
    
    with patch('requests.post') as mock_post:
        with patch('requests.get') as mock_get:
            # Mock token exchange
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_token_response
            
            # Mock company info
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_company_response
            
            # Test callback
            result = oauth_callback(
                code="test_auth_code",
                realmId="test_realm_id", 
                state="123",
                db=Mock()
            )
    
    assert result.status_code == 302  # Redirect response
    assert "quickbooks=connected" in result.headers["location"]

def test_quickbooks_service_initialization():
    """Test QuickBooks service initialization"""
    from services.quickbooks_service import QuickBooksService
    from models.quickbooks_integration import QuickBooksIntegration
    
    # Create mock integration
    mock_integration = Mock(spec=QuickBooksIntegration)
    mock_integration.access_token = "test_token"
    mock_integration.refresh_token = "test_refresh"
    mock_integration.realm_id = "test_realm"
    
    # Initialize service
    service = QuickBooksService(mock_integration)
    
    assert service.integration == mock_integration
    assert "sandbox" in service.api_url
    assert "intuit.com" in service.base_url

def test_token_refresh_logic():
    """Test token refresh functionality"""
    from services.quickbooks_service import QuickBooksService
    from models.quickbooks_integration import QuickBooksIntegration
    
    # Create mock integration with expired token
    mock_integration = Mock(spec=QuickBooksIntegration)
    mock_integration.access_token = "expired_token"
    mock_integration.refresh_token = "test_refresh"
    mock_integration.token_expires_at = datetime.utcnow() - timedelta(hours=1)
    mock_integration.needs_token_refresh = True
    
    # Mock refresh response
    mock_refresh_response = {
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token",
        "expires_in": 3600
    }
    
    service = QuickBooksService(mock_integration)
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_refresh_response
        
        result = service._refresh_token_if_needed()
        
        assert result == True
        assert mock_integration.access_token == "new_access_token"
        assert mock_integration.refresh_token == "new_refresh_token"

def test_category_mapping():
    """Test CORA to QuickBooks category mapping"""
    from services.quickbooks_service import QuickBooksService
    from models.quickbooks_integration import QuickBooksIntegration
    
    mock_integration = Mock(spec=QuickBooksIntegration)
    service = QuickBooksService(mock_integration)
    
    # Test known mappings
    assert service._map_cora_to_quickbooks_category("Office Supplies") == "Office Supplies"
    assert service._map_cora_to_quickbooks_category("Meals & Entertainment") == "Meals and Entertainment"
    assert service._map_cora_to_quickbooks_category("Transportation") == "Automobile"
    
    # Test unknown category
    assert service._map_cora_to_quickbooks_category("Unknown Category") is None

def test_purchase_creation():
    """Test QuickBooks purchase creation"""
    from services.quickbooks_service import QuickBooksService
    from models.quickbooks_integration import QuickBooksIntegration
    from models.expense import Expense
    
    # Create mock integration
    mock_integration = Mock(spec=QuickBooksIntegration)
    mock_integration.access_token = "test_token"
    mock_integration.realm_id = "test_realm"
    
    # Create test expense
    test_expense = Mock(spec=Expense)
    test_expense.amount = 100.00
    test_expense.category = "Office Supplies"
    test_expense.vendor = "Office Depot"
    test_expense.description = "Printer paper"
    test_expense.date = datetime.now()
    
    service = QuickBooksService(mock_integration)
    
    # Mock vendor and account creation
    with patch.object(service, '_get_or_create_vendor', return_value="vendor_123"):
        with patch.object(service, '_get_account_id', return_value="account_456"):
            with patch('requests.post') as mock_post:
                mock_post.return_value.status_code = 200
                mock_post.return_value.json.return_value = {"Purchase": {"Id": "purchase_789"}}
                
                result = service._create_quickbooks_purchase(test_expense)
                
                assert result == "purchase_789"
                assert mock_post.called

def test_connection_testing():
    """Test QuickBooks connection testing"""
    from services.quickbooks_service import QuickBooksService
    from models.quickbooks_integration import QuickBooksIntegration
    
    mock_integration = Mock(spec=QuickBooksIntegration)
    mock_integration.needs_token_refresh = False
    
    service = QuickBooksService(mock_integration)
    
    with patch.object(service, 'get_company_info', return_value={"email": "test@company.com"}):
        result = service.test_connection()
        assert result == True
    
    with patch.object(service, 'get_company_info', return_value={"error": "Invalid token"}):
        result = service.test_connection()
        assert result == False

def test_sync_error_handling():
    """Test error handling during sync operations"""
    from services.quickbooks_service import QuickBooksService
    from models.quickbooks_integration import QuickBooksIntegration
    from models.expense import Expense
    
    mock_integration = Mock(spec=QuickBooksIntegration)
    mock_integration.access_token = "test_token"
    mock_integration.realm_id = "test_realm"
    
    test_expense = Mock(spec=Expense)
    test_expense.id = 123
    test_expense.amount = 100.00
    test_expense.category = "Office Supplies"
    test_expense.vendor = "Office Depot"
    
    service = QuickBooksService(mock_integration)
    
    # Test token refresh failure
    with patch.object(service, '_refresh_token_if_needed', return_value=False):
        result = service.sync_expense(test_expense, Mock())
        assert result["success"] == False
        assert "Token refresh failed" in result["error"]

def test_batch_expense_sync():
    """Test batch expense synchronization"""
    from services.quickbooks_service import QuickBooksService
    from models.quickbooks_integration import QuickBooksIntegration
    from models.expense import Expense
    
    mock_integration = Mock(spec=QuickBooksIntegration)
    mock_integration.user_id = 123
    
    service = QuickBooksService(mock_integration)
    
    # Create mock expenses
    mock_expenses = []
    for i in range(3):
        expense = Mock(spec=Expense)
        expense.id = i + 1
        expense.amount = 100.0 * (i + 1)
        expense.category = "Office Supplies"
        expense.vendor = f"Vendor {i+1}"
        expense.user_id = 123
        mock_expenses.append(expense)
    
    # Mock database
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.all.return_value = mock_expenses
    
    # Mock successful sync
    with patch.object(service, 'sync_expense') as mock_sync:
        mock_sync.return_value = {"success": True, "quickbooks_id": "QB123"}
        
        result = service.sync_all_unsynced_expenses(mock_db)
        
        assert result["success"] == True
        assert result["synced_count"] == 3
        assert len(result["errors"]) == 0

def test_vendor_creation_and_caching():
    """Test vendor creation and caching in QuickBooks"""
    from services.quickbooks_service import QuickBooksService
    from models.quickbooks_integration import QuickBooksIntegration
    
    mock_integration = Mock(spec=QuickBooksIntegration)
    mock_integration.realm_id = "test_realm"
    
    service = QuickBooksService(mock_integration)
    
    # Test new vendor creation
    with patch('requests.get') as mock_get:
        with patch('requests.post') as mock_post:
            # Mock no existing vendor
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"QueryResponse": {"Vendor": []}}
            
            # Mock vendor creation
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"Vendor": {"Id": "new_vendor_123"}}
            
            vendor_id = service._get_or_create_vendor("New Vendor Co")
            
            assert vendor_id == "new_vendor_123"
            assert mock_get.called
            assert mock_post.called

def test_quickbooks_api_rate_limiting():
    """Test rate limiting handling for QuickBooks API"""
    from services.quickbooks_service import QuickBooksService
    from models.quickbooks_integration import QuickBooksIntegration
    
    mock_integration = Mock(spec=QuickBooksIntegration)
    service = QuickBooksService(mock_integration)
    
    # Test rate limit response
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 429  # Too Many Requests
        mock_post.return_value.headers = {"Retry-After": "60"}
        
        # This should handle rate limiting gracefully
        result = service._create_quickbooks_purchase(Mock())
        assert result is None  # Should return None on rate limit

def test_sync_history_recording():
    """Test that sync history is properly recorded"""
    from services.quickbooks_service import QuickBooksService
    from models.quickbooks_integration import QuickBooksIntegration
    from models.quickbooks_integration import QuickBooksSyncHistory
    from models.expense import Expense
    
    mock_integration = Mock(spec=QuickBooksIntegration)
    mock_integration.id = 1
    mock_integration.total_expenses_synced = 0
    
    test_expense = Mock(spec=Expense)
    test_expense.id = 123
    test_expense.amount = 100.00
    
    service = QuickBooksService(mock_integration)
    
    # Mock successful sync
    mock_db = Mock()
    with patch.object(service, '_create_quickbooks_purchase', return_value="QB123"):
        result = service.sync_expense(test_expense, mock_db)
        
        # Verify sync history was recorded
        assert mock_db.add.called
        sync_history_call = mock_db.add.call_args[0][0]
        assert isinstance(sync_history_call, QuickBooksSyncHistory)
        assert sync_history_call.quickbooks_id == "QB123"
        assert sync_history_call.quickbooks_status == "success"

def test_integration_status_endpoint():
    """Test integration status endpoint"""
    from routes.quickbooks_integration import get_integration_status
    from models.quickbooks_integration import QuickBooksIntegration
    
    # Mock database query with no integration
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    with patch('routes.quickbooks_integration.get_current_user', return_value="test_user"):
        with patch('routes.quickbooks_integration.get_db', return_value=mock_db):
            result = get_integration_status("test_user", mock_db)
    
    assert result.is_connected == False
    
    # Mock database query with active integration
    mock_integration = Mock(spec=QuickBooksIntegration)
    mock_integration.company_name = "Test Company"
    mock_integration.last_sync_at = datetime.now()
    mock_integration.total_expenses_synced = 5
    mock_integration.auto_sync = True
    
    mock_db.query.return_value.filter.return_value.first.return_value = mock_integration
    
    with patch('routes.quickbooks_integration.get_current_user', return_value="test_user"):
        with patch('routes.quickbooks_integration.get_db', return_value=mock_db):
            result = get_integration_status("test_user", mock_db)
    
    assert result.is_connected == True
    assert result.company_name == "Test Company"
    assert result.total_expenses_synced == 5

if __name__ == "__main__":
    # Run tests if environment variables are set
    if os.getenv("QUICKBOOKS_CLIENT_ID"):
        pytest.main([__file__, "-v"])
    else:
        print("[WARNING]  QuickBooks environment variables not set. Skipping tests.")
        print("📋 Set up environment variables following docs/quickbooks-test-env.md") 