#!/usr/bin/env python
"""Trace signup form submission"""
import sqlite3
import time

def check_signup():
    conn = sqlite3.connect('cora.db')
    cursor = conn.cursor()
    
    # Check for Christina's account
    cursor.execute("""
        SELECT id, email, is_active, email_verified, created_at 
        FROM users 
        WHERE email = 'cpartridge00@gmail.com'
        ORDER BY id DESC
        LIMIT 1
    """)
    
    user = cursor.fetchone()
    if user:
        print(f"[FOUND] Account created!")
        print(f"  ID: {user[0]}")
        print(f"  Email: {user[1]}")
        print(f"  Active: {user[2]}")
        print(f"  Verified: {user[3]}")
        print(f"  Created: {user[4]}")
        return True
    else:
        print("[WAITING] No account yet...")
        return False
    
    conn.close()

print("Monitoring signup for cpartridge00@gmail.com")
print("=" * 60)
print("Please submit the signup form now...")
print()

# Check every 2 seconds for 30 seconds
for i in range(15):
    if check_signup():
        print("\n[SUCCESS] Signup captured and stored in database!")
        break
    time.sleep(2)
else:
    print("\n[TIMEOUT] No signup detected after 30 seconds")