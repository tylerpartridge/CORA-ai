#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/chat.py
🎯 PURPOSE: Basic job query chat functionality
📝 STATUS: ACTIVE - Handles job-specific queries at /api/chat
🔗 IMPORTS: FastAPI, models, NLP utilities
📤 EXPORTS: chat_router
ℹ️ NOTE: This is the basic chat. For full CORA chat, see cora_chat_enhanced.py
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List, Dict
import re

from models import get_db, Job, Expense, User, AnalyticsLog
from dependencies.auth import get_current_user

# Create router
chat_router = APIRouter(
    prefix="/api/chat",
    tags=["chat"]
)

# Request/Response models
class JobQueryRequest(BaseModel):
    query: str
    context: str = "voice"  # voice or chat

class JobInfo(BaseModel):
    name: str
    status: str
    quoted: float
    spent: float
    remaining: float
    margin_percent: float
    days_active: int
    last_expense: str

class JobQueryResponse(BaseModel):
    job_found: bool
    job: Optional[JobInfo] = None
    response: str
    alerts: List[Dict] = []

# Job query patterns
JOB_QUERY_PATTERNS = [
    # "How's the Johnson job doing?"
    r"how(?:'s|s| is) (?:the )?([a-zA-Z]+(?:\s+[a-zA-Z]+)*?)\s*(?:job|project)?(?:\s+doing)?",
    # "Show me the Smith kitchen"
    r"show (?:me )?(?:the )?([a-zA-Z]+(?:\s+[a-zA-Z]+)*?)\s*(?:job|project|bathroom|kitchen|house|roof|deck)?",
    # "What's my profit on Miller house"
    r"what(?:'s|s| is) (?:my |the )?(?:profit|margin|status) (?:on |for )?(?:the )?([a-zA-Z]+(?:\s+[a-zA-Z]+)*)",
    # "Johnson bathroom status"
    r"([a-zA-Z]+(?:\s+[a-zA-Z]+)*?)\s+(?:status|profit|margin|update)",
    # Direct job name
    r"^([a-zA-Z]+(?:\s+[a-zA-Z]+)*)$"
]

def extract_job_name(query: str) -> Optional[str]:
    """Extract job name from natural language query"""
    query_lower = query.lower().strip()
    
    for pattern in JOB_QUERY_PATTERNS:
        match = re.search(pattern, query_lower, re.IGNORECASE)
        if match:
            job_name = match.group(1).strip()
            # Capitalize each word
            return ' '.join(word.capitalize() for word in job_name.split())
    
    return None

def format_job_response(job: Job, expenses: List[Expense], query: str) -> str:
    """Format natural language response about job status"""
    
    # Calculate totals
    total_spent = sum(e.amount_cents for e in expenses) / 100
    quoted = job.quoted_amount or 0
    remaining = quoted - total_spent
    margin_percent = ((quoted - total_spent) / quoted * 100) if quoted > 0 else 0
    
    # Determine response tone based on margin
    if margin_percent < 10:
        tone = "urgent"
        status = "needs immediate attention"
        emoji = "⚠️"
    elif margin_percent < 20:
        tone = "warning"
        status = "is getting tight"
        emoji = "⚡"
    elif margin_percent > 40:
        tone = "great"
        status = "is doing great"
        emoji = "✅"
    else:
        tone = "good"
        status = "is on track"
        emoji = "👍"
    
    # Check query intent
    if "profit" in query.lower() or "margin" in query.lower():
        # Focus on profitability
        response = f"{emoji} {job.job_name} has a {margin_percent:.1f}% profit margin. "
        response += f"You've spent ${total_spent:,.2f} of the ${quoted:,.2f} budget"
        if margin_percent < 20:
            response += f" - watch your costs carefully!"
        elif margin_percent > 40:
            response += f" - excellent work!"
        else:
            response += "."
    
    elif "status" in query.lower() or "update" in query.lower():
        # General status update
        response = f"{job.job_name} {status}! "
        response += f"Budget: ${quoted:,.2f}, Spent: ${total_spent:,.2f}, "
        response += f"Remaining: ${remaining:,.2f} ({margin_percent:.1f}% margin)"
    
    else:
        # Default friendly response
        response = f"The {job.job_name} {status}! "
        response += f"You've spent ${total_spent:,.2f} of the ${quoted:,.2f} budget, "
        response += f"leaving ${remaining:,.2f}. "
        
        if margin_percent < 20:
            response += f"Your margin is {margin_percent:.1f}% - below the 20% target."
        elif margin_percent > 30:
            response += f"Your margin is {margin_percent:.1f}% - well above target!"
        else:
            response += f"Your margin is {margin_percent:.1f}% - right on target."
    
    return response

@chat_router.post("/job-query", response_model=JobQueryResponse)
async def query_job_status(
    request: JobQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Natural language query about job status and profitability"""
    
    # Extract job name from query
    job_name = extract_job_name(request.query)
    
    if not job_name:
        response = JobQueryResponse(
            job_found=False,
            response="I couldn't understand which job you're asking about. Try saying something like 'How's the Johnson bathroom job doing?'",
            alerts=[]
        )
    else:
        # Find matching job (case-insensitive partial match)
        jobs = db.query(Job).filter(
            Job.user_id == current_user.id,
            func.lower(Job.job_name).contains(job_name.lower())
        ).all()
        
        if not jobs:
            response = JobQueryResponse(
                job_found=False,
                response=f"I couldn't find a job matching '{job_name}'. Check your active jobs in the dashboard.",
                alerts=[]
            )
        else:
            # Use the first match (could enhance with better matching logic)
            job = jobs[0]
            
            # Get job expenses
            expenses = db.query(Expense).filter(
                Expense.user_id == current_user.id,
                func.lower(Expense.job_name) == func.lower(job.job_name)
            ).all()
            
            # Calculate metrics
            total_spent = sum(e.amount_cents for e in expenses) / 100
            quoted = job.quoted_amount or 0
            remaining = quoted - total_spent
            margin_percent = ((quoted - total_spent) / quoted * 100) if quoted > 0 else 0
            
            # Calculate days active
            from datetime import datetime
            days_active = (datetime.now() - job.start_date).days if job.start_date else 0
            
            # Get last expense time
            last_expense = "No expenses yet"
            if expenses:
                latest = max(expenses, key=lambda e: e.created_at)
                time_diff = datetime.now() - latest.created_at
                if time_diff.days == 0:
                    hours = time_diff.seconds // 3600
                    if hours == 0:
                        last_expense = "Just now"
                    elif hours == 1:
                        last_expense = "1 hour ago"
                    else:
                        last_expense = f"{hours} hours ago"
                elif time_diff.days == 1:
                    last_expense = "Yesterday"
                else:
                    last_expense = f"{time_diff.days} days ago"
            
            # Build response
            job_info = JobInfo(
                name=job.job_name,
                status=job.status,
                quoted=quoted,
                spent=total_spent,
                remaining=remaining,
                margin_percent=margin_percent,
                days_active=days_active,
                last_expense=last_expense
            )
            
            # Check for alerts
            alerts = []
            if margin_percent < 20 and margin_percent >= 10:
                alerts.append({
                    "type": "low_margin",
                    "severity": "warning",
                    "message": f"Margin on {job.job_name} is below 20%"
                })
            elif margin_percent < 10:
                alerts.append({
                    "type": "low_margin", 
                    "severity": "urgent",
                    "message": f"URGENT: Margin on {job.job_name} is below 10%"
                })
            
            if remaining < 0:
                alerts.append({
                    "type": "over_budget",
                    "severity": "urgent",
                    "message": f"{job.job_name} is over budget by ${abs(remaining):,.2f}"
                })
            
            # Format natural language response
            response_text = format_job_response(job, expenses, request.query)
            
            response = JobQueryResponse(
                job_found=True,
                job=job_info,
                response=response_text,
                alerts=alerts
            )
    
    # Log analytics
    status = "success" if response.job_found else "failure"
    analytics = AnalyticsLog(
        user_id=current_user.id,
        query=request.query,
        response_status=status
    )
    db.add(analytics)
    db.commit()
    return response