#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/deploy_full.py
🎯 PURPOSE: Full deployment script including middleware security fix
🔗 IMPORTS: subprocess, os, sys
📤 EXPORTS: Deployment status
"""

import subprocess
import os
import sys
from datetime import datetime

# Production server details from INFRASTRUCTURE.md
PRODUCTION_IP = "159.89.94.181"
PRODUCTION_DIR = "/var/www/cora/"

def deploy_to_production():
    """Deploy complete application including security fixes to production"""
    print("🚀 CORA Full Deployment to Production")
    print(f"Server: root@{PRODUCTION_IP}")
    print(f"Directory: {PRODUCTION_DIR}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    # Directories and files to deploy
    items_to_deploy = [
        ("app.py", "file"),
        ("web/", "directory"),
        ("middleware/", "directory"),
        ("models/", "directory"),
        ("routes/", "directory"),
        ("services/", "directory"),
        ("dependencies/", "directory"),
        ("requirements.txt", "file"),
        (".env.example", "file")
    ]
    
    try:
        # Step 1: Create necessary directories on server
        print("\n📁 Step 1: Creating directories on server...")
        directories = [item[0] for item in items_to_deploy if item[1] == "directory"]
        for directory in directories:
            print(f"   Creating {PRODUCTION_DIR}{directory}")
            subprocess.run([
                'ssh', f'root@{PRODUCTION_IP}', 
                f'mkdir -p {PRODUCTION_DIR}{directory}'
            ], check=True)
        
        # Step 2: Deploy files and directories
        print("\n📤 Step 2: Deploying files and directories...")
        for item, item_type in items_to_deploy:
            if os.path.exists(item):
                print(f"   Uploading {item}...")
                if item_type == "directory":
                    subprocess.run([
                        'scp', '-r', item, 
                        f'root@{PRODUCTION_IP}:{PRODUCTION_DIR}'
                    ], check=True)
                else:
                    subprocess.run([
                        'scp', item, 
                        f'root@{PRODUCTION_IP}:{PRODUCTION_DIR}'
                    ], check=True)
            else:
                print(f"   ⚠️  Skipping {item} (not found locally)")
        
        # Step 3: Special handling for security headers fix
        print("\n🔒 Step 3: Applying security headers fix...")
        if os.path.exists("middleware/security_headers_fixed.py"):
            print("   Copying security_headers_fixed.py as security_headers.py...")
            subprocess.run([
                'scp', 'middleware/security_headers_fixed.py', 
                f'root@{PRODUCTION_IP}:{PRODUCTION_DIR}middleware/security_headers.py'
            ], check=True)
        
        # Step 4: Set permissions
        print("\n🔐 Step 4: Setting permissions...")
        subprocess.run([
            'ssh', f'root@{PRODUCTION_IP}', 
            f'chown -R www-data:www-data {PRODUCTION_DIR}'
        ], check=True)
        
        # Step 5: Install/update requirements
        print("\n📦 Step 5: Installing requirements...")
        subprocess.run([
            'ssh', f'root@{PRODUCTION_IP}', 
            f'cd {PRODUCTION_DIR} && pip install -r requirements.txt'
        ], check=True)
        
        # Step 6: Restart application
        print("\n🔄 Step 6: Restarting application...")
        subprocess.run([
            'ssh', f'root@{PRODUCTION_IP}', 'pm2 restart cora'
        ], check=True)
        
        # Step 7: Check application status
        print("\n✅ Step 7: Checking application status...")
        result = subprocess.run([
            'ssh', f'root@{PRODUCTION_IP}', 'pm2 status'
        ], capture_output=True, text=True)
        print(result.stdout)
        
        print("\n" + "=" * 60)
        print("✅ Deployment completed successfully!")
        print("\n🌐 Please verify:")
        print("1. Landing page: https://coraai.tech")
        print("2. API health: https://coraai.tech/api/health")
        print("\n📋 To verify CSP headers:")
        print("   curl -I https://coraai.tech | grep -i content-security-policy")
        print("=" * 60)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Deployment failed: {e}")
        print("\n🔧 Troubleshooting steps:")
        print(f"1. Test SSH connection: ssh root@{PRODUCTION_IP}")
        print("2. Check if the server IP has changed")
        print("3. Verify your SSH key is authorized")
        print("4. Check server disk space: df -h")
        return False
    except FileNotFoundError:
        print("\n❌ Error: SSH/SCP commands not found!")
        print("This script requires SSH to be installed.")
        print("On Windows, use WSL, Git Bash, or PuTTY.")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def verify_local_files():
    """Verify required files exist locally"""
    print("🔍 Verifying local files...")
    
    critical_files = [
        "app.py",
        "middleware/security_headers_fixed.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in critical_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️  Missing {len(missing_files)} critical files!")
        return False
    
    return True

def main():
    """Main deployment function"""
    print("🚀 CORA Production Deployment Script")
    print("=" * 60)
    print("This script will deploy the complete application to production")
    print("including the CSP security headers fix.")
    print("=" * 60)
    
    # Verify files
    if not verify_local_files():
        print("\n❌ Cannot proceed without critical files.")
        sys.exit(1)
    
    # Confirm deployment
    print(f"\n⚠️  PRODUCTION DEPLOYMENT WARNING")
    print(f"Server: {PRODUCTION_IP} (coraai.tech)")
    print("This will update the live production system!")
    print("-" * 60)
    
    response = input("\nProceed with deployment? (yes/no): ")
    
    if response.lower() == 'yes':
        deploy_to_production()
    else:
        print("❌ Deployment cancelled.")

if __name__ == "__main__":
    main()