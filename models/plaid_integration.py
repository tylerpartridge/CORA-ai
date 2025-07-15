#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/plaid_integration.py
🎯 PURPOSE: Plaid integration model for bank account connections and transaction sync
🔗 IMPORTS: SQLAlchemy, datetime
📤 EXPORTS: PlaidIntegration, PlaidAccount, PlaidTransaction classes
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from models.base import Base

class PlaidIntegration(Base):
    """Plaid integration model for storing access tokens and connection info"""
    
    __tablename__ = "plaid_integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, ForeignKey('users.email'), nullable=False)
    
    # Plaid access token
    access_token = Column(Text, nullable=False)  # Encrypted in production
    item_id = Column(String(255), nullable=False, unique=True)
    
    # Connection info
    institution_id = Column(String(255), nullable=True)
    institution_name = Column(String(255), nullable=True)
    institution_logo = Column(String(500), nullable=True)
    institution_primary_color = Column(String(7), nullable=True)  # Hex color
    
    # Sync settings
    auto_sync = Column(Boolean, default=True)
    sync_frequency = Column(String(50), default="daily")  # daily, weekly, monthly
    last_sync_at = Column(DateTime, nullable=True)
    last_sync_error = Column(Text, nullable=True)
    
    # Statistics
    total_transactions_synced = Column(Integer, default=0)
    total_amount_synced = Column(Float, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="plaid_integrations")
    accounts = relationship("PlaidAccount", back_populates="integration", cascade="all, delete-orphan")
    
    @property
    def is_connected(self) -> bool:
        """Check if Plaid integration is active and connected"""
        return self.is_active and self.access_token is not None

class PlaidAccount(Base):
    """Plaid account model for storing bank account information"""
    
    __tablename__ = "plaid_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("plaid_integrations.id"), nullable=False)
    
    # Plaid account data
    plaid_account_id = Column(String(255), nullable=False, unique=True)
    account_name = Column(String(255), nullable=False)
    account_type = Column(String(100), nullable=False)  # checking, savings, credit, loan
    account_subtype = Column(String(100), nullable=True)  # paypal, venmo, etc.
    
    # Account details
    mask = Column(String(10), nullable=True)  # Last 4 digits
    official_name = Column(String(255), nullable=True)
    verification_status = Column(String(50), nullable=True)
    
    # Balance info
    current_balance = Column(Float, nullable=True)
    available_balance = Column(Float, nullable=True)
    iso_currency_code = Column(String(10), nullable=True)
    unofficial_currency_code = Column(String(10), nullable=True)
    
    # Sync info
    last_sync_at = Column(DateTime, nullable=True)
    is_sync_enabled = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    integration = relationship("PlaidIntegration", back_populates="accounts")
    transactions = relationship("PlaidTransaction", back_populates="account", cascade="all, delete-orphan")
    
    @property
    def display_name(self) -> str:
        """Get display name for the account"""
        if self.mask:
            return f"{self.account_name} •••• {self.mask}"
        return self.account_name

class PlaidTransaction(Base):
    """Plaid transaction model for storing bank transactions"""
    
    __tablename__ = "plaid_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("plaid_accounts.id"), nullable=False)
    
    # Plaid transaction data
    plaid_transaction_id = Column(String(255), nullable=False, unique=True)
    transaction_id = Column(String(255), nullable=True)  # Internal transaction ID
    
    # Transaction details
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="USD")
    date = Column(DateTime, nullable=False)
    name = Column(String(255), nullable=False)
    merchant_name = Column(String(255), nullable=True)
    payment_channel = Column(String(50), nullable=True)  # online, in store, other
    pending = Column(Boolean, default=False)
    
    # Location data
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    zip_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    
    # Category data
    category = Column(JSON, nullable=True)  # Plaid category array
    category_id = Column(String(255), nullable=True)
    primary_category = Column(String(255), nullable=True)
    detailed_category = Column(String(255), nullable=True)
    
    # Additional data
    check_number = Column(String(50), nullable=True)
    payment_meta = Column(JSON, nullable=True)  # Payment metadata
    pending_transaction_id = Column(String(255), nullable=True)
    
    # CORA mapping
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=True)
    is_synced_to_cora = Column(Boolean, default=False)
    auto_categorized = Column(Boolean, default=False)
    confidence_score = Column(Float, nullable=True)
    
    # Timestamps
    imported_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    account = relationship("PlaidAccount", back_populates="transactions")
    expense = relationship("Expense", back_populates="plaid_transactions")
    
    @property
    def is_expense(self) -> bool:
        """Check if transaction is an expense (negative amount)"""
        return self.amount < 0
    
    @property
    def absolute_amount(self) -> float:
        """Get absolute amount for expense tracking"""
        return abs(self.amount)
    
    @property
    def display_category(self) -> str:
        """Get display category for the transaction"""
        if self.primary_category:
            return self.primary_category
        elif self.category and len(self.category) > 0:
            return " > ".join(self.category)
        return "Uncategorized"

class PlaidSyncHistory(Base):
    """Plaid sync history for tracking synchronization activities"""
    
    __tablename__ = "plaid_sync_history"
    
    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("plaid_integrations.id"), nullable=False)
    
    # Sync details
    sync_type = Column(String(50), nullable=False)  # account_sync, transaction_sync, balance_sync
    account_id = Column(Integer, ForeignKey("plaid_accounts.id"), nullable=True)
    plaid_transaction_id = Column(String(255), nullable=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=True)
    
    # Sync results
    sync_status = Column(String(50), nullable=False)  # success, error, pending
    sync_duration = Column(Integer, nullable=True)  # milliseconds
    error_message = Column(Text, nullable=True)
    
    # Transaction data
    amount = Column(Float, nullable=True)
    currency = Column(String(10), nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    integration = relationship("PlaidIntegration")
    account = relationship("PlaidAccount")
    expense = relationship("Expense", back_populates="plaid_sync_history") 