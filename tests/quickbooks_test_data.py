#!/usr/bin/env python3
"""
QuickBooks Integration Test Data
Creates test expenses for syncing to QuickBooks
"""

import json
from datetime import datetime, timedelta
from decimal import Decimal

# Test expenses that match QuickBooks categories
TEST_EXPENSES = [
    {
        "description": "Office supplies from Staples",
        "vendor": "Staples",
        "amount_cents": 8547,  # $85.47
        "currency": "USD",
        "expense_date": (datetime.now() - timedelta(days=1)).isoformat(),
        "payment_method": "Credit Card",
        "category": "Office Supplies",
        "expected_qb_account": "Office Supplies"
    },
    {
        "description": "Team lunch meeting with client",
        "vendor": "Chipotle",
        "amount_cents": 12650,  # $126.50
        "currency": "USD",
        "expense_date": (datetime.now() - timedelta(days=2)).isoformat(),
        "payment_method": "Credit Card",
        "category": "Meals & Entertainment",
        "expected_qb_account": "Meals and Entertainment"
    },
    {
        "description": "Monthly Adobe Creative Cloud subscription",
        "vendor": "Adobe",
        "amount_cents": 5499,  # $54.99
        "currency": "USD",
        "expense_date": (datetime.now() - timedelta(days=3)).isoformat(),
        "payment_method": "Credit Card",
        "category": "Software & Subscriptions",
        "expected_qb_account": "Computer and Internet Expenses"
    },
    {
        "description": "Uber ride to client meeting",
        "vendor": "Uber",
        "amount_cents": 2847,  # $28.47
        "currency": "USD",
        "expense_date": (datetime.now() - timedelta(days=4)).isoformat(),
        "payment_method": "Credit Card",
        "category": "Transportation",
        "expected_qb_account": "Automobile"
    },
    {
        "description": "Facebook ads campaign",
        "vendor": "Facebook",
        "amount_cents": 50000,  # $500.00
        "currency": "USD",
        "expense_date": (datetime.now() - timedelta(days=5)).isoformat(),
        "payment_method": "Credit Card",
        "category": "Marketing & Advertising",
        "expected_qb_account": "Advertising and Promotion"
    },
    {
        "description": "Conference registration - QuickBooks Connect",
        "vendor": "Intuit Events",
        "amount_cents": 29900,  # $299.00
        "currency": "USD",
        "expense_date": (datetime.now() - timedelta(days=7)).isoformat(),
        "payment_method": "Credit Card",
        "category": "Professional Development",
        "expected_qb_account": "Professional Development"
    },
    {
        "description": "Business insurance monthly premium",
        "vendor": "State Farm",
        "amount_cents": 15000,  # $150.00
        "currency": "USD",
        "expense_date": (datetime.now() - timedelta(days=10)).isoformat(),
        "payment_method": "Bank Transfer",
        "category": "Insurance",
        "expected_qb_account": "Insurance"
    },
    {
        "description": "Internet service for office",
        "vendor": "Comcast Business",
        "amount_cents": 12999,  # $129.99
        "currency": "USD",
        "expense_date": (datetime.now() - timedelta(days=15)).isoformat(),
        "payment_method": "Credit Card",
        "category": "Utilities",
        "expected_qb_account": "Utilities"
    },
    {
        "description": "Shipping supplies and postage",
        "vendor": "USPS",
        "amount_cents": 4532,  # $45.32
        "currency": "USD",
        "expense_date": (datetime.now() - timedelta(days=20)).isoformat(),
        "payment_method": "Credit Card",
        "category": "Shipping & Postage",
        "expected_qb_account": "Shipping and Delivery"
    },
    {
        "description": "Hotel for business trip",
        "vendor": "Marriott",
        "amount_cents": 24900,  # $249.00
        "currency": "USD",
        "expense_date": (datetime.now() - timedelta(days=30)).isoformat(),
        "payment_method": "Credit Card",
        "category": "Travel",
        "expected_qb_account": "Travel"
    }
]

# Test scenarios for QuickBooks sync
TEST_SCENARIOS = {
    "happy_path": {
        "name": "Successful Sync",
        "description": "All expenses sync successfully to QuickBooks",
        "expenses": TEST_EXPENSES[:5],
        "expected_result": "success",
        "expected_synced": 5
    },
    "vendor_creation": {
        "name": "New Vendor Creation",
        "description": "Test creating new vendors in QuickBooks",
        "expenses": [
            {
                "description": "New vendor test",
                "vendor": "Test Vendor ABC",
                "amount_cents": 10000,
                "currency": "USD",
                "expense_date": datetime.now().isoformat(),
                "payment_method": "Credit Card",
                "category": "Office Supplies"
            }
        ],
        "expected_result": "success",
        "expected_synced": 1
    },
    "batch_sync": {
        "name": "Batch Sync Performance",
        "description": "Test syncing multiple expenses at once",
        "expenses": TEST_EXPENSES,
        "expected_result": "success",
        "expected_synced": len(TEST_EXPENSES)
    },
    "duplicate_prevention": {
        "name": "Duplicate Prevention",
        "description": "Test that expenses aren't duplicated in QuickBooks",
        "expenses": TEST_EXPENSES[:2],
        "sync_twice": True,
        "expected_result": "success",
        "expected_synced": 2
    }
}

# QuickBooks sandbox test data
QUICKBOOKS_TEST_ACCOUNTS = [
    {"name": "Office Supplies", "id": "7", "type": "Expense"},
    {"name": "Meals and Entertainment", "id": "13", "type": "Expense"},
    {"name": "Automobile", "id": "8", "type": "Expense"},
    {"name": "Computer and Internet Expenses", "id": "45", "type": "Expense"},
    {"name": "Advertising and Promotion", "id": "2", "type": "Expense"},
    {"name": "Professional Development", "id": "46", "type": "Expense"},
    {"name": "Insurance", "id": "11", "type": "Expense"},
    {"name": "Utilities", "id": "23", "type": "Expense"},
    {"name": "Shipping and Delivery", "id": "19", "type": "Expense"},
    {"name": "Travel", "id": "21", "type": "Expense"}
]

def create_test_expense_json():
    """Create JSON file with test expenses"""
    test_data = {
        "expenses": TEST_EXPENSES,
        "scenarios": TEST_SCENARIOS,
        "quickbooks_accounts": QUICKBOOKS_TEST_ACCOUNTS,
        "generated_at": datetime.now().isoformat(),
        "total_amount_cents": sum(e["amount_cents"] for e in TEST_EXPENSES),
        "total_amount_formatted": f"${sum(e['amount_cents'] for e in TEST_EXPENSES) / 100:.2f}"
    }
    
    with open("tests/quickbooks_test_expenses.json", "w") as f:
        json.dump(test_data, f, indent=2)
    
    print(f"[OK] Created {len(TEST_EXPENSES)} test expenses")
    print(f"[$$] Total amount: {test_data['total_amount_formatted']}")
    print(f"[->] Saved to: tests/quickbooks_test_expenses.json")

def print_test_summary():
    """Print summary of test data"""
    print("\n" + "=" * 60)
    print("QuickBooks Test Data Summary")
    print("=" * 60)
    
    print(f"\n[Test Expenses: {len(TEST_EXPENSES)}]")
    for expense in TEST_EXPENSES:
        print(f"  - {expense['vendor']}: ${expense['amount_cents']/100:.2f} ({expense['category']})")
    
    print(f"\n[Test Scenarios: {len(TEST_SCENARIOS)}]")
    for key, scenario in TEST_SCENARIOS.items():
        print(f"  - {scenario['name']}: {scenario['description']}")
    
    print(f"\n[Category Mapping:]")
    for expense in TEST_EXPENSES:
        print(f"  - CORA: {expense['category']} -> QB: {expense['expected_qb_account']}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    create_test_expense_json()
    print_test_summary()