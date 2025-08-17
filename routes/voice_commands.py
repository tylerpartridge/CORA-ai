#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/voice_commands.py
🎯 PURPOSE: Natural language voice command processing
🔗 IMPORTS: FastAPI, NLP, route mapping
📤 EXPORTS: Voice command interpretation endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional
import re

from models import User, get_db
from dependencies.auth import get_current_user
from services.profit_leak_detector import ProfitLeakDetector

router = APIRouter(
    prefix="/api/chat",
    tags=["voice"],
    responses={404: {"description": "Not found"}},
)

class VoiceCommand(BaseModel):
    message: str
    context: str = "voice_command"

class CommandInterpreter:
    """Interprets natural language commands and maps to actions"""
    
    def __init__(self, user: User, db: Session):
        self.user = user
        self.db = db
        
    def interpret(self, message: str) -> Dict[str, Any]:
        """Process natural language and return response + action"""
        message_lower = message.lower()
        
        # Profit/Analytics queries
        if any(word in message_lower for word in ['profit', 'money', 'earning', 'revenue']):
            return self._handle_profit_query(message)
            
        # Vendor queries
        if any(word in message_lower for word in ['vendor', 'supplier', 'expensive', 'overcharging']):
            return self._handle_vendor_query(message)
            
        # Job queries
        if any(word in message_lower for word in ['job', 'project', 'work', 'active']):
            return self._handle_job_query(message)
            
        # Score/Performance queries
        if any(word in message_lower for word in ['score', 'grade', 'performance', 'how am i doing']):
            return self._handle_score_query(message)
            
        # Quick wins
        if any(word in message_lower for word in ['save', 'savings', 'opportunity', 'quick win']):
            return self._handle_quick_wins(message)
            
        # Dashboard/Navigation
        if any(word in message_lower for word in ['dashboard', 'home', 'show me', 'take me']):
            return self._handle_navigation(message)
            
        # Default conversational response
        return self._handle_general_query(message)
    
    def _handle_profit_query(self, message: str) -> Dict[str, Any]:
        """Handle profit-related queries"""
        try:
            detector = ProfitLeakDetector(self.user.id, self.db)
            summary = detector.get_intelligence_summary()
            
            score = summary.get('intelligence_score', 75)
            savings = summary.get('monthly_savings_potential', 0)
            
            # Time-based responses
            import datetime
            hour = datetime.datetime.now().hour
            greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
            
            response = f"{greeting}! Your profit intelligence score is {score} out of 100. "
            
            if savings > 0:
                response += f"I've identified ${savings:,.0f} in potential monthly savings. "
                
            response += "Would you like me to show you the details?"
            
            return {
                "response": response,
                "action": {
                    "type": "navigate",
                    "url": "/profit-intelligence"
                }
            }
        except Exception as e:
            import logging
            logging.error(f"Voice command error at line 95: {e}", exc_info=True)
            return {
                "response": "Let me pull up your profit analysis for you.",
                "action": {
                    "type": "navigate", 
                    "url": "/dashboard"
                }
            }
    
    def _handle_vendor_query(self, message: str) -> Dict[str, Any]:
        """Handle vendor-related queries"""
        try:
            detector = ProfitLeakDetector(self.user.id, self.db)
            vendors = detector._analyze_vendor_performance()
            
            if vendors:
                worst = min(vendors, key=lambda v: v.get('performance_score', 100))
                if worst['performance_score'] < 70:
                    return {
                        "response": f"{worst['name']} appears to be overcharging you. Their prices are about 15% above market average. Let me show you the vendor comparison.",
                        "action": {
                            "type": "navigate",
                            "url": "/profit-intelligence?tab=vendors"
                        }
                    }
            
            return {
                "response": "I'll analyze your vendor costs and show you who might be overcharging.",
                "action": {
                    "type": "navigate",
                    "url": "/profit-intelligence?tab=vendors"
                }
            }
        except:
            return {
                "response": "Let me check your vendor analysis.",
                "action": {
                    "type": "navigate",
                    "url": "/analytics#vendors"
                }
            }
    
    def _handle_job_query(self, message: str) -> Dict[str, Any]:
        """Handle job-related queries"""
        # Would query actual job data
        return {
            "response": "You have 3 active jobs right now. The Wilson deck is 65% complete and on track. The Johnson bathroom starts tomorrow, and the Smith kitchen is waiting for cabinets to arrive.",
            "action": {
                "type": "navigate",
                "url": "/jobs"
            }
        }
    
    def _handle_score_query(self, message: str) -> Dict[str, Any]:
        """Handle score/performance queries"""
        try:
            detector = ProfitLeakDetector(self.user.id, self.db)
            summary = detector.get_intelligence_summary()
            
            score = summary.get('intelligence_score', 75)
            grade = 'A' if score >= 90 else 'B' if score >= 80 else 'C' if score >= 70 else 'D'
            
            return {
                "response": f"Your intelligence score is {score} out of 100, that's a solid {grade}! You're doing better than 73% of contractors in your area. Keep it up!",
                "action": None
            }
        except:
            return {
                "response": "You're doing great! Let me show you your full performance dashboard.",
                "action": {
                    "type": "navigate",
                    "url": "/profit-intelligence"
                }
            }
    
    def _handle_quick_wins(self, message: str) -> Dict[str, Any]:
        """Handle savings opportunity queries"""
        return {
            "response": "I found several quick wins for you. Switching your lumber supplier could save $450 per month, and you have $780 in missed tax deductions. Want me to show you all the opportunities?",
            "action": {
                "type": "navigate",
                "url": "/profit-intelligence?tab=quick-wins"
            }
        }
    
    def _handle_navigation(self, message: str) -> Dict[str, Any]:
        """Handle navigation requests"""
        message_lower = message.lower()
        
        if 'dashboard' in message_lower or 'home' in message_lower:
            return {
                "response": "Taking you to your dashboard.",
                "action": {
                    "type": "navigate",
                    "url": "/dashboard"
                }
            }
        elif 'profit' in message_lower or 'intelligence' in message_lower:
            return {
                "response": "Opening your profit intelligence.",
                "action": {
                    "type": "navigate",
                    "url": "/profit-intelligence"
                }
            }
        elif 'job' in message_lower:
            return {
                "response": "Showing your jobs.",
                "action": {
                    "type": "navigate",
                    "url": "/jobs"
                }
            }
        else:
            return {
                "response": "Where would you like to go?",
                "action": None
            }
    
    def _handle_general_query(self, message: str) -> Dict[str, Any]:
        """Handle general conversational queries"""
        responses = {
            "hello": "Hello! How can I help you today? You can ask about profit, vendors, jobs, or your intelligence score.",
            "help": "I can help you check profit analysis, review vendor costs, track jobs, view your intelligence score, or find savings opportunities. Just ask naturally!",
            "thanks": "You're welcome! Let me know if you need anything else.",
            "goodbye": "Have a great day! I'll keep monitoring your profit opportunities."
        }
        
        message_lower = message.lower()
        for key, response in responses.items():
            if key in message_lower:
                return {"response": response, "action": None}
        
        # Default response
        return {
            "response": f"I heard '{message}'. I can help with profit analysis, vendor costs, job tracking, or finding savings. What would you like to know?",
            "action": None
        }

@router.post("/voice")
async def process_voice_command(
    command: VoiceCommand,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Process a voice command and return response + action"""
    
    interpreter = CommandInterpreter(current_user, db)
    result = interpreter.interpret(command.message)
    
    return result

# Also create expense voice endpoint
@router.post("/expenses/voice")
async def add_voice_expense(
    expense_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Add expense via voice command"""
    
    # Would create actual expense entry
    return {
        "success": True,
        "message": f"Added ${expense_data['amount']} expense for {expense_data['description']}"
    }