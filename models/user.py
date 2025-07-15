#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/user.py
🎯 PURPOSE: User database model matching existing schema
🔗 IMPORTS: SQLAlchemy, base model
📤 EXPORTS: User model
"""

from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class User(Base):
    """User model matching existing database schema"""
    __tablename__ = "users"
    
    # Match existing schema from audit
    email = Column(String, primary_key=True, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(String, default="true")  # Stored as string in existing DB
    
    # Relationships
    plaid_integrations = relationship("PlaidIntegration", back_populates="user", cascade="all, delete-orphan")
    quickbooks_integrations = relationship("QuickBooksIntegration", back_populates="user", cascade="all, delete-orphan")
    stripe_integrations = relationship("StripeIntegration", back_populates="user", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan", uselist=False)
    customers = relationship("Customer", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(email='{self.email}')>"