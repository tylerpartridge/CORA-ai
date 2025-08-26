#!/usr/bin/env python3

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

"""Test if CORA routes are working"""

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_routes():
    routes_to_test = [
        ("/", "Homepage"),
        ("/features", "Features page"),
        ("/pricing", "Pricing page"),
        ("/how-it-works", "How it works page"),
        ("/signup", "Signup page"),
        ("/login", "Login page")
    ]
    
    for route, name in routes_to_test:
        try:
            response = client.get(route)
            if response.status_code == 200:
                print(f"[OK] {name} ({route}): OK - {len(response.text)} bytes")
            else:
                print(f"[FAIL] {name} ({route}): Status {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {name} ({route}): ERROR - {e}")

if __name__ == "__main__":
    test_routes()