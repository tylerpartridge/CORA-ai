#!/usr/bin/env python
"""Check existing users in the database"""

import sqlite3
import os

# Find the database file
db_paths = [
    "/mnt/host/c/CORA/cora.db",
    "/mnt/host/c/CORA/data/cora.db",
    "cora.db"
]

db_path = None
for path in db_paths:
    if os.path.exists(path):
        db_path = path
        print(f"Found database at: {path}")
        break

if not db_path:
    print("No database found!")
    exit(1)

# Connect and check users
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# First check the schema
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
column_names = [col[1] for col in columns]
print(f"User table columns: {column_names}")

# Get all users
try:
    cursor.execute("""
        SELECT id, email, created_at 
        FROM users 
        ORDER BY created_at DESC
        LIMIT 10
    """)
    users = cursor.fetchall()
except Exception as e:
    print(f"Error: {e}")
    users = []

print("\n=== EXISTING USER ACCOUNTS ===")
print("-" * 80)
for user in users:
    user_id, email, created_at = user
    
    print(f"Email: {email}")
    print(f"  ID: {user_id}")
    print(f"  Created: {created_at}")
    print("-" * 80)

print(f"\nTotal users found: {len(users)}")

# Note: We cannot retrieve passwords as they are hashed
print("\nNOTE: Passwords are hashed and cannot be retrieved.")
print("Common test passwords that might work:")
print("  - TestPassword123!")
print("  - Password123!")
print("  - password123")

conn.close()