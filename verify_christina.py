#!/usr/bin/env python
"""Verify Christina's account"""
import sqlite3

conn = sqlite3.connect('cora.db')
cursor = conn.cursor()

# Update Christina's account to be active and verified
cursor.execute("""
    UPDATE users 
    SET is_active = 'true', 
        email_verified = 'true' 
    WHERE email = 'cpartridge00@gmail.com'
""")

affected = cursor.rowcount
conn.commit()

if affected > 0:
    print(f"Christina's account has been verified!")
    
    # Show the account details
    cursor.execute("""
        SELECT id, email, is_active, email_verified 
        FROM users 
        WHERE email = 'cpartridge00@gmail.com'
    """)
    
    row = cursor.fetchone()
    if row:
        print(f"\nAccount details:")
        print(f"ID: {row[0]}")
        print(f"Email: {row[1]}")
        print(f"Active: {row[2]}")
        print(f"Verified: {row[3]}")
else:
    print("Christina's account not found. She may need to sign up first.")

conn.close()