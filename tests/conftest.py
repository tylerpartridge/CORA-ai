import os, pathlib, pytest, importlib, sys

# ---------- baseline safe test env ----------
os.environ.setdefault("ENV", "testing")
os.environ.setdefault("TZ", "UTC")
cache = pathlib.Path(".pytest_cache"); cache.mkdir(exist_ok=True)
os.environ.setdefault("DATABASE_URL", f"sqlite:///{cache / 'test.db'}")
os.environ.setdefault("OPENAI_API_KEY", "")
os.environ.setdefault("SENTRY_DSN", "")
os.environ.setdefault("SECRET_KEY", "dev-test-key")

@pytest.fixture(scope="session", autouse=True)
def _session_setup():
    yield

# ---------- opt-in API fixtures (guarded by env) ----------
ENABLE_API_FIXTURES = any(os.getenv(k, "0") == "1" for k in (
    "CORA_DB_TESTS","CORA_DASH_TESTS","CORA_E2E","CORA_SALES_TESTS"
))

def _load_app():
    """Best-effort loader for FastAPI app, overridable via CORA_APP_MODULE=package.module:app"""
    # ensure repo root is on sys.path
    root = pathlib.Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    specs = []
    modspec = os.getenv("CORA_APP_MODULE")
    if modspec:
        specs.append(modspec)
    specs += [
        "main:app",
        "app.main:app",
        "backend.main:app",
        "src.main:app",
        "cora.main:app",
    ]
    for spec in specs:
        try:
            mod, attr = spec.split(":")
            module = importlib.import_module(mod)
            return getattr(module, attr)
        except Exception:
            continue
    return None

if not ENABLE_API_FIXTURES:
    @pytest.fixture
    def client():
        pytest.skip("API fixtures disabled (set CORA_DB_TESTS=1 or CORA_DASH_TESTS=1 or CORA_E2E=1 or CORA_SALES_TESTS=1)")
    @pytest.fixture
    def token():
        pytest.skip("API fixtures disabled")
else:
    from fastapi.testclient import TestClient

    @pytest.fixture(scope="session")
    def client():
        app = _load_app()
        if app is None:
            pytest.skip("Could not import FastAPI app. Set CORA_APP_MODULE='package.module:app' or place main.py at repo root.")
        # best-effort DB init if Base/engine are exposed
        for name in ("db","database","cora.db"):
            try:
                m = importlib.import_module(name)
                Base = getattr(m, "Base", None)
                engine = getattr(m, "engine", None)
                if Base is not None and engine is not None:
                    Base.metadata.create_all(bind=engine)
                    break
            except Exception:
                pass
        return TestClient(app)

    @pytest.fixture(scope="session")
    def token(client):
        email = os.getenv("TEST_ADMIN_EMAIL", "admin@coraai.tech")
        password = os.getenv("TEST_ADMIN_PASSWORD", "ChangeMe123!")
        client.post("/api/auth/register", json={"email": email, "password": password, "confirm_password": password})
        r = client.post("/api/auth/login", json={"email": email, "password": password})
        if r.status_code != 200:
            pytest.skip(f"Login failed: {r.status_code} {r.text}")
        return r.json().get("access_token")
