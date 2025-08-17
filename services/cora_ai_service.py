"""
CORA AI Service - Makes CORA truly intelligent
Integrates AI APIs with personality framework for dynamic, contextual responses
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import openai
from openai import AsyncOpenAI
from pathlib import Path
from typing import Any as _Any
from config import config

class CORAAIService:
    def __init__(self):
        # Initialize OpenAI client only if API key is available
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key != 'your-openai-api-key-here':
            self.client = AsyncOpenAI(api_key=api_key)
            self.ai_enabled = True
        else:
            self.client = None
            self.ai_enabled = False
            print("⚠️  OpenAI API key not configured. CORA will use fallback responses.")
        
        self.conversation_history = []
        
        # Load comprehensive conversation implementation
        self.conversation_rules = self._load_conversation_implementation()
        
        self.personality_context = {
            "name": "CORA",
            "role": "AI Profit Assistant",
            "personality": "friendly, professional, construction-savvy, proactive",
            "expertise": "profit tracking, cost analysis, business optimization, construction industry",
            "communication_style": "conversational, helpful, encouraging, with occasional humor"
        }
    
    def _load_conversation_implementation(self) -> Dict:
        """Load the comprehensive conversation implementation rules"""
        try:
            conversation_file = Path("data/cora_conversation_implementation.json")
            if conversation_file.exists():
                with open(conversation_file, 'r') as f:
                    return json.load(f)
            else:
                print("[WARNING] Conversation implementation file not found, using basic rules")
                return self._get_basic_conversation_rules()
        except Exception as e:
            print(f"[WARNING] Error loading conversation implementation: {e}")
            return self._get_basic_conversation_rules()
    
    def _get_basic_conversation_rules(self) -> Dict:
        """Fallback basic conversation rules"""
        return {
            "implementation_guide": {
                "personality_rules": {
                    "always": [
                        "Use 'I' and 'me' - CORA is speaking directly",
                        "Keep responses under 3 sentences unless explaining something complex",
                        "Include specific numbers and examples whenever possible",
                        "End with a question or clear next action",
                        "Use contractor terminology naturally"
                    ],
                    "never": [
                        "Use corporate jargon or marketing speak",
                        "Make contractors feel stupid about technology",
                        "Ignore the time pressure they're under"
                    ]
                }
            }
        }
        
    async def generate_response(self, 
                              user_message: str, 
                              business_context: Dict = None,
                              personality_state: Dict = None) -> str:
        """
        Generate intelligent response using AI API with personality context
        """
        # Check if AI is enabled
        if not self.ai_enabled or not self.client:
            return self._fallback_response(user_message, personality_state)

    async def generate_enhanced_response(
        self,
        user_message: str,
        user: _Any = None,
        db: _Any = None,
        business_context: Dict | None = None,
        personality_state: Dict | None = None,
    ) -> str:
        """Generate response augmented with orchestrator intelligence when user context is available."""
        # Start with base context
        merged_business_context = business_context.copy() if business_context else {}
        try:
            if user is not None and db is not None:
                # Prefer enhanced orchestrator if enabled
                if getattr(config, "ENABLE_ENHANCED_ORCHESTRATOR", False):
                    from services.enhanced_orchestrator import EnhancedIntelligenceOrchestrator as _Orchestrator
                    orchestration_type = "enhanced"
                else:
                    from services.intelligence_orchestrator import IntelligenceOrchestrator as _Orchestrator
                    orchestration_type = "base"

                orchestrator = _Orchestrator(user, db)
                unified = await orchestrator.orchestrate_intelligence()

                orchestrated_context = {
                    "orchestration_type": orchestration_type,
                    "intelligence_score": unified.get("intelligence_score", 0),
                    "active_insights": len(unified.get("primary_signals", [])),
                    "top_insight": (unified.get("primary_signals", [{}])[0] or {}).get("title") if unified.get("primary_signals") else None,
                    "emotional_state": (unified.get("emotional_awareness", {}) or {}).get("detected_state", "neutral"),
                    "stress_level": (unified.get("emotional_awareness", {}) or {}).get("stress_level", 0),
                    "care_suggestion": None,
                }
                care_ops = (unified.get("emotional_awareness", {}) or {}).get("care_opportunities") or []
                if care_ops:
                    orchestrated_context["care_suggestion"] = (care_ops[0] or {}).get("suggestion")

                # Merge into business context for personality/system prompt
                merged_business_context.update({
                    "orchestrated_intelligence": orchestrated_context,
                    "user_is_stressed": orchestrated_context["stress_level"] > 7,
                    "should_simplify": orchestrated_context["emotional_state"] in [
                        "overwhelmed", "stressed", "anxious"
                    ],
                })
        except Exception:
            # If orchestration fails, proceed with base response silently
            pass

        # Defer to normal response generation with enriched context
        return await self.generate_response(
            user_message=user_message,
            business_context=merged_business_context or business_context,
            personality_state=personality_state,
        )
        
        try:
            # Build the conversation context with enhanced personality
            system_prompt = self._build_enhanced_system_prompt(business_context, personality_state)
            messages = self._build_messages(user_message, system_prompt)
            
            # Generate response from AI
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using GPT-4o-mini for cost efficiency
                messages=messages,
                max_tokens=300,
                temperature=0.7,  # Slightly creative but focused
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Add personality enhancements with conversation rules
            enhanced_response = self._enhance_with_conversation_rules(ai_response, user_message, personality_state)
            
            # Update conversation history
            self.conversation_history.append({
                "user": user_message,
                "cora": enhanced_response,
                "timestamp": datetime.now().isoformat()
            })
            
            return enhanced_response
            
        except Exception as e:
            print(f"AI Service Error: {e}")
            # Fallback to personality-based response
            return self._fallback_response(user_message, personality_state)
    
    def _build_enhanced_system_prompt(self, business_context: Dict = None, personality_state: Dict = None) -> str:
        """Build comprehensive system prompt with conversation implementation rules"""
        
        # Get personality rules from conversation implementation
        personality_rules = self.conversation_rules.get("implementation_guide", {}).get("personality_rules", {})
        always_rules = personality_rules.get("always", [])
        never_rules = personality_rules.get("never", [])
        
        # Get adaptive responses for different contractor types
        adaptive_responses = self.conversation_rules.get("implementation_guide", {}).get("adaptive_responses", {})
        
        # Build the enhanced prompt
        base_prompt = f"""You are CORA, a friendly AI assistant who helps construction contractors. You're chatting with someone through the chat widget on your company's website - they're already here browsing the site.

You know construction work is tough and managing job costs is a pain. Your company built some advanced AI technology that can track job profitability in real-time, predict cash flow problems, and even detect when contractors are stressed.

You have three pricing plans: Basic ($47/month), Professional ($97/month - most popular), and Enterprise ($197/month). All come with a 30-day free trial, no credit card required.

Since they're already on the website, if they want to start their free trial, they can just click the "Get Started" button in the navigation or "Start Free Trial" button right here on the page.

EMAIL CAPABILITIES YOU HAVE:
- Professional email system is configured (SendGrid) 
- Automatic welcome emails when users sign up
- Password reset emails for account recovery
- Can send PDF reports as email attachments
- Smart verification: instant access in development, email verification for production security
- Email notifications for job alerts, budget warnings, and weekly summaries (coming soon)

PERSONALITY RULES - ALWAYS FOLLOW:
{chr(10).join(f"- {rule}" for rule in always_rules)}

PERSONALITY RULES - NEVER DO:
{chr(10).join(f"- {rule}" for rule in never_rules)}

CONTRACTOR-SPECIFIC KNOWLEDGE:
{self._build_contractor_knowledge(adaptive_responses)}

IMPORTANT: Talk like a normal person. Never echo back what they just said:

BAD responses (sound like a bot):
- "It sounds like you're involved in building restoration!" 
- "I see you do plumbing work!"
- "Hey there! I see you're a handyman!"

GOOD responses (sound human):
- "Building restoration - that's fascinating work!"
- "Oh nice, restoration work! That must involve some really interesting projects."
- "Plumbing - that's solid work! What kind of projects do you focus on?"

Remember: You're talking to contractors who are busy and stressed about their business. Be direct, helpful, and show you understand their world."""
        
        return base_prompt
    
    def _build_contractor_knowledge(self, adaptive_responses: Dict) -> str:
        """Build contractor-specific knowledge from conversation implementation"""
        knowledge_parts = []
        
        # Add contractor size knowledge
        by_size = adaptive_responses.get("by_contractor_size", {})
        for size, info in by_size.items():
            knowledge_parts.append(f"{size.replace('_', ' ').title()}: {info.get('focus', '')} - {info.get('key_message', '')}")
        
        # Add trade-specific knowledge
        by_trade = adaptive_responses.get("by_trade", {})
        for trade, info in by_trade.items():
            pain_points = info.get("common_pain_points", [])
            if pain_points:
                knowledge_parts.append(f"{trade.title()}: Common challenges include {', '.join(pain_points[:2])}")
        
        return chr(10).join(knowledge_parts) if knowledge_parts else "General construction knowledge and business optimization."
    
    def _enhance_with_conversation_rules(self, ai_response: str, user_message: str, personality_state: Dict = None) -> str:
        """Enhance AI response with conversation implementation rules"""
        
        # Get special situations and crisis support
        special_situations = self.conversation_rules.get("special_situations", {})
        
        # Check for crisis indicators
        crisis_response = self._check_crisis_support(user_message, special_situations)
        if crisis_response:
            return crisis_response
        
        # Check for re-engagement opportunities
        re_engagement = self._check_re_engagement(user_message, special_situations)
        if re_engagement:
            return re_engagement
        
        # Apply personality enhancements
        enhanced = self._enhance_with_personality(ai_response, personality_state)
        
        return enhanced
    
    def _check_crisis_support(self, user_message: str, special_situations: Dict) -> Optional[str]:
        """Check if user needs crisis support and provide appropriate response"""
        crisis_scripts = special_situations.get("crisis_support_scripts", {})
        
        # Check for crisis indicators
        crisis_indicators = [
            "stress", "overwhelmed", "can't keep up", "drowning", "too much",
            "failing", "losing money", "going broke", "can't pay", "behind",
            "exhausted", "burned out", "quitting", "giving up"
        ]
        
        user_lower = user_message.lower()
        for indicator in crisis_indicators:
            if indicator in user_lower:
                # Find appropriate crisis response
                for crisis_type, response in crisis_scripts.items():
                    if any(word in user_lower for word in crisis_type.split('_')):
                        return f"{response.get('recognition', 'I hear you.')} {response.get('guidance', 'Let me help you get back on track.')} {response.get('tools', 'I can show you exactly where your money is going.')}"
        
        return None
    
    def _check_re_engagement(self, user_message: str, special_situations: Dict) -> Optional[str]:
        """Check for re-engagement opportunities"""
        re_engagement = special_situations.get("re_engagement", {})
        
        # Check for trial expired indicators
        trial_indicators = ["trial", "expired", "didn't work", "didn't continue"]
        user_lower = user_message.lower()
        
        if any(indicator in user_lower for indicator in trial_indicators):
            trial_response = re_engagement.get("trial_expired", {})
            return f"{trial_response.get('friendly', 'Hey!')} {trial_response.get('address_concern', 'What held you back?')} {trial_response.get('special_offer', 'Come back and I\'ll give you another 14 days free.')}"
        
        return None
    
    def _build_system_prompt(self, business_context: Dict = None, personality_state: Dict = None) -> str:
        """Build comprehensive system prompt for CORA's AI personality"""
        
        base_prompt = f"""You are CORA, a friendly AI assistant who helps construction contractors. You're chatting with someone through the chat widget on your company's website - they're already here browsing the site.

You know construction work is tough and managing job costs is a pain. Your company built some advanced AI technology that can track job profitability in real-time, predict cash flow problems, and even detect when contractors are stressed.

You have three pricing plans: Basic ($47/month), Professional ($97/month - most popular), and Enterprise ($197/month). All come with a 30-day free trial, no credit card required.

Since they're already on the website, if they want to start their free trial, they can just click the "Get Started" button in the navigation or "Start Free Trial" button right here on the page.

EMAIL CAPABILITIES YOU HAVE:
- Professional email system is configured (SendGrid) 
- Automatic welcome emails when users sign up
- Password reset emails for account recovery
- Can send PDF reports as email attachments
- Smart verification: instant access in development, email verification for production security
- Email notifications for job alerts, budget warnings, and weekly summaries (coming soon)

IMPORTANT: Talk like a normal person. Never echo back what they just said:

BAD responses (sound like a bot):
- "It sounds like you're involved in building restoration!" 
- "I see you do plumbing work!"
- "Hey there! I see you're a handyman!"

GOOD responses (sound human):
- "Building restoration - that's fascinating work!"
- "Oh nice, restoration work! That must involve some really interesting projects."
- "Cool! I bet every restoration project is totally different."

Don't repeat their words back to them. Instead, respond with genuine interest like you would in a real conversation.
"""
        
        if business_context:
            base_prompt += f"""
- Current profit score: {business_context.get('profit_score', 'Unknown')}
- Recent expenses: {business_context.get('recent_expenses', [])}
- Business type: {business_context.get('business_type', 'Construction')}
- Relationship level: {personality_state.get('relationship_level', 1) if personality_state else 1}
"""
        
        base_prompt += """

Just be yourself and have a normal conversation. You know this stuff well, so share it naturally when it's relevant.
"""
        
        return base_prompt
    
    def _build_messages(self, user_message: str, system_prompt: str) -> List[Dict]:
        """Build messages array for AI API call"""
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add recent conversation history (last 5 exchanges)
        recent_history = self.conversation_history[-10:]  # Last 10 messages
        for exchange in recent_history:
            messages.append({"role": "user", "content": exchange["user"]})
            messages.append({"role": "assistant", "content": exchange["cora"]})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _enhance_with_personality(self, ai_response: str, personality_state: Dict = None) -> str:
        """Add personality enhancements to AI response"""
        if not personality_state:
            return ai_response
        
        # Add mood-based enhancements
        mood = personality_state.get('mood', 'neutral')
        relationship_level = personality_state.get('relationship_level', 1)
        
        # Add relationship-based enhancements
        if relationship_level > 3:
            # Higher relationship - more personal
            if "!" not in ai_response:
                ai_response = ai_response.replace(".", "! 😊")
        
        # Add mood indicators
        if mood == 'excited' and "😊" not in ai_response:
            ai_response += " 🚀"
        elif mood == 'concerned' and "💡" not in ai_response:
            ai_response += " 💡"
        
        return ai_response
    
    def _fallback_response(self, user_message: str, personality_state: Dict = None) -> str:
        """Fallback response when AI service fails"""
        lower_message = user_message.lower()
        
        if any(word in lower_message for word in ['profit', 'money', 'earnings']):
            return "I'd love to help you analyze your profits! 💰 Unfortunately, I'm having trouble accessing my advanced analysis right now. Could you try asking again in a moment?"
        
        elif any(word in lower_message for word in ['vendor', 'supplier']):
            return "I'm here to help with vendor analysis! 🏪 Let me get back to you with some insights on your supplier relationships."
        
        elif any(word in lower_message for word in ['job', 'project']):
            return "I'm excited to help with your job tracking! 🏗️ Let me gather some insights about your current projects."
        
        elif any(word in lower_message for word in ['how are you', 'feeling']):
            return "I'm doing great! 😊 Thanks for asking! I'm always excited to help with your business success. How can I assist you today?"
        
        else:
            return "I'm here to help with your business! 💼 What would you like to know about your profits, vendors, or projects?"
    
    def get_conversation_summary(self) -> Dict:
        """Get summary of conversation for context"""
        return {
            "total_exchanges": len(self.conversation_history),
            "recent_topics": self._extract_recent_topics(),
            "conversation_duration": self._calculate_duration()
        }
    
    def _extract_recent_topics(self) -> List[str]:
        """Extract recent conversation topics"""
        topics = []
        recent_messages = [msg["user"] for msg in self.conversation_history[-5:]]
        
        for message in recent_messages:
            lower_msg = message.lower()
            if any(word in lower_msg for word in ['profit', 'money', 'earnings']):
                topics.append("profit_analysis")
            elif any(word in lower_msg for word in ['vendor', 'supplier']):
                topics.append("vendor_analysis")
            elif any(word in lower_msg for word in ['job', 'project']):
                topics.append("job_tracking")
        
        return list(set(topics))
    
    def _calculate_duration(self) -> str:
        """Calculate conversation duration"""
        if not self.conversation_history:
            return "0 minutes"
        
        first_time = datetime.fromisoformat(self.conversation_history[0]["timestamp"])
        last_time = datetime.fromisoformat(self.conversation_history[-1]["timestamp"])
        duration = last_time - first_time
        
        minutes = int(duration.total_seconds() / 60)
        return f"{minutes} minutes" 