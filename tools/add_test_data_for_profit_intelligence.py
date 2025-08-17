#!/usr/bin/env python3
"""
Add test data for profit intelligence testing
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import random
from decimal import Decimal

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def create_test_data():
    """Create test data for profit intelligence"""
    print("Creating Test Data for Profit Intelligence...")
    print("=" * 50)
    
    try:
        from models import get_db, User, Expense, Job, BusinessProfile
        from models.base import engine, Base
        from models.expense_category import ExpenseCategory
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        db = next(get_db())
        
        # Find or create test user
        test_user = db.query(User).filter(User.email == "glen.day@testcontractor.com").first()
        
        if not test_user:
            print("[ERROR] Test user not found. Run create_test_user.py first")
            return
        
        print(f"[OK] Using test user: {test_user.email}")
        
        # Create expense categories if needed
        categories = ["Materials", "Labor", "Equipment", "Subcontractors", "Permits", "Other"]
        for cat_name in categories:
            cat = db.query(ExpenseCategory).filter(ExpenseCategory.name == cat_name).first()
            if not cat:
                cat = ExpenseCategory(name=cat_name, description=f"{cat_name} expenses")
                db.add(cat)
        db.commit()
        
        # Create test jobs
        jobs = [
            {
                "job_id": "JOB-2024-001",
                "job_name": "Kitchen Remodel - Smith Residence",
                "customer_name": "John Smith",
                "job_address": "123 Main St, Austin, TX",
                "quoted_amount": Decimal("25000.00"),
                "status": "completed"
            },
            {
                "job_id": "JOB-2024-002",
                "job_name": "Bathroom Renovation - Johnson",
                "customer_name": "Mary Johnson",
                "job_address": "456 Oak Ave, Austin, TX",
                "quoted_amount": Decimal("12000.00"),
                "status": "completed"
            },
            {
                "job_id": "JOB-2024-003",
                "job_name": "Deck Construction - Davis",
                "customer_name": "Robert Davis",
                "job_address": "789 Pine St, Austin, TX",
                "quoted_amount": Decimal("8000.00"),
                "status": "active"
            }
        ]
        
        for job_data in jobs:
            existing = db.query(Job).filter(Job.job_id == job_data["job_id"]).first()
            if not existing:
                job = Job(
                    user_id=test_user.id,
                    **job_data,
                    start_date=datetime.now() - timedelta(days=random.randint(30, 90)),
                    end_date=datetime.now() - timedelta(days=random.randint(1, 29)) if job_data["status"] == "completed" else None
                )
                db.add(job)
                print(f"[OK] Created job: {job_data['job_name']}")
        
        db.commit()
        
        # Create test expenses
        vendors = ["Home Depot", "Lowes", "Ace Hardware", "Ferguson", "ProBuild"]
        expense_descriptions = {
            "Materials": ["Lumber", "Drywall", "Paint", "Tiles", "Fixtures"],
            "Labor": ["Hourly wages", "Contractor payment", "Helper wages"],
            "Equipment": ["Tool rental", "Equipment lease", "Maintenance"],
            "Subcontractors": ["Electrician", "Plumber", "HVAC specialist"],
            "Permits": ["Building permit", "Electrical permit", "Inspection fee"]
        }
        
        # Get all categories
        all_categories = db.query(ExpenseCategory).all()
        
        # Create 50-100 expenses over the past 6 months
        for i in range(75):
            category = random.choice(all_categories)
            if category.name in expense_descriptions:
                desc_list = expense_descriptions[category.name]
            else:
                desc_list = ["Miscellaneous expense"]
            
            amount_dollars = round(random.uniform(50, 2000), 2)
            expense = Expense(
                user_id=test_user.id,
                amount_cents=int(amount_dollars * 100),
                description=random.choice(desc_list),
                vendor=random.choice(vendors),
                expense_date=datetime.now() - timedelta(days=random.randint(1, 180)),
                category_id=category.id
            )
            db.add(expense)
        
        db.commit()
        print(f"[OK] Created 75 test expenses")
        
        print("\n[SUCCESS] Test data created successfully!")
        print("\nData Summary:")
        print(f"- User: {test_user.email}")
        print(f"- Jobs: {len(jobs)}")
        print(f"- Expenses: 75")
        print(f"- Vendors: {len(vendors)}")
        print(f"- Categories: {len(categories)}")
        
    except Exception as e:
        print(f"[ERROR] Failed to create test data: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_test_data()