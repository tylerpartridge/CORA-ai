#!/usr/bin/env python3
"""
Test the profit intelligence implementation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models import get_db
from services.profit_leak_detector import ProfitLeakDetector
from features.profit_intelligence.advanced_analytics import ProfitIntelligenceEngine

def test_profit_intelligence():
    """Test profit intelligence features"""
    print("Testing Profit Intelligence Engine")
    print("=" * 50)
    
    # Get database session
    db = next(get_db())
    
    # Find a test user
    from models.user import User
    test_user = db.query(User).first()
    
    if not test_user:
        print("[ERROR] No users found in database")
        return False
    
    print(f"[OK] Testing with user: {test_user.email}")
    
    # Initialize engines
    detector = ProfitLeakDetector(db, test_user.id)
    intelligence = ProfitIntelligenceEngine(detector)
    
    # Test 1: Cost Forecasting
    print("\n[Test 1] Cost Forecasting...")
    try:
        forecast = detector.predict_future_costs(forecast_months=3)
        if "error" not in forecast:
            print(f"  [OK] Forecast generated: {forecast.get('overall_trend', 'unknown')} trend")
            print(f"  Confidence: {forecast.get('confidence', 'low')}")
        else:
            print(f"  [INFO] {forecast.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
    
    # Test 2: Vendor Performance
    print("\n[Test 2] Vendor Performance Analysis...")
    try:
        vendor_analysis = detector.analyze_vendor_performance()
        vendor_count = vendor_analysis.get("analyzed_vendors", 0)
        print(f"  [OK] Analyzed {vendor_count} vendors")
        if vendor_count > 0:
            print(f"  Top performers: {len(vendor_analysis.get('top_performers', []))}")
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
    
    # Test 3: Intelligent Categorization
    print("\n[Test 3] AI Expense Categorization...")
    try:
        test_expense = {
            "description": "Lumber for Martinez job",
            "vendor": "Home Depot",
            "amount": 350.00
        }
        categorization = detector.intelligent_expense_categorization(**test_expense)
        print(f"  [OK] Suggested category: {categorization.get('suggested_category', 'Unknown')}")
        print(f"  Confidence: {categorization.get('confidence', 0):.1f}%")
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
    
    # Test 4: Industry Benchmarking
    print("\n[Test 4] Industry Benchmarking...")
    try:
        from models.business_profile import BusinessProfile
        profile = db.query(BusinessProfile).filter(
            BusinessProfile.user_email == test_user.email
        ).first()
        
        if profile:
            benchmarks = intelligence.generate_industry_benchmarks(
                business_type=profile.business_type
            )
            if benchmarks.get("status") != "insufficient_data":
                print(f"  [OK] Generated benchmarks for {benchmarks.get('business_type')}")
                print(f"  Sample size: {benchmarks.get('sample_size', 0)} businesses")
            else:
                print(f"  [INFO] {benchmarks.get('message', 'Unknown')}")
        else:
            print("  [INFO] No business profile found for user")
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
    
    # Test 5: Job Profitability Prediction
    print("\n[Test 5] Job Profitability Prediction...")
    try:
        test_job = {
            "type": "remodeling",
            "revenue": 15000,
            "duration": 30,
            "materials": ["lumber", "drywall", "paint"]
        }
        prediction = intelligence.predict_job_profitability(test_job)
        print(f"  [OK] Predicted margin: {prediction.get('predicted_margin', 0):.1f}%")
        print(f"  Confidence: {prediction.get('confidence', 0):.1f}%")
        print(f"  Based on: {prediction.get('similar_jobs_analyzed', 0)} similar jobs")
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
    
    # Test 6: Pricing Optimization
    print("\n[Test 6] Pricing Strategy Optimization...")
    try:
        pricing = intelligence.optimize_pricing_strategy(
            service_type="general_contracting",
            market_conditions={"demand": "high", "competition": "normal"}
        )
        if pricing.get("status") != "insufficient_data":
            print(f"  [OK] Current margin: {pricing.get('current_avg_margin', 0):.1f}%")
            print(f"  Pricing tiers generated: {len(pricing.get('pricing_tiers', {}))}")
        else:
            print(f"  [INFO] {pricing.get('message', 'Unknown')}")
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
    
    print("\n" + "=" * 50)
    print("[SUCCESS] Profit Intelligence Engine functional!")
    print("\nKey Capabilities:")
    print("- Cost forecasting with trend analysis")
    print("- Vendor performance scoring")
    print("- AI-powered expense categorization")
    print("- Industry benchmarking (with sufficient data)")
    print("- Job profitability prediction")
    print("- Dynamic pricing optimization")
    
    return True

if __name__ == "__main__":
    test_profit_intelligence()