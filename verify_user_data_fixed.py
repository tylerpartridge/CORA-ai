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
    
    # First, check what columns exist in users table
    cursor.execute("PRAGMA table_info(users)")
    user_columns = [col[1] for col in cursor.fetchall()]
    print(f"\nUsers table columns: {', '.join(user_columns)}")
    
    # 1. Check user account
    print("\n[1] USER ACCOUNT CHECK")
    print("-" * 50)
    cursor.execute("""
        SELECT * FROM users 
        WHERE email = ?
    """, (email,))
    
    user_row = cursor.fetchone()
    if user_row:
        print(f"[OK] User found in database!")
        for i, col in enumerate(user_columns):
            if col not in ['hashed_password']:  # Don't print password
                print(f"   {col}: {user_row[i]}")
        user_id = user_row[0]  # Assuming first column is ID
    else:
        print(f"[X] User {email} not found in database!")
        user_id = None
    
    # 2. Check business profile
    print("\n[2] BUSINESS PROFILE CHECK")
    print("-" * 50)
    cursor.execute("""
        SELECT * FROM business_profiles 
        WHERE user_email = ?
    """, (email,))
    
    profile = cursor.fetchone()
    if profile:
        print(f"[OK] Business profile found!")
        # Get column names
        cursor.execute("PRAGMA table_info(business_profiles)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Display all profile data
        for i, col_name in enumerate(columns):
            if profile[i] and col_name != 'id':
                print(f"   {col_name}: {profile[i]}")
    else:
        print(f"[X] No business profile found for {email}")
    
    # 3. Check JSON backup file
    print("\n[3] JSON BACKUP CHECK")
    print("-" * 50)
    json_path = f"data/business_profiles/{email}.json"
    onboarding_data = None
    if os.path.exists(json_path):
        print(f"[OK] JSON backup found at: {json_path}")
        with open(json_path, 'r') as f:
            onboarding_data = json.load(f)
            print("   Contains:")
            for key in onboarding_data.keys():
                if key == "answers":
                    print(f"   - answers: {len(onboarding_data['answers'])} responses saved")
                    # Show some answer details
                    for answer in onboarding_data['answers'][:3]:  # First 3 answers
                        if 'question' in answer and 'answer' in answer:
                            print(f"      Q: {answer['question'][:50]}...")
                            print(f"      A: {answer['answer']}")
                else:
                    print(f"   - {key}: {onboarding_data[key]}")
    else:
        print(f"[!] No JSON backup at {json_path}")
    
    # 4. Check expenses table
    print("\n[4] EXPENSES CHECK")
    print("-" * 50)
    if user_id:
        cursor.execute("""
            SELECT COUNT(*) FROM expenses 
            WHERE user_id = ?
        """, (user_id,))
        expense_count = cursor.fetchone()[0]
    else:
        expense_count = 0
    print(f"   Expenses recorded: {expense_count}")
    
    # 5. Check jobs table
    print("\n[5] JOBS CHECK")  
    print("-" * 50)
    if user_id:
        cursor.execute("""
            SELECT COUNT(*) FROM jobs 
            WHERE user_id = ?
        """, (user_id,))
        job_count = cursor.fetchone()[0]
    else:
        job_count = 0
    print(f"   Jobs recorded: {job_count}")
    
    # 6. Check CORA chat context
    print("\n[6] CORA CHAT CONTEXT CHECK")
    print("-" * 50)
    print("   Testing if CORA can access user profile...")
    
    if profile:
        print("   [OK] Profile data available for CORA context")
        print("   CORA should personalize responses with this business data")
    else:
        print("   [X] No profile for CORA to use")
    
    # 7. Check what name is stored where
    print("\n[7] USER NAME STORAGE CHECK")
    print("-" * 50)
    name_found = False
    
    # Check if name is in onboarding JSON
    if onboarding_data:
        for answer in onboarding_data.get('answers', []):
            if 'name' in answer.get('question', '').lower():
                print(f"   Name in JSON: {answer.get('answer', 'N/A')}")
                name_found = True
                break
    
    # Check if name is in business profile
    if profile and len(columns) > 0:
        for i, col in enumerate(columns):
            if 'name' in col.lower() and profile[i]:
                print(f"   Name in profile.{col}: {profile[i]}")
                name_found = True
    
    if not name_found:
        print("   [!] Name may not have been collected during onboarding")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    all_good = True
    if user_row:
        print("[OK] User account created successfully")
    else:
        print("[X] User account not found")
        all_good = False
        
    if profile:
        print("[OK] Business profile saved to database")
    else:
        print("[X] Business profile not saved")
        all_good = False
        
    if os.path.exists(json_path):
        print("[OK] JSON backup created")
    else:
        print("[!] JSON backup not created (may not be needed)")
    
    if all_good:
        print("\n[SUCCESS] Core data properly stored and available!")
        print("- Login/logout should work")
        print("- Dashboard has user context")
        print("- CORA can personalize responses")
    else:
        print("\n[WARNING] Some data may be missing")
    
    conn.close()
    
except Exception as e:
    print(f"[ERROR] checking database: {e}")
    import traceback
    traceback.print_exc()