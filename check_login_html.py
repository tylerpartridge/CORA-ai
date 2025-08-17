#!/usr/bin/env python
"""Check what login.html is actually being served"""

import requests
from bs4 import BeautifulSoup

def check_login_page():
    """Fetch and analyze the login page"""
    try:
        response = requests.get('http://localhost:8001/login')
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for info-panel
        info_panel = soup.find('div', class_='info-panel')
        if info_panel:
            info_content = info_panel.find('div', class_='info-content')
            if info_content:
                print("[OK] INFO-PANEL FOUND WITH CONTENT")
                # Check for specific content
                h2 = info_content.find('h2')
                if h2 and '$23,000' in h2.text:
                    print("[OK] Has '$23,000' heading")
                else:
                    print("[FAIL] Missing '$23,000' heading")
            else:
                print("[FAIL] INFO-PANEL EXISTS BUT NO CONTENT")
        else:
            print("[FAIL] NO INFO-PANEL FOUND")
            
        # Check form structure
        form_panel = soup.find('div', class_='form-panel')
        if form_panel:
            print("[OK] Form panel found")
        
        # Check raw HTML for info-panel
        if 'Stop Losing' in response.text:
            print("[OK] Raw HTML contains 'Stop Losing' text")
        else:
            print("[FAIL] Raw HTML missing 'Stop Losing' text")
            
        # Save what we're actually getting
        with open('actual_login.html', 'w') as f:
            f.write(response.text)
        print("\n[SAVED] Actual served HTML saved to actual_login.html")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_login_page()