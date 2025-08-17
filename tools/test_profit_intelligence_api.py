#!/usr/bin/env python3
"""
Test profit intelligence API endpoints
"""

import requests
import json
from datetime import datetime

# Base URL
BASE_URL = "http://localhost:8000"

# Test credentials
test_email = "glen.day@testcontractor.com"
test_password = "test_password"

def test_api():
    """Test profit intelligence API endpoints"""
    print("Testing Profit Intelligence API")
    print("=" * 50)
    
    # First, login to get a token
    login_data = {
        "username": test_email,
        "password": test_password
    }
    
    print("\n[Test] Login...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("[OK] Login successful")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"[ERROR] Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
    except Exception as e:
        print(f"[ERROR] Login exception: {str(e)}")
        print("[INFO] Make sure the server is running: python app.py")
        return
    
    # Test endpoints
    endpoints = [
        {
            "name": "Health Check",
            "method": "GET",
            "path": "/api/profit-intelligence/health",
            "auth": False
        },
        {
            "name": "Cost Forecast",
            "method": "GET",
            "path": "/api/profit-intelligence/cost-forecast?months=3",
            "auth": True
        },
        {
            "name": "Vendor Performance",
            "method": "GET",
            "path": "/api/profit-intelligence/vendor-performance",
            "auth": True
        },
        {
            "name": "Intelligence Summary",
            "method": "GET",
            "path": "/api/profit-intelligence/profit-intelligence-summary",
            "auth": True
        }
    ]
    
    for endpoint in endpoints:
        print(f"\n[Test] {endpoint['name']}...")
        try:
            url = f"{BASE_URL}{endpoint['path']}"
            if endpoint["method"] == "GET":
                if endpoint["auth"]:
                    response = requests.get(url, headers=headers)
                else:
                    response = requests.get(url)
            
            if response.status_code == 200:
                print(f"  [OK] Status: {response.status_code}")
                data = response.json()
                if "status" in data:
                    print(f"  Response status: {data['status']}")
                if "intelligence_score" in data.get("intelligence_summary", {}):
                    score = data["intelligence_summary"]["intelligence_score"]
                    grade = data["intelligence_summary"]["intelligence_grade"]
                    print(f"  Intelligence Score: {score}/100 (Grade: {grade})")
            else:
                print(f"  [ERROR] Status: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
        except Exception as e:
            print(f"  [ERROR] Exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print("[COMPLETE] API testing finished")

if __name__ == "__main__":
    test_api()