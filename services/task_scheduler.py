#!/usr/bin/env python3
"""
Task Scheduler Service
Automatically executes business tasks based on their frequency and schedule
"""

import asyncio
import schedule
import time
import threading
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import json
from sqlalchemy.orm import sessionmaker

from models import User
from services.business_task_automation import BusinessTaskAutomation

logger = logging.getLogger(__name__)

class TaskScheduler:
    """Manages automated task execution based on schedules"""
    
    def __init__(self):
        self.is_running = False
        self.scheduler_thread = None
        self.active_tasks = {}
        self.task_results = {}
        self.load_config()
        
    def load_config(self):
        """Load task configuration"""
        try:
            with open('tools/config/business_task_templates.json', 'r') as f:
                self.task_config = json.load(f)['task_templates']
                logger.info(f"Loaded {len(self.task_config)} task configurations")
        except Exception as e:
            logger.error(f"Failed to load task configuration: {e}")
            self.task_config = {}
    
    def setup_schedules(self):
        """Setup task schedules based on frequency"""
        # Clear existing schedules
        schedule.clear()
        
        for task_name, config in self.task_config.items():
            if not config.get('auto_execute', False):
                continue
                
            frequency = config.get('frequency', 'DAILY')
            
            if frequency == 'DAILY':
                schedule.every().day.at("06:00").do(self.execute_task, task_name)
            elif frequency == 'WEEKLY':
                schedule.every().monday.at("06:00").do(self.execute_task, task_name)
            elif frequency == 'MONTHLY':
                # Schedule for 1st of each month at 6 AM
                schedule.every().day.at("06:00").do(self.execute_task, task_name)
            elif frequency == 'QUARTERLY':
                # Schedule for quarterly tasks (simplified to monthly for now)
                schedule.every().day.at("06:00").do(self.execute_task, task_name)
        
        logger.info(f"Setup {len(schedule.jobs)} scheduled tasks")
    
    async def execute_task(self, task_name: str):
        """Execute a scheduled task for all users"""
        logger.info(f"Executing scheduled task: {task_name}")
        
        try:
            # Get database session
            engine = create_engine("sqlite:///data/cora.db")
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionLocal()
            
            # Get all active users
            users = db.query(User).filter(User.is_active == True).all()
            
            total_executed = 0
            total_success = 0
            total_failed = 0
            
            for user in users:
                try:
                    # Create task automation instance for user
                    task_automation = BusinessTaskAutomation(user, db)
                    
                    # Execute task
                    result = await task_automation.execute_task(task_name)
                    
                    if result.get('success', False):
                        total_success += 1
                        logger.info(f"Task {task_name} completed successfully for user {user.id}")
                    else:
                        total_failed += 1
                        logger.error(f"Task {task_name} failed for user {user.id}: {result.get('error', 'Unknown error')}")
                    
                    total_executed += 1
                    
                except Exception as e:
                    total_failed += 1
                    logger.error(f"Task {task_name} failed for user {user.id}: {e}")
            
            # Store results
            self.task_results[task_name] = {
                "executed_at": datetime.now().isoformat(),
                "total_executed": total_executed,
                "total_success": total_success,
                "total_failed": total_failed,
                "success_rate": (total_success / total_executed * 100) if total_executed > 0 else 0
            }
            
            logger.info(f"Task {task_name} completed: {total_success}/{total_executed} successful")
            
        except Exception as e:
            logger.error(f"Failed to execute task {task_name}: {e}")
            self.task_results[task_name] = {
                "executed_at": datetime.now().isoformat(),
                "error": str(e),
                "total_executed": 0,
                "total_success": 0,
                "total_failed": 0
            }
    
    def start_scheduler(self):
        """Start the task scheduler"""
        if self.is_running:
            logger.warning("Task scheduler is already running")
            return
        
        self.setup_schedules()
        self.is_running = True
        
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Task scheduler started successfully")
    
    def stop_scheduler(self):
        """Stop the task scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Task scheduler stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            "is_running": self.is_running,
            "scheduled_tasks": len(schedule.jobs),
            "active_tasks": len(self.active_tasks),
            "last_results": self.task_results,
            "next_runs": self._get_next_runs()
        }
    
    def _get_next_runs(self) -> Dict[str, str]:
        """Get next run times for scheduled tasks"""
        next_runs = {}
        for job in schedule.jobs:
            next_runs[job.job_func.__name__] = job.next_run.isoformat() if job.next_run else "Unknown"
        return next_runs
    
    def get_task_history(self, task_name: str = None) -> List[Dict[str, Any]]:
        """Get task execution history"""
        if task_name:
            return [self.task_results.get(task_name, {})]
        return list(self.task_results.values())
    
    def manual_execute(self, task_name: str) -> Dict[str, Any]:
        """Manually execute a task"""
        if task_name not in self.task_config:
            return {
                "success": False,
                "error": f"Task '{task_name}' not found"
            }
        
        # Create event loop for async execution
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.execute_task(task_name))
            loop.close()
            
            return {
                "success": True,
                "message": f"Task {task_name} executed manually",
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Global scheduler instance
task_scheduler = TaskScheduler()

def start_task_scheduler():
    """Start the global task scheduler"""
    task_scheduler.start_scheduler()

def stop_task_scheduler():
    """Stop the global task scheduler"""
    task_scheduler.stop_scheduler()

def get_scheduler_status():
    """Get global scheduler status"""
    return task_scheduler.get_status() 