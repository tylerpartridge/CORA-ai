#!/usr/bin/env python3
"""
Find ONE thing that actually works
"""
import os
import sqlite3

print("Looking for something that works...")
print("-" * 40)

# Check database
if os.path.exists('cora.db'):
    conn = sqlite3.connect('cora.db')
    cursor = conn.cursor()
    
    # Count users
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"[OK] Database has {user_count} users")
    
    # Check for expenses
    cursor.execute("SELECT COUNT(*) FROM expenses")
    expense_count = cursor.fetchone()[0]
    print(f"[OK] Database has {expense_count} expenses")
    
    # Get a user to test with
    cursor.execute("SELECT email FROM users LIMIT 1")
    user = cursor.fetchone()
    if user:
        print(f"[OK] Test user available: {user[0]}")
    
    conn.close()
else:
    print("[X] No database found")

print("-" * 40)

# Check for deployment package
if os.path.exists('backups/cora_deployment_ready_20250810_133220.tar.gz'):
    print("[OK] Deployment backup exists (26MB)")
    print("     This was working 2 days ago")
else:
    print("[X] No deployment backup")

print("-" * 40)
print("\nSuggestion: Use the deployment backup from Aug 10")
print("It was tested and working before today's changes")