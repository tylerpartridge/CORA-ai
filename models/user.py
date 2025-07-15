#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/user.py
🎯 PURPOSE: User database model matching existing schema
🔗 IMPORTS: SQLAlchemy, base model
📤 EXPORTS: User model
"""

from sqlalchemy import Column, String, DateTime, Boolean
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
    
    def __repr__(self):
        return f"<User(email='{self.email}')>"