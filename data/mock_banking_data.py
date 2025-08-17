"""
🧭 LOCATION: /data/mock_banking_data.py
🎯 PURPOSE: Mock banking data for Tyler's dashboard development
🔗 IMPORTS: datetime
📤 EXPORTS: ACCOUNTS, TRANSACTIONS, get_current_financial_state
"""

from datetime import datetime, timedelta
import random

# Tyler's Scotiabank account structure
ACCOUNTS = {
    "scotia_checking": {
        "id": "acc_scotia_chk_001",
        "institution": "Scotiabank",
        "name": "Personal Checking",
        "type": "checking",
        "subtype": "checking",
        "balance": {
            "current": 3247.18,  # Enough to not be in "broke mode"
            "available": 3247.18
        },
        "currency": "CAD"
    },
    "scotia_savings": {
        "id": "acc_scotia_sav_001",
        "institution": "Scotiabank", 
        "name": "Emergency Savings",
        "type": "savings",
        "subtype": "savings",
        "balance": {
            "current": 892.50,
            "available": 892.50
        },
        "currency": "CAD"
    },
    "scotia_visa": {
        "id": "acc_scotia_visa_001",
        "institution": "Scotiabank",
        "name": "Visa Credit Card",
        "type": "credit",
        "subtype": "credit card",
        "balance": {
            "current": -2876.43,  # Negative = amount owed
            "available": 7123.57,  # Credit limit - current balance
            "limit": 10000.00
        },
        "currency": "CAD"
    },
    "paypal": {
        "id": "acc_paypal_001",
        "institution": "PayPal",
        "name": "PayPal Balance",
        "type": "other",
        "subtype": "digital wallet",
        "balance": {
            "current": 156.32,
            "available": 156.32
        },
        "currency": "CAD"
    }
}

# Generate realistic transactions based on Tyler's life
def generate_transactions():
    transactions = []
    today = datetime.now()
    
    # Subscriptions Tyler hates tracking
    subscriptions = [
        {"name": "NETFLIX.COM", "amount": -22.99, "day": 15},
        {"name": "SPOTIFY FAMILY", "amount": -15.99, "day": 5},
        {"name": "APPLE.COM/ICLOUD", "amount": -3.99, "day": 1},
        {"name": "DISNEY PLUS", "amount": -11.99, "day": 8},
        {"name": "CHATGPT PLUS", "amount": -20.00, "day": 10},
        {"name": "GITHUB COPILOT", "amount": -10.00, "day": 12},
        {"name": "AMAZON PRIME", "amount": -9.99, "day": 22},
        {"name": "GOOGLE STORAGE", "amount": -2.99, "day": 25}
    ]
    
    # Add subscription transactions for the last 3 months
    for month_offset in range(3):
        for sub in subscriptions:
            trans_date = today.replace(day=sub["day"]) - timedelta(days=30*month_offset)
            if trans_date <= today:
                transactions.append({
                    "id": f"trans_{len(transactions)}",
                    "account_id": "acc_scotia_visa_001",
                    "amount": sub["amount"],
                    "date": trans_date.strftime("%Y-%m-%d"),
                    "name": sub["name"],
                    "merchant_name": sub["name"],
                    "category": ["Subscription", "Entertainment"],
                    "pending": False,
                    "family_member": "Household"
                })
    
    # Daughter's spending (16-year-old in Quebec)
    daughter_expenses = [
        {"name": "TIM HORTONS", "amount": -8.50, "category": ["Food and Drink", "Coffee Shop"]},
        {"name": "SUBWAY", "amount": -12.75, "category": ["Food and Drink", "Fast Food"]},
        {"name": "APPLE APP STORE", "amount": -4.99, "category": ["Shopping", "Digital"]},
        {"name": "UBER EATS", "amount": -28.43, "category": ["Food and Drink", "Delivery"]},
        {"name": "WALMART", "amount": -45.67, "category": ["Shopping", "General"]},
        {"name": "STARBUCKS", "amount": -7.25, "category": ["Food and Drink", "Coffee Shop"]}
    ]
    
    # Add daughter's transactions (more frequent, smaller amounts)
    for i in range(15):
        trans = random.choice(daughter_expenses)
        trans_date = today - timedelta(days=random.randint(0, 30))
        transactions.append({
            "id": f"trans_{len(transactions)}",
            "account_id": "acc_scotia_visa_001",
            "amount": trans["amount"] * random.uniform(0.8, 1.2),  # Slight variation
            "date": trans_date.strftime("%Y-%m-%d"),
            "name": trans["name"],
            "merchant_name": trans["name"],
            "category": trans["category"],
            "pending": random.random() < 0.1,  # 10% chance of pending
            "family_member": "Sarah (Daughter)"
        })
    
    # Regular household expenses
    household = [
        {"name": "SOBEYS", "amount": -287.43, "category": ["Food and Drink", "Groceries"], "days_ago": 3},
        {"name": "COSTCO WHOLESALE", "amount": -456.78, "category": ["Shopping", "Wholesale"], "days_ago": 7},
        {"name": "ESSO", "amount": -75.00, "category": ["Transportation", "Gas"], "days_ago": 2},
        {"name": "NEWFOUNDLAND POWER", "amount": -234.56, "category": ["Bills", "Utilities"], "days_ago": 5},
        {"name": "BELL ALIANT", "amount": -189.99, "category": ["Bills", "Internet"], "days_ago": 10},
        {"name": "INSURANCE - HOME", "amount": -167.00, "category": ["Bills", "Insurance"], "days_ago": 15},
        {"name": "SMART WATCH STORE", "amount": -500.00, "category": ["Shopping", "Electronics"], "days_ago": 8,
         "note": "9-year-old daughter safety watch"}
    ]
    
    for expense in household:
        trans_date = today - timedelta(days=expense["days_ago"])
        transactions.append({
            "id": f"trans_{len(transactions)}",
            "account_id": "acc_scotia_chk_001" if expense["amount"] < -200 else "acc_scotia_visa_001",
            "amount": expense["amount"],
            "date": trans_date.strftime("%Y-%m-%d"),
            "name": expense["name"],
            "merchant_name": expense["name"],
            "category": expense["category"],
            "pending": False,
            "family_member": "Tyler/Wife",
            "note": expense.get("note", "")
        })
    
    # Sort by date descending
    transactions.sort(key=lambda x: x["date"], reverse=True)
    return transactions

TRANSACTIONS = generate_transactions()

def get_current_financial_state():
    """Determine Tyler's current financial state based on balances"""
    total_cash = ACCOUNTS["scotia_checking"]["balance"]["current"] + \
                 ACCOUNTS["scotia_savings"]["balance"]["current"] + \
                 ACCOUNTS["paypal"]["balance"]["current"]
    
    total_debt = abs(ACCOUNTS["scotia_visa"]["balance"]["current"])
    
    # Tyler's thresholds from the interview
    if total_cash < 1000:
        return "broke_mode"
    elif total_cash > 10000:
        return "flush_mode"
    else:
        return "planning_mode"

def get_subscription_summary():
    """Get all recurring subscriptions"""
    subs = {}
    for trans in TRANSACTIONS:
        if "Subscription" in trans.get("category", []):
            name = trans["merchant_name"]
            if name not in subs:
                subs[name] = {
                    "amount": trans["amount"],
                    "last_charged": trans["date"],
                    "account": trans["account_id"]
                }
    return subs

def get_family_spending(days=30):
    """Get spending by family member"""
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    family_totals = {}
    
    for trans in TRANSACTIONS:
        if trans["date"] >= cutoff_date and trans["amount"] < 0:
            member = trans.get("family_member", "Unknown")
            if member not in family_totals:
                family_totals[member] = 0
            family_totals[member] += abs(trans["amount"])
    
    return family_totals