#!/usr/bin/env python3
"""
Test what actually fucking works
"""
import requests
import json

print("Testing what actually works...")
print("-" * 40)

endpoints = [
    ("Home Page", "GET", "/"),
    ("Signup Page", "GET", "/signup"),
    ("Login Page", "GET", "/login"),
    ("Signup API", "POST", "/api/auth/register"),
    ("Login API", "POST", "/login"),
    ("Onboarding V1", "GET", "/api/onboarding/checklist"),
    ("Onboarding V2", "GET", "/api/onboarding/v2/progress"),
    ("Chat Onboarding", "GET", "/api/onboarding/chat/context/test"),
    ("Expenses", "GET", "/api/expenses"),
    ("Stripe", "GET", "/api/integrations/stripe/status"),
    ("Dashboard", "GET", "/dashboard"),
]

for name, method, endpoint in endpoints:
    url = f"http://localhost:8001{endpoint}"
    try:
        if method == "GET":
            r = requests.get(url, timeout=2)
        else:
            r = requests.post(url, json={}, timeout=2)
        
        if r.status_code in [200, 201]:
            print(f"[OK] {name:20} - WORKS")
        elif r.status_code == 401:
            print(f"[?] {name:20} - Needs auth (probably works)")
        elif r.status_code == 404:
            print(f"[X] {name:20} - NOT FOUND")
        else:
            print(f"[X] {name:20} - Status {r.status_code}")
    except:
        print(f"[X] {name:20} - BROKEN")

print("-" * 40)
print("\nReality check complete.")