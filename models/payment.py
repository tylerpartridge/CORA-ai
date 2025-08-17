#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/payment.py
🎯 PURPOSE: Payment model for transaction tracking
🔗 IMPORTS: SQLAlchemy, base model
📤 EXPORTS: Payment model
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from .base import Base

class Payment(Base):
    """Payment model for PostgreSQL with UUID foreign keys"""
    __tablename__ = "payments"
    
    # PostgreSQL schema with UUID FK
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    stripe_payment_intent_id = Column(String)
    amount = Column(Numeric(12,2))
    currency = Column(String(10))
    status = Column(String(50))
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, status='{self.status}')>"