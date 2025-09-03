#!/usr/bin/env bash
set -euo pipefail

BASE_URL="http://127.0.0.1:8000"
RETRIES=3
TIMEOUT=5

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base-url) BASE_URL="$2"; shift 2;;
    --retries) RETRIES="$2"; shift 2;;
    --timeout) TIMEOUT="$2"; shift 2;;
    *) echo "Unknown arg: $1"; exit 2;;
  esac
done

try_curl() {
  local path="$1" expected="$2" name="$3"
  local i code
  for ((i=1;i<=RETRIES;i++)); do
    code=$(curl -s -o /dev/null -m "$TIMEOUT" -w "%{http_code}" "${BASE_URL}${path}" || echo 000)
    echo "[${name}] Attempt ${i}/${RETRIES}: ${path} => ${code} (expect ${expected})"
    if [[ "${code}" == "${expected}" ]]; then
      echo "[${name}] PASS"
      return 0
    fi
    sleep 1
  done
  echo "[${name}] FAIL (last=${code}, expect=${expected})"
  return 1
}

overall=0
try_curl "/health" 200 "health" || overall=1
try_curl "/api/status" 200 "status" || overall=1
# Protected route should be unauthorized when no auth (expect 401)
try_curl "/api/admin" 401 "protected" || overall=1 || true

if [[ $overall -eq 0 ]]; then
  echo "SMOKES: PASS"
else
  echo "SMOKES: FAIL"
fi
exit $overall

#!/bin/bash
# 🧭 LOCATION: /CORA/tools/smoke.sh
# 🎯 PURPOSE: Canonical smoke test runner for CORA production health checks
# 🔗 IMPORTS: curl, standard POSIX utilities
# 📤 EXPORTS: Exit 0 on all pass, 1 on any fail

set -euo pipefail

# Defaults
BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
RETRIES="${RETRIES:-3}"
TIMEOUT="${TIMEOUT:-5}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --base-url)
      BASE_URL="$2"
      shift 2
      ;;
    --retries)
      RETRIES="$2"
      shift 2
      ;;
    --timeout)
      TIMEOUT="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [--base-url URL] [--retries N] [--timeout SECONDS]"
      echo "  --base-url URL    Base URL to test (default: http://127.0.0.1:8000)"
      echo "  --retries N       Number of retries per check (default: 3)"
      echo "  --timeout SECONDS Request timeout in seconds (default: 5)"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Colors for output (disabled if not a terminal)
if [ -t 1 ]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[1;33m'
  NC='\033[0m' # No Color
else
  RED=''
  GREEN=''
  YELLOW=''
  NC=''
fi

# Track overall status
FAILED=0
PASSED=0

# Function to run a single check with retries
run_check() {
  local method="$1"
  local endpoint="$2"
  local expected_codes="$3"
  local description="$4"
  local attempt=1
  
  while [ $attempt -le "$RETRIES" ]; do
    # Calculate backoff delay
    local delay=$(echo "0.5 * $attempt" | bc 2>/dev/null || echo "$attempt")
    
    # Make the request
    local response_code
    if [ "$method" = "HEAD" ]; then
      response_code=$(curl -s -o /dev/null -w "%{http_code}" \
        --max-time "$TIMEOUT" \
        --head \
        "${BASE_URL}${endpoint}" 2>/dev/null || echo "000")
    else
      response_code=$(curl -s -o /dev/null -w "%{http_code}" \
        --max-time "$TIMEOUT" \
        -X "$method" \
        "${BASE_URL}${endpoint}" 2>/dev/null || echo "000")
    fi
    
    # Check if response code matches expected
    if echo "$expected_codes" | grep -q "$response_code"; then
      echo -e "${GREEN}✓${NC} $description: $response_code (attempt $attempt/$RETRIES)"
      ((PASSED++))
      return 0
    fi
    
    # If this isn't the last attempt, wait and retry
    if [ $attempt -lt "$RETRIES" ]; then
      echo -e "${YELLOW}⟳${NC} $description: $response_code (retrying in ${delay}s...)"
      sleep "$delay"
    else
      echo -e "${RED}✗${NC} $description: $response_code (expected: $expected_codes)"
      ((FAILED++))
      return 1
    fi
    
    ((attempt++))
  done
}

# Start smoke tests
echo "=== CORA Smoke Tests ==="
echo "Base URL: $BASE_URL"
echo "Retries: $RETRIES"
echo "Timeout: ${TIMEOUT}s"
echo ""

# Test 1: API Status endpoint
run_check "GET" "/api/status" "200" "API Status" || true

# Test 2: Root endpoint (may be protected)
run_check "HEAD" "/" "200|401" "Root Endpoint" || true

# Test 3: Protected endpoint (expenses API requires auth)
run_check "GET" "/api/expenses" "401" "Protected API (unauthenticated)" || true

# Test 4: Public page (login or pricing)
# Try login first, fall back to pricing if login returns 401
if ! run_check "GET" "/login" "200" "Public Page (login)"; then
  # If login failed, try pricing as fallback
  run_check "GET" "/pricing" "200" "Public Page (pricing)" || true
fi

# Test 5: Health endpoint (if exists)
run_check "GET" "/health" "200" "Health Check" || true

# Summary
echo ""
echo "=== Summary ==="
echo -e "Passed: ${GREEN}${PASSED}${NC}"
echo -e "Failed: ${RED}${FAILED}${NC}"

if [ "$FAILED" -eq 0 ]; then
  echo -e "${GREEN}OVERALL: PASS${NC}"
  exit 0
else
  echo -e "${RED}OVERALL: FAIL${NC}"
  exit 1
fi