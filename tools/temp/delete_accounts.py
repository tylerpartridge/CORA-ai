#!/usr/bin/env python
"""Delete Tyler and Christina's accounts for fresh manual signup"""
import sqlite3

def delete_accounts():
    conn = sqlite3.connect('cora.db')
    cursor = conn.cursor()
    
    accounts_to_delete = [
        'tyler_partridge@hotmail.com',
        'cpartridge00@gmail.com'
    ]
    
    print("Deleting Real User Accounts")
    print("=" * 60)
    
    for email in accounts_to_delete:
        # First check if account exists
        cursor.execute("SELECT id, email FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if user:
            print(f"\nFound: {user[1]} (ID: {user[0]})")
            
            # Delete the user
            cursor.execute("DELETE FROM users WHERE email = ?", (email,))
            deleted = cursor.rowcount
            
            if deleted > 0:
                print(f"  [DELETED] Successfully removed {email}")
            else:
                print(f"  [ERROR] Could not delete {email}")
        else:
            print(f"\n[NOT FOUND] {email} - Already deleted or doesn't exist")
    
    # Commit the changes
    conn.commit()
    
    # Verify deletion
    print("\n" + "=" * 60)
    print("Verification:")
    for email in accounts_to_delete:
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            print(f"  [WARNING] {email} still exists!")
        else:
            print(f"  [CONFIRMED] {email} deleted successfully")
    
    # Show remaining users count
    cursor.execute("SELECT COUNT(*) FROM users WHERE email NOT LIKE '%test%'")
    real_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    print("\n" + "=" * 60)
    print("Database Status:")
    print(f"  Real users remaining: {real_users}")
    print(f"  Total users: {total_users}")
    print("\n[READY] You can now sign up manually with these emails!")
    print("  - tyler_partridge@hotmail.com")
    print("  - cpartridge00@gmail.com")
    
    conn.close()

if __name__ == "__main__":
    response = input("Delete Tyler and Christina's accounts? (yes/no): ")
    if response.lower() == 'yes':
        delete_accounts()
    else:
        print("Cancelled - no accounts deleted")