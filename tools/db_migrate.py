#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/db_migrate.py
🎯 PURPOSE: Database migration script for SQLite to PostgreSQL transition
🔗 IMPORTS: SQLAlchemy, models
📤 EXPORTS: Migration functions
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import models
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from models.base import Base, engine, DATABASE_URL
from models import (
    User, Expense, ExpenseCategory, Customer, Subscription, 
    Payment, BusinessProfile, UserPreference, PasswordResetToken,
    PlaidIntegration, PlaidAccount, PlaidTransaction, PlaidSyncHistory,
    QuickBooksIntegration, StripeIntegration
)

def create_tables():
    """Create all database tables"""
    print("🗄️ Creating database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
        
        # Verify tables exist
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            print(f"📋 Found {len(tables)} tables: {', '.join(tables)}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

def seed_categories():
    """Seed expense categories"""
    print("🌱 Seeding expense categories...")
    
    categories = [
        "Food & Dining",
        "Transportation", 
        "Entertainment",
        "Shopping",
        "Utilities",
        "Healthcare",
        "Travel",
        "Education",
        "Business",
        "Personal Care",
        "Home & Garden",
        "Technology",
        "Insurance",
        "Taxes",
        "Other"
    ]
    
    try:
        from sqlalchemy.orm import Session
        db = Session(engine)
        
        # Check if categories already exist
        existing = db.query(ExpenseCategory).count()
        if existing > 0:
            print(f"✅ {existing} categories already exist, skipping seed")
            return True
        
        # Add categories
        for name in categories:
            category = ExpenseCategory(name=name)
            db.add(category)
        
        db.commit()
        print(f"✅ Added {len(categories)} expense categories")
        
    except Exception as e:
        print(f"❌ Error seeding categories: {e}")
        return False
    
    return True

def test_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 Starting database migration...")
    print(f"📊 Database URL: {DATABASE_URL}")
    
    # Test connection
    if not test_connection():
        return False
    
    # Create tables
    if not create_tables():
        return False
    
    # Seed categories
    if not seed_categories():
        return False
    
    print("🎉 Database migration completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 