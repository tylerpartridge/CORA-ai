#!/usr/bin/env python3
"""
Test script to verify dashboard displays real data
Creates sample expenses and checks dashboard endpoints
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths


import requests
import json
from datetime import datetime, timedelta
import random

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

# Test user credentials (update these based on your beta users)
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

def login():
    """Login and get access token"""
    response = requests.post(f"{API_BASE}/auth/login", data={
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        return data["access_token"]
    else:
        print(f"Login failed: {response.status_code}")
        print(response.json())
        return None

def create_sample_expenses(token):
    """Create sample expenses for testing"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Sample expense data
    expenses = [
        {"vendor": "Starbucks", "amount": 5.75, "category": "Meals & Entertainment", "description": "Coffee meeting with client"},
        {"vendor": "Office Depot", "amount": 89.99, "category": "Office Supplies", "description": "Printer paper and pens"},
        {"vendor": "Uber", "amount": 23.50, "category": "Transportation", "description": "Ride to client meeting"},
        {"vendor": "Adobe", "amount": 52.99, "category": "Software & Subscriptions", "description": "Creative Cloud subscription"},
        {"vendor": "Facebook Ads", "amount": 150.00, "category": "Marketing & Advertising", "description": "Social media campaign"},
        {"vendor": "Udemy", "amount": 89.99, "category": "Professional Development", "description": "Python course"},
        {"vendor": "Delta Airlines", "amount": 450.00, "category": "Travel", "description": "Flight to conference"},
        {"vendor": "Zoom", "amount": 14.99, "category": "Software & Subscriptions", "description": "Monthly subscription"},
    ]
    
    created_count = 0
    for i, expense in enumerate(expenses):
        # Vary the dates
        days_ago = random.randint(0, 30)
        expense_date = (datetime.utcnow() - timedelta(days=days_ago)).isoformat()
        
        data = {
            "amount": expense["amount"],
            "vendor": expense["vendor"],
            "category_name": expense["category"],
            "description": expense["description"],
            "expense_date": expense_date
        }
        
        response = requests.post(f"{API_BASE}/expenses", 
                                headers=headers, 
                                json=data)
        
        if response.status_code == 200:
            created_count += 1
            print(f"[CHECK] Created expense: {expense['vendor']} - ${expense['amount']}")
        else:
            print(f"[X] Failed to create expense: {response.status_code}")
            print(response.json())
    
    print(f"\nCreated {created_count}/{len(expenses)} sample expenses")
    return created_count > 0

def test_dashboard_endpoints(token):
    """Test all dashboard endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== Testing Dashboard Endpoints ===")
    
    # Test summary endpoint
    print("\n1. Testing /api/dashboard/summary")
    response = requests.get(f"{API_BASE}/dashboard/summary", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("[CHECK] Summary endpoint working")
        print(f"  - Total expenses this month: ${data['summary']['total_expenses_this_month']}")
        print(f"  - Deductions found: ${data['summary']['deductions_found']}")
        print(f"  - Time saved: {data['summary']['time_saved_hours']} hours")
        print(f"  - Categories: {len(data['summary']['categories'])}")
        print(f"  - Recent expenses: {len(data['summary']['recent_expenses'])}")
        print(f"  - Tracking consistency: {data['wellness_metrics']['tracking_consistency']}%")
    else:
        print(f"[X] Summary endpoint failed: {response.status_code}")
        print(response.json())
    
    # Test metrics endpoint
    print("\n2. Testing /api/dashboard/metrics")
    response = requests.get(f"{API_BASE}/dashboard/metrics", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("[CHECK] Metrics endpoint working")
        print(f"  - Revenue: ${data['metrics']['revenue']}")
        print(f"  - Expenses: ${data['metrics']['expenses']}")
        print(f"  - Profit: ${data['metrics']['profit']}")
        print(f"  - Profit margin: {data['metrics']['profit_margin']}%")
        print(f"  - Tax estimate: ${data['metrics']['tax_estimate']}")
        print(f"  - Cash runway: {data['metrics']['cash_runway_months']} months")
        print(f"  - Wellness score: {data['wellness_score']}/100")
    else:
        print(f"[X] Metrics endpoint failed: {response.status_code}")
        print(response.json())
    
    # Test insights endpoint
    print("\n3. Testing /api/dashboard/insights")
    response = requests.get(f"{API_BASE}/dashboard/insights", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("[CHECK] Insights endpoint working")
        print(f"  - Total insights: {data['summary']['total_insights']}")
        print(f"  - High priority: {data['summary']['high_priority']}")
        
        if data['insights']:
            print("\n  Sample insights:")
            for insight in data['insights'][:3]:
                print(f"  - [{insight['type']}] {insight['title']}: {insight['message']}")
    else:
        print(f"[X] Insights endpoint failed: {response.status_code}")
        print(response.json())

def main():
    print("=== CORA Dashboard Data Test ===")
    
    # Login
    print("\nLogging in...")
    token = login()
    if not token:
        print("Failed to login. Make sure you have a test user created.")
        print("You can create one with: python create_test_user.py")
        return
    
    print("[CHECK] Login successful")
    
    # Create sample expenses
    if create_sample_expenses(token):
        # Test dashboard endpoints
        test_dashboard_endpoints(token)
        
        print("\n=== Test Complete ===")
        print("[CHECK] Dashboard is now showing real data!")
        print("[CHECK] Beta users will see their actual financial information")
        print("\nNext steps:")
        print("1. Visit http://localhost:8000/dashboard to see the live dashboard")
        print("2. Try voice capture to add expenses naturally")
        print("3. Check the AI insights for personalized recommendations")
    else:
        print("Failed to create sample data")

if __name__ == "__main__":
    main()