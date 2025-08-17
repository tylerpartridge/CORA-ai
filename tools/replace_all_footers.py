import os
import re

# Read the exact footer from pricing page
with open('exact_footer.html', 'r', encoding='utf-8') as f:
    exact_footer = f.read()

# List of files to update (excluding pricing.html since that's our source)
html_files = [
    'index.html',
    'features.html',
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

def replace_footer(file_path):
    """Replace entire footer with exact copy from pricing"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find footer start and end
        footer_start = content.find('<!-- Footer -->')
        if footer_start == -1:
            print(f"[ERROR] {file_path} - No footer found")
            return False
            
        # Find the closing </footer> tag
        footer_end = content.find('</footer>', footer_start)
        if footer_end == -1:
            print(f"[ERROR] {file_path} - No closing footer tag")
            return False
            
        footer_end += len('</footer>')
        
        # Replace the entire footer section
        new_content = content[:footer_start] + exact_footer + content[footer_end:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"[OK] {file_path} - Replaced entire footer")
        return True
        
    except Exception as e:
        print(f"[ERROR] {file_path} - {str(e)}")
        return False

# Update all files
total_files = len(html_files)
updated_files = 0

for file in html_files:
    if os.path.exists(file):
        if replace_footer(file):
            updated_files += 1
    else:
        print(f"[ERROR] {file} - File not found")

print(f"\nSummary: Updated {updated_files} out of {total_files} files")