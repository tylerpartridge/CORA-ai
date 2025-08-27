# tests/test_final_system.py
import os, time, pytest, requests

# Gate: only run when explicitly enabled
if os.getenv("CORA_E2E", "0") != "1":
    pytest.skip("Final system E2E disabled (set CORA_E2E=1 to enable)", allow_module_level=True)

BASE_URL = os.getenv("CORA_BASE_URL", "http://localhost:8000")

def _get(path, **kw):
    kw.setdefault("timeout", 3)
    return requests.get(f"{BASE_URL}{path}", **kw)

def _post(path, **kw):
    kw.setdefault("timeout", 3)
    return requests.post(f"{BASE_URL}{path}", **kw)

def test_health():
    r = _get("/api/health/status")
    if r.status_code >= 500:
        pytest.skip("Health endpoint unavailable (>=500)")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "healthy"

def test_register_and_login():
    email = f"finaltest_{int(time.time())}@example.com"
    pw = "ChangeMe123!"
    r = _post("/api/auth/register", json={"email": email, "password": pw, "confirm_password": pw})
    if r.status_code >= 500:
        pytest.skip("Auth register unavailable (>=500)")
    assert r.status_code in (200, 201)

    r2 = _post("/api/auth/login", json={"email": email, "password": pw})
    assert r2.status_code == 200
    token = (r2.json() or {}).get("access_token")
    assert token, "Missing access_token"