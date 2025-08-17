import os
import re

# List of HTML files to update (exclude pricing and signup as they already have it correct)
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

def move_fontawesome_to_end(file_path):
    """Move Font Awesome CSS to just before closing body tag"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and remove the Font Awesome link
        fa_pattern = r'(\s*<!-- Font Awesome -->\s*)?<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">\s*'
        
        if re.search(fa_pattern, content):
            # Remove it from current position
            content = re.sub(fa_pattern, '', content)
            
            # Add it just before </body>
            fa_link = '\n    <!-- Font Awesome - loaded at end like landing page -->\n    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">\n    \n'
            content = content.replace('</body>', fa_link + '</body>')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] {file_path} - Moved Font Awesome to end")
            return True
        else:
            print(f"[SKIP] {file_path} - Font Awesome not found")
            return False
            
    except Exception as e:
        print(f"[ERROR] {file_path} - {str(e)}")
        return False

# Update all files
total_files = len(html_files)
updated_files = 0

for file in html_files:
    if os.path.exists(file):
        if move_fontawesome_to_end(file):
            updated_files += 1
    else:
        print(f"[ERROR] {file} - File not found")

print(f"\nSummary: Updated {updated_files} out of {total_files} files")