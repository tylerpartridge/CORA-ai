#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/expenses.py
🎯 PURPOSE: Expense management routes
🔗 IMPORTS: FastAPI, models, services
📤 EXPORTS: expense_router
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.responses import Response
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import json
import logging
import hashlib

from models import get_db, Expense, ExpenseCategory, User
from utils.redis_manager import redis_manager
from utils.filenames import generate_filename
from dependencies.auth import get_current_user
import re
import asyncio
from routes.websocket import broadcast_expense_update
from middleware.monitoring import EXPENSES_CREATED, VOICE_EXPENSES_SUCCESS, VOICE_EXPENSES_FAILED
from services.alert_checker import AlertChecker

# AI Categorization mappings
CATEGORY_PATTERNS = {
    # Construction categories
    "Materials - Lumber": {
        "vendors": ["home depot", "lowes", "lumber", "wood"],
        "keywords": ["lumber", "wood", "plywood", "2x4", "2x6", "framing", "studs", "boards"],
        "weight": 1.2
    },
    "Materials - Electrical": {
        "vendors": ["home depot", "lowes", "electrical supply", "graybar"],
        "keywords": ["wire", "outlet", "switch", "breaker", "panel", "electrical", "conduit"],
        "weight": 1.2
    },
    "Materials - Plumbing": {
        "vendors": ["home depot", "lowes", "ferguson", "plumbing"],
        "keywords": ["pipe", "fitting", "valve", "faucet", "plumbing", "pvc", "copper", "pex"],
        "weight": 1.2
    },
    "Materials - Hardware": {
        "vendors": ["home depot", "lowes", "ace hardware", "true value"],
        "keywords": ["screws", "nails", "bolts", "fasteners", "hardware", "brackets", "hinges"],
        "weight": 1.1
    },
    "Equipment - Fuel": {
        "vendors": ["shell", "chevron", "exxon", "gas station", "fuel"],
        "keywords": ["gas", "diesel", "fuel", "gasoline"],
        "weight": 1.1
    },
    "Labor - Subcontractors": {
        "vendors": [],
        "keywords": ["subcontractor", "sub", "contractor", "labor", "crew", "helper"],
        "weight": 1.0
    },
    # Original categories
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

# Import unified currency service
from utils.currency import format_currency

# Cache helper functions
def generate_cache_key(prefix: str, **kwargs) -> str:
    """Generate a cache key from parameters"""
    # Sort kwargs for consistent key generation
    sorted_params = sorted(kwargs.items())
    param_str = json.dumps(sorted_params, sort_keys=True)
    return f"cora:{prefix}:{hashlib.md5(param_str.encode()).hexdigest()}"

def get_cached_data(cache_key: str, ttl: int = 300) -> Optional[dict]:
    """Get data from cache"""
    try:
        cached = redis_manager.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception as e:
        logging.warning(f"Cache get error for key {cache_key}: {e}")
        print(f"Cache get error: {e}")
    return None

def set_cached_data(cache_key: str, data: dict, ttl: int = 300) -> bool:
    """Set data in cache"""
    try:
        return redis_manager.set(cache_key, json.dumps(data), ttl)
    except Exception as e:
        logging.warning(f"Cache set error for key {cache_key}: {e}")
        print(f"Cache set error: {e}")
        return False

def invalidate_user_cache(user_email: str):
    """Invalidate all cache entries for a user"""
    try:
        # This is a simplified invalidation - in production you'd use Redis SCAN
        # For now, we'll rely on TTL-based expiration
        pass
    except Exception as e:
        logging.warning(f"Cache invalidation error for user {user_email}: {e}")
        print(f"Cache invalidation error: {e}")

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
    job_name: Optional[str]  # Construction job name
    job_id: Optional[str]  # Construction job ID
    
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

from utils.validation import ValidatedBaseModel, validate_amount, validate_description, validate_vendor, validate_job_name, validate_url

class ExpenseCreate(ValidatedBaseModel):
    expense_date: datetime
    description: str
    amount_cents: int
    currency: str = "USD"
    vendor: Optional[str] = None
    category_id: Optional[int] = None
    receipt_url: Optional[str] = None
    payment_method: Optional[str] = None
    job_name: Optional[str] = None  # Construction job name
    job_id: Optional[str] = None  # Construction job ID
    
    @validator('expense_date')
    def validate_expense_date(cls, v):
        """
        Validate expense date is present and not in the future.
        
        Args:
            v: The expense date to validate
            
        Returns:
            datetime: The validated expense date
            
        Raises:
            ValueError: If date is missing or in the future
        """
        if not v:
            raise ValueError("Expense date is required")
        # Ensure date is not in the future
        if v > datetime.utcnow():
            raise ValueError("Expense date cannot be in the future")
        return v
    
    @validator('description')
    def validate_description(cls, v):
        """
        Validate and sanitize expense description.
        
        Args:
            v: The description string to validate
            
        Returns:
            str: The validated and sanitized description
            
        Raises:
            ValueError: If description is invalid
        """
        return validate_description(v)
    
    @validator('amount_cents')
    def validate_amount_cents(cls, v):
        """
        Validate expense amount is a positive integer within acceptable range.
        
        Args:
            v: The amount in cents to validate
            
        Returns:
            int: The validated amount in cents
            
        Raises:
            ValueError: If amount is not an integer, <= 0, or exceeds $9,999,999.99
        """
        if not isinstance(v, int):
            raise ValueError("Amount must be an integer (in cents)")
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        if v > 999999999:  # $9,999,999.99
            raise ValueError("Amount cannot exceed $9,999,999.99")
        return v
    
    @validator('currency')
    def validate_currency(cls, v):
        """
        Validate currency is a 3-letter ISO code.
        
        Args:
            v: The currency code to validate
            
        Returns:
            str: The validated currency code in uppercase
            
        Raises:
            ValueError: If currency is not a valid 3-letter code
        """
        if not v or not isinstance(v, str):
            raise ValueError("Currency is required")
        if not re.match(r'^[A-Z]{3}$', v):
            raise ValueError("Currency must be a 3-letter code (e.g., USD)")
        return v.upper()
    
    @validator('vendor')
    def validate_vendor(cls, v):
        """
        Validate and sanitize vendor name.
        
        Args:
            v: The vendor name to validate
            
        Returns:
            str: The validated vendor name or None
            
        Raises:
            ValueError: If vendor name is invalid
        """
        if v is None:
            return v
        return validate_vendor(v)
    
    @validator('category_id')
    def validate_category_id(cls, v):
        """
        Validate category ID is a positive integer or None.
        
        Args:
            v: The category ID to validate
            
        Returns:
            int: The validated category ID or None
            
        Raises:
            ValueError: If category ID is not a positive integer
        """
        if v is not None and (not isinstance(v, int) or v <= 0):
            raise ValueError("Category ID must be a positive integer")
        return v
    
    @validator('receipt_url')
    def validate_receipt_url(cls, v):
        """
        Validate receipt URL format.
        
        Args:
            v: The receipt URL to validate
            
        Returns:
            str: The validated URL or None
            
        Raises:
            ValueError: If URL format is invalid
        """
        if v is None:
            return v
        return validate_url(v, "receipt_url")
    
    @validator('payment_method')
    def validate_payment_method(cls, v):
        """
        Validate payment method is from allowed list.
        
        Args:
            v: The payment method to validate
            
        Returns:
            str: The validated payment method in lowercase or None
            
        Raises:
            ValueError: If payment method is not in allowed list
        """
        if v is None:
            return v
        allowed_methods = ['cash', 'check', 'credit_card', 'debit_card', 'bank_transfer', 'paypal', 'other']
        if v.lower() not in allowed_methods:
            raise ValueError(f"Payment method must be one of: {', '.join(allowed_methods)}")
        return v.lower()
    
    @validator('job_name')
    def validate_job_name(cls, v):
        """
        Validate and sanitize construction job name.
        
        Args:
            v: The job name to validate
            
        Returns:
            str: The validated job name or None
            
        Raises:
            ValueError: If job name is invalid
        """
        if v is None:
            return v
        return validate_job_name(v)
    
    @validator('job_id')
    def validate_job_id(cls, v):
        """
        Validate construction job ID format.
        
        Args:
            v: The job ID to validate
            
        Returns:
            str: The validated job ID or None
            
        Raises:
            ValueError: If job ID format is invalid
        """
        if v is None:
            return v
        if not isinstance(v, str):
            raise ValueError("Job ID must be a string")
        if len(v) > 50:
            raise ValueError("Job ID must be 50 characters or less")
        if not re.match(r'^[A-Za-z0-9\-_]+$', v):
            raise ValueError("Job ID can only contain letters, numbers, hyphens, and underscores")
        return v

# Routes
@expense_router.get("/", response_model=List[ExpenseResponse])
async def get_expenses(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all expenses for a user with optimized queries and caching"""
    
    from utils.query_optimizer import get_optimized_expenses
    from utils.api_response_optimizer import optimize_api_response
    
    @optimize_api_response(compress=True, cache=True, cache_ttl=300)
    async def get_expenses_data():
        # Get optimized expenses
        expenses_data = get_optimized_expenses(db, current_user.id, skip, limit)
        
        # Convert to ExpenseResponse format
        result = []
        for expense_dict in expenses_data:
            # Create ExpenseResponse from dict
            expense_response = ExpenseResponse(
                id=expense_dict["id"],
                expense_date=datetime.fromisoformat(expense_dict["expense_date"]),
                description=expense_dict["description"],
                amount_cents=expense_dict["amount_cents"],
                currency=expense_dict["currency"],
                vendor=expense_dict["vendor"],
                category_id=expense_dict["category_id"],
                receipt_url=expense_dict["receipt_url"],
                payment_method=expense_dict["payment_method"],
                user_email=expense_dict["user_email"],
                created_at=datetime.fromisoformat(expense_dict["created_at"]),
                updated_at=datetime.fromisoformat(expense_dict["updated_at"]) if expense_dict["updated_at"] else None,
                confidence_score=expense_dict["confidence_score"],
                auto_categorized=expense_dict["auto_categorized"],
                job_name=expense_dict["job_name"],
                job_id=expense_dict["job_id"]
            )
            result.append(expense_response)
        
        return result
    
    return await get_expenses_data()

@expense_router.get("/categories", response_model=List[ExpenseCategoryResponse])
async def get_expense_categories(db: Session = Depends(get_db)):
    """Get all expense categories with caching"""
    # Categories rarely change, so cache for longer
    cache_key = generate_cache_key("categories")
    
    # Try to get from cache first
    cached_result = get_cached_data(cache_key, ttl=3600)  # 1 hour cache
    if cached_result:
        return cached_result
    
    # Query database
    categories = db.query(ExpenseCategory).all()
    
    # Convert to response format
    result = [ExpenseCategoryResponse.from_orm(category) for category in categories]
    
    # Cache the result
    set_cached_data(cache_key, [cat.dict() for cat in result], ttl=3600)
    
    return result

@expense_router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific expense"""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@expense_router.post("/", response_model=ExpenseResponse)
async def create_expense(
    expense: ExpenseCreate,
    current_user: User = Depends(get_current_user),
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
    
    # Handle job fields (remove None values)
    if expense_data.get('job_name') is None:
        expense_data.pop('job_name', None)
    if expense_data.get('job_id') is None:
        expense_data.pop('job_id', None)
    
    db_expense = Expense(
        **expense_data,
        user_id=current_user.id
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    
    # Invalidate user cache since expenses changed
    invalidate_user_cache(current_user.email)
    
    # Broadcast update via WebSocket
    expense_data = {
        "id": db_expense.id,
        "description": db_expense.description,
        "amount_cents": db_expense.amount_cents,
        "vendor": db_expense.vendor,
        "job_name": db_expense.job_name,
        "created_at": db_expense.created_at.isoformat() if db_expense.created_at else None
    }
    asyncio.create_task(broadcast_expense_update(current_user.email, expense_data))
    
    # Increment business metric
    EXPENSES_CREATED.labels(source='manual').inc()
    
    # Check for alerts
    job_id = int(db_expense.job_id) if db_expense.job_id else None
    asyncio.create_task(AlertChecker.check_and_create_alerts(current_user.id, job_id, db))
    
    return db_expense

@expense_router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a single expense by ID"""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Get category name
    category = db.query(ExpenseCategory).filter(
        ExpenseCategory.id == expense.category_id
    ).first() if expense.category_id else None
    
    return ExpenseResponse(
        id=expense.id,
        expense_date=expense.expense_date,
        description=expense.description,
        amount_cents=expense.amount_cents,
        currency=expense.currency,
        vendor=expense.vendor,
        category_id=expense.category_id,
        category_name=category.name if category else None,
        job_name=expense.job_name,
        job_id=expense.job_id,
        receipt_url=expense.receipt_url,
        payment_method=expense.payment_method,
        created_at=expense.created_at,
        updated_at=expense.updated_at
    )

@expense_router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an expense"""
    db_expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id
    ).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    for key, value in expense.dict().items():
        setattr(db_expense, key, value)
    
    db.commit()
    db.refresh(db_expense)
    
    # Invalidate user cache since expenses changed
    invalidate_user_cache(current_user.email)
    
    return db_expense

@expense_router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an expense"""
    db_expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id
    ).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    db.delete(db_expense)
    db.commit()
    
    # Invalidate user cache since expenses changed
    invalidate_user_cache(current_user.email)
    
    return {"message": "Expense deleted successfully"}

def _parse_date_range_spec(start_date: Optional[str], end_date: Optional[str], tz_name: str):
    """Parse date range per spec, return (start_local, end_local) as tz-aware datetimes.

    start_local = YYYY-MM-DD 00:00:00 in tz
    end_local = YYYY-MM-DD 23:59:59.999999 in tz
    Raises ValueError on invalid input or invalid order.
    """
    from datetime import datetime, time
    try:
        import zoneinfo
        tz = zoneinfo.ZoneInfo(tz_name)
    except Exception:
        raise ValueError("Invalid timezone identifier. Use IANA format (e.g., America/New_York)")

    start_local = None
    end_local = None
    try:
        if start_date:
            d = datetime.strptime(start_date, '%Y-%m-%d').date()
            start_local = datetime.combine(d, time.min).replace(tzinfo=tz)
        if end_date:
            d2 = datetime.strptime(end_date, '%Y-%m-%d').date()
            end_local = datetime.combine(d2, time.max).replace(tzinfo=tz)
    except Exception:
        raise ValueError("Invalid date format. Use YYYY-MM-DD format.")

    if start_local and end_local and start_local > end_local:
        start_local, end_local = end_local, start_local

    return start_local, end_local, tz


@expense_router.get("/export/csv")
async def export_expenses_csv(
    start: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    timezone: Optional[str] = Query(None, description="Timezone (IANA format)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export user's expenses as CSV file"""
    user_tz = timezone or getattr(current_user, 'timezone', None) or 'UTC'
    try:
        start_local, end_local, tz = _parse_date_range_spec(start, end, user_tz)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    from datetime import timezone as dt_tz
    # Normalize to UTC-naive boundaries for DB comparison (assumes DB stores naive UTC or naive local)
    def to_utc_naive(dt):
        if not dt:
            return None
        return dt.astimezone(dt_tz.utc).replace(tzinfo=None)

    start_bound = to_utc_naive(start_local)
    end_bound = to_utc_naive(end_local)

    qry = db.query(Expense).filter(Expense.user_id == current_user.id)
    if start_bound:
        qry = qry.filter(Expense.expense_date >= start_bound)
    if end_bound:
        qry = qry.filter(Expense.expense_date <= end_bound)
    expenses = qry.order_by(Expense.expense_date.desc()).all()
    
    # Get category names for display
    categories = {cat.id: cat.name for cat in db.query(ExpenseCategory).all()}
    
    # Create CSV content
    csv_content = "Date,Description,Amount,Currency,Vendor,Category,Payment Method,Receipt URL\n"
    
    for expense in expenses:
        category_name = categories.get(expense.category_id, "Uncategorized") if expense.category_id else "Uncategorized"
        amount_formatted = format_currency(expense.amount_cents, expense.currency)
        
        # Escape commas and quotes in CSV
        description = f'"{expense.description.replace("\"", "\"\"")}"' if ',' in expense.description or '"' in expense.description else expense.description
        vendor = f'"{expense.vendor.replace("\"", "\"\"")}"' if expense.vendor and (',' in expense.vendor or '"' in expense.vendor) else (expense.vendor or "")
        
        csv_content += f"{expense.expense_date.strftime('%Y-%m-%d')},{description},{amount_formatted},{expense.currency},{vendor},{category_name},{expense.payment_method or ''},{expense.receipt_url or ''}\n"
    
    # Generate standardized filename with user's timezone
    user_timezone = user_tz
    filename = generate_filename(
        'expenses',
        current_user.email,
        user_timezone,
        date_start=start_local.strftime('%Y-%m-%d') if start_local else None,
        date_end=end_local.strftime('%Y-%m-%d') if end_local else None,
    )
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "text/csv; charset=utf-8"
        }
    )


# Voice expense models
class VoiceExpenseRequest(BaseModel):
    transcript: str
    source: str = "dashboard_voice"


class VoiceExpenseResponse(BaseModel):
    success: bool
    expense: Optional[ExpenseResponse] = None
    error: Optional[str] = None
    parsed: Optional[dict] = None


# Construction job patterns for voice parsing
JOB_PATTERNS = [
    r"for (?:the )?([a-zA-Z]+(?:\s+[a-zA-Z]+)*?)\s+(?:job|project)",
    r"on (?:the )?([a-zA-Z]+(?:\s+[a-zA-Z]+)*?)\s+(?:job|project|bathroom|kitchen|house|roof|deck)",
    r"([a-zA-Z]+)\s+(bathroom|kitchen|house|roof|deck|basement|garage|addition|remodel)",
    r"([a-zA-Z]+(?:\s+[a-zA-Z]+)*?)\s+(?:job|project)(?:\s|$)"
]

# Construction vendor mappings
CONSTRUCTION_VENDORS = {
    'home depot': {'category': 'Materials - Hardware', 'common': True},
    'lowes': {'category': 'Materials - Hardware', 'common': True},
    'menards': {'category': 'Materials - Hardware', 'common': True},
    'ace hardware': {'category': 'Materials - Hardware', 'common': True},
    'lumber yard': {'category': 'Materials - Lumber', 'common': True},
    'electrical supply': {'category': 'Materials - Electrical', 'common': True},
    'plumbing supply': {'category': 'Materials - Plumbing', 'common': True},
    'gas station': {'category': 'Equipment - Fuel', 'common': True},
    'equipment rental': {'category': 'Equipment - Rental', 'common': True}
}


def parse_voice_expense(transcript: str) -> dict:
    """Parse voice transcript into expense data"""
    text = transcript.lower()
    
    # Extract job name
    job_name = None
    for pattern in JOB_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            job_name = match.group(1).strip()
            # Capitalize each word
            job_name = ' '.join(word.capitalize() for word in job_name.split())
            break
    
    # Extract amount
    amount = None
    
    # First try standard patterns
    amount_patterns = [
        r'\$(\d+(?:\.\d{2})?)',  # $123.45
        r'(\d+(?:\.\d{2})?)\s*dollars?',  # 123 dollars
        r'(\d+)\s*(?:bucks?|dollars?)',  # 45 bucks
    ]
    
    for pattern in amount_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount = float(match.group(1))
            break
    
    # Handle compound word numbers like "three forty seven" or "twenty three fifty"
    if not amount:
        # Word to number mappings
        word_numbers = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
            'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
            'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
            'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30,
            'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
            'eighty': 80, 'ninety': 90, 'hundred': 100, 'thousand': 1000
        }
        
        # Look for patterns like "three forty seven" (347) or "twenty three fifty" (23.50)
        compound_pattern = r'(' + '|'.join(word_numbers.keys()) + r')\s+(' + '|'.join(word_numbers.keys()) + r')(?:\s+(' + '|'.join(word_numbers.keys()) + r'))?'
        match = re.search(compound_pattern, text)
        if match:
            parts = [g for g in match.groups() if g]
            if len(parts) == 3:
                # Pattern like "three forty seven" = 347
                first = word_numbers.get(parts[0], 0)
                second = word_numbers.get(parts[1], 0)
                third = word_numbers.get(parts[2], 0)
                
                # If middle is "hundred", multiply first by 100
                if parts[1] == 'hundred':
                    amount = first * 100 + third
                # If last is "fifty", treat as cents (x.50)
                elif parts[2] == 'fifty':
                    # For "twenty three fifty", first=20, second=3, third=50 -> 23.50
                    if first >= 20 and first <= 90:
                        amount = first + second + 0.50
                    else:
                        amount = second + 0.50
                else:
                    # Otherwise concatenate as digits (3-4-7 = 347)
                    amount = first * 100 + second + third
            elif len(parts) == 2:
                # Pattern like "twenty five" = 25
                first = word_numbers.get(parts[0], 0)
                second = word_numbers.get(parts[1], 0)
                
                # If "fifty" at end, treat as .50
                if parts[1] == 'fifty' and first < 100:
                    amount = first + 0.50
                # If first is tens (twenty, thirty, etc)
                elif first >= 20 and first <= 90 and second < 10:
                    amount = first + second
                else:
                    amount = first * 10 + second
    
    # If still no amount, try simple word numbers
    if not amount:
        for word, value in word_numbers.items():
            if word in text and value >= 10:  # Only match tens and above as standalone
                amount = value
                break
    
    # Extract vendor
    vendor = None
    category = 'Materials - Other'
    
    # Check known construction vendors
    for vendor_name, info in CONSTRUCTION_VENDORS.items():
        if vendor_name in text:
            vendor = ' '.join(word.capitalize() for word in vendor_name.split())
            category = info['category']
            break
    
    # If no known vendor, try patterns
    if not vendor:
        vendor_patterns = [
            r'(?:at|from)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)*?)(?:\s+for|\s+on|\s|$)',
            r'([a-zA-Z]+(?:\s+[a-zA-Z]+)*?)\s+(?:receipt|purchase)'
        ]
        
        for pattern in vendor_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                vendor = match.group(1).strip()
                vendor = ' '.join(word.capitalize() for word in vendor.split())
                break
    
    if not vendor:
        vendor = 'Unknown'
    
    # Auto-categorize based on keywords
    category_keywords = {
        'Materials - Lumber': ['lumber', 'wood', 'plywood', '2x4', '2x6', 'boards'],
        'Materials - Electrical': ['wire', 'outlet', 'breaker', 'electrical'],
        'Materials - Plumbing': ['pipe', 'fitting', 'valve', 'plumbing'],
        'Equipment - Fuel': ['gas', 'diesel', 'fuel'],
        'Labor - Crew': ['lunch', 'food', 'meal', 'crew'],
        'Labor - Subcontractors': ['subcontractor', 'sub', 'contractor']
    }
    
    for cat, keywords in category_keywords.items():
        if any(keyword in text for keyword in keywords):
            category = cat
            break
    
    return {
        'amount': amount,
        'vendor': vendor,
        'category': category,
        'job_name': job_name,
        'description': transcript,
        'confidence': {
            'amount': 0.9 if amount else 0,
            'vendor': 0.95 if vendor != 'Unknown' else 0.3,
            'job': 0.9 if job_name else 0,
            'category': 0.85
        }
    }


@expense_router.post("/voice", response_model=VoiceExpenseResponse)
async def create_voice_expense(
    request: VoiceExpenseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create expense from voice transcript"""
    try:
        # Parse the transcript
        parsed = parse_voice_expense(request.transcript)
        
        # Check if we have the minimum required data
        if not parsed['amount']:
            return VoiceExpenseResponse(
                success=False,
                error="Could not detect amount",
                parsed={
                    'vendor': parsed['vendor'],
                    'job_name': parsed['job_name']
                }
            )
        
        # Find the category ID
        category_name = parsed['category']
        category = db.query(ExpenseCategory).filter(ExpenseCategory.name == category_name).first()
        
        # If category doesn't exist, use default
        if not category:
            category = db.query(ExpenseCategory).filter(ExpenseCategory.name == "Materials - Other").first()
            if not category:
                # Create it if it doesn't exist
                category = ExpenseCategory(name="Materials - Other", description="Other materials and supplies")
                db.add(category)
                db.commit()
        
        # Create the expense
        new_expense = Expense(
            user_id=current_user.id,
            expense_date=datetime.now(),
            description=parsed['description'],
            amount_cents=int(parsed['amount'] * 100),  # Convert to cents
            currency="USD",
            vendor=parsed['vendor'],
            category_id=category.id if category else None,
            job_name=parsed['job_name'],
            payment_method="Cash",  # Default for voice entries
            auto_categorized=True,
            confidence_score=int(parsed['confidence']['category'] * 100)
        )
        
        db.add(new_expense)
        db.commit()
        db.refresh(new_expense)
        
        # Build response
        response_expense = ExpenseResponse(
            id=new_expense.id,
            expense_date=new_expense.expense_date,
            description=new_expense.description,
            amount_cents=new_expense.amount_cents,
            currency=new_expense.currency,
            vendor=new_expense.vendor,
            category_id=new_expense.category_id,
            category_name=category.name if category else None,
            job_name=new_expense.job_name,
            receipt_url=new_expense.receipt_url,
            payment_method=new_expense.payment_method,
            created_at=new_expense.created_at,
            updated_at=new_expense.updated_at
        )
        
        # Add confidence scores to response
        response_dict = response_expense.model_dump()
        response_dict['confidence'] = parsed['confidence']
        
        # Broadcast update via WebSocket
        expense_data = {
            "id": new_expense.id,
            "description": new_expense.description,
            "amount_cents": new_expense.amount_cents,
            "vendor": new_expense.vendor,
            "job_name": new_expense.job_name,
            "source": "voice",
            "created_at": new_expense.created_at.isoformat() if new_expense.created_at else None
        }
        asyncio.create_task(broadcast_expense_update(current_user.email, expense_data))
        
        # Increment business metric
        VOICE_EXPENSES_SUCCESS.inc()
        
        # Check for alerts
        job_id = int(new_expense.job_id) if new_expense.job_id else None
        asyncio.create_task(AlertChecker.check_and_create_alerts(current_user.id, job_id, db))
        
        return VoiceExpenseResponse(
            success=True,
            expense=response_dict
        )
    
    except Exception as e:
        # Log the error
        print(f"Voice expense creation failed: {str(e)}")
        
        # Rollback any database changes
        db.rollback()
        
        # Increment business metric
        VOICE_EXPENSES_FAILED.inc()
        
        return VoiceExpenseResponse(
            success=False,
            error="Failed to create expense. Please try again."
        )
