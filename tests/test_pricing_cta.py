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
from bs4 import BeautifulSoup


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
    Extract CTA hrefs from pricing page HTML using data-testid attributes.
    Returns dict with plan names as keys and hrefs as values.
    """
    soup = BeautifulSoup(html, 'html.parser')
    hrefs = {}
    
    # Find CTAs by data-testid
    solo_cta = soup.find('a', attrs={'data-testid': 'cta-solo'})
    if solo_cta:
        hrefs['SOLO'] = solo_cta.get('href')
    
    crew_cta = soup.find('a', attrs={'data-testid': 'cta-crew'})
    if crew_cta:
        hrefs['CREW'] = crew_cta.get('href')
    
    business_cta = soup.find('a', attrs={'data-testid': 'cta-business'})
    if business_cta:
        hrefs['BUSINESS'] = business_cta.get('href')
    
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
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check SOLO CTA has target="_blank" for external link
        solo_cta = soup.find('a', attrs={'data-testid': 'cta-solo'})
        assert solo_cta.get('href') == 'https://buy.stripe.com/test'
        assert solo_cta.get('target') == '_blank'
        assert 'noopener' in str(solo_cta.get('rel'))
        
        # Check CREW CTA doesn't have target="_blank" for internal link
        crew_cta = soup.find('a', attrs={'data-testid': 'cta-crew'})
        assert crew_cta.get('href') == '/signup?plan=CREW'
        assert crew_cta.get('target') is None, "Internal links should not open in new tab"
        
        # Check BUSINESS CTA doesn't have target="_blank" for internal link
        business_cta = soup.find('a', attrs={'data-testid': 'cta-business'})
        assert business_cta.get('href') == '/signup?plan=BUSINESS'
        assert business_cta.get('target') is None, "Internal links should not open in new tab"


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])