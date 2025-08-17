#!/usr/bin/env python3
"""
Business Task Automation API Routes
Provides endpoints for managing and executing automated business tasks
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

from models import get_db, User
from dependencies.auth import get_current_user
from services.business_task_automation import BusinessTaskAutomation
from services.task_scheduler import task_scheduler, get_scheduler_status

router = APIRouter(
    prefix="/api/business-tasks",
    tags=["business-tasks"]
)

class TaskExecutionRequest(BaseModel):
    task_name: str

class TaskExecutionResponse(BaseModel):
    success: bool
    task_name: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.get("/scheduled")
async def get_scheduled_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get list of scheduled tasks for the current user"""
    try:
        task_automation = BusinessTaskAutomation(current_user, db)
        return task_automation.get_scheduled_tasks()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get scheduled tasks: {str(e)}")

@router.get("/status/{task_name}")
async def get_task_status(
    task_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get status of a specific task for the current user"""
    try:
        task_automation = BusinessTaskAutomation(current_user, db)
        status = task_automation.get_task_status(task_name)
        
        if status is None:
            raise HTTPException(status_code=404, detail=f"Task '{task_name}' not found")
        
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")

@router.post("/execute", response_model=TaskExecutionResponse)
async def execute_task(
    request: TaskExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TaskExecutionResponse:
    """Execute a specific task for the current user"""
    try:
        task_automation = BusinessTaskAutomation(current_user, db)
        result = await task_automation.execute_task(request.task_name)
        
        return TaskExecutionResponse(
            success=result.get('success', False),
            task_name=request.task_name,
            result=result.get('result'),
            error=result.get('error')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute task: {str(e)}")

@router.get("/health")
async def get_automation_health(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get automation system health for the current user"""
    try:
        task_automation = BusinessTaskAutomation(current_user, db)
        return task_automation.get_automation_health()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get automation health: {str(e)}")

@router.post("/cancel/{task_name}")
async def cancel_task(
    task_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Cancel a running task for the current user"""
    try:
        task_automation = BusinessTaskAutomation(current_user, db)
        cancelled = await task_automation.cancel_task(task_name)
        
        if cancelled:
            return {"success": True, "message": f"Task '{task_name}' cancelled successfully"}
        else:
            return {"success": False, "message": f"Task '{task_name}' not found or not running"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel task: {str(e)}")

# Admin endpoints for system-wide task management
@router.get("/admin/scheduler-status")
async def get_scheduler_status_admin() -> Dict[str, Any]:
    """Get system-wide task scheduler status (admin only)"""
    try:
        return get_scheduler_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get scheduler status: {str(e)}")

@router.post("/admin/execute/{task_name}")
async def execute_task_system_wide(
    task_name: str
) -> Dict[str, Any]:
    """Execute a task for all users (admin only)"""
    try:
        result = task_scheduler.manual_execute(task_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute system-wide task: {str(e)}")

@router.get("/admin/history")
async def get_task_history(
    task_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get task execution history (admin only)"""
    try:
        return task_scheduler.get_task_history(task_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task history: {str(e)}")

@router.post("/admin/start-scheduler")
async def start_scheduler_admin() -> Dict[str, Any]:
    """Start the task scheduler (admin only)"""
    try:
        task_scheduler.start_scheduler()
        return {"success": True, "message": "Task scheduler started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start scheduler: {str(e)}")

@router.post("/admin/stop-scheduler")
async def stop_scheduler_admin() -> Dict[str, Any]:
    """Stop the task scheduler (admin only)"""
    try:
        task_scheduler.stop_scheduler()
        return {"success": True, "message": "Task scheduler stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop scheduler: {str(e)}")

# Task templates endpoint
@router.get("/templates")
async def get_task_templates() -> Dict[str, Any]:
    """Get available task templates"""
    try:
        with open('tools/config/business_task_templates.json', 'r') as f:
            import json
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load task templates: {str(e)}") 