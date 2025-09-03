# Canonical Smoke Harness

## Scripts
- tools/smoke.sh — bash smokes with retries/timeouts
- tools/smoke.py — JSON mode for programmatic checks

## Checks (default)
- /health → 200
- /api/status → 200
- /api/admin (protected) → 401 when unauthenticated

## Usage
```bash
# Bash
./tools/smoke.sh --base-url http://127.0.0.1:8000 --retries 3 --timeout 5

# JSON
python3 tools/smoke.py --base-url http://127.0.0.1:8000 --retries 3 --timeout 5 --json
```

## Notes
- Extend with additional endpoints as needed; keep protected route check expecting 401 without auth.
- Intended to run locally on the server (no TLS assumptions) right after restarts/deploys.
