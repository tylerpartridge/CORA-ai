#!/usr/bin/env python3
"""
Nav Font Size Debug Tool
Run this to check what's causing nav font inconsistencies
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import app
from fastapi.testclient import TestClient
import re

client = TestClient(app)

def check_page(url):
    print(f"\n{'='*60}")
    print(f"Checking {url}")
    print('='*60)
    
    response = client.get(url)
    html = response.text
    
    # Check CSS files
    css_files = re.findall(r'<link[^>]+href="([^"]+\.css[^"]*)"', html)
    print(f"\nCSS Files ({len(css_files)}):")
    for i, css in enumerate(css_files, 1):
        print(f"  {i}. {css}")
    
    # Check for inline styles on nav
    nav_section = re.search(r'<nav[^>]*>.*?</nav>', html, re.DOTALL)
    if nav_section:
        nav_html = nav_section.group()
        
        # Check for inline color style
        if 'style="color: #4db8ff' in nav_html:
            print("\n❌ PROBLEM: Login link has inline blue color style!")
        
        # Check for any inline styles
        inline_styles = re.findall(r'style="([^"]+)"', nav_html)
        if inline_styles:
            print(f"\n⚠️ Found {len(inline_styles)} inline styles in nav:")
            for style in inline_styles[:3]:  # Show first 3
                print(f"    - {style}")
    
    # Check for style blocks
    style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
    if style_blocks:
        print(f"\n⚠️ Found {len(style_blocks)} <style> blocks")
        for i, block in enumerate(style_blocks, 1):
            if '.nav-link' in block or 'font-size' in block:
                print(f"  Style block {i} contains nav-link or font-size rules!")
                # Show a snippet
                lines = [line.strip() for line in block.split('\n') if 'nav-link' in line or 'font-size' in line]
                for line in lines[:3]:
                    print(f"    {line}")
    
    # Check specific issues
    if 'font-size: 14px' in html:
        print("\n⚠️ Found 'font-size: 14px' somewhere in HTML")
    
    if 'font-size: 1rem' in html:
        count = html.count('font-size: 1rem')
        print(f"\n📝 Found 'font-size: 1rem' {count} times")
    
    if 'font-size: 16px' in html:
        count = html.count('font-size: 16px')
        print(f"\n✓ Found 'font-size: 16px' {count} times")

# Check both pages
check_page('/login')
check_page('/signup')

# Compare
print(f"\n{'='*60}")
print("COMPARISON")
print('='*60)

login_response = client.get('/login')
signup_response = client.get('/signup')

# Extract just the nav sections
login_nav = re.search(r'<nav[^>]*>.*?</nav>', login_response.text, re.DOTALL)
signup_nav = re.search(r'<nav[^>]*>.*?</nav>', signup_response.text, re.DOTALL)

if login_nav and signup_nav:
    if login_nav.group() == signup_nav.group():
        print("✓ Nav HTML is IDENTICAL on both pages")
    else:
        print("❌ Nav HTML is DIFFERENT between pages")
        
        # Find specific differences
        login_styles = set(re.findall(r'style="([^"]+)"', login_nav.group()))
        signup_styles = set(re.findall(r'style="([^"]+)"', signup_nav.group()))
        
        if login_styles != signup_styles:
            print("\nInline style differences:")
            only_login = login_styles - signup_styles
            only_signup = signup_styles - login_styles
            if only_login:
                print(f"  Only on login: {only_login}")
            if only_signup:
                print(f"  Only on signup: {only_signup}")

print("\n" + "="*60)
print("Run this script after restarting the server to see changes")
print("="*60)