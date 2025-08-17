#!/usr/bin/env python3
"""
Create test user and data for profit engine testing
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def create_test_user_and_data():
    """Create test user with sample expense data"""
    print("Creating Test User and Data...")
    print("=" * 40)
    
    try:
        from models import get_db, User, Expense, Job, BusinessProfile
        from models.base import engine, Base
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        db = next(get_db())
        
        # Check if test user exists
        test_user = db.query(User).filter(User.email == "glen.day@testcontractor.com").first()
        
        if not test_user:
            # Create test user
            test_user = User(
                email="glen.day@testcontractor.com",
                hashed_password="$2b$12$test_hash_for_testing_only",
                is_active="true",
                is_admin="false"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"[OK] Created test user: {test_user.email}")
        else:
            print(f"[OK] Test user exists: {test_user.email}")
        
        # Create business profile
        business_profile = db.query(BusinessProfile).filter(
            BusinessProfile.user_email == test_user.email
        ).first()
        
        if not business_profile:
            business_profile = BusinessProfile(
                user_email=test_user.email,
                business_name="Glen Day Construction",
                business_type="General Contractor",
                industry="Construction",
                monthly_revenue_range="$50K-$100K"
            )
            db.add(business_profile)
            db.commit()
            print(f"[OK] Created business profile: {business_profile.business_name}")
        
        # Create test jobs
        existing_jobs = db.query(Job).filter(Job.user_id == test_user.id).count()
        if existing_jobs == 0:
            test_jobs = [
                Job(
                    user_id=test_user.id,
                    name="Martinez Kitchen Remodel",
                    customer_id=None,
                    description="Complete kitchen renovation",
                    budget=25000.00,
                    status="in_progress"
                ),
                Job(
                    user_id=test_user.id,
                    name="Williams Bathroom Addition",
                    customer_id=None,
                    description="Master bathroom addition",
                    budget=18000.00,
                    status="completed"
                )
            ]
            
            for job in test_jobs:
                db.add(job)
            db.commit()
            print(f"[OK] Created {len(test_jobs)} test jobs")
        
        # Create test expenses
        existing_expenses = db.query(Expense).filter(Expense.user_id == test_user.id).count()
        if existing_expenses == 0:
            # Get job IDs
            jobs = db.query(Job).filter(Job.user_id == test_user.id).all()
            job_ids = [job.id for job in jobs]
            
            test_expenses = []
            base_date = datetime.now() - timedelta(days=90)
            
            # Materials expenses with price variations
            vendors = {
                "Home Depot": [1200, 1450, 1380, 1520, 1290],
                "Lowes": [1150, 1200, 1180, 1250, 1160],
                "ACE Hardware": [180, 220, 200, 250, 190],
                "Menards": [1100, 1180, 1150, 1200, 1120]
            }
            
            for vendor, amounts in vendors.items():
                for i, amount in enumerate(amounts):
                    expense = Expense(
                        user_id=test_user.id,
                        job_id=random.choice(job_ids) if job_ids else None,
                        amount=amount,
                        description=f"Materials from {vendor}",
                        vendor=vendor,
                        category="Materials",
                        date=base_date + timedelta(days=i*15),
                        receipt_url=None,
                        metadata={"created_by": "test_script"}
                    )
                    test_expenses.append(expense)
            
            # Fuel expenses
            fuel_amounts = [85, 92, 88, 110, 95, 87, 145, 98]  # One outlier at 145
            for i, amount in enumerate(fuel_amounts):
                expense = Expense(
                    user_id=test_user.id,
                    job_id=random.choice(job_ids) if job_ids else None,
                    amount=amount,
                    description="Fuel for work truck",
                    vendor="Gas Station",
                    category="Fuel",
                    date=base_date + timedelta(days=i*10),
                    receipt_url=None,
                    metadata={"created_by": "test_script"}
                )
                test_expenses.append(expense)
            
            # Tool expenses
            tool_expenses = [
                {"vendor": "Harbor Freight", "amount": 150, "desc": "Power drill"},
                {"vendor": "Harbor Freight", "amount": 89, "desc": "Circular saw"},
                {"vendor": "Milwaukee Tools", "amount": 350, "desc": "Impact driver"},
                {"vendor": "DeWalt", "amount": 280, "desc": "Miter saw"}
            ]
            
            for i, tool in enumerate(tool_expenses):
                expense = Expense(
                    user_id=test_user.id,
                    job_id=random.choice(job_ids) if job_ids else None,
                    amount=tool["amount"],
                    description=tool["desc"],
                    vendor=tool["vendor"],
                    category="Tools",
                    date=base_date + timedelta(days=i*20),
                    receipt_url=None,
                    metadata={"created_by": "test_script"}
                )
                test_expenses.append(expense)
            
            # Add all expenses
            for expense in test_expenses:
                db.add(expense)
            
            db.commit()
            print(f"[OK] Created {len(test_expenses)} test expenses")
        
        # Summary
        total_expenses = db.query(Expense).filter(Expense.user_id == test_user.id).count()
        total_jobs = db.query(Job).filter(Job.user_id == test_user.id).count()
        
        print(f"\n[SUMMARY] Test data ready:")
        print(f"  User ID: {test_user.id}")
        print(f"  Expenses: {total_expenses}")
        print(f"  Jobs: {total_jobs}")
        
        return test_user.id
        
    except Exception as e:
        print(f"[ERROR] Failed to create test data: {e}")
        return None

if __name__ == "__main__":
    user_id = create_test_user_and_data()
    if user_id:
        print(f"\n[SUCCESS] Test data created. User ID: {user_id}")
    else:
        print("\n[FAILED] Could not create test data")
        sys.exit(1)