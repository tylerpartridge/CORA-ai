#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/stripe_integration.py
🎯 PURPOSE: Stripe integration model for OAuth tokens and sync history
🔗 IMPORTS: SQLAlchemy, datetime
📤 EXPORTS: StripeIntegration, StripeSyncHistory classes
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from models.base import Base

class StripeIntegration(Base):
    """Stripe integration model for storing OAuth tokens and connection info"""
    
    __tablename__ = "stripe_integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, ForeignKey('users.email'), nullable=False)
    
    # Stripe OAuth tokens
    stripe_account_id = Column(String(255), nullable=False, unique=True)
    access_token = Column(Text, nullable=False)  # Encrypted in production
    refresh_token = Column(Text, nullable=True)  # Encrypted in production
    token_expires_at = Column(DateTime, nullable=True)
    
    # Connection info
    business_name = Column(String(255), nullable=True)
    business_type = Column(String(100), nullable=True)  # individual, company
    country = Column(String(10), nullable=True)
    email = Column(String(255), nullable=True)
    
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
    user = relationship("User", back_populates="stripe_integrations")
    sync_history = relationship("StripeSyncHistory", back_populates="integration", cascade="all, delete-orphan")
    
    @property
    def needs_token_refresh(self) -> bool:
        """Check if access token needs refresh"""
        if not self.token_expires_at:
            return False
        return datetime.utcnow() >= self.token_expires_at
    
    @property
    def is_connected(self) -> bool:
        """Check if Stripe integration is active and connected"""
        return self.is_active and self.access_token is not None

class StripeSyncHistory(Base):
    """Stripe sync history for tracking transaction synchronization"""
    
    __tablename__ = "stripe_sync_history"
    
    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("stripe_integrations.id"), nullable=False)
    
    # Sync details
    sync_type = Column(String(50), nullable=False)  # transaction_created, transaction_updated, bulk_sync
    stripe_transaction_id = Column(String(255), nullable=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=True)
    
    # Sync results
    stripe_status = Column(String(50), nullable=False)  # success, error, pending
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
    integration = relationship("StripeIntegration", back_populates="sync_history")
    expense = relationship("Expense", back_populates="stripe_sync_history")

class StripeTransaction(Base):
    """Stripe transaction model for storing imported transactions"""
    
    __tablename__ = "stripe_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("stripe_integrations.id"), nullable=False)
    
    # Stripe transaction data
    stripe_transaction_id = Column(String(255), nullable=False, unique=True)
    stripe_charge_id = Column(String(255), nullable=True)
    stripe_payment_intent_id = Column(String(255), nullable=True)
    
    # Transaction details
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="usd")
    description = Column(Text, nullable=True)
    receipt_url = Column(Text, nullable=True)
    
    # Metadata
    transaction_metadata = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, nullable=False)
    
    # CORA mapping
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=True)
    is_synced_to_cora = Column(Boolean, default=False)
    
    # Timestamps
    imported_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    integration = relationship("StripeIntegration")
    expense = relationship("Expense", back_populates="stripe_transactions") 