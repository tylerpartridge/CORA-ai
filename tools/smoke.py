#!/usr/bin/env python3
import argparse, json, sys, time
import urllib.request

def get(url, timeout):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.getcode()
    except Exception:
        return 0

def try_path(base, path, expected, retries, timeout):
    for i in range(1, retries+1):
        code = get(base + path, timeout)
        print(f"[{path}] Attempt {i}/{retries}: => {code} (expect {expected})")
        if code == expected:
            return True, code
        time.sleep(1)
    return False, code

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base-url', default='http://127.0.0.1:8000')
    ap.add_argument('--retries', type=int, default=3)
    ap.add_argument('--timeout', type=int, default=5)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    checks = [
        ('/health', 200, 'health'),
        ('/api/status', 200, 'status'),
        ('/api/admin', 401, 'protected'),
    ]

    results = []
    overall = True
    for path, expected, name in checks:
        ok, code = try_path(args.base_url, path, expected, args.retries, args.timeout)
        overall = overall and ok
        results.append({'name': name, 'path': path, 'expected': expected, 'code': code, 'ok': ok})

    if args.json:
        print(json.dumps({'ok': overall, 'results': results}, indent=2))
    else:
        print('SMOKES:', 'PASS' if overall else 'FAIL')

    sys.exit(0 if overall else 1)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/smoke.py
🎯 PURPOSE: JSON-output smoke test runner for CORA
🔗 IMPORTS: requests, standard library
📤 EXPORTS: main() function with JSON/text output
"""

import sys
import json
import time
import argparse
from typing import List, Dict, Tuple
import urllib.request
import urllib.error
from urllib.parse import urljoin


class SmokeTest:
    """Smoke test runner with retry logic"""
    
    def __init__(self, base_url: str, retries: int = 3, timeout: int = 5):
        self.base_url = base_url.rstrip('/')
        self.retries = retries
        self.timeout = timeout
        self.results = []
        self.start_time = None
        
    def run_check(self, method: str, endpoint: str, expected_codes: List[int], 
                  description: str) -> Dict:
        """Run a single check with retries"""
        result = {
            'description': description,
            'endpoint': endpoint,
            'method': method,
            'expected_codes': expected_codes,
            'attempts': [],
            'passed': False,
            'response_code': None
        }
        
        url = urljoin(self.base_url, endpoint)
        
        for attempt in range(1, self.retries + 1):
            delay = 0.5 * attempt
            
            try:
                # Create request
                req = urllib.request.Request(url, method=method)
                
                # Execute request
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    response_code = response.getcode()
                    
            except urllib.error.HTTPError as e:
                response_code = e.code
            except urllib.error.URLError as e:
                response_code = 0  # Connection error
            except Exception as e:
                response_code = 0
            
            result['attempts'].append({
                'attempt': attempt,
                'response_code': response_code,
                'timestamp': time.time()
            })
            
            # Check if response matches expected
            if response_code in expected_codes:
                result['passed'] = True
                result['response_code'] = response_code
                break
            
            # Wait before retry (except on last attempt)
            if attempt < self.retries:
                time.sleep(delay)
        
        # Set final response code
        if result['response_code'] is None and result['attempts']:
            result['response_code'] = result['attempts'][-1]['response_code']
        
        self.results.append(result)
        return result
    
    def run_all_checks(self) -> Dict:
        """Run all smoke test checks"""
        self.start_time = time.time()
        
        # Define checks
        checks = [
            ('GET', '/api/status', [200], 'API Status'),
            ('HEAD', '/', [200, 401], 'Root Endpoint'),
            ('GET', '/api/expenses', [401], 'Protected API (unauthenticated)'),
            ('GET', '/login', [200], 'Public Page (login)'),
            ('GET', '/health', [200], 'Health Check'),
        ]
        
        # Run each check
        for method, endpoint, expected, description in checks:
            self.run_check(method, endpoint, expected, description)
        
        # Calculate summary
        duration_ms = int((time.time() - self.start_time) * 1000)
        passed_count = sum(1 for r in self.results if r['passed'])
        
        return {
            'base_url': self.base_url,
            'timestamp': self.start_time,
            'duration_ms': duration_ms,
            'checks': self.results,
            'summary': {
                'total': len(self.results),
                'passed': passed_count,
                'failed': len(self.results) - passed_count
            },
            'passed': all(r['passed'] for r in self.results)
        }


def format_text_output(results: Dict) -> str:
    """Format results as human-readable text"""
    lines = []
    lines.append("=== CORA Smoke Tests ===")
    lines.append(f"Base URL: {results['base_url']}")
    lines.append(f"Duration: {results['duration_ms']}ms")
    lines.append("")
    
    for check in results['checks']:
        status = "✓" if check['passed'] else "✗"
        code = check['response_code']
        expected = ','.join(str(c) for c in check['expected_codes'])
        attempts = len(check['attempts'])
        
        lines.append(f"{status} {check['description']}: {code} "
                    f"(expected: {expected}, attempts: {attempts})")
    
    lines.append("")
    lines.append("=== Summary ===")
    summary = results['summary']
    lines.append(f"Passed: {summary['passed']}/{summary['total']}")
    lines.append(f"OVERALL: {'PASS' if results['passed'] else 'FAIL'}")
    
    return '\n'.join(lines)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='CORA smoke test runner')
    parser.add_argument('--base-url', 
                       default='http://127.0.0.1:8000',
                       help='Base URL to test')
    parser.add_argument('--retries', 
                       type=int, 
                       default=3,
                       help='Number of retries per check')
    parser.add_argument('--timeout', 
                       type=int, 
                       default=5,
                       help='Request timeout in seconds')
    parser.add_argument('--json', 
                       action='store_true',
                       default=True,
                       help='Output JSON (default)')
    parser.add_argument('--text', 
                       action='store_true',
                       help='Output human-readable text')
    
    args = parser.parse_args()
    
    # Run smoke tests
    tester = SmokeTest(args.base_url, args.retries, args.timeout)
    results = tester.run_all_checks()
    
    # Output results
    if args.text:
        print(format_text_output(results))
    else:
        print(json.dumps(results, indent=2))
    
    # Exit code based on overall pass/fail
    sys.exit(0 if results['passed'] else 1)


if __name__ == "__main__":
    main()