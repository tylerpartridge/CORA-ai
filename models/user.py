#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/user.py
🎯 PURPOSE: User database model - SQLite compatible for demo
🔗 IMPORTS: SQLAlchemy, base model
📤 EXPORTS: User model
"""

from sqlalchemy import Column, String, DateTime, Integer, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class User(Base):
    """User model - SQLite compatible for demo reliability"""
    __tablename__ = "users"
    
    # SQLite compatible schema
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    is_active = Column(String(10), default="true")  # SQLite boolean as string
    is_admin = Column(String(10), default="false")  # SQLite boolean as string
    email_verified = Column(String(10), default="false")  # SQLite boolean as string
    email_verified_at = Column(DateTime, nullable=True)
    timezone = Column(String(50), nullable=True, default="America/New_York")  # User's timezone
    currency = Column(String(8), nullable=True, default="USD")  # User's currency preference
    weekly_insights_opt_in = Column(String(10), default="true")  # SQLite boolean as string for email preferences
    # Onboarding progress (JSON blob) for save/resume; minimal schema, app-managed
    onboarding_progress = Column(JSON, nullable=True, default=dict)
    # stripe_customer_id = Column(String, nullable=True)  # TODO: Add this column to database
    
    # Relationships
    plaid_integrations = relationship("PlaidIntegration", back_populates="user", cascade="all, delete-orphan")
    quickbooks_integrations = relationship("QuickBooksIntegration", back_populates="user", cascade="all, delete-orphan")
    stripe_integrations = relationship("StripeIntegration", back_populates="user", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan", uselist=False)
    alerts = relationship("JobAlert", back_populates="user", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    # Intelligence relationships
    intelligence_signals = relationship("IntelligenceSignal", back_populates="user", cascade="all, delete-orphan")
    emotional_profile = relationship("EmotionalProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    # Onboarding relationship is attached conditionally below to avoid import-time errors
    
    def __repr__(self):
        return f"<User(email='{self.email}')>"

# Indexes for common user queries
__table_args__ = (
    # Email lookups (already has unique index)
    Index('idx_users_active', 'is_active'),
    # Created date for user analytics
    Index('idx_users_created_at', 'created_at'),
)

# Optional onboarding relationship (guarded to avoid import errors when the model is absent)
try:
    # Importing registers the mapped class so the string-based relationship can resolve
    from .user_onboarding_step import UserOnboardingStep as _UserOnboardingStep  # type: ignore # noqa: F401
    # Attach relationship dynamically only if the dependency is available
    User.onboarding_steps = relationship(  # type: ignore[attr-defined]
        "UserOnboardingStep",
        back_populates="user",
        cascade="all, delete-orphan",
    )
except Exception:
    # In minimal deployments where onboarding steps are not modeled, skip attaching the relationship
    pass
