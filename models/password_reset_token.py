#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/password_reset_token.py
🎯 PURPOSE: Password reset token model
🔗 IMPORTS: SQLAlchemy, base model
📤 EXPORTS: PasswordResetToken model
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base

class PasswordResetToken(Base):
    """Password reset token model"""
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, ForeignKey("users.email"), nullable=False)
    token = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(String, default="false")
    
    def __repr__(self):
        return f"<PasswordResetToken(email={self.email})>"