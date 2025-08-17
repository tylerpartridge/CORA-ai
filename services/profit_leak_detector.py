#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/services/profit_leak_detector.py
🎯 PURPOSE: CORA's core profit leak detection engine - identifies cost-saving opportunities
🔗 IMPORTS: SQLAlchemy, datetime, statistics
📤 EXPORTS: ProfitLeakDetector class
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import statistics
from models.expense import Expense
from models.business_profile import BusinessProfile
from models.user import User

class ProfitLeakDetector:
    """
    CORA's Profit Leak Detection Engine
    
    Identifies cost-saving opportunities for contractors by analyzing:
    - Expense patterns and anomalies
    - Vendor price comparisons
    - Category spending optimization
    - Seasonal cost variations
    - Job profitability analysis
    """
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.user = db.query(User).filter(User.id == user_id).first()
        self.business_profile = db.query(BusinessProfile).filter(
            BusinessProfile.user_email == self.user.email
        ).first()
    
    def analyze_profit_leaks(self, months_back: int = 6) -> Dict[str, Any]:
        """
        Comprehensive profit leak analysis
        
        Returns:
        - Quick wins (immediate savings)
        - Category optimization opportunities
        - Vendor price anomalies
        - Seasonal cost patterns
        - Job profitability insights
        """
        start_date = datetime.now() - timedelta(days=months_back * 30)
        
        # Get user's expenses
        expenses = self.db.query(Expense).filter(
            and_(
                Expense.user_id == self.user_id,
                Expense.expense_date >= start_date
            )
        ).all()
        
        if not expenses:
            return self._empty_analysis()
        
        analysis = {
            "summary": self._generate_summary(expenses),
            "quick_wins": self._identify_quick_wins(expenses),
            "category_optimization": self._analyze_category_spending(expenses),
            "vendor_anomalies": self._detect_vendor_anomalies(expenses),
            "seasonal_patterns": self._analyze_seasonal_patterns(expenses),
            "job_profitability": self._analyze_job_profitability(expenses),
            "recommendations": [],
            "potential_savings": 0.0
        }
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)
        analysis["potential_savings"] = self._calculate_potential_savings(analysis)
        
        return analysis
    
    def _generate_summary(self, expenses: List[Expense]) -> Dict[str, Any]:
        """Generate expense summary and key metrics"""
        total_spent = sum(exp.amount for exp in expenses)
        avg_monthly = total_spent / 6  # Assuming 6 months
        
        # Top spending categories
        category_totals = {}
        for exp in expenses:
            category = exp.category.name if exp.category else "Uncategorized"
            category_totals[category] = category_totals.get(category, 0) + exp.amount
        
        top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_spent": total_spent,
            "avg_monthly_spending": avg_monthly,
            "expense_count": len(expenses),
            "top_spending_categories": top_categories,
            "business_type": self.business_profile.business_type if self.business_profile else "Unknown",
            "analysis_period": "6 months"
        }
    
    def _identify_quick_wins(self, expenses: List[Expense]) -> List[Dict[str, Any]]:
        """Identify immediate cost-saving opportunities"""
        quick_wins = []
        
        # 1. Duplicate or similar expenses
        vendor_expenses = {}
        for exp in expenses:
            vendor = exp.vendor.lower() if exp.vendor else "unknown"
            if vendor not in vendor_expenses:
                vendor_expenses[vendor] = []
            vendor_expenses[vendor].append(exp)
        
        # Find potential duplicates
        for vendor, vendor_exps in vendor_expenses.items():
            if len(vendor_exps) > 1:
                # Check for same-day similar amounts
                for i, exp1 in enumerate(vendor_exps):
                    for exp2 in vendor_exps[i+1:]:
                        if (exp1.expense_date.date() == exp2.expense_date.date() and
                            abs(exp1.amount - exp2.amount) < 5.0):  # Within $5
                            quick_wins.append({
                                "type": "potential_duplicate",
                                "title": f"Potential duplicate expense at {exp1.vendor}",
                                "description": f"Two expenses of ${exp1.amount:.2f} and ${exp2.amount:.2f} on {exp1.expense_date.strftime('%Y-%m-%d')}",
                                "potential_savings": min(exp1.amount, exp2.amount),
                                "confidence": "high",
                                "action": "Review and verify if duplicate"
                            })
        
        # 2. High-frequency small expenses (could be consolidated)
        small_expenses = [exp for exp in expenses if exp.amount < 50]
        if len(small_expenses) > 10:
            total_small = sum(exp.amount for exp in small_expenses)
            quick_wins.append({
                "type": "consolidation_opportunity",
                "title": "Consolidate small frequent expenses",
                "description": f"{len(small_expenses)} expenses under $50 totaling ${total_small:.2f}",
                "potential_savings": total_small * 0.15,  # 15% savings through consolidation
                "confidence": "medium",
                "action": "Consider bulk purchasing or vendor consolidation"
            })
        
        # 3. Unusual spending spikes
        monthly_totals = {}
        for exp in expenses:
            month_key = exp.expense_date.strftime('%Y-%m')
            monthly_totals[month_key] = monthly_totals.get(month_key, 0) + exp.amount
        
        if len(monthly_totals) > 2:
            avg_monthly = statistics.mean(monthly_totals.values())
            for month, total in monthly_totals.items():
                if total > avg_monthly * 1.5:  # 50% above average
                    quick_wins.append({
                        "type": "spending_spike",
                        "title": f"Unusual spending spike in {month}",
                        "description": f"Spent ${total:.2f} vs average of ${avg_monthly:.2f}",
                        "potential_savings": (total - avg_monthly) * 0.2,  # 20% of excess
                        "confidence": "medium",
                        "action": "Review what caused the spike and if it's recurring"
                    })
        
        return quick_wins
    
    def _analyze_category_spending(self, expenses: List[Expense]) -> Dict[str, Any]:
        """Analyze spending by category for optimization opportunities"""
        category_analysis = {}
        
        # Group by category
        for exp in expenses:
            category = exp.category.name if exp.category else "Uncategorized"
            if category not in category_analysis:
                category_analysis[category] = {
                    "total": 0,
                    "count": 0,
                    "avg_amount": 0,
                    "vendors": set(),
                    "months": set()
                }
            
            cat_data = category_analysis[category]
            cat_data["total"] += exp.amount
            cat_data["count"] += 1
            cat_data["vendors"].add(exp.vendor)
            cat_data["months"].add(exp.expense_date.strftime('%Y-%m'))
        
        # Calculate averages and identify opportunities
        opportunities = []
        for category, data in category_analysis.items():
            data["avg_amount"] = data["total"] / data["count"]
            data["vendor_count"] = len(data["vendors"])
            data["monthly_avg"] = data["total"] / len(data["months"])
            
            # Identify optimization opportunities
            if data["vendor_count"] > 3:
                opportunities.append({
                    "category": category,
                    "type": "vendor_consolidation",
                    "description": f"Using {data['vendor_count']} different vendors",
                    "potential_savings": data["total"] * 0.1,  # 10% through consolidation
                    "action": "Consider consolidating vendors for better pricing"
                })
            
            if data["avg_amount"] > 500:  # High-value category
                opportunities.append({
                    "category": category,
                    "type": "high_value_optimization",
                    "description": f"Average expense: ${data['avg_amount']:.2f}",
                    "potential_savings": data["total"] * 0.15,  # 15% savings potential
                    "action": "Negotiate better rates or seek competitive bids"
                })
        
        return {
            "category_breakdown": category_analysis,
            "optimization_opportunities": opportunities
        }
    
    def _detect_vendor_anomalies(self, expenses: List[Expense]) -> List[Dict[str, Any]]:
        """Detect unusual vendor pricing or patterns"""
        vendor_analysis = {}
        anomalies = []
        
        # Group by vendor
        for exp in expenses:
            vendor = exp.vendor
            if not vendor:
                continue
                
            if vendor not in vendor_analysis:
                vendor_analysis[vendor] = []
            vendor_analysis[vendor].append(exp)
        
        # Analyze each vendor
        for vendor, vendor_exps in vendor_analysis.items():
            if len(vendor_exps) < 3:
                continue  # Need multiple transactions for analysis
            
            amounts = [exp.amount for exp in vendor_exps]
            avg_amount = statistics.mean(amounts)
            std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
            
            # Find outliers
            for exp in vendor_exps:
                if std_dev > 0 and abs(exp.amount - avg_amount) > 2 * std_dev:
                    anomalies.append({
                        "vendor": vendor,
                        "expense_id": exp.id,
                        "amount": exp.amount,
                        "avg_amount": avg_amount,
                        "deviation": abs(exp.amount - avg_amount),
                        "date": exp.expense_date,
                        "type": "pricing_anomaly",
                        "description": f"Unusual amount ${exp.amount:.2f} vs average ${avg_amount:.2f}",
                        "action": "Verify pricing and consider negotiating"
                    })
        
        return anomalies
    
    def _analyze_seasonal_patterns(self, expenses: List[Expense]) -> Dict[str, Any]:
        """Analyze seasonal cost patterns"""
        monthly_totals = {}
        monthly_counts = {}
        
        for exp in expenses:
            month_key = exp.expense_date.strftime('%Y-%m')
            monthly_totals[month_key] = monthly_totals.get(month_key, 0) + exp.amount
            monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
        
        # Calculate seasonal trends
        if len(monthly_totals) >= 3:
            months = sorted(monthly_totals.keys())
            totals = [monthly_totals[month] for month in months]
            
            # Find peak and low months
            max_month = months[totals.index(max(totals))]
            min_month = months[totals.index(min(totals))]
            
            return {
                "monthly_totals": monthly_totals,
                "monthly_counts": monthly_counts,
                "peak_month": max_month,
                "low_month": min_month,
                "seasonal_variation": (max(totals) - min(totals)) / max(totals) * 100,
                "insights": [
                    f"Peak spending in {max_month}: ${max(totals):.2f}",
                    f"Lowest spending in {min_month}: ${min(totals):.2f}",
                    f"Seasonal variation: {((max(totals) - min(totals)) / max(totals) * 100):.1f}%"
                ]
            }
        
        return {"monthly_totals": monthly_totals, "insights": ["Insufficient data for seasonal analysis"]}
    
    def _analyze_job_profitability(self, expenses: List[Expense]) -> Dict[str, Any]:
        """Analyze job-specific profitability"""
        job_expenses = {}
        
        for exp in expenses:
            if exp.job_name:
                if exp.job_name not in job_expenses:
                    job_expenses[exp.job_name] = []
                job_expenses[exp.job_name].append(exp)
        
        job_analysis = {}
        for job_name, job_exps in job_expenses.items():
            total_cost = sum(exp.amount for exp in job_exps)
            avg_cost = total_cost / len(job_exps)
            
            job_analysis[job_name] = {
                "total_cost": total_cost,
                "expense_count": len(job_exps),
                "avg_cost": avg_cost,
                "categories": list(set(exp.category.name if exp.category else "Uncategorized" for exp in job_exps))
            }
        
        return {
            "jobs_analyzed": len(job_analysis),
            "job_breakdown": job_analysis,
            "insights": [
                f"Tracked expenses for {len(job_analysis)} jobs",
                "Consider tracking job revenue to calculate profitability"
            ]
        }
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Quick wins recommendations
        if analysis["quick_wins"]:
            recommendations.append({
                "priority": "high",
                "category": "immediate_savings",
                "title": "Address Quick Wins",
                "description": f"Found {len(analysis['quick_wins'])} immediate cost-saving opportunities",
                "potential_impact": sum(win["potential_savings"] for win in analysis["quick_wins"]),
                "actions": [win["action"] for win in analysis["quick_wins"][:3]]
            })
        
        # Category optimization
        if analysis["category_optimization"]["optimization_opportunities"]:
            recommendations.append({
                "priority": "medium",
                "category": "vendor_optimization",
                "title": "Optimize Vendor Relationships",
                "description": "Consolidate vendors and negotiate better rates",
                "potential_impact": sum(opp["potential_savings"] for opp in analysis["category_optimization"]["optimization_opportunities"]),
                "actions": ["Review vendor contracts", "Request competitive bids", "Negotiate volume discounts"]
            })
        
        # Seasonal planning
        if analysis["seasonal_patterns"].get("seasonal_variation", 0) > 20:
            recommendations.append({
                "priority": "medium",
                "category": "seasonal_planning",
                "title": "Plan for Seasonal Variations",
                "description": f"Spending varies by {analysis['seasonal_patterns']['seasonal_variation']:.1f}% seasonally",
                "potential_impact": analysis["summary"]["avg_monthly_spending"] * 0.1,
                "actions": ["Plan purchases during low-cost months", "Negotiate fixed pricing", "Build seasonal budgets"]
            })
        
        return recommendations
    
    def _calculate_potential_savings(self, analysis: Dict[str, Any]) -> float:
        """Calculate total potential savings from all recommendations"""
        total_savings = 0.0
        
        # Quick wins savings
        total_savings += sum(win["potential_savings"] for win in analysis["quick_wins"])
        
        # Category optimization savings
        total_savings += sum(opp["potential_savings"] for opp in analysis["category_optimization"]["optimization_opportunities"])
        
        # Vendor anomalies (conservative estimate)
        total_savings += len(analysis["vendor_anomalies"]) * 50  # $50 per anomaly
        
        return total_savings
    
    def predict_future_costs(self, forecast_months: int = 3) -> Dict[str, Any]:
        """
        Advanced predictive cost modeling using time series analysis
        Leverages pattern recognition to forecast future expenses
        """
        # Get historical data for trend analysis
        start_date = datetime.now() - timedelta(days=365)  # 1 year history
        expenses = self.db.query(Expense).filter(
            and_(
                Expense.user_id == self.user_id,
                Expense.expense_date >= start_date
            )
        ).order_by(Expense.expense_date).all()
        
        if len(expenses) < 10:
            return {"error": "Insufficient data for forecasting", "min_required": 10, "available": len(expenses)}
        
        # Monthly aggregation with trend analysis
        monthly_data = {}
        for exp in expenses:
            month_key = exp.expense_date.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {"total": 0, "count": 0, "categories": {}}
            
            monthly_data[month_key]["total"] += exp.amount
            monthly_data[month_key]["count"] += 1
            
            category = exp.category.name if exp.category else "Uncategorized"
            monthly_data[month_key]["categories"][category] = monthly_data[month_key]["categories"].get(category, 0) + exp.amount
        
        # Advanced trend analysis using linear regression concepts
        months = sorted(monthly_data.keys())
        if len(months) < 3:
            return {"error": "Need at least 3 months of data", "available_months": len(months)}
        
        totals = [monthly_data[month]["total"] for month in months]
        
        # Calculate trend (simplified linear regression)
        n = len(totals)
        x_values = list(range(n))
        sum_x = sum(x_values)
        sum_y = sum(totals)
        sum_xy = sum(x * y for x, y in zip(x_values, totals))
        sum_x2 = sum(x * x for x in x_values)
        
        # Linear trend coefficients
        if n * sum_x2 - sum_x * sum_x != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
        else:
            slope = 0
            intercept = sum_y / n
        
        # Generate forecasts
        forecasts = []
        base_month = len(months)
        for i in range(forecast_months):
            predicted_total = intercept + slope * (base_month + i)
            # Add confidence intervals based on historical variance
            variance = statistics.variance(totals) if len(totals) > 1 else 0
            confidence_range = variance ** 0.5 * 1.96  # 95% confidence
            
            forecasts.append({
                "month_offset": i + 1,
                "predicted_total": max(0, predicted_total),  # Ensure non-negative
                "confidence_low": max(0, predicted_total - confidence_range),
                "confidence_high": predicted_total + confidence_range,
                "trend": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
            })
        
        # Category-specific forecasting
        category_forecasts = {}
        for category in set().union(*[data["categories"].keys() for data in monthly_data.values()]):
            cat_totals = []
            for month in months:
                cat_totals.append(monthly_data[month]["categories"].get(category, 0))
            
            if sum(cat_totals) > 0:  # Only forecast categories with spending
                cat_avg = statistics.mean(cat_totals)
                cat_trend = (cat_totals[-1] - cat_totals[0]) / len(cat_totals) if len(cat_totals) > 1 else 0
                
                category_forecasts[category] = {
                    "avg_monthly": cat_avg,
                    "trend_direction": "up" if cat_trend > 0 else "down" if cat_trend < 0 else "stable",
                    "predicted_next_month": max(0, cat_avg + cat_trend)
                }
        
        return {
            "forecast_period": f"{forecast_months} months",
            "historical_months": len(months),
            "overall_trend": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
            "trend_magnitude": abs(slope),
            "monthly_forecasts": forecasts,
            "category_forecasts": category_forecasts,
            "insights": self._generate_forecast_insights(slope, forecasts, category_forecasts),
            "confidence": "high" if len(months) >= 6 else "medium" if len(months) >= 3 else "low"
        }
    
    def intelligent_expense_categorization(self, description: str, vendor: str = "", amount: float = 0) -> Dict[str, Any]:
        """
        AI-powered expense categorization using pattern recognition
        Analyzes description, vendor, and amount patterns from historical data
        """
        # Get user's historical expenses for pattern learning
        expenses = self.db.query(Expense).filter(Expense.user_id == self.user_id).all()
        
        if not expenses:
            return self._default_categorization(description, vendor, amount)
        
        # Build pattern recognition database
        patterns = {}
        vendor_patterns = {}
        amount_patterns = {}
        
        for exp in expenses:
            if exp.category:
                category = exp.category.name
                
                # Description patterns
                if exp.description:
                    words = exp.description.lower().split()
                    for word in words:
                        if len(word) > 2:  # Skip short words
                            if category not in patterns:
                                patterns[category] = {}
                            patterns[category][word] = patterns[category].get(word, 0) + 1
                
                # Vendor patterns
                if exp.vendor:
                    vendor_key = exp.vendor.lower()
                    if category not in vendor_patterns:
                        vendor_patterns[category] = {}
                    vendor_patterns[category][vendor_key] = vendor_patterns[category].get(vendor_key, 0) + 1
                
                # Amount range patterns
                amount_range = self._get_amount_range(exp.amount)
                if category not in amount_patterns:
                    amount_patterns[category] = {}
                amount_patterns[category][amount_range] = amount_patterns[category].get(amount_range, 0) + 1
        
        # Score potential categories
        category_scores = {}
        
        # Score based on description
        desc_words = description.lower().split()
        for category, words in patterns.items():
            score = 0
            for word in desc_words:
                if word in words:
                    score += words[word]
            if score > 0:
                category_scores[category] = category_scores.get(category, 0) + score
        
        # Score based on vendor
        if vendor:
            vendor_key = vendor.lower()
            for category, vendors in vendor_patterns.items():
                if vendor_key in vendors:
                    category_scores[category] = category_scores.get(category, 0) + vendors[vendor_key] * 2  # Vendor is strong signal
        
        # Score based on amount range
        amount_range = self._get_amount_range(amount)
        for category, ranges in amount_patterns.items():
            if amount_range in ranges:
                category_scores[category] = category_scores.get(category, 0) + ranges[amount_range]
        
        # Get top suggestions
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_categories:
            top_category = sorted_categories[0]
            confidence = min(top_category[1] / max(sum(category_scores.values()), 1) * 100, 95)  # Cap at 95%
            
            return {
                "suggested_category": top_category[0],
                "confidence": confidence,
                "alternatives": [cat for cat, score in sorted_categories[1:3]],  # Top 2 alternatives
                "reasoning": self._explain_categorization(top_category[0], description, vendor, amount),
                "pattern_strength": "strong" if confidence > 70 else "medium" if confidence > 40 else "weak"
            }
        
        return self._default_categorization(description, vendor, amount)
    
    def _get_amount_range(self, amount: float) -> str:
        """Categorize amounts into ranges for pattern recognition"""
        if amount < 50:
            return "small"
        elif amount < 200:
            return "medium"
        elif amount < 1000:
            return "large"
        else:
            return "very_large"
    
    def _explain_categorization(self, category: str, description: str, vendor: str, amount: float) -> str:
        """Generate human-readable explanation for categorization choice"""
        reasons = []
        
        if vendor:
            reasons.append(f"vendor '{vendor}' frequently used for {category}")
        
        if any(word in description.lower() for word in ["material", "lumber", "concrete"]):
            reasons.append("description contains material-related keywords")
        elif any(word in description.lower() for word in ["fuel", "gas", "diesel"]):
            reasons.append("description contains fuel-related keywords")
        elif any(word in description.lower() for word in ["tool", "equipment", "rental"]):
            reasons.append("description contains equipment-related keywords")
        
        amount_range = self._get_amount_range(amount)
        if amount_range in ["large", "very_large"]:
            reasons.append(f"amount (${amount:.2f}) typical for {category} expenses")
        
        return f"Categorized as {category} because: " + ", ".join(reasons) if reasons else f"Best match based on historical patterns"
    
    def _default_categorization(self, description: str, vendor: str, amount: float) -> Dict[str, Any]:
        """Provide default categorization when no patterns available"""
        # Simple keyword-based fallback
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ["lumber", "wood", "concrete", "steel", "material"]):
            return {"suggested_category": "Materials", "confidence": 60, "reasoning": "Contains material keywords"}
        elif any(word in desc_lower for word in ["fuel", "gas", "diesel"]):
            return {"suggested_category": "Fuel", "confidence": 70, "reasoning": "Contains fuel keywords"}
        elif any(word in desc_lower for word in ["tool", "equipment", "rental"]):
            return {"suggested_category": "Equipment", "confidence": 65, "reasoning": "Contains equipment keywords"}
        else:
            return {"suggested_category": "General", "confidence": 30, "reasoning": "No clear pattern detected"}
    
    def _generate_forecast_insights(self, slope: float, forecasts: List[Dict], category_forecasts: Dict) -> List[str]:
        """Generate actionable insights from forecast analysis"""
        insights = []
        
        # Overall trend insights
        if slope > 50:
            insights.append(f"Costs are increasing rapidly (${slope:.0f}/month trend) - consider cost control measures")
        elif slope > 20:
            insights.append(f"Costs are gradually increasing (${slope:.0f}/month) - monitor and plan accordingly")
        elif slope < -20:
            insights.append(f"Costs are decreasing (${abs(slope):.0f}/month saved) - identify what's working well")
        else:
            insights.append("Costs are relatively stable - good cost management")
        
        # Category-specific insights
        growing_categories = [cat for cat, data in category_forecasts.items() if data["trend_direction"] == "up"]
        if growing_categories:
            insights.append(f"Growing expense categories: {', '.join(growing_categories[:3])} - focus optimization here")
        
        # Seasonal planning
        if len(forecasts) >= 3:
            max_month = max(forecasts, key=lambda x: x["predicted_total"])
            insights.append(f"Peak spending expected in month {max_month['month_offset']} - plan cash flow accordingly")
        
        return insights
    
    def analyze_vendor_performance(self) -> Dict[str, Any]:
        """
        Advanced vendor performance scoring using multiple metrics
        Evaluates vendors on cost efficiency, reliability, and value
        """
        # Get all user expenses for comprehensive vendor analysis
        expenses = self.db.query(Expense).filter(Expense.user_id == self.user_id).all()
        
        if not expenses:
            return {"error": "No expense data available for vendor analysis"}
        
        vendor_metrics = {}
        
        # Group expenses by vendor
        for exp in expenses:
            vendor = exp.vendor
            if not vendor or vendor.lower() in ['unknown', 'n/a', '']:
                continue
            
            if vendor not in vendor_metrics:
                vendor_metrics[vendor] = {
                    "total_spent": 0,
                    "transaction_count": 0,
                    "amounts": [],
                    "categories": set(),
                    "dates": [],
                    "avg_amount": 0,
                    "consistency_score": 0,
                    "value_score": 0,
                    "reliability_score": 0,
                    "overall_score": 0
                }
            
            metrics = vendor_metrics[vendor]
            metrics["total_spent"] += exp.amount
            metrics["transaction_count"] += 1
            metrics["amounts"].append(exp.amount)
            metrics["categories"].add(exp.category.name if exp.category else "Uncategorized")
            metrics["dates"].append(exp.expense_date)
        
        # Calculate performance scores for each vendor
        for vendor, metrics in vendor_metrics.items():
            if metrics["transaction_count"] < 2:
                continue  # Need multiple transactions for meaningful analysis
            
            metrics["avg_amount"] = metrics["total_spent"] / metrics["transaction_count"]
            
            # 1. Consistency Score (0-100): Lower price variation = higher score
            amounts = metrics["amounts"]
            if len(amounts) > 1:
                std_dev = statistics.stdev(amounts)
                cv = std_dev / statistics.mean(amounts)  # Coefficient of variation
                metrics["consistency_score"] = max(0, 100 - (cv * 100))  # Lower variation = higher score
            else:
                metrics["consistency_score"] = 100
            
            # 2. Value Score (0-100): Compare against category averages
            category_avg_map = self._calculate_category_averages(expenses)
            value_scores = []
            
            for category in metrics["categories"]:
                if category in category_avg_map and category_avg_map[category]["count"] > 1:
                    market_avg = category_avg_map[category]["avg"]
                    vendor_avg = metrics["avg_amount"]
                    
                    if market_avg > 0:
                        # Score higher if vendor is below market average
                        ratio = vendor_avg / market_avg
                        if ratio <= 0.9:  # 10% below market
                            value_scores.append(100)
                        elif ratio <= 1.0:  # At or slightly below market
                            value_scores.append(80)
                        elif ratio <= 1.1:  # Slightly above market
                            value_scores.append(60)
                        elif ratio <= 1.2:  # 20% above market
                            value_scores.append(40)
                        else:  # More than 20% above market
                            value_scores.append(20)
            
            metrics["value_score"] = statistics.mean(value_scores) if value_scores else 70  # Default neutral
            
            # 3. Reliability Score (0-100): Based on transaction frequency and recency
            date_range = max(metrics["dates"]) - min(metrics["dates"])
            days_span = date_range.days if date_range.days > 0 else 1
            frequency = metrics["transaction_count"] / (days_span / 30)  # Transactions per month
            
            # Score based on usage frequency
            if frequency >= 2:  # 2+ times per month
                metrics["reliability_score"] = 100
            elif frequency >= 1:  # 1+ times per month
                metrics["reliability_score"] = 85
            elif frequency >= 0.5:  # 2+ times per 2 months
                metrics["reliability_score"] = 70
            elif frequency >= 0.25:  # 1+ times per 4 months
                metrics["reliability_score"] = 55
            else:  # Less frequent
                metrics["reliability_score"] = 40
            
            # 4. Overall Score: Weighted average
            metrics["overall_score"] = (
                metrics["consistency_score"] * 0.3 +  # 30% weight on price consistency
                metrics["value_score"] * 0.4 +        # 40% weight on value/cost efficiency
                metrics["reliability_score"] * 0.3    # 30% weight on reliability/frequency
            )
            
            # Convert sets to lists for JSON serialization
            metrics["categories"] = list(metrics["categories"])
        
        # Rank vendors and generate insights
        ranked_vendors = sorted(
            [(vendor, metrics) for vendor, metrics in vendor_metrics.items() 
             if metrics["transaction_count"] >= 2],
            key=lambda x: x[1]["overall_score"],
            reverse=True
        )
        
        return {
            "vendor_count": len(vendor_metrics),
            "analyzed_vendors": len(ranked_vendors),
            "top_performers": ranked_vendors[:5],  # Top 5 vendors
            "underperformers": ranked_vendors[-3:] if len(ranked_vendors) > 3 else [],  # Bottom 3
            "insights": self._generate_vendor_insights(ranked_vendors),
            "recommendations": self._generate_vendor_recommendations(ranked_vendors)
        }
    
    def _calculate_category_averages(self, expenses: List[Expense]) -> Dict[str, Dict[str, float]]:
        """Calculate average amounts by category for market comparison"""
        category_data = {}
        
        for exp in expenses:
            category = exp.category.name if exp.category else "Uncategorized"
            if category not in category_data:
                category_data[category] = {"total": 0, "count": 0, "avg": 0}
            
            category_data[category]["total"] += exp.amount
            category_data[category]["count"] += 1
        
        # Calculate averages
        for category, data in category_data.items():
            data["avg"] = data["total"] / data["count"]
        
        return category_data
    
    def _generate_vendor_insights(self, ranked_vendors: List) -> List[str]:
        """Generate actionable insights from vendor analysis"""
        insights = []
        
        if not ranked_vendors:
            return ["Insufficient vendor data for analysis"]
        
        # Top performer insights
        if ranked_vendors:
            top_vendor = ranked_vendors[0]
            insights.append(f"Top performing vendor: {top_vendor[0]} (Score: {top_vendor[1]['overall_score']:.1f}/100)")
        
        # Value insights
        high_value_vendors = [v for v in ranked_vendors if v[1]["value_score"] > 80]
        if high_value_vendors:
            insights.append(f"Found {len(high_value_vendors)} cost-efficient vendors - prioritize for future projects")
        
        # Consistency insights
        consistent_vendors = [v for v in ranked_vendors if v[1]["consistency_score"] > 85]
        if consistent_vendors:
            insights.append(f"{len(consistent_vendors)} vendors show consistent pricing - reliable for budgeting")
        
        # Underperformer insights
        underperformers = [v for v in ranked_vendors if v[1]["overall_score"] < 60]
        if underperformers:
            insights.append(f"{len(underperformers)} vendors scoring below 60/100 - consider alternatives")
        
        return insights
    
    def _generate_vendor_recommendations(self, ranked_vendors: List) -> List[Dict[str, Any]]:
        """Generate specific vendor recommendations"""
        recommendations = []
        
        if not ranked_vendors:
            return recommendations
        
        # Recommend top performers
        top_vendors = ranked_vendors[:3]
        if top_vendors:
            recommendations.append({
                "type": "preferred_vendors",
                "priority": "high",
                "title": "Use Top Performing Vendors",
                "vendors": [v[0] for v in top_vendors],
                "potential_impact": "Consistent pricing and reliable service",
                "action": "Prioritize these vendors for future projects"
            })
        
        # Flag underperformers
        underperformers = [v for v in ranked_vendors if v[1]["overall_score"] < 50]
        if underperformers:
            recommendations.append({
                "type": "vendor_review",
                "priority": "medium",
                "title": "Review Underperforming Vendors",
                "vendors": [v[0] for v in underperformers],
                "potential_impact": f"Potential savings by switching vendors",
                "action": "Negotiate better rates or find alternatives"
            })
        
        # Consolidation opportunities
        single_use_vendors = [v for v in ranked_vendors if v[1]["transaction_count"] == 1]
        if len(single_use_vendors) > 5:
            recommendations.append({
                "type": "consolidation",
                "priority": "low",
                "title": "Consolidate One-Time Vendors",
                "vendors": f"{len(single_use_vendors)} vendors used only once",
                "potential_impact": "Reduced administrative overhead and better rates",
                "action": "Use preferred vendors for better volume pricing"
            })
        
        return recommendations
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure when no data available"""
        return {
            "summary": {
                "total_spent": 0,
                "avg_monthly_spending": 0,
                "expense_count": 0,
                "top_spending_categories": [],
                "business_type": self.business_profile.business_type if self.business_profile else "Unknown",
                "analysis_period": "6 months"
            },
            "quick_wins": [],
            "category_optimization": {"category_breakdown": {}, "optimization_opportunities": []},
            "vendor_anomalies": [],
            "seasonal_patterns": {"monthly_totals": {}, "insights": ["No data available"]},
            "job_profitability": {"jobs_analyzed": 0, "job_breakdown": {}, "insights": ["No job data available"]},
            "recommendations": [{
                "priority": "info",
                "category": "data_needed",
                "title": "Start Tracking Expenses",
                "description": "Connect your bank account or upload receipts to start analyzing your spending",
                "potential_impact": 0,
                "actions": ["Connect bank account", "Upload receipts", "Add manual expenses"]
            }],
            "potential_savings": 0.0
        } 