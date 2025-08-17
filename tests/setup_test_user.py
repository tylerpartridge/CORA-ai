#!/usr/bin/env python3
"""
Create a test user with known password for CORA
"""

from models import SessionLocal, User
from services.auth_service import get_password_hash
import sys
import os

def create_test_user():
    """Create a test user for authentication testing"""
    db = SessionLocal()
    
    # Test user details - use environment variables for production
    test_email = os.getenv("TEST_USER_EMAIL", "test@cora.com")
    test_password = os.getenv("TEST_USER_PASSWORD", "TestPassword123!")
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == test_email).first()
        if existing_user:
            print(f"Test user already exists: {test_email}")
            # Update password
            existing_user.hashed_password = get_password_hash(test_password)
            db.commit()
            print("Password updated successfully!")
        else:
            # Create new user
            new_user = User(
                email=test_email,
                hashed_password=get_password_hash(test_password),
                is_active="true"
            )
            db.add(new_user)
            db.commit()
            print(f"Test user created successfully!")
        
        print(f"\nTest User Credentials:")
        print(f"Email: {test_email}")
        print(f"Password: {test_password}")
        print("\nYou can now login with these credentials!")
        
    except Exception as e:
        print(f"Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()