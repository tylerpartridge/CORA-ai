#!/usr/bin/env python3
"""
Database Connectivity Test
For Claude to verify models can connect to existing data
"""

def test_database_connectivity():
    print("[TEST] TESTING DATABASE CONNECTIVITY")
    print("=" * 50)
    
    try:
        # Add parent directory to path
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        # Test database connection
        from models.base import SessionLocal
        from models.user import User
        
        db = SessionLocal()
        
        # Test reading existing users
        users = db.query(User).all()
        print(f"[OK] Found {len(users)} users in database")
        
        if users:
            print(f"   Sample user: {users[0].email}")
        
        # Test reading existing expenses
        from models.expense import Expense
        expenses = db.query(Expense).all()
        print(f"[OK] Found {len(expenses)} expenses in database")
        
        if expenses:
            print(f"   Sample expense: {expenses[0].description} - ${expenses[0].amount_cents/100}")
        
        # Test reading expense categories
        from models.expense_category import ExpenseCategory
        categories = db.query(ExpenseCategory).all()
        print(f"[OK] Found {len(categories)} expense categories in database")
        
        # Test reading customers
        from models.customer import Customer
        customers = db.query(Customer).all()
        print(f"[OK] Found {len(customers)} customers in database")
        
        # Test reading subscriptions
        from models.subscription import Subscription
        subscriptions = db.query(Subscription).all()
        print(f"[OK] Found {len(subscriptions)} subscriptions in database")
        
        db.close()
        
        print("=" * 50)
        print("[SUCCESS] DATABASE CONNECTIVITY TEST PASSED!")
        print("   All models can read from existing database")
        print("   Ready for route integration")
        return True
        
    except Exception as e:
        print(f"[ERROR] DATABASE CONNECTIVITY TEST FAILED: {e}")
        print("   Check database path in models/base.py")
        return False

if __name__ == "__main__":
    test_database_connectivity() 