#!/usr/bin/env python
"""Verify manual signup worked correctly"""
import sqlite3
from datetime import datetime

def verify_signup(email):
    """Check if a signup was successful"""
    conn = sqlite3.connect('cora.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            id, 
            email, 
            is_active, 
            email_verified,
            created_at
        FROM users 
        WHERE email = ?
    """, (email,))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        print(f"\n[SUCCESS] Account found for {email}!")
        print(f"  User ID: {user[0]}")
        print(f"  Email: {user[1]}")
        print(f"  Active: {user[2]}")
        print(f"  Verified: {user[3]}")
        print(f"  Created: {user[4]}")
        
        if user[2] == 'true' and user[3] == 'true':
            print("  Status: READY TO LOGIN ✓")
        elif user[2] == 'false' or user[3] == 'false':
            print("  Status: Needs verification (check email)")
        
        return True
    else:
        print(f"\n[NOT FOUND] No account for {email}")
        print("  Please complete the signup process")
        return False

def main():
    print("=" * 60)
    print("MANUAL SIGNUP VERIFICATION")
    print("=" * 60)
    print("\nChecking for manually created accounts...")
    
    emails_to_check = [
        'tyler_partridge@hotmail.com',
        'cpartridge00@gmail.com'
    ]
    
    found_count = 0
    for email in emails_to_check:
        if verify_signup(email):
            found_count += 1
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"  Accounts found: {found_count}/{len(emails_to_check)}")
    
    if found_count == len(emails_to_check):
        print("\n[COMPLETE] All manual signups successful! 🎉")
        print("\nNext steps:")
        print("1. Try logging in at http://localhost:8000/login")
        print("2. Access the dashboard")
        print("3. Test CORA's features")
    elif found_count > 0:
        print("\n[PARTIAL] Some accounts created")
        print("Complete signup for remaining accounts")
    else:
        print("\n[WAITING] No accounts created yet")
        print("\nTo sign up manually:")
        print("1. Go to http://localhost:8000/signup")
        print("2. Fill in the form:")
        print("   - Name: Your full name")
        print("   - Email: tyler_partridge@hotmail.com or cpartridge00@gmail.com")
        print("   - Business: Your business name")
        print("   - Password: Must have uppercase + number + special char")
        print("3. Click 'START SAVING MONEY'")
        print("4. Run this script again to verify")

if __name__ == "__main__":
    main()