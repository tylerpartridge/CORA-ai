"""
Conversational Data Mapping for Natural CORA Onboarding
Maps conversational responses to user profile and business data
"""

class ConversationalDataMapper:
    """
    Transforms natural conversation into structured data
    while maintaining the flow of a friendly chat
    """
    
    def __init__(self):
        self.conversation_map = {
            # Natural question -> Database field mapping
            "name": {
                "variations": ["what's your name", "who am I talking to", "what should I call you"],
                "db_field": "user.full_name",
                "next_prompt": "Nice to meet you, {name}!"
            },
            "trade_type": {
                "variations": ["what kind of work do you do", "what's your trade", "what type of construction"],
                "db_field": "user.business_type",
                "profile_fields": ["primary_trade", "service_types"],
                "next_prompt": "{trade} - great! Those can be really profitable when priced right."
            },
            "experience": {
                "variations": ["how long have you been doing this", "years in business", "when did you start"],
                "db_field": "user.years_in_business",
                "next_prompt": "{years}! You've seen it all then."
            },
            "revenue_range": {
                "variations": ["how much revenue", "annual sales", "yearly income"],
                "db_field": "user.revenue_range",
                "next_prompt": "Perfect, that's a sweet spot for finding profit improvements."
            },
            "job_data": {
                "quote": {
                    "variations": ["what did you quote", "original estimate", "bid amount"],
                    "db_field": "job.quoted_amount",
                    "context": "recent_job"
                },
                "materials": {
                    "variations": ["material costs", "supplies", "home depot"],
                    "db_field": "job.material_cost",
                    "calculate": "markup_opportunity"
                },
                "labor": {
                    "variations": ["labor hours", "time spent", "hours worked"],
                    "db_field": "job.labor_hours",
                    "calculate": "hourly_rate_gap"
                }
            }
        }
    
    def extract_intent(self, cora_message: str) -> str:
        """
        Identifies what data CORA is asking for based on her message
        """
        message_lower = cora_message.lower()
        
        for intent, config in self.conversation_map.items():
            if isinstance(config, dict) and "variations" in config:
                for variation in config["variations"]:
                    if variation in message_lower:
                        return intent
        
        return "unknown"
    
    def map_response(self, intent: str, user_response: str) -> dict:
        """
        Maps user's natural response to structured data
        """
        if intent == "name":
            return {
                "field": "full_name",
                "value": user_response.strip(),
                "table": "user"
            }
        
        elif intent == "trade_type":
            # Parse trade type and create profile
            trade = self._parse_trade_type(user_response)
            return {
                "field": "business_type",
                "value": trade["primary"],
                "table": "user",
                "profile_data": {
                    "primary_trade": trade["primary"],
                    "service_types": trade["services"],
                    "specialty_focus": trade["specialty"]
                }
            }
        
        elif intent == "revenue_range":
            # Convert natural language to range
            revenue = self._parse_revenue(user_response)
            return {
                "field": "revenue_range",
                "value": revenue,
                "table": "user"
            }
        
        elif intent.startswith("job_"):
            # Handle job-related data
            return self._map_job_data(intent, user_response)
        
        return {"field": None, "value": None}
    
    def _parse_trade_type(self, response: str) -> dict:
        """
        Extracts trade information from natural response
        'I mostly do bathroom remodels' -> {primary: 'bathroom_remodel', services: ['bathroom']}
        """
        response_lower = response.lower()
        
        trade_keywords = {
            "bathroom": ["bathroom", "bath", "shower", "toilet"],
            "kitchen": ["kitchen", "cabinet", "countertop"],
            "general": ["general", "contractor", "gc", "various"],
            "plumbing": ["plumber", "plumbing", "pipes"],
            "electrical": ["electrician", "electrical", "wiring"],
            "roofing": ["roof", "roofing", "shingle"],
            "flooring": ["floor", "flooring", "tile", "hardwood"]
        }
        
        identified_trades = []
        for trade, keywords in trade_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                identified_trades.append(trade)
        
        primary = identified_trades[0] if identified_trades else "general"
        
        return {
            "primary": primary,
            "services": identified_trades,
            "specialty": "remodel" if "remodel" in response_lower else "new"
        }
    
    def _parse_revenue(self, response: str) -> str:
        """
        Converts natural revenue response to range
        'about 600k' -> '500K-1M'
        """
        import re
        
        # Extract numbers
        numbers = re.findall(r'[\d,]+', response.replace('k', '000').replace('K', '000'))
        if not numbers:
            return "unknown"
        
        # Convert to integer
        amount = int(numbers[0].replace(',', ''))
        
        # Map to ranges
        if amount < 250000:
            return "under_250k"
        elif amount < 500000:
            return "250k_500k"
        elif amount < 1000000:
            return "500k_1m"
        elif amount < 5000000:
            return "1m_5m"
        else:
            return "over_5m"
    
    def _map_job_data(self, intent: str, response: str) -> dict:
        """
        Maps job-related responses to job records
        """
        import re
        
        # Extract numeric value
        numbers = re.findall(r'[\d,]+\.?\d*', response)
        value = float(numbers[0].replace(',', '')) if numbers else 0
        
        field_map = {
            "job_quote": "quoted_amount",
            "job_materials": "material_cost",
            "job_labor": "labor_hours"
        }
        
        return {
            "field": field_map.get(intent, "unknown"),
            "value": value,
            "table": "job",
            "context": "current_conversation_job"
        }
    
    def save_to_profile(self, user_id: int, conversation_data: dict, db_session):
        """
        Persists conversational data to user profile and related tables
        Maintains relationships and calculates insights
        """
        from models import User, UserProfile, Job
        
        user = db_session.query(User).filter(User.id == user_id).first()
        
        # Update user fields
        for field, value in conversation_data.get("user_fields", {}).items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        # Create or update profile
        profile = db_session.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()
        
        if not profile:
            profile = UserProfile(user_id=user_id)
            db_session.add(profile)
        
        # Update profile with conversational insights
        profile_data = conversation_data.get("profile_data", {})
        profile.primary_trade = profile_data.get("primary_trade")
        profile.service_types = profile_data.get("service_types", [])
        profile.typical_job_size = profile_data.get("typical_job_size")
        profile.common_pain_points = self._identify_pain_points(conversation_data)
        
        # If job data was discussed, create a sample job
        if "job_data" in conversation_data:
            job = Job(
                user_id=user_id,
                name=f"Sample {profile.primary_trade} Job",
                quoted_amount=conversation_data["job_data"].get("quote", 0),
                material_cost=conversation_data["job_data"].get("materials", 0),
                labor_hours=conversation_data["job_data"].get("labor_hours", 0),
                job_type=profile.primary_trade,
                is_sample=True  # Flag for onboarding sample
            )
            db_session.add(job)
        
        db_session.commit()
        
        return {
            "profile_complete": True,
            "insights_available": True,
            "next_action": "show_profit_opportunities"
        }
    
    def _identify_pain_points(self, conversation_data: dict) -> list:
        """
        Identifies common contractor pain points from conversation
        """
        pain_points = []
        
        job_data = conversation_data.get("job_data", {})
        
        # Check for no material markup
        if job_data.get("materials", 0) > 0 and not job_data.get("markup_applied"):
            pain_points.append("no_material_markup")
        
        # Check for unbilled changes
        if conversation_data.get("had_changes") and not conversation_data.get("billed_changes"):
            pain_points.append("unbilled_change_orders")
        
        # Check for low hourly rate
        if job_data.get("hourly_rate", 0) < 65:  # Market rate benchmark
            pain_points.append("below_market_rate")
        
        return pain_points


# Integration with existing chat system
class ConversationalOnboarding:
    """
    Manages the natural onboarding flow while collecting necessary data
    """
    
    def __init__(self, data_mapper: ConversationalDataMapper):
        self.mapper = data_mapper
        self.conversation_state = {}
    
    def process_message(self, user_id: int, message: str, context: dict) -> dict:
        """
        Processes user message and updates profile naturally
        """
        # Identify what CORA last asked
        last_cora_message = context.get("last_cora_message", "")
        intent = self.mapper.extract_intent(last_cora_message)
        
        # Map the response to data
        mapped_data = self.mapper.map_response(intent, message)
        
        # Update conversation state
        if mapped_data["field"]:
            self.conversation_state[mapped_data["field"]] = mapped_data["value"]
        
        # Check if we have enough data to create insights
        if self._has_minimum_data():
            insights = self._generate_insights()
            return {
                "save_profile": True,
                "show_insights": True,
                "insights": insights,
                "next_prompt": self._get_insight_prompt(insights)
            }
        
        return {
            "save_profile": False,
            "continue_conversation": True,
            "next_topic": self._get_next_topic()
        }
    
    def _has_minimum_data(self) -> bool:
        """
        Checks if we have enough data to provide value
        """
        required_fields = ["full_name", "business_type", "quoted_amount", "material_cost"]
        return all(field in self.conversation_state for field in required_fields)
    
    def _generate_insights(self) -> dict:
        """
        Creates immediate value from conversational data
        """
        quote = self.conversation_state.get("quoted_amount", 0)
        materials = self.conversation_state.get("material_cost", 0)
        
        # Calculate opportunities
        material_markup = materials * 0.25
        unbilled = quote * 0.08 if self.conversation_state.get("had_changes") else 0
        
        return {
            "total_opportunity": material_markup + unbilled,
            "material_markup": material_markup,
            "unbilled_changes": unbilled,
            "annual_impact": (material_markup + unbilled) * 10  # Assuming 10 similar jobs
        }
    
    def _get_insight_prompt(self, insights: dict) -> str:
        """
        Creates natural transition to showing value
        """
        total = insights["total_opportunity"]
        annual = insights["annual_impact"]
        
        return f"""Based on what you just told me, you're leaving about ${total:,.0f} 
        on the table for jobs like this. That's ${annual:,.0f} per year! 
        Want me to show you exactly where it's hiding?"""
    
    def _get_next_topic(self) -> str:
        """
        Determines natural next question based on what we know
        """
        if "full_name" not in self.conversation_state:
            return "introduction"
        elif "business_type" not in self.conversation_state:
            return "trade_discovery"
        elif "quoted_amount" not in self.conversation_state:
            return "job_example"
        else:
            return "cost_breakdown"