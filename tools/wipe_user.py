#!/usr/bin/env python3
"""
Complete wipe of user account and all related data
"""
import sqlite3
import os
import sys
import json
from pathlib import Path

# Fix Unicode output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

email = "tyler_partridge@hotmail.com"
db_path = "cora.db"  # Relative path from CORA directory

print(f"[DELETE] Starting complete wipe for: {email}")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 1. Check if user exists
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    if user:
        print(f"[OK] Found user: {email}")
    else:
        print(f"[INFO] User not found: {email}")
    
    # 2. Delete from business_profiles
    cursor.execute("DELETE FROM business_profiles WHERE user_email=?", (email,))
    deleted = cursor.rowcount
    if deleted:
        print(f"[OK] Deleted {deleted} business profile(s)")
    
    # 3. Delete from email_verification_tokens
    cursor.execute("DELETE FROM email_verification_tokens WHERE email=?", (email,))
    deleted = cursor.rowcount
    if deleted:
        print(f"[OK] Deleted {deleted} email verification token(s)")
    
    # 4. Delete from password_reset_tokens
    cursor.execute("DELETE FROM password_reset_tokens WHERE email=?", (email,))
    deleted = cursor.rowcount
    if deleted:
        print(f"[OK] Deleted {deleted} password reset token(s)")
    
    # 5. Delete from user_preferences
    cursor.execute("DELETE FROM user_preferences WHERE user_email=?", (email,))
    deleted = cursor.rowcount
    if deleted:
        print(f"[OK] Deleted {deleted} user preference(s)")
    
    # 6. Delete from contractor_waitlist if exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contractor_waitlist'")
    if cursor.fetchone():
        cursor.execute("DELETE FROM contractor_waitlist WHERE email=?", (email,))
        deleted = cursor.rowcount
        if deleted:
            print(f"[OK] Deleted from contractor waitlist")
    
    # 7. Delete from expenses
    cursor.execute("DELETE FROM expenses WHERE user_email=?", (email,))
    deleted = cursor.rowcount
    if deleted:
        print(f"[OK] Deleted {deleted} expense(s)")
    
    # 8. Delete from jobs if exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'")
    if cursor.fetchone():
        cursor.execute("DELETE FROM jobs WHERE user_email=?", (email,))
        deleted = cursor.rowcount
        if deleted:
            print(f"[OK] Deleted {deleted} job(s)")
    
    # 9. Delete from feedback if exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback'")
    if cursor.fetchone():
        cursor.execute("DELETE FROM feedback WHERE user_email=?", (email,))
        deleted = cursor.rowcount
        if deleted:
            print(f"[OK] Deleted {deleted} feedback item(s)")
    
    # 10. Finally, delete the user
    cursor.execute("DELETE FROM users WHERE email=?", (email,))
    deleted = cursor.rowcount
    if deleted:
        print(f"[OK] Deleted user account")
    
    # Commit all deletions
    conn.commit()
    print("[OK] Database changes committed")
    
except Exception as e:
    print(f"[ERROR] Database error: {e}")
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
        os.remove(path)
        print(f"[OK] Deleted file: {path}")

# Clear any session files (if they exist)
session_pattern = Path("data/sessions/")
if session_pattern.exists():
    for session_file in session_pattern.glob(f"*{email}*"):
        session_file.unlink()
        print(f"[OK] Deleted session: {session_file}")

print("\n[SUCCESS] Complete wipe finished!")
print("\n[NEXT] Steps to clear browser data:")
print("1. Clear browser cookies and localStorage")
print("2. Use incognito/private browsing for fresh test")
print("3. Or run this in browser console:")
print("   localStorage.clear();")
print("   document.cookie.split(';').forEach(c => document.cookie = c.replace(/^ +/, '').replace(/=.*/, '=;expires=' + new Date().toUTCString() + ';path=/'));")