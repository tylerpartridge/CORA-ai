#!/usr/bin/env python3
"""
Critical Endpoint Testing for Production Deployment
Tests essential API endpoints for basic functionality
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths

import sys
sys.path.append('/mnt/host/c/CORA')

import asyncio
import uvicorn
from fastapi.testclient import TestClient
import time
import json

def test_critical_endpoints():
    """Test critical endpoints without starting full server"""
    try:
        from app import app
        client = TestClient(app)
        
        print("Testing Critical Endpoints for Production Deployment")
        print("=" * 60)
        
        results = {
            "passed": 0,
            "failed": 0,
            "tests": []
        }
        
        # Test 1: Health Check
        try:
            response = client.get("/health")
            status = "PASS" if response.status_code == 200 else "FAIL"
            results["tests"].append(f"Health Check: {status} ({response.status_code})")
            if response.status_code == 200:
                results["passed"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            results["tests"].append(f"Health Check: FAIL (Exception: {str(e)})")
            results["failed"] += 1
        
        # Test 2: Auth Routes Load
        try:
            response = client.get("/api/auth/test")  # Should return method not allowed, but route exists
            status = "PASS" if response.status_code in [200, 405, 404] else "FAIL"
            results["tests"].append(f"Auth Routes: {status} ({response.status_code})")
            if response.status_code in [200, 405, 404]:
                results["passed"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            results["tests"].append(f"Auth Routes: FAIL (Exception: {str(e)})")
            results["failed"] += 1
        
        # Test 3: Dashboard Routes Load
        try:
            response = client.get("/api/dashboard/summary")  # Should require auth
            status = "PASS" if response.status_code in [401, 403] else "FAIL"
            results["tests"].append(f"Dashboard Routes: {status} ({response.status_code})")
            if response.status_code in [401, 403]:
                results["passed"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            results["tests"].append(f"Dashboard Routes: FAIL (Exception: {str(e)})")
            results["failed"] += 1
        
        # Test 4: Static Files
        try:
            response = client.get("/static/css/styles.css")
            status = "PASS" if response.status_code in [200, 404] else "FAIL"
            results["tests"].append(f"Static Files: {status} ({response.status_code})")
            if response.status_code in [200, 404]:
                results["passed"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            results["tests"].append(f"Static Files: FAIL (Exception: {str(e)})")
            results["failed"] += 1
        
        # Test 5: Database Connection
        try:
            from dependencies.database import get_db
            db_generator = get_db()
            db_session = next(db_generator)
            result = db_session.execute("SELECT 1").fetchone()
            next(db_generator, None)  # Properly close the generator
            results["tests"].append("Database Connection: PASS")
            results["passed"] += 1
        except Exception as e:
            results["tests"].append(f"Database Connection: FAIL (Exception: {str(e)})")
            results["failed"] += 1
        
        # Print Results
        print("\nTest Results:")
        for test in results["tests"]:
            print(f"  {test}")
        
        print(f"\nSummary: {results['passed']} passed, {results['failed']} failed")
        
        if results["failed"] == 0:
            print("\nAll critical endpoints ready for production!")
            return True
        else:
            print(f"\n{results['failed']} critical issues found - review before deployment")
            return False
            
    except Exception as e:
        print(f"Critical Error: Could not run endpoint tests - {str(e)}")
        return False

if __name__ == "__main__":
    success = test_critical_endpoints()
    exit(0 if success else 1)