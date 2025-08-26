#!/usr/bin/env python3
"""
Test suite for CORA personality enhancements
Validates authentic contractor conversation flows
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths


import json
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from routes.cora_chat_enhanced_v2 import ContractorProfiler

class PersonalityTester:
    def __init__(self):
        self.profiler = ContractorProfiler()
        self.test_results = []
    
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details
        }
        self.test_results.append(result)
        status_icon = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[WARN]"
        print(f"{status_icon} {test_name}: {details}")
    
    def test_contractor_type_detection(self):
        """Test contractor type detection accuracy"""
        print("\n[TEST] Contractor Type Detection")
        
        test_cases = [
            ("I'm a general contractor managing multiple subs", "general_contractor"),
            ("I do plumbing work, mostly residential service calls", "specialty_trade"),
            ("We specialize in concrete driveways and foundations", "concrete_specialist"),
            ("Kitchen and bathroom remodeling is our focus", "remodeler"),
            ("I'm an electrician running a solo operation", "specialty_trade")
        ]
        
        for message, expected_type in test_cases:
            context = self.profiler.analyze_contractor_context(message, [])
            actual_type = context.get("contractor_type")
            
            if actual_type == expected_type:
                self.log_test(f"Type Detection: {expected_type}", "PASS", f"Correctly identified from: '{message[:30]}...'")
            else:
                self.log_test(f"Type Detection: {expected_type}", "FAIL", f"Expected {expected_type}, got {actual_type}")
    
    def test_emotional_state_recognition(self):
        """Test emotional state and stress detection"""
        print("\n[TEST] Emotional State Recognition")
        
        stress_test_cases = [
            ("Cash flow is really tight, payroll is due Friday", "financial_pressure_phrases"),
            ("I'm drowning in paperwork, working every weekend", "overwhelm_indicators"),
            ("Not sure if I'm pricing jobs right, maybe I'm wrong", "confidence_issues"),
            ("Everything's going great, just landed three new jobs", "neutral")
        ]
        
        for message, expected_state in stress_test_cases:
            context = self.profiler.analyze_contractor_context(message, [])
            emotional_state = context.get("emotional_state", "neutral")
            
            if expected_state == "neutral":
                if emotional_state == "neutral":
                    self.log_test("Emotional State: Neutral", "PASS", "Correctly identified positive/neutral state")
                else:
                    self.log_test("Emotional State: Neutral", "FAIL", f"False positive: {emotional_state}")
            else:
                if emotional_state != "neutral":
                    self.log_test(f"Emotional State: {expected_state}", "PASS", f"Detected stress in: '{message[:30]}...'")
                else:
                    self.log_test(f"Emotional State: {expected_state}", "FAIL", "Missed stress indicators")
    
    def test_conversation_phase_progression(self):
        """Test conversation phase detection and progression"""
        print("\n[TEST] Conversation Phase Progression")
        
        conversation_flow = [
            ("Hello", "greeting"),
            ("I'm a general contractor", "discovery"),
            ("My biggest problem is tracking job profitability", "discovery"),
            ("How does this help with change orders?", "education"),
            ("How much does this cost?", "pricing"),
            ("Can I try this for free?", "commitment")
        ]
        
        history = []
        for message, expected_phase in conversation_flow:
            context = self.profiler.analyze_contractor_context(message, history)
            actual_phase = context.get("conversation_phase")
            
            if actual_phase == expected_phase:
                self.log_test(f"Phase: {expected_phase}", "PASS", f"Message: '{message}'")
            else:
                self.log_test(f"Phase: {expected_phase}", "FAIL", f"Expected {expected_phase}, got {actual_phase}")
            
            # Add to history for next iteration
            history.append({"message": message})
    
    def test_glen_day_specific_responses(self):
        """Test Glen Day specific personality enhancements"""
        print("\n[TEST] Glen Day Specific Responses")
        
        glen_scenarios = [
            {
                "message": "I'm Glen Day, veteran general contractor with concrete and remodeling experience",
                "expected_elements": ["veteran", "experienced", "concrete", "multiple trades"]
            },
            {
                "message": "We're a growing company, need better systems as we scale",
                "expected_elements": ["growing", "scale", "systems", "can't track everything"]
            },
            {
                "message": "Concrete work seems most profitable but hard to track",
                "expected_elements": ["concrete", "profitable", "margin", "weather", "ready mix"]
            }
        ]
        
        for scenario in glen_scenarios:
            message = scenario["message"]
            expected_elements = scenario["expected_elements"]
            
            context = self.profiler.analyze_contractor_context(message, [])
            response = self.profiler.get_personalized_response(message, context, [])
            
            found_elements = sum(1 for element in expected_elements if element.lower() in response.lower())
            
            if found_elements >= len(expected_elements) / 2:  # At least half the elements
                self.log_test("Glen Day Personalization", "PASS", f"Found {found_elements}/{len(expected_elements)} relevant elements")
            else:
                self.log_test("Glen Day Personalization", "FAIL", f"Only found {found_elements}/{len(expected_elements)} relevant elements")
    
    def test_empathy_and_validation(self):
        """Test empathy and validation responses"""
        print("\n[TEST] Empathy and Validation")
        
        empathy_scenarios = [
            "I'm frustrated with losing money on jobs",
            "Paperwork is killing me, no time for family",
            "Don't know if I'm pricing jobs correctly",
            "Cash flow is always a struggle"
        ]
        
        empathy_indicators = [
            "i hear", "i get it", "that's tough", "frustration", "understand",
            "been there", "every contractor", "you're not alone", "pain"
        ]
        
        for message in empathy_scenarios:
            context = self.profiler.analyze_contractor_context(message, [])
            response = self.profiler.get_personalized_response(message, context, [])
            
            has_empathy = any(indicator in response.lower() for indicator in empathy_indicators)
            
            if has_empathy:
                self.log_test("Empathy Response", "PASS", f"Empathetic response to: '{message[:30]}...'")
            else:
                self.log_test("Empathy Response", "FAIL", f"No empathy detected in response to stress")
    
    def test_industry_terminology(self):
        """Test use of appropriate industry terminology"""
        print("\n[TEST] Industry Terminology")
        
        industry_terms = [
            "change order", "scope creep", "margin", "subs", "markup",
            "job site", "draw schedule", "overhead", "profit", "cash flow"
        ]
        
        general_message = "Tell me about your system"
        context = {"contractor_type": "general_contractor", "conversation_phase": "education"}
        response = self.profiler.get_personalized_response(general_message, context, [])
        
        terms_used = sum(1 for term in industry_terms if term in response.lower())
        
        if terms_used >= 2:
            self.log_test("Industry Terminology", "PASS", f"Used {terms_used} industry terms naturally")
        else:
            self.log_test("Industry Terminology", "WARN", f"Only used {terms_used} industry terms")
    
    def test_response_authenticity(self):
        """Test overall response authenticity and contractor voice"""
        print("\n[TEST] Response Authenticity")
        
        test_messages = [
            "What makes your system different?",
            "I'm worried about learning new technology",
            "How do you handle change orders?",
            "What about integration with QuickBooks?"
        ]
        
        authenticity_markers = [
            "contractor", "field", "job site", "real world", "experience",
            "buddy", "understand", "been there", "industry", "practical"
        ]
        
        authentic_responses = 0
        for message in test_messages:
            context = self.profiler.analyze_contractor_context(message, [])
            response = self.profiler.get_personalized_response(message, context, [])
            
            authenticity_score = sum(1 for marker in authenticity_markers if marker in response.lower())
            
            if authenticity_score >= 2:
                authentic_responses += 1
                self.log_test(f"Authenticity: '{message[:20]}...'", "PASS", f"Score: {authenticity_score}")
            else:
                self.log_test(f"Authenticity: '{message[:20]}...'", "FAIL", f"Score: {authenticity_score}")
        
        if authentic_responses >= len(test_messages) * 0.75:
            self.log_test("Overall Authenticity", "PASS", f"{authentic_responses}/{len(test_messages)} responses sound authentic")
        else:
            self.log_test("Overall Authenticity", "FAIL", f"Only {authentic_responses}/{len(test_messages)} responses sound authentic")
    
    def generate_personality_report(self):
        """Generate comprehensive personality testing report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["status"] == "PASS")
        failed_tests = sum(1 for result in self.test_results if result["status"] == "FAIL")
        warning_tests = sum(1 for result in self.test_results if result["status"] == "WARN")
        
        print(f"\n[SUMMARY] PERSONALITY ENHANCEMENT TESTING")
        print(f"Total Tests: {total_tests}")
        print(f"[PASS] Passed: {passed_tests}")
        print(f"[FAIL] Failed: {failed_tests}")
        print(f"[WARN] Warnings: {warning_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Save detailed report
        report_path = Path("data/test_results/personality_enhancement_report.json")
        report_path.parent.mkdir(exist_ok=True)
        
        report = {
            "personality_testing": {
                "timestamp": "2025-08-02",
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warnings": warning_tests,
                "success_rate": (passed_tests/total_tests)*100,
                "glen_day_demo_ready": failed_tests <= 2
            },
            "detailed_results": self.test_results,
            "enhancement_validation": [
                "Contractor type detection accuracy",
                "Emotional intelligence and empathy",
                "Industry terminology usage", 
                "Conversation phase management",
                "Glen Day specific personalization",
                "Authentic contractor voice"
            ]
        }
        
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n[REPORT] Personality report saved to: {report_path}")
        
        if failed_tests <= 2:
            print("\n[SUCCESS] PERSONALITY ENHANCEMENTS VALIDATED!")
            print("CORA ready for authentic contractor conversations.")
        else:
            print(f"\n[WARNING] {failed_tests} critical personality issues - review before demo")
        
        return failed_tests <= 2
    
    def run_all_tests(self):
        """Run complete personality enhancement test suite"""
        print("[START] CORA PERSONALITY ENHANCEMENT TESTING\n")
        
        self.test_contractor_type_detection()
        self.test_emotional_state_recognition()
        self.test_conversation_phase_progression()
        self.test_glen_day_specific_responses()
        self.test_empathy_and_validation()
        self.test_industry_terminology()
        self.test_response_authenticity()
        
        return self.generate_personality_report()

if __name__ == "__main__":
    tester = PersonalityTester()
    tester.run_all_tests()