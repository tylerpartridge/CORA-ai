#!/usr/bin/env python
"""Test email capture from hero section"""
import sqlite3
from datetime import datetime

def check_waitlist():
    conn = sqlite3.connect('cora.db')
    cursor = conn.cursor()
    
    print("Checking contractor_waitlist table...")
    print("=" * 60)
    
    # Get recent entries
    cursor.execute("""
        SELECT id, email, source, source_details, created_at 
        FROM contractor_waitlist 
        ORDER BY id DESC 
        LIMIT 5
    """)
    
    entries = cursor.fetchall()
    
    if entries:
        print(f"Found {len(entries)} recent waitlist entries:")
        for entry in entries:
            print(f"\nID: {entry[0]}")
            print(f"Email: {entry[1]}")
            print(f"Source: {entry[2]}")
            print(f"Details: {entry[3]}")
            print(f"Created: {entry[4]}")
    else:
        print("No waitlist entries found yet")
    
    conn.close()

if __name__ == "__main__":
    check_waitlist()