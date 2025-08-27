import os, pathlib, pytest
# Force safe test env BEFORE anything else imports
os.environ["ENV"] = "testing"
os.environ["TZ"] = "UTC"
cache = pathlib.Path(".pytest_cache"); cache.mkdir(exist_ok=True)
os.environ["DATABASE_URL"] = f"sqlite:///{cache / "test.db"}"
os.environ.setdefault("OPENAI_API_KEY","")
os.environ.setdefault("SENTRY_DSN","")
os.environ.setdefault("SECRET_KEY","dev-test-key")

# Do NOT import the app here; many startup side-effects on import.
# If a test needs the app, import inside that test explicitly.

@pytest.fixture(scope="session", autouse=True)
def _session_setup():
    yield
