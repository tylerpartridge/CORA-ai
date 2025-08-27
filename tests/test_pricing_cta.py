"""
Test pricing page CTA functionality with payment link integration
"""
import os
import pytest
from fastapi.testclient import TestClient

# Skip test if not explicitly enabled
if not os.getenv("RUN_PRICING_TESTS", "0") == "1":
    pytest.skip("Pricing tests disabled (set RUN_PRICING_TESTS=1)", allow_module_level=True)

@pytest.fixture
def client():
    """Create test client"""
    from app import app
    return TestClient(app)

def test_pricing_page_with_payment_link(client, monkeypatch):
    """Test that pricing page includes payment link when configured"""
    # Set payment link environment variable
    test_payment_link = "https://buy.stripe.com/test_ABC"
    monkeypatch.setenv("PAYMENT_LINK_SOLO", test_payment_link)
    
    # Request pricing page
    response = client.get("/pricing")
    
    # Check response is successful
    assert response.status_code == 200
    
    # Check payment link is in response
    assert test_payment_link in response.text
    assert 'href="https://buy.stripe.com/test_ABC"' in response.text

def test_pricing_page_without_payment_link(client, monkeypatch):
    """Test that pricing page falls back to checkout when no payment link"""
    # Ensure payment link is not set
    monkeypatch.delenv("PAYMENT_LINK_SOLO", raising=False)
    monkeypatch.delenv("PAYMENT_LINK_CREW", raising=False)
    monkeypatch.delenv("PAYMENT_LINK_BUSINESS", raising=False)
    
    # Request pricing page
    response = client.get("/pricing")
    
    # Check response is successful
    assert response.status_code == 200
    
    # Check for checkout function presence
    assert "initiateCheckout" in response.text
    assert "/api/payments/checkout" in response.text
    assert 'data-plan="SOLO"' in response.text or 'onclick="initiateCheckout' in response.text

def test_pricing_page_multiple_payment_links(client, monkeypatch):
    """Test that each plan can have its own payment link"""
    # Set different payment links
    monkeypatch.setenv("PAYMENT_LINK_SOLO", "https://buy.stripe.com/test_SOLO")
    monkeypatch.setenv("PAYMENT_LINK_CREW", "https://buy.stripe.com/test_CREW")
    monkeypatch.setenv("PAYMENT_LINK_BUSINESS", "https://buy.stripe.com/test_BUSINESS")
    
    # Request pricing page
    response = client.get("/pricing")
    
    # Check all links are present
    assert response.status_code == 200
    assert "https://buy.stripe.com/test_SOLO" in response.text
    assert "https://buy.stripe.com/test_CREW" in response.text
    assert "https://buy.stripe.com/test_BUSINESS" in response.text

def test_pricing_page_mixed_configuration(client, monkeypatch):
    """Test mixed configuration with some payment links and some checkout fallback"""
    # Only set CREW payment link
    monkeypatch.delenv("PAYMENT_LINK_SOLO", raising=False)
    monkeypatch.setenv("PAYMENT_LINK_CREW", "https://buy.stripe.com/test_CREW_ONLY")
    monkeypatch.delenv("PAYMENT_LINK_BUSINESS", raising=False)
    
    # Request pricing page
    response = client.get("/pricing")
    
    assert response.status_code == 200
    
    # CREW should have payment link
    assert "https://buy.stripe.com/test_CREW_ONLY" in response.text
    
    # SOLO and BUSINESS should have checkout fallback
    assert 'data-plan="SOLO"' in response.text or 'onclick="initiateCheckout(\'SOLO\')' in response.text
    assert 'data-plan="BUSINESS"' in response.text or 'onclick="initiateCheckout(\'BUSINESS\')' in response.text

if __name__ == "__main__":
    # Run tests locally
    pytest.main([__file__, "-v"])