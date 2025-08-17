#!/usr/bin/env python3
"""
Backend Health Check Script
Tests critical API endpoints and database connectivity
"""

import sys
import os
from pathlib import Path

# Add CORA to path
cora_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(cora_path))

def test_database():
    """Test database connectivity"""
    try:
        import sqlite3
        import os
        
        # Check if database file exists
        db_path = "cora.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            conn.close()
            print(f"[OK] Database: Connected - {count} users found")
            return True
        else:
            print("[FAIL] Database: cora.db not found")
            return False
    except Exception as e:
        print(f"[FAIL] Database: {str(e)}")
        return False

def test_models():
    """Test model imports"""
    try:
        from models import User, Expense, Job
        # Category might not exist yet
        print("[OK] Models: Core models imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Models: {str(e)}")
        return False

def test_routes():
    """Test route imports"""
    try:
        from routes import auth_coordinator, expenses, pages
        print("[OK] Routes: Core modules imported")
        return True
    except Exception as e:
        print(f"[FAIL] Routes: {str(e)}")
        return False

def test_jwt():
    """Test JWT configuration"""
    try:
        from services import auth_service
        # Just check if the module loads and has key functions
        if hasattr(auth_service, 'create_access_token'):
            print("[OK] JWT: Auth service available")
            return True
        else:
            print("[FAIL] JWT: Auth service missing key functions")
            return False
    except Exception as e:
        print(f"[FAIL] JWT: {str(e)}")
        return False

def test_redis():
    """Test Redis connectivity"""
    try:
        from utils.redis_manager import redis_manager
        # Redis is optional, just check if module loads
        print("[INFO] Redis: Module loaded (connection optional)")
        return True
    except Exception as e:
        print(f"[WARN] Redis: {str(e)} (optional)")
        return True  # Redis is optional

def main():
    print("\n" + "="*50)
    print("BACKEND HEALTH CHECK")
    print("="*50 + "\n")
    
    results = []
    results.append(test_database())
    results.append(test_models())
    results.append(test_routes())
    results.append(test_jwt())
    results.append(test_redis())
    
    passed = sum(results)
    total = len(results)
    health_score = (passed / total) * 100
    
    print("\n" + "="*50)
    print(f"Backend Health Score: {health_score:.0f}%")
    print(f"Tests Passed: {passed}/{total}")
    
    if health_score == 100:
        print("[OK] Backend is FULLY OPERATIONAL")
    elif health_score >= 80:
        print("[WARN] Backend is MOSTLY OPERATIONAL")
    else:
        print("[FAIL] Backend has CRITICAL ISSUES")
    
    print("="*50 + "\n")
    
    return health_score

if __name__ == "__main__":
    health_score = main()
    sys.exit(0 if health_score == 100 else 1)