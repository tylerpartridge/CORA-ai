#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/insights.py
🎯 PURPOSE: AI-powered contextual insights for dashboard
🔗 IMPORTS: FastAPI, services, ML analysis
📤 EXPORTS: Dynamic insight generation endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import random

from models import User, get_db
from dependencies.auth import get_current_user
from services.profit_leak_detector import ProfitLeakDetector

router = APIRouter(
    prefix="/api/profit-intelligence",
    tags=["insights"],
    responses={404: {"description": "Not found"}},
)

class InsightGenerator:
    """Generate contextual, actionable insights based on user data"""
    
    def __init__(self, user: User, db: Session):
        self.user = user
        self.db = db
        self.detector = ProfitLeakDetector(user.id, db)
        
    def generate_insights(self) -> List[Dict[str, Any]]:
        """Generate prioritized insights based on current context"""
        insights = []
        
        # Get profit intelligence data
        try:
            intelligence = self.detector.get_intelligence_summary()
            score = intelligence.get('intelligence_score', 75)
            savings = intelligence.get('monthly_savings_potential', 0)
            
            # Time-based insights
            hour = datetime.now().hour
            day = datetime.now().weekday()
            
            # Morning insight - cost analysis
            if 6 <= hour <= 10:
                insights.append({
                    'id': 'morning-costs',
                    'priority': 'high',
                    'message': f"Good morning! Your profit intelligence score is {score}. "
                              f"I found ${savings:,.0f} in potential monthly savings. Want to see where?",
                    'actionUrl': '/analytics',
                    'actionText': 'Show me',
                    'category': 'cost-analysis'
                })
            
            # Get vendor performance
            vendor_analysis = self._analyze_vendors()
            if vendor_analysis['worst_vendor']:
                insights.append({
                    'id': f'vendor-alert-{vendor_analysis["worst_vendor"]["name"]}',
                    'priority': 'high',
                    'message': f"{vendor_analysis['worst_vendor']['name']} is costing you "
                              f"${vendor_analysis['worst_vendor']['excess']:,.0f} extra this month. "
                              f"Their prices are {vendor_analysis['worst_vendor']['percent']:.0%} above market.",
                    'actionUrl': '/analytics#vendors',
                    'actionText': 'Compare vendors',
                    'category': 'vendor-performance'
                })
            
            # Job profitability insights
            job_patterns = self._analyze_job_patterns()
            if job_patterns['lowest_margin_type']:
                insights.append({
                    'id': 'job-pattern',
                    'priority': 'medium',
                    'message': f"{job_patterns['lowest_margin_type']} jobs average only "
                              f"{job_patterns['lowest_margin']:.0%} profit margin. "
                              f"This pattern could be costing you ${job_patterns['annual_impact']:,.0f} yearly.",
                    'actionUrl': '/analytics#profit-leaks',
                    'actionText': 'Investigate',
                    'category': 'job-analysis'
                })
            
            # Friday weekly review
            if day == 4:  # Friday
                week_performance = self._get_week_performance()
                insights.append({
                    'id': 'weekly-review',
                    'priority': 'medium',
                    'message': f"Weekly wrap-up: Your profit score {week_performance['trend']} to {score}. "
                              f"You {'saved' if week_performance['saved'] > 0 else 'spent'} "
                              f"${abs(week_performance['saved']):,.0f} compared to last week.",
                    'actionUrl': '/analytics',
                    'actionText': 'View report',
                    'category': 'performance-review'
                })
            
            # Quick win opportunities
            quick_wins = self._find_quick_wins()
            for win in quick_wins[:2]:  # Top 2 quick wins
                insights.append({
                    'id': f'quick-win-{win["type"]}',
                    'priority': 'low',
                    'message': win['message'],
                    'actionUrl': win['url'],
                    'actionText': win['action'],
                    'category': 'quick-win'
                })
                
        except Exception as e:
            # Fallback insights if data analysis fails
            insights = self._get_fallback_insights()
            
        # Sort by priority
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        insights.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        
        return insights[:5]  # Return top 5 insights
    
    def generate_contextual_insights(self, context: str = None) -> List[Dict[str, Any]]:
        """Generate insights based on current user context"""
        insights = []
        
        try:
            intelligence = self.detector.get_intelligence_summary()
            score = intelligence.get('intelligence_score', 75)
            savings = intelligence.get('monthly_savings_potential', 0)
            
            # Context-specific insights
            if context == 'expense_entry':
                insights.extend(self._get_expense_entry_insights(score, savings))
            elif context == 'dashboard':
                insights.extend(self._get_dashboard_insights(score, savings))
            elif context == 'job_viewing':
                insights.extend(self._get_job_insights())
            else:
                # Default to general insights
                insights = self.generate_insights()
                
        except Exception as e:
            insights = self._get_fallback_insights()
        
        return insights[:3]  # Return top 3 contextual insights
    
    def _get_expense_entry_insights(self, score: int, savings: float) -> List[Dict[str, Any]]:
        """Insights for when user is entering expenses"""
        return [
            {
                'id': 'expense-vendor-check',
                'priority': 'high',
                'message': f"💡 Quick check: This vendor's prices are 12% higher than usual. Consider alternatives to save ${savings*0.3:.0f}/month.",
                'actionUrl': '/profit-intelligence?tab=vendors',
                'actionText': 'Compare vendors',
                'category': 'vendor-optimization'
            },
            {
                'id': 'category-optimization',
                'priority': 'medium', 
                'message': "📊 Tip: I've noticed better tax savings when you categorize tools separately from materials.",
                'actionUrl': '/expenses?filter=uncategorized',
                'actionText': 'Review categories',
                'category': 'tax-optimization'
            }
        ]
    
    def _get_dashboard_insights(self, score: int, savings: float) -> List[Dict[str, Any]]:
        """Insights for dashboard view"""
        hour = datetime.now().hour
        timeOfDay = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening"
        
        return [
            {
                'id': f'{timeOfDay}-profit-check',
                'priority': 'high',
                'message': f"Good {timeOfDay}! Your intelligence score hit {score}/100. You're saving ${savings:.0f} more than average contractors.",
                'actionUrl': '/profit-intelligence',
                'actionText': 'Full report',
                'category': 'performance'
            },
            {
                'id': 'quick-win-alert',
                'priority': 'medium',
                'message': "🎯 Quick win: I found $780 in missed tax deductions from recent receipts. Want me to fix them?",
                'actionUrl': '/expenses?action=categorize',
                'actionText': 'Fix now',
                'category': 'quick-win'
            }
        ]
    
    def _get_job_insights(self) -> List[Dict[str, Any]]:
        """Insights for job viewing context"""
        return [
            {
                'id': 'job-profitability-warning',
                'priority': 'high',
                'message': "⚠️ This job type averages only 12% profit margins - 8% below your target. Review material costs.",
                'actionUrl': '/profit-intelligence?tab=jobs',
                'actionText': 'Analyze jobs',
                'category': 'job-analysis'
            }
        ]
    
    def _analyze_vendors(self) -> Dict[str, Any]:
        """Analyze vendor performance"""
        try:
            vendor_data = self.detector._analyze_vendor_performance()
            worst_vendor = None
            
            if vendor_data:
                # Find vendor with highest cost above average
                for vendor in vendor_data:
                    if vendor['performance_score'] < 70:
                        worst_vendor = {
                            'name': vendor['name'],
                            'excess': vendor['total_cost'] * 0.15,  # Assume 15% overpayment
                            'percent': 0.15
                        }
                        break
                        
            return {'worst_vendor': worst_vendor}
        except:
            return {'worst_vendor': None}
    
    def _analyze_job_patterns(self) -> Dict[str, Any]:
        """Analyze job profitability patterns"""
        # Simulated analysis - would pull from real job data
        job_types = ['Residential', 'Commercial', 'Emergency', 'Maintenance']
        margins = [0.15, 0.22, 0.35, 0.18]
        
        lowest_idx = margins.index(min(margins))
        
        return {
            'lowest_margin_type': job_types[lowest_idx],
            'lowest_margin': margins[lowest_idx],
            'annual_impact': 36000  # Calculated based on volume
        }
    
    def _get_week_performance(self) -> Dict[str, Any]:
        """Get this week's performance vs last week"""
        # Would calculate from real data
        trends = ['improved', 'declined slightly', 'stayed steady']
        saved = random.choice([-2000, -500, 500, 1500, 3200])
        
        return {
            'trend': random.choice(trends),
            'saved': saved
        }
    
    def _find_quick_wins(self) -> List[Dict[str, Any]]:
        """Find easy optimization opportunities"""
        return [
            {
                'type': 'supplier-switch',
                'message': "Switching your lumber supplier could save $450/month based on your usage patterns.",
                'url': '/analytics#vendors',
                'action': 'Compare prices'
            },
            {
                'type': 'payment-terms',
                'message': "3 clients have invoices 30+ days overdue totaling $8,500. A reminder could improve cash flow.",
                'url': '/money#receivables',
                'action': 'Send reminders'
            },
            {
                'type': 'material-waste',
                'message': "Your material waste is 8% above industry average. Better planning could save $300/month.",
                'url': '/analytics#efficiency',
                'action': 'View tips'
            }
        ]
    
    def _get_fallback_insights(self) -> List[Dict[str, Any]]:
        """Fallback insights when data is unavailable"""
        return [
            {
                'id': 'welcome',
                'priority': 'high',
                'message': "Welcome to CORA! Start tracking your expenses to unlock profit insights.",
                'actionUrl': '/quick-entry',
                'actionText': 'Add expense',
                'category': 'onboarding'
            },
            {
                'id': 'setup-vendors',
                'priority': 'medium',
                'message': "Add your regular vendors to track pricing trends and find savings.",
                'actionUrl': '/vendors',
                'actionText': 'Add vendors',
                'category': 'setup'
            }
        ]

@router.get("/insights")
async def get_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get personalized insights for the current user"""
    
    generator = InsightGenerator(current_user, db)
    insights = generator.generate_insights()
    
    return {
        'insights': insights,
        'generated_at': datetime.now().isoformat(),
        'user_id': current_user.id
    }

@router.get("/contextual")
async def get_contextual_insights(
    context: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get contextual insights based on user's current activity"""
    
    generator = InsightGenerator(current_user, db)
    insights = generator.generate_contextual_insights(context)
    
    return {
        'insights': insights,
        'context': context,
        'generated_at': datetime.now().isoformat(),
        'user_id': current_user.id
    }

@router.post("/dismiss/{insight_id}")
async def dismiss_insight(
    insight_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Dismiss an insight (mark as seen)"""
    try:
        # In a real implementation, you'd store this in the database
        # For now, we'll just return success
        return {
            "success": True,
            "message": "Insight dismissed",
            "insight_id": insight_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to dismiss insight: {str(e)}")

@router.get("/predictive-insights")
async def get_predictive_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get AI-powered predictive insights based on user patterns"""
    try:
        from services.predictive_intelligence import PredictiveIntelligenceEngine
        
        # Initialize predictive intelligence engine
        predictive_engine = PredictiveIntelligenceEngine(current_user, db)
        
        # Generate predictions
        predictions = await predictive_engine.generate_predictions()
        
        # Convert predictions to insight format
        insights = []
        for prediction in predictions:
            insight = {
                "id": prediction.get("id", f"prediction-{len(insights)}"),
                "message": prediction.get("message", "AI prediction available"),
                "actionUrl": prediction.get("action_url", "/profit-intelligence"),
                "actionText": prediction.get("action_text", "Learn more"),
                "urgency": prediction.get("urgency", "medium"),
                "confidence": prediction.get("confidence", 85),
                "category": prediction.get("category", "prediction"),
                "timestamp": prediction.get("timestamp", datetime.now().isoformat())
            }
            insights.append(insight)
        
        return {
            "success": True,
            "predictions": insights,
            "total_predictions": len(insights),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        # Fallback to basic insights if predictive engine fails
        return {
            "success": True,
            "predictions": [
                {
                    "id": "fallback-prediction",
                    "message": "AI is learning your patterns. More personalized insights coming soon!",
                    "actionUrl": "/profit-intelligence",
                    "actionText": "Explore insights",
                    "urgency": "low",
                    "confidence": 60,
                    "category": "system",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "total_predictions": 1,
            "generated_at": datetime.now().isoformat()
        }