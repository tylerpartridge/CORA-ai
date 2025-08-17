import os
import re

# List of all HTML files that need updating
html_files = [
    'admin.html',
    'privacy.html',
    'terms.html',
    'waitlist.html',
    'dashboard_unified.html',
    'onboarding/welcome.html',
    'onboarding/connect_bank.html',
    'onboarding/success.html',
    'integrations/plaid.html',
    'integrations/quickbooks.html',
    'integrations/stripe.html'
]

def update_fontawesome(file_path):
    """Update Font Awesome to 6.5.1 and move to end of body"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove any existing Font Awesome link (6.0.0 or other versions)
        fa_patterns = [
            r'<link\s+rel="stylesheet"\s+href="https://cdnjs\.cloudflare\.com/ajax/libs/font-awesome/[0-9.]+/css/all\.min\.css"\s*/?>\s*',
            r'<link\s+href="https://cdnjs\.cloudflare\.com/ajax/libs/font-awesome/[0-9.]+/css/all\.min\.css"\s+rel="stylesheet"\s*/?>\s*'
        ]
        
        modified = False
        for pattern in fa_patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, '', content)
                modified = True
        
        # If file doesn't have Font Awesome or had old version, add 6.5.1 at the end
        if modified or 'font-awesome' not in content.lower():
            # Add Font Awesome 6.5.1 just before </body>
            fa_link = '\n    <!-- Font Awesome - loaded at end like landing page -->\n    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">\n    \n'
            content = content.replace('</body>', fa_link + '</body>')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] {file_path} - Updated to Font Awesome 6.5.1 at end of body")
            return True
        else:
            print(f"[SKIP] {file_path} - Already has Font Awesome 6.5.1")
            return False
            
    except Exception as e:
        print(f"[ERROR] {file_path} - {str(e)}")
        return False

# Update all files
total_files = len(html_files)
updated_files = 0

for file in html_files:
    if os.path.exists(file):
        if update_fontawesome(file):
            updated_files += 1
    else:
        print(f"[ERROR] {file} - File not found")

print(f"\nSummary: Updated {updated_files} out of {total_files} files")