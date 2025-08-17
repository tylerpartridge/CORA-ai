#!/usr/bin/env python3
"""Generate a verification link for Tyler to simulate email click"""

import sqlite3
import secrets
from datetime import datetime

def create_verification_link():
    """Create a verification token and link for Tyler"""
    
    email = "tyler_partridge@hotmail.com"
    
    # Connect to database
    conn = sqlite3.connect('cora.db')
    cursor = conn.cursor()
    
    # Check if Tyler exists
    cursor.execute("SELECT id, email_verified FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if not user:
        print(f"[ERROR] User {email} not found in database")
        return None
    
    if user[1] == 'true':
        print(f"[NOTE] User {email} is already verified")
    
    # Check for existing unused token
    cursor.execute("""
        SELECT token FROM email_verification_tokens 
        WHERE email = ? AND used = 0 
        ORDER BY created_at DESC LIMIT 1
    """, (email,))
    
    existing = cursor.fetchone()
    
    if existing:
        token = existing[0]
        print(f"[REUSING] Existing token found")
    else:
        # Create new verification token
        token = secrets.token_urlsafe(32)
        cursor.execute("""
            INSERT INTO email_verification_tokens (email, token, created_at, expires_at, used)
            VALUES (?, ?, datetime('now'), datetime('now', '+1 day'), 0)
        """, (email, token))
        conn.commit()
        print(f"[CREATED] New verification token")
    
    conn.close()
    
    # Generate the verification link
    verification_url = f"http://localhost:8001/verify-email?token={token}"
    
    print("\n" + "="*60)
    print("VERIFICATION LINK FOR TYLER")
    print("="*60)
    print("\nClick this link to simulate email verification:")
    print(f"\n{verification_url}\n")
    print("This will:")
    print("1. Mark tyler_partridge@hotmail.com as verified")
    print("2. Redirect to /onboarding")
    print("3. Onboarding will ask for name and business details")
    print("="*60)
    
    return verification_url

if __name__ == "__main__":
    create_verification_link()