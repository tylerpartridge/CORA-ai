#!/usr/bin/env python3
"""
Test script to verify Voice Expense Entry activation
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths


import requests
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_TRANSCRIPT = "spent fifty dollars at home depot for lumber on the wilson job"

def test_voice_endpoint():
    """Test the voice expense endpoint"""
    print("Testing Voice Expense Entry activation...")
    print("-" * 50)
    
    # Test payload
    payload = {
        "transcript": TEST_TRANSCRIPT,
        "source": "test_script"
    }
    
    # Note: You'll need to add authentication headers if required
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # Make request
        response = requests.post(
            f"{BASE_URL}/api/expenses/voice",
            json=payload,
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("\n[SUCCESS] Voice Expense Entry is WORKING!")
                print(f"Created expense: ${result['expense']['amount_cents']/100:.2f} at {result['expense']['vendor']}")
            else:
                print("\n[ERROR] Voice processing failed:", result.get('error'))
        else:
            print(f"\n[ERROR] API returned error: {response.status_code}")
            
    except Exception as e:
        print(f"\n[ERROR] Error testing voice endpoint: {e}")
        print("\nPossible issues:")
        print("1. Server not running on port 8000")
        print("2. Authentication required")
        print("3. Endpoint not properly mounted")

def check_frontend_integration():
    """Check if frontend files are properly configured"""
    print("\n\nChecking Frontend Integration...")
    print("-" * 50)
    
    issues = []
    
    # Check if voice button is present in dashboard
    try:
        with open('web/templates/dashboard_unified.html', 'r') as f:
            content = f.read()
            
            if '.voice-button-container' in content:
                print("[OK] Voice button container found in dashboard")
            else:
                issues.append("Voice button container missing")
                
            if 'initVoiceButton()' in content:
                print("[OK] Voice button initialization found")
            else:
                issues.append("Voice button initialization missing")
                
            if "apiEndpoint: '/api/expenses/voice'" in content:
                print("[OK] Correct API endpoint configured")
            else:
                issues.append("API endpoint misconfigured")
                
    except Exception as e:
        issues.append(f"Could not read dashboard template: {e}")
    
    # Check backend route
    try:
        with open('routes/expenses.py', 'r') as f:
            content = f.read()
            
            if '@expense_router.post("/voice"' in content:
                print("[OK] Backend voice route exists")
            else:
                issues.append("Backend voice route missing")
                
    except Exception as e:
        issues.append(f"Could not read expenses routes: {e}")
    
    if issues:
        print("\n[ISSUES] Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n[SUCCESS] All frontend integrations look good!")

if __name__ == "__main__":
    check_frontend_integration()
    print("\n\nTo test the API endpoint, start the server and run:")
    print("python test_voice_activation.py --test-api")
    
    import sys
    if '--test-api' in sys.argv:
        test_voice_endpoint()