#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/business_profile.py
🎯 PURPOSE: Business profile model for onboarding
🔗 IMPORTS: SQLAlchemy, base model
📤 EXPORTS: BusinessProfile model
"""

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base

class BusinessProfile(Base):
    """Business profile model matching existing database schema"""
    __tablename__ = "business_profiles"
    
    # 6 business profiles exist
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(Text, ForeignKey("users.email"), nullable=False)
    business_name = Column(Text, nullable=False)
    business_type = Column(Text, nullable=False)
    industry = Column(Text, nullable=False)
    monthly_revenue_range = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<BusinessProfile(id={self.id}, business='{self.business_name}')>"