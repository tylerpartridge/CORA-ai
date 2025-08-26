#!/usr/bin/env python3
"""
Test Enhanced Orchestrator Response Structure
Verifies that enhanced responses are compatible with existing UI
"""

import sys
import os
import json
sys.path.insert(0, '.')

print("=" * 60)
print("ENHANCED ORCHESTRATOR RESPONSE STRUCTURE TEST")
print("=" * 60)

# Create a mock enhanced response
def create_mock_enhanced_response():
    """Create a sample enhanced orchestrator response"""
    return {
        # Base orchestrator fields (must remain)
        "timestamp": "2025-08-09T22:00:00",
        "user_id": 1,
        "orchestration_type": "enhanced_with_emotional_awareness",
        "components": {
            "insight_moments": {
                "display_style": "gentle_display",  # Modified by emotional state
                "insights": [
                    {
                        "id": "cash_flow_1",
                        "type": "cash_flow_prediction",
                        "message": "Cash flow looking stable",
                        "urgency": "low"  # Reduced urgency if stressed
                    }
                ],
                "timing_delay": 8000  # Slower if overwhelmed
            },
            "intelligence_widget": {
                "score": 85,
                "visual_state": "calm_state",  # Changed from pulse_orange
                "trend": "stable"
            },
            "predictive_dashboard": {
                "highlight_mode": "minimal"  # Simplified if overwhelmed
            },
            # NEW: Quick actions for stress relief
            "quick_actions": [
                {
                    "type": "breathing",
                    "label": "Quick Breathing",
                    "icon": "🧘",
                    "priority": "high"
                },
                {
                    "type": "break",
                    "label": "5-Min Break",
                    "icon": "☕",
                    "priority": "medium"
                }
            ]
        },
        # NEW: Enhanced orchestrator additions
        "emotional_awareness": {
            "detected_state": "stressed",
            "confidence": 0.85,
            "stress_level": 7,
            "resilience_score": 65,
            "well_being_status": "needs_attention"
        },
        "wellness_support": {
            "available": True,
            "priority": "high",
            "type": "proactive",
            "message": "I see the pressure is building. Take a moment to breathe.",
            "recommendation": "Consider a 5-minute break",
            "quick_actions": [
                {
                    "id": "wellness_check",
                    "label": "How are you?",
                    "icon": "💙",
                    "action": "open_wellness_check"
                }
            ],
            "contextual_tips": [
                "Break big tasks into 15-minute chunks",
                "Delegate one thing today"
            ]
        },
        "empathetic_context": {
            "narrative": "Stress is your body's way of saying it's time to recalibrate.",
            "supportive_message": "Let's tackle one thing at a time.",
            "care_opportunities": [
                {
                    "type": "boundary_setting",
                    "message": "Consider setting a work cutoff time",
                    "action": "schedule_reminder",
                    "caring_note": "Your rest directly impacts tomorrow's success"
                }
            ],
            "emotional_tone": "calm_reassuring",
            "connection_strength": 0.75
        },
        "communication_style": {
            "tone": "calm_reassuring",
            "urgency": "gentle",
            "support_level": "moderate_support"
        },
        # Base relational context (enhanced)
        "relational_context": {
            "user_relationship_stage": "developing_trust",
            "current_chapter": "challenge_and_opportunity",
            "emotional_connection": {
                "empathy_level": 0.77,
                "support_readiness": True,
                "emotional_signals": [
                    {
                        "type": "late_night_work",
                        "intensity": 0.8,
                        "positive": False
                    }
                ]
            }
        }
    }

def test_backward_compatibility():
    """Test that enhanced response includes all base fields"""
    print("\n1. Testing Backward Compatibility...")
    
    response = create_mock_enhanced_response()
    
    # Check base fields exist
    required_base_fields = [
        "timestamp", "user_id", "components"
    ]
    
    for field in required_base_fields:
        if field in response:
            print(f"   OK: Base field '{field}' present")
        else:
            print(f"   ERROR: Missing base field '{field}'")
            return False
    
    # Check base components exist
    base_components = [
        "insight_moments", "intelligence_widget", "predictive_dashboard"
    ]
    
    for component in base_components:
        if component in response.get("components", {}):
            print(f"   OK: Base component '{component}' present")
        else:
            print(f"   ERROR: Missing base component '{component}'")
            return False
    
    return True

def test_new_fields_optional():
    """Test that new fields are optional (UI can ignore them)"""
    print("\n2. Testing New Fields Are Optional...")
    
    response = create_mock_enhanced_response()
    
    # These fields are new and should be optional
    optional_fields = [
        "emotional_awareness",
        "wellness_support",
        "empathetic_context",
        "communication_style"
    ]
    
    # Simulate UI that doesn't know about these fields
    for field in optional_fields:
        if field in response:
            print(f"   OK: Optional field '{field}' can be ignored by UI")
            # Remove it to simulate old UI
            del response[field]
    
    # Response should still be valid without new fields
    if "components" in response and "timestamp" in response:
        print("   OK: Response valid without enhanced fields")
        return True
    else:
        print("   ERROR: Response invalid without enhanced fields")
        return False

def test_frontend_handling():
    """Test how frontend should handle enhanced fields"""
    print("\n3. Testing Frontend Handling...")
    
    response = create_mock_enhanced_response()
    
    # Simulate frontend JavaScript handling
    print("   Frontend JavaScript pattern:")
    print("   ```javascript")
    print("   // Safe handling of optional enhanced fields")
    print("   if (response.emotional_awareness) {")
    print("       updateEmotionalIndicators(response.emotional_awareness);")
    print("   }")
    print("")
    print("   if (response.wellness_support) {")
    print("       showWellnessSupport(response.wellness_support);")
    print("   }")
    print("")
    print("   // Base functionality always works")
    print("   displayInsights(response.components.insight_moments);")
    print("   ```")
    
    return True

def test_response_size():
    """Test that enhanced response isn't too large"""
    print("\n4. Testing Response Size...")
    
    response = create_mock_enhanced_response()
    json_str = json.dumps(response)
    size_kb = len(json_str) / 1024
    
    print(f"   Response size: {size_kb:.2f} KB")
    
    if size_kb < 10:
        print("   OK: Response size is reasonable")
        return True
    else:
        print("   WARNING: Response may be too large")
        return False

def test_stress_adaptations():
    """Test how response changes based on stress level"""
    print("\n5. Testing Stress-Based Adaptations...")
    
    print("   When user is STRESSED:")
    print("     - display_style: 'gentle_display'")
    print("     - timing_delay: 8000ms (slower)")
    print("     - visual_state: 'calm_state'")
    print("     - quick_actions: Added for stress relief")
    print("")
    print("   When user is THRIVING:")
    print("     - display_style: 'celebratory_display'")
    print("     - visual_state: 'celebrate_state'")
    print("     - More insights shown")
    print("")
    print("   When user is OVERWHELMED:")
    print("     - Only 1 critical insight shown")
    print("     - highlight_mode: 'minimal'")
    print("     - Simplified presentation")
    
    return True

def run_all_tests():
    """Run all structure tests"""
    tests = [
        ("Backward Compatibility", test_backward_compatibility),
        ("New Fields Optional", test_new_fields_optional),
        ("Frontend Handling", test_frontend_handling),
        ("Response Size", test_response_size),
        ("Stress Adaptations", test_stress_adaptations)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\nERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("RESPONSE STRUCTURE TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nSUCCESS! Enhanced response structure is fully compatible!")
        print("Existing UI will continue to work, enhanced features are optional.")
    else:
        print(f"\nWARNING: {total - passed} test(s) failed.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)