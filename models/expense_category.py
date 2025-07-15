#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/expense_category.py
🎯 PURPOSE: Expense category model matching existing schema
🔗 IMPORTS: SQLAlchemy, base model
📤 EXPORTS: ExpenseCategory model
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from .base import Base

class ExpenseCategory(Base):
    """Expense category model matching existing database schema"""
    __tablename__ = "expense_categories"
    
    # 15 categories exist in database
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<ExpenseCategory(id={self.id}, name='{self.name}')>"