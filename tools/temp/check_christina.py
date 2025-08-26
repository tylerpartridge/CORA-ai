#!/usr/bin/env python
"""Check if Christina's account exists in database"""
import sqlite3

conn = sqlite3.connect('cora.db')
cursor = conn.cursor()

print("Checking for Christina's account...")
print("=" * 60)

# Check multiple possible email variations
emails_to_check = [
    'cpartridge00@gmail.com',
    'christina@gmail.com', 
    'christina.partridge@gmail.com'
]

for email in emails_to_check:
    cursor.execute("""
        SELECT id, email, is_active, email_verified, created_at 
        FROM users 
        WHERE email = ? OR email LIKE ?
    """, (email, f'%{email.split("@")[0]}%'))
    
    results = cursor.fetchall()
    if results:
        print(f"\n✓ Found account(s) matching '{email}':")
        for row in results:
            print(f"  ID: {row[0]}")
            print(f"  Email: {row[1]}")
            print(f"  Active: {row[2]}")
            print(f"  Verified: {row[3]}")
            print(f"  Created: {row[4]}")

# Also check for any similar names
cursor.execute("""
    SELECT id, email, is_active, email_verified 
    FROM users 
    WHERE email LIKE '%christina%' OR email LIKE '%partridge%'
""")

similar = cursor.fetchall()
if similar:
    print("\n[Similar accounts found]:")
    for row in similar:
        print(f"  {row[1]} (Active: {row[2]}, Verified: {row[3]})")

# Check total user count
cursor.execute("SELECT COUNT(*) FROM users")
total = cursor.fetchone()[0]
print(f"\nTotal users in database: {total}")

# Check for any signup attempts (if we have a signup_attempts table)
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name='signup_attempts'
""")
if cursor.fetchone():
    cursor.execute("""
        SELECT * FROM signup_attempts 
        WHERE email LIKE '%christina%' OR email LIKE '%cpartridge%'
    """)
    attempts = cursor.fetchall()
    if attempts:
        print(f"\nSignup attempts found: {len(attempts)}")

conn.close()

print("\n" + "=" * 60)
print("Result: Christina's account (cpartridge00@gmail.com) does NOT exist yet.")
print("She needs to sign up through the signup form.")