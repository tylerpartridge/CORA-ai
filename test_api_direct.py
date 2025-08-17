#!/usr/bin/env python3
"""
Direct API Testing Script - Bypass Server Issues
Test profit intelligence endpoints directly
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths


import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from models import get_db, User
from services.profit_leak_detector import ProfitLeakDetector
from routes.profit_intelligence import get_profit_intelligence_summary

def test_direct_api():
    """Test profit intelligence API directly without HTTP"""
    print("Direct API Testing - Profit Intelligence")
    print("=" * 50)
    
    # Get database session
    db = next(get_db())
    
    # Get test user (Glen Day)
    user = db.query(User).filter(User.email == "glen.day@testcontractor.com").first()
    if not user:
        print("[ERROR] Test user glen.day@testcontractor.com not found")
        print("Run: python tools/add_test_data_for_profit_intelligence.py")
        return False
    
    print(f"[OK] Found test user: {user.email} (ID: {user.id})")
    
    try:
        # Test ProfitLeakDetector directly
        print("\n[Test 1] ProfitLeakDetector initialization...")
        detector = ProfitLeakDetector(db, user.id)
        print("[OK] ProfitLeakDetector created successfully")
        
        # Test basic analysis
        print("\n[Test 2] Basic profit analysis...")
        analysis = detector.analyze_profit_leaks(6)
        print(f"[OK] Basic analysis completed")
        print(f"   - Expenses: {analysis['summary']['expense_count']}")
        print(f"   - Quick wins: {len(analysis['quick_wins'])}")
        print(f"   - Potential savings: ${analysis['potential_savings']:.2f}")
        
        # Test cost forecasting
        print("\n[Test 3] Cost forecasting...")
        forecast = detector.predict_future_costs(3)
        if "error" in forecast:
            print(f"⚠️ Forecast warning: {forecast['error']}")
        else:
            print(f"[OK] Forecast completed - {forecast['confidence']} confidence")
        
        # Test vendor performance
        print("\n[Test 4] Vendor performance analysis...")
        vendor_perf = detector.analyze_vendor_performance()
        if "error" in vendor_perf:
            print(f"⚠️ Vendor analysis warning: {vendor_perf['error']}")
        else:
            print(f"[OK] Vendor analysis completed - {vendor_perf['analyzed_vendors']} vendors")
        
        # Test the main summary endpoint directly
        print("\n[Test 5] Profit intelligence summary endpoint...")
        
        # Create a mock user object for the endpoint
        class MockUser:
            def __init__(self, user_id, email):
                self.id = user_id
                self.email = email
        
        mock_user = MockUser(user.id, user.email)
        
        # Call the endpoint function directly (it's async, so we need to handle it)
        import asyncio
        
        async def call_async_endpoint():
            return await get_profit_intelligence_summary(mock_user, db)
        
        summary = asyncio.run(call_async_endpoint())
        
        print("[OK] Summary endpoint completed successfully")
        print(f"   - Intelligence Score: {summary.get('intelligenceScore', 'N/A')}")
        print(f"   - Letter Grade: {summary.get('letterGrade', 'N/A')}")
        print(f"   - Monthly Savings: ${summary.get('monthlySavingsPotential', 0)}")
        print(f"   - Vendor Count: {summary.get('vendorCount', 0)}")
        print(f"   - Has Forecast Data: {'forecast' in summary}")
        print(f"   - Vendors Listed: {len(summary.get('vendors', []))}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] API test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    success = test_direct_api()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1)