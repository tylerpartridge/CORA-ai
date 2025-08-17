#!/usr/bin/env python3
"""
Create demo user for CORA
Run this to create demo@cora.ai user for demo functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import get_db, User
from dependencies.auth import get_password_hash
from sqlalchemy.orm import Session

def create_demo_user():
    """Create demo user if it doesn't exist"""
    db = next(get_db())
    
    try:
        # Check if demo user exists
        demo_user = db.query(User).filter(User.email == "demo@cora.ai").first()
        
        if demo_user:
            print("Demo user already exists!")
            return
        
        # Create demo user
        demo_user = User(
            email="demo@cora.ai",
            hashed_password=get_password_hash("demo123"),
            is_active=True,
            is_demo=True,  # If this field exists
            name="Demo Contractor",
            created_at=datetime.utcnow()
        )
        
        db.add(demo_user)
        db.commit()
        
        print("✅ Demo user created successfully!")
        print("Email: demo@cora.ai")
        print("Password: demo123")
        
    except Exception as e:
        print(f"❌ Error creating demo user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    from datetime import datetime
    create_demo_user()