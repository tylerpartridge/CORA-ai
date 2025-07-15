#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/deploy_simple.py
🎯 PURPOSE: Simple deployment script for working CORA app
🔗 IMPORTS: subprocess, os
📤 EXPORTS: Deployment status
"""

import subprocess
import os
import sys

def deploy_to_digitalocean():
    """Deploy working app.py to DigitalOcean"""
    print("🚀 Deploying to DigitalOcean (coraai.tech)...")
    print("IP: 159.203.183.48")
    print("Directory: /var/www/cora/")
    
    try:
        # Copy app.py to server
        print("📤 Uploading app.py...")
        subprocess.run([
            'scp', 'app.py', 'root@159.203.183.48:/var/www/cora/'
        ], check=True)
        
        # Copy web directory
        print("📤 Uploading web directory...")
        subprocess.run([
            'scp', '-r', 'web/', 'root@159.203.183.48:/var/www/cora/'
        ], check=True)
        
        # Restart PM2 process
        print("🔄 Restarting PM2 process...")
        subprocess.run([
            'ssh', 'root@159.203.183.48', 'pm2 restart cora'
        ], check=True)
        
        print("✅ Deployment successful!")
        print("🌐 Check: https://coraai.tech")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_local_server():
    """Check if local server is running"""
    print("🔍 Checking local server...")
    try:
        result = subprocess.run(['curl', 'http://localhost:8000/health'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and "healthy" in result.stdout:
            print("✅ Local server is running")
            return True
        else:
            print("❌ Local server not responding")
            return False
    except Exception as e:
        print(f"❌ Cannot check local server: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_local_server()
    else:
        deploy_to_digitalocean() 