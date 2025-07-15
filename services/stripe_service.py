#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/services/stripe_service.py
🎯 PURPOSE: Stripe service for OAuth authentication and transaction synchronization
🔗 IMPORTS: Stripe SDK, requests, SQLAlchemy
📤 EXPORTS: StripeService class
"""

import stripe
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session

from models.stripe_integration import StripeIntegration, StripeSyncHistory, StripeTransaction
from models.expense import Expense

class StripeService:
    """Service for Stripe API interactions and transaction synchronization"""
    
    def __init__(self, integration: StripeIntegration):
        self.integration = integration
        # Initialize Stripe with the connected account's access token
        stripe.api_key = integration.access_token
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Stripe API requests"""
        return {
            "Authorization": f"Bearer {self.integration.access_token}",
            "Stripe-Version": "2023-10-16",  # Latest stable version
            "Content-Type": "application/json"
        }
    
    def _refresh_token_if_needed(self) -> bool:
        """Refresh access token if needed"""
        if not self.integration.needs_token_refresh:
            return True
            
        try:
            # Stripe Connect OAuth refresh
            refresh_url = "https://connect.stripe.com/oauth/token"
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.integration.refresh_token,
                "client_secret": "YOUR_STRIPE_CLIENT_SECRET"  # TODO: Get from env
            }
            
            response = requests.post(refresh_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Update integration with new tokens
                self.integration.access_token = token_data["access_token"]
                if "refresh_token" in token_data:
                    self.integration.refresh_token = token_data["refresh_token"]
                self.integration.token_expires_at = datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
                
                # Update Stripe API key
                stripe.api_key = self.integration.access_token
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Token refresh failed: {e}")
            return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get Stripe account information"""
        try:
            if not self._refresh_token_if_needed():
                return {"error": "Token refresh failed"}
            
            # Get account details
            account = stripe.Account.retrieve()
            
            return {
                "id": account.id,
                "business_name": account.business_profile.get("name"),
                "business_type": account.business_type,
                "country": account.country,
                "email": account.email,
                "charges_enabled": account.charges_enabled,
                "payouts_enabled": account.payouts_enabled
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_transactions(self, limit: int = 100, starting_after: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent transactions from Stripe"""
        try:
            if not self._refresh_token_if_needed():
                return []
            
            # Get charges (transactions)
            params = {
                "limit": limit,
                "expand": ["data.payment_intent", "data.receipt_url"]
            }
            
            if starting_after:
                params["starting_after"] = starting_after
            
            charges = stripe.Charge.list(**params)
            
            transactions = []
            for charge in charges.data:
                transaction = {
                    "id": charge.id,
                    "amount": charge.amount / 100,  # Convert from cents
                    "currency": charge.currency,
                    "description": charge.description,
                    "receipt_url": charge.receipt_url,
                    "created": datetime.fromtimestamp(charge.created),
                    "status": charge.status,
                    "transaction_metadata": charge.metadata,
                    "payment_intent_id": charge.payment_intent,
                    "customer_id": charge.customer
                }
                transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            print(f"Failed to get transactions: {e}")
            return []
    
    def _map_stripe_to_cora_category(self, transaction: Dict[str, Any]) -> str:
        """Map Stripe transaction to CORA category"""
        description = transaction.get("description", "").lower()
        transaction_metadata = transaction.get("transaction_metadata", {})
        
        # Check metadata first (most reliable)
        if "category" in transaction_metadata:
            return transaction_metadata["category"]
        
        # Pattern matching based on description
        if any(word in description for word in ["office", "supplies", "paper", "ink"]):
            return "Office Supplies"
        elif any(word in description for word in ["food", "lunch", "dinner", "restaurant", "coffee"]):
            return "Meals & Entertainment"
        elif any(word in description for word in ["uber", "lyft", "taxi", "gas", "fuel"]):
            return "Transportation"
        elif any(word in description for word in ["software", "subscription", "saas", "app"]):
            return "Software & Subscriptions"
        elif any(word in description for word in ["advertising", "marketing", "facebook", "google"]):
            return "Marketing & Advertising"
        elif any(word in description for word in ["shipping", "postage", "delivery"]):
            return "Shipping & Postage"
        elif any(word in description for word in ["course", "training", "education", "book"]):
            return "Professional Development"
        elif any(word in description for word in ["hotel", "flight", "travel", "airbnb"]):
            return "Travel"
        elif any(word in description for word in ["electricity", "water", "internet", "phone"]):
            return "Utilities"
        elif any(word in description for word in ["insurance", "premium"]):
            return "Insurance"
        else:
            return "Office Supplies"  # Default fallback
    
    def sync_transaction_to_cora(self, transaction: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Sync a single Stripe transaction to CORA expense"""
        start_time = datetime.utcnow()
        
        try:
            # Check if transaction already exists
            existing_transaction = db.query(StripeTransaction).filter(
                StripeTransaction.stripe_transaction_id == transaction["id"]
            ).first()
            
            if existing_transaction:
                return {
                    "success": True,
                    "message": "Transaction already synced",
                    "expense_id": existing_transaction.expense_id
                }
            
            # Create Stripe transaction record
            stripe_transaction = StripeTransaction(
                integration_id=self.integration.id,
                stripe_transaction_id=transaction["id"],
                stripe_charge_id=transaction["id"],
                stripe_payment_intent_id=transaction.get("payment_intent_id"),
                amount=transaction["amount"],
                currency=transaction["currency"],
                description=transaction.get("description", ""),
                receipt_url=transaction.get("receipt_url"),
                transaction_metadata=json.dumps(transaction.get("metadata", {})),
                created_at=transaction["created"]
            )
            
            db.add(stripe_transaction)
            db.flush()  # Get the ID
            
            # Map to CORA category
            category = self._map_stripe_to_cora_category(transaction)
            
            # Create CORA expense
            expense = Expense(
                user_id=self.integration.user_id,
                amount=transaction["amount"],
                description=transaction.get("description", f"Stripe transaction {transaction['id']}"),
                category=category,
                vendor="Stripe Transaction",
                date=transaction["created"].date(),
                payment_method="Stripe",
                auto_categorized=True,
                confidence_score=85.0  # High confidence for Stripe data
            )
            
            db.add(expense)
            db.flush()  # Get the expense ID
            
            # Link transaction to expense
            stripe_transaction.expense_id = expense.id
            stripe_transaction.is_synced_to_cora = True
            
            # Record sync history
            sync_duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            sync_history = StripeSyncHistory(
                integration_id=self.integration.id,
                sync_type="transaction_created",
                stripe_transaction_id=transaction["id"],
                expense_id=expense.id,
                stripe_status="success",
                sync_duration=sync_duration,
                amount=transaction["amount"],
                currency=transaction["currency"],
                description=transaction.get("description", ""),
                category=category
            )
            
            db.add(sync_history)
            
            # Update integration stats
            self.integration.total_transactions_synced += 1
            self.integration.total_amount_synced += transaction["amount"]
            self.integration.last_sync_at = datetime.utcnow()
            self.integration.last_sync_error = None
            
            db.commit()
            
            return {
                "success": True,
                "expense_id": expense.id,
                "sync_duration": sync_duration,
                "category": category
            }
            
        except Exception as e:
            # Record error
            sync_duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            sync_history = StripeSyncHistory(
                integration_id=self.integration.id,
                sync_type="transaction_created",
                stripe_transaction_id=transaction["id"],
                stripe_status="error",
                sync_duration=sync_duration,
                error_message=str(e),
                amount=transaction.get("amount"),
                currency=transaction.get("currency"),
                description=transaction.get("description", "")
            )
            
            db.add(sync_history)
            self.integration.last_sync_error = str(e)
            db.commit()
            
            return {
                "success": False,
                "error": str(e),
                "sync_duration": sync_duration
            }
    
    async def sync_all_transactions(self, db: Session, limit: int = 100) -> Dict[str, Any]:
        """Sync all recent transactions from Stripe"""
        try:
            if not self._refresh_token_if_needed():
                return {
                    "success": False,
                    "error": "Token refresh failed",
                    "synced_count": 0
                }
            
            # Get recent transactions
            transactions = self.get_transactions(limit=limit)
            
            results = {
                "success": True,
                "synced_count": 0,
                "errors": [],
                "sync_history": []
            }
            
            for transaction in transactions:
                result = self.sync_transaction_to_cora(transaction, db)
                if result["success"]:
                    results["synced_count"] += 1
                else:
                    results["errors"].append(f"Transaction {transaction['id']}: {result['error']}")
                    results["success"] = False
                
                results["sync_history"].append(result)
            
            return results
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "synced_count": 0
            }
    
    def test_connection(self) -> bool:
        """Test Stripe connection"""
        try:
            if not self._refresh_token_if_needed():
                return False
            
            # Try to get account info
            account_info = self.get_account_info()
            return "error" not in account_info
            
        except Exception:
            return False 