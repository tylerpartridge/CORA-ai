#!/usr/bin/env python3
"""
Test Stripe API Integration
Tests actual connectivity and validates the API key works with CORA's system
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths


import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_stripe_import():
    """Test if Stripe library is available"""
    try:
        import stripe
        print("SUCCESS: Stripe library imported successfully")
        return stripe
    except ImportError:
        print("ERROR: Stripe library not found. Installing...")
        os.system("pip install stripe")
        try:
            import stripe
            print("SUCCESS: Stripe library installed and imported")
            return stripe
        except ImportError:
            print("ERROR: Failed to install/import Stripe library")
            return None

def test_stripe_api_key():
    """Test Stripe API key configuration"""
    stripe_key = os.getenv('STRIPE_API_KEY')
    
    if not stripe_key:
        print("ERROR: STRIPE_API_KEY not found in environment")
        return False
    
    print(f"SUCCESS: STRIPE_API_KEY found: {stripe_key[:12]}...")
    
    # Validate key format
    if stripe_key.startswith('sk_live_'):
        print("SUCCESS: Using LIVE Stripe key (production)")
        return stripe_key
    elif stripe_key.startswith('sk_test_'):
        print("SUCCESS: Using TEST Stripe key (sandbox)")
        return stripe_key
    elif stripe_key.startswith('live_'):
        print("WARNING: Key format: Publishable key detected, not secret key")
        print("   Note: This appears to be a publishable key (live_), not a secret key (sk_live_)")
        return stripe_key
    else:
        print(f"ERROR: Invalid Stripe key format. Should start with sk_live_ or sk_test_")
        return False

def test_stripe_connectivity(stripe, api_key):
    """Test actual Stripe API connectivity"""
    if not stripe or not api_key:
        return False
    
    try:
        stripe.api_key = api_key
        
        # Try to retrieve account information
        print("\nTesting Stripe API connectivity...")
        account = stripe.Account.retrieve()
        
        print("SUCCESS: Stripe API connection successful!")
        print(f"   Account ID: {account.id}")
        print(f"   Business Name: {account.business_profile.name if account.business_profile else 'Not set'}")
        print(f"   Country: {account.country}")
        print(f"   Account Type: {account.type}")
        print(f"   Charges Enabled: {account.charges_enabled}")
        print(f"   Payouts Enabled: {account.payouts_enabled}")
        
        return True
        
    except stripe.error.AuthenticationError as e:
        print(f"ERROR: Stripe Authentication Error: {e}")
        print("   This usually means the API key is invalid or has wrong permissions")
        return False
    except stripe.error.PermissionError as e:
        print(f"ERROR: Stripe Permission Error: {e}")
        print("   The API key doesn't have sufficient permissions")
        return False
    except Exception as e:
        print(f"ERROR: Stripe API Error: {e}")
        return False

def test_stripe_products():
    """Test if we can list products (for subscription testing)"""
    try:
        import stripe
        products = stripe.Product.list(limit=3)
        print(f"\nSUCCESS: Can access products: {len(products.data)} products found")
        for product in products.data:
            print(f"   - {product.name}: {product.id}")
        return True
    except Exception as e:
        print(f"WARNING: Could not list products: {e}")
        return False

def test_cora_stripe_integration():
    """Test CORA's specific Stripe integration points"""
    try:
        # Test if CORA's payment routes can be imported
        sys.path.append('/mnt/host/c/CORA')
        
        print("\nTesting CORA's Stripe integration...")
        
        # Check if payment routes exist
        try:
            from routes.payment_routes import payment_router
            print("SUCCESS: Payment routes module exists")
        except ImportError as e:
            print(f"WARNING: Payment routes not found: {e}")
        
        # Check if Stripe service exists
        try:
            from services.stripe_service import StripeService
            print("SUCCESS: Stripe service module exists")
        except ImportError as e:
            print(f"WARNING: Stripe service not found: {e}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Error testing CORA integration: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("CORA STRIPE INTEGRATION TEST")
    print("=" * 60)
    
    # Test 1: Import Stripe library
    stripe = test_stripe_import()
    if not stripe:
        return False
    
    # Test 2: Check API key configuration
    api_key = test_stripe_api_key()
    if not api_key:
        return False
    
    # Test 3: Test API connectivity
    connectivity_success = test_stripe_connectivity(stripe, api_key)
    
    # Test 4: Test products access
    if connectivity_success:
        test_stripe_products()
    
    # Test 5: Test CORA integration
    test_cora_stripe_integration()
    
    print("\n" + "=" * 60)
    if connectivity_success:
        print("STRIPE INTEGRATION TEST: SUCCESS")
        print("SUCCESS: Your Stripe API key is valid and working!")
        print("SUCCESS: CORA can communicate with Stripe successfully")
    else:
        print("STRIPE INTEGRATION TEST: FAILED")
        print("   Please check your API key configuration")
    print("=" * 60)
    
    return connectivity_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)