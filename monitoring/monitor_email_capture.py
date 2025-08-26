#!/usr/bin/env python
"""Monitor email capture from hero section"""
import sqlite3
import time
from datetime import datetime

def check_email_capture_tables():
    """Check all possible tables where email might be stored"""
    conn = sqlite3.connect('cora.db')
    cursor = conn.cursor()
    
    print("=" * 60)
    print("MONITORING EMAIL CAPTURE")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Looking for: cpartridge00@gmail.com")
    print()
    
    # Check if there's a waitlist or email_captures table
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND (
            name LIKE '%email%' OR 
            name LIKE '%waitlist%' OR 
            name LIKE '%capture%' OR
            name LIKE '%lead%'
        )
    """)
    
    email_tables = cursor.fetchall()
    print("Email-related tables found:")
    for table in email_tables:
        print(f"  - {table[0]}")
    print()
    
    # Check waitlist table specifically
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='waitlist'")
    if cursor.fetchone():
        cursor.execute("""
            SELECT id, email, created_at 
            FROM waitlist 
            WHERE email = 'cpartridge00@gmail.com'
            ORDER BY id DESC
        """)
        waitlist_entry = cursor.fetchone()
        if waitlist_entry:
            print("[FOUND] Email in waitlist table:")
            print(f"  ID: {waitlist_entry[0]}")
            print(f"  Email: {waitlist_entry[1]}")
            print(f"  Created: {waitlist_entry[2]}")
        else:
            print("[NOT FOUND] Email not in waitlist table")
    else:
        print("[INFO] No waitlist table exists")
    
    print()
    
    # Check users table (in case it goes directly there)
    cursor.execute("""
        SELECT id, email, created_at 
        FROM users 
        WHERE email = 'cpartridge00@gmail.com'
    """)
    user = cursor.fetchone()
    if user:
        print("[FOUND] Email in users table:")
        print(f"  ID: {user[0]}")
        print(f"  Email: {user[1]}")
        print(f"  Created: {user[2]}")
    else:
        print("[NOT FOUND] Email not in users table")
    
    conn.close()
    print("\n" + "=" * 60)

def monitor_continuously():
    """Monitor for 30 seconds"""
    print("Monitoring for email capture (30 seconds)...")
    print("Submit the email form now!\n")
    
    for i in range(6):  # Check every 5 seconds for 30 seconds
        check_email_capture_tables()
        if i < 5:
            print(f"Checking again in 5 seconds... ({25 - i*5} seconds remaining)")
            time.sleep(5)
    
    print("\nMonitoring complete!")

if __name__ == "__main__":
    monitor_continuously()