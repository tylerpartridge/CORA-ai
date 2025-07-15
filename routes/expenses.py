#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/expenses.py
🎯 PURPOSE: Expense management routes
🔗 IMPORTS: FastAPI, models, services
📤 EXPORTS: expense_router
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from models import get_db, Expense, ExpenseCategory
import re

# AI Categorization mappings
CATEGORY_PATTERNS = {
    "Office Supplies": {
        "vendors": ["staples", "office depot", "amazon"],
        "keywords": ["supplies", "printer", "ink", "paper", "desk", "chair", "stationery"],
        "weight": 1.0
    },
    "Meals & Entertainment": {
        "vendors": ["chipotle", "starbucks", "mcdonalds", "subway", "olive garden", "restaurant"],
        "keywords": ["lunch", "dinner", "breakfast", "coffee", "meal", "food", "client lunch", "networking"],
        "weight": 1.0
    },
    "Transportation": {
        "vendors": ["uber", "lyft", "taxi", "parking"],
        "keywords": ["ride", "transport", "parking", "gas", "fuel", "mileage"],
        "weight": 1.0
    },
    "Software & Subscriptions": {
        "vendors": ["adobe", "microsoft", "google", "dropbox", "slack", "zoom"],
        "keywords": ["software", "subscription", "saas", "license", "cloud", "app"],
        "weight": 1.0
    },
    "Marketing & Advertising": {
        "vendors": ["facebook", "google ads", "mailchimp", "godaddy"],
        "keywords": ["marketing", "advertising", "promotion", "domain", "hosting", "seo", "ads"],
        "weight": 1.0
    },
    "Shipping & Postage": {
        "vendors": ["usps", "fedex", "ups", "dhl"],
        "keywords": ["shipping", "postage", "mail", "package", "delivery"],
        "weight": 1.0
    },
    "Professional Development": {
        "vendors": ["udemy", "coursera", "conference"],
        "keywords": ["training", "course", "conference", "workshop", "seminar", "education"],
        "weight": 1.0
    },
    "Travel": {
        "vendors": ["hotel", "airline", "airbnb", "booking.com"],
        "keywords": ["flight", "hotel", "travel", "accommodation", "lodging"],
        "weight": 1.0
    },
    "Utilities": {
        "vendors": ["electric", "water", "internet", "phone"],
        "keywords": ["utility", "electric", "water", "internet", "phone", "telecom"],
        "weight": 1.0
    },
    "Insurance": {
        "vendors": ["state farm", "geico", "allstate"],
        "keywords": ["insurance", "premium", "coverage", "liability"],
        "weight": 1.0
    }
}

def categorize_expense(description: str, vendor: str = None, amount_cents: int = None) -> tuple[str, int]:
    """
    AI-powered expense categorization
    Returns: (category_name, confidence_score)
    """
    # Normalize inputs
    desc_lower = description.lower() if description else ""
    vendor_lower = vendor.lower() if vendor else ""
    
    category_scores = {}
    
    # Score each category based on pattern matching
    for category, patterns in CATEGORY_PATTERNS.items():
        score = 0
        
        # Check vendor match (highest weight)
        for vendor_pattern in patterns["vendors"]:
            if vendor_pattern in vendor_lower:
                score += 50
                break
        
        # Check keyword matches
        for keyword in patterns["keywords"]:
            if keyword in desc_lower:
                score += 20
            if vendor and keyword in vendor_lower:
                score += 15
        
        # Amount-based heuristics
        if amount_cents:
            if category == "Meals & Entertainment" and 500 <= amount_cents <= 15000:
                score += 10
            elif category == "Transportation" and 1000 <= amount_cents <= 10000:
                score += 10
            elif category == "Professional Development" and amount_cents > 50000:
                score += 10
        
        if score > 0:
            category_scores[category] = score
    
    # Get best match
    if category_scores:
        best_category = max(category_scores, key=category_scores.get)
        confidence = min(category_scores[best_category], 95)  # Cap at 95%
        return best_category, confidence
    
    # Default fallback
    return "Other", 0

# Currency formatting helper
def format_currency(amount_cents: int, currency: str = "USD") -> str:
    """
    Format amount in cents to human-readable currency string
    
    Args:
        amount_cents: Amount in cents (e.g., 1550 for $15.50)
        currency: Currency code (default: USD)
    
    Returns:
        Formatted string (e.g., "$15.50")
    """
    amount = amount_cents / 100
    
    # Currency symbols mapping
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CAD": "C$",
        "AUD": "A$",
        "CHF": "Fr.",
        "CNY": "¥",
        "INR": "₹",
        "MXN": "$",
        "BRL": "R$",
        "KRW": "₩",
        "SGD": "S$",
        "HKD": "HK$",
        "NZD": "NZ$"
    }
    
    symbol = symbols.get(currency, currency + " ")
    
    # Format based on currency conventions
    if currency == "JPY" or currency == "KRW":
        # These currencies don't use decimal places
        return f"{symbol}{int(amount):,}"
    else:
        # Most currencies use 2 decimal places
        return f"{symbol}{amount:,.2f}"

# Create router
expense_router = APIRouter(
    prefix="/api/expenses",
    tags=["expenses"]
)

# Pydantic models for requests/responses
class ExpenseResponse(BaseModel):
    id: int
    expense_date: datetime
    description: str
    amount_cents: int
    currency: str
    vendor: Optional[str]
    category_id: Optional[int]
    receipt_url: Optional[str]
    payment_method: Optional[str]
    user_email: str
    created_at: datetime
    updated_at: Optional[datetime]
    confidence_score: Optional[int]
    auto_categorized: Optional[int]
    
    @property
    def formatted_amount(self) -> str:
        """Return formatted currency string"""
        return format_currency(self.amount_cents, self.currency)
    
    class Config:
        from_attributes = True

class ExpenseCategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True

class ExpenseCreate(BaseModel):
    expense_date: datetime
    description: str
    amount_cents: int
    currency: str = "USD"
    vendor: Optional[str] = None
    category_id: Optional[int] = None
    receipt_url: Optional[str] = None
    payment_method: Optional[str] = None

# Routes
@expense_router.get("/", response_model=List[ExpenseResponse])
async def get_expenses(
    user_email: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all expenses for a user"""
    expenses = db.query(Expense).filter(
        Expense.user_email == user_email
    ).offset(skip).limit(limit).all()
    return expenses

@expense_router.get("/categories", response_model=List[ExpenseCategoryResponse])
async def get_expense_categories(db: Session = Depends(get_db)):
    """Get all expense categories"""
    categories = db.query(ExpenseCategory).all()
    return categories

@expense_router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(expense_id: int, user_email: str, db: Session = Depends(get_db)):
    """Get a specific expense"""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_email == user_email
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@expense_router.post("/", response_model=ExpenseResponse)
async def create_expense(
    expense: ExpenseCreate,
    user_email: str,
    db: Session = Depends(get_db)
):
    """Create a new expense with AI categorization"""
    expense_data = expense.dict()
    
    # If no category provided, use AI to suggest one
    if not expense_data.get('category_id'):
        category_name, confidence = categorize_expense(
            expense_data['description'],
            expense_data.get('vendor'),
            expense_data.get('amount_cents')
        )
        
        # Find or create the category
        if category_name != "Other":
            category = db.query(ExpenseCategory).filter(
                ExpenseCategory.name == category_name
            ).first()
            
            if category:
                expense_data['category_id'] = category.id
                expense_data['auto_categorized'] = 1
                expense_data['confidence_score'] = confidence
    
    db_expense = Expense(
        **expense_data,
        user_email=user_email
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@expense_router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense: ExpenseCreate,
    user_email: str,
    db: Session = Depends(get_db)
):
    """Update an expense"""
    db_expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_email == user_email
    ).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    for key, value in expense.dict().items():
        setattr(db_expense, key, value)
    
    db.commit()
    db.refresh(db_expense)
    return db_expense

@expense_router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    user_email: str,
    db: Session = Depends(get_db)
):
    """Delete an expense"""
    db_expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_email == user_email
    ).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    db.delete(db_expense)
    db.commit()
    return {"message": "Expense deleted successfully"}

@expense_router.get("/export/csv")
async def export_expenses_csv(
    user_email: str,
    db: Session = Depends(get_db)
):
    """Export user's expenses as CSV file"""
    expenses = db.query(Expense).filter(
        Expense.user_email == user_email
    ).order_by(Expense.expense_date.desc()).all()
    
    # Get category names for display
    categories = {cat.id: cat.name for cat in db.query(ExpenseCategory).all()}
    
    # Create CSV content
    csv_content = "Date,Description,Amount,Currency,Vendor,Category,Payment Method,Receipt URL\n"
    
    for expense in expenses:
        category_name = categories.get(expense.category_id, "Uncategorized") if expense.category_id else "Uncategorized"
        amount_formatted = format_currency(expense.amount_cents, expense.currency)
        
        # Escape commas and quotes in CSV
        description = f'"{expense.description.replace('"', '""')}"' if ',' in expense.description or '"' in expense.description else expense.description
        vendor = f'"{expense.vendor.replace('"', '""')}"' if expense.vendor and (',' in expense.vendor or '"' in expense.vendor) else (expense.vendor or "")
        
        csv_content += f"{expense.expense_date.strftime('%Y-%m-%d')},{description},{amount_formatted},{expense.currency},{vendor},{category_name},{expense.payment_method or ''},{expense.receipt_url or ''}\n"
    
    # Generate filename with current date
    from datetime import date
    filename = f"cora_expenses_{user_email}_{date.today().strftime('%Y%m%d')}.csv"
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "text/csv; charset=utf-8"
        }
    )