#!/usr/bin/env python3
"""
Show what Plaid sandbox data actually provides
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Sample of what Plaid Sandbox returns for transactions
PLAID_SANDBOX_TRANSACTIONS = [
    {
        "account_id": "abc123",
        "amount": 500,
        "iso_currency_code": "USD",
        "category": ["Food and Drink", "Restaurants"],
        "date": "2025-01-20",
        "name": "SparkFun",
        "merchant_name": "SparkFun Electronics",
        "pending": False,
    },
    {
        "account_id": "abc123", 
        "amount": 2307.21,
        "iso_currency_code": "USD",
        "category": ["Shops", "Computers and Electronics"],
        "date": "2025-01-19",
        "name": "Apple Store",
        "merchant_name": "Apple",
        "pending": False,
    },
    {
        "account_id": "abc123",
        "amount": 12.50,
        "iso_currency_code": "USD", 
        "category": ["Food and Drink", "Coffee Shop"],
        "date": "2025-01-18",
        "name": "Starbucks",
        "merchant_name": "Starbucks",
        "pending": False,
    },
    {
        "account_id": "abc123",
        "amount": 89.99,
        "iso_currency_code": "USD",
        "category": ["Service", "Subscription"],
        "date": "2025-01-17",
        "name": "GOOGLE *YouTube TV",
        "merchant_name": "YouTube TV",
        "pending": False,
    },
    {
        "account_id": "abc123",
        "amount": 145.32,
        "iso_currency_code": "USD",
        "category": ["Shops", "Supermarkets and Groceries"],
        "date": "2025-01-16",
        "name": "Whole Foods",
        "merchant_name": "Whole Foods Market",
        "pending": False,
    }
]

PLAID_SANDBOX_ACCOUNTS = [
    {
        "account_id": "abc123",
        "balances": {
            "available": 1500.50,
            "current": 1650.25,
            "iso_currency_code": "USD",
        },
        "mask": "0000",
        "name": "Plaid Checking",
        "official_name": "Plaid Gold Standard 0% Interest Checking",
        "type": "depository",
        "subtype": "checking",
    },
    {
        "account_id": "def456",
        "balances": {
            "available": 5000.00,
            "current": 5234.52,
            "iso_currency_code": "USD",
        },
        "mask": "1111", 
        "name": "Plaid Saving",
        "official_name": "Plaid Silver Standard 0.1% Interest Saving",
        "type": "depository",
        "subtype": "savings",
    },
    {
        "account_id": "ghi789",
        "balances": {
            "available": 2000.00,
            "current": -1543.21,
            "iso_currency_code": "USD",
        },
        "mask": "2222",
        "name": "Plaid Credit Card", 
        "official_name": "Plaid Diamond 12.5% APR Interest Credit Card",
        "type": "credit",
        "subtype": "credit card",
    }
]

print("🏦 PLAID SANDBOX DATA EXAMPLE")
print("=" * 50)

print("\n📊 ACCOUNTS (What you get after connecting):")
for account in PLAID_SANDBOX_ACCOUNTS:
    print(f"\n✓ {account['name']} (****{account['mask']})")
    print(f"  Type: {account['type']} - {account['subtype']}")
    print(f"  Balance: ${account['balances']['current']:,.2f}")
    print(f"  Available: ${account['balances']['available']:,.2f}")

print("\n\n💳 RECENT TRANSACTIONS (Last 5 of ~100+ provided):")
for txn in PLAID_SANDBOX_TRANSACTIONS:
    print(f"\n✓ {txn['date']} - {txn['merchant_name'] or txn['name']}")
    print(f"  Amount: ${txn['amount']:,.2f}")
    print(f"  Category: {' > '.join(txn['category'])}")
    print(f"  Status: {'Pending' if txn['pending'] else 'Posted'}")

print("\n\n🎯 WHAT THIS ENABLES IN CORA:")
print("✓ Real spending insights based on actual transaction data")
print("✓ Automatic subscription detection (YouTube TV, Netflix, etc.)")
print("✓ Expense categorization for tax purposes")
print("✓ Cash flow analysis and predictions")
print("✓ Family spending tracking by merchant patterns")
print("✓ Real-time balance monitoring")

print("\n\n⚠️  RIGHT NOW:")
print("❌ We're connecting to Plaid successfully")
print("❌ But NOT syncing this data to the database")
print("❌ Dashboard still shows hardcoded values")
print("❌ Missing the actual value of Plaid integration!")