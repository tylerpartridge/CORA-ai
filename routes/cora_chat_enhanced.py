#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/cora_chat_enhanced.py
🎯 PURPOSE: CORA v2 Enhanced - Advanced chat with emotional intelligence
📝 STATUS: ACTIVE (Primary) - Handles /api/cora-chat-v2 endpoints
🔗 IMPORTS: FastAPI, OpenAI, personality scripts, contractor knowledge
📤 EXPORTS: cora_chat_enhanced_router with full personality implementation
🔄 PATTERN: Personality-driven conversational AI with emotional awareness
✨ FEATURES: Emotional intelligence, contractor profiling, stress detection
📝 TODOS: A/B test different conversation paths, add voice support

💡 AI HINT: Personality files are in /data/cora_contractor_personality.json
⭐ RECOMMENDED: This is the primary chat implementation for production use
⚠️ NEVER: Break character - CORA is always a knowledgeable contractor buddy
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import get_db
import os
import json
import hashlib
import logging
import re
import random
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)

# OpenAI import
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    if os.getenv('DEBUG', '').lower() == 'true':
        print("Warning: OpenAI module not installed. Run 'pip install openai' to enable AI responses.")
    OPENAI_AVAILABLE = False
    
from config import config

# Load enhanced personality and conversation scripts
DATA_PATH = Path(__file__).parent.parent / "data"
KNOWLEDGE_BASE_PATH = DATA_PATH / "cora_knowledge_base.json"
PERSONALITY_PATH = DATA_PATH / "cora_contractor_personality.json"
IMPLEMENTATION_PATH = DATA_PATH / "cora_conversation_implementation.json"

def load_json_file(path: Path) -> Dict:
    """Safely load JSON file with error handling"""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"File not found: {path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {path}: {e}")
        return {}

# Load all personality and knowledge data
CORA_KNOWLEDGE = load_json_file(KNOWLEDGE_BASE_PATH)
CONTRACTOR_PERSONALITY = load_json_file(PERSONALITY_PATH)
CONVERSATION_IMPLEMENTATION = load_json_file(IMPLEMENTATION_PATH)

# Create router
cora_chat_enhanced_router = APIRouter(prefix="/api/cora-chat-v2", tags=["cora-chat-enhanced"])

# In-memory storage for rate limiting and conversation tracking
conversation_limits = defaultdict(lambda: {"count": 0, "reset_time": datetime.utcnow()})
conversation_history = defaultdict(list)
conversation_metadata = defaultdict(dict)  # Track user type, urgency, etc.

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None  # User type, context, etc.

class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    messages_remaining: int
    suggest_signup: bool = False
    metadata: Optional[Dict[str, Any]] = None  # Response context

# Helper functions
def get_visitor_id(request: Request) -> str:
    """Generate a unique visitor ID based on IP and user agent"""
    ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    return hashlib.md5(f"{ip}:{user_agent}".encode()).hexdigest()

def check_rate_limit(visitor_id: str, is_onboarding: bool = False) -> Tuple[bool, int]:
    """Check if visitor has messages remaining"""
    # Exempt onboarding conversations from rate limiting
    if is_onboarding:
        return True, 999  # Allow unlimited messages for onboarding
    
    now = datetime.utcnow()
    visitor_data = conversation_limits[visitor_id]
    
    # Reset if 24 hours have passed
    if now > visitor_data["reset_time"] + timedelta(hours=24):
        visitor_data["count"] = 0
        visitor_data["reset_time"] = now
    
    remaining = 10 - visitor_data["count"]
    return remaining > 0, remaining

def analyze_user_context(message: str, history: List[Dict], user_profile: Dict = None) -> Dict[str, Any]:
    """Analyze user message and conversation history to determine context"""
    message_lower = message.lower()
    context = {
        "urgency": "normal",
        "contractor_type": None,
        "business_size": None,
        "pain_points": [],
        "current_tools": [],
        "conversation_phase": "discovery"
    }
    
    # Pre-fill context from user profile if available
    if user_profile:
        context["contractor_type"] = user_profile.get("business_type")
        context["business_size"] = user_profile.get("businessSize")
        context["business_name"] = user_profile.get("business_name")
        if user_profile.get("mainChallenge"):
            context["pain_points"].append(user_profile.get("mainChallenge"))
        if user_profile.get("trackingMethod"):
            context["current_tools"].append(user_profile.get("trackingMethod"))
        context["user_name"] = user_profile.get("name")
        context["years_in_business"] = user_profile.get("yearsInBusiness")
        context["service_area"] = user_profile.get("serviceArea")
        context["customer_type"] = user_profile.get("customerType")
        context["business_goal"] = user_profile.get("businessGoal")
    
    # Determine conversation phase
    if len(history) < 4:
        context["conversation_phase"] = "discovery"
    elif len(history) < 8:
        context["conversation_phase"] = "education"
    else:
        context["conversation_phase"] = "conversion"
    
    # Detect urgency
    urgent_keywords = ["asap", "urgent", "immediately", "today", "right now", "crisis", "emergency"]
    if any(word in message_lower for word in urgent_keywords):
        context["urgency"] = "high"
    
    # Detect contractor type
    contractor_types = {
        "general contractor": ["gc", "general contractor", "general", "multiple trades"],
        "plumber": ["plumb", "pipe", "drain", "water", "fixture"],
        "electrician": ["electric", "wire", "panel", "breaker", "voltage"],
        "hvac": ["hvac", "heating", "cooling", "air condition", "furnace"],
        "remodeler": ["remodel", "renovation", "kitchen", "bathroom", "addition"],
        "concrete": ["concrete", "foundation", "slab", "pour", "form"],
        "framer": ["framing", "framer", "rough", "lumber", "stud"],
        "roofer": ["roof", "shingle", "gutter", "fascia", "soffit"]
    }
    
    for contractor_type, keywords in contractor_types.items():
        if any(keyword in message_lower for keyword in keywords):
            context["contractor_type"] = contractor_type
            break
    
    # Detect business size
    if any(word in message_lower for word in ["solo", "myself", "one man", "just me"]):
        context["business_size"] = "solo"
    elif any(word in message_lower for word in ["crew", "guys", "team", "employees"]):
        context["business_size"] = "small_crew"
    elif any(word in message_lower for word in ["company", "multiple crews", "office"]):
        context["business_size"] = "established"
    
    # Detect pain points
    pain_point_keywords = {
        "cash_flow": ["cash", "money", "payroll", "pay", "collect", "receivable"],
        "organization": ["organize", "track", "lost", "mess", "chaos", "scattered"],
        "profitability": ["profit", "margin", "losing money", "break even", "pricing"],
        "time": ["time", "hours", "busy", "overwhelmed", "paperwork", "weekend"],
        "technology": ["computer", "tech", "complicated", "simple", "easy"],
        "taxes": ["tax", "deduction", "irs", "write off", "accountant"]
    }
    
    for pain_point, keywords in pain_point_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            context["pain_points"].append(pain_point)
    
    # Detect current tools
    tool_keywords = {
        "quickbooks": ["quickbooks", "qb", "quick books"],
        "excel": ["excel", "spreadsheet", "worksheet"],
        "paper": ["paper", "notebook", "folder", "file cabinet"],
        "nothing": ["nothing", "none", "don't track", "no system"]
    }
    
    for tool, keywords in tool_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            context["current_tools"].append(tool)
    
    return context

def get_personality_response(context: Dict[str, Any], message: str, history: List[Dict]) -> str:
    """Generate a personality-driven response based on context"""
    personality = CONTRACTOR_PERSONALITY.get("personality", {})
    scripts = CONTRACTOR_PERSONALITY.get("conversation_scripts", {})
    
    # Get appropriate greeting if first message
    if len(history) == 0:
        greetings = personality.get("speaking_style", {}).get("greetings", [])
        base_greeting = random.choice(greetings) if greetings else "Hey there! I'm CORA."
        
        # Personalize with user's name if available
        if context.get("user_name"):
            base_greeting = f"Hey {context['user_name']}! Good to see you back. I'm CORA."
        
        # Customize based on contractor type if detected
        if context["contractor_type"]:
            contractor_scripts = scripts.get("first_time_visitors", {})
            type_map = {
                "general contractor": "general_contractor",
                "plumber": "specialty_contractor",
                "electrician": "specialty_contractor",
                "hvac": "specialty_contractor",
                "remodeler": "residential_remodeler"
            }
            script_key = type_map.get(context["contractor_type"], "specialty_contractor")
            if script_key in contractor_scripts:
                return contractor_scripts[script_key]["greeting"]
        
        return base_greeting + " What type of construction work do you do?"
    
    # Handle specific scenarios based on conversation phase
    phase = context["conversation_phase"]
    
    if phase == "discovery":
        # Focus on understanding their business
        if not context["contractor_type"]:
            return "What type of construction do you specialize in? I work with GCs, plumbers, electricians, remodelers - all trades really."
        elif not context["business_size"]:
            return f"Nice, {context['contractor_type']} work! Are you flying solo or do you have a crew?"
        elif not context["pain_points"]:
            return "What's the biggest challenge with tracking your job costs right now?"
        else:
            # Acknowledge their pain point
            pain_responses = {
                "cash_flow": "Cash flow is king in construction. Let me show you how to track who owes you money and when it's coming.",
                "organization": "I get it - receipts everywhere, notes on napkins. I'll organize all that automatically.",
                "profitability": "Not knowing if you made money until months later is brutal. I show you profit in real-time.",
                "time": "Spending weekends on paperwork instead of with family sucks. I give you those weekends back.",
                "technology": "No worries - I'm built for contractors, not computer nerds. If you can text a photo, you can use me.",
                "taxes": "Most contractors leave thousands on the table at tax time. I track every deduction automatically."
            }
            pain_point = context["pain_points"][0]
            return pain_responses.get(pain_point, "Tell me more about that challenge.")
    
    elif phase == "education":
        # Connect their problems to solutions
        if context["current_tools"] and "quickbooks" in context["current_tools"]:
            return scripts["objection_handling"]["complexity_objections"]["already_have_system"]["response"]
        elif context["business_size"] == "solo":
            return "As a solo contractor, your time is everything. I save solo guys like you 20+ hours a month - that's almost a week of extra work time. Voice tracking from your truck, automatic mileage, instant profit reports. Want to see how?"
        elif context["contractor_type"]:
            # Give trade-specific value prop
            trade_benefits = {
                "plumber": "Track every service call's profit, manage parts inventory, and never miss marking up materials. One plumber found $3,200 in missed markups his first month.",
                "electrician": "Material prices changing daily? I track your actual costs per job and alert you when it's time to raise prices. Plus permit tracking by jurisdiction.",
                "remodeler": "Change orders killing your profits? I track every homeowner request and show the impact instantly. No more scope creep eating your margins.",
                "general contractor": "Managing subs across multiple jobs is chaos. I track every sub, every change order, handle progress billing, and show real-time profit by job."
            }
            benefit = trade_benefits.get(context["contractor_type"], 
                "I track all your costs by job, show real-time profits, and save you 20+ hours monthly on paperwork.")
            return benefit + " Try me free for 30 days?"
        else:
            return "Here's the deal: I save contractors 20+ hours a month and help find 15% more profit on average. That's real money in your pocket. Want to see how?"
    
    else:  # conversion phase
        # Push for trial signup
        if context["urgency"] == "high":
            return "Sounds like you need this yesterday. Good news - setup takes 30 minutes and you'll see your job profits immediately. Ready to start your free trial? No credit card needed."
        elif "price" in message.lower() or "cost" in message.lower():
            return scripts["objection_handling"]["price_objections"]["too_expensive"]["response"]
        else:
            return "You've asked great questions. Most contractors know within a week they'll never go back to the old way. Ready for your free 30-day trial? I'll walk you through setup."

def generate_enhanced_response(message: str, history: List[Dict], metadata: Dict) -> str:
    """Generate response using enhanced personality system"""
    
    # Check if this is onboarding FIRST - this takes priority
    if metadata and metadata.get('onboarding'):
        # Use OpenAI for onboarding responses to ensure proper instruction following
        system_prompt = generate_enhanced_system_prompt(metadata)
        response = generate_openai_response_sync(message, history, system_prompt, metadata)
        if response:
            return response
        else:
            # Fallback to hardcoded onboarding responses if OpenAI fails
            return generate_onboarding_fallback_response(message, history, metadata)
    
    # Analyze context (including user profile if available)
    user_profile = metadata.get("user_profile") if metadata else None
    context = analyze_user_context(message, history, user_profile)
    
    # Merge with provided metadata
    if metadata:
        context.update(metadata)
    
    # Store context for conversation continuity
    if history:
        conversation_id = metadata.get("conversation_id", "unknown")
        conversation_metadata[conversation_id] = context
    
    message_lower = message.lower()
    
    # Check for specific contractor queries first
    job_query_patterns = [
        (r"show me the (.+?) job", "job_status"),
        (r"how'?s the (.+?) (?:job|project)", "job_status"),
        (r"profit on (.+?)[\?\.]", "job_profit"),
        (r"(.+?) job cost", "job_cost"),
        (r"compare (.+?) (?:jobs|projects)", "job_comparison")
    ]
    
    for pattern, query_type in job_query_patterns:
        match = re.search(pattern, message_lower)
        if match:
            job_ref = match.group(1).strip()
            if query_type == "job_status":
                return f"The {job_ref.title()} job is at 67% complete with a 24% profit margin. You've spent $18,420 of the $28,000 budget. Materials are tracking 5% over estimate - might want to check those lumber receipts."
            elif query_type == "job_profit":
                return f"Current profit on {job_ref.title()}: $4,580 (22% margin). That's after all costs including your labor. Want me to break down where the money's going?"
            elif query_type == "job_comparison":
                return f"Here's your last 3 {job_ref} jobs: Miller (28% margin, 12 days), Johnson (19% margin, 18 days), Smith (24% margin, 14 days). Looks like Miller was your sweet spot. What made that one different?"
    
    # Check for command-style inputs
    if any(word in message_lower for word in ["track", "log", "add", "record"]):
        # Extract amount
        amount_match = re.search(r'\$?([\d,]+(?:\.\d{2})?)', message)
        if amount_match:
            amount = amount_match.group(1)
            return f"Got it - logged ${amount}. Which job should I assign this to? (You can just say the customer name or job address)"
    
    # Use personality-driven response system
    response = get_personality_response(context, message, history)
    
    # If no specific response generated, check knowledge base patterns
    if not response or response == message:  # Fallback if something went wrong
        # Price/cost questions
        if any(word in message_lower for word in ["price", "cost", "expensive", "afford", "how much"]):
            return "Just $29/month for most contractors - less than 30 minutes of your billable time. But here's the kicker: contractors find an average of $2,000 in missed deductions their first month. Try it free for 30 days and see for yourself?"
        
        # Time/busy objections
        elif any(word in message_lower for word in ["busy", "time", "swamped", "overwhelmed"]):
            return "Being too busy is exactly why you need me! Setup takes 30 minutes, then I save you 20+ hours every month. That's like getting your Fridays back. Free trial - what's stopping you?"
        
        # Trust/security concerns
        elif any(word in message_lower for word in ["secure", "safe", "trust", "privacy"]):
            return "Smart to ask. I use bank-level encryption, I'm SOC 2 certified, and your data is never sold. 800+ contractors trust me with their finances. Want to start with manual entry during your free trial?"
        
        # Getting started
        elif any(word in message_lower for word in ["start", "begin", "try", "sign up"]):
            return "Let's do this! Sign up at coraai.tech (no credit card needed), connect your bank (or start manual), and import your current jobs. You'll see your real profits in under 30 minutes. Ready?"
        
        # Default discovery question
        else:
            discovery_questions = [
                "What type of construction work keeps you busy?",
                "How many jobs are you juggling right now?",
                "What's your current system for tracking job costs?",
                "Ever finish a job thinking you made money, only to find out you didn't?",
                "What would you do with an extra 20 hours every month?"
            ]
            return random.choice(discovery_questions)
    
    return response

def generate_onboarding_fallback_response(message: str, history: List[Dict], metadata: Dict) -> str:
    """Generate onboarding responses when OpenAI is not available"""
    
    # Debug logging
    print(f"ONBOARDING FALLBACK - Message: '{message}', History length: {len(history)}, Metadata: {metadata}")
    
    # Get collected data from metadata
    collected_data = metadata.get('collectedData', {})
    
    # Determine current phase based on collected data (same logic as frontend)
    if not collected_data.get('name'):
        phase = 'greeting'
    elif not collected_data.get('businessType') and not collected_data.get('yearsInBusiness'):
        phase = 'business_discovery'
    elif not collected_data.get('yearsInBusiness'):
        phase = 'years_experience'
    elif not collected_data.get('businessSize'):
        phase = 'business_size'
    elif not collected_data.get('serviceArea'):
        phase = 'service_area'
    elif not collected_data.get('customerType'):
        phase = 'customer_type'
    elif not collected_data.get('trackingMethod'):
        phase = 'current_tracking'
    elif not collected_data.get('mainChallenge'):
        phase = 'main_challenge'
    elif not collected_data.get('busySeason'):
        phase = 'busy_season'
    elif not collected_data.get('businessGoal'):
        phase = 'business_goal'
    elif not collected_data.get('email'):
        phase = 'email_collection'
    elif not collected_data.get('password'):
        phase = 'password_creation'
    else:
        phase = 'completion'
    
    print(f"ONBOARDING FALLBACK - Determined phase: {phase} based on collected data: {collected_data}")
    
    # Handle first message (greeting phase)
    if not message and len(history) == 0:
        # Don't include any tags in the greeting - just ask for their name
        return "Hey! I'm CORA, I'm going to help you squeeze every dollar and leave nothing on the table. What should I call you?"
    
    # Handle user's name response
    if phase == 'greeting' and message:
        # Extract name from message
        name = message.strip().split()[0] if message.strip() else "there"
        return f"Great to meet you, {name}! What type of construction work do you do? [business_types]"
    
    # Handle business type selection
    if phase == 'business_discovery':
        return "How long have you been in business? [years_in_business]"
    
    # Handle years in business
    if phase == 'years_experience':
        return "And how would you describe your business size? [business_sizes]"
    
    # Handle business size
    if phase == 'business_size':
        return "And how would you describe your business size? [business_sizes]"
    
    # Handle service area
    if phase == 'service_area':
        return "Where do you primarily work? [service_areas]"
    
    # Handle customer type
    if phase == 'customer_type':
        return "Who are your typical customers? [customer_types]"
    
    # Handle tracking method
    if phase == 'current_tracking':
        return "How do you currently track your expenses and jobs? [tracking_methods]"
    
    # Handle main challenge
    if phase == 'main_challenge':
        return "What's your biggest challenge with the business side? [pain_points]"
    
    # Handle busy season
    if phase == 'busy_season':
        return "When's your busiest time of year? [busy_seasons]"
    
    # Handle business goal
    if phase == 'business_goal':
        return "What's your main goal for the next year? [business_goals]"
    
    # Handle email collection
    if phase == 'email_collection':
        return "Perfect! Now, what email should I send your profit reports to?"
    
    # Handle password creation
    if phase == 'password_creation':
        return "Great! Let's secure your account with a password. Choose something you'll remember."
    
    # Default fallback
    return "Thanks for sharing that! Let's continue with the next question."

# Enhanced system prompt with full personality
def generate_enhanced_system_prompt(metadata=None) -> str:
    """Generate system prompt with full personality implementation"""
    personality = CONTRACTOR_PERSONALITY.get("personality", {})
    implementation = CONVERSATION_IMPLEMENTATION.get("implementation_guide", {})
    
    # Check if this is onboarding
    if metadata and metadata.get('onboarding'):
        onboarding_context = metadata.get('onboardingContext', {})
        phase = onboarding_context.get('phase', 'greeting')
        instructions = metadata.get('instructions', '')
        user_data = onboarding_context.get('userData', {})
        
        prompt = f"""You are CORA, an AI assistant for contractors. This is ONBOARDING - you are GUIDING someone through setup.

Current onboarding phase: {phase}
Instructions for this phase: {instructions}
User data collected: {json.dumps(user_data, indent=2) if user_data else "None yet"}

CRITICAL ONBOARDING RULES:
1. You are the GUIDE - tell them exactly what's happening
2. For greeting phase, your FIRST message should be: "Hey! I'm CORA, I'm going to help you squeeze every dollar and leave nothing on the table. What should I call you?"
3. Be CLEAR about what you need from them at each step
4. If they seem confused, EXPLAIN the process: "I just need to learn a bit about your business so I can show you real insights"
5. Always make it clear WHY you're asking each question
6. CRITICAL: You MUST include the [tag] shown in each phase - this is what makes the selection boxes appear!

REQUIRED FLOW AND EXACT MESSAGES TO USE:
Phase 1 (greeting): Get their name warmly (no tag needed - they type their answer)
Phase 2 (business_discovery): Your message MUST end with: [business_types]
   Example: "Great to meet you, [name]! What type of construction work do you do? [business_types]"
Phase 3 (years_experience): MUST include [years_in_business] - "How long have you been in business? [years_in_business]"
Phase 4 (business_size): MUST include [business_sizes] - "And how would you describe your business size? [business_sizes]"
Phase 5 (service_area): MUST include [service_areas] - "Where do you primarily work? [service_areas]"
Phase 6 (customer_type): MUST include [customer_types] - "Who are your typical customers? [customer_types]"
Phase 7 (current_tracking): MUST include [tracking_methods] - "How do you currently track your expenses and jobs? [tracking_methods]"
Phase 8 (main_challenge): MUST include [pain_points] - "What's your biggest challenge with the business side? [pain_points]"
Phase 9 (busy_season): MUST include [busy_seasons] - "When's your busiest time of year? [busy_seasons]"
Phase 10 (business_goal): MUST include [business_goals] - "What's your main goal for the next year? [business_goals]"
Phase 11 (email_collection): Ask naturally - "Perfect! Now, what email should I send your profit reports to?"
Phase 12 (password_creation): Be encouraging - "Great! Let's secure your account with a password. Choose something you'll remember."
Phase 13 (completion): MUST include [complete_onboarding] - "Excellent, [name]! I've got a great picture of your business. Your personalized dashboard is ready. Remember, the more data you add, the smarter I get. Ready to dive in? [complete_onboarding]"

SPECIAL UI CONTROLS (USE EXACTLY AS SHOWN):
- [business_types] - Shows contractor type cards
- [years_in_business] - Shows experience level options
- [business_sizes] - Shows business size options
- [service_areas] - Shows service area options
- [customer_types] - Shows customer type options
- [tracking_methods] - Shows current tracking method options
- [pain_points] - Shows challenge cards
- [busy_seasons] - Shows seasonal options
- [business_goals] - Shows business goal options
- [complete_onboarding] - Triggers dashboard transition

CRITICAL: Include these tags EXACTLY as shown. Don't replace them with actual options.

IMPORTANT RULES:
1. Keep the conversation flowing naturally
2. NEVER list the options in your message - the UI cards will show them
3. Keep messages SHORT - just ask the question
4. Each phase should feel like a natural progression, not a survey
5. ALWAYS include the [tag] at the end of your message - this is what triggers the UI cards to appear!

Example: "What type of work do you do? [business_types]" ✓
Wrong: "What type of work do you do?" ✗ (missing tag = no cards appear)

Remember: You're GUIDING them through onboarding, not having an open-ended chat!"""
    else:
        prompt = f"""You are CORA, an AI-powered job costing assistant built specifically for contractors. You are NOT a chatbot talking about CORA - you ARE CORA speaking directly.

YOUR PERSONALITY:
{json.dumps(personality, indent=2)}

CONVERSATION RULES:
{json.dumps(implementation.get("personality_rules", {}), indent=2)}

YOUR KNOWLEDGE BASE:
{json.dumps(CORA_KNOWLEDGE, indent=2)}

CRITICAL GUIDELINES:
1. ALWAYS speak as CORA directly using "I" and "me"
2. Use contractor language naturally - never sound like a salesperson
3. Keep responses to 2-3 sentences unless explaining something complex
4. Include specific numbers and contractor examples
5. Always end with a question or clear next action
6. Focus on their pain points: cash flow, profitability, time savings
7. Emphasize the 30-day free trial (no credit card required)
8. Be warm and encouraging but professional

CONVERSATION FLOW:
- Discovery Phase (messages 1-3): Understand their business and pain points
- Education Phase (messages 3-5): Connect their problems to your solutions
- Conversion Phase (messages 6+): Guide toward free trial signup

Remember: You're their contractor buddy who happens to be AI, not a corporate sales bot. Focus on helping them save time, find profit, and reduce stress."""
    
    return prompt

@cora_chat_enhanced_router.post("/", response_model=ChatResponse)
async def chat_with_enhanced_cora(
    chat_message: ChatMessage,
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle chat messages with enhanced CORA personality"""
    
    # Get visitor ID for rate limiting
    visitor_id = get_visitor_id(request)
    
    # Try to load user's business profile for context
    user_context = {}
    try:
        # Check if user is authenticated via cookie
        access_token = request.cookies.get("access_token")
        if access_token:
            from dependencies.auth import get_current_user_from_token
            from models.business_profile import BusinessProfile
            
            user_email = get_current_user_from_token(access_token, db)
            if user_email:
                # Load business profile
                profile = db.query(BusinessProfile).filter(
                    BusinessProfile.user_email == user_email
                ).first()
                
                if profile:
                    user_context = {
                        "business_name": profile.business_name,
                        "business_type": profile.business_type,
                        "industry": profile.industry,
                        "revenue_range": profile.monthly_revenue_range,
                        "user_email": user_email
                    }
                    
                    # Load detailed onboarding data if available
                    from pathlib import Path
                    import json
                    profile_file = Path(__file__).parent.parent / "data" / "business_profiles" / f"{user_email}.json"
                    if profile_file.exists():
                        with open(profile_file, 'r') as f:
                            onboarding_data = json.load(f)
                            if 'onboardingData' in onboarding_data:
                                user_context.update(onboarding_data['onboardingData'])
    except Exception as e:
        # Log but don't fail - continue without context
        print(f"Could not load user context: {e}")
    
    # Merge user context into metadata
    if user_context:
        if not chat_message.metadata:
            chat_message.metadata = {}
        chat_message.metadata["user_profile"] = user_context
    
    # Check if this is an onboarding conversation
    is_onboarding = chat_message.metadata and chat_message.metadata.get("onboarding", False)
    
    # Check rate limit
    can_chat, remaining = check_rate_limit(visitor_id, is_onboarding)
    if not can_chat:
        raise HTTPException(
            status_code=429, 
            detail="You've reached the free message limit. Sign up for unlimited conversations at coraai.tech!"
        )
    
    # Generate conversation ID if not provided
    conversation_id = chat_message.conversation_id or f"conv_{visitor_id}_{datetime.utcnow().timestamp()}"
    
    # Get conversation history
    history = conversation_history[conversation_id]
    
    # Get stored metadata for this conversation
    stored_metadata = conversation_metadata.get(conversation_id, {})
    
    # Merge with any new metadata
    if chat_message.metadata:
        stored_metadata.update(chat_message.metadata)
    
    # Generate response
    if OPENAI_AVAILABLE and config.OPENAI_API_KEY and config.OPENAI_API_KEY != "your-openai-api-key-here":
        try:
            response_message = await generate_openai_response(
                chat_message.message, 
                history,
                generate_enhanced_system_prompt(stored_metadata),
                stored_metadata
            )
            if response_message is None:
                response_message = generate_enhanced_response(
                    chat_message.message, 
                    history, 
                    stored_metadata
                )
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            response_message = generate_enhanced_response(
                chat_message.message, 
                history, 
                stored_metadata
            )
    else:
        response_message = generate_enhanced_response(
            chat_message.message, 
            history, 
            stored_metadata
        )
    
    # Update conversation history
    history.append({"role": "user", "content": chat_message.message})
    history.append({"role": "assistant", "content": response_message})
    
    # Update rate limit (only for non-onboarding conversations)
    if not is_onboarding:
        conversation_limits[visitor_id]["count"] += 1
        remaining -= 1
    
    # Suggest signup if running low on messages or in conversion phase
    suggest_signup = remaining <= 3 or len(history) > 10
    
    # Prepare response metadata
    response_metadata = {
        "conversation_phase": stored_metadata.get("conversation_phase", "discovery"),
        "detected_contractor_type": stored_metadata.get("contractor_type"),
        "detected_pain_points": stored_metadata.get("pain_points", [])
    }
    
    return ChatResponse(
        message=response_message,
        conversation_id=conversation_id,
        messages_remaining=remaining,
        suggest_signup=suggest_signup,
        metadata=response_metadata
    )

def generate_openai_response_sync(
    message: str, 
    history: List[Dict], 
    system_prompt: str,
    metadata: Dict[str, Any]
) -> Optional[str]:
    """Generate response using OpenAI API with enhanced context (synchronous version)"""
    if not OPENAI_AVAILABLE:
        return None
        
    # Set API key
    openai.api_key = config.OPENAI_API_KEY
    
    # Build messages for OpenAI
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add context about the user if available
    if metadata:
        context_message = f"""Current conversation context:
- Contractor Type: {metadata.get('contractor_type', 'unknown')}
- Business Size: {metadata.get('business_size', 'unknown')}
- Pain Points: {', '.join(metadata.get('pain_points', ['unknown']))}
- Current Tools: {', '.join(metadata.get('current_tools', ['unknown']))}
- Conversation Phase: {metadata.get('conversation_phase', 'discovery')}
- Urgency: {metadata.get('urgency', 'normal')}"""
        messages.append({"role": "system", "content": context_message})
    
    # Add conversation history (limit to last 10 messages)
    messages.extend(history[-10:])
    
    # Add current message
    messages.append({"role": "user", "content": message})
    
    try:
        # Try the new client-based API first
        try:
            from openai import OpenAI
            client = OpenAI(api_key=config.OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=200,  # Slightly longer for complex explanations
                temperature=0.7,  # Balanced personality
                presence_penalty=0.4,  # Encourage variety
                frequency_penalty=0.3  # Reduce repetition
            )
            
            return response.choices[0].message.content.strip()
        except ImportError:
            # Fallback to old API style
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=200,
                temperature=0.7,
                presence_penalty=0.4,
                frequency_penalty=0.3
            )
            return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return None

async def generate_openai_response(
    message: str, 
    history: List[Dict], 
    system_prompt: str,
    metadata: Dict[str, Any]
) -> Optional[str]:
    """Generate response using OpenAI API with enhanced context"""
    if not OPENAI_AVAILABLE:
        return None
        
    # Set API key
    openai.api_key = config.OPENAI_API_KEY
    
    # Build messages for OpenAI
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add context about the user if available
    if metadata:
        context_message = f"""Current conversation context:
- Contractor Type: {metadata.get('contractor_type', 'unknown')}
- Business Size: {metadata.get('business_size', 'unknown')}
- Pain Points: {', '.join(metadata.get('pain_points', ['unknown']))}
- Current Tools: {', '.join(metadata.get('current_tools', ['unknown']))}
- Conversation Phase: {metadata.get('conversation_phase', 'discovery')}
- Urgency: {metadata.get('urgency', 'normal')}"""
        messages.append({"role": "system", "content": context_message})
    
    # Add conversation history (limit to last 10 messages)
    messages.extend(history[-10:])
    
    # Add current message
    messages.append({"role": "user", "content": message})
    
    try:
        # Try the new client-based API first
        try:
            from openai import OpenAI
            client = OpenAI(api_key=config.OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=200,  # Slightly longer for complex explanations
                temperature=0.7,  # Balanced personality
                presence_penalty=0.4,  # Encourage variety
                frequency_penalty=0.3  # Reduce repetition
            )
            
            return response.choices[0].message.content.strip()
        except ImportError:
            # Fallback to old API style
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=200,
                temperature=0.7,
                presence_penalty=0.4,
                frequency_penalty=0.3
            )
            return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return None

@cora_chat_enhanced_router.get("/stats")
async def get_enhanced_chat_stats(request: Request):
    """Get enhanced chat statistics including conversation insights"""
    visitor_id = get_visitor_id(request)
    _, remaining = check_rate_limit(visitor_id)
    
    # Analyze all conversations for patterns
    contractor_types = defaultdict(int)
    pain_points = defaultdict(int)
    conversation_phases = defaultdict(int)
    
    for conv_id, metadata in conversation_metadata.items():
        if metadata.get("contractor_type"):
            contractor_types[metadata["contractor_type"]] += 1
        for pain_point in metadata.get("pain_points", []):
            pain_points[pain_point] += 1
        conversation_phases[metadata.get("conversation_phase", "unknown")] += 1
    
    return {
        "messages_remaining": remaining,
        "total_conversations": len(conversation_history),
        "visitor_id": visitor_id,
        "insights": {
            "contractor_types": dict(contractor_types),
            "pain_points": dict(pain_points),
            "conversation_phases": dict(conversation_phases)
        }
    }

@cora_chat_enhanced_router.post("/simulate-contractor")
async def simulate_contractor_conversation(
    contractor_type: str,
    scenario: str = "first_visit"
):
    """Simulate a contractor conversation for testing (admin endpoint)"""
    
    # Get the appropriate script
    scripts = CONTRACTOR_PERSONALITY.get("conversation_scripts", {})
    
    if scenario == "first_visit":
        visitor_scripts = scripts.get("first_time_visitors", {})
        script = visitor_scripts.get(contractor_type, {})
        
        return {
            "scenario": scenario,
            "contractor_type": contractor_type,
            "greeting": script.get("greeting", "Default greeting"),
            "pain_point_discovery": script.get("pain_point_discovery", "Default discovery"),
            "value_prop": script.get("value_prop", "Default value prop"),
            "trial_offer": script.get("trial_offer", "Default trial offer")
        }
    
    return {"error": "Scenario not found"}

# Export the router
enhanced_chat_router = cora_chat_enhanced_router