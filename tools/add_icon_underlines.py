import os
import re

# List of HTML files to update
html_files = [
    'index.html',
    'features.html', 
    'pricing.html',
    'signup.html',
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

def add_icon_underlines(file_path):
    """Add blue underlines to social media icons"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to find the icon tags
        patterns = [
            (r'<i class="fab fa-twitter" style="color: #FF9800;"></i>',
             '<i class="fab fa-twitter" style="color: #FF9800; border-bottom: 3px solid #1976D2; padding-bottom: 2px;"></i>'),
            (r'<i class="fab fa-linkedin" style="color: #FF9800;"></i>',
             '<i class="fab fa-linkedin" style="color: #FF9800; border-bottom: 3px solid #1976D2; padding-bottom: 2px;"></i>'),
            (r'<i class="fab fa-youtube" style="color: #FF9800;"></i>',
             '<i class="fab fa-youtube" style="color: #FF9800; border-bottom: 3px solid #1976D2; padding-bottom: 2px;"></i>')
        ]
        
        modified = False
        for old_pattern, new_pattern in patterns:
            if old_pattern in content and 'border-bottom: 3px solid #1976D2' not in content:
                content = content.replace(old_pattern, new_pattern)
                modified = True
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] {file_path} - Added blue underlines to icons")
            return True
        else:
            print(f"[SKIP] {file_path} - Already has underlines or icons not found")
            return False
            
    except Exception as e:
        print(f"[ERROR] {file_path} - {str(e)}")
        return False

# Update all files
total_files = len(html_files)
updated_files = 0

for file in html_files:
    if os.path.exists(file):
        if add_icon_underlines(file):
            updated_files += 1
    else:
        print(f"[ERROR] {file} - File not found")

print(f"\nSummary: Updated {updated_files} out of {total_files} files")