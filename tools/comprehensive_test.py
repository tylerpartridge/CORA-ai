#!/usr/bin/env python3
"""
Comprehensive CORA System Test
Tests all critical components and dependencies
"""

import requests
import json
import sys
import time
from datetime import datetime

def test_health_endpoint():
    """Test basic health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health endpoint: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_api_status():
    """Test API status endpoint"""
    try:
        response = requests.get("http://localhost:8000/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API status: {data.get('status', 'unknown')} (uptime: {data.get('uptime', 'unknown')})")
            return True
        else:
            print(f"❌ API status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API status error: {e}")
        return False

def test_dashboard():
    """Test dashboard endpoint"""
    try:
        response = requests.get("http://localhost:8000/dashboard", timeout=5)
        if response.status_code == 200:
            content = response.text
            if "CORA" in content and "Dashboard" in content:
                print("✅ Dashboard: Loads successfully")
                return True
            else:
                print("❌ Dashboard: Content validation failed")
                return False
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        return False

def test_protected_endpoints():
    """Test protected endpoints return proper auth errors"""
    protected_endpoints = [
        "/api/expenses",
        "/api/jobs", 
        "/api/alerts",
        "/api/voice/expense"
    ]
    
    all_good = True
    for endpoint in protected_endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            if response.status_code in [401, 307]:  # 401 = unauthorized, 307 = redirect to login
                print(f"✅ {endpoint}: Properly protected ({response.status_code})")
            else:
                print(f"⚠️  {endpoint}: Unexpected status {response.status_code}")
                all_good = False
        except Exception as e:
            print(f"❌ {endpoint}: Error {e}")
            all_good = False
    
    return all_good

def test_imports():
    """Test critical Python imports"""
    try:
        from dependencies.database import get_db
        print("✅ Database dependency: OK")
    except Exception as e:
        print(f"❌ Database dependency: {e}")
        return False
    
    try:
        from services.job_alerts import JobAlertService
        print("✅ Job alerts service: OK")
    except Exception as e:
        print(f"❌ Job alerts service: {e}")
        return False
    
    try:
        from routes.waitlist import waitlist_router
        print("✅ Waitlist router: OK")
    except Exception as e:
        print(f"❌ Waitlist router: {e}")
        return False
    
    try:
        from routes.alert_routes import alert_router
        print("✅ Alert routes: OK")
    except Exception as e:
        print(f"❌ Alert routes: {e}")
        return False
    
    return True

def test_dependencies():
    """Test required Python packages"""
    required_packages = [
        "fastapi",
        "sqlalchemy", 
        "psycopg2",
        "redis",
        "uvicorn"
    ]
    
    all_good = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: Installed")
        except ImportError:
            print(f"❌ {package}: Missing")
            all_good = False
    
    return all_good

def main():
    """Run comprehensive system test"""
    print("🔍 CORA System Comprehensive Test")
    print("=" * 50)
    print(f"Test started at: {datetime.now()}")
    print()
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("API Status", test_api_status),
        ("Dashboard", test_dashboard),
        ("Protected Endpoints", test_protected_endpoints),
        ("Python Imports", test_imports),
        ("Dependencies", test_dependencies)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Testing: {test_name}")
        print("-" * 30)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: Test error - {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - System is ready!")
        return 0
    else:
        print("⚠️  Some tests failed - Review issues above")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 