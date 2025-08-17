#!/usr/bin/env python3
"""
Repair the broken HTML structure in pages
"""
import re
import os

def repair_html_file(filepath):
    """Fix the broken HTML structure"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove duplicate or misplaced navigation sections
    # First, extract the proper navigation
    proper_nav = '''    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark sticky-top" style="background: linear-gradient(180deg, rgba(26, 26, 26, 0.98) 0%, rgba(26, 26, 26, 0.95) 100%); border-bottom: 3px solid #FF9800;">
        <div class="container">
            <a class="navbar-brand" href="/">
                <img src="/static/images/logos/cora-logo.png" alt="CORA" style="height: 45px;">
            </a>
            
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse justify-content-end" id="navbarNav">
                <ul class="navbar-nav align-items-center">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/features">Features</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/how-it-works">How It Works</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/pricing">Pricing</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/blog">Blog</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/reviews">Reviews</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/contact">Contact</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/login" style="color: #4db8ff;">Login</a>
                    </li>
                    <li class="nav-item ms-3">
                        <a class="btn" href="/signup" style="background: #FF9800; color: #1a1a1a; padding: 0.75rem 2rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; border-radius: 4px;">Start Free Trial</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>'''
    
    # Find where </head> ends and <body> begins
    head_end = content.find('</head>')
    body_start = content.find('<body>', head_end)
    
    if head_end == -1 or body_start == -1:
        print(f"    [ERROR] Could not find proper HTML structure")
        return False
    
    # Find the first real content after body (not navigation)
    # Look for the hero section or main content
    hero_patterns = [
        r'<section[^>]*class="[^"]*hero[^"]*"',
        r'<section[^>]*id="[^"]*hero[^"]*"',
        r'<div[^>]*class="[^"]*container[^"]*"',
        r'<main[^>]*>',
        r'<!-- Hero Section',
        r'<!-- Blog Hero',
        r'<!-- Signup Form',
    ]
    
    content_start = -1
    for pattern in hero_patterns:
        match = re.search(pattern, content[body_start:], re.IGNORECASE)
        if match:
            content_start = body_start + match.start()
            break
    
    if content_start == -1:
        # If no hero section found, just find any section
        section_match = re.search(r'<section', content[body_start:], re.IGNORECASE)
        if section_match:
            content_start = body_start + section_match.start()
        else:
            print(f"    [WARNING] Could not find main content section")
            return False
    
    # Rebuild the file properly
    before_body = content[:body_start+6]  # Include '<body>'
    after_content = content[content_start:]
    
    # Reconstruct with proper navigation
    new_content = before_body + '\n' + proper_nav + '\n\n' + after_content
    
    # Write the repaired content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

# Pages to repair
pages = [
    'web/templates/features.html',
    'web/templates/pricing.html',
    'web/templates/reviews.html',
    'web/templates/contact.html',
    'web/templates/how-it-works.html',
    'web/templates/blog/index.html'
]

print("Repairing broken HTML structure...")
print("=" * 50)

for page in pages:
    if os.path.exists(page):
        print(f"Repairing {os.path.basename(page)}...", end=" ")
        if repair_html_file(page):
            print("[OK]")
        else:
            print("[FAILED]")
    else:
        print(f"[SKIP] {os.path.basename(page)} not found")

print("=" * 50)
print("Repair complete!")