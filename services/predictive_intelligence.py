"""
Predictive Intelligence Engine for CORA

This system learns from user patterns and proactively suggests actions,
transforming CORA from reactive to anticipatory intelligence.

Philosophy: True AI partnership means anticipating needs, not just responding to them.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from statistics import mean
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from models.expense import Expense
from models.job import Job
from models.user import User
from services.profit_leak_detector import ProfitLeakDetector


class PredictiveIntelligenceEngine:
    """
    Learns from user behavior patterns to provide proactive insights
    """
    
    def __init__(self, user: User, db: Session):
        self.user = user
        self.db = db
        self.detector = ProfitLeakDetector(user.id, db)
        self.patterns = {}
        
    async def generate_predictions(self) -> List[Dict[str, Any]]:
        """Generate proactive predictions based on learned patterns"""
        
        predictions = []
        
        # Learn user patterns first
        await self.analyze_user_patterns()
        
        # Generate different types of predictions
        predictions.extend(await self.predict_cash_flow_needs())
        predictions.extend(await self.predict_material_needs())
        predictions.extend(await self.predict_weather_impacts())
        predictions.extend(await self.predict_vendor_opportunities())
        predictions.extend(await self.predict_seasonal_trends())
        predictions.extend(await self.predict_client_behaviors())
        
        # Sort by urgency and confidence
        predictions = self.prioritize_predictions(predictions)
        
        return predictions[:5]  # Top 5 most important predictions
    
    async def analyze_user_patterns(self):
        """Analyze historical data to understand user patterns"""
        
        # Cash flow patterns
        self.patterns['cash_flow'] = await self.analyze_cash_flow_patterns()
        
        # Spending patterns
        self.patterns['spending'] = await self.analyze_spending_patterns()
        
        # Job scheduling patterns
        self.patterns['scheduling'] = await self.analyze_job_patterns()
        
        # Vendor usage patterns
        self.patterns['vendors'] = await self.analyze_vendor_patterns()
        
        # Seasonal patterns
        self.patterns['seasonal'] = await self.analyze_seasonal_patterns()
    
    async def analyze_cash_flow_patterns(self) -> Dict[str, Any]:
        """Analyze when user typically has cash flow challenges"""
        
        # Get expense patterns by day of month
        expenses_by_day = {}
        
        # Look at last 6 months of expenses
        six_months_ago = datetime.now() - timedelta(days=180)
        expenses = self.db.query(Expense).filter(
            Expense.user_id == self.user.id,
            Expense.created_at >= six_months_ago
        ).all()
        
        for expense in expenses:
            day_of_month = expense.created_at.day
            if day_of_month not in expenses_by_day:
                expenses_by_day[day_of_month] = []
            expenses_by_day[day_of_month].append(expense.amount)
        
        # Find patterns
        high_spend_days = []
        for day, amounts in expenses_by_day.items():
            if len(amounts) >= 3:  # Need enough data
                avg_amount = mean(amounts)
                if avg_amount > 1000:  # Significant spending day
                    high_spend_days.append({
                        'day': day,
                        'avg_amount': avg_amount,
                        'frequency': len(amounts)
                    })
        
        return {
            'high_spend_days': sorted(high_spend_days, key=lambda x: x['avg_amount'], reverse=True),
            'typical_monthly_spend': sum(sum(amounts) for amounts in expenses_by_day.values()) / len(set(exp.created_at.month for exp in expenses)) if expenses else 0
        }
    
    async def analyze_spending_patterns(self) -> Dict[str, Any]:
        """Analyze spending patterns by category and vendor"""
        
        # Get spending by category over time
        category_patterns = {}
        vendor_patterns = {}
        
        # Last 90 days for recent patterns
        ninety_days_ago = datetime.now() - timedelta(days=90)
        recent_expenses = self.db.query(Expense).filter(
            Expense.user_id == self.user.id,
            Expense.created_at >= ninety_days_ago
        ).all()
        
        for expense in recent_expenses:
            # Category patterns
            category = expense.category or 'Uncategorized'
            if category not in category_patterns:
                category_patterns[category] = []
            category_patterns[category].append({
                'amount': expense.amount,
                'date': expense.created_at,
                'vendor': expense.vendor
            })
            
            # Vendor patterns
            vendor = expense.vendor or 'Unknown'
            if vendor not in vendor_patterns:
                vendor_patterns[vendor] = []
            vendor_patterns[vendor].append({
                'amount': expense.amount,
                'date': expense.created_at,
                'category': expense.category
            })
        
        return {
            'category_patterns': category_patterns,
            'vendor_patterns': vendor_patterns
        }
    
    async def analyze_job_patterns(self) -> Dict[str, Any]:
        """Analyze job scheduling and completion patterns"""
        
        # Get recent jobs
        ninety_days_ago = datetime.now() - timedelta(days=90)
        recent_jobs = self.db.query(Job).filter(
            Job.user_id == self.user.id,
            Job.created_at >= ninety_days_ago
        ).all()
        
        patterns = {
            'avg_duration': 0,
            'completion_rate': 0,
            'busy_periods': [],
            'job_types': {}
        }
        
        if recent_jobs:
            # Calculate average duration for completed jobs
            completed_jobs = [j for j in recent_jobs if j.status == 'completed' and j.end_date]
            if completed_jobs:
                durations = []
                for job in completed_jobs:
                    if job.start_date and job.end_date:
                        duration = (job.end_date - job.start_date).days
                        durations.append(duration)
                
                if durations:
                    patterns['avg_duration'] = mean(durations)
            
            # Completion rate
            patterns['completion_rate'] = len(completed_jobs) / len(recent_jobs) * 100
            
            # Job type patterns
            for job in recent_jobs:
                job_type = job.job_type or 'General'
                if job_type not in patterns['job_types']:
                    patterns['job_types'][job_type] = {
                        'count': 0,
                        'avg_value': 0,
                        'completion_rate': 0
                    }
                patterns['job_types'][job_type]['count'] += 1
                if job.budget:
                    patterns['job_types'][job_type]['avg_value'] += job.budget
        
        return patterns
    
    async def analyze_vendor_patterns(self) -> Dict[str, Any]:
        """Analyze vendor usage and pricing patterns"""
        
        vendor_data = {}
        
        # Get vendor expenses from last 6 months
        six_months_ago = datetime.now() - timedelta(days=180)
        vendor_expenses = self.db.query(Expense).filter(
            Expense.user_id == self.user.id,
            Expense.created_at >= six_months_ago,
            Expense.vendor.isnot(None)
        ).all()
        
        for expense in vendor_expenses:
            vendor = expense.vendor
            if vendor not in vendor_data:
                vendor_data[vendor] = {
                    'transactions': [],
                    'categories': set(),
                    'total_spent': 0,
                    'frequency': 0
                }
            
            vendor_data[vendor]['transactions'].append({
                'amount': expense.amount,
                'date': expense.created_at,
                'category': expense.category
            })
            vendor_data[vendor]['categories'].add(expense.category)
            vendor_data[vendor]['total_spent'] += expense.amount
            vendor_data[vendor]['frequency'] += 1
        
        # Analyze patterns for each vendor
        for vendor, data in vendor_data.items():
            if len(data['transactions']) >= 3:
                amounts = [t['amount'] for t in data['transactions']]
                data['avg_amount'] = mean(amounts)
                data['price_volatility'] = max(amounts) - min(amounts) if amounts else 0
                
                # Calculate recent vs historical pricing
                recent_transactions = [t for t in data['transactions'] 
                                     if t['date'] >= datetime.now() - timedelta(days=30)]
                if recent_transactions and len(data['transactions']) > len(recent_transactions):
                    recent_avg = mean([t['amount'] for t in recent_transactions])
                    historical_avg = mean([t['amount'] for t in data['transactions'] 
                                         if t not in recent_transactions])
                    data['price_trend'] = (recent_avg - historical_avg) / historical_avg * 100
                else:
                    data['price_trend'] = 0
        
        return vendor_data
    
    async def analyze_seasonal_patterns(self) -> Dict[str, Any]:
        """Analyze seasonal spending and business patterns"""
        
        # This would ideally use multiple years of data
        # For now, analyze current year patterns
        current_year = datetime.now().year
        monthly_data = {}
        
        for month in range(1, 13):
            month_expenses = self.db.query(Expense).filter(
                Expense.user_id == self.user.id,
                func.extract('year', Expense.created_at) == current_year,
                func.extract('month', Expense.created_at) == month
            ).all()
            
            monthly_data[month] = {
                'total_spending': sum(e.amount for e in month_expenses),
                'transaction_count': len(month_expenses),
                'categories': {}
            }
            
            # Category breakdown by month
            for expense in month_expenses:
                category = expense.category or 'Uncategorized'
                if category not in monthly_data[month]['categories']:
                    monthly_data[month]['categories'][category] = 0
                monthly_data[month]['categories'][category] += expense.amount
        
        return monthly_data
    
    async def predict_cash_flow_needs(self) -> List[Dict[str, Any]]:
        """Predict upcoming cash flow challenges"""
        
        predictions = []
        
        if 'cash_flow' not in self.patterns:
            return predictions
        
        cash_flow_data = self.patterns['cash_flow']
        current_day = datetime.now().day
        
        # Check if we're approaching a historically high-spend period
        for high_spend_day in cash_flow_data['high_spend_days'][:3]:  # Top 3
            days_until = high_spend_day['day'] - current_day
            if days_until < 0:
                days_until += 30  # Next month
            
            if 1 <= days_until <= 7:  # Within a week
                predictions.append({
                    'id': f'cash_flow_alert_{high_spend_day["day"]}',
                    'type': 'cash_flow_prediction',
                    'urgency': 'high' if days_until <= 3 else 'medium',
                    'confidence': min(95, 60 + high_spend_day['frequency'] * 5),
                    'days_ahead': days_until,
                    'message': f"💰 Cash flow heads up: You typically spend ${high_spend_day['avg_amount']:,.0f} around the {high_spend_day['day']}th. That's in {days_until} days - consider preparing.",
                    'predicted_amount': high_spend_day['avg_amount'],
                    'action': {
                        'type': 'prepare_cash_flow',
                        'suggestions': [
                            'Review current cash position',
                            'Send invoice reminders to clients',
                            'Consider delaying non-essential purchases'
                        ]
                    }
                })
        
        return predictions
    
    async def predict_material_needs(self) -> List[Dict[str, Any]]:
        """Predict when user will need to restock materials"""
        
        predictions = []
        
        if 'spending' not in self.patterns:
            return predictions
        
        spending_patterns = self.patterns['spending']
        
        # Look for regular material purchases
        material_categories = ['Materials', 'Lumber', 'Hardware', 'Electrical', 'Plumbing']
        
        for category in material_categories:
            if category in spending_patterns['category_patterns']:
                expenses = spending_patterns['category_patterns'][category]
                
                if len(expenses) >= 3:
                    # Calculate average time between purchases
                    dates = sorted([e['date'] for e in expenses])
                    intervals = []
                    for i in range(1, len(dates)):
                        interval = (dates[i] - dates[i-1]).days
                        intervals.append(interval)
                    
                    if intervals:
                        avg_interval = mean(intervals)
                        last_purchase = max(dates)
                        days_since = (datetime.now() - last_purchase).days
                        
                        # If we're close to the typical reorder time
                        if days_since >= avg_interval * 0.8:
                            predictions.append({
                                'id': f'material_restock_{category.lower()}',
                                'type': 'material_prediction',
                                'urgency': 'medium' if days_since >= avg_interval else 'low',
                                'confidence': min(90, 50 + len(intervals) * 8),
                                'days_ahead': max(0, int(avg_interval - days_since)),
                                'message': f"🔧 {category} restock: Based on your pattern, you typically reorder every {avg_interval:.0f} days. It's been {days_since} days since your last purchase.",
                                'category': category,
                                'action': {
                                    'type': 'plan_purchase',
                                    'suggestions': [
                                        f'Review current {category.lower()} inventory',
                                        'Check with preferred vendors for pricing',
                                        'Consider bulk purchases for better rates'
                                    ]
                                }
                            })
        
        return predictions
    
    async def predict_weather_impacts(self) -> List[Dict[str, Any]]:
        """Predict weather-related business impacts"""
        
        predictions = []
        
        try:
            # Get weather forecast (would need API key in production)
            # For now, simulate weather predictions
            weather_data = await self.get_weather_forecast()
            
            if weather_data:
                for day_forecast in weather_data['daily'][:5]:  # Next 5 days
                    if day_forecast['rain_probability'] > 70:
                        days_ahead = day_forecast['days_from_now']
                        predictions.append({
                            'id': f'weather_rain_{days_ahead}',
                            'type': 'weather_prediction',
                            'urgency': 'medium' if days_ahead <= 2 else 'low',
                            'confidence': 85,
                            'days_ahead': days_ahead,
                            'message': f"🌧️ Weather alert: {day_forecast['rain_probability']}% chance of rain {self.format_day_ahead(days_ahead)}. Consider adjusting outdoor work schedules.",
                            'weather_type': 'rain',
                            'action': {
                                'type': 'schedule_adjustment',
                                'suggestions': [
                                    'Move outdoor work to earlier in week',
                                    'Notify clients of potential delays',
                                    'Prepare indoor alternatives'
                                ]
                            }
                        })
                    
                    if day_forecast['temperature_extreme']:
                        days_ahead = day_forecast['days_from_now']
                        predictions.append({
                            'id': f'weather_temp_{days_ahead}',
                            'type': 'weather_prediction',
                            'urgency': 'low',
                            'confidence': 80,
                            'days_ahead': days_ahead,
                            'message': f"🌡️ Temperature alert: Extreme {day_forecast['temp_type']} ({day_forecast['temp']}°F) {self.format_day_ahead(days_ahead)}. Plan accordingly for worker safety.",
                            'weather_type': 'temperature',
                            'action': {
                                'type': 'safety_preparation',
                                'suggestions': [
                                    'Ensure adequate hydration/warming supplies',
                                    'Adjust work hours to avoid extremes',
                                    'Brief team on weather safety protocols'
                                ]
                            }
                        })
        
        except Exception as e:
            # Weather API unavailable, skip weather predictions
            pass
        
        return predictions
    
    async def predict_vendor_opportunities(self) -> List[Dict[str, Any]]:
        """Predict vendor pricing opportunities and issues"""
        
        predictions = []
        
        if 'vendors' not in self.patterns:
            return predictions
        
        vendor_patterns = self.patterns['vendors']
        
        for vendor, data in vendor_patterns.items():
            if data['frequency'] >= 3:  # Regular vendor
                
                # Predict price increases
                if data.get('price_trend', 0) > 15:  # 15% increase trend
                    predictions.append({
                        'id': f'vendor_price_increase_{vendor.lower().replace(" ", "_")}',
                        'type': 'vendor_prediction',
                        'urgency': 'high',
                        'confidence': min(90, 70 + data['frequency'] * 2),
                        'days_ahead': 0,  # Happening now
                        'message': f"📈 Vendor alert: {vendor} prices are trending up {data['price_trend']:.1f}%. Consider stocking up or finding alternatives before further increases.",
                        'vendor': vendor,
                        'price_trend': data['price_trend'],
                        'action': {
                            'type': 'vendor_optimization',
                            'suggestions': [
                                f'Stock up on essentials from {vendor}',
                                'Research alternative suppliers',
                                'Negotiate volume discounts'
                            ]
                        }
                    })
                
                # Predict reorder timing based on frequency
                if data['frequency'] >= 5:  # Very regular vendor
                    avg_days_between = 90 / data['frequency']  # Rough estimate
                    last_transaction = max(data['transactions'], key=lambda x: x['date'])
                    days_since = (datetime.now() - last_transaction['date']).days
                    
                    if days_since >= avg_days_between * 0.9:
                        predictions.append({
                            'id': f'vendor_reorder_{vendor.lower().replace(" ", "_")}',
                            'type': 'vendor_prediction',
                            'urgency': 'medium',
                            'confidence': min(85, 60 + data['frequency'] * 3),
                            'days_ahead': max(0, int(avg_days_between - days_since)),
                            'message': f"🔄 Reorder reminder: You typically purchase from {vendor} every {avg_days_between:.0f} days. It's been {days_since} days since your last order.",
                            'vendor': vendor,
                            'action': {
                                'type': 'plan_purchase',
                                'suggestions': [
                                    f'Check current inventory for {vendor} items',
                                    'Review pricing and availability',
                                    'Consider combining orders for efficiency'
                                ]
                            }
                        })
        
        return predictions
    
    async def predict_seasonal_trends(self) -> List[Dict[str, Any]]:
        """Predict seasonal business trends and opportunities"""
        
        predictions = []
        
        current_month = datetime.now().month
        current_day = datetime.now().day
        
        # Construction industry seasonal patterns
        seasonal_insights = {
            # Spring preparation (March)
            3: {
                'message': "🌱 Spring prep: Material demand typically increases 20% in April. Consider ordering lumber and outdoor materials early.",
                'urgency': 'medium',
                'type': 'seasonal_opportunity'
            },
            # Summer peak season (June)
            6: {
                'message': "☀️ Peak season: Construction activity peaks in July-August. Book projects now and prepare for material price increases.",
                'urgency': 'high', 
                'type': 'seasonal_opportunity'
            },
            # Fall preparation (September)
            9: {
                'message': "🍂 Winter prep: Indoor project demand increases in October. Pivot marketing toward interior work.",
                'urgency': 'medium',
                'type': 'seasonal_opportunity'
            },
            # Winter planning (November)
            11: {
                'message': "❄️ Winter planning: Heating costs rise 30%. Factor increased overhead into December-February bids.",
                'urgency': 'medium',
                'type': 'seasonal_planning'
            }
        }
        
        if current_month in seasonal_insights:
            insight = seasonal_insights[current_month]
            predictions.append({
                'id': f'seasonal_trend_{current_month}',
                'type': 'seasonal_prediction',
                'urgency': insight['urgency'],
                'confidence': 75,
                'days_ahead': 7,  # Week ahead planning
                'message': insight['message'],
                'action': {
                    'type': insight['type'],
                    'suggestions': [
                        'Review historical seasonal patterns',
                        'Adjust marketing and pricing strategies',
                        'Plan material procurement timing'
                    ]
                }
            })
        
        return predictions
    
    async def predict_client_behaviors(self) -> List[Dict[str, Any]]:
        """Predict client payment patterns and behavior"""
        
        predictions = []
        
        # This would analyze invoice and payment data
        # For now, provide general client behavior predictions
        
        current_day = datetime.now().day
        
        # Month-end payment rush prediction
        if 25 <= current_day <= 28:
            predictions.append({
                'id': 'client_payment_rush',
                'type': 'client_prediction',
                'urgency': 'medium',
                'confidence': 80,
                'days_ahead': 30 - current_day,
                'message': f"💸 Payment pattern: Many clients pay invoices during month-end (in {30-current_day} days). Send reminders now for faster payment.",
                'action': {
                    'type': 'payment_optimization',
                    'suggestions': [
                        'Send friendly payment reminders',
                        'Offer early payment discounts',
                        'Follow up on overdue invoices'
                    ]
                }
            })
        
        return predictions
    
    async def get_weather_forecast(self) -> Optional[Dict[str, Any]]:
        """Get weather forecast data (mock for now)"""
        
        # Mock weather data - in production, would call actual weather API
        return {
            'daily': [
                {
                    'days_from_now': 1,
                    'rain_probability': 85,
                    'temperature_extreme': False,
                    'temp': 72,
                    'temp_type': 'normal'
                },
                {
                    'days_from_now': 2,
                    'rain_probability': 15,
                    'temperature_extreme': True,
                    'temp': 95,
                    'temp_type': 'hot'
                },
                {
                    'days_from_now': 3,
                    'rain_probability': 30,
                    'temperature_extreme': False,
                    'temp': 78,
                    'temp_type': 'normal'
                }
            ]
        }
    
    def format_day_ahead(self, days: int) -> str:
        """Format days ahead into human readable text"""
        if days == 0:
            return "today"
        elif days == 1:
            return "tomorrow"
        elif days <= 7:
            return f"in {days} days"
        else:
            return f"in {days} days"
    
    def prioritize_predictions(self, predictions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort predictions by urgency, confidence, and timing"""
        
        urgency_weights = {'high': 3, 'medium': 2, 'low': 1}
        
        def score_prediction(pred):
            urgency_score = urgency_weights.get(pred['urgency'], 1)
            confidence_score = pred['confidence'] / 100
            timing_score = max(0, 1 - (pred['days_ahead'] / 30))  # More urgent if sooner
            
            return urgency_score + confidence_score + timing_score
        
        return sorted(predictions, key=score_prediction, reverse=True)