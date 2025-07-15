#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/expense.py
🎯 PURPOSE: Expense database model matching existing schema
🔗 IMPORTS: SQLAlchemy, base model
📤 EXPORTS: Expense model
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Expense(Base):
    """Expense model matching existing database schema"""
    __tablename__ = "expenses"
    
    # Based on actual schema - 235 expense records exist
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), ForeignKey("users.email"), nullable=False)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(3), default="USD")
    category_id = Column(Integer, ForeignKey("expense_categories.id"))
    description = Column(Text, nullable=False)
    vendor = Column(String(200))
    expense_date = Column(DateTime, nullable=False)
    payment_method = Column(String(50))
    receipt_url = Column(String(500))
    tags = Column(Text)  # JSON stored as text
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())
    confidence_score = Column(Integer, default=None)
    auto_categorized = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="expenses")
    category = relationship("ExpenseCategory", back_populates="expenses")
    plaid_transactions = relationship("PlaidTransaction", back_populates="expense")
    plaid_sync_history = relationship("PlaidSyncHistory", back_populates="expense")
    stripe_sync_history = relationship("StripeSyncHistory", back_populates="expense")
    stripe_transactions = relationship("StripeTransaction", back_populates="expense")
    
    @property
    def amount(self):
        """Get amount in dollars"""
        return self.amount_cents / 100.0
    
    def __repr__(self):
        return f"<Expense(id={self.id}, vendor='{self.vendor}', amount={self.amount})>"