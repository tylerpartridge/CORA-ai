#!/usr/bin/env python3
"""
Performance Baseline Measurement Script
Purpose: Establish baseline metrics for API endpoints
Author: Claude (Opus 4.1)
Date: 2025-08-10
Safety: Read-only measurements, no system changes
"""

import time
import json
import statistics
from datetime import datetime
from pathlib import Path

def measure_endpoint_performance():
    """Measure response times for key endpoints"""
    
    print("="*60)
    print("PERFORMANCE BASELINE MEASUREMENT")
    print("="*60)
    print("\nThis will test endpoint response times.")
    print("Note: Requires the server to be running on localhost:8000\n")
    
    try:
        import httpx
    except ImportError:
        print("httpx not installed. Installing...")
        import subprocess
        subprocess.run(["pip", "install", "httpx"], capture_output=True)
        import httpx
    
    # Define endpoints to test
    endpoints = [
        {"path": "/health", "method": "GET", "name": "Health Check"},
        {"path": "/api/status", "method": "GET", "name": "API Status"},
        {"path": "/", "method": "GET", "name": "Landing Page"},
        {"path": "/login", "method": "GET", "name": "Login Page"},
        {"path": "/signup", "method": "GET", "name": "Signup Page"},
        {"path": "/pricing", "method": "GET", "name": "Pricing Page"},
        {"path": "/features", "method": "GET", "name": "Features Page"},
    ]
    
    results = []
    
    with httpx.Client(base_url="http://localhost:8000", timeout=10.0) as client:
        for endpoint in endpoints:
            print(f"Testing {endpoint['name']}...")
            times = []
            errors = 0
            
            # Make 5 requests to get average
            for i in range(5):
                try:
                    start = time.time()
                    
                    if endpoint['method'] == 'GET':
                        response = client.get(endpoint['path'])
                    else:
                        response = client.post(endpoint['path'])
                    
                    duration = (time.time() - start) * 1000  # Convert to ms
                    times.append(duration)
                    
                    # Brief pause between requests
                    time.sleep(0.1)
                    
                except Exception as e:
                    errors += 1
                    print(f"  Error: {e}")
            
            if times:
                result = {
                    "endpoint": endpoint['path'],
                    "name": endpoint['name'],
                    "method": endpoint['method'],
                    "avg_ms": round(statistics.mean(times), 2),
                    "min_ms": round(min(times), 2),
                    "max_ms": round(max(times), 2),
                    "median_ms": round(statistics.median(times), 2),
                    "errors": errors,
                    "samples": len(times)
                }
                results.append(result)
                
                # Print inline result
                print(f"  ✓ {result['name']}: {result['avg_ms']}ms avg")
            else:
                print(f"  ✗ {endpoint['name']}: Failed all attempts")
    
    return results

def generate_baseline_report(results):
    """Generate performance baseline report"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""# Performance Baseline Report
**Generated:** {timestamp}
**Total Endpoints Tested:** {len(results)}

## Summary Statistics

| Endpoint | Avg (ms) | Min (ms) | Max (ms) | Status |
|----------|----------|----------|----------|--------|
"""
    
    for r in results:
        status = "✅ Good" if r['avg_ms'] < 200 else "⚠️ Slow" if r['avg_ms'] < 500 else "❌ Critical"
        report += f"| {r['name']} | {r['avg_ms']} | {r['min_ms']} | {r['max_ms']} | {status} |\n"
    
    # Calculate overall stats
    all_avgs = [r['avg_ms'] for r in results]
    overall_avg = round(statistics.mean(all_avgs), 2)
    
    report += f"""
## Overall Performance

- **Average Response Time:** {overall_avg}ms
- **Fastest Endpoint:** {min(results, key=lambda x: x['avg_ms'])['name']} ({min(all_avgs)}ms)
- **Slowest Endpoint:** {max(results, key=lambda x: x['avg_ms'])['name']} ({max(all_avgs)}ms)

## Performance Targets

| Category | Target | Current | Status |
|----------|--------|---------|--------|
| API Endpoints | <100ms | {overall_avg}ms | {'✅' if overall_avg < 100 else '❌'} |
| Page Loads | <200ms | - | - |
| Database Queries | <50ms | - | - |

## Recommendations

"""
    
    # Add recommendations based on results
    slow_endpoints = [r for r in results if r['avg_ms'] > 200]
    if slow_endpoints:
        report += "### Slow Endpoints Needing Optimization:\n"
        for endpoint in slow_endpoints:
            report += f"- **{endpoint['name']}** ({endpoint['avg_ms']}ms) - "
            if endpoint['avg_ms'] > 500:
                report += "Critical performance issue\n"
            else:
                report += "Consider caching or query optimization\n"
    else:
        report += "### All endpoints performing within acceptable limits!\n"
    
    report += """
## Next Steps

1. Run load testing to measure performance under stress
2. Profile slow endpoints to identify bottlenecks
3. Implement caching for frequently accessed data
4. Consider async operations for I/O-bound tasks
5. Add performance monitoring to production
"""
    
    return report

if __name__ == "__main__":
    print("Starting performance baseline measurement...")
    print("Make sure the server is running on localhost:8000\n")
    
    try:
        results = measure_endpoint_performance()
        
        if results:
            # Save raw results
            with open("performance_baseline.json", "w") as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "results": results
                }, f, indent=2)
            
            # Generate report
            report = generate_baseline_report(results)
            
            # Save report
            report_path = Path("features/system_optimization/claude/PERFORMANCE_BASELINE_REPORT.md")
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, "w") as f:
                f.write(report)
            
            print("\n" + "="*60)
            print("BASELINE COMPLETE")
            print("="*60)
            print(f"Results saved to: performance_baseline.json")
            print(f"Report saved to: {report_path}")
            
            # Print summary
            print("\nQuick Summary:")
            for r in results:
                status = "✅" if r['avg_ms'] < 200 else "⚠️" if r['avg_ms'] < 500 else "❌"
                print(f"  {status} {r['name']}: {r['avg_ms']}ms")
                
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure the server is running with: python app.py")