#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/services/plaid_service.py
🎯 PURPOSE: Plaid service for bank account connection and transaction synchronization
🔗 IMPORTS: Plaid SDK, SQLAlchemy
📤 EXPORTS: PlaidService class
"""

import plaid
from plaid.api import plaid_api
from plaid.model import *
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session

from models.plaid_integration import PlaidIntegration, PlaidAccount, PlaidTransaction, PlaidSyncHistory
from models.expense import Expense

class PlaidService:
    """Service for Plaid API interactions and bank transaction synchronization"""
    
    def __init__(self, integration: PlaidIntegration):
        self.integration = integration
        
        # Initialize Plaid client
        configuration = plaid.Configuration(
            host=plaid.Environment.Sandbox,  # Change to Production for live
            api_key={
                'clientId': 'YOUR_PLAID_CLIENT_ID',  # TODO: Get from env
                'secret': 'YOUR_PLAID_SECRET',  # TODO: Get from env
            }
        )
        
        api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)
    
    def _map_plaid_to_cora_category(self, transaction: Dict[str, Any]) -> str:
        """Map Plaid transaction to CORA category"""
        # Use Plaid's category if available
        if transaction.get("category") and len(transaction["category"]) > 0:
            primary_category = transaction["category"][0].lower()
            
            # Map Plaid categories to CORA categories
            category_mapping = {
                "food and drink": "Meals & Entertainment",
                "shopping": "Office Supplies",
                "transportation": "Transportation",
                "travel": "Travel",
                "bills and utilities": "Utilities",
                "entertainment": "Meals & Entertainment",
                "health and fitness": "Professional Development",
                "professional services": "Professional Services",
                "education": "Professional Development",
                "personal care": "Office Supplies",
                "insurance": "Insurance",
                "financial services": "Banking & Finance",
                "government services": "Taxes & Fees",
                "income": "Income",
                "transfer": "Transfer",
                "payment": "Payment"
            }
            
            return category_mapping.get(primary_category, "Office Supplies")
        
        # Fallback to merchant name analysis
        merchant_name = transaction.get("merchant_name", "").lower()
        transaction_name = transaction.get("name", "").lower()
        
        if any(word in merchant_name or word in transaction_name for word in ["office", "staples", "supplies", "paper", "ink"]):
            return "Office Supplies"
        elif any(word in merchant_name or word in transaction_name for word in ["restaurant", "coffee", "starbucks", "mcdonalds", "uber eats"]):
            return "Meals & Entertainment"
        elif any(word in merchant_name or word in transaction_name for word in ["uber", "lyft", "taxi", "gas", "shell", "exxon"]):
            return "Transportation"
        elif any(word in merchant_name or word in transaction_name for word in ["amazon", "software", "subscription", "saas"]):
            return "Software & Subscriptions"
        elif any(word in merchant_name or word in transaction_name for word in ["facebook", "google", "advertising", "marketing"]):
            return "Marketing & Advertising"
        elif any(word in merchant_name or word in transaction_name for word in ["hotel", "airbnb", "flight", "airline"]):
            return "Travel"
        elif any(word in merchant_name or word in transaction_name for word in ["electricity", "water", "internet", "phone", "verizon", "at&t"]):
            return "Utilities"
        else:
            return "Office Supplies"  # Default fallback
    
    def get_accounts(self) -> List[Dict[str, Any]]:
        """Get all accounts for the connected item"""
        try:
            request = AccountsGetRequest(
                access_token=self.integration.access_token
            )
            
            response = self.client.accounts_get(request)
            
            accounts = []
            for account in response.accounts:
                account_data = {
                    "id": account.account_id,
                    "name": account.name,
                    "mask": account.mask,
                    "official_name": account.official_name,
                    "type": account.type.value,
                    "subtype": account.subtype.value if account.subtype else None,
                    "verification_status": account.verification_status.value if account.verification_status else None,
                    "current_balance": account.balances.current,
                    "available_balance": account.balances.available,
                    "iso_currency_code": account.balances.iso_currency_code,
                    "unofficial_currency_code": account.balances.unofficial_currency_code
                }
                accounts.append(account_data)
            
            return accounts
            
        except Exception as e:
            print(f"Failed to get accounts: {e}")
            return []
    
    def get_transactions(self, account_id: str, start_date: str, end_date: str, count: int = 100) -> List[Dict[str, Any]]:
        """Get transactions for a specific account"""
        try:
            request = TransactionsGetRequest(
                access_token=self.integration.access_token,
                start_date=start_date,
                end_date=end_date,
                options=TransactionsGetRequestOptions(
                    account_ids=[account_id],
                    count=count
                )
            )
            
            response = self.client.transactions_get(request)
            
            transactions = []
            for transaction in response.transactions:
                transaction_data = {
                    "id": transaction.transaction_id,
                    "account_id": transaction.account_id,
                    "amount": transaction.amount,
                    "currency": transaction.iso_currency_code,
                    "date": transaction.date,
                    "name": transaction.name,
                    "merchant_name": transaction.merchant_name,
                    "payment_channel": transaction.payment_channel.value if transaction.payment_channel else None,
                    "pending": transaction.pending,
                    "address": transaction.location.address if transaction.location else None,
                    "city": transaction.location.city if transaction.location else None,
                    "state": transaction.location.state if transaction.location else None,
                    "zip_code": transaction.location.zip if transaction.location else None,
                    "country": transaction.location.country if transaction.location else None,
                    "lat": transaction.location.lat if transaction.location else None,
                    "lon": transaction.location.lon if transaction.location else None,
                    "category": transaction.category,
                    "category_id": transaction.category_id,
                    "check_number": transaction.check_number,
                    "payment_meta": transaction.payment_meta.to_dict() if transaction.payment_meta else None,
                    "pending_transaction_id": transaction.pending_transaction_id
                }
                transactions.append(transaction_data)
            
            return transactions
            
        except Exception as e:
            print(f"Failed to get transactions: {e}")
            return []
    
    def sync_accounts_to_cora(self, db: Session) -> Dict[str, Any]:
        """Sync Plaid accounts to CORA"""
        start_time = datetime.utcnow()
        
        try:
            # Get accounts from Plaid
            plaid_accounts = self.get_accounts()
            
            results = {
                "success": True,
                "synced_count": 0,
                "errors": [],
                "accounts": []
            }
            
            for plaid_account in plaid_accounts:
                try:
                    # Check if account already exists
                    existing_account = db.query(PlaidAccount).filter(
                        PlaidAccount.plaid_account_id == plaid_account["id"]
                    ).first()
                    
                    if existing_account:
                        # Update existing account
                        existing_account.current_balance = plaid_account.get("current_balance")
                        existing_account.available_balance = plaid_account.get("available_balance")
                        existing_account.updated_at = datetime.utcnow()
                        results["accounts"].append({
                            "id": existing_account.id,
                            "name": existing_account.display_name,
                            "status": "updated"
                        })
                    else:
                        # Create new account
                        account = PlaidAccount(
                            integration_id=self.integration.id,
                            plaid_account_id=plaid_account["id"],
                            account_name=plaid_account["name"],
                            account_type=plaid_account["type"],
                            account_subtype=plaid_account.get("subtype"),
                            mask=plaid_account.get("mask"),
                            official_name=plaid_account.get("official_name"),
                            verification_status=plaid_account.get("verification_status"),
                            current_balance=plaid_account.get("current_balance"),
                            available_balance=plaid_account.get("available_balance"),
                            iso_currency_code=plaid_account.get("iso_currency_code"),
                            unofficial_currency_code=plaid_account.get("unofficial_currency_code")
                        )
                        
                        db.add(account)
                        db.flush()  # Get the ID
                        
                        results["accounts"].append({
                            "id": account.id,
                            "name": account.display_name,
                            "status": "created"
                        })
                    
                    results["synced_count"] += 1
                    
                except Exception as e:
                    results["errors"].append(f"Account {plaid_account['name']}: {str(e)}")
                    results["success"] = False
            
            # Update integration stats
            self.integration.last_sync_at = datetime.utcnow()
            self.integration.last_sync_error = None
            
            db.commit()
            
            return results
            
        except Exception as e:
            # Record error
            self.integration.last_sync_error = str(e)
            db.commit()
            
            return {
                "success": False,
                "error": str(e),
                "synced_count": 0
            }
    
    def sync_transactions_to_cora(self, db: Session, days_back: int = 30) -> Dict[str, Any]:
        """Sync Plaid transactions to CORA"""
        start_time = datetime.utcnow()
        
        try:
            # Get date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days_back)
            
            # Get all accounts for this integration
            accounts = db.query(PlaidAccount).filter(
                PlaidAccount.integration_id == self.integration.id,
                PlaidAccount.is_sync_enabled == True
            ).all()
            
            results = {
                "success": True,
                "synced_count": 0,
                "errors": [],
                "sync_history": []
            }
            
            for account in accounts:
                try:
                    # Get transactions for this account
                    transactions = self.get_transactions(
                        account.plaid_account_id,
                        start_date.strftime("%Y-%m-%d"),
                        end_date.strftime("%Y-%m-%d")
                    )
                    
                    for transaction in transactions:
                        result = self._sync_single_transaction(transaction, account, db)
                        
                        if result["success"]:
                            results["synced_count"] += 1
                        else:
                            results["errors"].append(f"Transaction {transaction['id']}: {result['error']}")
                            results["success"] = False
                        
                        results["sync_history"].append(result)
                        
                except Exception as e:
                    results["errors"].append(f"Account {account.display_name}: {str(e)}")
                    results["success"] = False
            
            # Update integration stats
            self.integration.last_sync_at = datetime.utcnow()
            self.integration.last_sync_error = None
            
            db.commit()
            
            return results
            
        except Exception as e:
            # Record error
            self.integration.last_sync_error = str(e)
            db.commit()
            
            return {
                "success": False,
                "error": str(e),
                "synced_count": 0
            }
    
    def _sync_single_transaction(self, transaction: Dict[str, Any], account: PlaidAccount, db: Session) -> Dict[str, Any]:
        """Sync a single transaction to CORA"""
        start_time = datetime.utcnow()
        
        try:
            # Check if transaction already exists
            existing_transaction = db.query(PlaidTransaction).filter(
                PlaidTransaction.plaid_transaction_id == transaction["id"]
            ).first()
            
            if existing_transaction:
                return {
                    "success": True,
                    "message": "Transaction already synced",
                    "expense_id": existing_transaction.expense_id
                }
            
            # Only sync expenses (negative amounts)
            if transaction["amount"] >= 0:
                return {
                    "success": True,
                    "message": "Skipped income transaction",
                    "expense_id": None
                }
            
            # Create Plaid transaction record
            plaid_transaction = PlaidTransaction(
                account_id=account.id,
                plaid_transaction_id=transaction["id"],
                amount=transaction["amount"],
                currency=transaction["currency"],
                date=datetime.strptime(transaction["date"], "%Y-%m-%d"),
                name=transaction["name"],
                merchant_name=transaction.get("merchant_name"),
                payment_channel=transaction.get("payment_channel"),
                pending=transaction["pending"],
                address=transaction.get("address"),
                city=transaction.get("city"),
                state=transaction.get("state"),
                zip_code=transaction.get("zip_code"),
                country=transaction.get("country"),
                lat=transaction.get("lat"),
                lon=transaction.get("lon"),
                category=transaction.get("category"),
                category_id=transaction.get("category_id"),
                check_number=transaction.get("check_number"),
                payment_meta=transaction.get("payment_meta")
            )
            
            db.add(plaid_transaction)
            db.flush()  # Get the ID
            
            # Map to CORA category
            category = self._map_plaid_to_cora_category(transaction)
            
            # Create CORA expense
            expense = Expense(
                user_id=self.integration.user_id,
                amount=abs(transaction["amount"]),  # Convert to positive for expense
                description=transaction["name"],
                category=category,
                vendor=transaction.get("merchant_name", "Bank Transaction"),
                date=datetime.strptime(transaction["date"], "%Y-%m-%d").date(),
                payment_method=f"Bank - {account.display_name}",
                auto_categorized=True,
                confidence_score=90.0  # High confidence for bank data
            )
            
            db.add(expense)
            db.flush()  # Get the expense ID
            
            # Link transaction to expense
            plaid_transaction.expense_id = expense.id
            plaid_transaction.is_synced_to_cora = True
            plaid_transaction.auto_categorized = True
            plaid_transaction.confidence_score = 90.0
            
            # Record sync history
            sync_duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            sync_history = PlaidSyncHistory(
                integration_id=self.integration.id,
                sync_type="transaction_sync",
                account_id=account.id,
                plaid_transaction_id=transaction["id"],
                expense_id=expense.id,
                sync_status="success",
                sync_duration=sync_duration,
                amount=abs(transaction["amount"]),
                currency=transaction["currency"],
                description=transaction["name"],
                category=category
            )
            
            db.add(sync_history)
            
            # Update integration stats
            self.integration.total_transactions_synced += 1
            self.integration.total_amount_synced += abs(transaction["amount"])
            
            return {
                "success": True,
                "expense_id": expense.id,
                "sync_duration": sync_duration,
                "category": category
            }
            
        except Exception as e:
            # Record error
            sync_duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            sync_history = PlaidSyncHistory(
                integration_id=self.integration.id,
                sync_type="transaction_sync",
                account_id=account.id,
                plaid_transaction_id=transaction["id"],
                sync_status="error",
                sync_duration=sync_duration,
                error_message=str(e),
                amount=abs(transaction.get("amount", 0)),
                currency=transaction.get("currency", "USD"),
                description=transaction.get("name", "")
            )
            
            db.add(sync_history)
            
            return {
                "success": False,
                "error": str(e),
                "sync_duration": sync_duration
            }
    
    def test_connection(self) -> bool:
        """Test Plaid connection"""
        try:
            # Try to get accounts
            accounts = self.get_accounts()
            return len(accounts) > 0
            
        except Exception:
            return False 