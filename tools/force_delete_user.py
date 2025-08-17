#!/usr/bin/env python3
"""
Force delete user - handles all possible table structures
"""
import sqlite3
import os
import sys

# Fix Unicode output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

email = "tyler_partridge@hotmail.com"
db_path = "cora.db"

print(f"[FORCE DELETE] Starting aggressive wipe for: {email}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # First, let's see what tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"[INFO] Found {len(tables)} tables in database")
    
    # Check users table structure
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print("[INFO] Users table columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Try to find the user first
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    if user:
        print(f"[FOUND] User exists with data: {user[:3]}...")  # Show first 3 fields
    else:
        print("[WARNING] User not found in initial query")
    
    # Force delete from users table
    print("[ACTION] Force deleting from users table...")
    cursor.execute("DELETE FROM users WHERE email=? OR email LIKE ?", (email, f"%{email}%"))
    deleted = cursor.rowcount
    print(f"[RESULT] Deleted {deleted} user record(s)")
    
    # Delete from all other tables that might have email references
    tables_to_clean = [
        ('business_profiles', 'user_email'),
        ('email_verification_tokens', 'email'),
        ('password_reset_tokens', 'email'),
        ('user_preferences', 'user_email'),
        ('expenses', 'user_email'),
        ('feedback', 'user_email'),
        ('contractor_waitlist', 'email'),
        ('jobs', 'user_email'),
        ('onboarding_progress', 'user_email'),
        ('user_sessions', 'user_email')
    ]
    
    for table_name, email_column in tables_to_clean:
        try:
            # Check if table exists
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if cursor.fetchone():
                # Try to delete with the expected column name
                cursor.execute(f"DELETE FROM {table_name} WHERE {email_column}=? OR {email_column} LIKE ?", (email, f"%{email}%"))
                deleted = cursor.rowcount
                if deleted:
                    print(f"[OK] Deleted {deleted} record(s) from {table_name}")
            else:
                print(f"[SKIP] Table {table_name} doesn't exist")
        except sqlite3.OperationalError as e:
            # Column might not exist, try with just 'email'
            try:
                cursor.execute(f"DELETE FROM {table_name} WHERE email=? OR email LIKE ?", (email, f"%{email}%"))
                deleted = cursor.rowcount
                if deleted:
                    print(f"[OK] Deleted {deleted} record(s) from {table_name} (using 'email' column)")
            except:
                print(f"[SKIP] Could not clean {table_name}: {e}")
    
    # Commit all changes
    conn.commit()
    print("[SUCCESS] All deletions committed to database")
    
    # Verify deletion
    cursor.execute("SELECT * FROM users WHERE email=? OR email LIKE ?", (email, f"%{email}%"))
    if cursor.fetchone():
        print("[ERROR] User still exists after deletion attempt!")
    else:
        print("[VERIFIED] User successfully deleted from database")
        
except Exception as e:
    print(f"[ERROR] Database operation failed: {e}")
    conn.rollback()
finally:
    conn.close()

# Delete JSON files
profile_paths = [
    f"data/business_profiles/{email}.json",
    f"data/onboarding/{email}.json",
    f"features/onboarding/{email}.json"
]

for path in profile_paths:
    if os.path.exists(path):
        try:
            os.remove(path)
            print(f"[OK] Deleted file: {path}")
        except:
            pass

print("\n[COMPLETE] Force deletion finished!")
print("\nNOW CLEAR YOUR BROWSER:")
print("1. Use Incognito/Private browsing")
print("2. Or press F12 and run:")
print("   localStorage.clear(); sessionStorage.clear();")