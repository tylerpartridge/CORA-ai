# 🎯 Cursor Execution Tasks - Phase 1 Core Functionality

## Task 1: PostgreSQL Migration (PRIORITY 1)

### Objective
Migrate from SQLite to PostgreSQL for production readiness

### Specific Implementation Steps

#### 1.1 Set up PostgreSQL Database
```bash
# DigitalOcean Managed Database recommended
# Budget: $15/month for basic cluster
```

**Files to modify:**
- `/CORA/models/base.py` - Update database URL
- `/CORA/app.py` - Update connection string
- Create `/CORA/alembic.ini` for migrations
- Create `/CORA/migrations/` directory structure

**Exact changes needed:**
```python
# In models/base.py, replace:
SQLALCHEMY_DATABASE_URL = "sqlite:///./cora.db"

# With:
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost/coradb"
)

# Add connection pooling:
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

#### 1.2 Create Migration Scripts
```bash
# Commands to run:
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Success Criteria
- [ ] PostgreSQL database created on DigitalOcean
- [ ] All models successfully migrated
- [ ] Connection pooling configured
- [ ] Automated backups enabled
- [ ] Environment variables set

---

## Task 2: Implement Expense CRUD Operations (PRIORITY 2)

### Objective
Create working expense tracking API endpoints

### 2.1 Complete Expense Routes Implementation

**File: `/CORA/routes/expenses.py`**

Currently this file only has stubs. Implement:

```python
@router.post("/expenses", response_model=ExpenseResponse)
async def create_expense(
    expense: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new expense with AI categorization"""
    # Implementation needed:
    # 1. Validate expense data
    # 2. Call AI categorization
    # 3. Save to database
    # 4. Return response
    
@router.get("/expenses", response_model=List[ExpenseResponse])
async def list_expenses(
    skip: int = 0,
    limit: int = 100,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's expenses with filtering"""
    # Implementation needed

@router.put("/expenses/{expense_id}")
async def update_expense(
    expense_id: int,
    expense_update: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an expense"""
    # Implementation needed

@router.delete("/expenses/{expense_id}")
async def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an expense"""
    # Implementation needed
```

### 2.2 Create Pydantic Schemas

**Create: `/CORA/schemas/expense.py`**

```python
from pydantic import BaseModel, validator
from datetime import date
from typing import Optional
from decimal import Decimal

class ExpenseBase(BaseModel):
    amount: Decimal
    description: str
    vendor: Optional[str] = None
    date: date
    receipt_url: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

class ExpenseUpdate(BaseModel):
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    vendor: Optional[str] = None
    category_id: Optional[int] = None
    date: Optional[date] = None
    
class ExpenseResponse(ExpenseBase):
    id: int
    user_id: int
    category_id: Optional[int]
    category_name: Optional[str]
    ai_confidence: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

### Success Criteria
- [ ] All CRUD endpoints working
- [ ] Input validation complete
- [ ] Error handling implemented
- [ ] Database transactions working
- [ ] Response schemas correct

---

## Task 3: Basic Dashboard UI (PRIORITY 3)

### Objective
Create functional expense dashboard

### 3.1 Create Dashboard Template

**Create: `/CORA/templates/dashboard.html`**

```html
{% extends "base.html" %}
{% block content %}
<div class="dashboard-container">
    <!-- Stats Summary -->
    <div class="stats-grid">
        <div class="stat-card">
            <h3>Total Expenses</h3>
            <p class="stat-value">${{ total_expenses }}</p>
        </div>
        <div class="stat-card">
            <h3>This Month</h3>
            <p class="stat-value">${{ monthly_expenses }}</p>
        </div>
        <div class="stat-card">
            <h3>Categories</h3>
            <p class="stat-value">{{ category_count }}</p>
        </div>
    </div>

    <!-- Add Expense Form -->
    <div class="add-expense-form">
        <h2>Add New Expense</h2>
        <form id="expense-form">
            <!-- Form implementation -->
        </form>
    </div>

    <!-- Expense List -->
    <div class="expense-list">
        <h2>Recent Expenses</h2>
        <table id="expenses-table">
            <!-- Table implementation -->
        </table>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script src="{{ url_for('static', path='/js/dashboard.js') }}"></script>
{% endblock %}
```

### 3.2 Create Dashboard Route

**Add to: `/CORA/routes/pages.py`**

```python
@router.get("/dashboard")
async def dashboard(request: Request, current_user: User = Depends(get_current_user)):
    # Fetch user's expenses
    # Calculate statistics
    # Render template
    return templates.TemplateResponse(
        "dashboard.html", 
        {
            "request": request,
            "user": current_user,
            "total_expenses": total,
            "monthly_expenses": monthly,
            "expenses": recent_expenses
        }
    )
```

### 3.3 Create Dashboard JavaScript

**Create: `/CORA/static/js/dashboard.js`**

```javascript
// Expense form submission
document.getElementById('expense-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    // Implementation needed
});

// Load expenses
async function loadExpenses() {
    // Fetch from API
    // Update table
}

// Delete expense
async function deleteExpense(id) {
    // Confirmation
    // API call
    // Refresh list
}
```

### Success Criteria
- [ ] Dashboard loads successfully
- [ ] Expense form works
- [ ] Expense list displays
- [ ] Statistics calculate correctly
- [ ] Mobile responsive

---

## Task 4: Database Operations Service (PRIORITY 4)

### Objective
Create reusable database service layer

### 4.1 Create Expense Service

**Create: `/CORA/services/expense_service.py`**

```python
from typing import List, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from models.expense import Expense
from models.user import User
from schemas.expense import ExpenseCreate, ExpenseUpdate

class ExpenseService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_expense(self, user_id: int, expense_data: ExpenseCreate) -> Expense:
        """Create new expense with AI categorization"""
        expense = Expense(
            user_id=user_id,
            amount_cents=int(expense_data.amount * 100),
            description=expense_data.description,
            vendor=expense_data.vendor,
            date=expense_data.date,
            receipt_url=expense_data.receipt_url
        )
        
        # TODO: Call AI categorization service
        # category, confidence = self.categorize_expense(expense)
        # expense.category_id = category.id
        # expense.ai_confidence = confidence
        
        self.db.add(expense)
        self.db.commit()
        self.db.refresh(expense)
        return expense
    
    def get_user_expenses(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        category_id: Optional[int] = None
    ) -> List[Expense]:
        """Get filtered expenses for user"""
        query = self.db.query(Expense).filter(Expense.user_id == user_id)
        
        if date_from:
            query = query.filter(Expense.date >= date_from)
        if date_to:
            query = query.filter(Expense.date <= date_to)
        if category_id:
            query = query.filter(Expense.category_id == category_id)
            
        return query.offset(skip).limit(limit).all()
    
    def update_expense(
        self,
        expense_id: int,
        user_id: int,
        update_data: ExpenseUpdate
    ) -> Optional[Expense]:
        """Update expense if owned by user"""
        expense = self.db.query(Expense).filter(
            and_(Expense.id == expense_id, Expense.user_id == user_id)
        ).first()
        
        if not expense:
            return None
            
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(expense, field, value)
            
        expense.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(expense)
        return expense
    
    def delete_expense(self, expense_id: int, user_id: int) -> bool:
        """Delete expense if owned by user"""
        expense = self.db.query(Expense).filter(
            and_(Expense.id == expense_id, Expense.user_id == user_id)
        ).first()
        
        if not expense:
            return False
            
        self.db.delete(expense)
        self.db.commit()
        return True
    
    def get_user_statistics(self, user_id: int) -> dict:
        """Calculate expense statistics for user"""
        # Implementation needed
        return {
            "total_expenses": 0,
            "monthly_expenses": 0,
            "category_breakdown": {},
            "daily_average": 0
        }
```

### Success Criteria
- [ ] Service layer working
- [ ] All database operations tested
- [ ] Error handling complete
- [ ] Transactions properly managed
- [ ] Performance optimized

---

## Execution Order for Cursor

1. **First**: PostgreSQL Migration (blocking everything else)
2. **Second**: Expense Service Layer (foundation for API)
3. **Third**: Complete CRUD Endpoints (API functionality)
4. **Fourth**: Dashboard UI (user interface)

## Testing Requirements

After each task:
- Unit tests for new functions
- Integration tests for API endpoints
- Manual testing of UI components
- Performance testing with sample data

---

**These tasks are ready for immediate execution. Each has specific file paths, code snippets, and clear success criteria.**