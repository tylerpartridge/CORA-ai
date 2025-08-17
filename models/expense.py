#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/expense.py
🎯 PURPOSE: Expense database model matching existing schema
🔗 IMPORTS: SQLAlchemy, base model
📤 EXPORTS: Expense model
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Expense(Base):
    """Expense model - SQLite compatible"""
    __tablename__ = "expenses"
    
    # SQLite compatible schema with Integer FK
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(3), default="USD")
    category_id = Column(Integer, ForeignKey("expense_categories.id"), index=True)
    description = Column(Text, nullable=False)
    vendor = Column(String(200), index=True)
    job_name = Column(String(200), index=True)  # Construction job name
    job_id = Column(String(100), index=True)  # Construction job ID
    expense_date = Column(DateTime, nullable=False, index=True)
    payment_method = Column(String(50))
    receipt_url = Column(String(500))
    receipt_path = Column(String(500))  # Local file path for uploaded receipts
    ocr_text = Column(Text)  # OCR extracted text
    is_auto_generated = Column(Boolean, default=False)  # Generated from receipt upload
    tags = Column(Text)  # JSON as text for SQLite compatibility
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    confidence_score = Column(Integer, default=None)
    auto_categorized = Column(Boolean, default=False)
    
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

# Composite indexes for common query patterns
__table_args__ = (
    # Most common: user expenses by date range
    Index('idx_expenses_user_date', 'user_id', 'expense_date'),
    # Category filtering for user
    Index('idx_expenses_user_category', 'user_id', 'category_id'),
    # Vendor searches
    Index('idx_expenses_vendor_lower', 'vendor'),
    # Date range queries
    Index('idx_expenses_date_range', 'expense_date'),
    # Auto-generated expenses
    Index('idx_expenses_auto_generated', 'is_auto_generated'),
    # Job tracking indexes for construction
    Index('idx_expenses_job_name', 'job_name'),
    Index('idx_expenses_job_id', 'job_id'),
    Index('idx_expenses_user_job', 'user_id', 'job_name'),
)