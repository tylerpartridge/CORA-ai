#!/usr/bin/env python3
"""Check database schema"""

import sqlite3

def check_database():
    """Check what tables exist in the database"""
    try:
        # Try multiple database files
        db_files = ['database.db', 'cora.db', 'data/cora.db']
        
        for db_file in db_files:
            print(f"\n=== Checking {db_file} ===")
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Get all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                print(f"Available tables in {db_file}:")
                for table in tables:
                    print(f"  - {table[0]}")
                
                # Check if users table has email verification columns
                if ('users',) in tables:
                    cursor.execute("PRAGMA table_info(users);")
                    columns = cursor.fetchall()
                    print(f"\nUsers table columns in {db_file}:")
                    for col in columns:
                        print(f"  - {col[1]} ({col[2]})")
                    
                    # Check if there are any users
                    cursor.execute("SELECT COUNT(*) FROM users;")
                    user_count = cursor.fetchone()[0]
                    print(f"Total users: {user_count}")
                    
                    if user_count > 0:
                        cursor.execute("SELECT email, email_verified FROM users LIMIT 5;")
                        users = cursor.fetchall()
                        print("Sample users:")
                        for user in users:
                            print(f"  - {user[0]} (verified: {user[1] if len(user) > 1 else 'NO COLUMN'})")
                
                # Check for email verification tokens table
                if ('email_verification_tokens',) in tables:
                    cursor.execute("SELECT COUNT(*) FROM email_verification_tokens;")
                    token_count = cursor.fetchone()[0]
                    print(f"Email verification tokens: {token_count}")
                    
                    if token_count > 0:
                        cursor.execute("SELECT email, used FROM email_verification_tokens LIMIT 3;")
                        tokens = cursor.fetchall()
                        print("Sample tokens:")
                        for token in tokens:
                            print(f"  - {token[0]} (used: {token[1]})")
                
                conn.close()
                print(f"[SUCCESS] Successfully checked {db_file}")
                
            except Exception as e:
                print(f"[ERROR] Error with {db_file}: {e}")
        
    except Exception as e:
        print(f"General Error: {e}")

if __name__ == "__main__":
    check_database()