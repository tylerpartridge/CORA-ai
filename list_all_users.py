#!/usr/bin/env python
"""List all users in the CORA database"""
import sqlite3
from datetime import datetime

conn = sqlite3.connect('cora.db')
cursor = conn.cursor()

# Get all users with key details
cursor.execute("""
    SELECT 
        id, 
        email, 
        is_active, 
        email_verified,
        created_at
    FROM users 
    ORDER BY id DESC
""")

users = cursor.fetchall()

print("=" * 80)
print("CORA USER ACCOUNTS")
print("=" * 80)
print(f"Total Users: {len(users)}")
print()

# Group users by type
real_users = []
test_users = []
demo_users = []

for user in users:
    email = user[1].lower()
    if 'test' in email or 'test_' in email:
        test_users.append(user)
    elif 'demo' in email:
        demo_users.append(user)
    else:
        real_users.append(user)

# Display real users
if real_users:
    print("REAL USER ACCOUNTS:")
    print("-" * 40)
    for user in real_users:
        user_id, email, is_active, email_verified, created_at = user
        status = "Active" if is_active == "true" else "Inactive"
        verified = "Verified" if email_verified == "true" else "Unverified"
        print(f"  ID: {user_id:3} | {email:40} | {status:8} | {verified:10}")
        if created_at:
            print(f"         Created: {created_at}")
    print()

# Display demo users
if demo_users:
    print("DEMO ACCOUNTS:")
    print("-" * 40)
    for user in demo_users:
        user_id, email, is_active, email_verified, created_at = user
        status = "Active" if is_active == "true" else "Inactive"
        print(f"  ID: {user_id:3} | {email:40} | {status}")
    print()

# Display test users count
if test_users:
    print(f"TEST ACCOUNTS: {len(test_users)} accounts")
    print("-" * 40)
    print("  (Created during development and testing)")
    # Show first few test accounts
    for user in test_users[:3]:
        user_id, email, is_active, email_verified, created_at = user
        print(f"  ID: {user_id:3} | {email}")
    if len(test_users) > 3:
        print(f"  ... and {len(test_users) - 3} more test accounts")
    print()

# Summary
print("=" * 80)
print("SUMMARY:")
print(f"  Real Users: {len(real_users)}")
print(f"  Demo Accounts: {len(demo_users)}")
print(f"  Test Accounts: {len(test_users)}")
print(f"  Total: {len(users)}")
print("=" * 80)

# Highlight Christina
print()
print("CHRISTINA'S ACCOUNT:")
cursor.execute("""
    SELECT id, email, is_active, email_verified 
    FROM users 
    WHERE email = 'cpartridge00@gmail.com'
""")
christina = cursor.fetchone()
if christina:
    print(f"  [FOUND] ID: {christina[0]} | {christina[1]}")
    print(f"  Status: Active={christina[2]}, Verified={christina[3]}")
else:
    print("  [NOT FOUND]")

conn.close()