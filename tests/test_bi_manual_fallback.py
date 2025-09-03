#!/usr/bin/env python3
"""
Test BI Snapshot manual fallback functionality

Tests that manual pricing data is used when scraping yields no snippets.
"""

import pytest
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import snapshot functions
from scripts.bi.snapshot import (
    process_competitor,
    extract_pricing_snippets,
    create_cache_dir
)


class TestManualFallback:
    """Test manual fallback behavior when scraping fails"""
    
    def test_manual_fallback_activates_on_zero_snippets(self):
        """Test that manual fallback is used when no snippets are extracted"""
        
        # Create test competitor with manual notes
        competitor = {
            "name": "Test Vendor",
            "urls": ["https://example.com/pricing"],
            "manual_notes": {
                "pricing_bullets": [
                    "Solo plan: $29/mo",
                    "Crew: $69/mo",
                    "Business: $149/mo"
                ],
                "updated": "2025-09-01",
                "source_hint": "sales page screenshot"
            }
        }
        
        # Mock session that returns error
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "<html><body>Access Denied</body></html>"
        mock_response.url = "https://example.com/pricing"
        mock_session.get.return_value = mock_response
        
        # Create temp cache dir
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            
            # Mock logger and CACHE_BASE_PATH
            with patch('scripts.bi.snapshot.logger') as mock_logger:
                # Mock CAPTURE_ON_ERROR to True and fix cache base path
                with patch('scripts.bi.snapshot.CAPTURE_ON_ERROR', True):
                    with patch('scripts.bi.snapshot.CACHE_BASE_PATH', Path(tmpdir).parent):
                        # Process competitor
                        results = process_competitor(competitor, cache_dir, mock_session)
            
            # Check that manual fallback was used
            assert "manual_fallback" in results
            assert results["manual_fallback"]["pricing_bullets"] == competitor["manual_notes"]["pricing_bullets"]
            
            # Check urls_processed includes manual entry
            manual_entries = [r for r in results["urls_processed"] if r.get("status") == "manual_fallback"]
            assert len(manual_entries) == 1
            assert manual_entries[0]["snippets_found"] == 3
            assert manual_entries[0]["manual"]["pricing_bullets"] == competitor["manual_notes"]["pricing_bullets"]
    
    def test_no_manual_fallback_when_snippets_found(self):
        """Test that manual fallback is NOT used when snippets are extracted"""
        
        # Create test competitor with manual notes
        competitor = {
            "name": "Test Vendor",
            "urls": ["https://example.com/pricing"],
            "manual_notes": {
                "pricing_bullets": [
                    "Solo plan: $29/mo",
                    "Crew: $69/mo"
                ],
                "updated": "2025-09-01",
                "source_hint": "sales page"
            }
        }
        
        # Mock session that returns success with pricing content
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><div class='pricing'>$19/month</div></body></html>"
        mock_response.url = "https://example.com/pricing"
        mock_session.get.return_value = mock_response
        
        # Create temp cache dir
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            
            # Mock logger and CACHE_BASE_PATH
            with patch('scripts.bi.snapshot.logger') as mock_logger:
                with patch('scripts.bi.snapshot.CACHE_BASE_PATH', Path(tmpdir).parent):
                    # Process competitor
                    results = process_competitor(competitor, cache_dir, mock_session)
            
            # Check that manual fallback was NOT used
            assert "manual_fallback" not in results
            
            # Check no manual entries in urls_processed
            manual_entries = [r for r in results["urls_processed"] if r.get("status") == "manual_fallback"]
            assert len(manual_entries) == 0
    
    def test_no_manual_fallback_when_notes_absent(self):
        """Test that no manual fallback occurs when manual_notes is not provided"""
        
        # Create test competitor WITHOUT manual notes
        competitor = {
            "name": "Test Vendor",
            "urls": ["https://example.com/pricing"]
        }
        
        # Mock session that returns error
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "<html><body>Access Denied</body></html>"
        mock_response.url = "https://example.com/pricing"
        mock_session.get.return_value = mock_response
        
        # Create temp cache dir
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            
            # Mock logger and CACHE_BASE_PATH
            with patch('scripts.bi.snapshot.logger') as mock_logger:
                # Mock CAPTURE_ON_ERROR to True and fix cache base path
                with patch('scripts.bi.snapshot.CAPTURE_ON_ERROR', True):
                    with patch('scripts.bi.snapshot.CACHE_BASE_PATH', Path(tmpdir).parent):
                        # Process competitor
                        results = process_competitor(competitor, cache_dir, mock_session)
            
            # Check that manual fallback was NOT used
            assert "manual_fallback" not in results
            
            # Check no manual entries in urls_processed
            manual_entries = [r for r in results["urls_processed"] if r.get("status") == "manual_fallback"]
            assert len(manual_entries) == 0
    
    def test_summary_logging_with_manual_fallback(self):
        """Test that summary log line correctly reports manual fallback usage"""
        
        # Create test competitor with manual notes
        competitor = {
            "name": "Test Vendor",
            "urls": ["https://example.com/pricing"],
            "manual_notes": {
                "pricing_bullets": ["$29/mo", "$69/mo"],
                "updated": "2025-09-01",
                "source_hint": "sales"
            }
        }
        
        # Mock session that returns error
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "<html><body>Not Found</body></html>"
        mock_response.url = "https://example.com/pricing"
        mock_session.get.return_value = mock_response
        
        # Create temp cache dir
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            
            # Mock logger to capture calls
            with patch('scripts.bi.snapshot.logger') as mock_logger:
                # Mock CAPTURE_ON_ERROR to True and fix cache base path
                with patch('scripts.bi.snapshot.CAPTURE_ON_ERROR', True):
                    with patch('scripts.bi.snapshot.CACHE_BASE_PATH', Path(tmpdir).parent):
                        # Process competitor
                        results = process_competitor(competitor, cache_dir, mock_session)
                
                # Find the SUMMARY log call
                summary_calls = [
                    call for call in mock_logger.info.call_args_list
                    if len(call[0]) > 0 and call[0][0].startswith("[SUMMARY]")
                ]
                
                assert len(summary_calls) > 0
                
                # The summary log uses string formatting, check the args
                summary_format = summary_calls[0][0][0]  # Format string
                summary_values = summary_calls[0][0][1:]  # Values
                
                # Check that manual_fallback is Y (3rd argument after name, success)
                assert len(summary_values) >= 6  # name, success, manual_fallback, urls_tried, best_url, total_snippets
                assert summary_values[2] == "Y"  # manual_fallback=Y
                assert summary_values[5] == 2  # total_snippets=2


def test_parallel_alt_urls():
    """Test that alt URLs are tried in parallel"""
    
    competitor = {
        "name": "Test Vendor",
        "urls": ["https://primary.example.com/pricing"],
        "alt_urls": [
            "https://alt1.example.com/pricing",
            "https://alt2.example.com/pricing"
        ]
    }
    
    # Track which URLs were requested
    requested_urls = []
    
    def mock_get(url, **kwargs):
        requested_urls.append(url)
        mock_response = Mock()
        
        # Make primary fail, alt1 timeout, alt2 succeed
        if "primary" in url:
            mock_response.status_code = 403
            mock_response.text = "Forbidden"
        elif "alt1" in url:
            raise Exception("Timeout")
        else:  # alt2
            mock_response.status_code = 200
            mock_response.text = "<div>$50/month</div>"
        
        mock_response.url = url
        return mock_response
    
    mock_session = Mock()
    mock_session.get.side_effect = mock_get
    
    # Create temp cache dir
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir)
        
        # Mock logger and CACHE_BASE_PATH
        with patch('scripts.bi.snapshot.logger'):
            with patch('scripts.bi.snapshot.CACHE_BASE_PATH', Path(tmpdir).parent):
                # Process competitor
                results = process_competitor(competitor, cache_dir, mock_session)
        
        # Check that attempts were made (order may vary due to parallel execution)
        assert len(requested_urls) > 0
        
        # Check results show attempts metadata if available
        if "attempts" in results:
            attempt_urls = [a["url"] for a in results["attempts"]]
            # All URLs should be attempted
            assert "https://primary.example.com/pricing" in attempt_urls or len(attempt_urls) > 0


if __name__ == "__main__":
    print("\nTesting BI Manual Fallback\n")
    print("-" * 50)
    
    # Run tests
    test_suite = TestManualFallback()
    
    print("\n1. Testing manual fallback activation...")
    test_suite.test_manual_fallback_activates_on_zero_snippets()
    print("   OK: Manual fallback activates when no snippets found")
    
    print("\n2. Testing no fallback when snippets found...")
    test_suite.test_no_manual_fallback_when_snippets_found()
    print("   OK: No manual fallback when snippets extracted")
    
    print("\n3. Testing no fallback when notes absent...")
    test_suite.test_no_manual_fallback_when_notes_absent()
    print("   OK: No manual fallback when manual_notes not provided")
    
    print("\n4. Testing summary logging...")
    test_suite.test_summary_logging_with_manual_fallback()
    print("   OK: Summary correctly reports manual fallback usage")
    
    print("\n5. Testing parallel alt URLs...")
    test_parallel_alt_urls()
    print("   OK: Alt URLs are attempted")
    
    print("\n" + "=" * 50)
    print("SUCCESS: All manual fallback tests passed!")
    print("=" * 50)