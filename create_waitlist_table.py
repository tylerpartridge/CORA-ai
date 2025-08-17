#!/usr/bin/env python
"""Create waitlist table for email capture"""
import sqlite3

conn = sqlite3.connect('cora.db')
cursor = conn.cursor()

# Create waitlist table
cursor.execute("""
CREATE TABLE IF NOT EXISTS waitlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    source TEXT DEFAULT 'hero_section',
    converted_to_user BOOLEAN DEFAULT 0,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Add index for faster lookups
cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_waitlist_email 
ON waitlist(email)
""")

conn.commit()
print("SUCCESS: Waitlist table created successfully!")

# Check if it was created
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='waitlist'")
if cursor.fetchone():
    print("SUCCESS: Verified: waitlist table exists")
    
    # Show table structure
    cursor.execute("PRAGMA table_info(waitlist)")
    columns = cursor.fetchall()
    print("\nTable structure:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

conn.close()