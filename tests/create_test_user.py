#!/usr/bin/env python3
"""
Create a test user for dashboard testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from models import get_db, User
from services.auth_service import create_user
from datetime import datetime

def create_test_user():
    """Create a test user in the database"""
    db = next(get_db())
    
    try:
        # Check if user already exists
        existing = db.query(User).filter(User.email == "test@example.com").first()
        if existing:
            print("Test user already exists!")
            return True
        
        # Create new user
        user = create_user(
            db=db,
            email="test@example.com",
            password="testpassword123"
        )
        
        if user:
            print("✓ Test user created successfully!")
            print("  Email: test@example.com")
            print("  Password: testpassword123")
            return True
        else:
            print("✗ Failed to create test user")
            return False
            
    except Exception as e:
        print(f"Error creating test user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=== Creating Test User ===")
    if create_test_user():
        print("\nYou can now run: python test_dashboard_data.py")
    else:
        print("\nFailed to create test user")