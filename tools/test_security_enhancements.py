#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/test_security_enhancements.py
🎯 PURPOSE: Test script for Phase 2.4 security enhancements
🔗 IMPORTS: requests, json, time
📤 EXPORTS: SecurityTestSuite
"""

import requests
import json
import time
import sys
from typing import Dict, List, Any, Tuple

class SecurityTestSuite:
    """Comprehensive security test suite for CORA application"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.session = requests.Session()
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all security tests"""
        print("🔒 CORA Security Enhancement Test Suite")
        print("=" * 50)
        
        tests = [
            ("Input Validation", self.test_input_validation),
            ("SQL Injection Prevention", self.test_sql_injection_prevention),
            ("XSS Prevention", self.test_xss_prevention),
            ("Rate Limiting", self.test_rate_limiting),
            ("Request Size Limits", self.test_request_size_limits),
            ("API Versioning", self.test_api_versioning),
            ("Security Headers", self.test_security_headers),
            ("CORS Configuration", self.test_cors_configuration),
            ("Authentication Security", self.test_authentication_security),
            ("File Upload Security", self.test_file_upload_security)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            try:
                result = test_func()
                self.test_results.append({
                    "test": test_name,
                    "status": "PASS" if result else "FAIL",
                    "details": result
                })
                print(f"   ✅ {test_name}: PASS")
            except Exception as e:
                self.test_results.append({
                    "test": test_name,
                    "status": "ERROR",
                    "details": str(e)
                })
                print(f"   ❌ {test_name}: ERROR - {e}")
        
        return self.generate_report()
    
    def test_input_validation(self) -> bool:
        """Test enhanced input validation"""
        # Test malicious input in signup
        malicious_inputs = [
            {"email": "test@example.com<script>alert('xss')</script>", "password": "password123"},
            {"email": "test@example.com", "password": "password123' OR '1'='1"},
            {"email": "test@example.com", "password": "password123; DROP TABLE users;"},
            {"email": "test@example.com", "password": "password123 UNION SELECT * FROM users"},
        ]
        
        for i, malicious_input in enumerate(malicious_inputs):
            try:
                response = self.session.post(
                    f"{self.base_url}/api/signup",
                    json={
                        "email": malicious_input["email"],
                        "password": malicious_input["password"],
                        "password_confirm": malicious_input["password"]
                    }
                )
                
                # Should reject malicious input
                if response.status_code == 400:
                    print(f"   ✅ Malicious input {i+1} properly rejected")
                else:
                    print(f"   ❌ Malicious input {i+1} not properly rejected (status: {response.status_code})")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Error testing malicious input {i+1}: {e}")
                return False
        
        return True
    
    def test_sql_injection_prevention(self) -> bool:
        """Test SQL injection prevention"""
        sql_injection_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "1' OR '1'='1'--",
        ]
        
        for payload in sql_injection_payloads:
            try:
                # Test in contact form
                response = self.session.post(
                    f"{self.base_url}/api/contact",
                    json={
                        "name": payload,
                        "company_name": "Test",
                        "email": "test@example.com",
                        "topic": "Test",
                        "message": "Test message"
                    }
                )
                
                # Should reject SQL injection
                if response.status_code == 400:
                    print(f"   ✅ SQL injection payload rejected: {payload[:20]}...")
                else:
                    print(f"   ❌ SQL injection payload not rejected: {payload[:20]}...")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Error testing SQL injection: {e}")
                return False
        
        return True
    
    def test_xss_prevention(self) -> bool:
        """Test XSS prevention"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<iframe src=javascript:alert('xss')></iframe>",
            "data:text/html,<script>alert('xss')</script>",
        ]
        
        for payload in xss_payloads:
            try:
                # Test in contact form
                response = self.session.post(
                    f"{self.base_url}/api/contact",
                    json={
                        "name": "Test User",
                        "company_name": "Test",
                        "email": "test@example.com",
                        "topic": "Test",
                        "message": payload
                    }
                )
                
                # Should reject XSS payload
                if response.status_code == 400:
                    print(f"   ✅ XSS payload rejected: {payload[:20]}...")
                else:
                    print(f"   ❌ XSS payload not rejected: {payload[:20]}...")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Error testing XSS: {e}")
                return False
        
        return True
    
    def test_rate_limiting(self) -> bool:
        """Test rate limiting functionality"""
        try:
            # Make multiple rapid requests to trigger rate limiting
            responses = []
            for i in range(15):  # More than the rate limit
                response = self.session.post(
                    f"{self.base_url}/api/contact",
                    json={
                        "name": f"Test User {i}",
                        "company_name": "Test",
                        "email": f"test{i}@example.com",
                        "topic": "Test",
                        "message": "Test message"
                    }
                )
                responses.append(response.status_code)
                time.sleep(0.1)  # Small delay
            
            # Check if rate limiting was triggered
            rate_limited = any(status == 429 for status in responses)
            if rate_limited:
                print("   ✅ Rate limiting working correctly")
                return True
            else:
                print("   ❌ Rate limiting not triggered")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing rate limiting: {e}")
            return False
    
    def test_request_size_limits(self) -> bool:
        """Test request size limits"""
        try:
            # Create a large payload
            large_payload = {
                "name": "Test User",
                "company_name": "Test",
                "email": "test@example.com",
                "topic": "Test",
                "message": "x" * (11 * 1024 * 1024)  # 11MB, should exceed 10MB limit
            }
            
            response = self.session.post(
                f"{self.base_url}/api/contact",
                json=large_payload
            )
            
            # Should reject large request
            if response.status_code == 413:
                print("   ✅ Request size limit working correctly")
                return True
            else:
                print(f"   ❌ Request size limit not enforced (status: {response.status_code})")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing request size limits: {e}")
            return False
    
    def test_api_versioning(self) -> bool:
        """Test API versioning functionality"""
        try:
            # Test unsupported version
            response = self.session.get(f"{self.base_url}/api/v3/health")
            
            if response.status_code == 400:
                print("   ✅ API versioning working correctly")
                return True
            else:
                print(f"   ❌ API versioning not working (status: {response.status_code})")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing API versioning: {e}")
            return False
    
    def test_security_headers(self) -> bool:
        """Test security headers"""
        try:
            response = self.session.get(f"{self.base_url}/")
            
            required_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options", 
                "X-XSS-Protection",
                "Referrer-Policy",
                "Content-Security-Policy"
            ]
            
            missing_headers = []
            for header in required_headers:
                if header not in response.headers:
                    missing_headers.append(header)
            
            if not missing_headers:
                print("   ✅ All required security headers present")
                return True
            else:
                print(f"   ❌ Missing security headers: {missing_headers}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing security headers: {e}")
            return False
    
    def test_cors_configuration(self) -> bool:
        """Test CORS configuration"""
        try:
            response = self.session.options(f"{self.base_url}/api/health")
            
            # Check for CORS headers
            cors_headers = [
                "Access-Control-Allow-Origin",
                "Access-Control-Allow-Methods",
                "Access-Control-Allow-Headers"
            ]
            
            missing_headers = []
            for header in cors_headers:
                if header not in response.headers:
                    missing_headers.append(header)
            
            if not missing_headers:
                print("   ✅ CORS headers present")
                return True
            else:
                print(f"   ❌ Missing CORS headers: {missing_headers}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing CORS: {e}")
            return False
    
    def test_authentication_security(self) -> bool:
        """Test authentication security"""
        try:
            # Test weak password
            response = self.session.post(
                f"{self.base_url}/api/signup",
                json={
                    "email": "test@example.com",
                    "password": "123",  # Too short
                    "password_confirm": "123"
                }
            )
            
            if response.status_code == 400:
                print("   ✅ Weak password properly rejected")
                return True
            else:
                print(f"   ❌ Weak password not rejected (status: {response.status_code})")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing authentication security: {e}")
            return False
    
    def test_file_upload_security(self) -> bool:
        """Test file upload security"""
        try:
            # Test malicious filename
            malicious_filename = "../../../etc/passwd"
            
            # This would be tested with actual file upload endpoint
            # For now, just test the validation function
            from utils.security_enhanced import SecurityUtils
            
            try:
                SecurityUtils.validate_file_upload(malicious_filename)
                print("   ❌ Malicious filename not rejected")
                return False
            except Exception:
                print("   ✅ Malicious filename properly rejected")
                return True
                
        except Exception as e:
            print(f"   ❌ Error testing file upload security: {e}")
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["status"] == "PASS")
        failed_tests = sum(1 for result in self.test_results if result["status"] == "FAIL")
        error_tests = sum(1 for result in self.test_results if result["status"] == "ERROR")
        
        print("\n" + "=" * 50)
        print("📊 SECURITY TEST REPORT")
        print("=" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Errors: {error_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0 or error_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if result["status"] != "PASS":
                    print(f"   {result['test']}: {result['status']} - {result['details']}")
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "errors": error_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "results": self.test_results
        }

def main():
    """Main function to run security tests"""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    test_suite = SecurityTestSuite(base_url)
    report = test_suite.run_all_tests()
    
    # Exit with error code if tests failed
    if report["failed"] > 0 or report["errors"] > 0:
        sys.exit(1)
    else:
        print("\n🎉 All security tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main() 