#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/deploy_production.py
🎯 PURPOSE: Production deployment script for CORA system
🔗 IMPORTS: os, subprocess, pathlib
📤 EXPORTS: Deployment status and configuration
"""

import os
import subprocess
import sys
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('sqlalchemy', 'sqlalchemy'),
        ('pydantic', 'pydantic'),
        ('python-multipart', 'multipart'),
        ('python-jose', 'jose'),
        ('passlib', 'passlib'),
        ('slowapi', 'slowapi')
    ]
    
    missing = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install " + " ".join(missing))
        return False
    
    print("✅ All dependencies installed")
    return True

def check_environment():
    """Check environment configuration"""
    required_files = [
        'data/cora.db',
        'web/templates/index.html',
        'app.py'
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        print(f"❌ Missing files: {', '.join(missing)}")
        return False
    
    print("✅ All required files present")
    return True

def check_database():
    """Check database connectivity"""
    try:
        from models import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database connectivity verified")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def deploy_to_digitalocean():
    """Deploy to existing DigitalOcean infrastructure"""
    print("\n🚀 Deploying to DigitalOcean (coraai.tech)...")
    print("IP: 159.203.183.48")
    print("Directory: /var/www/cora/")
    
    try:
        # Copy files to server
        print("📤 Uploading files...")
        subprocess.run([
            'scp', '-r', 'app.py', 'web/', 'root@159.203.183.48:/var/www/cora/'
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

def start_server():
    """Start the production server"""
    print("\n🚀 Starting CORA production server...")
    print("Server will be available at: http://localhost:8000")
    print("API docs at: http://localhost:8000/api/docs")
    print("Press Ctrl+C to stop")
    
    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

def main():
    """Main deployment function"""
    print("🏭 CORA PRODUCTION DEPLOYMENT")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "deploy":
        # Deploy to DigitalOcean
        checks = [
            ("Dependencies", check_dependencies),
            ("Environment", check_environment),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            print(f"\n🔍 Checking: {check_name}")
            print("-" * 30)
            if not check_func():
                all_passed = False
        
        if all_passed:
            print("\n✅ All checks passed! Deploying to production...")
            return deploy_to_digitalocean()
        else:
            print("\n❌ Some checks failed. Please fix issues before deployment.")
            return False
    else:
        # Local development mode
        checks = [
            ("Dependencies", check_dependencies),
            ("Environment", check_environment),
            ("Database", check_database),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            print(f"\n🔍 Checking: {check_name}")
            print("-" * 30)
            if not check_func():
                all_passed = False
        
        if all_passed:
            print("\n✅ All checks passed! Ready for local development.")
            start_server()
        else:
            print("\n❌ Some checks failed. Please fix issues before deployment.")
            return False
    
    return True

if __name__ == "__main__":
    main() 