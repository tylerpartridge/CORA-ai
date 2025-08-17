#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/features/profit_intelligence/advanced_analytics.py
🎯 PURPOSE: Advanced profit intelligence algorithms for revenue optimization
🔗 IMPORTS: numpy-like calculations, pattern recognition, business intelligence
📤 EXPORTS: ProfitIntelligenceEngine class
"""

from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
import statistics
import json
from collections import defaultdict

class ProfitIntelligenceEngine:
    """
    Advanced Profit Intelligence Engine
    
    Transforms basic expense tracking into predictive profit optimization
    using pattern recognition, market intelligence, and AI-driven insights
    """
    
    def __init__(self, profit_detector):
        """Initialize with existing profit detector for data access"""
        self.profit_detector = profit_detector
        self.db = profit_detector.db
        self.user_id = profit_detector.user_id
        
    def generate_industry_benchmarks(self, business_type: str, region: str = None) -> Dict[str, Any]:
        """
        Generate anonymous industry benchmarks by aggregating all users' data
        Provides competitive intelligence without revealing individual data
        """
        # Get all businesses of same type
        from models.business_profile import BusinessProfile
        from models.expense import Expense
        
        similar_businesses = self.db.query(BusinessProfile).filter(
            BusinessProfile.business_type == business_type
        ).all()
        
        if len(similar_businesses) < 3:  # Need minimum for anonymity
            return {"status": "insufficient_data", "message": "More businesses needed for benchmarking"}
        
        # Aggregate expense patterns
        category_benchmarks = defaultdict(lambda: {"total": 0, "count": 0, "businesses": set()})
        revenue_ranges = defaultdict(int)
        
        for business in similar_businesses:
            # Get expenses for this business's user
            user_expenses = self.db.query(Expense).filter(
                Expense.user_id == business.user_id
            ).all()
            
            for expense in user_expenses:
                category = expense.category.name if expense.category else "Uncategorized"
                category_benchmarks[category]["total"] += expense.amount
                category_benchmarks[category]["count"] += 1
                category_benchmarks[category]["businesses"].add(business.user_id)
            
            # Track revenue ranges
            revenue_ranges[business.monthly_revenue_range] += 1
        
        # Calculate benchmark percentages
        benchmarks = {}
        total_spending = sum(data["total"] for data in category_benchmarks.values())
        
        for category, data in category_benchmarks.items():
            if len(data["businesses"]) >= 3:  # Anonymity threshold
                benchmarks[category] = {
                    "avg_percentage": (data["total"] / total_spending * 100) if total_spending > 0 else 0,
                    "avg_amount": data["total"] / data["count"] if data["count"] > 0 else 0,
                    "businesses_reporting": len(data["businesses"]),
                    "frequency": data["count"] / len(data["businesses"])
                }
        
        # Compare to user's spending
        user_comparison = self._compare_to_benchmarks(benchmarks)
        
        return {
            "business_type": business_type,
            "sample_size": len(similar_businesses),
            "benchmarks": benchmarks,
            "revenue_distribution": dict(revenue_ranges),
            "user_comparison": user_comparison,
            "insights": self._generate_benchmark_insights(benchmarks, user_comparison),
            "opportunities": self._identify_benchmark_opportunities(user_comparison)
        }
    
    def predict_job_profitability(self, job_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict job profitability before completion using historical patterns
        and machine learning-like pattern matching
        """
        # Extract job parameters
        job_type = job_details.get("type", "general")
        estimated_revenue = job_details.get("revenue", 0)
        duration_days = job_details.get("duration", 30)
        materials_list = job_details.get("materials", [])
        
        # Get historical job data
        from models.job import Job
        from models.expense import Expense
        
        historical_jobs = self.db.query(Job).filter(
            Job.user_id == self.user_id,
            Job.status == "completed"
        ).all()
        
        if not historical_jobs:
            return self._default_job_prediction(job_details)
        
        # Analyze similar jobs
        similar_jobs = []
        for job in historical_jobs:
            similarity_score = self._calculate_job_similarity(job, job_details)
            if similarity_score > 0.5:  # 50% similarity threshold
                job_expenses = self.db.query(Expense).filter(
                    Expense.job_id == job.id
                ).all()
                
                total_cost = sum(exp.amount for exp in job_expenses)
                profit_margin = ((float(job.quoted_amount) - total_cost) / float(job.quoted_amount) * 100) if job.quoted_amount > 0 else 0
                
                similar_jobs.append({
                    "job": job,
                    "total_cost": total_cost,
                    "profit_margin": profit_margin,
                    "similarity": similarity_score,
                    "expense_breakdown": self._categorize_job_expenses(job_expenses)
                })
        
        if not similar_jobs:
            return self._default_job_prediction(job_details)
        
        # Weight predictions by similarity
        weighted_costs = sum(float(j["total_cost"]) * j["similarity"] for j in similar_jobs)
        weighted_margins = sum(float(j["profit_margin"]) * j["similarity"] for j in similar_jobs)
        total_weight = sum(j["similarity"] for j in similar_jobs)
        
        predicted_cost = weighted_costs / total_weight if total_weight > 0 else 0
        predicted_margin = weighted_margins / total_weight if total_weight > 0 else 0
        
        # Material cost predictions
        material_predictions = self._predict_material_costs(materials_list, similar_jobs)
        
        # Risk assessment
        risk_factors = self._assess_job_risks(job_details, similar_jobs)
        
        return {
            "job_type": job_type,
            "estimated_revenue": estimated_revenue,
            "predicted_cost": predicted_cost,
            "predicted_profit": estimated_revenue - predicted_cost,
            "predicted_margin": predicted_margin,
            "confidence": self._calculate_prediction_confidence(similar_jobs),
            "similar_jobs_analyzed": len(similar_jobs),
            "cost_breakdown": {
                "materials": material_predictions["total"],
                "labor": predicted_cost * 0.4,  # Industry average
                "equipment": predicted_cost * 0.15,
                "other": predicted_cost * 0.05
            },
            "material_predictions": material_predictions,
            "risk_assessment": risk_factors,
            "recommendations": self._generate_job_recommendations(predicted_margin, risk_factors),
            "optimization_opportunities": self._identify_job_optimizations(similar_jobs)
        }
    
    def optimize_pricing_strategy(self, service_type: str, market_conditions: Dict = None) -> Dict[str, Any]:
        """
        AI-driven pricing optimization based on market analysis and profit goals
        """
        # Analyze historical pricing and margins
        from models.job import Job
        from models.expense import Expense
        
        completed_jobs = self.db.query(Job).filter(
            Job.user_id == self.user_id,
            Job.status == "completed"
        ).all()
        
        pricing_data = []
        for job in completed_jobs:
            job_expenses = self.db.query(Expense).filter(
                Expense.job_id == job.id
            ).all()
            
            total_cost = sum(exp.amount for exp in job_expenses)
            if job.quoted_amount > 0:
                pricing_data.append({
                    "job_name": job.job_name,
                    "quoted": job.quoted_amount,
                    "actual_cost": total_cost,
                    "margin": (float(job.quoted_amount) - total_cost) / float(job.quoted_amount) * 100,
                    "duration": (job.end_date - job.start_date).days if job.end_date and job.start_date else 0
                })
        
        if not pricing_data:
            return {"status": "insufficient_data", "message": "Need completed jobs for pricing analysis"}
        
        # Calculate optimal pricing metrics
        margins = [p["margin"] for p in pricing_data]
        avg_margin = statistics.mean(margins)
        margin_std = statistics.stdev(margins) if len(margins) > 1 else 0
        
        # Identify pricing sweet spots
        high_margin_jobs = [p for p in pricing_data if p["margin"] > avg_margin + margin_std]
        low_margin_jobs = [p for p in pricing_data if p["margin"] < avg_margin - margin_std]
        
        # Market-adjusted recommendations
        market_factor = 1.0
        if market_conditions:
            if market_conditions.get("demand", "normal") == "high":
                market_factor = 1.1  # 10% premium in high demand
            elif market_conditions.get("competition", "normal") == "low":
                market_factor = 1.05  # 5% premium with low competition
        
        # Generate pricing tiers
        pricing_tiers = {
            "premium": {
                "margin_target": avg_margin + margin_std,
                "multiplier": 1.2 * market_factor,
                "conditions": ["Complex jobs", "Tight deadlines", "Specialized skills"],
                "expected_close_rate": 0.3
            },
            "standard": {
                "margin_target": avg_margin,
                "multiplier": 1.0 * market_factor,
                "conditions": ["Regular jobs", "Normal timeline", "Standard scope"],
                "expected_close_rate": 0.6
            },
            "competitive": {
                "margin_target": max(avg_margin - margin_std, 10),  # Minimum 10% margin
                "multiplier": 0.9 * market_factor,
                "conditions": ["High competition", "Repeat customer", "Volume work"],
                "expected_close_rate": 0.8
            }
        }
        
        # ROI projections
        roi_projections = self._calculate_pricing_roi(pricing_tiers, len(completed_jobs))
        
        return {
            "current_avg_margin": avg_margin,
            "margin_volatility": margin_std / avg_margin * 100 if avg_margin > 0 else 0,
            "pricing_tiers": pricing_tiers,
            "roi_projections": roi_projections,
            "optimization_insights": [
                f"Your average margin is {avg_margin:.1f}%",
                f"High-margin jobs ({len(high_margin_jobs)}) averaged {statistics.mean([j['margin'] for j in high_margin_jobs]):.1f}%" if high_margin_jobs else None,
                f"Consider raising prices by {(market_factor - 1) * 100:.0f}% based on market conditions" if market_factor > 1 else None
            ],
            "action_items": self._generate_pricing_actions(avg_margin, pricing_tiers)
        }
    
    def network_effect_analysis(self) -> Dict[str, Any]:
        """
        Analyze potential network effects and referral opportunities
        Creates value through aggregated intelligence
        """
        # Analyze vendor relationships
        vendor_network = self._analyze_vendor_network()
        
        # Identify collaboration opportunities
        collaboration_potential = self._identify_collaboration_opportunities()
        
        # Calculate network value
        network_value = {
            "vendor_negotiation_power": vendor_network["aggregate_volume"],
            "knowledge_sharing_value": collaboration_potential["shared_insights"],
            "referral_network_size": collaboration_potential["potential_referrals"],
            "collective_bargaining_savings": vendor_network["potential_savings"]
        }
        
        return {
            "network_analysis": vendor_network,
            "collaboration_opportunities": collaboration_potential,
            "network_value": network_value,
            "growth_strategies": self._generate_network_strategies(network_value)
        }
    
    # Helper methods
    def _compare_to_benchmarks(self, benchmarks: Dict) -> Dict[str, Any]:
        """Compare user's spending to industry benchmarks"""
        from models.expense import Expense
        
        user_expenses = self.db.query(Expense).filter(
            Expense.user_id == self.user_id
        ).all()
        
        user_categories = defaultdict(float)
        total_spending = 0
        
        for expense in user_expenses:
            category = expense.category.name if expense.category else "Uncategorized"
            user_categories[category] += expense.amount
            total_spending += expense.amount
        
        comparison = {}
        for category, amount in user_categories.items():
            if category in benchmarks:
                user_percentage = (amount / total_spending * 100) if total_spending > 0 else 0
                benchmark_percentage = benchmarks[category]["avg_percentage"]
                
                comparison[category] = {
                    "user_percentage": user_percentage,
                    "benchmark_percentage": benchmark_percentage,
                    "difference": user_percentage - benchmark_percentage,
                    "status": "above" if user_percentage > benchmark_percentage else "below" if user_percentage < benchmark_percentage else "at",
                    "potential_savings": amount * 0.1 if user_percentage > benchmark_percentage * 1.2 else 0
                }
        
        return comparison
    
    def _generate_benchmark_insights(self, benchmarks: Dict, comparison: Dict) -> List[str]:
        """Generate insights from benchmark comparison"""
        insights = []
        
        # Find categories where user is significantly above benchmark
        overspending = [cat for cat, data in comparison.items() if data["difference"] > 5]
        if overspending:
            insights.append(f"You're spending more than industry average on: {', '.join(overspending)}")
        
        # Find categories where user is below benchmark (potential quality concern)
        underspending = [cat for cat, data in comparison.items() if data["difference"] < -5]
        if underspending:
            insights.append(f"You're spending less than industry average on: {', '.join(underspending)} - ensure quality isn't compromised")
        
        # Total savings opportunity
        total_savings = sum(data["potential_savings"] for data in comparison.values())
        if total_savings > 0:
            insights.append(f"Potential savings of ${total_savings:.0f}/month by matching industry benchmarks")
        
        return insights
    
    def _identify_benchmark_opportunities(self, comparison: Dict) -> List[Dict[str, Any]]:
        """Identify specific opportunities from benchmark analysis"""
        opportunities = []
        
        for category, data in comparison.items():
            if data["potential_savings"] > 100:  # Significant savings opportunity
                opportunities.append({
                    "category": category,
                    "action": f"Reduce {category} spending by {data['difference']:.1f}%",
                    "potential_savings": data["potential_savings"],
                    "risk": "low" if data["difference"] > 10 else "medium",
                    "implementation": f"Review {category} vendors and negotiate better rates"
                })
        
        return sorted(opportunities, key=lambda x: x["potential_savings"], reverse=True)
    
    def _calculate_job_similarity(self, historical_job, job_details: Dict) -> float:
        """Calculate similarity score between jobs"""
        similarity = 0.0
        factors = 0
        
        # Revenue similarity (most important)
        if historical_job.quoted_amount and job_details.get("revenue"):
            revenue_diff = abs(float(historical_job.quoted_amount) - job_details["revenue"]) / max(float(historical_job.quoted_amount), job_details["revenue"])
            similarity += (1 - revenue_diff) * 0.4
            factors += 0.4
        
        # Duration similarity
        if historical_job.start_date and historical_job.end_date and job_details.get("duration"):
            hist_duration = (historical_job.end_date - historical_job.start_date).days
            duration_diff = abs(hist_duration - job_details["duration"]) / max(hist_duration, job_details["duration"])
            similarity += (1 - duration_diff) * 0.3
            factors += 0.3
        
        # Type similarity
        if job_details.get("type"):
            if job_details["type"].lower() in historical_job.job_name.lower():
                similarity += 0.3
            factors += 0.3
        
        return similarity / factors if factors > 0 else 0
    
    def _categorize_job_expenses(self, expenses: List) -> Dict[str, float]:
        """Categorize job expenses"""
        categories = defaultdict(float)
        for expense in expenses:
            category = expense.category.name if expense.category else "Other"
            categories[category] += expense.amount
        return dict(categories)
    
    def _predict_material_costs(self, materials_list: List[str], similar_jobs: List[Dict]) -> Dict[str, Any]:
        """Predict material costs based on historical data"""
        material_costs = defaultdict(list)
        
        for job_data in similar_jobs:
            if "Materials" in job_data["expense_breakdown"]:
                material_costs["total"].append(job_data["expense_breakdown"]["Materials"])
        
        if material_costs["total"]:
            avg_material_cost = statistics.mean(material_costs["total"])
            return {
                "total": avg_material_cost,
                "confidence": "high" if len(material_costs["total"]) > 3 else "medium",
                "based_on": len(material_costs["total"])
            }
        
        return {"total": 0, "confidence": "low", "based_on": 0}
    
    def _assess_job_risks(self, job_details: Dict, similar_jobs: List[Dict]) -> Dict[str, Any]:
        """Assess risks for the job"""
        risks = {
            "cost_overrun": "low",
            "timeline": "low",
            "profitability": "low"
        }
        
        # Analyze margin volatility in similar jobs
        if similar_jobs:
            margins = [j["profit_margin"] for j in similar_jobs]
            if len(margins) > 1:
                margin_volatility = statistics.stdev(margins)
                if margin_volatility > 10:
                    risks["profitability"] = "high"
                elif margin_volatility > 5:
                    risks["profitability"] = "medium"
        
        # Check if job type is new
        if not similar_jobs:
            risks["cost_overrun"] = "high"
            risks["timeline"] = "medium"
        
        return risks
    
    def _calculate_prediction_confidence(self, similar_jobs: List[Dict]) -> float:
        """Calculate confidence in prediction"""
        if not similar_jobs:
            return 0.0
        
        # Base confidence on number of similar jobs and their similarity scores
        base_confidence = min(len(similar_jobs) / 5, 1.0) * 50  # Up to 50% from quantity
        similarity_confidence = statistics.mean([j["similarity"] for j in similar_jobs]) * 50  # Up to 50% from similarity
        
        return min(base_confidence + similarity_confidence, 95)  # Cap at 95%
    
    def _generate_job_recommendations(self, predicted_margin: float, risk_factors: Dict) -> List[str]:
        """Generate recommendations for job execution"""
        recommendations = []
        
        if predicted_margin < 15:
            recommendations.append("Consider increasing quote - margin below 15% target")
        
        if risk_factors["cost_overrun"] == "high":
            recommendations.append("Add 10-15% contingency for unexpected costs")
        
        if risk_factors["profitability"] == "high":
            recommendations.append("Monitor expenses closely - high volatility in similar jobs")
        
        if predicted_margin > 30:
            recommendations.append("Excellent margin predicted - ensure quality delivery to maintain reputation")
        
        return recommendations
    
    def _identify_job_optimizations(self, similar_jobs: List[Dict]) -> List[Dict[str, Any]]:
        """Identify optimization opportunities from similar jobs"""
        optimizations = []
        
        # Find best performing similar jobs
        if similar_jobs:
            best_margin = max(j["profit_margin"] for j in similar_jobs)
            best_job = next(j for j in similar_jobs if j["profit_margin"] == best_margin)
            
            optimizations.append({
                "opportunity": "Match best performing job",
                "reference": best_job["job"].job_name,
                "potential_improvement": f"{best_margin - statistics.mean([j['profit_margin'] for j in similar_jobs]):.1f}% margin increase",
                "tactics": ["Review cost structure", "Replicate efficient practices", "Negotiate similar vendor rates"]
            })
        
        return optimizations
    
    def _default_job_prediction(self, job_details: Dict) -> Dict[str, Any]:
        """Default prediction when no historical data available"""
        estimated_revenue = job_details.get("revenue", 0)
        industry_avg_margin = 20  # Industry average for construction
        
        return {
            "job_type": job_details.get("type", "general"),
            "estimated_revenue": estimated_revenue,
            "predicted_cost": estimated_revenue * 0.8,
            "predicted_profit": estimated_revenue * 0.2,
            "predicted_margin": industry_avg_margin,
            "confidence": 10.0,
            "similar_jobs_analyzed": 0,
            "cost_breakdown": {
                "materials": estimated_revenue * 0.4,
                "labor": estimated_revenue * 0.32,
                "equipment": estimated_revenue * 0.12,
                "other": estimated_revenue * 0.04
            },
            "recommendations": [
                "Track actual costs to improve future predictions",
                "Industry average margin is 20% - aim higher for specialty work",
                "Document all expenses for better analysis"
            ]
        }
    
    def _calculate_pricing_roi(self, pricing_tiers: Dict, job_count: int) -> Dict[str, Any]:
        """Calculate ROI for different pricing strategies"""
        annual_jobs = job_count * 2  # Assume similar pace
        
        roi_projections = {}
        for tier_name, tier_data in pricing_tiers.items():
            expected_jobs = annual_jobs * tier_data["expected_close_rate"]
            margin_improvement = tier_data["margin_target"] - 20  # vs industry average
            
            roi_projections[tier_name] = {
                "expected_annual_jobs": expected_jobs,
                "margin_improvement": margin_improvement,
                "additional_profit_per_job": margin_improvement * 0.01 * 10000,  # Assume $10k avg job
                "annual_additional_profit": expected_jobs * margin_improvement * 100,
                "implementation_effort": "low" if tier_name == "standard" else "medium"
            }
        
        return roi_projections
    
    def _generate_pricing_actions(self, current_margin: float, pricing_tiers: Dict) -> List[str]:
        """Generate specific pricing action items"""
        actions = []
        
        if current_margin < 15:
            actions.append("URGENT: Increase prices immediately - margins too low for sustainability")
        
        if current_margin < pricing_tiers["standard"]["margin_target"]:
            actions.append(f"Raise standard pricing by {pricing_tiers['standard']['margin_target'] - current_margin:.0f}%")
        
        actions.extend([
            "Create pricing template with three tiers",
            "Test premium pricing on next complex job",
            "Track close rates by pricing tier"
        ])
        
        return actions
    
    def _analyze_vendor_network(self) -> Dict[str, Any]:
        """Analyze vendor relationships and network effects"""
        from models.expense import Expense
        
        # Get all platform expenses (simplified - in production would be across users)
        vendor_volumes = defaultdict(float)
        expenses = self.db.query(Expense).filter(Expense.vendor.isnot(None)).all()
        
        for expense in expenses:
            vendor_volumes[expense.vendor] += expense.amount
        
        # Identify high-volume vendors
        high_volume_vendors = {v: amt for v, amt in vendor_volumes.items() if amt > 10000}
        
        return {
            "vendor_count": len(vendor_volumes),
            "high_volume_vendors": high_volume_vendors,
            "aggregate_volume": sum(vendor_volumes.values()),
            "potential_savings": sum(vendor_volumes.values()) * 0.05,  # 5% through collective bargaining
            "negotiation_opportunities": [v for v, amt in high_volume_vendors.items()]
        }
    
    def _identify_collaboration_opportunities(self) -> Dict[str, Any]:
        """Identify opportunities for user collaboration"""
        return {
            "shared_insights": ["Material cost trends", "Vendor performance", "Seasonal patterns"],
            "potential_referrals": 10,  # Placeholder - would calculate based on user base
            "knowledge_value": "high",
            "collaboration_types": ["Vendor recommendations", "Job referrals", "Best practices"]
        }
    
    def _generate_network_strategies(self, network_value: Dict) -> List[str]:
        """Generate strategies to leverage network effects"""
        strategies = []
        
        if network_value["vendor_negotiation_power"] > 100000:
            strategies.append("Leverage collective buying power for 5-10% vendor discounts")
        
        if network_value["referral_network_size"] > 5:
            strategies.append("Activate referral network for new business opportunities")
        
        strategies.extend([
            "Share anonymized cost benchmarks with network",
            "Create vendor performance ratings",
            "Enable job collaboration features"
        ])
        
        return strategies