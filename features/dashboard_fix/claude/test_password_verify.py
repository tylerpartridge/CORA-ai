#!/usr/bin/env python3
"""Test password verification"""

import sys
sys.path.insert(0, '/mnt/host/c/CORA')

from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

# Get the user's hashed password
conn = sqlite3.connect('cora.db')
cursor = conn.cursor()

cursor.execute("SELECT email, hashed_password FROM users WHERE email='dashtest@example.com'")
result = cursor.fetchone()

if result:
    email, stored_hash = result
    print(f"User: {email}")
    print(f"Stored hash: {stored_hash[:50]}...")
    
    # Test password verification
    test_password = "Password123!"
    
    # Check if password matches
    match = check_password_hash(stored_hash, test_password)
    print(f"\nPassword '{test_password}' matches: {match}")
    
    if not match:
        # Create a new hash and compare
        new_hash = generate_password_hash(test_password)
        print(f"\nNew hash would be: {new_hash[:50]}...")
        
        # Update the password directly
        print("\nUpdating password hash...")
        cursor.execute("UPDATE users SET hashed_password=? WHERE email=?", (new_hash, email))
        conn.commit()
        print("[OK] Password updated")
else:
    print("User not found")

conn.close()