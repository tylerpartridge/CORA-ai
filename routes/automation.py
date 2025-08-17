"""
Business Task Automation API Routes
Provides endpoints for automated business task management
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime
import logging

from models import get_db, User
from services.business_task_automation import BusinessTaskAutomation
from dependencies.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# Store active automation instances
active_automations = {}

@router.get("/tasks")
async def get_scheduled_tasks(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get all scheduled automation tasks for the current user
    """
    try:
        # Get or create automation instance for user
        if user.id not in active_automations:
            active_automations[user.id] = BusinessTaskAutomation(user, db)
        
        automation = active_automations[user.id]
        tasks = automation.get_scheduled_tasks()
        
        return {
            "success": True,
            "tasks": tasks,
            "count": len(tasks),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to get scheduled tasks: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve scheduled tasks: {str(e)}"
        )

@router.post("/tasks/{task_name}/execute")
async def execute_task(
    task_name: str,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Execute a specific automation task
    """
    try:
        # Get or create automation instance
        if user.id not in active_automations:
            active_automations[user.id] = BusinessTaskAutomation(user, db)
        
        automation = active_automations[user.id]
        
        # Execute task asynchronously
        result = await automation.execute_task(task_name)
        
        # Log execution
        logger.info(f"Task {task_name} executed for user {user.id}: {result.get('success')}")
        
        return result
    
    except Exception as e:
        logger.error(f"Failed to execute task {task_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute task: {str(e)}"
        )

@router.get("/tasks/{task_name}/status")
async def get_task_status(
    task_name: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get the status of a specific task
    """
    try:
        if user.id not in active_automations:
            return {
                "success": False,
                "message": "No automation instance found for user"
            }
        
        automation = active_automations[user.id]
        status = automation.get_task_status(task_name)
        
        if status:
            return {
                "success": True,
                "task_name": task_name,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": f"No status found for task '{task_name}'"
            }
    
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve task status: {str(e)}"
        )

@router.delete("/tasks/{task_name}/cancel")
async def cancel_task(
    task_name: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Cancel a running task
    """
    try:
        if user.id not in active_automations:
            return {
                "success": False,
                "message": "No automation instance found for user"
            }
        
        automation = active_automations[user.id]
        cancelled = await automation.cancel_task(task_name)
        
        if cancelled:
            return {
                "success": True,
                "message": f"Task '{task_name}' cancelled successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": f"Task '{task_name}' not found or not running"
            }
    
    except Exception as e:
        logger.error(f"Failed to cancel task: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel task: {str(e)}"
        )

@router.get("/health")
async def get_automation_health(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get health status of the automation system
    """
    try:
        # Get or create automation instance
        if user.id not in active_automations:
            active_automations[user.id] = BusinessTaskAutomation(user, db)
        
        automation = active_automations[user.id]
        health = automation.get_automation_health()
        
        return {
            "success": True,
            "health": health,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to get automation health: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve automation health: {str(e)}"
        )

@router.post("/tasks/execute-all")
async def execute_all_tasks(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Execute all auto-execute tasks for the user
    """
    try:
        # Get or create automation instance
        if user.id not in active_automations:
            active_automations[user.id] = BusinessTaskAutomation(user, db)
        
        automation = active_automations[user.id]
        tasks = automation.get_scheduled_tasks()
        
        # Filter for auto-execute tasks
        auto_tasks = [t for t in tasks if t.get('auto_execute', False)]
        
        results = []
        for task in auto_tasks:
            task_name = task['name']
            result = await automation.execute_task(task_name)
            results.append({
                "task_name": task_name,
                "success": result.get('success', False),
                "message": result.get('message', '')
            })
        
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        return {
            "success": True,
            "executed": len(results),
            "successful": successful,
            "failed": failed,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to execute all tasks: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute tasks: {str(e)}"
        )

@router.get("/reports/financial")
async def get_financial_report(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate and return a financial report
    """
    try:
        # Get or create automation instance
        if user.id not in active_automations:
            active_automations[user.id] = BusinessTaskAutomation(user, db)
        
        automation = active_automations[user.id]
        
        # Execute financial reporting task
        result = await automation.execute_task("monthly_financial_reporting")
        
        if result.get('success'):
            return {
                "success": True,
                "report": result.get('result', {}),
                "generated_at": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": result.get('error', 'Failed to generate report')
            }
    
    except Exception as e:
        logger.error(f"Failed to generate financial report: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )

@router.get("/dashboard")
async def get_automation_dashboard(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive automation dashboard data
    """
    try:
        # Get or create automation instance
        if user.id not in active_automations:
            active_automations[user.id] = BusinessTaskAutomation(user, db)
        
        automation = active_automations[user.id]
        
        # Gather dashboard data
        tasks = automation.get_scheduled_tasks()
        health = automation.get_automation_health()
        
        # Categorize tasks by frequency
        daily_tasks = [t for t in tasks if t['frequency'] == 'DAILY']
        weekly_tasks = [t for t in tasks if t['frequency'] == 'WEEKLY']
        monthly_tasks = [t for t in tasks if t['frequency'] == 'MONTHLY']
        quarterly_tasks = [t for t in tasks if t['frequency'] == 'QUARTERLY']
        
        # Get next upcoming tasks
        upcoming = sorted(tasks, key=lambda x: x.get('next_run', ''))[:5]
        
        return {
            "success": True,
            "dashboard": {
                "health": health,
                "task_summary": {
                    "total": len(tasks),
                    "daily": len(daily_tasks),
                    "weekly": len(weekly_tasks),
                    "monthly": len(monthly_tasks),
                    "quarterly": len(quarterly_tasks)
                },
                "upcoming_tasks": upcoming,
                "automation_enabled": True,
                "last_update": datetime.now().isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to get automation dashboard: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve dashboard: {str(e)}"
        )