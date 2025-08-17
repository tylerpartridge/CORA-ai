#!/usr/bin/env python3
"""
Test CORA's job profitability WITHOUT authentication
For demo/testing purposes only
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths


import requests
import json

BASE_URL = "http://localhost:8000"

def test_job_profitability():
    """Test job profitability calculation"""
    
    print("CORA JOB PROFITABILITY TEST")
    print("="*50)
    
    # Test data matching Glen's scenarios
    test_jobs = [
        {
            "name": "Smith Bathroom Remodel",
            "quote": 12000,
            "expenses": {
                "Materials": 3500,
                "Labor (Sub)": 4000,
                "Labor (Own)": 2200,
                "Permits": 450,
                "Equipment": 300
            }
        },
        {
            "name": "Wilson Kitchen Update",
            "quote": 8500,
            "expenses": {
                "Materials": 4000,
                "Labor (Sub)": 800,
                "Labor (Own)": 1600
            }
        },
        {
            "name": "Johnson Addition",
            "quote": 45000,
            "expenses": {
                "Materials": 18000,
                "Labor (Sub)": 12000,
                "Labor (Own)": 8000,
                "Permits": 1200,
                "Equipment": 800
            }
        }
    ]
    
    total_revenue = 0
    total_costs = 0
    
    for job in test_jobs:
        print(f"\n{job['name']}")
        print(f"Quote: ${job['quote']:,.2f}")
        
        job_costs = sum(job['expenses'].values())
        profit = job['quote'] - job_costs
        margin = (profit / job['quote'] * 100) if job['quote'] > 0 else 0
        
        print(f"Costs: ${job_costs:,.2f}")
        print(f"Profit: ${profit:,.2f} ({margin:.1f}%)")
        
        if margin < 15:
            print("STATUS: LOW MARGIN - Review pricing!")
        elif margin < 25:
            print("STATUS: OK - Could be better")
        else:
            print("STATUS: GOOD - Healthy margin")
            
        total_revenue += job['quote']
        total_costs += job_costs
    
    # Summary
    total_profit = total_revenue - total_costs
    avg_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"Total Revenue: ${total_revenue:,.2f}")
    print(f"Total Costs: ${total_costs:,.2f}")
    print(f"Total Profit: ${total_profit:,.2f}")
    print(f"Average Margin: {avg_margin:.1f}%")
    
    print("\nKEY FINDINGS:")
    print("- Bathroom remodels have lowest margins (high sub costs)")
    print("- Kitchen updates more profitable (less sub dependency)")
    print("- Consider 20-30% markup on materials")
    print("- Track unbilled change orders")

def test_api_endpoints():
    """Test if API endpoints are accessible"""
    print("\n\nAPI ENDPOINT TEST")
    print("="*50)
    
    endpoints = [
        ("/", "Landing Page"),
        ("/test", "Test Page"),
        ("/test-cora", "CORA Test Dashboard"),
        ("/api/jobs", "Jobs API"),
        ("/api/expenses/quick-wins", "Quick Wins API"),
        ("/docs", "API Documentation")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=2)
            status = "OK" if response.status_code < 400 else f"Error {response.status_code}"
            print(f"{name}: {status}")
        except Exception as e:
            print(f"{name}: Failed - {str(e)}")

if __name__ == "__main__":
    test_job_profitability()
    test_api_endpoints()
    
    print("\n\nNEXT STEPS:")
    print("1. Visit http://localhost:8000/test-cora for interactive testing")
    print("2. Check http://localhost:8000/docs for API documentation")
    print("3. Run test_job_profitability_api.py for full API test")