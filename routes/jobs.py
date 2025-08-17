#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/jobs.py
🎯 PURPOSE: Construction job management routes
🔗 IMPORTS: FastAPI, models, services
📤 EXPORTS: job_router
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from typing import List, Optional

from models import get_db, Job, JobNote, Expense, User
from dependencies.auth import get_current_user
from middleware.monitoring import JOBS_CREATED, JOBS_COMPLETED
from services.alert_checker import AlertChecker
from utils.error_constants import ErrorMessages, STATUS_NOT_FOUND, STATUS_BAD_REQUEST
import asyncio

# Create router
job_router = APIRouter(
    prefix="/api/jobs",
    tags=["jobs"]
)

# Pydantic models
class JobCreate(BaseModel):
    job_id: str
    job_name: str
    customer_name: Optional[str] = None
    job_address: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    quoted_amount: Optional[float] = None
    status: str = "active"

class JobUpdate(BaseModel):
    job_name: Optional[str] = None
    customer_name: Optional[str] = None
    job_address: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    quoted_amount: Optional[float] = None
    status: Optional[str] = None

class JobNoteCreate(BaseModel):
    note_type: Optional[str] = None  # change_order, delay, issue, general
    note: str

class JobResponse(BaseModel):
    id: int
    job_id: str
    job_name: str
    customer_name: Optional[str]
    job_address: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    quoted_amount: Optional[float]
    status: str
    created_at: datetime
    updated_at: datetime
    total_costs: float = 0
    profit: float = 0
    profit_margin_percent: float = 0
    
    class Config:
        from_attributes = True

class JobProfitabilityResponse(BaseModel):
    job_id: int
    job_name: str
    customer_name: Optional[str]
    quoted_amount: Optional[float]
    total_costs: float
    profit: float
    profit_margin_percent: float
    expense_breakdown: dict
    status: str

class JobNoteResponse(BaseModel):
    id: int
    note_type: Optional[str]
    note: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Routes
@job_router.get("/", response_model=List[JobResponse])
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all jobs for the current user (optimized with ordering)"""
    query = db.query(Job).filter(Job.user_id == current_user.id).order_by(Job.created_at.desc())
    
    if status:
        query = query.filter(Job.status == status)
    
    jobs = query.offset(skip).limit(limit).all()
    
    # Calculate profitability for each job using materialized views
    from utils.materialized_views import get_job_profitability_optimized
    
    job_responses = []
    for job in jobs:
        # Get materialized view profitability data
        profitability = get_job_profitability_optimized(db, current_user.id, job.job_id)
        
        if profitability.get("status") == "error":
            # Fallback to basic calculation
            total_costs = db.query(func.sum(Expense.amount_cents)).filter(
                Expense.user_id == current_user.id,
                Expense.job_name == job.job_name
            ).scalar() or 0
            total_costs = total_costs / 100.0
        else:
            total_costs = profitability.get("total_costs", 0)
        
        job_dict = job.__dict__.copy()
        job_dict['total_costs'] = total_costs
        job_dict['profit'] = float(job.quoted_amount or 0) - total_costs
        job_dict['profit_margin_percent'] = (
            ((float(job.quoted_amount or 0) - total_costs) / float(job.quoted_amount) * 100)
            if job.quoted_amount and job.quoted_amount > 0 else 0
        )
        
        job_responses.append(JobResponse(**job_dict))
    
    return job_responses

@job_router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific job by ID"""
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=STATUS_NOT_FOUND, detail=ErrorMessages.not_found("job"))
    
    # Get total costs using materialized view
    from utils.materialized_views import get_job_profitability_optimized
    
    profitability = get_job_profitability_optimized(db, current_user.id, job.job_id)
    if profitability.get("status") == "success":
        total_costs = profitability.get("total_costs", 0)
    else:
        # Fallback to basic calculation
        total_costs = db.query(func.sum(Expense.amount_cents)).filter(
            Expense.user_id == current_user.id,
            Expense.job_name == job.job_name
        ).scalar() or 0
        total_costs = total_costs / 100.0
    
    job_dict = job.__dict__.copy()
    job_dict['total_costs'] = total_costs
    job_dict['profit'] = float(job.quoted_amount or 0) - total_costs
    job_dict['profit_margin_percent'] = (
        ((float(job.quoted_amount or 0) - total_costs) / float(job.quoted_amount) * 100)
        if job.quoted_amount and job.quoted_amount > 0 else 0
    )
    
    return JobResponse(**job_dict)

@job_router.get("/by-name/{job_name}/profitability", response_model=JobProfitabilityResponse)
async def get_job_profitability_by_name(
    job_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get job profitability by job name (for CORA chat queries)"""
    # Find job by name
    job = db.query(Job).filter(
        Job.user_id == current_user.id,
        func.lower(Job.job_name) == job_name.lower()
    ).first()
    
    # If no formal job exists, still calculate based on expenses
    if job:
        job_id = job.id
        job_name_actual = job.job_name
        customer_name = job.customer_name
        quoted_amount = job.quoted_amount
        status = job.status
    else:
        job_id = 0
        job_name_actual = job_name
        customer_name = None
        quoted_amount = None
        status = "informal"
    
    # Get all expenses for this job
    expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id,
        func.lower(Expense.job_name) == job_name.lower()
    ).all()
    
    # Calculate totals by category
    expense_breakdown = {}
    total_costs = 0
    
    for expense in expenses:
        category_name = "Uncategorized"
        if expense.category:
            category_name = expense.category.name
        
        if category_name not in expense_breakdown:
            expense_breakdown[category_name] = 0
        
        amount = expense.amount_cents / 100.0
        expense_breakdown[category_name] += amount
        total_costs += amount
    
    # Calculate profit
    profit = float(quoted_amount or 0) - total_costs
    profit_margin_percent = (
        (profit / float(quoted_amount) * 100)
        if quoted_amount and float(quoted_amount) > 0 else 0
    )
    
    return JobProfitabilityResponse(
        job_id=job_id,
        job_name=job_name_actual,
        customer_name=customer_name,
        quoted_amount=quoted_amount,
        total_costs=total_costs,
        profit=profit,
        profit_margin_percent=profit_margin_percent,
        expense_breakdown=expense_breakdown,
        status=status
    )

@job_router.post("/", response_model=JobResponse)
async def create_job(
    job: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new job"""
    # Check if job_id already exists
    existing = db.query(Job).filter(Job.job_id == job.job_id).first()
    if existing:
        raise HTTPException(status_code=STATUS_BAD_REQUEST, detail=ErrorMessages.already_exists("job ID"))
    
    db_job = Job(
        **job.dict(),
        user_id=current_user.id
    )
    
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    # Increment business metric
    JOBS_CREATED.inc()
    
    # Check for alerts
    asyncio.create_task(AlertChecker.check_and_create_alerts(current_user.id, db_job.id, db))
    
    # Return with profitability info
    job_dict = db_job.__dict__.copy()
    job_dict['total_costs'] = 0
    job_dict['profit'] = float(db_job.quoted_amount or 0)
    job_dict['profit_margin_percent'] = 100 if db_job.quoted_amount else 0
    
    return JobResponse(**job_dict)

@job_router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: int,
    job_update: JobUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a job"""
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=STATUS_NOT_FOUND, detail=ErrorMessages.not_found("job"))
    
    # Update fields
    for field, value in job_update.dict(exclude_unset=True).items():
        setattr(job, field, value)
    
    # Check if job was completed
    if job_update.status == "completed" and job.status != "completed":
        JOBS_COMPLETED.inc()
    
    db.commit()
    
    # Check for alerts
    asyncio.create_task(AlertChecker.check_and_create_alerts(current_user.id, job.id, db))
    db.refresh(job)
    
    # Get profitability info
    total_costs = db.query(func.sum(Expense.amount_cents)).filter(
        Expense.user_id == current_user.id,
        Expense.job_name == job.job_name
    ).scalar() or 0
    
    total_costs = total_costs / 100.0
    
    job_dict = job.__dict__.copy()
    job_dict['total_costs'] = total_costs
    job_dict['profit'] = float(job.quoted_amount or 0) - total_costs
    job_dict['profit_margin_percent'] = (
        ((float(job.quoted_amount or 0) - total_costs) / float(job.quoted_amount) * 100)
        if job.quoted_amount and job.quoted_amount > 0 else 0
    )
    
    return JobResponse(**job_dict)

@job_router.delete("/{job_id}")
async def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a job"""
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=STATUS_NOT_FOUND, detail=ErrorMessages.not_found("job"))
    
    db.delete(job)
    db.commit()
    
    return {"message": "Job deleted successfully"}

@job_router.post("/{job_id}/notes", response_model=JobNoteResponse)
async def add_job_note(
    job_id: int,
    note: JobNoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a note to a job"""
    # Verify job exists and belongs to user
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=STATUS_NOT_FOUND, detail=ErrorMessages.not_found("job"))
    
    db_note = JobNote(
        job_id=job_id,
        user_id=current_user.id,
        **note.dict()
    )
    
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    return db_note

@job_router.get("/{job_id}/notes", response_model=List[JobNoteResponse])
async def get_job_notes(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all notes for a job"""
    # Verify job exists and belongs to user
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=STATUS_NOT_FOUND, detail=ErrorMessages.not_found("job"))
    
    notes = db.query(JobNote).filter(JobNote.job_id == job_id).all()
    return notes

@job_router.get("/search/{search_term}")
async def search_jobs(
    search_term: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search jobs by name or customer"""
    jobs = db.query(Job).filter(
        Job.user_id == current_user.id,
        (func.lower(Job.job_name).contains(search_term.lower()) |
         func.lower(Job.customer_name).contains(search_term.lower()))
    ).all()
    
    return [{"id": job.id, "job_name": job.job_name, "customer_name": job.customer_name} for job in jobs]