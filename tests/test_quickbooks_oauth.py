#!/usr/bin/env python3
"""
Test script for QuickBooks OAuth flow
Run this to verify your QuickBooks app configuration
"""

import os
import sys
import base64
from urllib.parse import urlencode
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_oauth_configuration():
    """Test QuickBooks OAuth configuration"""
    print("🔍 Testing QuickBooks OAuth Configuration...\n")
    
    # Check required environment variables
    required_vars = [
        "QUICKBOOKS_CLIENT_ID",
        "QUICKBOOKS_CLIENT_SECRET",
        "QUICKBOOKS_BASIC_AUTH",
        "QUICKBOOKS_REDIRECT_URI",
        "QUICKBOOKS_ENVIRONMENT"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith("your_"):
            missing_vars.append(var)
            print(f"❌ {var}: Missing or not configured")
        else:
            if var == "QUICKBOOKS_CLIENT_SECRET" or var == "QUICKBOOKS_BASIC_AUTH":
                print(f"✅ {var}: ********** (hidden)")
            else:
                print(f"✅ {var}: {value}")
    
    if missing_vars:
        print(f"\n❌ Missing configuration for: {', '.join(missing_vars)}")
        print("\n📋 Setup Instructions:")
        print("1. Copy .env.quickbooks.example to .env")
        print("2. Fill in your QuickBooks app credentials")
        print("3. Generate Basic Auth: echo -n 'CLIENT_ID:CLIENT_SECRET' | base64")
        return False
    
    # Verify Basic Auth encoding
    print("\n🔐 Verifying Basic Auth encoding...")
    client_id = os.getenv("QUICKBOOKS_CLIENT_ID")
    client_secret = os.getenv("QUICKBOOKS_CLIENT_SECRET")
    expected_auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    actual_auth = os.getenv("QUICKBOOKS_BASIC_AUTH")
    
    if expected_auth == actual_auth:
        print("✅ Basic Auth correctly encoded")
    else:
        print("❌ Basic Auth encoding mismatch")
        print("   Expected (based on CLIENT_ID:CLIENT_SECRET):", expected_auth[:10] + "...")
        print("   Actual:", actual_auth[:10] + "...")
        return False
    
    # Generate OAuth URL
    print("\n🔗 Generating OAuth URL...")
    auth_url = os.getenv("QUICKBOOKS_AUTH_URL", "https://appcenter.intuit.com/connect/oauth2")
    params = {
        "client_id": client_id,
        "response_type": "code",
        "scope": "com.intuit.quickbooks.accounting",
        "redirect_uri": os.getenv("QUICKBOOKS_REDIRECT_URI"),
        "state": "test_user_123"  # CSRF protection
    }
    
    full_url = f"{auth_url}?{urlencode(params)}"
    print(f"✅ OAuth URL generated successfully")
    print(f"\n📋 Test OAuth Flow:")
    print(f"1. Open this URL in your browser:")
    print(f"   {full_url[:100]}...")
    print(f"\n2. Log in with your QuickBooks account")
    print(f"3. Authorize the CORA app")
    print(f"4. You'll be redirected to: {params['redirect_uri']}")
    print(f"5. The redirect URL will contain 'code' and 'realmId' parameters")
    
    # Check API URLs
    print(f"\n🌍 Environment: {os.getenv('QUICKBOOKS_ENVIRONMENT', 'sandbox')}")
    if os.getenv("QUICKBOOKS_ENVIRONMENT") == "production":
        print("   API URL: https://quickbooks.api.intuit.com")
        print("   User Info URL: https://accounts.platform.intuit.com")
    else:
        print("   API URL: https://sandbox-quickbooks.api.intuit.com")
        print("   User Info URL: https://sandbox-accounts.platform.intuit.com")
    
    print("\n✅ QuickBooks OAuth configuration is valid!")
    return True

def test_sandbox_connection():
    """Test connection to QuickBooks sandbox"""
    print("\n🧪 Testing QuickBooks Sandbox Connection...")
    
    # This would require a valid access token
    # For now, just verify the URLs are reachable
    import requests
    
    try:
        # Test OAuth endpoint
        oauth_url = "https://oauth.platform.intuit.com/.well-known/openid_configuration"
        response = requests.get(oauth_url, timeout=5)
        if response.status_code == 200:
            print("✅ OAuth endpoint is reachable")
        else:
            print(f"❌ OAuth endpoint returned: {response.status_code}")
            
        # Test sandbox API endpoint (will return 401 without auth, which is expected)
        api_url = "https://sandbox-quickbooks.api.intuit.com/v3/company/123/companyinfo/123"
        response = requests.get(api_url, timeout=5)
        if response.status_code == 401:
            print("✅ Sandbox API endpoint is reachable (401 expected without auth)")
        else:
            print(f"❌ Unexpected response from sandbox API: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 QuickBooks Integration Test Suite")
    print("=" * 60)
    
    # Test OAuth configuration
    config_valid = test_oauth_configuration()
    
    # Test sandbox connection
    if config_valid:
        test_sandbox_connection()
    
    print("\n" + "=" * 60)
    if config_valid:
        print("✅ QuickBooks integration is ready for testing!")
        print("\n📋 Next Steps:")
        print("1. Click the OAuth URL above to test the authorization flow")
        print("2. After authorization, test the /api/integrations/quickbooks/status endpoint")
        print("3. Try syncing an expense with /api/integrations/quickbooks/sync")
    else:
        print("❌ Please fix the configuration issues before proceeding")
    print("=" * 60)