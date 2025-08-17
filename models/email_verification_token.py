#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/email_verification_token.py
🎯 PURPOSE: Email verification token model for user signup
🔗 IMPORTS: SQLAlchemy, base model
📤 EXPORTS: EmailVerificationToken model
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base

class EmailVerificationToken(Base):
    """Email verification token model for new user signups"""
    __tablename__ = "email_verification_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, ForeignKey("users.email"), nullable=False, index=True)
    token = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(String, default="false")  # SQLite boolean as string
    
    def __repr__(self):
        return f"<EmailVerificationToken(email={self.email})>"