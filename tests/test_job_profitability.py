#!/usr/bin/env python3
"""
Test job profitability with construction sample data
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths

import asyncio
import sys
sys.path.append('/mnt/host/c/CORA')

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import get_db, User, Job, Expense, ExpenseCategory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cora.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_sample_data():
    """Create sample construction jobs and expenses"""
    db = next(get_test_db())
    
    # Get or create test user
    user = db.query(User).filter(User.email == "test@contractor.com").first()
    if not user:
        user = User(
            email="test@contractor.com",
            hashed_password="test",
            is_active=True
        )
        db.add(user)
        db.commit()
    
    print(f"Using user: {user.email} (ID: {user.id})")
    
    # Create construction categories if they don't exist
    categories = [
        ("Materials - Hardware", "General hardware and supplies"),
        ("Materials - Lumber", "Wood and lumber products"),
        ("Materials - Electrical", "Electrical supplies"),
        ("Materials - Plumbing", "Plumbing supplies"),
        ("Labor - Crew", "Crew wages and meals"),
        ("Labor - Subcontractors", "Subcontractor costs"),
        ("Equipment - Rental", "Equipment rentals"),
        ("Equipment - Fuel", "Fuel and vehicle costs"),
        ("Permits & Fees", "Permits and inspection fees"),
    ]
    
    category_map = {}
    for name, desc in categories:
        cat = db.query(ExpenseCategory).filter(ExpenseCategory.name == name).first()
        if not cat:
            cat = ExpenseCategory(name=name, description=desc)
            db.add(cat)
            db.commit()
        category_map[name] = cat.id
    
    # Create sample jobs
    jobs_data = [
        {
            "job_id": "JOB-001",
            "job_name": "Johnson Bathroom Remodel",
            "customer_name": "Robert Johnson",
            "job_address": "123 Oak Street, Springfield",
            "quoted_amount": 12500.00,
            "status": "active",
            "start_date": datetime.now() - timedelta(days=14)
        },
        {
            "job_id": "JOB-002", 
            "job_name": "Smith Kitchen Renovation",
            "customer_name": "Sarah Smith",
            "job_address": "456 Maple Ave, Springfield",
            "quoted_amount": 18750.00,
            "status": "active",
            "start_date": datetime.now() - timedelta(days=21)
        },
        {
            "job_id": "JOB-003",
            "job_name": "Miller House Rewire",
            "customer_name": "Mike Miller", 
            "job_address": "789 Pine Road, Springfield",
            "quoted_amount": 8500.00,
            "status": "completed",
            "start_date": datetime.now() - timedelta(days=45),
            "end_date": datetime.now() - timedelta(days=5)
        }
    ]
    
    # Create jobs
    for job_data in jobs_data:
        job = db.query(Job).filter(
            Job.user_id == user.id,
            Job.job_id == job_data["job_id"]
        ).first()
        
        if not job:
            job = Job(user_id=user.id, **job_data)
            db.add(job)
            db.commit()
            print(f"Created job: {job.job_name}")
        else:
            print(f"Job exists: {job.job_name}")
    
    # Create sample expenses for each job
    expenses_data = [
        # Johnson Bathroom expenses
        {"job_name": "Johnson Bathroom Remodel", "vendor": "Home Depot", "amount": 347.00, 
         "category": "Materials - Hardware", "description": "Bathroom fixtures and hardware"},
        {"job_name": "Johnson Bathroom Remodel", "vendor": "Lowes", "amount": 892.50,
         "category": "Materials - Plumbing", "description": "Shower valve and plumbing supplies"},
        {"job_name": "Johnson Bathroom Remodel", "vendor": "Tile Shop", "amount": 1250.00,
         "category": "Materials - Hardware", "description": "Bathroom tile and grout"},
        {"job_name": "Johnson Bathroom Remodel", "vendor": "Labor", "amount": 2400.00,
         "category": "Labor - Crew", "description": "Demo and installation - 3 days"},
        {"job_name": "Johnson Bathroom Remodel", "vendor": "City Permits", "amount": 175.00,
         "category": "Permits & Fees", "description": "Bathroom renovation permit"},
        
        # Smith Kitchen expenses  
        {"job_name": "Smith Kitchen Renovation", "vendor": "Home Depot", "amount": 2847.32,
         "category": "Materials - Hardware", "description": "Cabinets and hardware"},
        {"job_name": "Smith Kitchen Renovation", "vendor": "Appliance Store", "amount": 4599.00,
         "category": "Materials - Hardware", "description": "New appliances package"},
        {"job_name": "Smith Kitchen Renovation", "vendor": "Electrical Supply", "amount": 468.90,
         "category": "Materials - Electrical", "description": "New outlets and wiring"},
        {"job_name": "Smith Kitchen Renovation", "vendor": "Granite Works", "amount": 3200.00,
         "category": "Labor - Subcontractors", "description": "Countertop fabrication and install"},
        {"job_name": "Smith Kitchen Renovation", "vendor": "Labor", "amount": 3600.00,
         "category": "Labor - Crew", "description": "Kitchen demo and install - 5 days"},
        
        # Miller Rewire expenses
        {"job_name": "Miller House Rewire", "vendor": "Electrical Supply", "amount": 1847.25,
         "category": "Materials - Electrical", "description": "Wire, breakers, and panel"},
        {"job_name": "Miller House Rewire", "vendor": "Home Depot", "amount": 234.18,
         "category": "Materials - Electrical", "description": "Outlets, switches, and covers"},
        {"job_name": "Miller House Rewire", "vendor": "Labor", "amount": 4800.00,
         "category": "Labor - Crew", "description": "Complete house rewire - 6 days"},
        {"job_name": "Miller House Rewire", "vendor": "City Permits", "amount": 425.00,
         "category": "Permits & Fees", "description": "Electrical permit and inspection"},
    ]
    
    # Add expenses
    for exp_data in expenses_data:
        # Check if similar expense exists
        existing = db.query(Expense).filter(
            Expense.user_id == user.id,
            Expense.job_name == exp_data["job_name"],
            Expense.amount_cents == int(exp_data["amount"] * 100),
            Expense.vendor == exp_data["vendor"]
        ).first()
        
        if not existing:
            expense = Expense(
                user_id=user.id,
                expense_date=datetime.now() - timedelta(days=7),
                description=exp_data["description"],
                amount_cents=int(exp_data["amount"] * 100),
                currency="USD",
                vendor=exp_data["vendor"],
                category_id=category_map[exp_data["category"]],
                job_name=exp_data["job_name"],
                payment_method="Credit Card"
            )
            db.add(expense)
    
    db.commit()
    print("\nSample data created successfully!")
    
    # Show job profitability summary
    print("\n" + "="*60)
    print("JOB PROFITABILITY SUMMARY")
    print("="*60)
    
    jobs = db.query(Job).filter(Job.user_id == user.id).all()
    for job in jobs:
        # Calculate total expenses for this job
        total_expenses = db.query(func.sum(Expense.amount_cents)).filter(
            Expense.user_id == user.id,
            Expense.job_name == job.job_name
        ).scalar() or 0
        
        total_expenses = total_expenses / 100  # Convert to dollars
        quoted = job.quoted_amount or 0
        profit = quoted - total_expenses
        margin = (profit / quoted * 100) if quoted > 0 else 0
        
        print(f"\n{job.job_name}")
        print(f"  Customer: {job.customer_name}")
        print(f"  Status: {job.status}")
        print(f"  Quoted: ${quoted:,.2f}")
        print(f"  Costs: ${total_expenses:,.2f}")
        print(f"  Profit: ${profit:,.2f} ({margin:.1f}% margin)")
        
        if margin < 20:
            print(f"  [WARNING]  WARNING: Low margin!")
        elif margin > 30:
            print(f"  [OK] Great margin!")

if __name__ == "__main__":
    create_sample_data()