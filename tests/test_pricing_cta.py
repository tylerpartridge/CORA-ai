import os
from contextlib import contextmanager

# Prefer Starlette's TestClient (works with FastAPI)
from starlette.testclient import TestClient

# Try common app entrypoints
try:
    from app import app  # e.g., app.py exporting "app"
except Exception:
    try:
        from main import app  # e.g., main.py exporting "app"
    except Exception as e:
        raise RuntimeError("Could not import FastAPI 'app' from app.py or main.py") from e

@contextmanager
def set_env(**kwargs):
    old = {k: os.environ.get(k) for k in kwargs}
    try:
        for k, v in kwargs.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

def test_pricing_cta_uses_payment_link_when_set():
    test_link = "https://buy.stripe.com/test_12345"
    with set_env(PAYMENT_LINK=test_link):
        client = TestClient(app)
        r = client.get("/pricing")
        assert r.status_code == 200
        html = r.text
        assert f'href="{test_link}"' in html

def test_pricing_cta_falls_back_to_signup_when_unset():
    with set_env(PAYMENT_LINK=None):
        client = TestClient(app)
        r = client.get("/pricing")
        assert r.status_code == 200
        html = r.text
        # Fallback should be /signup (not landing anchors)
        assert 'href="/signup"' in html
