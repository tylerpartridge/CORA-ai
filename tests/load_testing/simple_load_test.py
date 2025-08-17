#!/usr/bin/env python3
"""
Simple load testing script for CORA application
Uses asyncio and aiohttp for basic load testing without external dependencies
"""

import asyncio
import aiohttp
import time
import json
import statistics
from typing import List, Dict, Tuple
from datetime import datetime
import sys

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_SCENARIOS = {
    "smoke": {"users": 5, "requests_per_user": 10, "duration": 60},
    "load": {"users": 50, "requests_per_user": 20, "duration": 120},
    "stress": {"users": 100, "requests_per_user": 30, "duration": 180}
}

class SimpleLoadTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results = []
        
    async def make_request(self, session: aiohttp.ClientSession, endpoint: str, method: str = "GET") -> Tuple[float, int, str]:
        """Make a single request and return response time, status, and any error"""
        start_time = time.time()
        error = None
        status = 0
        
        try:
            url = f"{self.base_url}{endpoint}"
            async with session.request(method, url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                status = response.status
                await response.text()
        except asyncio.TimeoutError:
            error = "Timeout"
        except Exception as e:
            error = str(e)
            
        response_time = time.time() - start_time
        return response_time, status, error
        
    async def run_user_simulation(self, session: aiohttp.ClientSession, user_id: int, requests: int) -> List[Dict]:
        """Simulate a single user making requests"""
        user_results = []
        
        # Test different endpoints
        endpoints = [
            ("/health", "GET"),
            ("/", "GET"),
            ("/api/status", "GET"),
            ("/onboarding", "GET"),
        ]
        
        for i in range(requests):
            endpoint, method = endpoints[i % len(endpoints)]
            response_time, status, error = await self.make_request(session, endpoint, method)
            
            user_results.append({
                "user_id": user_id,
                "request_num": i,
                "endpoint": endpoint,
                "response_time": response_time,
                "status_code": status,
                "error": error,
                "timestamp": datetime.now().isoformat()
            })
            
            # Small delay between requests
            await asyncio.sleep(0.5)
            
        return user_results
        
    async def run_test(self, scenario_name: str) -> Dict:
        """Run a load test scenario"""
        scenario = TEST_SCENARIOS[scenario_name]
        print(f"\nRunning {scenario_name.upper()} test...")
        print(f"  Users: {scenario['users']}")
        print(f"  Requests per user: {scenario['requests_per_user']}")
        
        connector = aiohttp.TCPConnector(limit=scenario['users'])
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = []
            for user_id in range(scenario['users']):
                task = self.run_user_simulation(session, user_id, scenario['requests_per_user'])
                tasks.append(task)
                
            start_time = time.time()
            all_results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
        # Process results
        results = []
        for user_results in all_results:
            if isinstance(user_results, Exception):
                print(f"  User simulation failed: {user_results}")
            else:
                results.extend(user_results)
                
        # Calculate metrics
        response_times = [r["response_time"] for r in results if r["error"] is None]
        errors = [r for r in results if r["error"] is not None]
        status_codes = [r["status_code"] for r in results if r["status_code"] > 0]
        
        metrics = {
            "scenario": scenario_name,
            "total_requests": len(results),
            "successful_requests": len(response_times),
            "failed_requests": len(errors),
            "total_test_time": total_time,
            "requests_per_second": len(results) / total_time if total_time > 0 else 0,
            "response_times": {
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "mean": statistics.mean(response_times) if response_times else 0,
                "median": statistics.median(response_times) if response_times else 0,
                "p95": sorted(response_times)[int(len(response_times) * 0.95)] if response_times else 0,
                "p99": sorted(response_times)[int(len(response_times) * 0.99)] if response_times else 0
            },
            "status_codes": {}
        }
        
        # Count status codes
        for code in set(status_codes):
            metrics["status_codes"][str(code)] = status_codes.count(code)
            
        # Count error types
        if errors:
            error_types = {}
            for error in errors:
                error_type = error["error"]
                error_types[error_type] = error_types.get(error_type, 0) + 1
            metrics["error_types"] = error_types
            
        return metrics
        
    def print_results(self, metrics: Dict):
        """Print test results"""
        print(f"\nResults for {metrics['scenario'].upper()} test:")
        print(f"  Total Requests: {metrics['total_requests']}")
        print(f"  Successful: {metrics['successful_requests']}")
        print(f"  Failed: {metrics['failed_requests']}")
        print(f"  Requests/sec: {metrics['requests_per_second']:.2f}")
        print(f"  Response Times:")
        print(f"    Min: {metrics['response_times']['min']:.3f}s")
        print(f"    Mean: {metrics['response_times']['mean']:.3f}s")
        print(f"    Median: {metrics['response_times']['median']:.3f}s")
        print(f"    95th percentile: {metrics['response_times']['p95']:.3f}s")
        print(f"    99th percentile: {metrics['response_times']['p99']:.3f}s")
        print(f"    Max: {metrics['response_times']['max']:.3f}s")
        
        if metrics['status_codes']:
            print(f"  Status Codes: {metrics['status_codes']}")
        if metrics.get('error_types'):
            print(f"  Errors: {metrics['error_types']}")
            
    def analyze_results(self, metrics: Dict) -> Dict:
        """Analyze results and provide recommendations"""
        analysis = {
            "passed": True,
            "issues": [],
            "recommendations": []
        }
        
        # Check response times
        if metrics['response_times']['p95'] > 1.0:
            analysis["passed"] = False
            analysis["issues"].append(f"P95 response time ({metrics['response_times']['p95']:.3f}s) exceeds 1 second")
            
        if metrics['response_times']['p99'] > 2.0:
            analysis["issues"].append(f"P99 response time ({metrics['response_times']['p99']:.3f}s) exceeds 2 seconds")
            
        # Check error rate
        error_rate = metrics['failed_requests'] / metrics['total_requests'] if metrics['total_requests'] > 0 else 0
        if error_rate > 0.01:  # 1% threshold
            analysis["passed"] = False
            analysis["issues"].append(f"Error rate ({error_rate:.1%}) exceeds 1% threshold")
            
        # Check requests per second
        if metrics['requests_per_second'] < 10:
            analysis["issues"].append(f"Low throughput: {metrics['requests_per_second']:.2f} requests/sec")
            
        # Add recommendations
        if analysis["issues"]:
            analysis["recommendations"].extend([
                "Consider implementing caching for frequently accessed endpoints",
                "Review database query optimization",
                "Check for N+1 query problems",
                "Consider implementing connection pooling",
                "Review server resource allocation"
            ])
        else:
            analysis["recommendations"].append("System performs well under tested load")
            
        return analysis

async def main():
    """Run load tests"""
    print("CORA Simple Load Testing Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status != 200:
                    print(f"WARNING: Health check returned status {response.status}")
    except Exception as e:
        print(f"ERROR: Cannot connect to {BASE_URL} - {e}")
        print("Make sure the CORA application is running")
        return 1
        
    tester = SimpleLoadTester()
    
    # Run tests
    test_order = ["smoke", "load", "stress"]
    all_results = []
    
    for test_name in test_order:
        if len(sys.argv) > 1 and sys.argv[1] != "all" and sys.argv[1] != test_name:
            continue
            
        try:
            metrics = await tester.run_test(test_name)
            tester.print_results(metrics)
            
            # Analyze results
            analysis = tester.analyze_results(metrics)
            
            print(f"\nAnalysis:")
            print(f"  Test {'PASSED' if analysis['passed'] else 'FAILED'}")
            
            if analysis['issues']:
                print("  Issues found:")
                for issue in analysis['issues']:
                    print(f"    - {issue}")
                    
            print("  Recommendations:")
            for rec in analysis['recommendations']:
                print(f"    - {rec}")
                
            all_results.append({
                "test": test_name,
                "metrics": metrics,
                "analysis": analysis
            })
            
            # Wait between tests
            if test_name != test_order[-1]:
                print("\nWaiting 10 seconds before next test...")
                await asyncio.sleep(10)
                
        except Exception as e:
            print(f"ERROR: {test_name} test failed - {e}")
            
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"load_test_report_{timestamp}.json"
    
    with open(report_file, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "base_url": BASE_URL,
            "results": all_results
        }, f, indent=2)
        
    print(f"\nReport saved to: {report_file}")
    
    # Overall summary
    print("\n" + "=" * 50)
    print("OVERALL SUMMARY:")
    
    all_passed = all(r["analysis"]["passed"] for r in all_results)
    print(f"  Overall: {'PASSED' if all_passed else 'FAILED'}")
    
    total_issues = sum(len(r["analysis"]["issues"]) for r in all_results)
    if total_issues > 0:
        print(f"  Total issues found: {total_issues}")
        
    return 0 if all_passed else 1

if __name__ == "__main__":
    # Handle command line arguments
    if len(sys.argv) > 1 and sys.argv[1] in ["smoke", "load", "stress"]:
        print(f"Running {sys.argv[1]} test only")
    elif len(sys.argv) > 1 and sys.argv[1] != "all":
        print("Usage: python simple_load_test.py [smoke|load|stress|all]")
        sys.exit(1)
        
    exit_code = asyncio.run(main())
    sys.exit(exit_code)