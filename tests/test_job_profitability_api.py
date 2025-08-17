#!/usr/bin/env python3
"""
Test job profitability using the API endpoints
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# Test user credentials
TEST_USER = {
    "email": "test@contractor.com",
    "password": "testpass123"
}

def register_user():
    """Register test user"""
    response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"],
        "is_active": True
    })
    if response.status_code == 200:
        print(f"✅ User registered: {TEST_USER['email']}")
    elif response.status_code == 400:
        print(f"ℹ️  User already exists: {TEST_USER['email']}")
    else:
        print(f"❌ Registration failed: {response.text}")
    return response.status_code in [200, 400]

def login_user():
    """Login and get session cookie"""
    response = requests.post(f"{BASE_URL}/api/auth/login", 
                           data={"username": TEST_USER["email"], "password": TEST_USER["password"]})
    if response.status_code == 200:
        print("✅ Login successful")
        return response.cookies
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def create_jobs(cookies):
    """Create sample construction jobs"""
    jobs_data = [
        {
            "job_id": "JOB-001",
            "job_name": "Johnson Bathroom Remodel",
            "customer_name": "Robert Johnson",
            "job_address": "123 Oak Street, Springfield",
            "quoted_amount": 12500.00,
            "status": "active",
            "start_date": (datetime.now() - timedelta(days=14)).isoformat()
        },
        {
            "job_id": "JOB-002", 
            "job_name": "Smith Kitchen Renovation",
            "customer_name": "Sarah Smith",
            "job_address": "456 Maple Ave, Springfield",
            "quoted_amount": 18750.00,
            "status": "active",
            "start_date": (datetime.now() - timedelta(days=21)).isoformat()
        },
        {
            "job_id": "JOB-003",
            "job_name": "Miller House Rewire",
            "customer_name": "Mike Miller", 
            "job_address": "789 Pine Road, Springfield",
            "quoted_amount": 8500.00,
            "status": "completed",
            "start_date": (datetime.now() - timedelta(days=45)).isoformat(),
            "end_date": (datetime.now() - timedelta(days=5)).isoformat()
        }
    ]
    
    for job in jobs_data:
        response = requests.post(f"{BASE_URL}/api/jobs", json=job, cookies=cookies)
        if response.status_code == 200:
            print(f"✅ Created job: {job['job_name']}")
        else:
            print(f"⚠️  Job creation issue: {response.text}")

def create_expenses_via_voice(cookies):
    """Create expenses using the voice endpoint"""
    voice_expenses = [
        # Johnson Bathroom
        {"transcript": "Home Depot receipt Johnson bathroom three forty seven"},
        {"transcript": "Lowes purchase for Johnson bathroom plumbing supplies eight ninety two fifty"},
        {"transcript": "Tile shop for Johnson bathroom twelve fifty"},
        {"transcript": "Labor costs Johnson bathroom twenty four hundred"},
        {"transcript": "City permits for Johnson bathroom one seventy five"},
        
        # Smith Kitchen  
        {"transcript": "Home Depot cabinets for Smith kitchen twenty eight forty seven"},
        {"transcript": "Appliance store Smith kitchen forty five ninety nine"},
        {"transcript": "Electrical supply for Smith kitchen four sixty eight ninety"},
        {"transcript": "Granite countertops Smith kitchen thirty two hundred"},
        {"transcript": "Labor for Smith kitchen renovation thirty six hundred"},
        
        # Miller Rewire
        {"transcript": "Electrical supply Miller house rewire eighteen forty seven twenty five"},
        {"transcript": "Home Depot outlets for Miller rewire two thirty four"},
        {"transcript": "Labor Miller house rewire forty eight hundred"},
        {"transcript": "City permits Miller electrical four twenty five"},
    ]
    
    for expense in voice_expenses:
        response = requests.post(f"{BASE_URL}/api/voice/expense", 
                               json=expense, 
                               cookies=cookies)
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                exp = data["expense"]
                print(f"✅ Added: ${exp['amount_cents']/100:.2f} - {exp['vendor']} ({exp['job_name']})")
            else:
                print(f"⚠️  Failed: {data['error']} - {expense['transcript']}")
        else:
            print(f"❌ API Error: {response.text}")

def show_job_profitability(cookies):
    """Display job profitability summary"""
    response = requests.get(f"{BASE_URL}/api/jobs", cookies=cookies)
    if response.status_code != 200:
        print(f"❌ Failed to get jobs: {response.text}")
        return
    
    jobs = response.json()
    
    print("\n" + "="*60)
    print("JOB PROFITABILITY SUMMARY")
    print("="*60)
    
    for job in jobs:
        profit = job.get('profit', 0)
        margin = job.get('profit_margin_percent', 0)
        
        print(f"\n{job['job_name']}")
        print(f"  Customer: {job.get('customer_name', 'N/A')}")
        print(f"  Status: {job['status']}")
        print(f"  Quoted: ${job.get('quoted_amount', 0):,.2f}")
        print(f"  Costs: ${job.get('total_costs', 0):,.2f}")
        print(f"  Profit: ${profit:,.2f} ({margin:.1f}% margin)")
        
        if margin < 20:
            print(f"  ⚠️  WARNING: Low margin!")
        elif margin > 30:
            print(f"  ✅ Great margin!")

def test_dashboard_api(cookies):
    """Test the dashboard summary API"""
    response = requests.get(f"{BASE_URL}/api/dashboard/summary", cookies=cookies)
    if response.status_code == 200:
        data = response.json()
        print(f"\n📊 Dashboard Summary:")
        print(f"  Total Cash: ${data.get('total_cash', 0):,.2f}")
        print(f"  Net Income: ${data.get('net_income', 0):,.2f}")
        print(f"  Total Income: ${data.get('total_income', 0):,.2f}")
        print(f"  Total Expenses: ${data.get('total_expenses', 0):,.2f}")
    else:
        print(f"⚠️  Dashboard API issue: {response.text}")

def main():
    print("🚧 Testing CORA Job Profitability\n")
    
    # Register/login
    if not register_user():
        return
    
    cookies = login_user()
    if not cookies:
        return
    
    # Create test data
    print("\n📝 Creating sample jobs...")
    create_jobs(cookies)
    
    print("\n🎤 Adding expenses via voice...")
    create_expenses_via_voice(cookies)
    
    # Show results
    show_job_profitability(cookies)
    test_dashboard_api(cookies)
    
    print("\n✅ Test complete! Check dashboard at http://localhost:8000/dashboard")

if __name__ == "__main__":
    main()