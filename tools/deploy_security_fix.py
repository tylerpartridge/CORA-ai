#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/deploy_security_fix.py
🎯 PURPOSE: Deploy security headers fix to production
🔗 IMPORTS: subprocess, os, sys
📤 EXPORTS: Deployment status
"""

import subprocess
import os
import sys

# Using the correct production IP from INFRASTRUCTURE.md
PRODUCTION_IP = "159.89.94.181"
PRODUCTION_DIR = "/var/www/cora/"

def deploy_security_fix():
    """Deploy security headers fix to production"""
    print("🔒 Deploying Security Headers Fix to Production")
    print(f"Server: root@{PRODUCTION_IP}")
    print(f"Directory: {PRODUCTION_DIR}")
    print("-" * 50)
    
    try:
        # First, check if middleware directory exists locally
        if not os.path.exists("middleware/security_headers_fixed.py"):
            print("❌ Error: middleware/security_headers_fixed.py not found!")
            return False
            
        print("📤 Step 1: Creating middleware directory on server...")
        subprocess.run([
            'ssh', f'root@{PRODUCTION_IP}', 
            f'mkdir -p {PRODUCTION_DIR}middleware'
        ], check=True)
        
        print("📤 Step 2: Uploading security headers fix...")
        subprocess.run([
            'scp', 'middleware/security_headers_fixed.py', 
            f'root@{PRODUCTION_IP}:{PRODUCTION_DIR}middleware/security_headers.py'
        ], check=True)
        
        print("📤 Step 3: Uploading entire middleware directory...")
        subprocess.run([
            'scp', '-r', 'middleware/', 
            f'root@{PRODUCTION_IP}:{PRODUCTION_DIR}'
        ], check=True)
        
        print("📤 Step 4: Uploading updated app.py...")
        subprocess.run([
            'scp', 'app.py', 
            f'root@{PRODUCTION_IP}:{PRODUCTION_DIR}'
        ], check=True)
        
        print("🔄 Step 5: Restarting PM2 process...")
        subprocess.run([
            'ssh', f'root@{PRODUCTION_IP}', 'pm2 restart cora'
        ], check=True)
        
        print("\n✅ Security fix deployed successfully!")
        print("🌐 Please verify at: https://coraai.tech")
        print("\n📋 To verify CSP headers are working:")
        print("1. Open browser developer tools (F12)")
        print("2. Go to Network tab")
        print("3. Reload https://coraai.tech")
        print("4. Click on the main document request")
        print("5. Check Response Headers for 'Content-Security-Policy'")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Deployment failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check SSH access: ssh root@{PRODUCTION_IP}")
        print("2. Verify IP address in INFRASTRUCTURE.md")
        print("3. Ensure SSH key is configured")
        return False
    except FileNotFoundError:
        print("\n❌ Error: SSH command not found!")
        print("This script needs to be run from a system with SSH installed.")
        print("On Windows, use WSL, Git Bash, or deploy from a Linux/Mac system.")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def check_files():
    """Check if required files exist"""
    print("🔍 Checking required files...")
    
    files_to_check = [
        "app.py",
        "middleware/security_headers_fixed.py",
        "middleware/__init__.py"
    ]
    
    all_exist = True
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - NOT FOUND")
            all_exist = False
    
    return all_exist

if __name__ == "__main__":
    print("🔒 CORA Security Headers Deployment Script")
    print("=" * 50)
    
    if not check_files():
        print("\n❌ Missing required files. Please ensure all files exist.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("⚠️  IMPORTANT: This will deploy to PRODUCTION")
    print(f"Server: {PRODUCTION_IP}")
    print("Domain: https://coraai.tech")
    print("=" * 50)
    
    response = input("\nProceed with deployment? (yes/no): ")
    
    if response.lower() == 'yes':
        deploy_security_fix()
    else:
        print("❌ Deployment cancelled.")