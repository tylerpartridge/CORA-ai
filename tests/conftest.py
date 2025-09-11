import os
import pytest
from typing import Optional

_IT: Optional[str] = os.getenv("IT_ACCESS_TOKEN") or None

def _apply_auth(client) -> None:
    """
    Make authed requests succeed in IT by adding both header and cookie.
    Header: Authorization: Bearer <token>
    Cookie: access_token=Bearer <token> (covers cookie-based paths)
    """
    if not _IT:
        return
    # Header
    client.headers.update({"Authorization": f"Bearer {_IT}"})
    # Cookie (domain 'testserver' is what TestClient uses)
    try:
        client.cookies.set("access_token", f"Bearer {_IT}", domain="testserver")
    except Exception:
        pass

@pytest.fixture(autouse=True)
def _ensure_auth_header(request):
    """
    Autouse so it runs before every test:
    - If the module created a module-level `client`, patch it.
    - If tests use their own client fixtures, they can call _apply_auth explicitly,
      but this still helps for common patterns.
    """
    g = request.node.module.__dict__
    client = g.get("client")
    try:
        # FastAPI's TestClient class loads lazily in user modules;
        # we avoid direct imports here to keep this fixture robust.
        if client is not None and hasattr(client, "headers") and hasattr(client, "cookies"):
            _apply_auth(client)
    except Exception:
        pass
    yield

