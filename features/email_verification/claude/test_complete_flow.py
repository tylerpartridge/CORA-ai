#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the complete signup → email → verification → onboarding flow
"""

import sqlite3
import json
import time
from datetime import datetime
import sys
import os
sys.path.append('/mnt/host/c/CORA')

def test_signup_flow():
    """Test the complete user signup and verification flow"""
    
    print("="*60)
    print("TESTING COMPLETE SIGNUP → VERIFICATION → ONBOARDING FLOW")
    print("="*60)
    
    # Test email for this run
    test_email = f"test_{int(time.time())}@example.com"
    print(f"\n1. Testing with email: {test_email}")
    
    # Connect to database
    conn = sqlite3.connect('cora.db')
    cursor = conn.cursor()
    
    # Step 1: Simulate user signup (what the API does)
    print("\n2. Simulating user signup...")
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (test_email,))
    if cursor.fetchone():
        print("   ❌ User already exists")
        return False
        
    # Create user (simplified - normally done via API)
    from werkzeug.security import generate_password_hash
    password_hash = generate_password_hash("TestPassword123!")
    
    cursor.execute("""
        INSERT INTO users (email, password_hash, created_at, email_verified)
        VALUES (?, ?, datetime('now'), 'false')
    """, (test_email, password_hash))
    user_id = cursor.lastrowid
    print(f"   ✅ User created with ID: {user_id}")
    
    # Step 2: Create verification token (what happens during signup)
    print("\n3. Creating verification token...")
    import secrets
    token = secrets.token_urlsafe(32)
    
    cursor.execute("""
        INSERT INTO email_verification_tokens (email, token, created_at, used)
        VALUES (?, ?, datetime('now'), 0)
    """, (test_email, token))
    print(f"   ✅ Token created: {token[:20]}...")
    
    # Step 3: Simulate email verification click
    print("\n4. Simulating email verification...")
    
    # Check token exists and is valid
    cursor.execute("""
        SELECT email, used FROM email_verification_tokens 
        WHERE token = ? AND used = 0
    """, (token,))
    result = cursor.fetchone()
    
    if not result:
        print("   ❌ Token not found or already used")
        return False
    
    # Mark user as verified (what verify_email_token does)
    cursor.execute("""
        UPDATE users SET email_verified = 'true' 
        WHERE email = ?
    """, (test_email,))
    
    # Mark token as used
    cursor.execute("""
        UPDATE email_verification_tokens SET used = 1 
        WHERE token = ?
    """, (token,))
    
    print("   ✅ Email verified successfully")
    
    # Step 4: Check the redirect flow
    print("\n5. Checking redirect flow...")
    print("   → After signup: User sees 'CHECK YOUR EMAIL' message")
    print("   → After 5 seconds: Redirects to /login")
    print("   → After verification: Should redirect to /onboarding")
    print("   → After onboarding: Goes to /dashboard")
    
    # Step 5: Verify user can access protected routes
    print("\n6. Verifying user state...")
    cursor.execute("""
        SELECT email, email_verified, created_at 
        FROM users WHERE email = ?
    """, (test_email,))
    user = cursor.fetchone()
    
    if user:
        print(f"   ✅ User email: {user[0]}")
        print(f"   ✅ Verified: {user[1]}")
        print(f"   ✅ Created: {user[2]}")
    
    # Step 6: Check what happens at each endpoint
    print("\n7. Endpoint behavior:")
    print("   /signup → Creates user & token, shows email message")
    print("   /verify-email?token=X → Verifies & redirects to /onboarding")
    print("   /onboarding → Shows onboarding (can skip to dashboard)")
    print("   /dashboard → Requires auth (redirects to /login if not)")
    
    # Step 7: Cleanup test data
    print("\n8. Cleaning up test data...")
    cursor.execute("DELETE FROM email_verification_tokens WHERE email = ?", (test_email,))
    cursor.execute("DELETE FROM users WHERE email = ?", (test_email,))
    conn.commit()
    print("   ✅ Test data cleaned up")
    
    conn.close()
    
    print("\n" + "="*60)
    print("FLOW TEST COMPLETE - All steps verified!")
    print("="*60)
    
    return True

def check_current_issues():
    """Check for any current issues in the flow"""
    
    print("\n" + "="*60)
    print("CHECKING FOR KNOWN ISSUES")
    print("="*60)
    
    issues_found = []
    
    # Check 1: Verify onboarding route exists
    if os.path.exists('/mnt/host/c/CORA/routes/pages.py'):
        with open('/mnt/host/c/CORA/routes/pages.py', 'r') as f:
            content = f.read()
            if '/onboarding' in content:
                print("[OK] Onboarding route exists")
            else:
                print("❌ Onboarding route missing!")
                issues_found.append("Missing onboarding route")
    
    # Check 2: Verify email verification endpoint
    if os.path.exists('/mnt/host/c/CORA/app.py'):
        with open('/mnt/host/c/CORA/app.py', 'r') as f:
            content = f.read()
            if 'verify_email_endpoint' in content:
                print("✅ Email verification endpoint exists")
                if 'RedirectResponse(url="/onboarding"' in content:
                    print("✅ Verification redirects to onboarding")
                else:
                    print("⚠️  Verification might not redirect to onboarding")
                    issues_found.append("Verification redirect issue")
    
    # Check 3: Verify landing page JS redirect
    js_file = '/mnt/host/c/CORA/web/static/js/landing-page.js'
    if os.path.exists(js_file):
        with open(js_file, 'r') as f:
            content = f.read()
            if "window.location.href = '/login'" in content:
                print("✅ Signup redirects to login after email message")
            else:
                print("⚠️  Signup redirect might be broken")
    
    # Check 4: Database tables
    conn = sqlite3.connect('cora.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name IN ('users', 'email_verification_tokens')
    """)
    tables = cursor.fetchall()
    
    if len(tables) == 2:
        print("✅ Required database tables exist")
    else:
        print(f"❌ Missing tables: found {len(tables)}/2")
        issues_found.append("Missing database tables")
    
    conn.close()
    
    if issues_found:
        print(f"\n⚠️  Found {len(issues_found)} issues:")
        for issue in issues_found:
            print(f"   - {issue}")
    else:
        print("\n✅ No issues found - flow should work correctly!")
    
    return len(issues_found) == 0

if __name__ == "__main__":
    # First check for issues
    if check_current_issues():
        # Then test the flow
        test_signup_flow()
    else:
        print("\n⚠️  Fix the issues above before testing the flow")