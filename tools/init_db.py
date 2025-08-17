#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/init_db.py
🎯 PURPOSE: Initialize database with tables and sample data
🔗 IMPORTS: models, SQLAlchemy
📤 EXPORTS: None
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Base, engine, SessionLocal
from models.expense_category import ExpenseCategory
from models.expense import Expense
from models.user_activity import UserActivity
from datetime import datetime

def init_database():
    """Initialize database with tables and sample data"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Adding sample expense categories...")
    db = SessionLocal()
    
    # Sample expense categories
    categories = [
        {"name": "Office Supplies", "description": "Office equipment and supplies"},
        {"name": "Meals & Entertainment", "description": "Food, drinks, and entertainment"},
        {"name": "Transportation", "description": "Travel and transportation costs"},
        {"name": "Software & Subscriptions", "description": "Software licenses and subscriptions"},
        {"name": "Marketing & Advertising", "description": "Marketing and advertising expenses"},
        {"name": "Shipping & Postage", "description": "Shipping and postage costs"},
        {"name": "Professional Development", "description": "Training and education"},
        {"name": "Travel", "description": "Business travel expenses"},
        {"name": "Utilities", "description": "Utility bills and services"},
        {"name": "Insurance", "description": "Insurance premiums"},
        {"name": "Other", "description": "Miscellaneous expenses"}
    ]
    
    for category_data in categories:
        existing = db.query(ExpenseCategory).filter(
            ExpenseCategory.name == category_data["name"]
        ).first()
        
        if not existing:
            category = ExpenseCategory(**category_data)
            db.add(category)
            print(f"Added category: {category_data['name']}")
    
    db.commit()
    db.close()
    print("Database initialization complete!")

if __name__ == "__main__":
    init_database() 