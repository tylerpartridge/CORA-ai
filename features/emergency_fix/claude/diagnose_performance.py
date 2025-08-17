#!/usr/bin/env python3
"""
Quick performance diagnostic - what's making pages slow?
"""

import time
import requests

print("Testing page load times...")
print("-" * 40)

pages = [
    ("Home", "http://localhost:8000/"),
    ("Features", "http://localhost:8000/features"),
    ("Pricing", "http://localhost:8000/pricing"),
    ("About", "http://localhost:8000/about"),
]

for name, url in pages:
    try:
        start = time.time()
        response = requests.get(url, timeout=10)
        load_time = time.time() - start
        
        status = "✓" if response.status_code == 200 else "✗"
        print(f"{status} {name:15} {load_time:.2f}s - Status: {response.status_code}")
        
        if load_time > 1.0:
            print(f"  ⚠️ SLOW! Should be < 0.5s")
            
    except requests.exceptions.ConnectionError:
        print(f"✗ {name:15} - Cannot connect (is server running?)")
    except Exception as e:
        print(f"✗ {name:15} - Error: {e}")

print("-" * 40)
print("\nIf pages are slow, likely causes:")
print("1. Too many middleware layers")
print("2. Database queries on every page")
print("3. Redis/caching misconfigured")
print("4. Multiple server instances fighting")