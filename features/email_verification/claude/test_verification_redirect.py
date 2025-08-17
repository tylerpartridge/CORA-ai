#!/usr/bin/env python3
"""Test that email verification redirects to onboarding"""

import sys
import os

def test_redirect():
    print("Testing email verification redirect...")
    
    # Check the code
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find the verify_email_endpoint function
    if 'def verify_email_endpoint' not in content:
        print("[FAIL] verify_email_endpoint not found")
        return False
        
    # Check what happens after successful verification
    lines = content.split('\n')
    in_verify_func = False
    for i, line in enumerate(lines):
        if 'def verify_email_endpoint' in line:
            in_verify_func = True
        elif in_verify_func and 'if verification_successful:' in line:
            # Check next few lines for redirect
            for j in range(i+1, min(i+10, len(lines))):
                if 'RedirectResponse(url="/onboarding"' in lines[j]:
                    print("[OK] Verification redirects to /onboarding")
                    return True
                elif 'RedirectResponse(url="/login"' in lines[j]:
                    print("[FAIL] Verification redirects to /login (WRONG!)")
                    return False
    
    print("[WARN] Could not determine redirect target")
    return False

if __name__ == "__main__":
    if test_redirect():
        print("\nFIXED: Email verification now redirects to /onboarding")
    else:
        print("\nERROR: Redirect still broken")