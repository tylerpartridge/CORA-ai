#!/usr/bin/env python3
"""
Setup realistic demo data for contractor video demonstration
Shows a compelling story: One job doing great, one okay, one going over budget
"""
import requests
import json
from datetime import datetime, timedelta
import time

BASE_URL = "http://localhost:8000"

# Demo contractor credentials
DEMO_USER = {
    "email": "tyler@contractordemo.com",
    "password": "demo123"
}

def setup_demo():
    """Setup complete demo scenario"""
    print("🎬 Setting up CORA Demo Data...\n")
    
    # 1. Register demo user
    register_response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": DEMO_USER["email"],
        "password": DEMO_USER["password"],
        "is_active": True
    })
    
    if register_response.status_code not in [200, 400]:
        print(f"❌ Failed to register user: {register_response.text}")
        return
    
    # 2. Login
    login_response = requests.post(f"{BASE_URL}/api/auth/login", 
                                 data={"username": DEMO_USER["email"], 
                                       "password": DEMO_USER["password"]})
    
    if login_response.status_code != 200:
        print(f"❌ Failed to login: {login_response.text}")
        return
    
    cookies = login_response.cookies
    print("✅ Demo user ready\n")
    
    # 3. Create realistic jobs
    jobs = [
        {
            "job_id": "DEMO-001",
            "job_name": "Johnson Bathroom Remodel",
            "customer_name": "Robert & Lisa Johnson",
            "job_address": "742 Maple Street",
            "quoted_amount": 8500.00,
            "status": "active",
            "start_date": (datetime.now() - timedelta(days=7)).isoformat()
        },
        {
            "job_id": "DEMO-002",
            "job_name": "Chen Kitchen Update", 
            "customer_name": "David Chen",
            "job_address": "1829 Oak Avenue",
            "quoted_amount": 15750.00,
            "status": "active",
            "start_date": (datetime.now() - timedelta(days=14)).isoformat()
        },
        {
            "job_id": "DEMO-003",
            "job_name": "Williams Deck Build",
            "customer_name": "Tom Williams",
            "job_address": "456 Pine Road",
            "quoted_amount": 6200.00,
            "status": "active",
            "start_date": (datetime.now() - timedelta(days=10)).isoformat()
        }
    ]
    
    print("📋 Creating demo jobs...")
    for job in jobs:
        response = requests.post(f"{BASE_URL}/api/jobs", json=job, cookies=cookies)
        if response.status_code == 200:
            print(f"  ✅ {job['job_name']} - ${job['quoted_amount']:,.0f}")
    
    # 4. Add strategic expenses to tell a story
    print("\n💸 Adding realistic expenses...")
    
    # Johnson Bathroom - Going great! (35% margin)
    johnson_expenses = [
        ("Home Depot fixtures Johnson bathroom", 847.32, -7),
        ("Lowes tile for Johnson bathroom", 1234.18, -6),
        ("Plumbing supply Johnson bathroom", 423.90, -5),
        ("Labor Johnson bathroom demo", 1200.00, -4),
        ("Labor Johnson bathroom install", 1800.00, -2),
    ]
    
    # Chen Kitchen - Okay but tight (18% margin)
    chen_expenses = [
        ("Home Depot cabinets Chen kitchen", 3847.50, -14),
        ("Appliance store Chen kitchen", 4299.00, -12),
        ("Granite countertops Chen kitchen", 2850.00, -10),
        ("Electrical work Chen kitchen", 890.00, -8),
        ("Labor Chen kitchen five days", 2000.00, -6),
        ("Unexpected plumbing Chen kitchen", 475.00, -3),
    ]
    
    # Williams Deck - Over budget! (-8% margin)
    williams_expenses = [
        ("Lumber yard deck materials Williams", 2847.00, -10),
        ("Home Depot fasteners Williams deck", 234.75, -9),
        ("Concrete for Williams deck posts", 450.00, -8),
        ("Equipment rental Williams deck", 380.00, -7),
        ("Labor Williams deck three days", 1800.00, -5),
        ("Extra lumber Williams deck repair", 487.50, -3),
        ("City permit Williams deck", 275.00, -2),
    ]
    
    # Process expenses with delays for realism
    for expense_list in [johnson_expenses, chen_expenses, williams_expenses]:
        for transcript, amount, days_ago in expense_list:
            # Skip some for demo brevity
            if days_ago < -10:
                continue
                
            response = requests.post(f"{BASE_URL}/api/voice/expense", 
                                   json={"transcript": transcript, "source": "demo_setup"},
                                   cookies=cookies)
            
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    print(f"  ✅ ${amount:.2f} - {transcript[:40]}...")
            
            time.sleep(0.1)  # Slight delay for realism
    
    # 5. Show final state
    print("\n📊 DEMO SCENARIO READY:")
    print("="*50)
    
    jobs_response = requests.get(f"{BASE_URL}/api/jobs", cookies=cookies)
    if jobs_response.status_code == 200:
        jobs_data = jobs_response.json()
        for job in sorted(jobs_data, key=lambda x: x['profit_margin_percent'], reverse=True):
            margin = job['profit_margin_percent']
            status_emoji = "✅" if margin > 25 else "⚡" if margin > 15 else "🚨"
            
            print(f"\n{status_emoji} {job['job_name']}")
            print(f"   Quoted: ${job['quoted_amount']:,.0f}")
            print(f"   Spent:  ${job['total_costs']:,.0f}")
            print(f"   Profit: ${job['profit']:,.0f} ({margin:.1f}%)")
            
            if margin < 20:
                print(f"   ⚠️  NEEDS ATTENTION!")
    
    print("\n" + "="*50)
    print("\n🎬 Demo script ready! Key moments:")
    print("1. Voice: 'Home Depot receipt Johnson bathroom three forty seven'")
    print("2. Voice: 'How's the Johnson bathroom job doing?'")
    print("3. Voice: 'Show me the Williams deck job' (see the problem!)")
    print("4. Dashboard shows instant updates and alerts")
    print("\n✅ Login at http://localhost:8000")
    print(f"   Email: {DEMO_USER['email']}")
    print(f"   Password: {DEMO_USER['password']}")

if __name__ == "__main__":
    setup_demo()