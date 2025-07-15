#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/feedback.py
🎯 PURPOSE: Feedback database model for user feedback
🔗 IMPORTS: SQLAlchemy, base model
📤 EXPORTS: Feedback model
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base

class Feedback(Base):
    """Feedback model for storing user feedback"""
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, ForeignKey("users.email"), nullable=False)
    category = Column(String, nullable=False)
    message = Column(String, nullable=False)
    rating = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Feedback(user_email={self.user_email}, category={self.category})>" 