#!/usr/bin/env python
"""Fix test users to be active and verified"""
import sqlite3

conn = sqlite3.connect('cora.db')
cursor = conn.cursor()

# Update all test users to be active and verified
cursor.execute("""
    UPDATE users 
    SET is_active = 'true', 
        email_verified = 'true' 
    WHERE email LIKE 'test_%' OR email = 'cpartridge00@gmail.com'
""")

affected = cursor.rowcount
conn.commit()

print(f"Updated {affected} test users to be active and verified")

# Show the updated users
cursor.execute("""
    SELECT id, email, is_active, email_verified 
    FROM users 
    WHERE email LIKE 'test_%' OR email = 'cpartridge00@gmail.com'
    ORDER BY id DESC 
    LIMIT 10
""")

print("\nUpdated users:")
print("ID | Email | is_active | email_verified")
print("-" * 60)
for row in cursor.fetchall():
    print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")

conn.close()