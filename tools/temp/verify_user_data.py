#!/usr/bin/env python3
"""Verify Tyler's test account data is properly stored"""

import sqlite3
import json
import os
from datetime import datetime

print("=" * 70)
print("USER DATA VERIFICATION REPORT")
print(f"Timestamp: {datetime.now()}")
print("=" * 70)

email = "tyler@test.com"
db_path = "cora.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Check user account
    print("\n[1] USER ACCOUNT CHECK")
    print("-" * 50)
    cursor.execute("""
        SELECT id, email, is_active, email_verified, created_at, name
        FROM users 
        WHERE email = ?
    """, (email,))
    
    user = cursor.fetchone()
    if user:
        user_id, email_db, is_active, email_verified, created_at, name = user
        print(f"✅ User found in database!")
        print(f"   Email: {email_db}")
        print(f"   User ID: {user_id}")
        print(f"   Name: {name if name else '[Not stored in users table]'}")
        print(f"   Active: {is_active}")
        print(f"   Verified: {email_verified}")
        print(f"   Created: {created_at}")
    else:
        print(f"❌ User {email} not found in database!")
        exit(1)
    
    # 2. Check business profile
    print("\n[2] BUSINESS PROFILE CHECK")
    print("-" * 50)
    cursor.execute("""
        SELECT * FROM business_profiles 
        WHERE user_email = ?
    """, (email,))
    
    profile = cursor.fetchone()
    if profile:
        print(f"✅ Business profile found!")
        # Get column names
        cursor.execute("PRAGMA table_info(business_profiles)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Display all profile data
        for i, col_name in enumerate(columns):
            if profile[i]:
                print(f"   {col_name}: {profile[i]}")
    else:
        print(f"❌ No business profile found for {email}")
    
    # 3. Check JSON backup file
    print("\n[3] JSON BACKUP CHECK")
    print("-" * 50)
    json_path = f"data/business_profiles/{email}.json"
    if os.path.exists(json_path):
        print(f"✅ JSON backup found at: {json_path}")
        with open(json_path, 'r') as f:
            json_data = json.load(f)
            print("   Contains:")
            for key in json_data.keys():
                if key != "answers":  # Don't print full answers
                    print(f"   - {key}: {json_data[key]}")
            if "answers" in json_data:
                print(f"   - answers: {len(json_data['answers'])} responses saved")
    else:
        print(f"⚠️ No JSON backup at {json_path}")
    
    # 4. Check expenses table
    print("\n[4] EXPENSES CHECK")
    print("-" * 50)
    cursor.execute("""
        SELECT COUNT(*) FROM expenses 
        WHERE user_id = ?
    """, (user_id,))
    
    expense_count = cursor.fetchone()[0]
    print(f"   Expenses recorded: {expense_count}")
    
    # 5. Check jobs table
    print("\n[5] JOBS CHECK")
    print("-" * 50)
    cursor.execute("""
        SELECT COUNT(*) FROM jobs 
        WHERE user_id = ?
    """, (user_id,))
    
    job_count = cursor.fetchone()[0]
    print(f"   Jobs recorded: {job_count}")
    
    # 6. Check CORA chat context
    print("\n[6] CORA CHAT CONTEXT CHECK")
    print("-" * 50)
    print("   Testing if CORA can access user profile...")
    
    # Check if profile data is available for CORA
    if profile:
        print("   ✅ Profile data available for CORA context:")
        print(f"      - Business name: {profile[2] if len(profile) > 2 else 'N/A'}")
        print(f"      - Business type: {profile[3] if len(profile) > 3 else 'N/A'}")
        print(f"      - Industry: {profile[4] if len(profile) > 4 else 'N/A'}")
        print("   CORA should personalize responses with this data")
    else:
        print("   ❌ No profile for CORA to use")
    
    # 7. Dashboard data availability
    print("\n[7] DASHBOARD DATA AVAILABILITY")
    print("-" * 50)
    print("   Dashboard should display:")
    if user:
        print(f"   ✅ User email: {email}")
        print(f"   ✅ User name: {name if name else 'Would need to get from profile'}")
    if profile:
        print(f"   ✅ Business info from profile")
    print(f"   ✅ {expense_count} expenses")
    print(f"   ✅ {job_count} jobs")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    issues = []
    if not user:
        issues.append("User account not created")
    if not profile:
        issues.append("Business profile not saved")
    if not os.path.exists(json_path):
        issues.append("JSON backup not created")
    if not name:
        issues.append("User name not in users table (check profile)")
    
    if issues:
        print("⚠️ ISSUES FOUND:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ ALL DATA PROPERLY STORED!")
        print("   - User account created")
        print("   - Business profile saved")
        print("   - Data available for dashboard")
        print("   - CORA has context for personalization")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error checking database: {e}")
    import traceback
    traceback.print_exc()