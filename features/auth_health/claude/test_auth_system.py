#!/usr/bin/env python3
"""
Authentication System Health Check
Tests all auth endpoints and functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from datetime import datetime, timedelta
import json

def test_auth_imports():
    """Test that all auth modules import correctly"""
    try:
        from services.auth_service import (
            create_access_token, 
            verify_password, 
            get_password_hash,
            get_current_user
        )
        print("[OK] Auth service imports successful")
        return True
    except ImportError as e:
        print(f"[FAIL] Auth service import failed: {e}")
        return False

def test_password_hashing():
    """Test password hashing and verification"""
    try:
        from services.auth_service import verify_password, get_password_hash
        
        test_password = "TestPassword123!"
        hashed = get_password_hash(test_password)
        
        # Verify correct password
        if verify_password(test_password, hashed):
            print("[OK] Password hashing and verification works")
        else:
            print("[FAIL] Password verification failed for correct password")
            return False
            
        # Verify wrong password fails
        if not verify_password("WrongPassword", hashed):
            print("[OK] Wrong password correctly rejected")
        else:
            print("[FAIL] Wrong password was incorrectly accepted")
            return False
            
        return True
    except Exception as e:
        print(f"[FAIL] Password hashing test failed: {e}")
        return False

def test_jwt_creation():
    """Test JWT token creation"""
    try:
        from services.auth_service import create_access_token
        
        # Create token
        test_data = {"sub": "test@example.com"}
        token = create_access_token(data=test_data)
        
        if token and len(token) > 20:
            print(f"[OK] JWT token created: {token[:20]}...")
        else:
            print("[FAIL] JWT token creation failed")
            return False
            
        # Create token with expiry
        token_with_expiry = create_access_token(
            data=test_data,
            expires_delta=timedelta(hours=1)
        )
        
        if token_with_expiry:
            print("[OK] JWT token with expiry created")
        else:
            print("[FAIL] JWT token with expiry failed")
            return False
            
        return True
    except Exception as e:
        print(f"[FAIL] JWT creation test failed: {e}")
        return False

def test_database_connection():
    """Test database connection for auth"""
    try:
        import sqlite3
        conn = sqlite3.connect('cora.db')
        cursor = conn.cursor()
        
        # Check users table exists
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"[OK] Database connection successful, {user_count} users found")
        
        # Check for auth-related columns
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = ['email', 'hashed_password', 'is_active']
        missing = [c for c in required_columns if c not in columns]
        
        if missing:
            print(f"[WARN] Missing columns in users table: {missing}")
        else:
            print("[OK] All required auth columns present")
            
        conn.close()
        return True
    except Exception as e:
        print(f"[FAIL] Database connection test failed: {e}")
        return False

def test_auth_endpoints():
    """Test that auth endpoints are registered"""
    try:
        from app import app
        
        # Get all routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
                
        # Check for auth endpoints
        auth_endpoints = [
            '/api/auth/login',
            '/api/auth/register', 
            '/api/auth/logout',
            '/api/users/me'
        ]
        
        missing_endpoints = []
        for endpoint in auth_endpoints:
            if endpoint in routes:
                print(f"[OK] Endpoint registered: {endpoint}")
            else:
                print(f"[WARN] Endpoint not found: {endpoint}")
                missing_endpoints.append(endpoint)
                
        return len(missing_endpoints) == 0
    except Exception as e:
        print(f"[FAIL] Endpoint test failed: {e}")
        return False

def run_auth_health_check():
    """Run complete auth system health check"""
    print("\n" + "="*60)
    print("AUTHENTICATION SYSTEM HEALTH CHECK")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*60)
    
    tests = [
        ("Import Test", test_auth_imports),
        ("Password Hashing", test_password_hashing),
        ("JWT Creation", test_jwt_creation),
        ("Database Connection", test_database_connection),
        ("Endpoint Registration", test_auth_endpoints)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        print("-" * 40)
        if test_func():
            passed += 1
        else:
            failed += 1
            
    print("\n" + "="*60)
    print("RESULTS:")
    print(f"  Passed: {passed}/{len(tests)}")
    print(f"  Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\nStatus: ALL TESTS PASSED - Auth system is healthy!")
    elif failed <= 1:
        print("\nStatus: MOSTLY WORKING - Minor issues detected")
    else:
        print("\nStatus: CRITICAL - Multiple auth system failures")
        
    print("="*60 + "\n")
    
    return failed == 0

if __name__ == "__main__":
    healthy = run_auth_health_check()
    exit(0 if healthy else 1)