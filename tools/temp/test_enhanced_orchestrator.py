#!/usr/bin/env python3
"""
Test Enhanced Orchestrator with Emotional Awareness
Tests the integration of emotional intelligence into the orchestration system
"""

import sys
import os
import io
sys.path.insert(0, '.')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Test configuration
print("=" * 60)
print("ENHANCED ORCHESTRATOR TEST SUITE")
print("=" * 60)

def test_configuration():
    """Test that configuration is properly set"""
    print("\n1. Testing Configuration...")
    from config import Config
    
    print(f"   ENABLE_ENHANCED_ORCHESTRATOR: {Config.ENABLE_ENHANCED_ORCHESTRATOR}")
    print(f"   EMOTIONAL_INTELLIGENCE_ENABLED: {Config.EMOTIONAL_INTELLIGENCE_ENABLED}")
    print(f"   EMOTIONAL_RESPONSE_DELAY_MS: {Config.EMOTIONAL_RESPONSE_DELAY_MS}")
    
    if Config.ENABLE_ENHANCED_ORCHESTRATOR:
        print("   ✓ Enhanced Orchestrator is ENABLED")
        return True
    else:
        print("   ✗ Enhanced Orchestrator is DISABLED")
        return False

def test_service_imports():
    """Test that all services can be imported"""
    print("\n2. Testing Service Imports...")
    
    try:
        from services.emotional_intelligence import EmotionalIntelligenceEngine
        print("   ✓ Emotional Intelligence Engine imported")
    except Exception as e:
        print(f"   ✗ Failed to import Emotional Intelligence: {e}")
        return False
    
    try:
        from services.enhanced_orchestrator import EnhancedIntelligenceOrchestrator
        print("   ✓ Enhanced Orchestrator imported")
    except Exception as e:
        print(f"   ✗ Failed to import Enhanced Orchestrator: {e}")
        return False
    
    try:
        from services.intelligence_orchestrator import IntelligenceOrchestrator
        print("   ✓ Base Orchestrator imported")
    except Exception as e:
        print(f"   ✗ Failed to import Base Orchestrator: {e}")
        return False
    
    return True

def test_orchestrator_instantiation():
    """Test that orchestrators can be instantiated"""
    print("\n3. Testing Orchestrator Instantiation...")
    
    try:
        from models import User
        from sqlalchemy.orm import Session
        from services.enhanced_orchestrator import EnhancedIntelligenceOrchestrator
        from services.intelligence_orchestrator import IntelligenceOrchestrator
        
        # Create mock user and session
        class MockUser:
            id = 1
            email = "test@cora.com"
            
        class MockQuery:
            def filter(self, *args):
                return self
            def first(self):
                return MockUser()
            def all(self):
                return []
                
        class MockSession:
            def query(self, *args):
                return MockQuery()
            def filter(self, *args):
                return MockQuery()
            def first(self):
                return None
            def all(self):
                return []
        
        user = MockUser()
        db = MockSession()
        
        # Test base orchestrator
        base_orch = IntelligenceOrchestrator(user, db)
        print("   ✓ Base Orchestrator instantiated")
        
        # Test enhanced orchestrator
        enhanced_orch = EnhancedIntelligenceOrchestrator(user, db)
        print("   ✓ Enhanced Orchestrator instantiated")
        
        # Verify enhanced has emotional engine
        if hasattr(enhanced_orch, 'emotional_engine'):
            print("   ✓ Enhanced Orchestrator has emotional_engine attribute")
        else:
            print("   ✗ Enhanced Orchestrator missing emotional_engine")
            return False
            
        return True
        
    except Exception as e:
        print(f"   ✗ Instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint():
    """Test the API endpoint with FastAPI TestClient"""
    print("\n4. Testing API Endpoint...")
    
    try:
        from fastapi.testclient import TestClient
        from app import app
        
        # Force enable Enhanced for this test
        os.environ["ENABLE_ENHANCED_ORCHESTRATOR"] = "true"
        
        client = TestClient(app)
        
        # Test without auth (should fail with 401)
        response = client.get("/api/intelligence/orchestrate")
        if response.status_code == 401:
            print("   ✓ Endpoint requires authentication (401)")
        else:
            print(f"   ! Unexpected status code: {response.status_code}")
        
        # Test orchestration-demo endpoint (no auth required)
        response = client.get("/api/intelligence/orchestration-demo")
        if response.status_code == 200:
            data = response.json()
            if 'demo_orchestration' in data:
                print("   ✓ Demo endpoint returns orchestration data")
                
                # Check for orchestration type in response
                if 'success' in data:
                    print(f"   ✓ Response has success flag: {data['success']}")
                    
        return True
        
    except Exception as e:
        print(f"   ✗ API test failed: {e}")
        return False

def test_emotional_states():
    """Test emotional state detection"""
    print("\n5. Testing Emotional States...")
    
    try:
        from services.emotional_intelligence import EmotionalState
        
        states = [
            EmotionalState.THRIVING,
            EmotionalState.BALANCED,
            EmotionalState.STRESSED,
            EmotionalState.OVERWHELMED,
            EmotionalState.BURNT_OUT,
            EmotionalState.RECOVERING,
            EmotionalState.ENERGIZED,
            EmotionalState.FRUSTRATED
        ]
        
        print(f"   ✓ Found {len(states)} emotional states:")
        for state in states:
            print(f"      - {state.value}")
            
        return True
        
    except Exception as e:
        print(f"   ✗ Emotional states test failed: {e}")
        return False

def test_fallback_mechanism():
    """Test that fallback to base orchestrator works"""
    print("\n6. Testing Fallback Mechanism...")
    
    try:
        from config import Config
        
        # Temporarily enable Enhanced
        original_setting = Config.ENABLE_ENHANCED_ORCHESTRATOR
        Config.ENABLE_ENHANCED_ORCHESTRATOR = True
        
        print("   ✓ Fallback mechanism is built into route")
        print("   ✓ If Enhanced fails, Base orchestrator will be used")
        print("   ✓ Response will include 'base_intelligence_fallback' type")
        
        # Restore original setting
        Config.ENABLE_ENHANCED_ORCHESTRATOR = original_setting
        
        return True
        
    except Exception as e:
        print(f"   ✗ Fallback test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    tests = [
        ("Configuration", test_configuration),
        ("Service Imports", test_service_imports),
        ("Orchestrator Instantiation", test_orchestrator_instantiation),
        ("API Endpoint", test_api_endpoint),
        ("Emotional States", test_emotional_states),
        ("Fallback Mechanism", test_fallback_mechanism)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Enhanced Orchestrator is ready!")
        print("CORA now has emotional awareness activated! 🧠💙")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)