#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/smoke.py
🎯 PURPOSE: Canonical JSON-output smoke test runner for CORA
🔗 IMPORTS: urllib.request, urllib.error, argparse, json, sys, time
📤 EXPORTS: CLI that prints JSON (or PASS/FAIL) and returns exit code
"""

import argparse
import json
import sys
import time
from typing import Tuple, List, Dict
import urllib.request
import urllib.error


def fetch_status_code(url: str, timeout: int) -> int:
    """Return HTTP status code for url; 0 for network errors.
    Handles HTTPError to surface codes like 401/403 instead of masking them.
    """
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.getcode()
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception:
        return 0


def try_path(base_url: str, path: str, expected: int, retries: int, timeout: int) -> Tuple[bool, int]:
    last_code = 0
    full_url = f"{base_url.rstrip('/')}{path}"
    for attempt in range(1, retries + 1):
        code = fetch_status_code(full_url, timeout)
        last_code = code
        print(f"[{path}] Attempt {attempt}/{retries}: => {code} (expect {expected})")
        if code == expected:
            return True, code
        time.sleep(1)
    return False, last_code


def main() -> None:
    parser = argparse.ArgumentParser(description="CORA smoke test runner")
    parser.add_argument('--base-url', default='http://127.0.0.1:8000')
    parser.add_argument('--retries', type=int, default=3)
    parser.add_argument('--timeout', type=int, default=5)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    # Canonical checks
    checks: List[Tuple[str, int, str]] = [
        ('/health', 200, 'health'),
        ('/api/status', 200, 'status'),
        # Protected route should be unauthorized when unauthenticated
        ('/api/feature-flags', 401, 'protected'),
    ]

    results: List[Dict] = []
    overall_ok = True
    for path, expected, name in checks:
        ok, code = try_path(args.base_url, path, expected, args.retries, args.timeout)
        overall_ok = overall_ok and ok
        results.append({
            'name': name,
            'path': path,
            'expected': expected,
            'code': code,
            'ok': ok,
        })

    if args.json:
        print(json.dumps({'ok': overall_ok, 'results': results}, indent=2))
    else:
        print('SMOKES:', 'PASS' if overall_ok else 'FAIL')

    sys.exit(0 if overall_ok else 1)


if __name__ == '__main__':
    main()