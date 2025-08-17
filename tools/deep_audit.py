#!/usr/bin/env python3
"""
Deep System Audit for CORA
Comprehensive check of all components for beta readiness
"""

import sqlite3
import os
import sys
import requests
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_database_integrity():
    """Check database tables, data, and relationships"""
    print("🔍 DATABASE INTEGRITY CHECK")
    print("=" * 50)
    
    db_path = "data/cora.db"
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📋 Found {len(tables)} tables")
        
        # Check critical tables
        critical_tables = [
            'users', 'expenses', 'expense_categories', 
            'jobs', 'job_alerts', 'business_profiles',
            'contractor_waitlist', 'plaid_integrations'
        ]
        
        missing_critical = [t for t in critical_tables if t not in tables]
        
        if missing_critical:
            print(f"🚨 MISSING CRITICAL TABLES: {missing_critical}")
            return False
        else:
            print("✅ All critical tables present")
        
        # Check data counts
        print("\n📊 Data Counts:")
        for table in critical_tables:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count} rows")
        
        # Check for test user
        cursor.execute("SELECT email FROM users WHERE email = 'test@cora.com'")
        test_user = cursor.fetchone()
        if test_user:
            print("✅ Test user exists")
        else:
            print("⚠️  No test user found")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_api_endpoints():
    """Test all critical API endpoints"""
    print("\n🔍 API ENDPOINTS CHECK")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    endpoints = [
        "/health",
        "/api/status", 
        "/dashboard",
        "/api/expenses",
        "/api/jobs",
        "/api/alerts/summary",
        "/api/onboarding/checklist"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = response.status_code
            if status == 200:
                print(f"✅ {endpoint}: {status}")
                results[endpoint] = "OK"
            elif status == 307:  # Redirect (auth required)
                print(f"⚠️  {endpoint}: {status} (Auth required)")
                results[endpoint] = "AUTH_REQUIRED"
            else:
                print(f"❌ {endpoint}: {status}")
                results[endpoint] = "ERROR"
        except Exception as e:
            print(f"❌ {endpoint}: Connection failed - {e}")
            results[endpoint] = "FAILED"
    
    return results

def check_file_structure():
    """Check critical files exist"""
    print("\n🔍 FILE STRUCTURE CHECK")
    print("=" * 50)
    
    critical_files = [
        "app.py",
        "config.py",
        "web/templates/dashboard_unified.html",
        "web/static/js/cora-chat.js",
        "web/static/js/voice_expense_entry.js",
        "web/static/js/job_profitability.js",
        "web/static/js/demo_video_ui.js",
        "web/static/js/quick_tour.js",
        "web/static/js/automated_demo.js",
        "models/base.py",
        "models/user.py",
        "models/expense.py",
        "models/job.py",
        "routes/expenses.py",
        "routes/jobs.py",
        "routes/alerts.py",
        "services/job_alerts.py",
        "dependencies/auth.py",
        "dependencies/database.py"
    ]
    
    missing_files = []
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def check_imports():
    """Test all critical imports"""
    print("\n🔍 IMPORT CHECK")
    print("=" * 50)
    
    try:
        # Test core imports
        import app
        print("✅ app.py imports successfully")
        
        from models.base import Base
        print("✅ models.base imports successfully")
        
        from dependencies.auth import get_current_user
        print("✅ dependencies.auth imports successfully")
        
        from dependencies.database import get_db
        print("✅ dependencies.database imports successfully")
        
        from services.job_alerts import JobAlertService
        print("✅ services.job_alerts imports successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def check_frontend_assets():
    """Check frontend assets are accessible"""
    print("\n🔍 FRONTEND ASSETS CHECK")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    assets = [
        "/static/js/cora-chat.js",
        "/static/js/voice_expense_entry.js", 
        "/static/js/job_profitability.js",
        "/static/js/demo_video_ui.js",
        "/static/js/quick_tour.js",
        "/static/js/automated_demo.js",
        "/static/css/cora-chat.css",
        "/static/css/onboarding.css"
    ]
    
    accessible = 0
    total = len(assets)
    
    for asset in assets:
        try:
            response = requests.get(f"{base_url}{asset}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {asset}")
                accessible += 1
            else:
                print(f"❌ {asset}: {response.status_code}")
        except Exception as e:
            print(f"❌ {asset}: Connection failed")
    
    print(f"\n📊 Assets accessible: {accessible}/{total}")
    return accessible == total

def generate_audit_report():
    """Generate comprehensive audit report"""
    print("\n" + "="*60)
    print("🔍 COMPREHENSIVE CORA SYSTEM AUDIT")
    print("="*60)
    print(f"Audit Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all checks
    db_ok = check_database_integrity()
    api_results = check_api_endpoints()
    files_ok = check_file_structure()
    imports_ok = check_imports()
    assets_ok = check_frontend_assets()
    
    # Summary
    print("\n" + "="*60)
    print("📋 AUDIT SUMMARY")
    print("="*60)
    
    checks = [
        ("Database Integrity", db_ok),
        ("File Structure", files_ok), 
        ("Import System", imports_ok),
        ("Frontend Assets", assets_ok)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name}: {status}")
        if result:
            passed += 1
    
    # API summary
    api_ok = sum(1 for result in api_results.values() if result in ["OK", "AUTH_REQUIRED"])
    api_total = len(api_results)
    print(f"API Endpoints: {api_ok}/{api_total} accessible")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total and api_ok == api_total:
        print("\n🎉 SYSTEM IS READY FOR BETA LAUNCH!")
    else:
        print("\n⚠️  SYSTEM NEEDS ATTENTION BEFORE BETA LAUNCH")
    
    return passed == total

if __name__ == "__main__":
    generate_audit_report() 