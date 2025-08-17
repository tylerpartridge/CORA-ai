#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/profit_analysis.py
🎯 PURPOSE: API routes for CORA's profit leak detection engine
🔗 IMPORTS: FastAPI, dependencies, profit leak detector
📤 EXPORTS: Profit analysis API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from dependencies.database import get_db
from dependencies.auth import get_current_user
from services.profit_leak_detector import ProfitLeakDetector
from models.user import User

router = APIRouter(prefix="/api/profit-analysis", tags=["profit-analysis"])

@router.get("/leak-detection")
async def analyze_profit_leaks(
    months_back: int = Query(6, ge=1, le=24, description="Number of months to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Analyze profit leaks and identify cost-saving opportunities
    
    Returns comprehensive analysis including:
    - Quick wins (immediate savings)
    - Category optimization opportunities  
    - Vendor price anomalies
    - Seasonal cost patterns
    - Job profitability insights
    """
    try:
        detector = ProfitLeakDetector(db, current_user.id)
        analysis = detector.analyze_profit_leaks(months_back)
        
        return {
            "success": True,
            "data": analysis,
            "message": f"Profit leak analysis completed for {months_back} months"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing profit leaks: {str(e)}"
        )

@router.get("/quick-wins")
async def get_quick_wins(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get immediate cost-saving opportunities (quick wins)
    """
    try:
        detector = ProfitLeakDetector(db, current_user.id)
        analysis = detector.analyze_profit_leaks(6)  # 6 months for quick wins
        
        return {
            "success": True,
            "data": {
                "quick_wins": analysis["quick_wins"],
                "total_potential_savings": sum(win["potential_savings"] for win in analysis["quick_wins"]),
                "count": len(analysis["quick_wins"])
            },
            "message": f"Found {len(analysis['quick_wins'])} quick win opportunities"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting quick wins: {str(e)}"
        )

@router.get("/category-optimization")
async def get_category_optimization(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get category spending optimization opportunities
    """
    try:
        detector = ProfitLeakDetector(db, current_user.id)
        analysis = detector.analyze_profit_leaks(6)
        
        return {
            "success": True,
            "data": analysis["category_optimization"],
            "message": "Category optimization analysis completed"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing category optimization: {str(e)}"
        )

@router.get("/vendor-anomalies")
async def get_vendor_anomalies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get vendor pricing anomalies and unusual patterns
    """
    try:
        detector = ProfitLeakDetector(db, current_user.id)
        analysis = detector.analyze_profit_leaks(6)
        
        return {
            "success": True,
            "data": {
                "vendor_anomalies": analysis["vendor_anomalies"],
                "count": len(analysis["vendor_anomalies"]),
                "total_potential_savings": len(analysis["vendor_anomalies"]) * 50  # Conservative estimate
            },
            "message": f"Found {len(analysis['vendor_anomalies'])} vendor anomalies"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing vendor anomalies: {str(e)}"
        )

@router.get("/seasonal-patterns")
async def get_seasonal_patterns(
    months_back: int = Query(12, ge=6, le=24, description="Number of months for seasonal analysis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get seasonal spending patterns and insights
    """
    try:
        detector = ProfitLeakDetector(db, current_user.id)
        analysis = detector.analyze_profit_leaks(months_back)
        
        return {
            "success": True,
            "data": analysis["seasonal_patterns"],
            "message": "Seasonal pattern analysis completed"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing seasonal patterns: {str(e)}"
        )

@router.get("/cost-forecast")
async def get_cost_forecast(
    forecast_months: int = Query(3, ge=1, le=12, description="Number of months to forecast"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Advanced predictive cost modeling using AI pattern recognition
    Forecasts future expenses based on historical trends and patterns
    """
    try:
        detector = ProfitLeakDetector(db, current_user.id)
        forecast = detector.predict_future_costs(forecast_months)
        
        if "error" in forecast:
            return {
                "success": False,
                "error": forecast["error"],
                "details": forecast,
                "message": "Insufficient data for accurate forecasting"
            }
        
        return {
            "success": True,
            "data": forecast,
            "message": f"Generated {forecast_months}-month cost forecast with {forecast['confidence']} confidence"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating cost forecast: {str(e)}"
        )

@router.post("/smart-categorization")
async def smart_expense_categorization(
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    AI-powered expense categorization using pattern recognition
    Learns from user's historical data to suggest optimal categories
    """
    try:
        description = request.get("description", "")
        vendor = request.get("vendor", "")
        amount = float(request.get("amount", 0))
        
        if not description:
            raise HTTPException(status_code=400, detail="Description is required")
        
        detector = ProfitLeakDetector(db, current_user.id)
        categorization = detector.intelligent_expense_categorization(description, vendor, amount)
        
        return {
            "success": True,
            "data": categorization,
            "message": f"Suggested category: {categorization['suggested_category']} ({categorization['confidence']:.1f}% confidence)"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid amount: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error categorizing expense: {str(e)}"
        )

@router.get("/vendor-performance")
async def get_vendor_performance_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Advanced vendor performance analysis with scoring and recommendations
    Evaluates vendors on cost efficiency, reliability, and consistency
    """
    try:
        detector = ProfitLeakDetector(db, current_user.id)
        performance = detector.analyze_vendor_performance()
        
        if "error" in performance:
            return {
                "success": False,
                "error": performance["error"],
                "message": "No vendor data available for analysis"
            }
        
        return {
            "success": True,
            "data": performance,
            "message": f"Analyzed {performance['analyzed_vendors']} vendors with performance scoring"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing vendor performance: {str(e)}"
        )

@router.get("/job-profitability")
async def get_job_profitability(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get job-specific profitability analysis
    """
    try:
        detector = ProfitLeakDetector(db, current_user.id)
        analysis = detector.analyze_profit_leaks(6)
        
        return {
            "success": True,
            "data": analysis["job_profitability"],
            "message": "Job profitability analysis completed"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing job profitability: {str(e)}"
        )

@router.get("/recommendations")
async def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get actionable recommendations based on profit leak analysis
    """
    try:
        detector = ProfitLeakDetector(db, current_user.id)
        analysis = detector.analyze_profit_leaks(6)
        
        return {
            "success": True,
            "data": {
                "recommendations": analysis["recommendations"],
                "total_potential_savings": analysis["potential_savings"],
                "priority_breakdown": {
                    "high": len([r for r in analysis["recommendations"] if r["priority"] == "high"]),
                    "medium": len([r for r in analysis["recommendations"] if r["priority"] == "medium"]),
                    "low": len([r for r in analysis["recommendations"] if r["priority"] == "low"])
                }
            },
            "message": f"Generated {len(analysis['recommendations'])} recommendations"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )

@router.get("/summary")
async def get_profit_analysis_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get summary of profit leak analysis with key metrics
    """
    try:
        detector = ProfitLeakDetector(db, current_user.id)
        analysis = detector.analyze_profit_leaks(6)
        
        return {
            "success": True,
            "data": {
                "summary": analysis["summary"],
                "potential_savings": analysis["potential_savings"],
                "quick_wins_count": len(analysis["quick_wins"]),
                "vendor_anomalies_count": len(analysis["vendor_anomalies"]),
                "recommendations_count": len(analysis["recommendations"]),
                "roi_percentage": (analysis["potential_savings"] / analysis["summary"]["total_spent"] * 100) if analysis["summary"]["total_spent"] > 0 else 0
            },
            "message": "Profit analysis summary generated"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summary: {str(e)}"
        ) 