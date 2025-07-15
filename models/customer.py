#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/customer.py
🎯 PURPOSE: Customer model for Stripe integration
🔗 IMPORTS: SQLAlchemy, base model
📤 EXPORTS: Customer model
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Customer(Base):
    """Customer model matching existing database schema"""
    __tablename__ = "customers"
    
    # 4 customers exist with Stripe integration
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, ForeignKey("users.email"))
    stripe_customer_id = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="customers")
    
    def __repr__(self):
        return f"<Customer(id={self.id}, user_email='{self.user_email}')>"