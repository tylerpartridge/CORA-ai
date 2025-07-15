#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/payment.py
🎯 PURPOSE: Payment model for transaction tracking
🔗 IMPORTS: SQLAlchemy, base model
📤 EXPORTS: Payment model
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base

class Payment(Base):
    """Payment model matching existing database schema"""
    __tablename__ = "payments"
    
    # 6 payment records exist
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    stripe_payment_intent_id = Column(String)
    amount = Column(Float)
    currency = Column(String)
    status = Column(String)
    description = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, status='{self.status}')>"