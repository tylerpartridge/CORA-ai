#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/test_all_endpoints.py
🎯 PURPOSE: Test all API endpoints to diagnose 502 issues
🔗 IMPORTS: subprocess
📤 EXPORTS: Endpoint test results
"""

import subprocess
import json

PRODUCTION_IP = "159.203.183.48"

def test_endpoints():
    """Test various endpoints to see what's working"""
    print("🔍 Testing all CORA endpoints...")
    print(f"Server: {PRODUCTION_IP}")
    print("-" * 50)
    
    # Endpoints to test
    endpoints = [
        ("http://localhost:8000/", "Root (localhost:8000)"),
        ("http://localhost:8000/health", "Health (localhost:8000)"),
        ("http://localhost:8000/api/status", "API Status (localhost:8000)"),
        ("http://localhost:8000/docs", "API Docs (localhost:8000)"),
        ("http://localhost/", "Root (through nginx)"),
        ("http://localhost/health", "Health (through nginx)"),
        ("http://localhost/api/status", "API Status (through nginx)"),
    ]
    
    for endpoint, description in endpoints:
        print(f"\n📌 Testing {description}...")
        command = f"curl -s -o /dev/null -w '%{{http_code}}' {endpoint} || echo 'Failed'"
        
        try:
            result = subprocess.run(
                ['ssh', f'root@{PRODUCTION_IP}', command],
                capture_output=True,
                text=True
            )
            status_code = result.stdout.strip()
            
            if status_code == "200":
                print(f"✅ {description}: {status_code} OK")
            elif status_code == "502":
                print(f"❌ {description}: {status_code} Bad Gateway")
            elif status_code == "404":
                print(f"⚠️  {description}: {status_code} Not Found")
            else:
                print(f"⚠️  {description}: {status_code}")
                
        except Exception as e:
            print(f"Failed to test: {e}")
    
    # Also check if the app is actually listening
    print("\n📌 Checking app process...")
    try:
        result = subprocess.run(
            ['ssh', f'root@{PRODUCTION_IP}', "ps aux | grep 'python.*app.py' | grep -v grep"],
            capture_output=True,
            text=True
        )
        if result.stdout:
            print("✅ Python app process found:")
            print(result.stdout)
        else:
            print("❌ No Python app process found!")
    except Exception as e:
        print(f"Failed: {e}")
    
    # Check PM2 logs for recent errors
    print("\n📌 Recent PM2 errors...")
    try:
        result = subprocess.run(
            ['ssh', f'root@{PRODUCTION_IP}', "pm2 logs cora --err --lines 10 --nostream"],
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
    except Exception as e:
        print(f"Failed: {e}")

def quick_fix_app_startup():
    """Quick fix to ensure app starts on correct port"""
    print("\n🔧 Applying quick startup fix...")
    
    commands = [
        # 1. Stop current PM2 process
        ("pm2 stop cora", "Stopping current process"),
        
        # 2. Check if port 8000 is in use
        ("lsof -i :8000 || echo 'Port 8000 is free'", "Checking port 8000"),
        
        # 3. Start app directly to test
        ("cd /var/www/cora && timeout 10 python3 app.py || echo 'App startup test complete'", "Testing direct startup"),
        
        # 4. Start with PM2 using uvicorn
        ("cd /var/www/cora && pm2 delete cora; pm2 start 'uvicorn app:app --host 0.0.0.0 --port 8000' --name cora", "Starting with uvicorn"),
        
        # 5. Check status
        ("pm2 status", "PM2 status"),
        
        # 6. Test health endpoint
        ("sleep 3 && curl http://localhost:8000/health", "Testing health endpoint")
    ]
    
    for command, description in commands:
        print(f"\n📌 {description}...")
        try:
            result = subprocess.run(
                ['ssh', f'root@{PRODUCTION_IP}', command],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.stdout:
                print(result.stdout)
            if result.stderr and "Warning" not in result.stderr and "Terminated" not in result.stderr:
                print(f"Error: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("Command timed out (expected for startup test)")
        except Exception as e:
            print(f"Failed: {e}")

if __name__ == "__main__":
    test_endpoints()
    print("\n" + "=" * 50)
    response = input("\nApply quick startup fix? (yes/no): ")
    if response.lower() == 'yes':
        quick_fix_app_startup()