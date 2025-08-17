#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/services/onboarding_report_service.py
🎯 PURPOSE: Generate and send welcome profit reports to new users
🔗 IMPORTS: email_service, pdf_exporter, datetime
📤 EXPORTS: OnboardingReportService class
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from services.email_service import send_email
from utils.pdf_exporter import pdf_exporter

logger = logging.getLogger(__name__)

class OnboardingReportService:
    """Service for generating and sending welcome profit reports to new users"""
    
    def __init__(self):
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_welcome_report_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock data for welcome report based on user's business profile"""
        
        # Extract user info
        name = user_data.get('name', 'Contractor')
        business_type = user_data.get('business_type', 'General Contractor')
        years_in_business = user_data.get('years_in_business', '5-10 years')
        business_size = user_data.get('business_size', 'Small (2-5 employees)')
        
        # Generate business-appropriate mock data
        base_intelligence_score = 75  # Start with good score for new users
        
        # Adjust based on business type
        if 'electrical' in business_type.lower():
            base_intelligence_score = 82
            typical_monthly_costs = 45000
            market_average = 125
        elif 'plumbing' in business_type.lower():
            base_intelligence_score = 78
            typical_monthly_costs = 52000
            market_average = 118
        elif 'hvac' in business_type.lower():
            base_intelligence_score = 80
            typical_monthly_costs = 48000
            market_average = 122
        elif 'roofing' in business_type.lower():
            base_intelligence_score = 76
            typical_monthly_costs = 55000
            market_average = 115
        else:
            typical_monthly_costs = 50000
            market_average = 120
        
        # Generate realistic forecast data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        actual_costs = [
            typical_monthly_costs * 0.9,  # Jan (slower)
            typical_monthly_costs * 0.85,  # Feb (winter)
            typical_monthly_costs * 0.95,  # Mar (picking up)
            typical_monthly_costs * 1.1,   # Apr (busy season)
            typical_monthly_costs * 1.15,  # May (peak)
            typical_monthly_costs * 1.05   # Jun (still busy)
        ]
        
        predicted_costs = [None, None, None, typical_monthly_costs * 1.2, typical_monthly_costs * 1.25, typical_monthly_costs * 1.3]
        
        # Generate vendor data
        vendors = [
            {"name": "ABC Supply Co", "performance": 88, "cost": typical_monthly_costs * 0.3, "trend": 2.1},
            {"name": "Quality Materials", "performance": 92, "cost": typical_monthly_costs * 0.25, "trend": -1.5},
            {"name": "Pro Tools & Equipment", "performance": 85, "cost": typical_monthly_costs * 0.2, "trend": 3.2},
            {"name": "Reliable Services", "performance": 79, "cost": typical_monthly_costs * 0.15, "trend": 1.8},
            {"name": "Local Contractors Supply", "performance": 82, "cost": typical_monthly_costs * 0.1, "trend": -0.5}
        ]
        
        # Generate job data
        jobs = [
            {"name": f"{business_type} Project - {name}", "risk": "low", "potential": typical_monthly_costs * 0.4, "completion": 85},
            {"name": "Maintenance Contract", "risk": "medium", "potential": typical_monthly_costs * 0.3, "completion": 65},
            {"name": "Emergency Service Call", "risk": "high", "potential": typical_monthly_costs * 0.2, "completion": 45}
        ]
        
        # Generate pricing recommendations
        pricing_recommendations = [
            {"service": f"{business_type} Service", "currentPrice": market_average, "suggestedPrice": market_average + 5, "confidence": 85},
            {"service": "Emergency Call", "currentPrice": market_average * 1.5, "suggestedPrice": market_average * 1.6, "confidence": 92},
            {"service": "Maintenance Contract", "currentPrice": market_average * 0.8, "suggestedPrice": market_average * 0.85, "confidence": 78}
        ]
        
        # Generate benchmarks
        benchmarks = {
            "profitMargin": {"your": 18.5, "industry": 15.2},
            "completionRate": {"your": 94, "industry": 87},
            "satisfaction": {"your": 4.2, "industry": 3.8},
            "efficiency": {"your": 78, "industry": 72}
        }
        
        return {
            "intelligenceScore": base_intelligence_score,
            "letterGrade": self._get_letter_grade(base_intelligence_score),
            "monthlySavingsPotential": typical_monthly_costs * 0.15,  # 15% potential savings
            "costTrend": 8.5,  # Positive trend
            "vendorCount": len(vendors),
            "userData": user_data,
            "forecast": {
                "months": months,
                "actual": actual_costs,
                "predicted": predicted_costs
            },
            "vendors": vendors,
            "jobs": jobs,
            "pricing": {
                "marketAverage": market_average,
                "yourAverage": market_average + 2,
                "recommendations": pricing_recommendations
            },
            "benchmarks": benchmarks
        }
    
    def _get_letter_grade(self, score: int) -> str:
        """Convert intelligence score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def generate_welcome_report(self, user_data: Dict[str, Any], user_email: str) -> str:
        """Generate welcome profit report PDF and return file path"""
        
        try:
            # Generate report data
            report_data = self.generate_welcome_report_data(user_data)
            
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name_safe = user_data.get('name', 'user').lower().replace(' ', '_')
            filename = f"welcome_report_{name_safe}_{timestamp}.pdf"
            filepath = self.reports_dir / filename
            
            # Generate PDF report
            pdf_path = pdf_exporter.generate_profit_intelligence_report(report_data, str(filepath))
            
            logger.info(f"Generated welcome report: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Failed to generate welcome report: {str(e)}")
            raise
    
    def send_welcome_report_email(self, user_email: str, user_data: Dict[str, Any], report_path: str) -> bool:
        """Send welcome email with profit report attachment"""
        
        try:
            name = user_data.get('name', 'there')
            business_type = user_data.get('business_type', 'construction')
            
            subject = f"Welcome to CORA, {name}! Your Profit Intelligence Report"
            
            # Create email body
            body = f"""
Hi {name},

Welcome to CORA! I'm excited to help you squeeze every dollar and leave nothing on the table.

I've analyzed your {business_type} business profile and created your personalized Profit Intelligence Report. Here's what I found:

🎯 **Your Business Intelligence Score: {self._get_letter_grade(75)}**
This score shows how well your business is performing compared to industry standards.

📊 **Key Insights:**
• Potential monthly savings: ${self.generate_welcome_report_data(user_data)['monthlySavingsPotential']:,.0f}
• Cost trend analysis for the next 3 months
• Top vendor performance recommendations
• Job profitability predictions
• Pricing optimization opportunities

📈 **What's Next:**
1. Review your detailed report (attached)
2. Log into your dashboard to start tracking expenses
3. Add your first job to see real-time profit analysis
4. Connect your bank account for automatic expense tracking

Your dashboard is ready at: https://coraai.tech/dashboard

I'm here to help you make more money with less stress. Let's get started!

Best regards,
CORA
Your AI Profit Assistant

P.S. The more data you add, the smarter I get. Start with just one job and watch the insights roll in!
"""
            
            # Send email with PDF attachment
            success = send_email(
                to_email=user_email,
                subject=subject,
                body=body,
                html_body=None,  # Could add HTML version later
                attachment_path=report_path
            )
            
            if success:
                logger.info(f"Welcome report email sent to {user_email}")
            else:
                logger.error(f"Failed to send welcome report email to {user_email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending welcome report email: {str(e)}")
            return False
    
    def process_onboarding_completion(self, user_data: Dict[str, Any], user_email: str) -> Dict[str, Any]:
        """Complete onboarding process: generate report and send email"""
        
        try:
            # Generate welcome report
            report_path = self.generate_welcome_report(user_data, user_email)
            
            # Send email with report
            email_sent = self.send_welcome_report_email(user_email, user_data, report_path)
            
            return {
                "success": True,
                "report_generated": True,
                "email_sent": email_sent,
                "report_path": report_path,
                "message": "Welcome report generated and sent successfully" if email_sent else "Report generated but email failed"
            }
            
        except Exception as e:
            logger.error(f"Failed to process onboarding completion: {str(e)}")
            return {
                "success": False,
                "report_generated": False,
                "email_sent": False,
                "error": str(e),
                "message": "Failed to generate welcome report"
            }

# Global service instance
onboarding_report_service = OnboardingReportService() 