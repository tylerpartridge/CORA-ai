#!/usr/bin/env python
"""Quick server test script"""
import requests
import sys

def test_server():
    print("Testing CORA server at http://localhost:8000...")
    
    try:
        # Test landing page
        response = requests.get("http://localhost:8000", timeout=5)
        print(f"[OK] Landing page: {response.status_code}")
        
        # Test API health
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        print(f"[OK] API health: {response.status_code}")
        
        # Test signup page
        response = requests.get("http://localhost:8000/signup", timeout=5)
        print(f"[OK] Signup page: {response.status_code}")
        
        # Test login page
        response = requests.get("http://localhost:8000/login", timeout=5)
        print(f"[OK] Login page: {response.status_code}")
        
        print("\nServer is running and responding!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("[FAIL] Cannot connect to server at http://localhost:8000")
        print("  Please ensure the server is running: python app.py")
        return False
    except requests.exceptions.Timeout:
        print("[FAIL] Server is not responding (timeout)")
        return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)