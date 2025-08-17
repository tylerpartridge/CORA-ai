#!/usr/bin/env python3
"""
[LOCATION] LOCATION: /CORA/tests/test_template_inheritance.py
[TARGET] PURPOSE: Automated tests for template inheritance system
[LINK] IMPORTS: pytest, FastAPI test client
[EXPORT] EXPORTS: Test suite for template consistency
"""

import pytest
from fastapi.testclient import TestClient
from bs4 import BeautifulSoup
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app

client = TestClient(app)

class TestTemplateInheritance:
    """Test suite for template inheritance consistency"""
    
    # Pages that should use template inheritance
    TEMPLATE_PAGES = [
        "/",
        "/features",
        "/how-it-works",
        "/pricing",
        "/reviews",
        "/contact",
        "/about",
    ]
    
    # Pages that return simple HTML (not using templates)
    SIMPLE_PAGES = [
        "/help",
        "/privacy",
        "/terms",
    ]
    
    def test_all_pages_load(self):
        """Test that all pages return 200 status"""
        for page in self.TEMPLATE_PAGES:
            response = client.get(page)
            assert response.status_code == 200, f"Page {page} failed with status {response.status_code}"
    
    def test_navbar_consistency(self):
        """Test that all pages have consistent navigation"""
        navbars = []
        
        for page in self.TEMPLATE_PAGES[:3]:  # Test first 3 pages
            response = client.get(page)
            soup = BeautifulSoup(response.text, 'html.parser')
            nav = soup.find('nav', class_='navbar')
            
            if nav:
                # Get nav links
                links = [a.get('href') for a in nav.find_all('a', class_='nav-link')]
                navbars.append(links)
        
        # Check all navbars are identical
        if navbars:
            first_nav = navbars[0]
            for nav in navbars[1:]:
                assert nav == first_nav, "Navigation inconsistent across pages"
    
    def test_footer_consistency(self):
        """Test that all pages have consistent footer"""
        footers = []
        
        for page in self.TEMPLATE_PAGES[:3]:  # Test first 3 pages
            response = client.get(page)
            soup = BeautifulSoup(response.text, 'html.parser')
            footer = soup.find('footer')
            
            if footer:
                # Check for key footer elements
                has_newsletter = 'Newsletter' in footer.text or 'Subscribe' in footer.text
                has_social = footer.find('a', href=lambda x: x and 'twitter' in x)
                has_copyright = '© 2025 CORA' in footer.text
                
                footers.append({
                    'newsletter': has_newsletter,
                    'social': has_social,
                    'copyright': has_copyright
                })
        
        # Check all footers have same elements
        if footers:
            first_footer = footers[0]
            for footer in footers[1:]:
                assert footer == first_footer, "Footer inconsistent across pages"
    
    def test_security_scripts_present(self):
        """Test that security scripts are loaded on all pages"""
        for page in self.TEMPLATE_PAGES:
            response = client.get(page)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for security.js
            security_script = soup.find('script', src=lambda x: x and 'security.js' in x)
            assert security_script is not None, f"security.js missing on {page}"
            
            # Check for api-error-handler.js
            error_handler = soup.find('script', src=lambda x: x and 'api-error-handler.js' in x)
            assert error_handler is not None, f"api-error-handler.js missing on {page}"
    
    def test_css_files_loaded(self):
        """Test that required CSS files are loaded"""
        required_css = [
            'bootstrap',
            'navbar.css',
            'construction-theme.css'
        ]
        
        for page in self.TEMPLATE_PAGES[:3]:
            response = client.get(page)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for css_file in required_css:
                css_link = soup.find('link', href=lambda x: x and css_file in x)
                assert css_link is not None, f"{css_file} missing on {page}"
    
    def test_no_duplicate_css_declarations(self):
        """Test that CSS isn't duplicated in page content"""
        for page in self.TEMPLATE_PAGES[:3]:
            response = client.get(page)
            
            # Count occurrences of common CSS patterns
            content = response.text
            
            # These should only appear once (in base template)
            assert content.count('--construction-orange: #FF9800') <= 1, \
                f"Duplicate CSS variables on {page}"
            assert content.count('font-family: \'Inter\'') <= 2, \
                f"Duplicate font declarations on {page}"
    
    def test_page_specific_content(self):
        """Test that each page has unique content"""
        contents = {}
        
        for page in self.TEMPLATE_PAGES[:3]:
            response = client.get(page)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove nav and footer to get main content
            nav = soup.find('nav')
            footer = soup.find('footer')
            if nav:
                nav.decompose()
            if footer:
                footer.decompose()
            
            # Get remaining content
            content = soup.get_text().strip()
            contents[page] = content
        
        # Ensure each page has unique content
        content_values = list(contents.values())
        for i, content1 in enumerate(content_values):
            for j, content2 in enumerate(content_values[i+1:], i+1):
                # Allow some similarity but not identical
                similarity = len(set(content1.split()) & set(content2.split())) / len(set(content1.split()))
                assert similarity < 0.8, f"Pages have too similar content (>80% overlap)"
    
    def test_bootstrap_loaded(self):
        """Test that Bootstrap JS is loaded correctly"""
        for page in self.TEMPLATE_PAGES[:2]:
            response = client.get(page)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for Bootstrap JS
            bootstrap_script = soup.find('script', src=lambda x: x and 'bootstrap' in x)
            assert bootstrap_script is not None, f"Bootstrap JS missing on {page}"
    
    def test_responsive_meta_tag(self):
        """Test that viewport meta tag is present"""
        for page in self.TEMPLATE_PAGES[:2]:
            response = client.get(page)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            assert viewport is not None, f"Viewport meta tag missing on {page}"
            assert 'width=device-width' in viewport.get('content', ''), \
                f"Viewport not configured for responsive on {page}"

def run_tests():
    """Run all template inheritance tests"""
    test_suite = TestTemplateInheritance()
    
    print("Running Template Inheritance Tests...")
    print("-" * 50)
    
    tests = [
        ("Page Loading", test_suite.test_all_pages_load),
        ("Navbar Consistency", test_suite.test_navbar_consistency),
        ("Footer Consistency", test_suite.test_footer_consistency),
        ("Security Scripts", test_suite.test_security_scripts_present),
        ("CSS Files", test_suite.test_css_files_loaded),
        ("No Duplicate CSS", test_suite.test_no_duplicate_css_declarations),
        ("Unique Content", test_suite.test_page_specific_content),
        ("Bootstrap Loading", test_suite.test_bootstrap_loaded),
        ("Responsive Meta", test_suite.test_responsive_meta_tag),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"[PASS] {test_name}")
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test_name}: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {test_name}: {str(e)}")
            failed += 1
    
    print("-" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)