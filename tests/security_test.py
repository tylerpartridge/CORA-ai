#!/usr/bin/env python3
"""
Security Testing Suite for CORA Application
Tests for common vulnerabilities and security best practices
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Tuple
from datetime import datetime
import sys

BASE_URL = "http://localhost:8000"

class SecurityTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results = []
        
    async def test_security_headers(self, session: aiohttp.ClientSession) -> Dict:
        """Test for security headers"""
        results = {
            "test": "Security Headers",
            "passed": True,
            "issues": []
        }
        
        try:
            async with session.get(f"{self.base_url}/") as response:
                headers = response.headers
                
                # Check for important security headers
                security_headers = {
                    "X-Content-Type-Options": "nosniff",
                    "X-Frame-Options": ["DENY", "SAMEORIGIN"],
                    "X-XSS-Protection": "1; mode=block",
                    "Strict-Transport-Security": None,  # Optional for local testing
                    "Content-Security-Policy": None,  # Should be present
                }
                
                for header, expected in security_headers.items():
                    if header not in headers:
                        if header in ["Strict-Transport-Security"]:  # Optional for HTTP
                            continue
                        results["passed"] = False
                        results["issues"].append(f"Missing security header: {header}")
                    elif expected and headers[header] not in (expected if isinstance(expected, list) else [expected]):
                        results["passed"] = False
                        results["issues"].append(f"Incorrect {header}: {headers[header]}")
                        
        except Exception as e:
            results["passed"] = False
            results["issues"].append(f"Error testing headers: {str(e)}")
            
        return results
        
    async def test_sql_injection(self, session: aiohttp.ClientSession) -> Dict:
        """Test for SQL injection vulnerabilities"""
        results = {
            "test": "SQL Injection",
            "passed": True,
            "issues": []
        }
        
        # SQL injection payloads
        payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' UNION SELECT * FROM users--",
            "admin'--",
            "1 OR 1=1",
        ]
        
        # Test endpoints that might accept user input
        test_endpoints = [
            ("/api/auth/login", "POST", {"email": "test@example.com", "password": "payload"}),
            ("/api/expenses", "GET", {"search": "payload"}),
            ("/api/onboarding/chat/message", "POST", {"message": "payload"}),
        ]
        
        for endpoint, method, data_template in test_endpoints:
            for payload in payloads:
                try:
                    # Replace payload in data
                    data = {}
                    for key, value in data_template.items():
                        data[key] = payload if value == "payload" else value
                        
                    if method == "GET":
                        url = f"{self.base_url}{endpoint}"
                        async with session.get(url, params=data) as response:
                            # Check for SQL error messages in response
                            text = await response.text()
                            sql_errors = ["sql", "syntax error", "mysql", "postgresql", "sqlite"]
                            for error in sql_errors:
                                if error.lower() in text.lower():
                                    results["passed"] = False
                                    results["issues"].append(f"Potential SQL injection at {endpoint}: {error} found in response")
                                    break
                    else:
                        url = f"{self.base_url}{endpoint}"
                        async with session.post(url, json=data) as response:
                            text = await response.text()
                            sql_errors = ["sql", "syntax error", "mysql", "postgresql", "sqlite"]
                            for error in sql_errors:
                                if error.lower() in text.lower():
                                    results["passed"] = False
                                    results["issues"].append(f"Potential SQL injection at {endpoint}: {error} found in response")
                                    break
                                    
                except Exception as e:
                    # Connection errors are expected for some payloads
                    pass
                    
        return results
        
    async def test_xss(self, session: aiohttp.ClientSession) -> Dict:
        """Test for Cross-Site Scripting (XSS) vulnerabilities"""
        results = {
            "test": "Cross-Site Scripting (XSS)",
            "passed": True,
            "issues": []
        }
        
        # XSS payloads
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//",
        ]
        
        # Test endpoints that might reflect user input
        test_endpoints = [
            ("/api/onboarding/chat/message", {"message": "payload"}),
            ("/api/expenses", {"description": "payload"}),
        ]
        
        for endpoint, data_template in test_endpoints:
            for payload in payloads:
                try:
                    data = {}
                    for key, value in data_template.items():
                        data[key] = payload if value == "payload" else value
                        
                    url = f"{self.base_url}{endpoint}"
                    async with session.post(url, json=data) as response:
                        text = await response.text()
                        # Check if payload is reflected without encoding
                        if payload in text:
                            results["passed"] = False
                            results["issues"].append(f"Potential XSS at {endpoint}: payload reflected in response")
                            
                except Exception as e:
                    pass
                    
        return results
        
    async def test_authentication(self, session: aiohttp.ClientSession) -> Dict:
        """Test authentication security"""
        results = {
            "test": "Authentication Security",
            "passed": True,
            "issues": []
        }
        
        # Test protected endpoints without auth
        protected_endpoints = [
            "/dashboard",
            "/api/expenses",
            "/api/admin/stats",
            "/api/profit-analysis/summary",
        ]
        
        for endpoint in protected_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                async with session.get(url) as response:
                    if response.status == 200:
                        # Check if it's actually protected
                        text = await response.text()
                        if "login" not in text.lower() and "unauthorized" not in text.lower():
                            results["passed"] = False
                            results["issues"].append(f"Endpoint {endpoint} accessible without authentication")
                            
            except Exception as e:
                pass
                
        # Test weak passwords
        weak_passwords = ["123456", "password", "admin", "12345678", "qwerty"]
        for password in weak_passwords:
            try:
                url = f"{self.base_url}/api/auth/register"
                data = {
                    "email": f"test{int(time.time())}@example.com",
                    "password": password,
                    "confirm_password": password
                }
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        results["passed"] = False
                        results["issues"].append(f"Weak password '{password}' accepted")
                        
            except Exception as e:
                pass
                
        return results
        
    async def test_rate_limiting(self, session: aiohttp.ClientSession) -> Dict:
        """Test rate limiting"""
        results = {
            "test": "Rate Limiting",
            "passed": True,
            "issues": []
        }
        
        # Test rapid requests
        endpoint = f"{self.base_url}/api/auth/login"
        data = {"email": "test@example.com", "password": "wrongpassword"}
        
        blocked = False
        for i in range(20):  # Try 20 rapid requests
            try:
                async with session.post(endpoint, json=data) as response:
                    if response.status == 429:  # Too Many Requests
                        blocked = True
                        break
            except Exception as e:
                pass
                
        if not blocked:
            results["passed"] = False
            results["issues"].append("No rate limiting detected on login endpoint")
            
        return results
        
    async def test_csrf(self, session: aiohttp.ClientSession) -> Dict:
        """Test CSRF protection"""
        results = {
            "test": "CSRF Protection",
            "passed": True,
            "issues": []
        }
        
        # Test state-changing operations without CSRF token
        endpoints = [
            ("/api/expenses", "POST", {"amount": 100, "description": "Test"}),
            ("/api/auth/logout", "POST", {}),
        ]
        
        for endpoint, method, data in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                # Make request without any CSRF token
                headers = {"Origin": "http://evil.com"}
                async with session.request(method, url, json=data, headers=headers) as response:
                    # If request succeeds without CSRF token, it's a vulnerability
                    if response.status in [200, 201]:
                        text = await response.text()
                        if "csrf" not in text.lower():
                            results["issues"].append(f"Potential CSRF vulnerability at {endpoint}")
                            
            except Exception as e:
                pass
                
        return results
        
    async def test_information_disclosure(self, session: aiohttp.ClientSession) -> Dict:
        """Test for information disclosure"""
        results = {
            "test": "Information Disclosure",
            "passed": True,
            "issues": []
        }
        
        # Test for debug endpoints
        debug_endpoints = [
            "/.env",
            "/config",
            "/debug",
            "/.git/config",
            "/backup",
            "/api/debug",
        ]
        
        for endpoint in debug_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                async with session.get(url) as response:
                    if response.status == 200:
                        results["passed"] = False
                        results["issues"].append(f"Sensitive endpoint exposed: {endpoint}")
                        
            except Exception as e:
                pass
                
        # Test error messages
        try:
            url = f"{self.base_url}/api/this-does-not-exist"
            async with session.get(url) as response:
                text = await response.text()
                # Check for stack traces or sensitive info
                sensitive_patterns = ["traceback", "stacktrace", "line", "file", "debug"]
                for pattern in sensitive_patterns:
                    if pattern.lower() in text.lower():
                        results["passed"] = False
                        results["issues"].append(f"Stack trace or debug info exposed in error messages")
                        break
                        
        except Exception as e:
            pass
            
        return results
        
    def print_results(self, all_results: List[Dict]):
        """Print security test results"""
        print("\n" + "=" * 60)
        print("SECURITY TEST RESULTS")
        print("=" * 60)
        
        passed_count = sum(1 for r in all_results if r["passed"])
        total_count = len(all_results)
        
        print(f"\nOverall: {passed_count}/{total_count} tests passed")
        
        for result in all_results:
            status = "PASSED" if result["passed"] else "FAILED"
            print(f"\n{result['test']}: {status}")
            
            if result["issues"]:
                print("  Issues found:")
                for issue in result["issues"]:
                    print(f"    - {issue}")
                    
        # Summary
        print("\n" + "=" * 60)
        if passed_count == total_count:
            print("SECURITY STATUS: EXCELLENT")
            print("All security tests passed!")
        else:
            print("SECURITY STATUS: NEEDS ATTENTION")
            print(f"{total_count - passed_count} security issues found")
            
async def main():
    """Run security tests"""
    print("CORA Security Testing Suite")
    print("=" * 60)
    
    # First restart the app
    print("Starting CORA application...")
    import subprocess
    import os
    
    # Kill any existing app
    if os.name == 'nt':  # Windows
        subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/FI", "WINDOWTITLE eq app.py*"], capture_output=True)
    else:
        subprocess.run(["pkill", "-f", "app.py"], capture_output=True)
        
    # Start the app
    app_process = subprocess.Popen(["python", "app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for app to start
    print("Waiting for app to start...")
    await asyncio.sleep(5)
    
    # Check if app is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status != 200:
                    print("ERROR: App not responding")
                    return 1
    except Exception as e:
        print(f"ERROR: Cannot connect to app - {e}")
        return 1
        
    tester = SecurityTester()
    all_results = []
    
    # Run security tests
    async with aiohttp.ClientSession() as session:
        # Test security headers
        print("\nTesting security headers...")
        result = await tester.test_security_headers(session)
        all_results.append(result)
        
        # Test SQL injection
        print("Testing SQL injection protection...")
        result = await tester.test_sql_injection(session)
        all_results.append(result)
        
        # Test XSS
        print("Testing XSS protection...")
        result = await tester.test_xss(session)
        all_results.append(result)
        
        # Test authentication
        print("Testing authentication security...")
        result = await tester.test_authentication(session)
        all_results.append(result)
        
        # Test rate limiting
        print("Testing rate limiting...")
        result = await tester.test_rate_limiting(session)
        all_results.append(result)
        
        # Test CSRF
        print("Testing CSRF protection...")
        result = await tester.test_csrf(session)
        all_results.append(result)
        
        # Test information disclosure
        print("Testing information disclosure...")
        result = await tester.test_information_disclosure(session)
        all_results.append(result)
        
    # Print results
    tester.print_results(all_results)
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"security_test_report_{timestamp}.json"
    
    with open(report_file, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "base_url": BASE_URL,
            "results": all_results,
            "summary": {
                "total_tests": len(all_results),
                "passed": sum(1 for r in all_results if r["passed"]),
                "failed": sum(1 for r in all_results if not r["passed"])
            }
        }, f, indent=2)
        
    print(f"\nReport saved to: {report_file}")
    
    # Cleanup - stop the app
    app_process.terminate()
    
    return 0 if all(r["passed"] for r in all_results) else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)