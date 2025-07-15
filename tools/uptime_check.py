#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/uptime_check.py
🎯 PURPOSE: Simple uptime monitoring for CORA production system
🔗 IMPORTS: requests, sys
📤 EXPORTS: Health check functions
"""

import requests
import sys
import time
from datetime import datetime

def check_health():
    """Check if the CORA system is healthy"""
    try:
        response = requests.get('https://coraai.tech/health', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                print(f"✅ CORA is healthy - {datetime.now().isoformat()}")
                return True
            else:
                print(f"❌ CORA returned unhealthy status - {datetime.now().isoformat()}")
                return False
        else:
            print(f"❌ CORA returned status {response.status_code} - {datetime.now().isoformat()}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ CORA health check failed: {e} - {datetime.now().isoformat()}")
        return False

def check_api_status():
    """Check the API status endpoint"""
    try:
        response = requests.get('https://coraai.tech/api/status', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"📊 API Status: {data.get('status')} | Uptime: {data.get('uptime')} | Version: {data.get('version')}")
            return True
        else:
            print(f"❌ API status check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API status check failed: {e}")
        return False

def main():
    """Main monitoring function"""
    print("🔍 CORA Production Health Check")
    print("=" * 40)
    
    # Check basic health
    health_ok = check_health()
    
    # Check API status
    api_ok = check_api_status()
    
    # Overall status
    if health_ok and api_ok:
        print("✅ All systems operational")
        sys.exit(0)
    else:
        print("❌ System issues detected")
        sys.exit(1)

if __name__ == "__main__":
    main() 