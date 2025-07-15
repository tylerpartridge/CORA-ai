#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/quickbooks_integration.py
🎯 PURPOSE: QuickBooks integration model for OAuth tokens and sync settings
🔗 IMPORTS: SQLAlchemy Base, Column types
📤 EXPORTS: QuickBooksIntegration model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from models.base import Base

class QuickBooksIntegration(Base):
    """QuickBooks integration model for storing OAuth tokens and sync settings"""
    
    __tablename__ = "quickbooks_integrations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    realm_id = Column(String(50), nullable=False)  # QuickBooks company ID
    company_name = Column(String(200))  # QuickBooks company name
    
    # OAuth 2.0 tokens
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    token_expires_at = Column(DateTime, nullable=False)
    
    # Sync settings
    is_active = Column(Boolean, default=True)
    auto_sync = Column(Boolean, default=True)  # Auto-sync new expenses
    sync_frequency = Column(String(20), default="realtime")  # realtime, hourly, daily
    
    # Category mapping (JSON string)
    category_mapping = Column(Text, default="{}")  # CORA categories → QuickBooks accounts
    
    # Sync statistics
    last_sync_at = Column(DateTime)
    total_expenses_synced = Column(Integer, default=0)
    last_sync_error = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="quickbooks_integrations")
    sync_history = relationship("QuickBooksSyncHistory", back_populates="integration")
    
    def __repr__(self):
        return f"<QuickBooksIntegration(user_id={self.user_id}, realm_id={self.realm_id})>"
    
    @property
    def is_token_expired(self):
        """Check if the access token is expired"""
        return datetime.utcnow() >= self.token_expires_at
    
    @property
    def needs_token_refresh(self):
        """Check if token needs refresh (within 1 hour of expiry)"""
        return datetime.utcnow() >= (self.token_expires_at - timedelta(hours=1))
    
    def get_category_mapping(self):
        """Get category mapping as dictionary"""
        import json
        try:
            return json.loads(self.category_mapping or "{}")
        except json.JSONDecodeError:
            return {}
    
    def set_category_mapping(self, mapping):
        """Set category mapping from dictionary"""
        import json
        self.category_mapping = json.dumps(mapping)

class QuickBooksSyncHistory(Base):
    """History of QuickBooks sync operations"""
    
    __tablename__ = "quickbooks_sync_history"
    
    id = Column(Integer, primary_key=True)
    integration_id = Column(Integer, ForeignKey("quickbooks_integrations.id"), nullable=False)
    
    # Sync details
    sync_type = Column(String(20), nullable=False)  # expense_created, expense_updated, bulk_sync
    expense_id = Column(Integer, ForeignKey("expenses.id"))  # If syncing specific expense
    
    # QuickBooks response
    quickbooks_id = Column(String(50))  # QuickBooks transaction ID
    quickbooks_status = Column(String(20))  # success, error, pending
    
    # Sync metadata
    sync_duration = Column(Integer)  # Duration in milliseconds
    error_message = Column(Text)  # Error details if failed
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    integration = relationship("QuickBooksIntegration", back_populates="sync_history")
    expense = relationship("Expense")
    
    def __repr__(self):
        return f"<QuickBooksSyncHistory(integration_id={self.integration_id}, sync_type={self.sync_type})>"

class QuickBooksVendor(Base):
    """Cached QuickBooks vendors for faster lookups"""
    
    __tablename__ = "quickbooks_vendors"
    
    id = Column(Integer, primary_key=True)
    integration_id = Column(Integer, ForeignKey("quickbooks_integrations.id"), nullable=False)
    
    # QuickBooks vendor data
    quickbooks_id = Column(String(50), nullable=False)
    vendor_name = Column(String(200), nullable=False)
    display_name = Column(String(200))
    
    # Cached data
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    integration = relationship("QuickBooksIntegration")
    
    def __repr__(self):
        return f"<QuickBooksVendor(quickbooks_id={self.quickbooks_id}, vendor_name={self.vendor_name})>"

class QuickBooksAccount(Base):
    """Cached QuickBooks accounts for faster lookups"""
    
    __tablename__ = "quickbooks_accounts"
    
    id = Column(Integer, primary_key=True)
    integration_id = Column(Integer, ForeignKey("quickbooks_integrations.id"), nullable=False)
    
    # QuickBooks account data
    quickbooks_id = Column(String(50), nullable=False)
    account_name = Column(String(200), nullable=False)
    account_type = Column(String(50))  # Expense, Income, Asset, etc.
    
    # Cached data
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    integration = relationship("QuickBooksIntegration")
    
    def __repr__(self):
        return f"<QuickBooksAccount(quickbooks_id={self.quickbooks_id}, account_name={self.account_name})>" 