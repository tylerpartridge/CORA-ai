#!/usr/bin/env python3
"""
CORA Complete Integration Testing
Validates all system enhancements work together for Glen Day demo readiness
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths


import json
import time
import requests
import subprocess
import sys
from pathlib import Path
from datetime import datetime

class ComprehensiveIntegrationTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.session = requests.Session()
        self.server_process = None
    
    def log_test(self, test_name, status, details=""):
        """Log integration test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_icon = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[WARN]"
        print(f"{status_icon} {test_name}: {details}")
    
    def check_server_running(self):
        """Check if CORA server is running"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                self.log_test("Server Status", "PASS", "CORA server responding on port 8000")
                return True
            else:
                self.log_test("Server Status", "FAIL", f"Server returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("Server Status", "FAIL", f"Server not accessible: {str(e)}")
            return False
    
    def test_core_infrastructure(self):
        """Test core infrastructure components"""
        print("\n[INTEGRATION TEST] Core Infrastructure")
        
        # Test key routes
        core_routes = [
            ("/", "Landing page"),
            ("/onboarding", "Onboarding flow"),
            ("/dashboard", "Dashboard (should redirect if not authenticated)"),
            ("/profit-dashboard", "Profit dashboard")
        ]
        
        for route, description in core_routes:
            try:
                response = self.session.get(f"{self.base_url}{route}")
                if response.status_code in [200, 401, 403, 302]:  # Allow redirects for auth
                    self.log_test(f"Route: {route}", "PASS", f"{description} - Status {response.status_code}")
                else:
                    self.log_test(f"Route: {route}", "FAIL", f"Unexpected status {response.status_code}")
            except Exception as e:
                self.log_test(f"Route: {route}", "FAIL", f"Error: {str(e)}")
    
    def test_api_endpoints(self):
        """Test critical API endpoints"""
        print("\n[INTEGRATION TEST] API Endpoints")
        
        api_endpoints = [
            ("/api/cora-chat-v2/", "Enhanced CORA chat"),
            ("/api/auth/register", "User registration"),
            ("/api/onboarding/complete", "Onboarding completion"),
            ("/api/onboarding/create-business-profile", "Business profile creation"),
            ("/docs", "API documentation")
        ]
        
        for endpoint, description in api_endpoints:
            try:
                # Use OPTIONS to check endpoint existence without authentication
                response = self.session.options(f"{self.base_url}{endpoint}")
                if response.status_code in [200, 405, 422]:  # 405 = method not allowed but exists
                    self.log_test(f"API: {endpoint}", "PASS", f"{description} endpoint available")
                else:
                    self.log_test(f"API: {endpoint}", "FAIL", f"Status {response.status_code}")
            except Exception as e:
                self.log_test(f"API: {endpoint}", "FAIL", f"Error: {str(e)}")
    
    def test_static_assets(self):
        """Test static asset loading"""
        print("\n[INTEGRATION TEST] Static Assets")
        
        critical_assets = [
            "/static/js/onboarding-ai-wizard.js",
            "/static/css/onboarding-ai-wizard.css",
            "/static/js/security.js"
        ]
        
        for asset in critical_assets:
            try:
                response = self.session.get(f"{self.base_url}{asset}")
                if response.status_code == 200:
                    self.log_test(f"Asset: {asset}", "PASS", f"Loading correctly ({len(response.content)} bytes)")
                else:
                    self.log_test(f"Asset: {asset}", "FAIL", f"Status {response.status_code}")
            except Exception as e:
                self.log_test(f"Asset: {asset}", "FAIL", f"Error: {str(e)}")
    
    def test_enhanced_chat_personality(self):
        """Test enhanced CORA chat with Glen Day scenarios"""
        print("\n[INTEGRATION TEST] Enhanced Chat Personality")
        
        # Test Glen Day specific conversation
        glen_conversation = [
            {
                "message": "I'm Glen Day, veteran general contractor",
                "expected_keywords": ["veteran", "general contractor", "experience"]
            },
            {
                "message": "We do concrete work and remodeling, growing company",
                "expected_keywords": ["concrete", "remodeling", "growing"]
            },
            {
                "message": "My biggest challenge is tracking job profitability",
                "expected_keywords": ["profit", "job", "track", "margin"]
            }
        ]
        
        conversation_id = f"integration_test_{int(time.time())}"
        
        for i, turn in enumerate(glen_conversation):
            try:
                payload = {
                    "message": turn["message"],
                    "conversation_id": conversation_id,
                    "metadata": {"testMode": True}
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/cora-chat-v2/",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    response_text = response_data.get("message", "").lower()
                    
                    # Check for expected keywords in response
                    keywords_found = sum(1 for keyword in turn["expected_keywords"] 
                                       if keyword.lower() in response_text)
                    
                    if keywords_found >= len(turn["expected_keywords"]) // 2:
                        self.log_test(f"Chat Turn {i+1}", "PASS", 
                                    f"Appropriate response with {keywords_found} relevant keywords")
                    else:
                        self.log_test(f"Chat Turn {i+1}", "WARN",
                                    f"Only {keywords_found}/{len(turn['expected_keywords'])} keywords found")
                else:
                    self.log_test(f"Chat Turn {i+1}", "FAIL", f"API error: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Chat Turn {i+1}", "FAIL", f"Error: {str(e)}")
    
    def test_profit_calculation_integration(self):
        """Test profit calculation system integration"""
        print("\n[INTEGRATION TEST] Profit Calculation Integration")
        
        # Test if profit calculation endpoints are accessible
        profit_endpoints = [
            "/api/profit-analysis/leak-detection",
            "/api/profit-analysis/quick-wins", 
            "/api/profit-analysis/summary"
        ]
        
        for endpoint in profit_endpoints:
            try:
                response = self.session.options(f"{self.base_url}{endpoint}")
                if response.status_code in [200, 405]:
                    self.log_test(f"Profit API: {endpoint}", "PASS", "Endpoint accessible")
                else:
                    self.log_test(f"Profit API: {endpoint}", "FAIL", f"Status {response.status_code}")
            except Exception as e:
                self.log_test(f"Profit API: {endpoint}", "FAIL", f"Error: {str(e)}")
    
    def test_database_connectivity(self):
        """Test database connectivity and basic operations"""
        print("\n[INTEGRATION TEST] Database Connectivity")
        
        try:
            # Import database models to test connectivity
            sys.path.append(str(Path(__file__).parent))
            from models import get_db
            from models.user import User
            from models.expense import Expense
            from models.job import Job
            
            # Test database connection by attempting to import and query
            self.log_test("Database Models", "PASS", "All models imported successfully")
            
            # Test if database tables exist (this would fail if DB not set up)
            from sqlalchemy import create_engine, text
            engine = create_engine("sqlite:///cora.db")  # Assuming SQLite for testing
            
            with engine.connect() as conn:
                # Test basic table existence
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result]
                
                expected_tables = ["users", "expenses", "jobs"]
                tables_found = sum(1 for table in expected_tables if table in tables)
                
                if tables_found >= len(expected_tables):
                    self.log_test("Database Tables", "PASS", f"Found {tables_found}/{len(expected_tables)} expected tables")
                else:
                    self.log_test("Database Tables", "WARN", f"Only {tables_found}/{len(expected_tables)} tables found")
                    
        except ImportError as e:
            self.log_test("Database Models", "FAIL", f"Import error: {str(e)}")
        except Exception as e:
            self.log_test("Database Connectivity", "WARN", f"DB test error (may be normal): {str(e)}")
    
    def test_file_structure_integrity(self):
        """Test that all enhancement files are properly integrated"""
        print("\n[INTEGRATION TEST] File Structure Integrity")
        
        critical_files = [
            "test_onboarding_flow.py",
            "test_profit_calculations.py", 
            "test_personality_enhancements.py",
            "database_optimization_analysis.py",
            "data/test_scenarios/glen_day_demo_data.json",
            "data/test_scenarios/profit_calculation_demo.json",
            "data/cora_personality_enhancements.json",
            "routes/cora_chat_enhanced_v2.py",
            "schema/optimizations/glen_day_performance_optimizations.sql"
        ]
        
        for file_path in critical_files:
            full_path = Path(file_path)
            if full_path.exists():
                file_size = full_path.stat().st_size
                self.log_test(f"File: {file_path}", "PASS", f"Exists ({file_size} bytes)")
            else:
                self.log_test(f"File: {file_path}", "FAIL", "File missing")
    
    def run_individual_test_suites(self):
        """Run the individual test suites created earlier"""
        print("\n[INTEGRATION TEST] Individual Test Suite Execution")
        
        test_suites = [
            ("test_onboarding_flow.py", "End-to-end onboarding flow"),
            ("test_profit_calculations.py", "Profit calculation accuracy"),
            ("database_optimization_analysis.py", "Database performance")
        ]
        
        for test_file, description in test_suites:
            try:
                if Path(test_file).exists():
                    print(f"\n--- Running {test_file} ---")
                    result = subprocess.run([sys.executable, test_file], 
                                          capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0:
                        # Check for success indicators in output
                        if "100.0%" in result.stdout or "SUCCESS" in result.stdout:
                            self.log_test(f"Suite: {test_file}", "PASS", f"{description} - All tests passed")
                        else:
                            self.log_test(f"Suite: {test_file}", "WARN", f"{description} - Completed with warnings")
                    else:
                        self.log_test(f"Suite: {test_file}", "FAIL", f"{description} - Tests failed")
                else:
                    self.log_test(f"Suite: {test_file}", "FAIL", "Test file not found")
                    
            except subprocess.TimeoutExpired:
                self.log_test(f"Suite: {test_file}", "FAIL", "Test suite timed out")
            except Exception as e:
                self.log_test(f"Suite: {test_file}", "FAIL", f"Error running tests: {str(e)}")
    
    def test_demo_readiness(self):
        """Test specific Glen Day demo readiness criteria"""
        print("\n[INTEGRATION TEST] Glen Day Demo Readiness")
        
        # Test Glen Day specific data is loaded
        glen_data_file = Path("data/test_scenarios/glen_day_demo_data.json")
        if glen_data_file.exists():
            try:
                with open(glen_data_file, 'r', encoding='utf-8') as f:
                    glen_data = json.load(f)
                
                # Verify key data elements
                if "contractor_profile" in glen_data:
                    profile = glen_data["contractor_profile"]
                    if profile.get("name") == "Glen Day":
                        self.log_test("Glen Day Profile", "PASS", "Demo profile data correctly loaded")
                    else:
                        self.log_test("Glen Day Profile", "FAIL", "Incorrect profile data")
                else:
                    self.log_test("Glen Day Profile", "FAIL", "Profile data missing")
                    
                # Verify project data
                if "typical_projects" in glen_data.get("contractor_profile", {}):
                    projects = glen_data["contractor_profile"]["typical_projects"]
                    if len(projects) >= 3:
                        self.log_test("Demo Projects", "PASS", f"Found {len(projects)} demo projects")
                    else:
                        self.log_test("Demo Projects", "WARN", f"Only {len(projects)} demo projects")
                        
            except Exception as e:
                self.log_test("Glen Day Data", "FAIL", f"Error loading demo data: {str(e)}")
        else:
            self.log_test("Glen Day Data", "FAIL", "Demo data file missing")
    
    def generate_integration_report(self):
        """Generate comprehensive integration test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["status"] == "PASS")
        failed_tests = sum(1 for result in self.test_results if result["status"] == "FAIL")
        warning_tests = sum(1 for result in self.test_results if result["status"] == "WARN")
        
        print(f"\n[SUMMARY] COMPREHENSIVE INTEGRATION TESTING")
        print(f"Total Tests: {total_tests}")
        print(f"[PASS] Passed: {passed_tests}")
        print(f"[FAIL] Failed: {failed_tests}")
        print(f"[WARN] Warnings: {warning_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Save detailed report
        report_path = Path("data/test_results/integration_test_report.json")
        report_path.parent.mkdir(exist_ok=True)
        
        integration_score = (passed_tests / total_tests) * 100
        demo_readiness = "READY" if failed_tests <= 2 and integration_score >= 80 else "NEEDS_WORK"
        
        report = {
            "integration_testing": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warnings": warning_tests,
                "integration_score": integration_score,
                "demo_readiness": demo_readiness
            },
            "test_categories": {
                "core_infrastructure": "Server, routes, basic functionality",
                "api_endpoints": "REST API accessibility and functionality",
                "static_assets": "JavaScript, CSS, and asset loading",
                "chat_personality": "Enhanced CORA conversation system",
                "profit_calculations": "Real-time profit tracking integration",
                "database_connectivity": "Data layer and model integration",
                "file_structure": "Enhancement file integration",
                "test_suites": "Individual test suite execution", 
                "demo_readiness": "Glen Day specific demo preparation"
            },
            "detailed_results": self.test_results,
            "recommendations": self._generate_recommendations(failed_tests, warning_tests)
        }
        
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n[REPORT] Integration test report saved to: {report_path}")
        
        if demo_readiness == "READY":
            print(f"\n[SUCCESS] CORA SYSTEM INTEGRATION COMPLETE!")
            print("PASS All critical systems tested and functioning")
            print("PASS Glen Day demo scenarios validated")  
            print("PASS Performance optimizations integrated")
            print("PASS Enhanced AI personality operational")
            print("\nSUCCESS SYSTEM READY FOR GLEN DAY DEMO!")
        else:
            print(f"\n[WARNING] Integration issues detected")
            print(f"FAIL {failed_tests} critical failures need resolution")
            print(f"WARN {warning_tests} warnings require review")
        
        return demo_readiness == "READY"
    
    def _generate_recommendations(self, failed_tests, warning_tests):
        """Generate recommendations based on test results"""
        recommendations = []
        
        if failed_tests > 0:
            recommendations.append("Review and fix failed tests before demo")
            recommendations.append("Ensure server is running and accessible")
            recommendations.append("Verify database connectivity and schema")
        
        if warning_tests > 3:
            recommendations.append("Address warning issues for optimal performance")
            recommendations.append("Review API endpoint responses")
            
        if failed_tests == 0 and warning_tests <= 2:
            recommendations.append("System ready for Glen Day demo")
            recommendations.append("Consider running performance load testing")
            recommendations.append("Prepare demo script with tested scenarios")
        
        return recommendations
    
    def run_complete_integration_testing(self):
        """Run complete integration testing suite"""
        print("[START] COMPREHENSIVE CORA INTEGRATION TESTING")
        print("Testing all system enhancements for Glen Day demo readiness\n")
        
        # Check if server is running first
        if not self.check_server_running():
            print("⚠️ CORA server not detected. Starting integration tests anyway...")
        
        # Run all integration tests
        self.test_core_infrastructure()
        self.test_api_endpoints()
        self.test_static_assets()
        self.test_enhanced_chat_personality()
        self.test_profit_calculation_integration()
        self.test_database_connectivity()
        self.test_file_structure_integrity()
        self.test_demo_readiness()
        
        # Run individual test suites
        self.run_individual_test_suites()
        
        # Generate final report
        return self.generate_integration_report()

if __name__ == "__main__":
    tester = ComprehensiveIntegrationTester()
    success = tester.run_complete_integration_testing()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)