#!/usr/bin/env python3
"""
Simple expense tracking routes for CORA
LAUNCH CRITICAL - Keep it simple!
"""

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, date
import csv
import io
from typing import Optional

from models import get_db, User, Expense
from dependencies.auth import get_current_user

# Router setup
expense_router = APIRouter(prefix="", tags=["Expenses"])
templates = Jinja2Templates(directory="web/templates")

# Hardcoded categories for MVP (don't overcomplicate)
EXPENSE_CATEGORIES = [
    (1, "Materials"),
    (2, "Labor"),
    (3, "Equipment"),
    (4, "Travel"),
    (5, "Permits"),
    (6, "Subcontractor"),
    (7, "Tools"),
    (8, "Office"),
    (9, "Vehicle"),
    (10, "Other")
]

@expense_router.get("/expenses", response_class=HTMLResponse)
async def expenses_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display user's expenses in a simple table"""
    
    # Get user's expenses, newest first
    expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id
    ).order_by(Expense.expense_date.desc()).all()
    
    # Calculate total
    total_cents = sum(e.amount_cents for e in expenses)
    total_dollars = total_cents / 100
    
    # Format expenses for display
    expense_list = []
    for expense in expenses:
        # Get category name
        category_name = "Other"
        for cat_id, cat_name in EXPENSE_CATEGORIES:
            if expense.category_id == cat_id:
                category_name = cat_name
                break
        
        expense_list.append({
            'id': expense.id,
            'date': expense.expense_date.strftime('%Y-%m-%d') if expense.expense_date else '',
            'amount': f"${expense.amount_cents / 100:.2f}",
            'category': category_name,
            'description': expense.description or '',
            'job': expense.job_name or '',
            'vendor': expense.vendor or ''
        })
    
    return templates.TemplateResponse("expenses.html", {
        "request": request,
        "expenses": expense_list,
        "total": f"${total_dollars:.2f}",
        "count": len(expenses),
        "user": current_user
    })

@expense_router.get("/add-expense", response_class=HTMLResponse)
async def add_expense_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Display add expense form"""
    
    # Get user's recent jobs for dropdown (nice to have)
    # For MVP, just let them type it
    
    return templates.TemplateResponse("add_expense.html", {
        "request": request,
        "categories": EXPENSE_CATEGORIES,
        "today": date.today().isoformat(),
        "user": current_user
    })

@expense_router.post("/api/expenses/add")
async def create_expense(
    amount: float = Form(...),
    category: int = Form(...),
    description: str = Form(None),
    vendor: str = Form(None),
    job_name: str = Form(None),
    expense_date: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a new expense"""
    
    try:
        # Convert amount to cents
        amount_cents = int(amount * 100)
        
        # Parse date
        exp_date = datetime.strptime(expense_date, '%Y-%m-%d')
        
        # Create expense
        expense = Expense(
            user_id=current_user.id,
            amount_cents=amount_cents,
            category_id=category,
            description=description,
            vendor=vendor,
            job_name=job_name,
            expense_date=exp_date,
            created_at=datetime.now()
        )
        
        db.add(expense)
        db.commit()
        
        # Redirect back to expenses list
        return RedirectResponse(url="/expenses", status_code=303)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@expense_router.post("/api/expenses/delete/{expense_id}")
async def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an expense"""
    
    # Get expense and verify ownership
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    db.delete(expense)
    db.commit()
    
    return RedirectResponse(url="/expenses", status_code=303)

@expense_router.get("/api/expenses/export")
async def export_expenses_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export expenses as CSV"""
    
    # Get all user's expenses
    expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id
    ).order_by(Expense.expense_date.desc()).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Date', 'Amount', 'Category', 'Description', 'Vendor', 'Job'])
    
    # Data rows
    for expense in expenses:
        # Get category name
        category_name = "Other"
        for cat_id, cat_name in EXPENSE_CATEGORIES:
            if expense.category_id == cat_id:
                category_name = cat_name
                break
        
        writer.writerow([
            expense.expense_date.strftime('%Y-%m-%d') if expense.expense_date else '',
            f"{expense.amount_cents / 100:.2f}",
            category_name,
            expense.description or '',
            expense.vendor or '',
            expense.job_name or ''
        ])
    
    # Prepare download
    output.seek(0)
    filename = f"expenses_{current_user.email}_{date.today().isoformat()}.csv"
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )