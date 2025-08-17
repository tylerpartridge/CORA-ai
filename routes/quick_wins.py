#!/usr/bin/env python3
"""
Quick Win API Routes
Provides endpoints for tax deduction discovery
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from dependencies.database import get_db
from models.user import User
from models.expense import Expense
from dependencies.auth import get_current_user
from tools.quick_win_engine import QuickWinEngine, QuickWin

router = APIRouter(prefix="/api/expenses", tags=["quick_wins"])

class QuickWinResponse(BaseModel):
    expense_id: str
    vendor: str
    amount: float
    category: str
    deduction_rate: float
    tax_savings: float
    annual_savings: float
    tip: str
    confidence: str
    celebration_level: str

class QuickWinsListResponse(BaseModel):
    success: bool
    quick_wins: List[QuickWinResponse]
    total_savings: float
    annual_projection: float
    deduction_rate: float

class AnalyzeDeductionsResponse(BaseModel):
    success: bool
    new_savings: float
    total_analyzed: int
    message: str

@router.get("/quick-wins", response_model=QuickWinsListResponse)
async def get_quick_wins(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current month's quick win deductions"""
    try:
        # Initialize Quick Win Engine with user's tax rate
        # Default to 25% if not set
        tax_rate = getattr(current_user, 'tax_rate', 0.25)
        engine = QuickWinEngine(user_tax_rate=tax_rate)
        
        # Get current month's expenses
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        
        expenses = db.query(Expense).filter(
            Expense.user_id == current_user.id,
            Expense.expense_date >= start_of_month,
            Expense.is_deleted == False
        ).order_by(Expense.expense_date.desc()).all()
        
        # Analyze expenses for quick wins
        quick_wins = []
        total_savings = 0
        total_expenses = 0
        
        for expense in expenses:
            # Skip if already analyzed or marked as personal
            if hasattr(expense, 'is_deductible') and expense.is_deductible is False:
                continue
                
            # Find quick win
            quick_win = engine.find_quick_win(
                expense_description=expense.description,
                amount=expense.amount_cents / 100,  # Convert to dollars
                vendor=expense.vendor
            )
            
            if quick_win:
                quick_wins.append(QuickWinResponse(
                    expense_id=str(expense.id),
                    vendor=expense.vendor or "Unknown",
                    amount=expense.amount_cents / 100,
                    category=quick_win.category,
                    deduction_rate=quick_win.deduction_rate * 100,  # Convert to percentage
                    tax_savings=quick_win.tax_savings,
                    annual_savings=quick_win.annual_savings,
                    tip=quick_win.tip,
                    confidence=quick_win.confidence,
                    celebration_level=quick_win.celebration_level
                ))
                total_savings += quick_win.tax_savings
            
            total_expenses += expense.amount_cents / 100
        
        # Calculate overall deduction rate
        deduction_rate = 0
        if total_expenses > 0:
            total_deductions = sum(
                qw.amount * qw.deduction_rate / 100 
                for qw in quick_wins
            )
            deduction_rate = (total_deductions / total_expenses) * 100
        
        return QuickWinsListResponse(
            success=True,
            quick_wins=quick_wins[:10],  # Top 10 wins
            total_savings=total_savings,
            annual_projection=total_savings * 12,
            deduction_rate=deduction_rate
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-deductions", response_model=AnalyzeDeductionsResponse)
async def analyze_more_deductions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze older expenses for deduction opportunities"""
    try:
        # Initialize Quick Win Engine
        tax_rate = getattr(current_user, 'tax_rate', 0.25)
        engine = QuickWinEngine(user_tax_rate=tax_rate)
        
        # Get unanalyzed expenses from last 90 days
        cutoff_date = datetime.now() - timedelta(days=90)
        
        expenses = db.query(Expense).filter(
            Expense.user_id == current_user.id,
            Expense.expense_date >= cutoff_date,
            Expense.is_deleted == False
        ).all()
        
        # Filter to unanalyzed expenses
        unanalyzed = []
        for expense in expenses:
            # Check if already analyzed (you might add a field for this)
            if not hasattr(expense, 'quick_win_analyzed'):
                unanalyzed.append(expense)
        
        # Analyze batch
        expense_dicts = [
            {
                'description': e.description,
                'amount': e.amount_cents / 100,
                'vendor': e.vendor
            }
            for e in unanalyzed[:50]  # Analyze up to 50 at a time
        ]
        
        results = engine.analyze_expense_batch(expense_dicts)
        
        # Mark expenses as analyzed (you might want to add this field)
        for expense in unanalyzed[:50]:
            # expense.quick_win_analyzed = True
            pass
        
        db.commit()
        
        return AnalyzeDeductionsResponse(
            success=True,
            new_savings=results['total_tax_savings'],
            total_analyzed=len(expense_dicts),
            message=f"Found ${results['total_tax_savings']:.2f} in new deductions!"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/deduction-tips")
async def get_deduction_tips(
    business_type: Optional[str] = "general",
    current_user: User = Depends(get_current_user)
):
    """Get personalized deduction tips"""
    engine = QuickWinEngine()
    
    # Get user's business type or use provided
    user_business_type = business_type
    if hasattr(current_user, 'business_type'):
        user_business_type = current_user.business_type or business_type
    
    tips = engine.get_personalized_tips(user_business_type)
    
    return {
        "success": True,
        "business_type": user_business_type,
        "tips": tips
    }

@router.post("/test-quick-win")
async def test_quick_win(
    description: str,
    amount: float,
    vendor: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Test the quick win engine with a sample expense"""
    engine = QuickWinEngine()
    
    quick_win = engine.find_quick_win(description, amount, vendor)
    
    if quick_win:
        return {
            "success": True,
            "found_deduction": True,
            "quick_win": {
                "category": quick_win.category,
                "deduction_amount": quick_win.deduction_amount,
                "tax_savings": quick_win.tax_savings,
                "annual_savings": quick_win.annual_savings,
                "tip": quick_win.tip,
                "confidence": quick_win.confidence
            }
        }
    else:
        return {
            "success": True,
            "found_deduction": False,
            "message": "No clear deduction found for this expense"
        }

# Mount this router in your main app
# app.include_router(router)