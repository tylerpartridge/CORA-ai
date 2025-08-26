#!/usr/bin/env python
"""Fix Christina's account to allow login"""
import sqlite3

conn = sqlite3.connect('cora.db')
cursor = conn.cursor()

# Fix the account
cursor.execute("""
    UPDATE users 
    SET email_verified='true', is_active='true' 
    WHERE email='cpartridge00@gmail.com'
""")
conn.commit()

# Verify it worked
cursor.execute("""
    SELECT email, is_active, email_verified 
    FROM users 
    WHERE email='cpartridge00@gmail.com'
""")
user = cursor.fetchone()

if user:
    print(f"SUCCESS! Account fixed:")
    print(f"  Email: {user[0]}")
    print(f"  Active: {user[1]}")
    print(f"  Verified: {user[2]}")
    print(f"\nYou can now login at /login with:")
    print(f"  Email: cpartridge00@gmail.com")
    print(f"  Password: [whatever you set during signup]")
else:
    print("Account not found - you may need to sign up first")

conn.close()