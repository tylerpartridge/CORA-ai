
import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient


def test_public_pages_status_codes():
    # Import app lazily to avoid side effects at import time
    from app import app  # noqa: WPS433

    client = TestClient(app)

    pages = [
        "/",
        "/features",
        "/pricing",
        "/reviews",
        "/how-it-works",
        "/contact",
        "/terms",
        "/privacy",
        "/blog",
        "/help",
    ]

    for path in pages:
        response = client.get(path)
        assert response.status_code == 200, f"{path} returned {response.status_code}"

