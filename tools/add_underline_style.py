import os

# List of all HTML files (excluding pricing and signup which already work)
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

# CSS to add that forces blue underlines on footer social icons
css_to_add = '''
    <style>
        /* Force blue underlines on footer social media icons like pricing page */
        footer .fab.fa-twitter,
        footer .fab.fa-linkedin,
        footer .fab.fa-youtube {
            text-decoration: underline !important;
            text-decoration-color: #1976D2 !important;
            text-decoration-thickness: 3px !important;
            text-underline-offset: 3px !important;
        }
    </style>
'''

def add_underline_css(file_path):
    """Add CSS to force blue underlines on social icons"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if CSS already exists
        if 'Force blue underlines on footer social media icons' in content:
            print(f"[SKIP] {file_path} - CSS already exists")
            return False
        
        # Add CSS just before </head>
        content = content.replace('</head>', css_to_add + '\n</head>')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[OK] {file_path} - Added underline CSS")
        return True
        
    except Exception as e:
        print(f"[ERROR] {file_path} - {str(e)}")
        return False

# Update all files
total_files = len(html_files)
updated_files = 0

for file in html_files:
    if os.path.exists(file):
        if add_underline_css(file):
            updated_files += 1
    else:
        print(f"[ERROR] {file} - File not found")

print(f"\nSummary: Updated {updated_files} out of {total_files} files")