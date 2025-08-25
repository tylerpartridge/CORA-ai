#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/diagnose_502_error.py
🎯 PURPOSE: Diagnose 502 error on production server
🔗 IMPORTS: subprocess, sys
📤 EXPORTS: Diagnostic results
"""

import subprocess
import sys

PRODUCTION_IP = "159.203.183.48"
PRODUCTION_DIR = "/var/www/cora/"

def run_ssh_command(command, description):
    """Run SSH command and return output"""
    print(f"\n📋 {description}...")
    print(f"Command: {command}")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            ['ssh', f'root@{PRODUCTION_IP}', command],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}")
            
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False, "", "Timeout"
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, "", str(e)

def diagnose_502_error():
    """Diagnose why the application is returning 502"""
    print("🔍 CORA 502 Error Diagnostics")
    print(f"Server: {PRODUCTION_IP}")
    print("=" * 60)
    
    # Step 1: Check PM2 status
    run_ssh_command("pm2 status", "Checking PM2 process status")
    
    # Step 2: Get PM2 logs (last 50 lines)
    run_ssh_command("pm2 logs cora --lines 50 --nostream", "Getting PM2 logs")
    
    # Step 3: Check if Python app can start manually
    print("\n🐍 Testing Python app directly...")
    run_ssh_command(
        f"cd {PRODUCTION_DIR} && python app.py 2>&1 | head -50",
        "Testing direct Python execution"
    )
    
    # Step 4: Check for missing dependencies
    run_ssh_command(
        f"cd {PRODUCTION_DIR} && pip list | grep -E 'fastapi|uvicorn|pydantic'",
        "Checking key dependencies"
    )
    
    # Step 5: Check file permissions
    run_ssh_command(
        f"ls -la {PRODUCTION_DIR}middleware/",
        "Checking middleware directory permissions"
    )
    
    # Step 6: Check if security_headers.py exists and is valid
    run_ssh_command(
        f"ls -la {PRODUCTION_DIR}middleware/security_headers.py",
        "Checking security headers file"
    )
    
    # Step 7: Test imports
    run_ssh_command(
        f"cd {PRODUCTION_DIR} && python -c 'from middleware.security_headers import setup_security_headers; print(\"Import successful\")'",
        "Testing security headers import"
    )
    
    # Step 8: Check nginx error logs
    run_ssh_command(
        "tail -30 /var/log/nginx/error.log",
        "Checking Nginx error logs"
    )
    
    # Step 9: Check system resources
    run_ssh_command(
        "free -h && df -h /",
        "Checking memory and disk space"
    )
    
    print("\n" + "=" * 60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    print("\n🔧 Common 502 causes to check:")
    print("1. Python import errors (check logs above)")
    print("2. Missing dependencies (pip install -r requirements.txt)")
    print("3. Port mismatch (app running on different port than nginx expects)")
    print("4. Syntax errors in Python code")
    print("5. Missing __init__.py files in directories")
    print("\n💡 Quick fixes to try:")
    print("1. Create __init__.py: touch /var/www/cora/middleware/__init__.py")
    print("2. Install deps: cd /var/www/cora && pip install -r requirements.txt")
    print("3. Fix permissions: chown -R www-data:www-data /var/www/cora/")
    print("4. Restart PM2: pm2 restart cora")

def create_quick_fix_script():
    """Create a script with common fixes"""
    fix_script = """#!/bin/bash
# Quick fix script for common 502 issues

echo "🔧 Running quick fixes..."

# 1. Create __init__.py files
echo "Creating __init__.py files..."
touch /var/www/cora/middleware/__init__.py
touch /var/www/cora/models/__init__.py
touch /var/www/cora/routes/__init__.py
touch /var/www/cora/services/__init__.py
touch /var/www/cora/dependencies/__init__.py

# 2. Fix permissions
echo "Fixing permissions..."
chown -R www-data:www-data /var/www/cora/

# 3. Install/update dependencies
echo "Installing dependencies..."
cd /var/www/cora/
pip install fastapi uvicorn pydantic python-multipart python-jose passlib bcrypt sqlalchemy

# 4. Test the app
echo "Testing app startup..."
python app.py &
sleep 5
kill $!

# 5. Restart PM2
echo "Restarting PM2..."
pm2 restart cora
pm2 logs cora --lines 20

echo "✅ Quick fixes applied!"
"""
    
    with open("tools/quick_fix_502.sh", "w") as f:
        f.write(fix_script)
    
    print("\n📝 Created quick fix script: tools/quick_fix_502.sh")
    print("To run it on the server:")
    print(f"1. scp tools/quick_fix_502.sh root@{PRODUCTION_IP}:/tmp/")
    print(f"2. ssh root@{PRODUCTION_IP} 'bash /tmp/quick_fix_502.sh'")

if __name__ == "__main__":
    print("🚨 502 Error Diagnostic Tool")
    print("This will help identify why the app is not responding")
    print("-" * 60)
    
    try:
        diagnose_502_error()
        create_quick_fix_script()
    except FileNotFoundError:
        print("\n❌ SSH command not found!")
        print("Please run this from a system with SSH installed.")
        print("On Windows, use WSL or Git Bash.")
    except KeyboardInterrupt:
        print("\n❌ Diagnostic cancelled by user")
        sys.exit(1)