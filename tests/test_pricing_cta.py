"""
Test pricing page CTA functionality with Stripe Payment Links integration.

Tests ensure that:
1. With payment links configured -> CTAs link to Stripe
2. Without payment links -> CTAs fallback to /signup?plan=X
3. Generic PAYMENT_LINK applies to all plans when specific ones aren't set
"""
import os
from contextlib import contextmanager
from fastapi.testclient import TestClient
import pytest


@contextmanager
def env(**kwargs):
    """Context manager to temporarily set environment variables for testing."""
    old = {k: os.environ.get(k) for k in kwargs}
    try:
        for k, v in kwargs.items():
            if v is None and k in os.environ:
                os.environ.pop(k)
            elif v is not None:
                os.environ[k] = v
        yield
    finally:
        for k, v in old.items():
            if v is None and k in os.environ:
                os.environ.pop(k)
            elif v is not None:
                os.environ[k] = v


def get_cta_hrefs(html: str) -> dict:
    """
    Extract CTA hrefs from pricing page HTML.
    Returns dict with plan names as keys and hrefs as values.
    
    Using simple string parsing instead of BeautifulSoup to avoid dependency.
    """
    # Find all pricing card CTAs by looking for the pattern
    import re
    
    hrefs = {}
    
    # Find SOLO CTA
    solo_match = re.search(r'<a[^>]*href="([^"]+)"[^>]*>.*?Start Free Trial.*?</a>.*?SOLO', html, re.DOTALL)
    if not solo_match:
        # Try reverse order
        solo_match = re.search(r'SOLO.*?<a[^>]*href="([^"]+)"[^>]*>.*?Start Free Trial.*?</a>', html, re.DOTALL)
    if solo_match:
        hrefs['SOLO'] = solo_match.group(1)
    
    # Find CREW CTA (different text)
    crew_match = re.search(r'CREW.*?<a[^>]*href="([^"]+)"[^>]*>.*?Start Tracking Jobs Now.*?</a>', html, re.DOTALL)
    if crew_match:
        hrefs['CREW'] = crew_match.group(1)
    
    # Find BUSINESS CTA
    business_match = re.search(r'BUSINESS.*?<a[^>]*href="([^"]+)"[^>]*>.*?Start Free Trial.*?</a>', html, re.DOTALL)
    if business_match:
        hrefs['BUSINESS'] = business_match.group(1)
    
    return hrefs


@pytest.fixture
def test_client():
    """Create test client for pricing tests."""
    from app import app
    return TestClient(app)


def test_no_payment_links_fallback_to_signup(test_client):
    """Test that CTAs fallback to /signup?plan=X when no payment links are configured."""
    with env(
        PAYMENT_LINK_SOLO=None,
        PAYMENT_LINK_CREW=None,
        PAYMENT_LINK_BUSINESS=None,
        PAYMENT_LINK=None
    ):
        response = test_client.get("/pricing")
        assert response.status_code == 200
        
        hrefs = get_cta_hrefs(response.text)
        
        assert hrefs.get('SOLO') == '/signup?plan=SOLO', f"SOLO CTA should fallback to /signup?plan=SOLO, got {hrefs.get('SOLO')}"
        assert hrefs.get('CREW') == '/signup?plan=CREW', f"CREW CTA should fallback to /signup?plan=CREW, got {hrefs.get('CREW')}"
        assert hrefs.get('BUSINESS') == '/signup?plan=BUSINESS', f"BUSINESS CTA should fallback to /signup?plan=BUSINESS, got {hrefs.get('BUSINESS')}"


def test_specific_payment_links(test_client):
    """Test that plan-specific payment links are used when configured."""
    with env(
        PAYMENT_LINK_SOLO="https://buy.stripe.com/5kQfZh1yqarab9P8SXgw002",
        PAYMENT_LINK_CREW="https://buy.stripe.com/bJefZhdh8arafq57OTgw001",
        PAYMENT_LINK_BUSINESS="https://buy.stripe.com/8x2fZh1yq7eYcdT6KPgw000",
        PAYMENT_LINK=None
    ):
        response = test_client.get("/pricing")
        assert response.status_code == 200
        
        hrefs = get_cta_hrefs(response.text)
        
        assert hrefs.get('SOLO') == "https://buy.stripe.com/5kQfZh1yqarab9P8SXgw002"
        assert hrefs.get('CREW') == "https://buy.stripe.com/bJefZhdh8arafq57OTgw001"
        assert hrefs.get('BUSINESS') == "https://buy.stripe.com/8x2fZh1yq7eYcdT6KPgw000"


def test_generic_payment_link_applies_to_all(test_client):
    """Test that generic PAYMENT_LINK applies to all plans when specific ones aren't set."""
    generic_link = "https://buy.stripe.com/generic_link"
    
    with env(
        PAYMENT_LINK=generic_link,
        PAYMENT_LINK_SOLO=None,
        PAYMENT_LINK_CREW=None,
        PAYMENT_LINK_BUSINESS=None
    ):
        response = test_client.get("/pricing")
        assert response.status_code == 200
        
        hrefs = get_cta_hrefs(response.text)
        
        assert hrefs.get('SOLO') == generic_link, f"SOLO should use generic link"
        assert hrefs.get('CREW') == generic_link, f"CREW should use generic link"
        assert hrefs.get('BUSINESS') == generic_link, f"BUSINESS should use generic link"


def test_mixed_configuration(test_client):
    """Test mixed configuration with some specific links and fallback for others."""
    crew_link = "https://buy.stripe.com/crew_specific"
    
    with env(
        PAYMENT_LINK_SOLO=None,
        PAYMENT_LINK_CREW=crew_link,
        PAYMENT_LINK_BUSINESS=None,
        PAYMENT_LINK=None
    ):
        response = test_client.get("/pricing")
        assert response.status_code == 200
        
        hrefs = get_cta_hrefs(response.text)
        
        assert hrefs.get('SOLO') == '/signup?plan=SOLO', f"SOLO should fallback"
        assert hrefs.get('CREW') == crew_link, f"CREW should use specific link"
        assert hrefs.get('BUSINESS') == '/signup?plan=BUSINESS', f"BUSINESS should fallback"


def test_specific_overrides_generic(test_client):
    """Test that plan-specific links override generic PAYMENT_LINK."""
    generic_link = "https://buy.stripe.com/generic"
    solo_specific = "https://buy.stripe.com/solo_specific"
    
    with env(
        PAYMENT_LINK=generic_link,
        PAYMENT_LINK_SOLO=solo_specific,
        PAYMENT_LINK_CREW=None,
        PAYMENT_LINK_BUSINESS=None
    ):
        response = test_client.get("/pricing")
        assert response.status_code == 200
        
        hrefs = get_cta_hrefs(response.text)
        
        assert hrefs.get('SOLO') == solo_specific, f"SOLO should use specific link"
        assert hrefs.get('CREW') == generic_link, f"CREW should use generic link"
        assert hrefs.get('BUSINESS') == generic_link, f"BUSINESS should use generic link"


def test_target_blank_for_payment_links(test_client):
    """Test that payment links open in new tab with proper attributes."""
    with env(
        PAYMENT_LINK_SOLO="https://buy.stripe.com/test",
        PAYMENT_LINK_CREW=None,
        PAYMENT_LINK_BUSINESS=None,
        PAYMENT_LINK=None
    ):
        response = test_client.get("/pricing")
        assert response.status_code == 200
        
        # Check for target="_blank" and rel="noopener" on payment links
        assert 'href="https://buy.stripe.com/test"' in response.text
        assert 'target="_blank"' in response.text
        assert 'rel="noopener"' in response.text
        
        # Check that signup links don't have target="_blank"
        assert 'href="/signup?plan=CREW"' in response.text
        # The /signup links should not have target="_blank" immediately after them
        import re
        signup_pattern = re.compile(r'href="/signup\?plan=\w+"[^>]*target="_blank"')
        assert not signup_pattern.search(response.text), "Signup links should not open in new tab"


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])