#!/usr/bin/env python3
"""
Test SQLite concurrent connection handling
"""

import sys
import threading
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_endpoint(url, test_id):
    """Test a single endpoint"""
    try:
        response = requests.get(f"{url}/health", timeout=10)
        if response.status_code == 200:
            return {"success": True, "test_id": test_id, "response_time": response.elapsed.total_seconds()}
        else:
            return {"success": False, "test_id": test_id, "status_code": response.status_code}
    except Exception as e:
        return {"success": False, "test_id": test_id, "error": str(e)}

def run_concurrent_test(base_url, num_users):
    """Run concurrent user test"""
    print(f"\n[Testing] {num_users} concurrent users against {base_url}")
    
    results = []
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_users) as executor:
        futures = [executor.submit(test_endpoint, base_url, i) for i in range(num_users)]
        
        for future in as_completed(futures):
            results.append(future.result())
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Analyze results
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    success_rate = len(successful) / len(results) * 100
    avg_response_time = sum(r.get("response_time", 0) for r in successful) / len(successful) if successful else 0
    
    print(f"Results: {len(successful)}/{len(results)} successful ({success_rate:.1f}%)")
    print(f"Average response time: {avg_response_time:.3f}s")
    print(f"Total test time: {total_time:.2f}s")
    
    if failed:
        print(f"Failures: {len(failed)}")
        for f in failed[:3]:  # Show first 3 failures
            if "error" in f:
                print(f"  - Test {f['test_id']}: {f['error']}")
            else:
                print(f"  - Test {f['test_id']}: HTTP {f.get('status_code', 'Unknown')}")
    
    return success_rate >= 95  # 95% success rate required

def main():
    print("SQLite Concurrent Connection Test")
    print("=" * 50)
    
    # Test different concurrency levels
    base_url = "http://localhost:8001"
    
    print(f"Testing against: {base_url}")
    
    # Quick connectivity test
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code != 200:
            print(f"[ERROR] Server not responding: HTTP {response.status_code}")
            return False
        print("[OK] Server is responding")
    except Exception as e:
        print(f"[ERROR] Cannot connect to server: {e}")
        print("Please start the server with: python app.py")
        return False
    
    # Test escalating concurrent users
    test_levels = [10, 25, 50, 75]
    all_passed = True
    
    for users in test_levels:
        passed = run_concurrent_test(base_url, users)
        if not passed:
            print(f"[FAIL] {users} concurrent users test failed")
            all_passed = False
            break
        else:
            print(f"[PASS] {users} concurrent users test passed")
        
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 50)
    if all_passed:
        print("[SUCCESS] All concurrent user tests passed!")
        print("SQLite optimization is working well.")
    else:
        print("[WARNING] Some tests failed.")
        print("Consider PostgreSQL migration for higher concurrency.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)