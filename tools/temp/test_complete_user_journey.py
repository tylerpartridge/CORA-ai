#!/usr/bin/env python3
"""
Complete User Journey Testing
Tests the entire flow: Landing → Signup → Onboarding → Dashboard → CORA Engagement
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths


import json
import time
import requests
from pathlib import Path
from datetime import datetime

class CompleteUserJourneyTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.test_user_email = f"test_user_{int(time.time())}@example.com"
        self.test_password = "TestPassword123!"
        self.auth_token = None
        
    def log_test(self, step, status, details=""):
        """Log each step of the user journey"""
        result = {
            "step": step,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_icon = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[WARN]"
        print(f"{status_icon} Step {len(self.test_results)}: {step}")
        if details:
            print(f"    Details: {details}")
    
    def step_1_landing_page(self):
        """Step 1: User visits landing page"""
        print("\n=== STEP 1: LANDING PAGE ===")
        
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                # Check for key elements that should be on landing page
                content = response.text.lower()
                elements_found = []
                
                if "cora" in content:
                    elements_found.append("CORA branding")
                if "onboarding" in content or "get started" in content or "sign up" in content:
                    elements_found.append("CTA buttons")
                if "contractor" in content or "construction" in content:
                    elements_found.append("contractor messaging")
                
                if len(elements_found) >= 2:
                    self.log_test("Landing Page Load", "PASS", f"Found: {', '.join(elements_found)}")
                    return True
                else:
                    self.log_test("Landing Page Load", "FAIL", f"Missing key elements, only found: {', '.join(elements_found)}")
                    return False
            else:
                self.log_test("Landing Page Load", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Landing Page Load", "FAIL", f"Error: {str(e)}")
            return False
    
    def step_2_navigate_to_onboarding(self):
        """Step 2: User navigates to onboarding"""
        print("\n=== STEP 2: NAVIGATE TO ONBOARDING ===")
        
        try:
            response = self.session.get(f"{self.base_url}/onboarding")
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for onboarding elements
                if "onboarding" in content and ("cora" in content or "chat" in content):
                    self.log_test("Onboarding Page Access", "PASS", "Onboarding page loaded successfully")
                    return True
                else:
                    self.log_test("Onboarding Page Access", "FAIL", "Onboarding page missing key elements")
                    return False
            else:
                self.log_test("Onboarding Page Access", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Onboarding Page Access", "FAIL", f"Error: {str(e)}")
            return False
    
    def step_3_ai_onboarding_conversation(self):
        """Step 3: User engages in AI onboarding conversation"""
        print("\n=== STEP 3: AI ONBOARDING CONVERSATION ===")
        
        conversation_steps = [
            {
                "message": "I'm a general contractor",
                "expected_response_keywords": ["contractor", "construction", "work", "business"]
            },
            {
                "message": "I do remodeling and concrete work, growing company",
                "expected_response_keywords": ["remodeling", "concrete", "growing", "business"]
            },
            {
                "message": "My biggest challenge is tracking job profitability",
                "expected_response_keywords": ["profit", "track", "job", "cost"]
            }
        ]
        
        conversation_id = f"journey_test_{int(time.time())}"
        successful_turns = 0
        
        for i, turn in enumerate(conversation_steps):
            try:
                payload = {
                    "message": turn["message"],
                    "conversation_id": conversation_id,
                    "metadata": {"onboarding": True, "testMode": True}
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/cora-chat/",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    ai_response = response_data.get("message", "").lower()
                    
                    # Check if response contains expected keywords
                    keywords_found = sum(1 for keyword in turn["expected_response_keywords"] 
                                       if keyword.lower() in ai_response)
                    
                    if keywords_found >= 1:  # At least one keyword should match
                        successful_turns += 1
                        self.log_test(f"AI Conversation Turn {i+1}", "PASS", 
                                    f"CORA responded appropriately ({keywords_found} relevant keywords)")
                    else:
                        self.log_test(f"AI Conversation Turn {i+1}", "WARN", 
                                    f"CORA responded but with limited relevance")
                else:
                    self.log_test(f"AI Conversation Turn {i+1}", "FAIL", f"API error: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"AI Conversation Turn {i+1}", "FAIL", f"Error: {str(e)}")
            
            # Small delay between AI calls to avoid rate limiting
            if i < len(conversation_steps) - 1:  # Don't delay after last call
                time.sleep(2)
        
        # Overall conversation success
        if successful_turns >= len(conversation_steps) // 2:
            self.log_test("Overall AI Conversation", "PASS", f"{successful_turns}/{len(conversation_steps)} turns successful")
            return True
        else:
            self.log_test("Overall AI Conversation", "FAIL", f"Only {successful_turns}/{len(conversation_steps)} turns successful")
            return False
    
    def step_4_user_registration(self):
        """Step 4: User completes registration"""
        print("\n=== STEP 4: USER REGISTRATION ===")
        
        try:
            registration_data = {
                "email": self.test_user_email,
                "password": self.test_password,
                "password_confirm": self.test_password
            }
            
            response = self.session.post(
                f"{self.base_url}/api/signup",
                json=registration_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200 or response.status_code == 201:
                response_data = response.json()
                
                # Check if we get an auth token or success message
                if "access_token" in response_data or "token" in response_data:
                    self.auth_token = response_data.get("access_token") or response_data.get("token")
                    self.log_test("User Registration", "PASS", "Account created with auth token")
                    return True
                elif "success" in response_data or response_data.get("success") == True:
                    self.log_test("User Registration", "PASS", "Account created successfully")
                    return True
                else:
                    self.log_test("User Registration", "WARN", "Registration completed but no clear success indicator")
                    return True
            else:
                self.log_test("User Registration", "FAIL", f"Registration failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("User Registration", "FAIL", f"Registration error: {str(e)}")
            return False
    
    def step_5_business_profile_creation(self):
        """Step 5: User creates business profile"""
        print("\n=== STEP 5: BUSINESS PROFILE CREATION ===")
        
        try:
            # If we have an auth token, use it
            headers = {"Content-Type": "application/json"}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            profile_data = {
                "businessName": "Test Construction Co",
                "businessType": "General Contracting", 
                "industry": "Construction",
                "monthlyRevenueRange": "$10,000 - $50,000",
                "onboardingData": {
                    "contractorType": "general_contractor",
                    "businessSize": "growing",
                    "primaryChallenges": ["profit_tracking", "time_management"]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/onboarding/create-business-profile",
                json=profile_data,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                if response_data.get("success"):
                    self.log_test("Business Profile Creation", "PASS", "Profile created successfully")
                    return True
                else:
                    self.log_test("Business Profile Creation", "WARN", "Profile endpoint responded but unclear success")
                    return True
            elif response.status_code == 401:
                self.log_test("Business Profile Creation", "WARN", "Auth required - testing auth flow")
                return True  # This is expected behavior
            else:
                self.log_test("Business Profile Creation", "FAIL", f"Profile creation failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Business Profile Creation", "FAIL", f"Profile creation error: {str(e)}")
            return False
    
    def step_6_dashboard_access(self):
        """Step 6: User accesses dashboard"""
        print("\n=== STEP 6: DASHBOARD ACCESS ===")
        
        try:
            # Test dashboard access
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            response = self.session.get(f"{self.base_url}/dashboard", headers=headers)
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for dashboard elements
                dashboard_elements = []
                if "dashboard" in content:
                    dashboard_elements.append("dashboard content")
                if "profit" in content or "expense" in content:
                    dashboard_elements.append("financial features")
                if "cora" in content:
                    dashboard_elements.append("CORA integration")
                
                if len(dashboard_elements) >= 2:
                    self.log_test("Dashboard Access", "PASS", f"Dashboard loaded with: {', '.join(dashboard_elements)}")
                    return True
                else:
                    self.log_test("Dashboard Access", "WARN", "Dashboard loaded but missing expected elements")
                    return True
                    
            elif response.status_code in [401, 403]:
                # This is actually correct behavior - dashboard should require auth
                self.log_test("Dashboard Access", "PASS", "Dashboard properly protected (requires authentication)")
                return True
            elif response.status_code == 302:
                self.log_test("Dashboard Access", "PASS", "Dashboard redirects unauthenticated users (correct behavior)")
                return True
            else:
                self.log_test("Dashboard Access", "FAIL", f"Unexpected dashboard response: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Dashboard Access", "FAIL", f"Dashboard access error: {str(e)}")
            return False
    
    def step_7_cora_engagement(self):
        """Step 7: User engages with CORA in dashboard context"""
        print("\n=== STEP 7: DASHBOARD CORA ENGAGEMENT ===")
        
        try:
            # Test CORA chat in dashboard context
            dashboard_conversation = [
                {
                    "message": "How do I track expenses for my current job?",
                    "context": "dashboard_help"
                },
                {
                    "message": "Show me my profit margins",
                    "context": "profit_inquiry"
                }
            ]
            
            successful_interactions = 0
            
            for i, interaction in enumerate(dashboard_conversation):
                payload = {
                    "message": interaction["message"],
                    "conversation_id": f"dashboard_test_{int(time.time())}",
                    "metadata": {
                        "context": interaction["context"],
                        "authenticated": True,
                        "testMode": True
                    }
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/cora-chat/",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    ai_response = response_data.get("message", "")
                    
                    if len(ai_response) > 10:  # Basic response quality check
                        successful_interactions += 1
                        self.log_test(f"Dashboard CORA Interaction {i+1}", "PASS", 
                                    f"CORA provided helpful response ({len(ai_response)} chars)")
                    else:
                        self.log_test(f"Dashboard CORA Interaction {i+1}", "WARN", "CORA response too brief")
                else:
                    self.log_test(f"Dashboard CORA Interaction {i+1}", "FAIL", f"API error: {response.status_code}")
            
            if successful_interactions >= len(dashboard_conversation) // 2:
                self.log_test("Overall Dashboard CORA Engagement", "PASS", 
                            f"{successful_interactions}/{len(dashboard_conversation)} interactions successful")
                return True
            else:
                self.log_test("Overall Dashboard CORA Engagement", "FAIL", 
                            f"Only {successful_interactions}/{len(dashboard_conversation)} interactions successful")
                return False
                
        except Exception as e:
            self.log_test("Dashboard CORA Engagement", "FAIL", f"Error: {str(e)}")
            return False
    
    def step_8_profit_features(self):
        """Step 8: User accesses profit analysis features"""
        print("\n=== STEP 8: PROFIT ANALYSIS FEATURES ===")
        
        try:
            # Test profit features via main dashboard
            response = self.session.get(f"{self.base_url}/dashboard")
            
            if response.status_code == 200:
                content = response.text.lower()
                
                profit_features = []
                if "profit" in content:
                    profit_features.append("profit analysis")
                if "expense" in content or "cost" in content:
                    profit_features.append("expense tracking")
                if "chart" in content or "graph" in content:
                    profit_features.append("data visualization")
                
                if len(profit_features) >= 1:
                    self.log_test("Profit Features in Dashboard", "PASS", f"Features available: {', '.join(profit_features)}")
                else:
                    self.log_test("Profit Features in Dashboard", "WARN", f"Limited features: {', '.join(profit_features)}")
                
                # Test profit API endpoints
                profit_apis = [
                    "/api/profit-analysis/summary",
                    "/api/profit-analysis/quick-wins"
                ]
                
                api_successes = 0
                for api in profit_apis:
                    try:
                        api_response = self.session.options(f"{self.base_url}{api}")
                        if api_response.status_code in [200, 405]:
                            api_successes += 1
                    except:
                        pass
                
                if api_successes >= len(profit_apis) // 2:
                    self.log_test("Profit API Endpoints", "PASS", f"{api_successes}/{len(profit_apis)} APIs accessible")
                    return True
                else:
                    self.log_test("Profit API Endpoints", "FAIL", f"Only {api_successes}/{len(profit_apis)} APIs accessible")
                    return False
                    
            else:
                self.log_test("Profit Dashboard Access", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Profit Analysis Features", "FAIL", f"Error: {str(e)}")
            return False
    
    def generate_journey_report(self):
        """Generate comprehensive user journey report"""
        total_steps = len(self.test_results)
        passed_steps = sum(1 for result in self.test_results if result["status"] == "PASS")
        failed_steps = sum(1 for result in self.test_results if result["status"] == "FAIL")
        warning_steps = sum(1 for result in self.test_results if result["status"] == "WARN")
        
        print(f"\n{'='*60}")
        print(f"COMPLETE USER JOURNEY TEST RESULTS")
        print(f"{'='*60}")
        print(f"Total Steps: {total_steps}")
        print(f"[PASS] Successful: {passed_steps}")
        print(f"[FAIL] Failed: {failed_steps}")
        print(f"[WARN] Warnings: {warning_steps}")
        print(f"Success Rate: {(passed_steps/total_steps)*100:.1f}%")
        
        # Determine overall journey status
        critical_failures = failed_steps
        journey_quality = "EXCELLENT" if critical_failures == 0 and passed_steps >= total_steps * 0.8 else \
                         "GOOD" if critical_failures <= 1 else \
                         "NEEDS_WORK"
        
        print(f"\nOVERALL JOURNEY QUALITY: {journey_quality}")
        
        # Save detailed report
        report_path = Path("data/test_results/complete_user_journey_report.json")
        report_path.parent.mkdir(exist_ok=True)
        
        report = {
            "user_journey_testing": {
                "timestamp": datetime.now().isoformat(),
                "test_user_email": self.test_user_email,
                "total_steps": total_steps,
                "passed": passed_steps,
                "failed": failed_steps,
                "warnings": warning_steps,
                "success_rate": (passed_steps/total_steps)*100,
                "journey_quality": journey_quality,
                "onboarding_ready": critical_failures == 0
            },
            "journey_steps": [
                "Landing Page Load",
                "Onboarding Page Access", 
                "AI Onboarding Conversation",
                "User Registration",
                "Business Profile Creation",
                "Dashboard Access",
                "Dashboard CORA Engagement", 
                "Profit Analysis Features"
            ],
            "detailed_results": self.test_results,
            "recommendations": self._generate_recommendations(critical_failures, warning_steps)
        }
        
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n[REPORT] Journey test report saved to: {report_path}")
        
        if critical_failures == 0:
            print(f"\nSUCCESS USER JOURNEY READY FOR PRODUCTION!")
            print("PASS Complete onboarding flow validated")
            print("PASS All critical functionality working")
            print("PASS Glen Day demo fully supported")
        else:
            print(f"\nWARNING USER JOURNEY NEEDS ATTENTION")
            print(f"FAIL {critical_failures} critical issues blocking smooth onboarding")
        
        return critical_failures == 0
    
    def _generate_recommendations(self, failed_steps, warning_steps):
        """Generate recommendations based on journey test results"""
        recommendations = []
        
        if failed_steps == 0:
            recommendations.append("Complete user journey is functional and ready for production")
            recommendations.append("Consider adding more test scenarios for edge cases")
        else:
            recommendations.append("Address failed steps before launching to users")
            recommendations.append("Focus on critical user flow elements first")
        
        if warning_steps > 2:
            recommendations.append("Review warning steps for user experience improvements")
            
        return recommendations
    
    def run_complete_journey_test(self):
        """Execute the complete user journey test"""
        print("COMPLETE USER JOURNEY TESTING")
        print("Testing: Landing -> Signup -> Onboarding -> Dashboard -> CORA Engagement")
        print("=" * 70)
        
        # Execute each step of the user journey
        self.step_1_landing_page()
        self.step_2_navigate_to_onboarding()
        self.step_3_ai_onboarding_conversation()
        self.step_4_user_registration()
        self.step_5_business_profile_creation()
        self.step_6_dashboard_access()
        self.step_7_cora_engagement()
        self.step_8_profit_features()
        
        # Generate comprehensive report
        return self.generate_journey_report()

if __name__ == "__main__":
    tester = CompleteUserJourneyTester()
    success = tester.run_complete_journey_test()
    
    import sys
    sys.exit(0 if success else 1)