import os
import re

# List of all HTML files
html_files = [
    'index.html',
    'features.html',
    'privacy.html',
    'terms.html',
    'waitlist.html',
    'admin.html',
    'dashboard_unified.html',
    'onboarding/welcome.html',
    'onboarding/connect_bank.html',
    'onboarding/success.html',
    'integrations/plaid.html',
    'integrations/quickbooks.html',
    'integrations/stripe.html'
]

# Pattern to remove the CSS block I added
css_pattern = r'\s*<style>\s*\/\* Force blue underlines on footer social media icons like pricing page \*\/\s*footer \.fab\.fa-twitter,\s*footer \.fab\.fa-linkedin,\s*footer \.fab\.fa-youtube \{\s*text-decoration: underline !important;\s*text-decoration-color: #1976D2 !important;\s*text-decoration-thickness: 3px !important;\s*text-underline-offset: 3px !important;\s*\}\s*</style>\s*'

def remove_underline_css(file_path):
    """Remove the underline CSS I added"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove the CSS block
        if re.search(css_pattern, content):
            content = re.sub(css_pattern, '', content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"[OK] {file_path} - Removed underline CSS")
            return True
        else:
            print(f"[SKIP] {file_path} - CSS not found")
            return False
            
    except Exception as e:
        print(f"[ERROR] {file_path} - {str(e)}")
        return False

# Update all files
total_files = len(html_files)
updated_files = 0

for file in html_files:
    if os.path.exists(file):
        if remove_underline_css(file):
            updated_files += 1
    else:
        print(f"[ERROR] {file} - File not found")

print(f"\nSummary: Removed CSS from {updated_files} out of {total_files} files")