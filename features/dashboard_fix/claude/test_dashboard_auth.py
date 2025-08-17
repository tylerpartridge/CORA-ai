#!/usr/bin/env python3
"""Test dashboard authentication and create sample data"""

import requests
import json
import sys
from datetime import datetime, timedelta
import random

# Base URL
BASE_URL = "http://localhost:8001"

def test_login_and_dashboard():
    """Test login flow and dashboard access"""
    
    session = requests.Session()
    
    # Test with multiple users
    test_users = [
        {"email": "test311pm@example.com", "password": "TestPassword123!"},
        {"email": "logintest@coratest.com", "password": "password123"},
        {"email": "test@example.com", "password": "password123"}
    ]
    
    for user in test_users:
        print(f"\n{'='*60}")
        print(f"Testing with user: {user['email']}")
        print(f"{'='*60}")
        
        # Try to login
        login_response = session.post(f"{BASE_URL}/api/auth/login", json=user)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ Login successful!")
            login_data = login_response.json()
            print(f"  Token received: {'access_token' in login_data}")
            print(f"  Cookies: {session.cookies.get_dict()}")
            
            # Test dashboard endpoints
            endpoints = [
                "/api/dashboard/summary",
                "/api/dashboard/metrics?period=month",
                "/api/dashboard/insights",
                "/api/dashboard/jobs",
                "/api/dashboard/expenses/recent"
            ]
            
            for endpoint in endpoints:
                print(f"\nTesting {endpoint}...")
                response = session.get(f"{BASE_URL}{endpoint}")
                print(f"  Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ Success! Data keys: {list(data.keys())[:5]}")
                else:
                    print(f"  ❌ Error: {response.text[:200]}")
            
            # If successful, break after first working user
            if login_response.status_code == 200:
                return True
        else:
            print(f"❌ Login failed: {login_response.text[:200]}")
    
    return False

def create_sample_data():
    """Create sample data for testing"""
    print("\n" + "="*60)
    print("Creating sample data for dashboard testing...")
    print("="*60)
    
    # Import necessary modules
    import sys
    sys.path.insert(0, '/mnt/host/c/CORA')
    
    from models import get_db, User, Job, Expense, ExpenseCategory
    from sqlalchemy.orm import Session
    from datetime import datetime, timedelta
    import random
    
    # Get database session
    db = next(get_db())
    
    try:
        # Find a test user
        test_user = db.query(User).filter(User.email == "test311pm@example.com").first()
        if not test_user:
            print("Test user not found, checking for any user...")
            test_user = db.query(User).first()
        
        if not test_user:
            print("❌ No users found in database!")
            return False
            
        print(f"Using user: {test_user.email} (ID: {test_user.id})")
        
        # Check existing data
        job_count = db.query(Job).filter(Job.user_id == test_user.id).count()
        expense_count = db.query(Expense).filter(Expense.user_id == test_user.id).count()
        print(f"Existing: {job_count} jobs, {expense_count} expenses")
        
        if job_count == 0:
            # Create sample jobs
            jobs_data = [
                {"job_name": "Kitchen Remodel - Smith", "status": "active", "quoted_amount": 15000},
                {"job_name": "Bathroom Renovation - Jones", "status": "active", "quoted_amount": 8500},
                {"job_name": "Deck Construction - Wilson", "status": "completed", "quoted_amount": 12000},
                {"job_name": "Basement Finishing - Brown", "status": "active", "quoted_amount": 25000}
            ]
            
            for job_data in jobs_data:
                job = Job(
                    user_id=test_user.id,
                    job_name=job_data["job_name"],
                    status=job_data["status"],
                    quoted_amount_cents=job_data["quoted_amount"] * 100,
                    start_date=datetime.now() - timedelta(days=random.randint(10, 60)),
                    created_at=datetime.now()
                )
                db.add(job)
            
            db.commit()
            print(f"✅ Created {len(jobs_data)} sample jobs")
        
        if expense_count == 0:
            # Create sample expenses
            categories = ["materials", "labor", "equipment", "permits", "subcontractor"]
            jobs = db.query(Job).filter(Job.user_id == test_user.id).all()
            
            expenses_created = 0
            for job in jobs:
                # Create 5-10 expenses per job
                for _ in range(random.randint(5, 10)):
                    expense = Expense(
                        user_id=test_user.id,
                        job_id=job.id,
                        job_name=job.job_name,
                        category=random.choice(categories),
                        amount_cents=random.randint(50, 500) * 100,  # $50-$500
                        description=f"Sample expense for {job.job_name}",
                        expense_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                        created_at=datetime.now()
                    )
                    db.add(expense)
                    expenses_created += 1
            
            db.commit()
            print(f"✅ Created {expenses_created} sample expenses")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("CORA Dashboard Authentication Test")
    print("="*60)
    
    # First, create sample data
    if create_sample_data():
        print("\n✅ Sample data ready")
    else:
        print("\n⚠️ Sample data creation had issues")
    
    # Then test authentication
    if test_login_and_dashboard():
        print("\n✅ Dashboard authentication working!")
    else:
        print("\n❌ Dashboard authentication failed - needs investigation")