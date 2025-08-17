#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/services/quickbooks_service.py
🎯 PURPOSE: QuickBooks service for API interactions and expense synchronization
🔗 IMPORTS: Requests, SQLAlchemy, models
📤 EXPORTS: QuickBooksService class
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from models.quickbooks_integration import QuickBooksIntegration, QuickBooksSyncHistory
from models.expense import Expense

logger = logging.getLogger(__name__)

class QuickBooksService:
    """Service for QuickBooks API interactions and expense synchronization"""
    
    def __init__(self, integration: QuickBooksIntegration):
        import os
        self.integration = integration
        self.base_url = os.getenv("QUICKBOOKS_USERINFO_URL", "https://sandbox-accounts.platform.intuit.com").replace("/v1/openid_connect/userinfo", "")
        self.api_url = os.getenv("QUICKBOOKS_API_URL", "https://sandbox-quickbooks.api.intuit.com/v3/company")
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for QuickBooks API requests"""
        return {
            "Authorization": f"Bearer {self.integration.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def _refresh_token_if_needed(self) -> bool:
        """Refresh access token if needed"""
        if not self.integration.needs_token_refresh:
            return True
            
        try:
            import os
            token_url = os.getenv("QUICKBOOKS_TOKEN_URL", "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer")
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.integration.refresh_token
            }
            
            # Import centralized config
            from config import config
            
            headers = {
                "Authorization": f"Basic {config.QUICKBOOKS_CLIENT_SECRET}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            response = requests.post(token_url, data=data, headers=headers)
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Update integration with new tokens
                self.integration.access_token = token_data["access_token"]
                self.integration.refresh_token = token_data["refresh_token"]
                self.integration.token_expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Token refresh failed: {e}")
            return False
    
    async def refresh_access_token(self) -> dict:
        """Refresh access token and return new tokens"""
        try:
            token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
            
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.integration.refresh_token
            }
            
            # Import centralized config
            from config import config
            import base64
            
            # Create Basic Auth header
            credentials = f"{config.QUICKBOOKS_CLIENT_ID}:{config.QUICKBOOKS_CLIENT_SECRET}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }
            
            response = requests.post(token_url, data=data, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            return {
                "access_token": token_data["access_token"],
                "refresh_token": token_data["refresh_token"],
                "expires_in": token_data.get("expires_in", 3600)
            }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"QuickBooks token refresh failed: {str(e)}")
            raise Exception(f"Failed to refresh QuickBooks token: {str(e)}")
    
    def _map_cora_to_quickbooks_category(self, cora_category: str) -> Optional[str]:
        """Map CORA category to QuickBooks account"""
        category_mapping = {
            "Office Supplies": "Office Supplies",
            "Meals & Entertainment": "Meals and Entertainment", 
            "Transportation": "Automobile",
            "Software & Subscriptions": "Computer and Internet Expenses",
            "Marketing & Advertising": "Advertising and Promotion",
            "Shipping & Postage": "Shipping and Delivery",
            "Professional Development": "Professional Development",
            "Travel": "Travel",
            "Utilities": "Utilities",
            "Insurance": "Insurance"
        }
        
        return category_mapping.get(cora_category)
    
    def _get_or_create_vendor(self, vendor_name: str) -> Optional[str]:
        """Get or create vendor in QuickBooks"""
        try:
            # First, try to find existing vendor
            vendor_url = f"{self.api_url}/{self.integration.realm_id}/vendor"
            response = requests.get(vendor_url, headers=self._get_headers())
            
            if response.status_code == 200:
                vendors = response.json().get("QueryResponse", {}).get("Vendor", [])
                for vendor in vendors:
                    if vendor.get("DisplayName", "").lower() == vendor_name.lower():
                        return vendor.get("Id")
            
            # Create new vendor if not found
            vendor_data = {
                "DisplayName": vendor_name,
                "Active": True
            }
            
            response = requests.post(vendor_url, json=vendor_data, headers=self._get_headers())
            
            if response.status_code == 200:
                vendor = response.json().get("Vendor", {})
                return vendor.get("Id")
            
            return None
            
        except Exception as e:
            print(f"Vendor creation failed: {e}")
            return None
    
    def _get_account_id(self, account_name: str) -> Optional[str]:
        """Get QuickBooks account ID by name"""
        try:
            account_url = f"{self.api_url}/{self.integration.realm_id}/account"
            response = requests.get(account_url, headers=self._get_headers())
            
            if response.status_code == 200:
                accounts = response.json().get("QueryResponse", {}).get("Account", [])
                for account in accounts:
                    if account.get("Name", "").lower() == account_name.lower():
                        return account.get("Id")
            
            return None
            
        except Exception as e:
            print(f"Account lookup failed: {e}")
            return None
    
    def _create_quickbooks_purchase(self, expense: Expense) -> Optional[str]:
        """Create purchase transaction in QuickBooks"""
        try:
            # Map CORA expense to QuickBooks purchase
            account_name = self._map_cora_to_quickbooks_category(expense.category)
            if not account_name:
                account_name = "Office Supplies"  # Default fallback
            
            account_id = self._get_account_id(account_name)
            vendor_id = self._get_or_create_vendor(expense.vendor or "Unknown Vendor")
            
            purchase_data = {
                "Line": [
                    {
                        "Amount": float(expense.amount),
                        "DetailType": "AccountBasedExpenseLineDetail",
                        "AccountBasedExpenseLineDetail": {
                            "AccountRef": {
                                "value": account_id or "7",  # Default to Office Supplies
                                "name": account_name
                            }
                        }
                    }
                ],
                "VendorRef": {
                    "value": vendor_id or "1",  # Default vendor
                    "name": expense.vendor or "Unknown Vendor"
                },
                "TxnDate": expense.date.strftime("%Y-%m-%d") if expense.date else datetime.now().strftime("%Y-%m-%d"),
                "PrivateNote": expense.description or f"Expense: {expense.amount}"
            }
            
            # Create purchase
            purchase_url = f"{self.api_url}/{self.integration.realm_id}/purchase"
            response = requests.post(purchase_url, json=purchase_data, headers=self._get_headers())
            
            if response.status_code == 200:
                purchase = response.json().get("Purchase", {})
                return purchase.get("Id")
            
            return None
            
        except Exception as e:
            print(f"Purchase creation failed: {e}")
            return None
    
    async def sync_expense(self, expense: Expense, db: Session) -> Dict[str, any]:
        """Sync a single expense to QuickBooks"""
        start_time = datetime.utcnow()
        
        try:
            # Refresh token if needed
            if not self._refresh_token_if_needed():
                return {
                    "success": False,
                    "error": "Token refresh failed",
                    "quickbooks_id": None
                }
            
            # Create purchase in QuickBooks
            quickbooks_id = self._create_quickbooks_purchase(expense)
            
            if quickbooks_id:
                # Record successful sync
                sync_duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                sync_history = QuickBooksSyncHistory(
                    integration_id=self.integration.id,
                    sync_type="expense_created",
                    expense_id=expense.id,
                    quickbooks_id=quickbooks_id,
                    quickbooks_status="success",
                    sync_duration=sync_duration
                )
                
                db.add(sync_history)
                
                # Update integration stats
                self.integration.total_expenses_synced += 1
                self.integration.last_sync_at = datetime.utcnow()
                self.integration.last_sync_error = None
                
                db.commit()
                
                return {
                    "success": True,
                    "quickbooks_id": quickbooks_id,
                    "sync_duration": sync_duration
                }
            else:
                # Record failed sync
                sync_duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                error_message = "Failed to create purchase in QuickBooks"
                
                sync_history = QuickBooksSyncHistory(
                    integration_id=self.integration.id,
                    sync_type="expense_created",
                    expense_id=expense.id,
                    quickbooks_status="error",
                    sync_duration=sync_duration,
                    error_message=error_message
                )
                
                db.add(sync_history)
                self.integration.last_sync_error = error_message
                db.commit()
                
                return {
                    "success": False,
                    "error": error_message,
                    "quickbooks_id": None
                }
                
        except Exception as e:
            # Record error
            sync_duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            sync_history = QuickBooksSyncHistory(
                integration_id=self.integration.id,
                sync_type="expense_created",
                expense_id=expense.id,
                quickbooks_status="error",
                sync_duration=sync_duration,
                error_message=str(e)
            )
            
            db.add(sync_history)
            self.integration.last_sync_error = str(e)
            db.commit()
            
            return {
                "success": False,
                "error": str(e),
                "quickbooks_id": None
            }
    
    async def sync_expenses_by_ids(self, expense_ids: List[int], db: Session) -> Dict[str, any]:
        """Sync specific expenses by IDs"""
        results = {
            "success": True,
            "synced_count": 0,
            "errors": [],
            "sync_history": []
        }
        
        for expense_id in expense_ids:
            expense = db.query(Expense).filter(Expense.id == expense_id).first()
            if expense:
                result = await self.sync_expense(expense, db)
                if result["success"]:
                    results["synced_count"] += 1
                else:
                    results["errors"].append(f"Expense {expense_id}: {result['error']}")
                    results["success"] = False
            else:
                results["errors"].append(f"Expense {expense_id} not found")
                results["success"] = False
        
        return results
    
    async def sync_all_unsynced_expenses(self, db: Session) -> Dict[str, any]:
        """Sync all expenses that haven't been synced yet"""
        # Get all expenses for this user that haven't been synced
        # (This would need a field to track sync status - TODO: Add to Expense model)
        expenses = db.query(Expense).filter(
            Expense.user_id == self.integration.user_id
        ).all()
        
        results = {
            "success": True,
            "synced_count": 0,
            "errors": [],
            "sync_history": []
        }
        
        for expense in expenses:
            result = await self.sync_expense(expense, db)
            if result["success"]:
                results["synced_count"] += 1
            else:
                results["errors"].append(f"Expense {expense.id}: {result['error']}")
                results["success"] = False
        
        return results
    
    def get_company_info(self) -> Dict[str, any]:
        """Get QuickBooks company information"""
        try:
            if not self._refresh_token_if_needed():
                return {"error": "Token refresh failed"}
            
            company_url = f"{self.base_url}/v1/openid_connect/userinfo"
            response = requests.get(company_url, headers=self._get_headers())
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "Failed to get company info"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def test_connection(self) -> bool:
        """Test QuickBooks connection"""
        try:
            if not self._refresh_token_if_needed():
                return False
            
            # Try to get company info
            company_info = self.get_company_info()
            return "error" not in company_info
            
        except requests.RequestException as e:
            logger.error(f"QuickBooks connection test failed - Request error: {str(e)}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"QuickBooks connection test failed - JSON decode error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"QuickBooks connection test failed - Unexpected error: {str(e)}")
            return False 