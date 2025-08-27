# --- E2E base URL autodetect (inserted by helper) ---
import os, pytest, requests
BASE_URL = os.getenv("CORA_BASE_URL", "http://localhost:8000")
REMOTE_URL = os.getenv("CORA_REMOTE_URL", "https://coraai.tech")

def _ok(u):
    try:
        requests.get(f"{u}/api/health/status", timeout=1)
        return True
    except Exception:
        return False

if not _ok(BASE_URL):
    if _ok(REMOTE_URL):
        BASE_URL = REMOTE_URL
        print(f"[OK] Using remote server for E2E: {REMOTE_URL}")
    else:
        pytest.skip("E2E target not reachable (start local server or set CORA_REMOTE_URL/CORA_BASE_URL)", allow_module_level=True)
# --- end insert ---
import os, pytest
if os.getenv('CORA_E2E','0') != '1':
    pytest.skip('E2E tests disabled (set CORA_E2E=1 to enable)', allow_module_level=True)
#!/usr/bin/env python3
"""
API Testing Suite for CORA
Tests all endpoints to verify functionality
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths


import requests
import json
from datetime import datetime

# Base URL
BASE_URL = "http://localhost:8000"

# Test data
TEST_USER = {
    "email": "test@cora.com",
    "password": "TestPassword123!"
}

def test_health_endpoints():
    """Test health check endpoints"""
    print("\n=== Testing Health Endpoints ===")
    
    # Test health status
    response = requests.get(f"{BASE_URL}/api/health/status")
    print(f"Health Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    
    # Test readiness
    response = requests.get(f"{BASE_URL}/api/health/ready")
    print(f"Readiness: {response.status_code}")
    
    # Test liveness
    response = requests.get(f"{BASE_URL}/api/health/live")
    print(f"Liveness: {response.status_code}")

def test_pages():
    """Test page endpoints"""
    print("\n=== Testing Page Endpoints ===")
    
    pages = ["/", "/about", "/contact", "/pricing"]
    for page in pages:
        response = requests.get(f"{BASE_URL}{page}")
        print(f"Page {page}: {response.status_code}")

def test_authentication():
    """Test authentication endpoints"""
    print("\n=== Testing Authentication ===")
    
    # Test login
    login_data = {
        "username": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data=login_data
    )
    
    print(f"Login: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        print(f"Token received: {token_data.get('token_type')}")
        return token_data.get("access_token")
    else:
        print(f"Login failed: {response.text}")
        return None

def test_protected_endpoints(token):
    """Test protected endpoints with authentication"""
    print("\n=== Testing Protected Endpoints ===")
    
    if not token:
        print("No token available, skipping protected endpoint tests")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test expenses
    response = requests.get(f"{BASE_URL}/api/expenses", headers=headers)
    print(f"Get Expenses: {response.status_code}")
    if response.status_code == 200:
        expenses = response.json()
        print(f"Found {len(expenses)} expenses")
    
    # Test expense categories
    response = requests.get(f"{BASE_URL}/api/expenses/categories", headers=headers)
    print(f"Get Categories: {response.status_code}")
    
    # Test payments
    response = requests.get(f"{BASE_URL}/api/payments", headers=headers)
    print(f"Get Payments: {response.status_code}")
    
    # Test customers
    response = requests.get(f"{BASE_URL}/api/payments/customers", headers=headers)
    print(f"Get Customers: {response.status_code}")
    
    # Test subscriptions
    response = requests.get(f"{BASE_URL}/api/payments/subscriptions", headers=headers)
    print(f"Get Subscriptions: {response.status_code}")

def test_security_headers():
    """Test security headers"""
    print("\n=== Testing Security Headers ===")
    
    response = requests.get(f"{BASE_URL}/api/health/status")
    headers = response.headers
    
    security_headers = [
        "X-Content-Type-Options",
        "X-Frame-Options",
        "X-XSS-Protection",
        "Strict-Transport-Security",
        "Content-Security-Policy"
    ]
    
    for header in security_headers:
        if header in headers:
            print(f"[OK] {header}: {headers[header][:50]}...")
        else:
            print(f"[MISSING] {header}")

def main():
    """Run all tests"""
    print("Starting CORA API Tests...")
    print(f"Testing against: {BASE_URL}")
    print(f"Time: {datetime.now()}")
    
    # Test health endpoints
    test_health_endpoints()
    
    # Test pages
    test_pages()
    
    # Test authentication and get token
    token = test_authentication()
    
    # Test protected endpoints
    test_protected_endpoints(token)
    
    # Test security headers
    test_security_headers()
    
    print("\n=== Tests Complete ===")

if __name__ == "__main__":
    main()

