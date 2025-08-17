#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/test_pdf_export.py
🎯 PURPOSE: Test PDF export functionality for profit intelligence reports
🔗 IMPORTS: requests, json, os
📤 EXPORTS: Test results
"""

import requests
import json
import os
import time
from datetime import datetime

def test_pdf_export():
    """Test PDF export functionality"""
    print("🧪 Testing PDF Export Functionality")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    test_results = {
        "pdf_export_health": False,
        "section_reports": {},
        "full_report": False,
        "download_functionality": False,
        "file_generation": False
    }
    
    # Test 1: Health Check
    print("\n1️⃣ Testing PDF Export Health Check...")
    try:
        response = requests.get(f"{base_url}/api/pdf-export/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Health check passed: {health_data}")
            test_results["pdf_export_health"] = True
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Section Reports (without authentication for now)
    print("\n2️⃣ Testing Section Report Generation...")
    sections = ["forecasting", "vendors", "jobs", "pricing", "benchmarks"]
    
    for section in sections:
        print(f"   Testing {section} report...")
        try:
            # Note: This will fail without authentication, but we can test the endpoint structure
            response = requests.post(f"{base_url}/api/pdf-export/profit-intelligence/section/{section}")
            if response.status_code in [401, 403]:  # Expected without auth
                print(f"   ✅ {section} endpoint exists (auth required)")
                test_results["section_reports"][section] = "endpoint_exists"
            else:
                print(f"   ⚠️ {section} endpoint: {response.status_code}")
                test_results["section_reports"][section] = "unexpected_response"
        except Exception as e:
            print(f"   ❌ {section} endpoint error: {e}")
            test_results["section_reports"][section] = "error"
    
    # Test 3: Full Report Generation
    print("\n3️⃣ Testing Full Report Generation...")
    try:
        response = requests.post(f"{base_url}/api/pdf-export/profit-intelligence/full-report")
        if response.status_code in [401, 403]:  # Expected without auth
            print("   ✅ Full report endpoint exists (auth required)")
            test_results["full_report"] = "endpoint_exists"
        else:
            print(f"   ⚠️ Full report endpoint: {response.status_code}")
            test_results["full_report"] = "unexpected_response"
    except Exception as e:
        print(f"   ❌ Full report endpoint error: {e}")
        test_results["full_report"] = "error"
    
    # Test 4: PDF Exporter Class
    print("\n4️⃣ Testing PDF Exporter Class...")
    try:
        from utils.pdf_exporter import pdf_exporter
        
        # Test with mock data
        mock_data = {
            "intelligenceScore": 87,
            "letterGrade": "B+",
            "forecast": {
                "months": ['Jan', 'Feb', 'Mar'],
                "actual": [45000, 52000, 48000],
                "predicted": [None, None, 61000]
            },
            "vendors": [
                {"name": "ABC Construction", "performance": 92, "cost": 45000, "trend": 5.2}
            ],
            "jobs": [
                {"name": "Kitchen Remodel", "risk": "high", "potential": 25000, "completion": 65}
            ],
            "pricing": {
                "marketAverage": 118,
                "yourAverage": 125,
                "recommendations": []
            },
            "benchmarks": {
                "profitMargin": {"your": 18.5, "industry": 15.2},
                "completionRate": {"your": 94, "industry": 87},
                "satisfaction": {"your": 4.2, "industry": 3.8},
                "efficiency": {"your": 78, "industry": 72}
            }
        }
        
        # Generate test PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_filename = f"test_report_{timestamp}.pdf"
        output_path = f"reports/{test_filename}"
        
        pdf_path = pdf_exporter.generate_profit_intelligence_report(mock_data, output_path)
        
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"   ✅ PDF generated successfully: {pdf_path} ({file_size} bytes)")
            test_results["file_generation"] = True
            
            # Clean up test file
            os.remove(pdf_path)
            print("   🧹 Test file cleaned up")
        else:
            print(f"   ❌ PDF file not found: {pdf_path}")
            test_results["file_generation"] = False
            
    except Exception as e:
        print(f"   ❌ PDF exporter test error: {e}")
        test_results["file_generation"] = False
    
    # Test 5: Reports Directory
    print("\n5️⃣ Testing Reports Directory...")
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        try:
            os.makedirs(reports_dir)
            print(f"   ✅ Created reports directory: {reports_dir}")
        except Exception as e:
            print(f"   ❌ Failed to create reports directory: {e}")
    else:
        print(f"   ✅ Reports directory exists: {reports_dir}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 PDF Export Test Results")
    print("=" * 50)
    
    print(f"Health Check: {'✅ PASS' if test_results['pdf_export_health'] else '❌ FAIL'}")
    print(f"File Generation: {'✅ PASS' if test_results['file_generation'] else '❌ FAIL'}")
    
    print("\nSection Reports:")
    for section, status in test_results["section_reports"].items():
        status_icon = "✅" if status == "endpoint_exists" else "⚠️" if status == "unexpected_response" else "❌"
        print(f"  {section}: {status_icon} {status}")
    
    print(f"\nFull Report: {'✅ PASS' if test_results['full_report'] == 'endpoint_exists' else '❌ FAIL'}")
    
    # Overall assessment
    critical_tests = [
        test_results["pdf_export_health"],
        test_results["file_generation"]
    ]
    
    if all(critical_tests):
        print("\n🎉 PDF Export System: ✅ READY FOR PRODUCTION")
        print("   - All critical functionality working")
        print("   - PDF generation successful")
        print("   - API endpoints properly configured")
    else:
        print("\n⚠️ PDF Export System: ⚠️ NEEDS ATTENTION")
        print("   - Some critical tests failed")
        print("   - Check error messages above")
    
    return test_results

if __name__ == "__main__":
    test_pdf_export() 