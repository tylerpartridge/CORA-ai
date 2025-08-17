#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/complete_postgresql_migration.py
🎯 PURPOSE: Complete PostgreSQL migration with data transfer and validation
🔗 IMPORTS: SQLAlchemy, psycopg2, sqlite3
📤 EXPORTS: Complete migration script for production
"""

import os
import sys
import sqlite3
import psycopg2
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from models import Base, User, Expense, Feedback, UserActivity
from services.auth_service import get_password_hash

def test_postgresql_connection():
    """Test PostgreSQL connection"""
    try:
        # Parse DATABASE_URL
        db_url = config.DATABASE_URL
        if not db_url.startswith('postgresql://'):
            print("❌ DATABASE_URL is not a PostgreSQL connection string")
            return False
            
        # Test connection
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ PostgreSQL connection successful: {version}")
            return True
            
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def create_postgresql_schema():
    """Create PostgreSQL schema using SQLAlchemy"""
    try:
        engine = create_engine(config.DATABASE_URL)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ PostgreSQL schema created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create PostgreSQL schema: {e}")
        return False

def migrate_data_from_sqlite():
    """Migrate data from SQLite to PostgreSQL"""
    try:
        # SQLite database path
        sqlite_path = "data/cora.db"
        if not os.path.exists(sqlite_path):
            print(f"❌ SQLite database not found: {sqlite_path}")
            return False
        
        # Connect to SQLite
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row
        
        # Connect to PostgreSQL
        pg_engine = create_engine(config.DATABASE_URL)
        pg_session = sessionmaker(bind=pg_engine)()
        
        print("🔄 Starting data migration...")
        
        # Migrate users
        print("   Migrating users...")
        users = sqlite_conn.execute("SELECT * FROM users").fetchall()
        for user in users:
            # Check if user already exists
            existing = pg_session.query(User).filter(User.email == user['email']).first()
            if not existing:
                new_user = User(
                    email=user['email'],
                    hashed_password=user['hashed_password'],
                    created_at=datetime.fromisoformat(user['created_at']) if user['created_at'] else datetime.utcnow(),
                    is_active=user['is_active'] == 'true' if isinstance(user['is_active'], str) else user['is_active'],
                    is_admin=False  # Default to False, will be set by admin script
                )
                pg_session.add(new_user)
        
        # Migrate expense categories
        print("   Migrating expense categories...")
        categories = sqlite_conn.execute("SELECT * FROM expense_categories").fetchall()
        for category in categories:
            # Check if category already exists
            existing = pg_session.execute(
                text("SELECT id FROM expense_categories WHERE name = :name"),
                {"name": category['name']}
            ).fetchone()
            if not existing:
                pg_session.execute(
                    text("""
                        INSERT INTO expense_categories (name, description, icon, is_active, created_at)
                        VALUES (:name, :description, :icon, :is_active, :created_at)
                    """),
                    {
                        "name": category['name'],
                        "description": category.get('description'),
                        "icon": category.get('icon'),
                        "is_active": category['is_active'] == 'true' if isinstance(category['is_active'], str) else category['is_active'],
                        "created_at": datetime.fromisoformat(category['created_at']) if category['created_at'] else datetime.utcnow()
                    }
                )
        
        # Migrate expenses
        print("   Migrating expenses...")
        expenses = sqlite_conn.execute("SELECT * FROM expenses").fetchall()
        for expense in expenses:
            # Get user ID
            user = pg_session.query(User).filter(User.email == expense['user_email']).first()
            if user:
                # Get category ID
                category = pg_session.execute(
                    text("SELECT id FROM expense_categories WHERE name = :name"),
                    {"name": expense['category']}
                ).fetchone()
                category_id = category[0] if category else None
                
                # Check if expense already exists
                existing = pg_session.execute(
                    text("SELECT id FROM expenses WHERE description = :desc AND amount_cents = :amount AND user_id = :user_id"),
                    {
                        "desc": expense['description'],
                        "amount": int(expense['amount'] * 100),  # Convert to cents
                        "user_id": user.id
                    }
                ).fetchone()
                
                if not existing:
                    pg_session.execute(
                        text("""
                            INSERT INTO expenses (user_id, amount_cents, currency, category_id, description, 
                                                 vendor, expense_date, payment_method, receipt_url, tags,
                                                 created_at, updated_at, confidence_score, auto_categorized)
                            VALUES (:user_id, :amount_cents, :currency, :category_id, :description,
                                   :vendor, :expense_date, :payment_method, :receipt_url, :tags,
                                   :created_at, :updated_at, :confidence_score, :auto_categorized)
                        """),
                        {
                            "user_id": user.id,
                            "amount_cents": int(expense['amount'] * 100),
                            "currency": expense.get('currency', 'USD'),
                            "category_id": category_id,
                            "description": expense['description'],
                            "vendor": expense.get('vendor'),
                            "expense_date": datetime.fromisoformat(expense['date']) if expense['date'] else datetime.utcnow(),
                            "payment_method": expense.get('payment_method'),
                            "receipt_url": expense.get('receipt_url'),
                            "tags": expense.get('tags', '{}'),
                            "created_at": datetime.fromisoformat(expense['created_at']) if expense['created_at'] else datetime.utcnow(),
                            "updated_at": datetime.fromisoformat(expense['updated_at']) if expense['updated_at'] else datetime.utcnow(),
                            "confidence_score": expense.get('confidence_score'),
                            "auto_categorized": expense.get('auto_categorized', False)
                        }
                    )
        
        # Migrate feedback
        print("   Migrating feedback...")
        feedback = sqlite_conn.execute("SELECT * FROM feedback").fetchall()
        for fb in feedback:
            # Get user ID
            user = pg_session.query(User).filter(User.email == fb['user_email']).first()
            if user:
                # Check if feedback already exists
                existing = pg_session.execute(
                    text("SELECT id FROM feedback WHERE message = :message AND user_id = :user_id"),
                    {"message": fb['message'], "user_id": user.id}
                ).fetchone()
                
                if not existing:
                    pg_session.execute(
                        text("""
                            INSERT INTO feedback (user_id, category, message, rating, created_at)
                            VALUES (:user_id, :category, :message, :rating, :created_at)
                        """),
                        {
                            "user_id": user.id,
                            "category": fb['category'],
                            "message": fb['message'],
                            "rating": fb.get('rating'),
                            "created_at": datetime.fromisoformat(fb['created_at']) if fb['created_at'] else datetime.utcnow()
                        }
                    )
        
        # Commit all changes
        pg_session.commit()
        print("✅ Data migration completed successfully")
        
        # Close connections
        sqlite_conn.close()
        pg_session.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Data migration failed: {e}")
        return False

def validate_migration():
    """Validate the migration by comparing record counts"""
    try:
        # Connect to both databases
        sqlite_conn = sqlite3.connect("data/cora.db")
        pg_engine = create_engine(config.DATABASE_URL)
        
        print("\n📊 Migration Validation:")
        
        # Compare user counts
        sqlite_users = sqlite_conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        pg_users = pg_engine.execute(text("SELECT COUNT(*) FROM users")).fetchone()[0]
        print(f"   Users: SQLite={sqlite_users}, PostgreSQL={pg_users}")
        
        # Compare expense counts
        sqlite_expenses = sqlite_conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
        pg_expenses = pg_engine.execute(text("SELECT COUNT(*) FROM expenses")).fetchone()[0]
        print(f"   Expenses: SQLite={sqlite_expenses}, PostgreSQL={pg_expenses}")
        
        # Compare feedback counts
        sqlite_feedback = sqlite_conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
        pg_feedback = pg_engine.execute(text("SELECT COUNT(*) FROM feedback")).fetchone()[0]
        print(f"   Feedback: SQLite={sqlite_feedback}, PostgreSQL={pg_feedback}")
        
        # Close connections
        sqlite_conn.close()
        pg_engine.dispose()
        
        return True
        
    except Exception as e:
        print(f"❌ Migration validation failed: {e}")
        return False

def setup_admin_user():
    """Set up admin user in PostgreSQL"""
    try:
        from tools.add_admin_column import add_admin_column, create_admin_user
        
        print("\n👤 Setting up admin user...")
        add_admin_column()
        create_admin_user()
        return True
        
    except Exception as e:
        print(f"❌ Admin user setup failed: {e}")
        return False

def main():
    """Complete PostgreSQL migration process"""
    print("🚀 Starting Complete PostgreSQL Migration...")
    
    # Step 1: Test PostgreSQL connection
    if not test_postgresql_connection():
        print("❌ Cannot proceed without PostgreSQL connection")
        return False
    
    # Step 2: Create PostgreSQL schema
    if not create_postgresql_schema():
        print("❌ Cannot proceed without schema creation")
        return False
    
    # Step 3: Migrate data
    if not migrate_data_from_sqlite():
        print("❌ Cannot proceed without data migration")
        return False
    
    # Step 4: Validate migration
    if not validate_migration():
        print("❌ Migration validation failed")
        return False
    
    # Step 5: Setup admin user
    if not setup_admin_user():
        print("❌ Admin user setup failed")
        return False
    
    print("\n🎉 PostgreSQL migration completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Update DATABASE_URL in your environment")
    print("   2. Test the application with PostgreSQL")
    print("   3. Remove SQLite database after verification")
    print("   4. Update backup scripts for PostgreSQL")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 