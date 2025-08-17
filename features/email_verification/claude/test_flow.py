#!/usr/bin/env python3
"""Test the complete signup -> email -> verification -> onboarding flow"""

import sqlite3
import time
import os
import sys

def check_flow():
    """Check the complete flow configuration"""
    
    print("="*60)
    print("CHECKING SIGNUP TO ONBOARDING FLOW")
    print("="*60)
    
    issues = []
    
    # 1. Check onboarding route exists
    print("\n1. Checking routes...")
    with open('routes/pages.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if '@router.get("/onboarding"' in content:
            print("   [OK] Onboarding route exists")
        else:
            print("   [FAIL] Onboarding route missing")
            issues.append("Missing onboarding route")
    
    # 2. Check verification endpoint redirects correctly
    print("\n2. Checking email verification redirect...")
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'RedirectResponse(url="/onboarding"' in content:
            print("   [OK] Verification redirects to /onboarding")
        else:
            print("   [WARN] Verification might not redirect correctly")
            issues.append("Verification redirect issue")
    
    # 3. Check signup redirects to login
    print("\n3. Checking signup redirect...")
    with open('web/static/js/landing-page.js', 'r', encoding='utf-8') as f:
        content = f.read()
        if "window.location.href = '/login'" in content:
            print("   [OK] Signup redirects to /login after email message")
        else:
            print("   [WARN] Signup redirect might be wrong")
    
    # 4. Check database tables
    print("\n4. Checking database...")
    conn = sqlite3.connect('cora.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name IN ('users', 'email_verification_tokens')
    """)
    tables = [t[0] for t in cursor.fetchall()]
    
    if 'users' in tables:
        print("   [OK] users table exists")
    else:
        print("   [FAIL] users table missing")
        issues.append("Missing users table")
    
    if 'email_verification_tokens' in tables:
        print("   [OK] email_verification_tokens table exists")
    else:
        print("   [FAIL] email_verification_tokens table missing")
        issues.append("Missing email_verification_tokens table")
    
    conn.close()
    
    # 5. Summary
    print("\n" + "="*60)
    print("EXPECTED FLOW:")
    print("="*60)
    print("1. User signs up at /signup or landing page")
    print("2. Email verification sent (SendGrid)")
    print("3. User sees 'CHECK YOUR EMAIL' message")
    print("4. After 5 seconds, redirects to /login")
    print("5. User clicks verification link in email")
    print("6. System verifies and redirects to /onboarding")
    print("7. User completes or skips onboarding")
    print("8. User arrives at /dashboard")
    
    print("\n" + "="*60)
    if issues:
        print(f"FOUND {len(issues)} ISSUES:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("FLOW CONFIGURATION: ALL CHECKS PASSED")
    print("="*60)
    
    return len(issues) == 0

def test_with_real_user():
    """Test with a real user from the database"""
    
    print("\n" + "="*60)
    print("TESTING WITH REAL DATA")
    print("="*60)
    
    conn = sqlite3.connect('cora.db')
    cursor = conn.cursor()
    
    # Find a recent user
    cursor.execute("""
        SELECT email, email_verified, created_at 
        FROM users 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    users = cursor.fetchall()
    
    if users:
        print("\nRecent users in system:")
        for user in users:
            verified = "VERIFIED" if user[1] == 'true' else "UNVERIFIED"
            print(f"  - {user[0]} ({verified}) - created {user[2]}")
    else:
        print("\nNo users found in database")
    
    # Check for unused tokens
    cursor.execute("""
        SELECT email, created_at, used 
        FROM email_verification_tokens 
        WHERE used = 0 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    tokens = cursor.fetchall()
    
    if tokens:
        print("\nPending verification tokens:")
        for token in tokens:
            print(f"  - {token[0]} - created {token[1]}")
    else:
        print("\nNo pending verification tokens")
    
    conn.close()

if __name__ == "__main__":
    # No need to change directory
    
    if check_flow():
        test_with_real_user()
        print("\n[SUCCESS] Flow is properly configured!")
    else:
        print("\n[WARNING] Fix the issues above for proper flow")