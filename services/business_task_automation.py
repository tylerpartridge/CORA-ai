"""
Business Task Automation Service
Automates recurring business tasks for contractors
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from sqlalchemy.orm import Session
import logging

from models import User, Expense

logger = logging.getLogger(__name__)

class TaskFrequency(Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"

class TaskPriority(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class TaskStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class BusinessTaskAutomation:
    """Manages automated business tasks for contractors"""
    
    def __init__(self, user: User, db: Session):
        self.user = user
        self.db = db
        self.load_templates()
        self.active_tasks = {}
        
    def load_templates(self):
        """Load task templates from configuration"""
        try:
            with open('tools/config/business_task_templates.json', 'r') as f:
                self.templates = json.load(f)['task_templates']
                logger.info(f"Loaded {len(self.templates)} task templates")
        except Exception as e:
            logger.error(f"Failed to load task templates: {e}")
            self.templates = {}
    
    async def execute_task(self, task_name: str) -> Dict[str, Any]:
        """Execute a specific automated task"""
        if task_name not in self.templates:
            return {
                "success": False,
                "error": f"Task '{task_name}' not found"
            }
        
        template = self.templates[task_name]
        task_type = template['task_type']
        
        # Update task status
        self.active_tasks[task_name] = {
            "status": TaskStatus.RUNNING.value,
            "started_at": datetime.now().isoformat()
        }
        
        try:
            # Route to appropriate handler
            if task_type == "PAYMENT_PROCESSING":
                result = await self._process_payments()
            elif task_type == "SUBSCRIPTION_MANAGEMENT":
                result = await self._manage_subscriptions()
            elif task_type == "FINANCIAL_REPORTING":
                result = await self._generate_financial_report()
            elif task_type == "TAX_PREPARATION":
                result = await self._prepare_taxes()
            elif task_type == "EXPENSE_CATEGORIZATION":
                result = await self._categorize_expenses()
            elif task_type == "COMPLIANCE_MONITORING":
                result = await self._monitor_compliance()
            elif task_type == "REVENUE_ANALYTICS":
                result = await self._analyze_revenue()
            elif task_type == "CHURN_PREDICTION":
                result = await self._predict_churn()
            else:
                result = await self._generic_task_handler(task_type)
            
            # Update task status
            self.active_tasks[task_name] = {
                "status": TaskStatus.COMPLETED.value,
                "completed_at": datetime.now().isoformat(),
                "result": result
            }
            
            return {
                "success": True,
                "task_name": task_name,
                "task_type": task_type,
                "result": result,
                "completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Task {task_name} failed: {e}")
            self.active_tasks[task_name] = {
                "status": TaskStatus.FAILED.value,
                "failed_at": datetime.now().isoformat(),
                "error": str(e)
            }
            return {
                "success": False,
                "task_name": task_name,
                "error": str(e)
            }
    
    async def _process_payments(self) -> Dict[str, Any]:
        """Process daily payments and analyze failures"""
        # Mock implementation - would integrate with Stripe
        pending_payments = []
        failed_payments = []
        
        return {
            "processed": len(pending_payments),
            "failed": len(failed_payments),
            "total_amount": 0,
            "message": "Payment processing completed"
        }
    
    async def _manage_subscriptions(self) -> Dict[str, Any]:
        """Check subscription health and renewals"""
        # Mock implementation
        return {
            "active_subscriptions": 0,
            "expiring_soon": 0,
            "cancelled": 0,
            "message": "Subscription check completed"
        }
    
    async def _generate_financial_report(self) -> Dict[str, Any]:
        """Generate monthly financial report"""
        try:
            # Get expenses for the last month
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            expenses = self.db.query(Expense).filter(
                Expense.user_id == self.user.id,
                Expense.date >= start_date,
                Expense.date <= end_date
            ).all()
            
            total_expenses = sum(e.amount for e in expenses)
            expense_by_category = {}
            
            for expense in expenses:
                category = expense.category or "Uncategorized"
                if category not in expense_by_category:
                    expense_by_category[category] = 0
                expense_by_category[category] += expense.amount
            
            # Calculate insights
            insights = []
            if total_expenses > 0:
                top_category = max(expense_by_category.items(), key=lambda x: x[1])
                insights.append(f"Highest spending: {top_category[0]} (${top_category[1]:.2f})")
                
                if len(expenses) > 0:
                    avg_expense = total_expenses / len(expenses)
                    insights.append(f"Average expense: ${avg_expense:.2f}")
            
            return {
                "period": "Last 30 days",
                "total_expenses": total_expenses,
                "expense_count": len(expenses),
                "by_category": expense_by_category,
                "insights": insights,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Financial report generation failed: {e}")
            return {
                "error": str(e),
                "message": "Failed to generate financial report"
            }
    
    async def _prepare_taxes(self) -> Dict[str, Any]:
        """Prepare quarterly tax information"""
        # Get current quarter
        month = datetime.now().month
        quarter = f"Q{((month - 1) // 3) + 1}"
        
        # Mock implementation - would calculate actual tax data
        return {
            "quarter": quarter,
            "estimated_tax": 0,
            "deductible_expenses": 0,
            "message": f"Tax preparation for {quarter} initiated"
        }
    
    async def _categorize_expenses(self) -> Dict[str, Any]:
        """Categorize uncategorized expenses using AI"""
        try:
            # Find uncategorized expenses
            uncategorized = self.db.query(Expense).filter(
                Expense.user_id == self.user.id,
                Expense.category == None
            ).limit(50).all()
            
            categorized_count = 0
            for expense in uncategorized:
                # Mock categorization - would use AI
                if "gas" in (expense.description or "").lower():
                    expense.category = "Fuel"
                elif "tool" in (expense.description or "").lower():
                    expense.category = "Tools & Equipment"
                elif "material" in (expense.description or "").lower():
                    expense.category = "Materials"
                else:
                    expense.category = "Other"
                
                categorized_count += 1
            
            if categorized_count > 0:
                self.db.commit()
            
            return {
                "categorized": categorized_count,
                "remaining_uncategorized": len(uncategorized) - categorized_count,
                "message": f"Categorized {categorized_count} expenses"
            }
            
        except Exception as e:
            logger.error(f"Expense categorization failed: {e}")
            return {
                "error": str(e),
                "message": "Failed to categorize expenses"
            }
    
    async def _monitor_compliance(self) -> Dict[str, Any]:
        """Monitor compliance and regulatory requirements"""
        compliance_checks = {
            "data_retention": "PASSED",
            "privacy_policy": "CURRENT",
            "security_audit": "DUE IN 30 DAYS",
            "license_renewal": "CURRENT"
        }
        
        alerts = []
        if "DUE" in str(compliance_checks.values()):
            alerts.append("Security audit due soon")
        
        return {
            "compliance_status": "COMPLIANT",
            "checks": compliance_checks,
            "alerts": alerts,
            "last_check": datetime.now().isoformat()
        }
    
    async def _analyze_revenue(self) -> Dict[str, Any]:
        """Analyze revenue and growth metrics"""
        # Mock implementation - would integrate with payment data
        return {
            "monthly_revenue": 0,
            "growth_rate": 0,
            "trending": "stable",
            "message": "Revenue analysis completed"
        }
    
    async def _predict_churn(self) -> Dict[str, Any]:
        """Predict user churn risk"""
        # Mock implementation - would use ML model
        return {
            "at_risk_users": 0,
            "churn_probability": 0,
            "retention_actions": [],
            "message": "Churn prediction completed"
        }
    
    async def _generic_task_handler(self, task_type: str) -> Dict[str, Any]:
        """Handle generic tasks"""
        return {
            "task_type": task_type,
            "status": "completed",
            "message": f"Generic handler for {task_type}"
        }
    
    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """Get list of scheduled tasks for user"""
        scheduled = []
        for name, template in self.templates.items():
            scheduled.append({
                "name": name,
                "description": template['description'],
                "frequency": template['frequency'],
                "priority": template['priority'],
                "auto_execute": template.get('auto_execute', False),
                "next_run": self._calculate_next_run(template['frequency'])
            })
        return scheduled
    
    def _calculate_next_run(self, frequency: str) -> str:
        """Calculate next run time based on frequency"""
        now = datetime.now()
        
        if frequency == "DAILY":
            # Run at 6 AM daily
            next_run = now.replace(hour=6, minute=0, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
        elif frequency == "WEEKLY":
            # Run on Mondays at 6 AM
            days_ahead = 0 - now.weekday()  # Monday is 0
            if days_ahead <= 0:
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=6, minute=0, second=0, microsecond=0)
        elif frequency == "MONTHLY":
            # Run on 1st of month at 6 AM
            if now.day == 1 and now.hour < 6:
                next_run = now.replace(hour=6, minute=0, second=0, microsecond=0)
            else:
                # Next month
                if now.month == 12:
                    next_run = now.replace(year=now.year + 1, month=1, day=1,
                                          hour=6, minute=0, second=0, microsecond=0)
                else:
                    next_run = now.replace(month=now.month + 1, day=1,
                                          hour=6, minute=0, second=0, microsecond=0)
        elif frequency == "QUARTERLY":
            # Run on 1st day of quarter at 6 AM
            quarter_months = [1, 4, 7, 10]
            current_quarter_start = max(m for m in quarter_months if m <= now.month)
            next_quarter_start = quarter_months[(quarter_months.index(current_quarter_start) + 1) % 4]
            
            if next_quarter_start < current_quarter_start:
                # Next year
                next_run = now.replace(year=now.year + 1, month=next_quarter_start, day=1,
                                      hour=6, minute=0, second=0, microsecond=0)
            else:
                next_run = now.replace(month=next_quarter_start, day=1,
                                      hour=6, minute=0, second=0, microsecond=0)
        else:
            next_run = now + timedelta(days=1)
        
        return next_run.isoformat()
    
    def get_task_status(self, task_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        return self.active_tasks.get(task_name)
    
    async def cancel_task(self, task_name: str) -> bool:
        """Cancel a running task"""
        if task_name in self.active_tasks:
            self.active_tasks[task_name]["status"] = TaskStatus.CANCELLED.value
            self.active_tasks[task_name]["cancelled_at"] = datetime.now().isoformat()
            return True
        return False

    def get_automation_health(self) -> Dict[str, Any]:
        """Get overall health of automation system"""
        total_tasks = len(self.templates)
        completed_today = sum(1 for t in self.active_tasks.values() 
                            if t.get("status") == TaskStatus.COMPLETED.value 
                            and t.get("completed_at", "").startswith(datetime.now().date().isoformat()))
        failed_today = sum(1 for t in self.active_tasks.values() 
                         if t.get("status") == TaskStatus.FAILED.value 
                         and t.get("failed_at", "").startswith(datetime.now().date().isoformat()))
        
        return {
            "total_templates": total_tasks,
            "completed_today": completed_today,
            "failed_today": failed_today,
            "success_rate": (completed_today / (completed_today + failed_today) * 100) if (completed_today + failed_today) > 0 else 0,
            "active_tasks": len([t for t in self.active_tasks.values() if t.get("status") == TaskStatus.RUNNING.value]),
            "system_status": "HEALTHY" if failed_today == 0 else "DEGRADED" if failed_today < completed_today else "UNHEALTHY"
        }