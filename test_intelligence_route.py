#!/usr/bin/env python3
"""
Test the intelligence orchestrator demo route
"""

import sys
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from app import app

def test_intelligence_demo():
    client = TestClient(app)
    
    print("Testing /api/intelligence/demo route...")
    
    try:
        response = client.get("/api/intelligence/demo")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS: Demo page loads correctly!")
            print(f"Content-Type: {response.headers.get('content-type', 'Not set')}")
            print(f"Content length: {len(response.content)} bytes")
            
            # Check if it's HTML
            if response.headers.get('content-type', '').startswith('text/html'):
                content = response.text
                if 'Intelligence Orchestration' in content:
                    print("✓ Page contains expected title")
                else:
                    print("✗ Page missing expected title")
                    
                if 'CORA' in content:
                    print("✓ Page contains CORA branding")
                else:
                    print("✗ Page missing CORA branding")
            
        else:
            print(f"ERROR: Status {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        
    print("\nTesting other intelligence routes...")
    
    # Test orchestration-demo (no auth required)
    try:
        response = client.get("/api/intelligence/orchestration-demo")
        print(f"orchestration-demo: {response.status_code}")
    except Exception as e:
        print(f"orchestration-demo error: {e}")

if __name__ == "__main__":
    test_intelligence_demo()