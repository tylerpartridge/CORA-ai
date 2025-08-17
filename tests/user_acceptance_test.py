#!/usr/bin/env python3
"""
User Acceptance Testing for CORA
Tests complete user journeys from a contractor's perspective
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
import random

BASE_URL = "http://localhost:8000"

class UserAcceptanceTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = None
        self.auth_token = None
        self.user_data = None
        
    async def test_complete_contractor_journey(self) -> Dict:
        """Test the complete contractor journey from landing to profit analysis"""
        results = {
            "journey": "Complete Contractor Journey",
            "steps": [],
            "passed": True,
            "user_satisfaction_score": 0
        }
        
        async with aiohttp.ClientSession() as self.session:
            # Step 1: Landing Page
            step1 = await self._test_landing_page()
            results["steps"].append(step1)
            if not step1["passed"]:
                results["passed"] = False
                
            # Step 2: Onboarding Flow
            step2 = await self._test_onboarding_flow()
            results["steps"].append(step2)
            if not step2["passed"]:
                results["passed"] = False
                
            # Step 3: Dashboard Access
            step3 = await self._test_dashboard_access()
            results["steps"].append(step3)
            if not step3["passed"]:
                results["passed"] = False
                
            # Step 4: Add Expenses
            step4 = await self._test_expense_entry()
            results["steps"].append(step4)
            if not step4["passed"]:
                results["passed"] = False
                
            # Step 5: View Profit Analysis
            step5 = await self._test_profit_analysis()
            results["steps"].append(step5)
            if not step5["passed"]:
                results["passed"] = False
                
            # Step 6: CORA Chat Interaction
            step6 = await self._test_cora_chat()
            results["steps"].append(step6)
            if not step6["passed"]:
                results["passed"] = False
                
        # Calculate satisfaction score
        passed_steps = sum(1 for step in results["steps"] if step["passed"])
        results["user_satisfaction_score"] = (passed_steps / len(results["steps"])) * 100
        
        return results
        
    async def _test_landing_page(self) -> Dict:
        """Test landing page experience"""
        result = {
            "step": "Landing Page",
            "passed": True,
            "time_taken": 0,
            "issues": []
        }
        
        start_time = time.time()
        
        try:
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status != 200:
                    result["passed"] = False
                    result["issues"].append(f"Landing page returned {response.status}")
                    
                text = await response.text()
                
                # Check for key elements
                required_elements = [
                    "CORA",
                    "contractors",
                    "profit",
                    "Get Started"
                ]
                
                for element in required_elements:
                    if element.lower() not in text.lower():
                        result["issues"].append(f"Missing key element: {element}")
                        
        except Exception as e:
            result["passed"] = False
            result["issues"].append(f"Error accessing landing page: {str(e)}")
            
        result["time_taken"] = time.time() - start_time
        return result
        
    async def _test_onboarding_flow(self) -> Dict:
        """Test onboarding flow"""
        result = {
            "step": "Onboarding Flow",
            "passed": True,
            "time_taken": 0,
            "issues": []
        }
        
        start_time = time.time()
        
        try:
            # Access onboarding page
            async with self.session.get(f"{self.base_url}/onboarding") as response:
                if response.status != 200:
                    result["passed"] = False
                    result["issues"].append("Cannot access onboarding page")
                    return result
                    
            # Simulate onboarding conversation
            conversation_flow = [
                {"message": "Mike Johnson", "phase": "greeting"},
                {"message": "I do general contracting and concrete work", "phase": "business_discovery"},
                {"message": "5-10 years", "phase": "years_experience"},
                {"message": "Small crew (2-5 people)", "phase": "business_size"},
                {"message": "Denver metro area", "phase": "service_area"},
                {"message": "Residential homeowners", "phase": "customer_type"},
                {"message": "Spreadsheets and paper", "phase": "current_tracking"},
                {"message": "Not knowing my real profit margins", "phase": "main_challenge"},
                {"message": "Summer", "phase": "busy_season"},
                {"message": "Increase profits", "phase": "business_goal"},
                {"message": "mike@johnsonconstruction.com", "phase": "email_collection"},
                {"message": "SecurePass123!", "phase": "password_creation"}
            ]
            
            for step in conversation_flow:
                url = f"{self.base_url}/api/onboarding/chat/message"
                data = {
                    "message": step["message"],
                    "metadata": {
                        "onboarding": True,
                        "phase": step["phase"]
                    }
                }
                
                async with self.session.post(url, json=data) as response:
                    if response.status != 200:
                        result["issues"].append(f"Onboarding step {step['phase']} failed")
                        
            # Complete onboarding
            complete_url = f"{self.base_url}/api/onboarding/complete"
            complete_data = {
                "userData": {
                    "name": "Mike Johnson",
                    "businessType": ["general_contractor", "concrete"],
                    "yearsInBusiness": "5-10",
                    "businessSize": "small_crew",
                    "serviceArea": "local",
                    "customerType": ["residential"],
                    "currentTracking": ["spreadsheets", "paper"],
                    "mainChallenge": "profitability",
                    "busySeason": "summer",
                    "businessGoal": "increase_profits",
                    "email": "mike@johnsonconstruction.com"
                }
            }
            
            async with self.session.post(complete_url, json=complete_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    self.user_data = complete_data["userData"]
                else:
                    result["passed"] = False
                    result["issues"].append("Failed to complete onboarding")
                    
        except Exception as e:
            result["passed"] = False
            result["issues"].append(f"Onboarding error: {str(e)}")
            
        result["time_taken"] = time.time() - start_time
        return result
        
    async def _test_dashboard_access(self) -> Dict:
        """Test dashboard access and personalization"""
        result = {
            "step": "Dashboard Access",
            "passed": True,
            "time_taken": 0,
            "issues": []
        }
        
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            async with self.session.get(f"{self.base_url}/dashboard", headers=headers) as response:
                if response.status != 200:
                    result["passed"] = False
                    result["issues"].append(f"Dashboard returned {response.status}")
                    
                text = await response.text()
                
                # Check for personalization
                if self.user_data and self.user_data["name"] not in text:
                    result["issues"].append("Dashboard not personalized with user name")
                    
                # Check for key dashboard elements
                required_elements = ["Talk to CORA", "Quick Actions", "Recent"]
                for element in required_elements:
                    if element not in text:
                        result["issues"].append(f"Missing dashboard element: {element}")
                        
        except Exception as e:
            result["passed"] = False
            result["issues"].append(f"Dashboard error: {str(e)}")
            
        result["time_taken"] = time.time() - start_time
        return result
        
    async def _test_expense_entry(self) -> Dict:
        """Test expense entry functionality"""
        result = {
            "step": "Expense Entry",
            "passed": True,
            "time_taken": 0,
            "issues": []
        }
        
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            # Add multiple expenses
            expenses = [
                {
                    "amount": 487.50,
                    "description": "Lumber for Johnson kitchen remodel",
                    "category": "Materials",
                    "vendor": "Home Depot",
                    "job_id": "johnson_kitchen",
                    "date": "2025-01-15"
                },
                {
                    "amount": 320.00,
                    "description": "Concrete for Martinez driveway",
                    "category": "Materials", 
                    "vendor": "Concrete Supply Co",
                    "job_id": "martinez_driveway",
                    "date": "2025-01-14"
                },
                {
                    "amount": 800.00,
                    "description": "Labor - 8 hours crew work",
                    "category": "Labor",
                    "vendor": "Internal",
                    "job_id": "johnson_kitchen",
                    "date": "2025-01-15"
                }
            ]
            
            for expense in expenses:
                url = f"{self.base_url}/api/expenses"
                async with self.session.post(url, json=expense, headers=headers) as response:
                    if response.status not in [200, 201]:
                        result["issues"].append(f"Failed to add expense: {expense['description']}")
                        
            # Verify expenses were added
            async with self.session.get(f"{self.base_url}/api/expenses", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if len(data.get("expenses", [])) < len(expenses):
                        result["issues"].append("Not all expenses were saved")
                else:
                    result["passed"] = False
                    result["issues"].append("Cannot retrieve expenses")
                    
        except Exception as e:
            result["passed"] = False
            result["issues"].append(f"Expense entry error: {str(e)}")
            
        result["time_taken"] = time.time() - start_time
        return result
        
    async def _test_profit_analysis(self) -> Dict:
        """Test profit analysis features"""
        result = {
            "step": "Profit Analysis",
            "passed": True,
            "time_taken": 0,
            "issues": []
        }
        
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            # Test profit analysis endpoints
            endpoints = [
                "/api/profit-analysis/summary",
                "/api/profit-analysis/quick-wins",
                "/api/profit-analysis/category-optimization",
                "/api/profit-analysis/job-profitability"
            ]
            
            for endpoint in endpoints:
                url = f"{self.base_url}{endpoint}"
                async with self.session.get(url, headers=headers) as response:
                    if response.status != 200:
                        result["issues"].append(f"Endpoint {endpoint} returned {response.status}")
                    else:
                        data = await response.json()
                        # Verify we get meaningful data
                        if not data:
                            result["issues"].append(f"No data from {endpoint}")
                            
            # Access profit dashboard
            async with self.session.get(f"{self.base_url}/profit-dashboard", headers=headers) as response:
                if response.status != 200:
                    result["issues"].append("Cannot access profit dashboard")
                    
        except Exception as e:
            result["passed"] = False
            result["issues"].append(f"Profit analysis error: {str(e)}")
            
        result["time_taken"] = time.time() - start_time
        return result
        
    async def _test_cora_chat(self) -> Dict:
        """Test CORA chat interaction"""
        result = {
            "step": "CORA Chat Interaction",
            "passed": True,
            "time_taken": 0,
            "issues": []
        }
        
        start_time = time.time()
        
        try:
            # Test contractor-specific questions
            questions = [
                "How much profit did I make on the Johnson kitchen job?",
                "What are my biggest expenses this month?",
                "Which vendors should I negotiate with?",
                "Am I charging enough for labor?"
            ]
            
            for question in questions:
                url = f"{self.base_url}/api/cora-chat-v2/"
                data = {
                    "message": question,
                    "metadata": {
                        "contractor_type": "general_contractor",
                        "business_size": "small_crew"
                    }
                }
                
                async with self.session.post(url, json=data) as response:
                    if response.status != 200:
                        result["issues"].append(f"CORA failed to answer: {question}")
                    else:
                        response_data = await response.json()
                        if not response_data.get("message"):
                            result["issues"].append(f"Empty response for: {question}")
                            
        except Exception as e:
            result["passed"] = False
            result["issues"].append(f"CORA chat error: {str(e)}")
            
        result["time_taken"] = time.time() - start_time
        return result
        
    def generate_report(self, results: Dict) -> str:
        """Generate user acceptance test report"""
        report = []
        report.append("=" * 60)
        report.append("USER ACCEPTANCE TEST REPORT")
        report.append("=" * 60)
        report.append(f"Test: {results['journey']}")
        report.append(f"Overall Status: {'PASSED' if results['passed'] else 'FAILED'}")
        report.append(f"User Satisfaction Score: {results['user_satisfaction_score']:.1f}%")
        report.append("")
        
        total_time = sum(step["time_taken"] for step in results["steps"])
        report.append(f"Total Journey Time: {total_time:.2f} seconds")
        report.append("")
        
        report.append("Step-by-Step Results:")
        report.append("-" * 40)
        
        for i, step in enumerate(results["steps"], 1):
            status = "PASSED" if step["passed"] else "FAILED"
            report.append(f"{i}. {step['step']}: {status} ({step['time_taken']:.2f}s)")
            
            if step["issues"]:
                for issue in step["issues"]:
                    report.append(f"   - {issue}")
                    
        report.append("")
        report.append("User Experience Assessment:")
        report.append("-" * 40)
        
        if results["user_satisfaction_score"] >= 90:
            report.append("EXCELLENT: Smooth, intuitive user experience")
        elif results["user_satisfaction_score"] >= 75:
            report.append("GOOD: Generally positive experience with minor issues")
        elif results["user_satisfaction_score"] >= 60:
            report.append("FAIR: Functional but needs improvement")
        else:
            report.append("POOR: Significant user experience issues")
            
        # Performance analysis
        report.append("")
        report.append("Performance Metrics:")
        report.append("-" * 40)
        
        for step in results["steps"]:
            if step["time_taken"] > 3.0:
                report.append(f"SLOW: {step['step']} took {step['time_taken']:.2f}s")
            elif step["time_taken"] < 0.5:
                report.append(f"FAST: {step['step']} took {step['time_taken']:.2f}s")
                
        return "\n".join(report)

async def main():
    """Run user acceptance tests"""
    print("CORA User Acceptance Testing")
    print("=" * 60)
    
    # Start the app if not running
    import subprocess
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status != 200:
                    print("Starting CORA application...")
                    subprocess.Popen(["python", "app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    await asyncio.sleep(5)
    except:
        print("Starting CORA application...")
        subprocess.Popen(["python", "app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        await asyncio.sleep(5)
        
    tester = UserAcceptanceTester()
    
    print("\nTesting Complete Contractor Journey...")
    print("This simulates a real contractor using CORA from start to finish\n")
    
    results = await tester.test_complete_contractor_journey()
    
    # Generate and print report
    report = tester.generate_report(results)
    print(report)
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"user_acceptance_report_{timestamp}.json"
    
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"\nDetailed report saved to: {report_file}")
    
    return 0 if results["passed"] else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    import sys
    sys.exit(exit_code)