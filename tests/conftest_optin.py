import os, pytest

ENABLE_API_FIXTURES = any(os.getenv(k,'0') == '1' for k in (
    'CORA_DB_TESTS','CORA_DASH_TESTS','CORA_E2E','CORA_SALES_TESTS'
))

if not ENABLE_API_FIXTURES:
    @pytest.fixture
    def client():
        pytest.skip("API fixtures disabled (set CORA_DB_TESTS=1 or CORA_DASH_TESTS=1 to enable)")
    @pytest.fixture
    def token():
        pytest.skip("API fixtures disabled")
else:
    from fastapi.testclient import TestClient
    from main import app

    # Try to ensure tables exist if your project exposes Base/engine; ignore if not
    try:
        from db import Base, engine  # adjust to your project if different
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass

    @pytest.fixture(scope="session")
    def client():
        return TestClient(app)

    @pytest.fixture(scope="session")
    def token(client):
        email = os.getenv("TEST_ADMIN_EMAIL", "admin@coraai.tech")
        password = os.getenv("TEST_ADMIN_PASSWORD", "ChangeMe123!")
        # best-effort create then login
        client.post("/api/auth/register", json={"email": email, "password": password, "confirm_password": password})
        r = client.post("/api/auth/login", json={"email": email, "password": password})
        r.raise_for_status()
        return r.json().get("access_token")
