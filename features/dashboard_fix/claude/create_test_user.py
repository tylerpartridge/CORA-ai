#!/usr/bin/env python3
"""Create a test user with known credentials for dashboard testing"""

import sys
import os
sys.path.insert(0, '/mnt/host/c/CORA')

# Use the same password hashing as the auth service
from passlib.context import CryptContext
import sqlite3
from datetime import datetime

# Same configuration as auth_service.py
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def create_test_user():
    """Create a test user directly in the database"""
    
    conn = sqlite3.connect('cora.db')
    cursor = conn.cursor()
    
    # Test user details
    email = "dashtest@example.com"
    password = "Password123!"  # Password with uppercase and special char
    hashed_password = pwd_context.hash(password)  # Use bcrypt like auth service
    
    try:
        # Check if user exists
        cursor.execute("SELECT email FROM users WHERE email=?", (email,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"User {email} already exists, updating password...")
            cursor.execute("""
                UPDATE users 
                SET hashed_password=?, is_active='true', email_verified='true'
                WHERE email=?
            """, (hashed_password, email))
        else:
            print(f"Creating new user {email}...")
            cursor.execute("""
                INSERT INTO users (email, hashed_password, created_at, is_active, is_admin, email_verified, email_verified_at)
                VALUES (?, ?, ?, 'true', 'false', 'true', ?)
            """, (email, hashed_password, datetime.now(), datetime.now()))
        
        conn.commit()
        print(f"[OK] User {email} ready with password: {password}")
        
        # Get user ID for sample data
        cursor.execute("SELECT id FROM users WHERE email=?", (email,))
        user_id = cursor.fetchone()[0]
        
        # Check if user has any jobs
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE user_id=?", (user_id,))
        job_count = cursor.fetchone()[0]
        
        if job_count == 0:
            print("\nCreating sample jobs...")
            jobs = [
                ("JOB001", "Kitchen Remodel - Smith", "active", 15000.00),
                ("JOB002", "Bathroom Renovation - Jones", "active", 8500.00),
                ("JOB003", "Deck Construction - Wilson", "completed", 12000.00),
                ("JOB004", "Basement Finishing - Brown", "active", 25000.00)
            ]
            
            for job_id, job_name, status, amount in jobs:
                cursor.execute("""
                    INSERT INTO jobs (user_id, job_id, job_name, status, quoted_amount, start_date, created_at)
                    VALUES (?, ?, ?, ?, ?, date('now', '-30 days'), ?)
                """, (user_id, job_id, job_name, status, amount, datetime.now()))
            
            conn.commit()
            print(f"[OK] Created {len(jobs)} sample jobs")
            
            # Get job IDs for expenses
            cursor.execute("SELECT id, job_name FROM jobs WHERE user_id=?", (user_id,))
            user_jobs = cursor.fetchall()
            
            # Create sample expenses
            print("\nCreating sample expenses...")
            expense_count = 0
            for job_id, job_name in user_jobs:
                # Create 5 expenses per job (using existing category IDs)
                expenses = [
                    (1, 25000, "Lumber and supplies"),  # Office Supplies as placeholder
                    (3, 35000, "Crew wages"),  # Transportation as placeholder
                    (1, 15000, "Tool rental"),
                    (2, 5000, "Building permits"),  # Meals as placeholder
                    (3, 45000, "Electrical work")
                ]
                
                for category_id, amount, description in expenses:
                    cursor.execute("""
                        INSERT INTO expenses (user_id, job_id, job_name, category_id, amount_cents, description, expense_date, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, date('now', '-' || abs(random() % 30) || ' days'), ?)
                    """, (user_id, job_id, job_name, category_id, amount, description, datetime.now()))
                    expense_count += 1
            
            conn.commit()
            print(f"[OK] Created {expense_count} sample expenses")
        else:
            print(f"User already has {job_count} jobs")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("="*60)
    print("Creating Test User for Dashboard")
    print("="*60)
    
    if create_test_user():
        print("\n" + "="*60)
        print("[OK] Test user ready!")
        print("Email: dashtest@example.com")
        print("Password: Password123!")
        print("="*60)
    else:
        print("\n[ERROR] Failed to create test user")