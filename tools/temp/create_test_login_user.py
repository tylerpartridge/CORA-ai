#!/usr/bin/env python
"""Create a test user for login testing"""

import sqlite3
import bcrypt
from datetime import datetime

# Database path
db_path = "cora.db"

# Test user credentials
email = "logintest@coratest.com"
password = "TestLogin123!"

# Hash the password
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if user already exists
cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
existing = cursor.fetchone()

if existing:
    # Update existing user's password
    cursor.execute("""
        UPDATE users 
        SET hashed_password = ?, 
            is_active = 1, 
            email_verified = 1,
            email_verified_at = ?
        WHERE email = ?
    """, (hashed.decode('utf-8'), datetime.now().isoformat(), email))
    print(f"Updated existing user: {email}")
else:
    # Create new user
    cursor.execute("""
        INSERT INTO users (email, hashed_password, created_at, is_active, is_admin, email_verified, email_verified_at)
        VALUES (?, ?, ?, 1, 0, 1, ?)
    """, (email, hashed.decode('utf-8'), datetime.now().isoformat(), datetime.now().isoformat()))
    print(f"Created new user: {email}")

conn.commit()
conn.close()

print("\n=== TEST USER CREATED ===")
print(f"Email: {email}")
print(f"Password: {password}")
print("\nYou can now test login at: http://localhost:8001/login")