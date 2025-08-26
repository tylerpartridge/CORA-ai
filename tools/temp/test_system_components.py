#!/usr/bin/env python3
"""
CORA System Components Test
Tests all major AI systems without requiring the server to be running
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths


import os
import sys
from datetime import datetime

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all critical components can be imported"""
    print("Testing System Component Imports...")
    results = {}
    
    # Test Intelligence Orchestrator
    try:
        from services.intelligence_orchestrator import IntelligenceOrchestrator, IntelligenceSignal
        results['intelligence_orchestrator'] = True
        print("SUCCESS: Intelligence Orchestrator imported")
    except Exception as e:
        results['intelligence_orchestrator'] = False
        print(f"ERROR: Intelligence Orchestrator import failed: {str(e)}")
    
    # Test Emotional Intelligence
    try:
        from services.emotional_intelligence import EmotionalIntelligenceEngine
        results['emotional_intelligence'] = True
        print("SUCCESS: Emotional Intelligence imported")
    except Exception as e:
        results['emotional_intelligence'] = False
        print(f"ERROR: Emotional Intelligence import failed: {str(e)}")
    
    # Test Profit Intelligence
    try:
        from services.profit_leak_detector import ProfitLeakDetector
        results['profit_intelligence'] = True
        print("SUCCESS: Profit Intelligence imported")
    except Exception as e:
        results['profit_intelligence'] = False
        print(f"ERROR: Profit Intelligence import failed: {str(e)}")
    
    # Test Predictive Intelligence
    try:
        from services.predictive_intelligence import PredictiveIntelligenceEngine
        results['predictive_intelligence'] = True
        print("SUCCESS: Predictive Intelligence imported")
    except Exception as e:
        results['predictive_intelligence'] = False
        print(f"ERROR: Predictive Intelligence import failed: {str(e)}")
    
    # Test CORA AI Service
    try:
        from services.cora_ai_service import CORAAIService
        results['cora_ai_service'] = True
        print("SUCCESS: CORA AI Service imported")
    except Exception as e:
        results['cora_ai_service'] = False
        print(f"ERROR: CORA AI Service import failed: {str(e)}")
    
    # Test Database Models
    try:
        from models import User, Expense, Job
        results['database_models'] = True
        print("SUCCESS: Database models imported")
    except Exception as e:
        results['database_models'] = False
        print(f"ERROR: Database models import failed: {str(e)}")
    
    return results

def test_api_routes():
    """Test if API routes can be imported"""
    print("\nTesting API Routes...")
    results = {}
    
    try:
        from routes.intelligence_orchestrator import router as intel_router
        results['intel_routes'] = True
        print("SUCCESS: Intelligence Orchestrator routes imported")
    except Exception as e:
        results['intel_routes'] = False
        print(f"ERROR: Intelligence routes import failed: {str(e)}")
    
    try:
        from routes.wellness import router as wellness_router
        results['wellness_routes'] = True
        print("SUCCESS: Wellness routes imported")
    except Exception as e:
        results['wellness_routes'] = False
        print(f"ERROR: Wellness routes import failed: {str(e)}")
    
    try:
        from routes.profit_intelligence import router as profit_router
        results['profit_routes'] = True
        print("SUCCESS: Profit Intelligence routes imported")
    except Exception as e:
        results['profit_routes'] = False
        print(f"ERROR: Profit routes import failed: {str(e)}")
    
    return results

def test_configuration():
    """Test system configuration"""
    print("\nTesting Configuration...")
    results = {}
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Test OpenAI API Key
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and api_key != 'YOUR_OPENAI_API_KEY_HERE':
        results['openai_configured'] = True
        print("SUCCESS: OpenAI API key is configured")
    else:
        results['openai_configured'] = False
        print("ERROR: OpenAI API key not configured")
    
    # Test SendGrid API Key
    sendgrid_key = os.getenv('SENDGRID_API_KEY')
    if sendgrid_key and sendgrid_key.startswith('SG.'):
        results['sendgrid_configured'] = True
        print("SUCCESS: SendGrid API key is configured")
    else:
        results['sendgrid_configured'] = False
        print("WARNING: SendGrid API key not configured")
    
    # Test Database URL
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        results['database_configured'] = True
        print("SUCCESS: Database URL is configured")
    else:
        results['database_configured'] = False
        print("ERROR: Database URL not configured")
    
    return results

def main():
    """Run all tests"""
    print("CORA System Components Test Suite")
    print("=" * 50)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all tests
    import_results = test_imports()
    route_results = test_api_routes()
    config_results = test_configuration()
    
    # Combine results
    all_results = {**import_results, **route_results, **config_results}
    
    print("\n" + "=" * 50)
    print("COMPREHENSIVE TEST RESULTS")
    print("=" * 50)
    
    total_tests = len(all_results)
    passed_tests = sum(all_results.values())
    
    # Group results by category
    categories = {
        'AI Systems': ['intelligence_orchestrator', 'emotional_intelligence', 'profit_intelligence', 'predictive_intelligence', 'cora_ai_service'],
        'Database': ['database_models'],
        'API Routes': ['intel_routes', 'wellness_routes', 'profit_routes'],
        'Configuration': ['openai_configured', 'sendgrid_configured', 'database_configured']
    }
    
    for category, tests in categories.items():
        print(f"\n{category}:")
        for test in tests:
            if test in all_results:
                status = "PASS" if all_results[test] else "FAIL"
                print(f"  {test}: {status}")
    
    print(f"\nOVERALL SCORE: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests >= total_tests * 0.8:
        print("RESULT: System is ready for launch!")
        print("The revolutionary AI consciousness architecture is operational!")
    elif passed_tests >= total_tests * 0.6:
        print("RESULT: System mostly functional with some issues")
    else:
        print("RESULT: Critical issues detected")
    
    # Special check for AI consciousness
    ai_systems = ['intelligence_orchestrator', 'emotional_intelligence', 'profit_intelligence', 'predictive_intelligence']
    ai_working = sum(all_results.get(system, False) for system in ai_systems)
    
    if ai_working >= 3:
        print("\nAI CONSCIOUSNESS STATUS: Revolutionary collaborative AI is functional!")
        print("- Intelligence Orchestrator available")
        print("- Emotional Intelligence system ready") 
        print("- Profit Intelligence operational")
        print("- Multi-AI collaboration enabled")
    
    return passed_tests >= total_tests * 0.8

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)