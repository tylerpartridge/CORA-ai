#!/usr/bin/env python3
"""
Test script to check CORA endpoints
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths

import requests
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_endpoint(endpoint, expected_status=200):
    """Test a single endpoint"""
    url = f"http://127.0.0.1:8000{endpoint}"
    try:
        response = requests.get(url, timeout=10)
        success = response.status_code == expected_status
        return {
            "endpoint": endpoint,
            "status_code": response.status_code,
            "success": success,
            "response_size": len(response.content),
            "error": None
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "status_code": None,
            "success": False,
            "response_size": 0,
            "error": str(e)
        }

def main():
    """Test main CORA endpoints"""
    print("Testing CORA System Endpoints")
    print("=" * 50)
    
    # Test endpoints
    endpoints = [
        "/health",
        "/",
        "/features",
        "/pricing", 
        "/how-it-works",
        "/api/status",
        "/login",
        "/signup",
    ]
    
    results = []
    
    # Test each endpoint
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_endpoint = {
            executor.submit(test_endpoint, endpoint): endpoint 
            for endpoint in endpoints
        }
        
        for future in as_completed(future_to_endpoint):
            result = future.result()
            results.append(result)
            
            # Print immediate result
            status_icon = "OK" if result["success"] else "FAIL"
            print(f"{status_icon} {result['endpoint']:<20} | Status: {result['status_code']:<3} | Size: {result['response_size']:<6} bytes")
            
            if result["error"]:
                print(f"   Error: {result['error']}")
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    print("\nSummary:")
    print(f"Working: {successful}/{total}")
    print(f"Broken:  {total - successful}/{total}")
    
    if successful == total:
        print("\nAll endpoints are working!")
    else:
        print(f"\n{total - successful} endpoints need attention")
        
    return 0 if successful == total else 1

if __name__ == "__main__":
    sys.exit(main())