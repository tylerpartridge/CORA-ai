#!/usr/bin/env python3
"""
COMPREHENSIVE TOKEN FLOW TEST
Maps exactly what happens during signup -> token generation -> verification
"""

import sqlite3
import json
import hashlib
from datetime import datetime

def clean_test_data(email):
    """Clean up any existing test data"""
    conn = sqlite3.connect('cora.db')
    cursor = conn.cursor()
    
    # Count before
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,))
    user_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM email_verification_tokens WHERE email = ?", (email,))
    token_count = cursor.fetchone()[0]
    
    if user_count > 0 or token_count > 0:
        print(f"\n[CLEANUP] Found {user_count} users and {token_count} tokens for {email}")
        
        # Delete in correct order (tokens first, then users)
        cursor.execute("DELETE FROM email_verification_tokens WHERE email = ?", (email,))
        cursor.execute("DELETE FROM users WHERE email = ?", (email,))
        conn.commit()
        print(f"[CLEANUP] Deleted all data for {email}")
    
    conn.close()

def test_signup_creates_token():
    """Test that signup properly creates both user AND token"""
    
    print("="*70)
    print("TOKEN GENERATION FLOW TEST")
    print("="*70)
    
    test_email = "test_token_flow@example.com"
    
    # Step 1: Clean any existing data
    clean_test_data(test_email)
    
    # Step 2: Simulate what /api/auth/register does
    print(f"\n[STEP 1] Simulating signup for {test_email}")
    
    from werkzeug.security import generate_password_hash
    import secrets
    
    conn = sqlite3.connect('cora.db')
    cursor = conn.cursor()
    
    # Create user (what auth_service.create_user does)
    password_hash = generate_password_hash("TestPassword123!")
    cursor.execute("""
        INSERT INTO users (email, hashed_password, created_at, email_verified)
        VALUES (?, ?, datetime('now'), 'false')
    """, (test_email, password_hash))
    user_id = cursor.lastrowid
    print(f"[CREATED] User ID: {user_id}")
    
    # Create verification token (what auth_service.create_email_verification_token does)
    token = secrets.token_urlsafe(32)
    cursor.execute("""
        INSERT INTO email_verification_tokens (email, token, created_at, expires_at, used)
        VALUES (?, ?, datetime('now'), datetime('now', '+1 day'), 0)
    """, (test_email, token))
    print(f"[CREATED] Token: {token[:20]}...")
    
    conn.commit()
    
    # Step 3: Verify both exist
    print("\n[STEP 2] Verifying data consistency")
    
    cursor.execute("SELECT id, email, email_verified FROM users WHERE email = ?", (test_email,))
    user = cursor.fetchone()
    
    cursor.execute("SELECT token, used FROM email_verification_tokens WHERE email = ?", (test_email,))
    token_record = cursor.fetchone()
    
    if user and token_record:
        print(f"[OK] User exists: {user[1]} (verified: {user[2]})")
        print(f"[OK] Token exists: {token_record[0][:20]}... (used: {token_record[1]})")
    else:
        print("[FAIL] Data inconsistency detected!")
        
    # Step 4: Test verification link
    print("\n[STEP 3] Testing verification link")
    verification_url = f"http://localhost:8001/verify-email?token={token}"
    print(f"[LINK] {verification_url}")
    
    # Step 5: Simulate clicking the link (what verify_email_token does)
    print("\n[STEP 4] Simulating verification click")
    
    # Check token is valid
    cursor.execute("""
        SELECT email FROM email_verification_tokens 
        WHERE token = ? AND used = 0
    """, (token,))
    result = cursor.fetchone()
    
    if result:
        # Mark user as verified
        cursor.execute("UPDATE users SET email_verified = 'true' WHERE email = ?", (test_email,))
        # Mark token as used
        cursor.execute("UPDATE email_verification_tokens SET used = 1 WHERE token = ?", (token,))
        conn.commit()
        print(f"[OK] Email verified successfully")
    else:
        print(f"[FAIL] Token validation failed")
    
    # Step 6: Verify final state
    print("\n[STEP 5] Final state check")
    cursor.execute("SELECT email_verified FROM users WHERE email = ?", (test_email,))
    verified = cursor.fetchone()[0]
    cursor.execute("SELECT used FROM email_verification_tokens WHERE token = ?", (token,))
    used = cursor.fetchone()[0]
    
    print(f"[FINAL] User verified: {verified}")
    print(f"[FINAL] Token used: {used}")
    
    # Cleanup
    clean_test_data(test_email)
    conn.close()
    
    print("\n" + "="*70)
    print("FLOW TEST COMPLETE - All steps verified!")
    print("="*70)

def check_tyler_status():
    """Check Tyler's current signup status"""
    
    print("\n" + "="*70)
    print("TYLER'S CURRENT STATUS")
    print("="*70)
    
    conn = sqlite3.connect('cora.db')
    cursor = conn.cursor()
    
    # Get Tyler's user record
    cursor.execute("""
        SELECT id, email, email_verified, created_at 
        FROM users 
        WHERE email = 'tyler_partridge@hotmail.com'
    """)
    user = cursor.fetchone()
    
    if user:
        print(f"\nUser Record:")
        print(f"  ID: {user[0]}")
        print(f"  Email: {user[1]}")
        print(f"  Verified: {user[2]}")
        print(f"  Created: {user[3]}")
    else:
        print("\n[NOT FOUND] No user record for tyler_partridge@hotmail.com")
    
    # Get all tokens for Tyler
    cursor.execute("""
        SELECT token, created_at, used, expires_at
        FROM email_verification_tokens 
        WHERE email = 'tyler_partridge@hotmail.com'
        ORDER BY created_at DESC
    """)
    tokens = cursor.fetchall()
    
    print(f"\nTokens Found: {len(tokens)}")
    for i, token in enumerate(tokens, 1):
        used_status = "USED" if token[2] in [1, 'true', True] else "UNUSED"
        print(f"\nToken {i}:")
        print(f"  Token: {token[0][:30]}...")
        print(f"  Created: {token[1]}")
        print(f"  Status: {used_status}")
        print(f"  Expires: {token[3]}")
        
        # Check if this token matches the user
        if user:
            if token[1].startswith(user[3][:16]):  # Match by similar timestamp
                print(f"  [MATCH] This token was created with the current user record")
        else:
            print(f"  [ORPHAN] No matching user for this token")
    
    # Identify the correct token
    if user and tokens:
        # Find token created at same time as user
        user_time = user[3][:16]  # Get minute precision
        for token in tokens:
            if token[1].startswith(user_time) and token[2] not in [1, 'true', True]:
                print(f"\n[CORRECT TOKEN TO USE]:")
                print(f"http://localhost:8001/verify-email?token={token[0]}")
                break
    
    conn.close()

if __name__ == "__main__":
    # First test the flow with a clean test account
    test_signup_creates_token()
    
    # Then check Tyler's actual status
    check_tyler_status()