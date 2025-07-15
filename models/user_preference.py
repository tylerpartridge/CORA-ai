#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/user_preference.py
🎯 PURPOSE: User preferences model
🔗 IMPORTS: SQLAlchemy, base model
📤 EXPORTS: UserPreference model
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class UserPreference(Base):
    """User preferences model"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, ForeignKey("users.email"), nullable=False)
    key = Column(String, nullable=False)
    value = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="preferences")
    
    def __repr__(self):
        return f"<UserPreference(user={self.user_email}, key={self.key})>"