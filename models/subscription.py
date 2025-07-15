#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/subscription.py
🎯 PURPOSE: Subscription model for payment tracking
🔗 IMPORTS: SQLAlchemy, base model
📤 EXPORTS: Subscription model
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base

class Subscription(Base):
    """Subscription model matching existing database schema"""
    __tablename__ = "subscriptions"
    
    # 4 subscriptions exist in database
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    stripe_subscription_id = Column(String)
    plan_name = Column(String)
    status = Column(String)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    canceled_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, plan='{self.plan_name}', status='{self.status}')>"