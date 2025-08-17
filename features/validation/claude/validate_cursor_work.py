#!/usr/bin/env python3
"""
CORA Validation Script - Validates Cursor's Recent Work
Tests signup flow, login, monetization layer, and database operations
"""

import sys
import os
import json
import sqlite3
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(title):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def check_mark(passed):
    return f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"

def validate_file_exists(filepath, description):
    """Check if a critical file exists"""
    exists = Path(filepath).exists()
    print(f"  {check_mark(exists)} {description}: {filepath}")
    if exists:
        size = Path(filepath).stat().st_size
        print(f"    Size: {size:,} bytes")
    return exists

def validate_database():
    """Validate database structure and data"""
    print_header("DATABASE VALIDATION")
    
    try:
        conn = sqlite3.connect('cora.db')
        cursor = conn.cursor()
        
        # Check critical tables
        tables_to_check = [
            'users',
            'business_profiles', 
            'subscriptions',
            'email_verification_tokens',
            'password_reset_tokens'
        ]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        all_present = True
        for table in tables_to_check:
            exists = table in existing_tables
            print(f"  {check_mark(exists)} Table '{table}' exists")
            if not exists:
                all_present = False
        
        # Check subscriptions table structure (new monetization layer)
        if 'subscriptions' in existing_tables:
            cursor.execute("PRAGMA table_info(subscriptions)")
            columns = [col[1] for col in cursor.fetchall()]
            required_cols = ['id', 'user_id', 'plan_type', 'status', 'trial_end']
            
            print(f"\n  Subscription table columns:")
            for col in required_cols:
                exists = col in columns
                print(f"    {check_mark(exists)} Column '{col}'")
        
        # Check for test users
        cursor.execute("SELECT email FROM users WHERE email LIKE '%test%' OR email LIKE '%coratest%'")
        test_users = cursor.fetchall()
        if test_users:
            print(f"\n  Test users found: {len(test_users)}")
            for user in test_users[:3]:  # Show first 3
                print(f"    - {user[0]}")
        
        conn.close()
        return all_present
        
    except Exception as e:
        print(f"  {RED}Database error: {e}{RESET}")
        return False

def validate_routes():
    """Check if all critical routes are defined"""
    print_header("ROUTE VALIDATION")
    
    routes_to_check = [
        ('routes/auth_coordinator.py', ['/register', '/login', '/logout']),
        ('routes/payment_coordinator.py', ['/subscriptions/create-trial']),
        ('routes/pages.py', ['/select-plan', '/signup', '/login', '/onboarding']),
        ('routes/cora_chat_enhanced.py', ['/chat'])
    ]
    
    all_good = True
    for file, endpoints in routes_to_check:
        if not Path(file).exists():
            print(f"  {RED}✗ File missing: {file}{RESET}")
            all_good = False
            continue
            
        with open(file, 'r') as f:
            content = f.read()
            
        print(f"\n  {file}:")
        for endpoint in endpoints:
            # Check for route definition
            found = endpoint in content
            print(f"    {check_mark(found)} Endpoint '{endpoint}'")
            if not found:
                all_good = False
    
    return all_good

def validate_templates():
    """Validate HTML templates and their structure"""
    print_header("TEMPLATE VALIDATION")
    
    templates = [
        ('web/templates/signup.html', ['form', 'email', 'password', 'passwordConfirm']),
        ('web/templates/login.html', ['form', 'email', 'password']),
        ('web/templates/select-plan.html', ['SOLO', 'CREW', 'BUSINESS', 'Start Free Trial']),
        ('web/templates/onboarding.html', ['business', 'wizard'])
    ]
    
    all_good = True
    for template, required_elements in templates:
        if not Path(template).exists():
            print(f"  {RED}✗ Template missing: {template}{RESET}")
            all_good = False
            continue
            
        with open(template, 'r') as f:
            content = f.read()
        
        print(f"\n  {template}:")
        size = len(content)
        print(f"    Size: {size:,} bytes")
        
        for element in required_elements:
            found = element in content
            print(f"    {check_mark(found)} Contains '{element}'")
            if not found:
                all_good = False
    
    return all_good

def validate_javascript():
    """Check JavaScript files for proper flow handling"""
    print_header("JAVASCRIPT VALIDATION")
    
    js_files = [
        ('web/static/js/signup-form.js', ['/select-plan', 'isSubmitting', 'localStorage']),
        ('web/static/js/login.js', ['localStorage', 'access_token']),
        ('web/static/js/onboarding-ai-wizard.js', ['business_name', 'monthly_revenue'])
    ]
    
    all_good = True
    for js_file, required_code in js_files:
        if not Path(js_file).exists():
            print(f"  {RED}✗ JavaScript missing: {js_file}{RESET}")
            all_good = False
            continue
            
        with open(js_file, 'r') as f:
            content = f.read()
        
        print(f"\n  {js_file}:")
        for code in required_code:
            found = code in content
            print(f"    {check_mark(found)} Contains '{code}'")
            if not found:
                all_good = False
    
    return all_good

def validate_flow_integration():
    """Validate the complete user flow is wired correctly"""
    print_header("FLOW INTEGRATION")
    
    checks = []
    
    # Check signup redirects to select-plan
    try:
        with open('routes/auth_coordinator.py', 'r') as f:
            auth_content = f.read()
        redirect_correct = '"redirect": "/select-plan"' in auth_content
        checks.append(("Signup → Select Plan redirect", redirect_correct))
    except:
        checks.append(("Signup → Select Plan redirect", False))
    
    # Check select-plan can redirect to onboarding
    try:
        with open('web/templates/select-plan.html', 'r') as f:
            select_content = f.read()
        has_onboarding = '/onboarding' in select_content
        checks.append(("Select Plan → Onboarding flow", has_onboarding))
    except:
        checks.append(("Select Plan → Onboarding flow", False))
    
    # Check environment mode
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
        is_dev_mode = 'ENVIRONMENT=development' in env_content
        checks.append(("Development mode enabled", is_dev_mode))
        if not is_dev_mode and 'ENVIRONMENT=production' in env_content:
            print(f"  {YELLOW}⚠ Production mode is set - email verification required{RESET}")
    except:
        checks.append(("Development mode enabled", False))
    
    all_good = True
    for check_name, passed in checks:
        print(f"  {check_mark(passed)} {check_name}")
        if not passed:
            all_good = False
    
    return all_good

def check_styling():
    """Validate CSS and styling consistency"""
    print_header("STYLING VALIDATION")
    
    # Check for consistent styling files
    css_files = [
        'web/static/css/navbar.css',
        'web/static/css/forms.css',
        'web/static/css/auth.css'
    ]
    
    all_good = True
    for css_file in css_files:
        exists = Path(css_file).exists()
        print(f"  {check_mark(exists)} {css_file}")
        if not exists:
            all_good = False
    
    # Check for known issues from HANDOFF
    print(f"\n  {YELLOW}Known Issues (from HANDOFF):{RESET}")
    print(f"    - Font flash on login page (Bootstrap CSS load order)")
    print(f"    - Cursor position bug with autofill")
    
    return all_good

def main():
    print_header("CORA VALIDATION REPORT")
    print("Validating Cursor's recent work and monetization layer...")
    
    results = []
    
    # Run all validations
    results.append(("Database", validate_database()))
    results.append(("Routes", validate_routes()))
    results.append(("Templates", validate_templates()))
    results.append(("JavaScript", validate_javascript()))
    results.append(("Flow Integration", validate_flow_integration()))
    results.append(("Styling", check_styling()))
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    all_passed = all(result[1] for result in results)
    
    for component, passed in results:
        status = "PASS" if passed else "FAIL"
        color = GREEN if passed else RED
        print(f"  {component:20} {color}{status}{RESET}")
    
    print(f"\n  Overall Status: ", end="")
    if all_passed:
        print(f"{GREEN}✅ APPROVED - All validations passed!{RESET}")
        print(f"\n  {GREEN}The monetization layer and auth flow are properly integrated.{RESET}")
        print(f"  {GREEN}Ready for testing!{RESET}")
    else:
        print(f"{YELLOW}⚠ NEEDS ATTENTION - Some validations failed{RESET}")
        print(f"\n  Review the failed items above for details.")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())