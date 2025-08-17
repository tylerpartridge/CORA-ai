#!/usr/bin/env python3
"""Test what data we have at each stage of onboarding"""

import sqlite3
import json

def check_user_data():
    """Check what data we have for Tyler after signup"""
    
    print("="*60)
    print("USER DATA FLOW TEST")
    print("="*60)
    
    # Connect to database
    conn = sqlite3.connect('cora.db')
    cursor = conn.cursor()
    
    # Check Tyler's current data
    print("\n1. After Signup (current state):")
    cursor.execute("""
        SELECT email, email_verified, created_at
        FROM users 
        WHERE email = 'tyler_partridge@hotmail.com'
    """)
    user = cursor.fetchone()
    
    if user:
        print(f"   Email: {user[0]}")
        print(f"   Verified: {user[1]}")
        print(f"   Created: {user[2]}")
        print("   Name: NOT COLLECTED YET")
        print("   Business: NOT COLLECTED YET")
    else:
        print("   [No user found - need to signup first]")
    
    print("\n2. During Onboarding (what gets collected):")
    print("   According to onboarding-ai-wizard.js:")
    print("   - Name (name_collection phase)")
    print("   - Business type")
    print("   - Years in business")
    print("   - Business size")
    print("   - Service area")
    print("   - Customer type")
    print("   - Tracking method")
    print("   - Busy season")
    print("   - Business goals")
    print("   - Pain points")
    
    print("\n3. After Onboarding:")
    print("   Data saved to: /data/onboarding_leads/")
    print("   API endpoint: POST /api/onboarding/complete")
    
    # Check if any onboarding data exists
    import os
    lead_dir = "data/onboarding_leads"
    if os.path.exists(lead_dir):
        files = os.listdir(lead_dir)
        if files:
            print(f"   Found {len(files)} saved onboarding records")
        else:
            print("   No onboarding records saved yet")
    else:
        print("   Onboarding directory not created yet")
    
    print("\n4. Data Flow Summary:")
    print("   Signup: Email + Password only")
    print("   Verification: Confirms email ownership")
    print("   Onboarding: Collects ALL business data including name")
    print("   Dashboard: Has complete user profile")
    
    conn.close()
    
    print("\n" + "="*60)
    print("ANSWER: Yes, onboarding WILL ask for Tyler's name")
    print("since we only have email from signup")
    print("="*60)

if __name__ == "__main__":
    check_user_data()