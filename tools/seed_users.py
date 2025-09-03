#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/seed_users.py
🎯 PURPOSE: Idempotent admin user seeding for production
🔗 IMPORTS: SQLAlchemy, models, auth service
📤 EXPORTS: main() function for CLI execution
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import SessionLocal, User
from services.auth_service import get_password_hash


def main():
    """
    Create admin user if not exists. Idempotent operation.
    Reads from environment:
    - ADMIN_EMAIL: Email for admin user
    - ADMIN_PASSWORD: Password for admin user  
    - ADMIN_TIMEZONE: Timezone (default: America/St_Johns)
    """
    # Read environment variables
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin_timezone = os.getenv("ADMIN_TIMEZONE", "America/St_Johns")
    
    # Validate required environment variables
    if not admin_email:
        print(json.dumps({
            "status": "error",
            "message": "ADMIN_EMAIL environment variable is required"
        }))
        return 1
    
    if not admin_password:
        print(json.dumps({
            "status": "error", 
            "message": "ADMIN_PASSWORD environment variable is required"
        }))
        return 1
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter_by(email=admin_email).first()
        
        if existing_user:
            print(json.dumps({
                "status": "exists",
                "message": f"Admin user {admin_email} already exists",
                "user_id": existing_user.id,
                "is_admin": existing_user.is_admin
            }))
            return 0
        
        # Create new admin user
        hashed_password = get_password_hash(admin_password)
        
        admin_user = User(
            email=admin_email,
            hashed_password=hashed_password,
            is_active="true",  # SQLite uses strings for booleans
            is_admin="true",   # SQLite uses strings for booleans
            email_verified="true",  # Admin users are pre-verified
            timezone=admin_timezone,
            weekly_insights_opt_in="true"
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(json.dumps({
            "status": "created",
            "message": f"Admin user {admin_email} created successfully",
            "user_id": admin_user.id,
            "timezone": admin_timezone
        }))
        return 0
        
    except Exception as e:
        db.rollback()
        print(json.dumps({
            "status": "error",
            "message": f"Failed to create admin user: {str(e)}"
        }))
        return 1
    
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())