#!/usr/bin/env python
"""Check user in database"""
import sqlite3

conn = sqlite3.connect('cora.db')
cursor = conn.cursor()

# Get recent test users
cursor.execute("""
    SELECT id, email, is_active, email_verified 
    FROM users 
    WHERE email LIKE 'test_%' 
    ORDER BY id DESC 
    LIMIT 5
""")

print("Recent test users:")
print("ID | Email | is_active | email_verified")
print("-" * 50)
for row in cursor.fetchall():
    print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")

conn.close()