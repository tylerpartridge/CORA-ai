#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/expense_coordinator.py
🎯 PURPOSE: Expense routes stub - minimal safe implementation
🔗 IMPORTS: FastAPI router
📤 EXPORTS: expense_router
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from dependencies.database import get_db
from models import Expense, User
from dependencies.auth import get_current_user

# Create router
expense_router = APIRouter(
    prefix="/api/expenses",
    tags=["Expenses"],
    responses={404: {"description": "Not found"}},
)

# Request/Response models
class ExpenseCreate(BaseModel):
    amount: float
    vendor: str
    category: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None

class ExpenseResponse(BaseModel):
    id: int
    amount: float
    vendor: str
    category: Optional[str]
    description: Optional[str]
    date: datetime
    created_at: datetime

@expense_router.get("/")
async def list_expenses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    expenses = db.query(Expense).filter(Expense.user_id == current_user.id).order_by(Expense.created_at.desc()).offset(skip).limit(limit).all()
    return [ExpenseResponse.from_orm(exp) for exp in expenses]

@expense_router.post("/")
async def create_expense(
    expense: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_expense = Expense(**expense.dict(), user_id=current_user.id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return ExpenseResponse.from_orm(db_expense)

@expense_router.get("/{expense_id}")
async def get_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return ExpenseResponse.from_orm(expense)