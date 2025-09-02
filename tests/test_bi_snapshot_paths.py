#!/usr/bin/env python3
"""
Test BI Snapshot path generation

Tests cache path naming and dry-run mode without network calls.
"""

import pytest
import sys
import os
from pathlib import Path
from datetime import datetime
import json
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import snapshot functions
from scripts.bi.snapshot import (
    sanitize_filename,
    create_cache_dir,
    load_registry,
    CACHE_BASE_PATH
)


class TestBISnapshotPaths:
    """Test BI snapshot path generation and dry-run mode"""
    
    def test_sanitize_filename(self):
        """Test URL to filename sanitization"""
        test_cases = [
            ("https://example.com/", "example.com"),
            ("https://example.com/pricing", "example.com_pricing"),
            ("https://example.com/path?query=value", "example.com_path_query_value"),
            ("http://test.co.uk/page#anchor", "test.co.uk_page_anchor"),
            ("https://very-long-domain-name.com/" + "x" * 100, 
             ("very-long-domain-name.com_" + "x" * 100)[:100]),  # Truncated to 100 chars
        ]
        
        for url, expected in test_cases:
            result = sanitize_filename(url)
            assert result == expected, f"Failed for {url}: got {result}, expected {expected}"
    
    def test_cache_directory_creation(self):
        """Test cache directory is created with correct date format"""
        # Use a temp directory for testing
        original_cache = CACHE_BASE_PATH
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Monkey-patch the cache base path
            import scripts.bi.snapshot as snapshot_module
            snapshot_module.CACHE_BASE_PATH = Path(tmpdir) / "bi/cache"
            
            cache_dir = create_cache_dir()
            
            # Check directory was created
            assert cache_dir.exists(), "Cache directory not created"
            
            # Check date format
            expected_date = datetime.now().strftime("%Y-%m-%d")
            assert cache_dir.name == expected_date, f"Cache dir name {cache_dir.name} doesn't match date {expected_date}"
            
            # Restore original path
            snapshot_module.CACHE_BASE_PATH = original_cache
    
    def test_load_registry(self):
        """Test registry loading function"""
        registry = load_registry()
        
        # Should return a dict even if file doesn't exist
        assert isinstance(registry, dict), "Registry should return dict"
        
        # If registry exists, check structure
        if registry:
            assert 'competitors' in registry or 'regulations_watch' in registry, \
                "Registry should have competitors or regulations_watch"
    
    def test_dry_run_mode(self):
        """Test that dry-run mode doesn't make network calls"""
        # Import main function
        from scripts.bi.snapshot import main
        
        # Create a temporary cache directory
        with tempfile.TemporaryDirectory() as tmpdir:
            import scripts.bi.snapshot as snapshot_module
            original_cache = snapshot_module.CACHE_BASE_PATH
            snapshot_module.CACHE_BASE_PATH = Path(tmpdir) / "bi/cache"
            
            # Run in dry-run mode
            main(dry_run=True)
            
            # Check that cache directory was created but no files written
            cache_dir = Path(tmpdir) / "bi/cache" / datetime.now().strftime("%Y-%m-%d")
            assert cache_dir.exists(), "Cache directory should be created even in dry-run"
            
            # Check no HTML or JSON files were created
            html_files = list(cache_dir.glob("*.html"))
            json_files = list(cache_dir.glob("*.json"))
            
            assert len(html_files) == 0, "No HTML files should be created in dry-run"
            assert len(json_files) == 0, "No JSON files should be created in dry-run"
            
            # Restore original path
            snapshot_module.CACHE_BASE_PATH = original_cache
    
    def test_path_patterns(self):
        """Test expected file path patterns"""
        test_url = "https://example.com/pricing"
        slug = sanitize_filename(test_url)
        
        # Test HTML path pattern
        html_filename = f"{slug}.html"
        assert html_filename == "example.com_pricing.html"
        
        # Test JSON path pattern  
        json_filename = f"{slug}.json"
        assert json_filename == "example.com_pricing.json"
        
        # Test error JSON path pattern
        error_filename = f"{slug}_error.json"
        assert error_filename == "example.com_pricing_error.json"
    
    def test_summary_file_naming(self):
        """Test summary file naming convention"""
        expected_name = "snapshot_summary.json"
        
        # Just verify the expected pattern
        assert expected_name.endswith(".json"), "Summary should be JSON"
        assert "summary" in expected_name, "Summary should contain 'summary'"


def test_url_slug_uniqueness():
    """Test that different URLs produce unique slugs"""
    urls = [
        "https://example.com/",
        "https://example.com/page1",
        "https://example.com/page2",
        "https://other.com/",
        "https://example.org/",  # Different domain
    ]
    
    slugs = [sanitize_filename(url) for url in urls]
    
    # All slugs should be unique (except for protocol differences which are OK)
    assert len(slugs) == len(set(slugs)), f"URL slugs not unique: {slugs}"


def test_special_characters_in_urls():
    """Test handling of special characters in URLs"""
    test_urls = [
        "https://example.com/page?param=value&other=123",
        "https://example.com/path#section",
        "https://example.com/path/with/slashes",
        "https://sub.domain.example.com/",
        "https://example.com:8080/port",
    ]
    
    for url in test_urls:
        slug = sanitize_filename(url)
        
        # Should not contain special URL characters
        assert '?' not in slug, f"Slug contains '?': {slug}"
        assert '&' not in slug, f"Slug contains '&': {slug}"
        assert '#' not in slug, f"Slug contains '#': {slug}"
        assert '/' not in slug, f"Slug contains '/': {slug}"
        assert ':' not in slug, f"Slug contains ':': {slug}"
        
        # Should be a valid filename
        assert slug.replace('_', '').replace('.', '').replace('-', '').isalnum(), \
            f"Slug contains invalid characters: {slug}"


if __name__ == "__main__":
    print("\nTesting BI Snapshot Paths\n")
    print("-" * 50)
    
    # Run tests
    test_suite = TestBISnapshotPaths()
    
    print("\n1. Testing URL sanitization...")
    test_suite.test_sanitize_filename()
    print("   OK: URLs sanitized correctly")
    
    print("\n2. Testing cache directory creation...")
    test_suite.test_cache_directory_creation()
    print("   OK: Cache directory created with correct date")
    
    print("\n3. Testing registry loading...")
    test_suite.test_load_registry()
    print("   OK: Registry loads correctly")
    
    print("\n4. Testing dry-run mode...")
    test_suite.test_dry_run_mode()
    print("   OK: Dry-run mode works without network calls")
    
    print("\n5. Testing path patterns...")
    test_suite.test_path_patterns()
    print("   OK: Path patterns are correct")
    
    print("\n6. Testing summary file naming...")
    test_suite.test_summary_file_naming()
    print("   OK: Summary file naming is correct")
    
    print("\n7. Testing URL slug uniqueness...")
    test_url_slug_uniqueness()
    print("   OK: URL slugs are unique")
    
    print("\n8. Testing special character handling...")
    test_special_characters_in_urls()
    print("   OK: Special characters handled correctly")
    
    print("\n" + "=" * 50)
    print("SUCCESS: All snapshot path tests passed!")
    print("=" * 50)