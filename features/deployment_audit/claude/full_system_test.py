#!/usr/bin/env python3
"""
CORA Full System Test - Deployment Readiness Check
Purpose: Test all critical user flows and API endpoints
Author: Claude
Date: 2025-08-13
"""

import requests
import json
import time
from datetime import datetime
import sys
import os

# Configuration
BASE_URL = "http://localhost:8001"
TEST_EMAIL = f"test_{int(time.time())}@example.com"
TEST_PASSWORD = "TestPassword123!"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "warnings": [],
    "critical_issues": []
}

def test_endpoint(name, method, url, **kwargs):
    """Test a single endpoint"""
    results["total"] += 1
    try:
        response = requests.request(method, f"{BASE_URL}{url}", timeout=5, **kwargs)
        if response.status_code < 400:
            print(f"{GREEN}✓{RESET} {name}: {response.status_code}")
            results["passed"] += 1
            return response
        else:
            print(f"{RED}✗{RESET} {name}: {response.status_code}")
            results["failed"] += 1
            if response.status_code >= 500:
                results["critical_issues"].append(f"{name}: Server error {response.status_code}")
            return response
    except Exception as e:
        print(f"{RED}✗{RESET} {name}: {str(e)}")
        results["failed"] += 1
        results["critical_issues"].append(f"{name}: {str(e)}")
        return None

def check_frontend_pages():
    """Test all public pages"""
    print(f"\n{BLUE}=== Testing Public Pages ==={RESET}")
    
    pages = [
        ("/", "Landing Page"),
        ("/login", "Login Page"),
        ("/signup", "Signup Page"),
        ("/features", "Features Page"),
        ("/pricing", "Pricing Page"),
        ("/how-it-works", "How It Works"),
        ("/reviews", "Reviews Page"),
        ("/contact", "Contact Page"),
        ("/about", "About Page"),
        ("/help", "Help Center"),
        ("/terms", "Terms of Service"),
        ("/privacy", "Privacy Policy"),
        ("/security", "Security Page"),
        ("/blog", "Blog Index"),
    ]
    
    for url, name in pages:
        response = test_endpoint(name, "GET", url)
        if response and response.status_code == 200:
            # Check for placeholder content
            if "Lorem ipsum" in response.text or "TODO" in response.text:
                results["warnings"].append(f"{name} contains placeholder content")

def check_api_endpoints():
    """Test API endpoints"""
    print(f"\n{BLUE}=== Testing API Endpoints ==={RESET}")
    
    # Health checks
    test_endpoint("Health Check", "GET", "/health")
    test_endpoint("API Health", "GET", "/api/health")
    
    # Public endpoints
    test_endpoint("Capture Email", "POST", "/api/v1/capture-email", 
                 json={"email": "test@example.com"})
    
    # Auth endpoints (should fail without auth)
    response = test_endpoint("Dashboard API", "GET", "/api/dashboard")
    if response and response.status_code == 200:
        results["critical_issues"].append("Dashboard API accessible without auth!")
    
    test_endpoint("Expenses API", "GET", "/api/expenses")
    test_endpoint("Jobs API", "GET", "/api/jobs")

def test_authentication_flow():
    """Test complete auth flow"""
    print(f"\n{BLUE}=== Testing Authentication Flow ==={RESET}")
    
    # Test registration
    register_response = test_endpoint(
        "User Registration", "POST", "/api/auth/register",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "full_name": "Test User",
            "business_name": "Test Construction Co"
        }
    )
    
    if register_response and register_response.status_code == 200:
        # Test login
        login_response = test_endpoint(
            "User Login", "POST", "/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        
        if login_response and login_response.status_code == 200:
            token = login_response.json().get("access_token")
            if token:
                # Test authenticated endpoints
                headers = {"Authorization": f"Bearer {token}"}
                test_endpoint("Auth Dashboard", "GET", "/api/dashboard", headers=headers)
                test_endpoint("Auth Expenses", "GET", "/api/expenses", headers=headers)
                return token
    
    return None

def check_form_submissions():
    """Test form endpoints"""
    print(f"\n{BLUE}=== Testing Form Submissions ==={RESET}")
    
    # Contact form
    test_endpoint("Contact Form", "POST", "/api/contact",
                 json={"name": "Test", "email": "test@test.com", "message": "Test message"})
    
    # Feedback form
    test_endpoint("Feedback Form", "POST", "/api/feedback",
                 json={"feedback": "Test feedback", "rating": 5})
    
    # Newsletter signup
    test_endpoint("Newsletter Signup", "POST", "/api/newsletter",
                 json={"email": "newsletter@test.com"})

def check_critical_features():
    """Check if critical features are working"""
    print(f"\n{BLUE}=== Testing Critical Features ==={RESET}")
    
    # Check if database is accessible
    try:
        import sqlite3
        conn = sqlite3.connect('cora.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"{GREEN}✓{RESET} Database accessible: {user_count} users")
        results["passed"] += 1
    except Exception as e:
        print(f"{RED}✗{RESET} Database error: {e}")
        results["critical_issues"].append(f"Database not accessible: {e}")
        results["failed"] += 1
    
    # Check static files
    test_endpoint("CSS Files", "GET", "/static/css/navbar.css")
    test_endpoint("JS Files", "GET", "/static/js/main.js")
    
    # Check if chat endpoint exists
    test_endpoint("CORA Chat", "POST", "/api/cora-ai/chat",
                 json={"message": "Hello"})

def check_missing_endpoints():
    """Check for potentially missing endpoints"""
    print(f"\n{BLUE}=== Checking Potentially Missing Endpoints ==={RESET}")
    
    missing = [
        ("/api/cora-chat-v2/", "CORA Chat v2"),
        ("/api/wellness/emotional-state", "Wellness Emotional State"),
        ("/api/predictive-intelligence/insights", "Predictive Intelligence"),
        ("/api/signup", "Legacy Signup Endpoint"),
    ]
    
    for url, name in missing:
        response = test_endpoint(name, "GET", url)
        if response and response.status_code == 404:
            results["warnings"].append(f"{name} endpoint not found (may be deprecated)")

def generate_report():
    """Generate final report"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}DEPLOYMENT READINESS REPORT{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    success_rate = (results["passed"] / results["total"]) * 100 if results["total"] > 0 else 0
    
    print(f"\nTest Results:")
    print(f"  Total Tests: {results['total']}")
    print(f"  {GREEN}Passed: {results['passed']}{RESET}")
    print(f"  {RED}Failed: {results['failed']}{RESET}")
    print(f"  Success Rate: {success_rate:.1f}%")
    
    if results["critical_issues"]:
        print(f"\n{RED}CRITICAL ISSUES (Must Fix):{RESET}")
        for issue in results["critical_issues"]:
            print(f"  ❌ {issue}")
    
    if results["warnings"]:
        print(f"\n{YELLOW}WARNINGS (Should Review):{RESET}")
        for warning in results["warnings"]:
            print(f"  ⚠️  {warning}")
    
    # Deployment readiness assessment
    print(f"\n{BLUE}DEPLOYMENT READINESS:{RESET}")
    if success_rate >= 90 and not results["critical_issues"]:
        print(f"  {GREEN}✅ READY FOR DEPLOYMENT{RESET}")
        print("  System is functioning well with minor issues only")
    elif success_rate >= 70:
        print(f"  {YELLOW}⚠️  MOSTLY READY{RESET}")
        print("  Fix critical issues before deploying to production")
    else:
        print(f"  {RED}❌ NOT READY{RESET}")
        print("  Major issues need to be resolved first")
    
    # Save detailed report
    report = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "success_rate": success_rate,
        "ready_for_deployment": success_rate >= 90 and not results["critical_issues"]
    }
    
    with open("/mnt/host/c/CORA/features/deployment_audit/claude/test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: test_report.json")

def main():
    print(f"{BLUE}Starting CORA Full System Test...{RESET}")
    print(f"Testing against: {BASE_URL}")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        print(f"{GREEN}✓ Server is running{RESET}")
    except:
        print(f"{RED}✗ Server is not running on {BASE_URL}{RESET}")
        print("Please start the server with: python app.py")
        sys.exit(1)
    
    # Run all tests
    check_frontend_pages()
    check_api_endpoints()
    test_authentication_flow()
    check_form_submissions()
    check_critical_features()
    check_missing_endpoints()
    
    # Generate report
    generate_report()

if __name__ == "__main__":
    main()