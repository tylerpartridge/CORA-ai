#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/cora_chat.py
🎯 PURPOSE: CORA v1 - Original AI-powered sales & support chat
📝 STATUS: ACTIVE (Legacy) - Handles /api/cora-chat endpoints
🔗 IMPORTS: FastAPI, OpenAI, rate limiting, knowledge base
📤 EXPORTS: cora_chat_router with sales-focused conversation endpoints
🔄 PATTERN: Knowledge-enhanced conversational AI
⚡ UPGRADE: For enhanced version with emotional intelligence, see cora_chat_enhanced.py
📝 TODOS: Add analytics tracking, A/B test responses

💡 AI HINT: The knowledge base is expandable - add new data to cora_knowledge_base.json
⚠️ NEVER: Share pricing without mentioning Founders Pricing (limited to first 1,000 users)
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import os
import json
import hashlib
import logging
from collections import defaultdict
from pathlib import Path
from models import AnalyticsLog
from models import get_db

logger = logging.getLogger(__name__)

# OpenAI import
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    # Only print warning in debug mode
    if os.getenv('DEBUG', '').lower() == 'true':
        print("Warning: OpenAI module not installed. Run 'pip install openai' to enable AI responses.")
    OPENAI_AVAILABLE = False
    
from config import config

# Load CORA Sales Intelligence Knowledge Base
KNOWLEDGE_BASE_PATH = Path(__file__).parent.parent / "data" / "cora_knowledge_base.json"
try:
    with open(KNOWLEDGE_BASE_PATH, 'r') as f:
        CORA_KNOWLEDGE = json.load(f)
except FileNotFoundError:
    print(f"Warning: Knowledge base not found at {KNOWLEDGE_BASE_PATH}")
    CORA_KNOWLEDGE = {}

# Create router
cora_chat_router = APIRouter(prefix="/api/cora-chat", tags=["cora-chat"])

# In-memory storage for rate limiting (replace with Redis in production)
conversation_limits = defaultdict(lambda: {"count": 0, "reset_time": datetime.utcnow()})
conversation_history = defaultdict(list)

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    messages_remaining: int
    suggest_signup: bool = False

# Rate limiting helper
def get_visitor_id(request: Request) -> str:
    """Generate a unique visitor ID based on IP and user agent"""
    ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    return hashlib.md5(f"{ip}:{user_agent}".encode()).hexdigest()

def check_rate_limit(visitor_id: str) -> tuple[bool, int]:
    """Check if visitor has messages remaining"""
    now = datetime.utcnow()
    visitor_data = conversation_limits[visitor_id]
    
    # Reset if 24 hours have passed
    if now > visitor_data["reset_time"] + timedelta(hours=24):
        visitor_data["count"] = 0
        visitor_data["reset_time"] = now
    
    remaining = 10 - visitor_data["count"]
    return remaining > 0, remaining

# Knowledge base helper functions
def get_pricing_info(tier_name: Optional[str] = None) -> Dict[str, Any]:
    """Get pricing information from knowledge base"""
    if not CORA_KNOWLEDGE:
        return {}
    
    pricing = CORA_KNOWLEDGE.get("pricing", {})
    if tier_name:
        for tier in pricing.get("tiers", []):
            if tier["name"].lower() == tier_name.lower():
                return tier
    return pricing

def get_feature_info(feature_name: str) -> Dict[str, Any]:
    """Get specific feature information"""
    if not CORA_KNOWLEDGE:
        return {}
    
    features = CORA_KNOWLEDGE.get("features", {})
    # Search in core features
    for category in features.values():
        if isinstance(category, dict):
            for key, feature in category.items():
                if feature_name.lower() in key.lower() or feature_name.lower() in str(feature).lower():
                    return feature
    return {}

def get_integration_info(integration_name: str) -> Dict[str, Any]:
    """Get integration setup information"""
    if not CORA_KNOWLEDGE:
        return {}
    
    integrations = CORA_KNOWLEDGE.get("integrations_guide", {})
    for key, integration in integrations.items():
        if integration_name.lower() in key.lower() or integration_name.lower() in integration.get("name", "").lower():
            return integration
    return {}

def get_comparison_info(competitor: str) -> List[str]:
    """Get comparison advantages"""
    if not CORA_KNOWLEDGE:
        return []
    
    comparisons = CORA_KNOWLEDGE.get("comparisons", {})
    for key, comparison in comparisons.items():
        if competitor.lower() in key.lower():
            return comparison.get("advantages", [])
    return []

# Enhanced CORA Sales Intelligence System Prompt
CORA_SYSTEM_PROMPT = f"""You are CORA, an AI-powered Financial Wellness Companion and sales representative for CORA AI. You help stressed entrepreneurs save 20+ hours per month while reducing financial anxiety.

YOUR KNOWLEDGE BASE:
{json.dumps(CORA_KNOWLEDGE, indent=2)}

YOUR PERSONALITY:
- Warm, empathetic, and genuinely caring about their financial stress
- Professional yet conversational (like a knowledgeable friend, not a salesperson)
- Solution-focused - always connect their pain points to how CORA helps
- Confident in CORA's value but never pushy
- Use "I" statements - you ARE CORA, not talking about CORA

CONVERSATION GUIDELINES:

1. DISCOVERY PHASE (First 2-3 messages):
   - Understand their specific pain points
   - Ask about their current financial management process
   - Identify time wasters and stress points
   - Show genuine empathy for their struggles

2. EDUCATION PHASE (Messages 3-5):
   - Connect their specific problems to CORA's solutions
   - Share relevant success stories from the knowledge base
   - Highlight time savings (20+ hours/month)
   - Mention specific features that address their needs

3. CONVERSION PHASE (Messages 6+):
   - Address any objections using the knowledge base
   - Emphasize the 30-day free trial (no credit card required)
   - Create urgency by quantifying their current losses
   - Guide them to take action

KEY SELLING POINTS TO EMPHASIZE:
- 30-day free trial with no credit card required
- Save 20+ hours per month (worth $1000+ at $50/hour)
- Most users find $2000+ in missed tax deductions
- Voice-first design - capture expenses in seconds
- Designed for entrepreneurs, not accountants
- Persistent AI memory - I get smarter about your business over time

PRICING GUIDANCE:
- Lead with Founders Pricing (limited time)
- $47 Basic, $97 Professional (most popular), $197 Enterprise
- Regular pricing: $79, $149, $299 (emphasize savings)
- Compare to manual bookkeeping costs: "Save $500+ monthly"
- Always mention "First 1,000 contractors only - lock in forever"

OBJECTION HANDLING:
- Price: Compare to time saved, tax deductions found, peace of mind value
- Time to learn: "10-minute setup, then I learn YOUR way of working"
- Already using QuickBooks: "I'm 10x faster and designed for entrepreneurs, not accountants"
- Security concerns: "Bank-level encryption, SOC 2 compliant, your data is never sold"

RESPONSE STYLE:
- Keep responses to 2-3 sentences for easy reading
- Use natural, conversational language
- Include specific numbers and examples when possible
- End with a question to keep engagement high
- Be enthusiastic about helping them succeed

Remember: You're not just selling software - you're offering peace of mind and 20+ hours of their life back every month."""

@cora_chat_router.post("/", response_model=ChatResponse)
async def chat_with_cora(
    chat_message: ChatMessage,
    request: Request
):
    """Handle chat messages with CORA"""
    
    # Get visitor ID for rate limiting
    visitor_id = get_visitor_id(request)
    
    # Check rate limit
    can_chat, remaining = check_rate_limit(visitor_id)
    if not can_chat:
        raise HTTPException(
            status_code=429, 
            detail="You've reached the free message limit. Sign up to continue chatting with CORA!"
        )
    
    # Generate conversation ID if not provided
    conversation_id = chat_message.conversation_id or f"conv_{visitor_id}_{datetime.utcnow().timestamp()}"
    
    # Get conversation history
    history = conversation_history[conversation_id]
    
    # Debug logging (only in development)
    if os.getenv('DEBUG', '').lower() == 'true':
        print(f"OPENAI_AVAILABLE: {OPENAI_AVAILABLE}")
        print(f"API Key exists: {bool(config.OPENAI_API_KEY)}")
        print(f"API Key not default: {config.OPENAI_API_KEY != 'your-openai-api-key-here' if config.OPENAI_API_KEY else False}")
    
    # Use OpenAI if available and configured, otherwise use mock responses
    if OPENAI_AVAILABLE and config.OPENAI_API_KEY and config.OPENAI_API_KEY != "your-openai-api-key-here":
        try:
            if os.getenv('DEBUG', '').lower() == 'true':
                print("Attempting OpenAI call...")
            response_message = await generate_openai_response(
                chat_message.message, 
                history,
                CORA_SYSTEM_PROMPT
            )
            if response_message is None:
                # OpenAI not available, use fallback
                response_message = generate_mock_response(chat_message.message, len(history))
            elif os.getenv('DEBUG', '').lower() == 'true':
                print("OpenAI call successful!")
        except Exception as e:
            if os.getenv('DEBUG', '').lower() == 'true':
                print(f"OpenAI error, falling back to mock: {e}")
            response_message = generate_mock_response(chat_message.message, len(history))
    else:
        if os.getenv('DEBUG', '').lower() == 'true':
            print("Using mock responses - OpenAI not configured")
        response_message = generate_mock_response(chat_message.message, len(history))
    
    # Update conversation history
    history.append({"role": "user", "content": chat_message.message})
    history.append({"role": "assistant", "content": response_message})
    
    # Update rate limit
    conversation_limits[visitor_id]["count"] += 1
    remaining -= 1
    
    # Suggest signup if running low on messages
    suggest_signup = remaining <= 3

    # Log to AnalyticsLog
    analytics = AnalyticsLog(
        user_id=visitor_id,  # Using visitor_id as string
        query=chat_message.message,
        response_status="success",
        variant="mock" if not OPENAI_AVAILABLE or not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "your-openai-api-key-here" else "openai"
    )
    db = next(get_db())
    db.add(analytics)
    db.commit()
    
    return ChatResponse(
        message=response_message,
        conversation_id=conversation_id,
        messages_remaining=remaining,
        suggest_signup=suggest_signup
    )

def generate_mock_response(message: str, conversation_length: int) -> str:
    """Generate knowledge-based sales responses using CSIS"""
    
    message_lower = message.lower()
    
    # First message - warm introduction
    if conversation_length == 0:
        return "I'm CORA, and I help contractors save $500+ monthly on bookkeeping - with AI-powered job costing! Founders Pricing available for first 1,000 contractors only. What's your biggest expense tracking challenge?"
    
    # Pricing questions - use knowledge base
    if any(word in message_lower for word in ["price", "cost", "expensive", "afford", "how much", "pricing"]):
        pricing = get_pricing_info()
        return "Founders Pricing: $47-197/month (first 1,000 contractors only)! Regular pricing will be $79-299. Sarah saved $1,847 in manual bookkeeping costs her first month. Lock in your Founders rate forever - which plan interests you?"
    
    # Specific tier questions
    if "basic" in message_lower:
        tier = get_pricing_info("Basic")
        return "Basic at $47/month (Founders Pricing) includes essential profit tracking - perfect for getting started! Regular pricing will be $79. Most contractors prefer Professional at $97. Lock in Founders rate forever?"
    
    if "pro" in message_lower or "professional" in message_lower:
        tier = get_pricing_info("Professional")
        return "Professional at $97/month (Founders Pricing) is our most popular - includes AI profit intelligence and saves contractors $500+ monthly! Regular pricing will be $149. Ready to lock in your Founders rate?"
    
    # QuickBooks comparison
    if "quickbooks" in message_lower or "quickbook" in message_lower:
        advantages = get_comparison_info("quickbooks")
        return "QuickBooks is for accountants - I'm for busy entrepreneurs like you! Lisa switched and cut her finance time by 80% with voice entry. Import your QuickBooks data and try free for 30 days?"
    
    # Integration questions
    if any(word in message_lower for word in ["integrate", "connect", "sync", "work with", "compatible"]):
        return "I sync with QuickBooks, Stripe, PayPal, and 10,000+ banks - everything flows in automatically! Mike connected 5 accounts in minutes during his free trial. What tools do you need integrated?"
    
    # Tax concerns - use testimonials
    if any(word in message_lower for word in ["tax", "deduction", "irs", "audit", "write off"]):
        testimonials = CORA_KNOWLEDGE.get("testimonials", {}).get("success_stories", [])
        return "I track deductions automatically - Mike found $2,134 in missed write-offs his first month! Plus quarterly tax estimates so no surprises. Try free for 30 days and see what you're missing?"
    
    # Time savings emphasis
    if any(word in message_lower for word in ["time", "busy", "hours", "quick", "fast"]):
        return "Setup takes 10 minutes, then I save you 20+ hours monthly! Lisa went from 8 hours to 15 minutes weekly on finances. Free 30-day trial - what's stopping you from getting your time back?"
    
    # Voice feature interest
    if any(word in message_lower for word in ["voice", "speak", "talk", "hands free"]):
        return "Just say 'gas for client meeting, $52' and I track everything - even mileage for tax deductions! No typing, no receipts. Try it free for 30 days and never miss an expense again!"
    
    # Construction/Job queries - NEW FEATURE
    if any(phrase in message_lower for phrase in ["show me the", "how much on", "what's the profit", "job cost", "project status"]):
        # Extract job name patterns
        job_patterns = [
            r"show me the (.+?) job",
            r"how much on (.+?)[\?\.]",
            r"what's the profit on (.+?)[\?\.]",
            r"(.+?) job cost",
            r"(.+?) project"
        ]
        
        import re
        job_name = None
        for pattern in job_patterns:
            match = re.search(pattern, message_lower)
            if match:
                job_name = match.group(1).strip()
                break
        
        if job_name:
            # Simulate job data response (in production, would query database)
            return f"The {job_name.title()} job: $12,847 spent so far, quoted at $18,500, current profit $5,653 (31% margin). Want me to break down the costs by category?"
        else:
            return "I track all your job costs in real-time! Just ask 'Show me the Johnson bathroom job' or 'How much on the Smith kitchen?' and I'll give you instant profit numbers. Which job would you like to see?"
    
    # Construction-specific questions
    if any(word in message_lower for word in ["contractor", "construction", "job site", "materials", "crew", "subcontractor"]):
        return "I'm built specifically for contractors! Track jobs from your truck, see real-time profit margins, never miss a Home Depot receipt. Steve saved $3,200 finding missed deductions. Try free for 30 days?"
    
    # Security concerns
    if any(word in message_lower for word in ["secure", "safe", "privacy", "data", "security"]):
        security = CORA_KNOWLEDGE.get("technical_details", {}).get("security", {})
        return "Bank-level encryption, SOC 2 compliant, and 6,000+ entrepreneurs trust me with their finances. Your data is never sold! Start with manual entry during your free trial if you prefer?"
    
    # Stress and overwhelm
    if any(word in message_lower for word in ["stress", "overwhelm", "anxious", "worried", "scared", "peace"]):
        return "Financial stress is exhausting - I get it! That's why I focus on peace of mind, not just numbers. Try free for 30 days and feel the difference. What's your biggest financial worry?"
    
    # Feature questions
    if any(word in message_lower for word in ["feature", "can you", "do you", "what can", "capabilities"]):
        return "Voice tracking, tax estimates, receipt scanning - I do it all! Sarah says I'm like having a CFO in her pocket. Try free for 30 days and see which feature saves you most time!"
    
    # Comparison shopping
    if any(word in message_lower for word in ["compare", "versus", "vs", "alternative", "better than"]):
        return "I'm built for entrepreneurs, not accountants - saving you 20+ hours monthly with zero learning curve! Mike switched from Excel and found $2,134 in deductions. Try free for 30 days?"
    
    # Getting started questions
    if any(word in message_lower for word in ["start", "begin", "setup", "onboard", "how do i"]):
        return "Setup takes 10 minutes: sign up (no credit card), connect your bank, and I start saving you time immediately! Free 30-day trial with full features. Ready to reduce your financial stress?"
    
    # Objection: Too busy to switch
    if any(word in message_lower for word in ["switch", "migrate", "change", "transition"]):
        return "I import your existing data automatically - switching takes 10 minutes! Lisa switched from QuickBooks and saves a full day monthly. Free 30-day trial to test it yourself?"
    
    # Closing/conversion (after engagement)
    if conversation_length > 5:
        return "Based on our chat, I could save you $500+ monthly on manual bookkeeping like I did for Mike! Founders Pricing is limited to first 1,000 contractors - lock in your rate forever. Ready to secure your spot?"
    
    # Trial emphasis
    if any(word in message_lower for word in ["trial", "try", "test", "demo"]):
        return "Yes! 30-day free trial with ALL Pro features, no credit card required. Most users know within a week they'll never go back. Ready to save 20+ hours monthly?"
    
    # Default response - stay curious and helpful
    questions = [
        "Tell me more about your current financial workflow - what takes the most time?",
        "What would you do with an extra 20 hours every month?",
        "What's your biggest financial pain point right now?",
        "How do you currently track business expenses?",
        "What made you start looking for a financial solution?"
    ]
    
    # Rotate through engaging questions based on conversation length
    return questions[conversation_length % len(questions)]

async def generate_openai_response(
    message: str, 
    history: List[Dict], 
    system_prompt: str
) -> str:
    """Generate response using OpenAI API"""
    if not OPENAI_AVAILABLE:
        # Return None to trigger fallback instead of raising exception
        return None
        
    # Set API key
    openai.api_key = config.OPENAI_API_KEY
    
    # Build messages for OpenAI
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history (limit to last 10 messages to control token usage)
    messages.extend(history[-10:])
    
    # Add current message
    messages.append({"role": "user", "content": message})
    
    # Call OpenAI API with comprehensive error handling
    try:
        # Try the new client-based API first (OpenAI v1.0+)
        try:
            from openai import OpenAI
            client = OpenAI(api_key=config.OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,  # Keep responses concise
                temperature=0.8,  # Friendly but professional
                presence_penalty=0.3,  # Encourage variety
                frequency_penalty=0.2  # Reduce repetition
            )
            
            return response.choices[0].message.content.strip()
        except ImportError as e:
            logger.error(f"Failed to import OpenAI client - likely using old API version: {str(e)}")
            # Fallback to old API style (OpenAI < v1.0)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,  # Keep responses concise
                temperature=0.8,  # Friendly but professional
                presence_penalty=0.3,  # Encourage variety
                frequency_penalty=0.2  # Reduce repetition
            )
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise
            
            return response.choices[0].message.content.strip()
    except Exception as e:
        # Log error only in debug mode
        if os.getenv('DEBUG', '').lower() == 'true':
            print(f"OpenAI API error: {str(e)}")
        # Return None to trigger fallback
        return None

@cora_chat_router.get("/stats")
async def get_chat_stats(request: Request):
    """Get chat statistics (admin endpoint - add auth in production)"""
    visitor_id = get_visitor_id(request)
    _, remaining = check_rate_limit(visitor_id)
    
    return {
        "messages_remaining": remaining,
        "total_conversations": len(conversation_history),
        "visitor_id": visitor_id
    }

@cora_chat_router.post("/reload-knowledge")
async def reload_knowledge_base():
    """Reload the knowledge base from file (admin endpoint - add auth in production)"""
    global CORA_KNOWLEDGE, CORA_SYSTEM_PROMPT
    
    try:
        with open(KNOWLEDGE_BASE_PATH, 'r') as f:
            CORA_KNOWLEDGE = json.load(f)
        
        # Regenerate system prompt with new knowledge
        CORA_SYSTEM_PROMPT = f"""You are CORA, an AI-powered Financial Wellness Companion and sales representative for CORA AI. You help stressed entrepreneurs save 20+ hours per month while reducing financial anxiety.

YOUR KNOWLEDGE BASE:
{json.dumps(CORA_KNOWLEDGE, indent=2)}

YOUR PERSONALITY:
- Warm, empathetic, and genuinely caring about their financial stress
- Professional yet conversational (like a knowledgeable friend, not a salesperson)
- Solution-focused - always connect their pain points to how CORA helps
- Confident in CORA's value but never pushy
- Use "I" statements - you ARE CORA, not talking about CORA

CONVERSATION GUIDELINES:

1. DISCOVERY PHASE (First 2-3 messages):
   - Understand their specific pain points
   - Ask about their current financial management process
   - Identify time wasters and stress points
   - Show genuine empathy for their struggles

2. EDUCATION PHASE (Messages 3-5):
   - Connect their specific problems to CORA's solutions
   - Share relevant success stories from the knowledge base
   - Highlight time savings (20+ hours/month)
   - Mention specific features that address their needs

3. CONVERSION PHASE (Messages 6+):
   - Address any objections using the knowledge base
   - Emphasize the 30-day free trial (no credit card required)
   - Create urgency by quantifying their current losses
   - Guide them to take action

KEY SELLING POINTS TO EMPHASIZE:
- 30-day free trial with no credit card required
- Save 20+ hours per month (worth $1000+ at $50/hour)
- Most users find $2000+ in missed tax deductions
- Voice-first design - capture expenses in seconds
- Designed for entrepreneurs, not accountants
- Persistent AI memory - I get smarter about your business over time

PRICING GUIDANCE:
- Lead with Founders Pricing (limited time)
- $47 Basic, $97 Professional (most popular), $197 Enterprise
- Regular pricing: $79, $149, $299 (emphasize savings)
- Compare to manual bookkeeping costs: "Save $500+ monthly"
- Always mention "First 1,000 contractors only - lock in forever"

OBJECTION HANDLING:
- Price: Compare to time saved, tax deductions found, peace of mind value
- Time to learn: "10-minute setup, then I learn YOUR way of working"
- Already using QuickBooks: "I'm 10x faster and designed for entrepreneurs, not accountants"
- Security concerns: "Bank-level encryption, SOC 2 compliant, your data is never sold"

RESPONSE STYLE:
- Keep responses to 2-3 sentences for easy reading
- Use natural, conversational language
- Include specific numbers and examples when possible
- End with a question to keep engagement high
- Be enthusiastic about helping them succeed

Remember: You're not just selling software - you're offering peace of mind and 20+ hours of their life back every month."""
        
        return {
            "success": True,
            "message": "Knowledge base reloaded successfully",
            "knowledge_items": len(CORA_KNOWLEDGE.keys()) if CORA_KNOWLEDGE else 0
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to reload knowledge base: {str(e)}"
        }

@cora_chat_router.get("/knowledge-summary")
async def get_knowledge_summary():
    """Get a summary of the current knowledge base (admin endpoint)"""
    if not CORA_KNOWLEDGE:
        return {"error": "Knowledge base not loaded"}
    
    summary = {
        "pricing_tiers": len(CORA_KNOWLEDGE.get("pricing", {}).get("tiers", [])),
        "feature_categories": list(CORA_KNOWLEDGE.get("features", {}).keys()),
        "integrations": len(CORA_KNOWLEDGE.get("integrations_guide", {})),
        "testimonials": len(CORA_KNOWLEDGE.get("testimonials", {}).get("success_stories", [])),
        "faq_count": len(CORA_KNOWLEDGE.get("faq", {}).get("common_questions", [])),
        "comparisons": list(CORA_KNOWLEDGE.get("comparisons", {}).keys())
    }
    
    return summary