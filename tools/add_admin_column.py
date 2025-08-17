#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/add_admin_column.py
🎯 PURPOSE: Database migration to add is_admin column to users table
🔗 IMPORTS: SQLAlchemy, database models
📤 EXPORTS: Migration script for admin column
"""

import os
import sys
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import get_db, User
from config import config

def add_admin_column():
    """Add is_admin column to users table and set admin user"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if column already exists
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'is_admin'
        """))
        
        if result.fetchone():
            print("✅ is_admin column already exists")
        else:
            # Add is_admin column
            db.execute(text("""
                ALTER TABLE users 
                ADD COLUMN is_admin BOOLEAN DEFAULT FALSE NOT NULL
            """))
            print("✅ Added is_admin column to users table")
        
        # Set admin user (you can change this email)
        admin_email = os.getenv("ADMIN_EMAIL", "admin@coraai.tech")
        
        # Update admin user
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if admin_user:
            admin_user.is_admin = True
            db.commit()
            print(f"✅ Set {admin_email} as admin user")
        else:
            print(f"⚠️  Admin user {admin_email} not found. Please create manually.")
            print("   You can set any user as admin by updating their is_admin field to TRUE")
        
        # Show current admin users
        admin_users = db.query(User).filter(User.is_admin == True).all()
        print(f"📋 Current admin users: {[user.email for user in admin_users]}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_admin_user():
    """Create a new admin user if needed"""
    
    # Get database session
    db = next(get_db())
    
    try:
        admin_email = os.getenv("ADMIN_EMAIL", "admin@coraai.tech")
        admin_password = os.getenv("ADMIN_PASSWORD", "AdminPassword123!")
        
        # Check if admin user exists
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if existing_admin:
            print(f"✅ Admin user {admin_email} already exists")
            return
        
        # Import password hashing
        from services.auth_service import get_password_hash
        
        # Create admin user
        admin_user = User(
            email=admin_email,
            hashed_password=get_password_hash(admin_password),
            is_active=True,
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print(f"✅ Created admin user: {admin_email}")
        print(f"   Password: {admin_password}")
        print("   ⚠️  Please change this password immediately!")
        
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Adding admin column to users table...")
    add_admin_column()
    
    print("\n👤 Creating admin user...")
    create_admin_user()
    
    print("\n✅ Admin authorization setup complete!")
    print("\n📋 Next steps:")
    print("   1. Test admin access with the admin credentials")
    print("   2. Change the admin password")
    print("   3. Set up additional admin users if needed") 