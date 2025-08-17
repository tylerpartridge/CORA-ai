import os

# Define the pattern to find and replace
old_pattern = '''                            <i class="fab fa-youtube" style="color: #FF9800;"></i>
                        </a>
                    </div>
                </div>'''

new_pattern = '''                            <i class="fab fa-youtube" style="color: #FF9800;"></i>
                        </a>
                    </div>
                    <!-- Decorative blue lines -->
                    <div class="mt-3">
                        <div style="height: 3px; width: 60px; background: #1976D2; margin-bottom: 8px;"></div>
                        <div style="height: 3px; width: 40px; background: #1976D2; margin-bottom: 8px;"></div>
                        <div style="height: 3px; width: 20px; background: #1976D2;"></div>
                    </div>
                </div>'''

# List of HTML files to update
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

for file in html_files:
    file_path = file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if blue lines already exist
        if 'Decorative blue lines' in content:
            print(f"[SKIP] {file_path} - Blue lines already exist")
            continue
            
        # Replace the pattern
        if old_pattern in content:
            new_content = content.replace(old_pattern, new_pattern)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"[OK] {file_path} - Added blue lines")
        else:
            print(f"[WARNING] {file_path} - Pattern not found")
            
    except Exception as e:
        print(f"[ERROR] {file_path} - {str(e)}")