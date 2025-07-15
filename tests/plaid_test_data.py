#!/usr/bin/env python3
"""
Plaid Integration Test Data
Creates test transactions and accounts for Plaid integration testing
"""

import json
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Plaid category mappings to CORA categories
PLAID_TO_CORA_CATEGORY_MAP = {
    "Food and Drink, Restaurants": "Meals & Entertainment",
    "Shops, Computers and Electronics": "Office Supplies",
    "Transfer, Debit": "Transportation",
    "Service, Financial": "Professional Services",
    "Shops, Supermarkets and Groceries": "Office Supplies",
    "Travel, Airlines and Aviation Services": "Travel",
    "Service, Telecommunication Services": "Utilities",
    "Transfer, Credit": "Income",
    "Service, Insurance": "Insurance",
    "Service, Advertising and Marketing": "Marketing & Advertising"
}

# Test bank accounts
TEST_ACCOUNTS = [
    {
        "account_id": "test_checking_001",
        "name": "Business Checking",
        "official_name": "Small Business Checking Account",
        "type": "depository",
        "subtype": "checking",
        "mask": "4567",
        "current_balance": 15432.50,
        "available_balance": 14932.50,
        "currency_code": "USD"
    },
    {
        "account_id": "test_credit_001",
        "name": "Business Credit Card",
        "official_name": "Business Rewards Credit Card",
        "type": "credit",
        "subtype": "credit card",
        "mask": "1234",
        "current_balance": -3456.78,
        "available_balance": 6543.22,
        "currency_code": "USD"
    },
    {
        "account_id": "test_savings_001",
        "name": "Business Savings",
        "official_name": "Business High Yield Savings",
        "type": "depository",
        "subtype": "savings",
        "mask": "8901",
        "current_balance": 50000.00,
        "available_balance": 50000.00,
        "currency_code": "USD"
    }
]

# Test transactions with realistic Plaid data
TEST_TRANSACTIONS = [
    {
        "transaction_id": "plaid_txn_001",
        "account_id": "test_checking_001",
        "amount": 156.78,
        "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "name": "STAPLES STORE #1234",
        "merchant_name": "Staples",
        "category": ["Shops", "Computers and Electronics"],
        "category_id": "19013000",
        "location": {
            "address": "123 Market St",
            "city": "San Francisco",
            "region": "CA",
            "postal_code": "94105",
            "country": "US",
            "lat": 37.7749,
            "lon": -122.4194
        },
        "payment_channel": "in store",
        "pending": False,
        "authorized_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    },
    {
        "transaction_id": "plaid_txn_002",
        "account_id": "test_credit_001",
        "amount": 89.50,
        "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
        "name": "CHIPOTLE ONLINE",
        "merchant_name": "Chipotle Mexican Grill",
        "category": ["Food and Drink", "Restaurants"],
        "category_id": "13005000",
        "location": {
            "city": "San Francisco",
            "region": "CA",
            "country": "US"
        },
        "payment_channel": "online",
        "pending": False
    },
    {
        "transaction_id": "plaid_txn_003",
        "account_id": "test_checking_001",
        "amount": 1200.00,
        "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
        "name": "GOOGLE ADS",
        "merchant_name": "Google",
        "category": ["Service", "Advertising and Marketing"],
        "category_id": "18001000",
        "payment_channel": "online",
        "pending": False
    },
    {
        "transaction_id": "plaid_txn_004",
        "account_id": "test_credit_001",
        "amount": 45.99,
        "date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
        "name": "UBER TRIP",
        "merchant_name": "Uber",
        "category": ["Transportation", "Taxi"],
        "category_id": "22016000",
        "location": {
            "city": "San Francisco",
            "region": "CA"
        },
        "payment_channel": "online",
        "pending": False
    },
    {
        "transaction_id": "plaid_txn_005",
        "account_id": "test_checking_001",
        "amount": 299.00,
        "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
        "name": "ADOBE CREATIVE CLOUD",
        "merchant_name": "Adobe",
        "category": ["Service", "Financial", "Financial Planning and Investments"],
        "category_id": "18020000",
        "payment_channel": "online",
        "pending": False
    },
    {
        "transaction_id": "plaid_txn_006",
        "account_id": "test_checking_001",
        "amount": 2500.00,
        "date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
        "name": "Transfer to Savings",
        "category": ["Transfer", "Account Transfer"],
        "category_id": "21001000",
        "payment_channel": "online",
        "pending": False
    },
    {
        "transaction_id": "plaid_txn_007",
        "account_id": "test_credit_001",
        "amount": 789.45,
        "date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
        "name": "DELTA AIR LINES",
        "merchant_name": "Delta Air Lines",
        "category": ["Travel", "Airlines and Aviation Services"],
        "category_id": "22001000",
        "payment_channel": "online",
        "pending": False
    },
    {
        "transaction_id": "plaid_txn_008",
        "account_id": "test_checking_001",
        "amount": 150.00,
        "date": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
        "name": "STATE FARM INSURANCE",
        "merchant_name": "State Farm",
        "category": ["Service", "Insurance"],
        "category_id": "18030000",
        "payment_channel": "online",
        "pending": False
    },
    {
        "transaction_id": "plaid_txn_009",
        "account_id": "test_checking_001",
        "amount": 35.00,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "name": "PENDING - STARBUCKS",
        "merchant_name": "Starbucks",
        "category": ["Food and Drink", "Coffee Shop"],
        "category_id": "13005043",
        "payment_channel": "in store",
        "pending": True,
        "authorized_date": datetime.now().strftime("%Y-%m-%d")
    },
    {
        "transaction_id": "plaid_txn_010",
        "account_id": "test_credit_001",
        "amount": -1500.00,  # Credit/refund
        "date": (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d"),
        "name": "PAYMENT RECEIVED - THANK YOU",
        "category": ["Transfer", "Credit"],
        "category_id": "21005000",
        "payment_channel": "online",
        "pending": False
    }
]

# Test webhook payloads
TEST_WEBHOOKS = {
    "sync_updates_available": {
        "webhook_type": "SYNC_UPDATES_AVAILABLE",
        "webhook_code": "SYNC_UPDATES_AVAILABLE",
        "item_id": "test_item_001",
        "initial_update_complete": True,
        "historical_update_complete": False
    },
    "initial_update": {
        "webhook_type": "INITIAL_UPDATE",
        "webhook_code": "INITIAL_UPDATE",
        "item_id": "test_item_001",
        "new_transactions": 30,
        "error": None
    },
    "historical_update": {
        "webhook_type": "HISTORICAL_UPDATE",
        "webhook_code": "HISTORICAL_UPDATE",
        "item_id": "test_item_001",
        "new_transactions": 450,
        "error": None
    },
    "transactions_removed": {
        "webhook_type": "TRANSACTIONS_REMOVED",
        "webhook_code": "TRANSACTIONS_REMOVED",
        "item_id": "test_item_001",
        "removed_transactions": ["plaid_txn_009"]  # Remove pending transaction
    },
    "error": {
        "webhook_type": "ERROR",
        "webhook_code": "ERROR",
        "item_id": "test_item_001",
        "error": {
            "error_type": "ITEM_ERROR",
            "error_code": "ITEM_LOGIN_REQUIRED",
            "error_message": "The login credentials have changed",
            "display_message": "Please update your bank login credentials"
        }
    }
}

# Test scenarios for Plaid sync
TEST_SCENARIOS = {
    "happy_path": {
        "name": "Successful Bank Sync",
        "description": "Connect bank account and sync all transactions successfully",
        "accounts": TEST_ACCOUNTS,
        "transactions": TEST_TRANSACTIONS[:8],  # Exclude pending and credit
        "expected_expenses": 7,
        "expected_categories": ["Office Supplies", "Meals & Entertainment", "Marketing & Advertising", 
                               "Transportation", "Software & Subscriptions", "Travel", "Insurance"]
    },
    "pending_transactions": {
        "name": "Pending Transaction Handling",
        "description": "Test pending transactions that get confirmed or removed",
        "accounts": [TEST_ACCOUNTS[1]],
        "transactions": [TEST_TRANSACTIONS[8]],  # Pending transaction
        "webhook_sequence": ["sync_updates_available", "transactions_removed"],
        "expected_behavior": "Pending transaction should not create expense until confirmed"
    },
    "credit_refund": {
        "name": "Credit and Refund Handling",
        "description": "Test negative amount transactions (credits/refunds)",
        "accounts": [TEST_ACCOUNTS[1]],
        "transactions": [TEST_TRANSACTIONS[9]],  # Credit transaction
        "expected_behavior": "Should create income or reduce expense"
    },
    "reauth_required": {
        "name": "Re-authentication Flow",
        "description": "Test when bank requires re-authentication",
        "webhook": TEST_WEBHOOKS["error"],
        "expected_behavior": "User should be prompted to reconnect bank"
    },
    "large_historical_sync": {
        "name": "Large Historical Data Sync",
        "description": "Test syncing 24 months of historical data",
        "accounts": TEST_ACCOUNTS,
        "transaction_count": 500,
        "expected_behavior": "Should handle large data sets without timeout"
    }
}

def generate_bulk_transactions(count: int, account_ids: list) -> list:
    """Generate bulk test transactions for stress testing"""
    transactions = []
    merchants = ["Amazon", "Walmart", "Target", "Best Buy", "Home Depot", "Costco"]
    categories = list(PLAID_TO_CORA_CATEGORY_MAP.keys())
    
    for i in range(count):
        days_ago = random.randint(0, 730)  # Up to 2 years
        amount = round(random.uniform(10, 1000), 2)
        
        transactions.append({
            "transaction_id": f"plaid_bulk_{i:04d}",
            "account_id": random.choice(account_ids),
            "amount": amount,
            "date": (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "name": f"{random.choice(merchants)} PURCHASE",
            "merchant_name": random.choice(merchants),
            "category": random.choice(categories).split(", "),
            "payment_channel": random.choice(["in store", "online"]),
            "pending": False
        })
    
    return transactions

def create_plaid_test_json():
    """Create JSON file with Plaid test data"""
    test_data = {
        "accounts": TEST_ACCOUNTS,
        "transactions": TEST_TRANSACTIONS,
        "webhooks": TEST_WEBHOOKS,
        "scenarios": TEST_SCENARIOS,
        "category_mappings": PLAID_TO_CORA_CATEGORY_MAP,
        "generated_at": datetime.now().isoformat(),
        "total_test_amount": sum(t["amount"] for t in TEST_TRANSACTIONS if t["amount"] > 0),
        "test_credentials": {
            "sandbox": {
                "username": "user_good",
                "password": "pass_good",
                "institution": "ins_109508"  # First Platypus Bank
            }
        }
    }
    
    with open("tests/plaid_test_data.json", "w") as f:
        json.dump(test_data, f, indent=2)
    
    print(f"[OK] Created {len(TEST_TRANSACTIONS)} test transactions")
    print(f"[OK] Created {len(TEST_ACCOUNTS)} test accounts")
    print(f"[->] Saved to: tests/plaid_test_data.json")

def print_test_summary():
    """Print summary of test data"""
    print("\n" + "=" * 60)
    print("Plaid Test Data Summary")
    print("=" * 60)
    
    print(f"\n[Test Accounts: {len(TEST_ACCOUNTS)}]")
    for account in TEST_ACCOUNTS:
        print(f"  - {account['name']}: ${account['current_balance']:,.2f} ({account['subtype']})")
    
    print(f"\n[Test Transactions: {len(TEST_TRANSACTIONS)}]")
    for txn in TEST_TRANSACTIONS:
        status = "[PENDING]" if txn.get('pending') else ""
        amount = f"${txn['amount']:,.2f}" if txn['amount'] > 0 else f"-${abs(txn['amount']):,.2f}"
        print(f"  - {txn.get('merchant_name', txn['name'])}: {amount} {status}")
    
    print(f"\n[Test Scenarios: {len(TEST_SCENARIOS)}]")
    for key, scenario in TEST_SCENARIOS.items():
        print(f"  - {scenario['name']}: {scenario['description']}")
    
    print(f"\n[Category Mappings: {len(PLAID_TO_CORA_CATEGORY_MAP)}]")
    for plaid_cat, cora_cat in list(PLAID_TO_CORA_CATEGORY_MAP.items())[:5]:
        print(f"  - {plaid_cat} -> {cora_cat}")
    print("  - ... and more")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    create_plaid_test_json()
    print_test_summary()