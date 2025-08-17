"""
Enhanced Intelligence Orchestrator with Emotional Awareness

This integrates the Emotional Intelligence system with the existing Intelligence
Orchestrator to create a truly empathetic AI that understands not just WHAT
contractors need, but HOW they're feeling.

Created by: Opus
Date: 2025-08-03
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from models import User
from services.intelligence_orchestrator import IntelligenceOrchestrator
from services.emotional_intelligence import (
    EmotionalIntelligenceEngine,
    EmotionalState,
    EmotionalProfile
)


class EnhancedIntelligenceOrchestrator(IntelligenceOrchestrator):
    """
    Enhanced orchestrator that considers emotional well-being alongside business intelligence
    """
    
    def __init__(self, user: User, db: Session):
        super().__init__(user, db)
        self.emotional_engine = EmotionalIntelligenceEngine(user, db)
        
    async def orchestrate_intelligence(self) -> Dict[str, Any]:
        """
        Enhanced orchestration that includes emotional awareness
        """
        
        # Get base orchestrated intelligence
        base_intelligence = await super().orchestrate_intelligence()
        
        # Get emotional profile
        emotional_profile = await self.emotional_engine.analyze_emotional_state()
        
        # Enhance the response with emotional awareness
        enhanced_intelligence = self.enhance_with_emotional_context(
            base_intelligence,
            emotional_profile
        )
        
        # Adjust presentation based on emotional state
        enhanced_intelligence = self.adjust_for_emotional_state(
            enhanced_intelligence,
            emotional_profile
        )
        
        # Add wellness support if needed
        if self.should_offer_wellness_support(emotional_profile):
            enhanced_intelligence['wellness_support'] = self.create_wellness_support(
                emotional_profile
            )
        
        # Add empathetic messaging
        enhanced_intelligence['empathetic_context'] = self.create_empathetic_context(
            emotional_profile,
            base_intelligence
        )
        
        return enhanced_intelligence
    
    def enhance_with_emotional_context(
        self,
        base_intelligence: Dict[str, Any],
        emotional_profile: EmotionalProfile
    ) -> Dict[str, Any]:
        """Add emotional context to the orchestrated response"""
        
        enhanced = base_intelligence.copy()
        
        # Add emotional awareness to the response
        enhanced['emotional_awareness'] = {
            'detected_state': emotional_profile.current_state.value,
            'confidence': emotional_profile.confidence,
            'stress_level': emotional_profile.stress_level,
            'resilience_score': emotional_profile.resilience_score,
            'well_being_status': self.get_well_being_status(emotional_profile)
        }
        
        # Enhance relational context with emotional understanding
        if 'relational_context' in enhanced:
            enhanced['relational_context']['emotional_connection'] = {
                'empathy_level': self.calculate_empathy_level(emotional_profile),
                'support_readiness': emotional_profile.stress_level > 5,
                'emotional_signals': [
                    {
                        'type': signal.indicator.value,
                        'intensity': signal.intensity,
                        'positive': signal.is_positive
                    }
                    for signal in emotional_profile.recent_signals[:3]
                ]
            }
        
        return enhanced
    
    def adjust_for_emotional_state(
        self,
        intelligence: Dict[str, Any],
        emotional_profile: EmotionalProfile
    ) -> Dict[str, Any]:
        """Adjust the intelligence presentation based on emotional state"""
        
        # If overwhelmed, simplify the response
        if emotional_profile.current_state == EmotionalState.OVERWHELMED:
            # Reduce cognitive load
            if 'components' in intelligence:
                # Show only the most critical insight
                if 'insight_moments' in intelligence['components']:
                    insights = intelligence['components']['insight_moments'].get('insights', [])
                    if insights:
                        intelligence['components']['insight_moments']['insights'] = [insights[0]]
                    intelligence['components']['insight_moments']['display_style'] = 'gentle_display'
                    intelligence['components']['insight_moments']['timing_delay'] = 8000  # Slower
                
                # Soften the intelligence widget
                if 'intelligence_widget' in intelligence['components']:
                    intelligence['components']['intelligence_widget']['visual_state'] = 'calm_state'
                
                # Simplify predictive dashboard
                if 'predictive_dashboard' in intelligence['components']:
                    intelligence['components']['predictive_dashboard']['highlight_mode'] = 'minimal'
        
        # If thriving, celebrate and energize
        elif emotional_profile.current_state == EmotionalState.THRIVING:
            if 'components' in intelligence:
                if 'insight_moments' in intelligence['components']:
                    intelligence['components']['insight_moments']['display_style'] = 'celebratory_display'
                if 'intelligence_widget' in intelligence['components']:
                    intelligence['components']['intelligence_widget']['visual_state'] = 'celebrate_state'
        
        # If stressed, offer proactive support
        elif emotional_profile.current_state == EmotionalState.STRESSED:
            if 'components' in intelligence:
                # Add stress-relief quick actions
                intelligence['components']['quick_actions'] = [
                    {
                        'type': 'breathing',
                        'label': 'Quick Breathing',
                        'icon': '🧘',
                        'priority': 'high'
                    },
                    {
                        'type': 'break',
                        'label': '5-Min Break',
                        'icon': '☕',
                        'priority': 'medium'
                    }
                ]
        
        # Adjust communication tone
        intelligence['communication_style'] = {
            'tone': self.get_appropriate_tone(emotional_profile),
            'urgency': self.get_appropriate_urgency(emotional_profile),
            'support_level': self.get_support_level(emotional_profile)
        }
        
        return intelligence
    
    def should_offer_wellness_support(self, profile: EmotionalProfile) -> bool:
        """Determine if wellness support should be offered"""
        
        # Offer support if:
        # - Stress level is high
        # - State indicates distress
        # - Multiple negative signals detected
        # - It's been a while since last support
        
        if profile.stress_level > 6:
            return True
        
        if profile.current_state in [
            EmotionalState.OVERWHELMED,
            EmotionalState.STRESSED,
            EmotionalState.BURNT_OUT
        ]:
            return True
        
        negative_signals = sum(
            1 for signal in profile.recent_signals 
            if not signal.is_positive
        )
        if negative_signals >= 3:
            return True
        
        return False
    
    def create_wellness_support(self, profile: EmotionalProfile) -> Dict[str, Any]:
        """Create wellness support component"""
        
        # Get top recommendation
        top_recommendation = profile.support_recommendations[0] if profile.support_recommendations else None
        
        # Create empathetic message
        empathetic_messages = self.emotional_engine.create_empathetic_responses(profile)
        
        return {
            'available': True,
            'priority': self.get_wellness_priority(profile),
            'type': 'proactive' if profile.stress_level > 7 else 'available',
            'message': empathetic_messages[0] if empathetic_messages else 
                      "I'm here if you need support.",
            'recommendation': top_recommendation,
            'quick_actions': [
                {
                    'id': 'wellness_check',
                    'label': 'How are you?',
                    'icon': '💙',
                    'action': 'open_wellness_check'
                },
                {
                    'id': 'quick_break',
                    'label': 'Take a break',
                    'icon': '☕',
                    'action': 'start_break_timer'
                },
                {
                    'id': 'breathing',
                    'label': 'Breathe',
                    'icon': '🧘',
                    'action': 'breathing_exercise'
                }
            ],
            'contextual_tips': self.get_contextual_wellness_tips(profile)
        }
    
    def create_empathetic_context(
        self,
        emotional_profile: EmotionalProfile,
        base_intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create empathetic context for the response"""
        
        # Determine the emotional narrative
        narrative = self.create_emotional_narrative(emotional_profile)
        
        # Create supportive messaging
        supportive_message = self.create_supportive_message(
            emotional_profile,
            base_intelligence
        )
        
        # Identify care opportunities
        care_opportunities = self.identify_care_opportunities(
            emotional_profile,
            base_intelligence
        )
        
        return {
            'narrative': narrative,
            'supportive_message': supportive_message,
            'care_opportunities': care_opportunities,
            'emotional_tone': self.get_appropriate_tone(emotional_profile),
            'connection_strength': self.calculate_emotional_connection(emotional_profile)
        }
    
    def create_emotional_narrative(self, profile: EmotionalProfile) -> str:
        """Create a narrative about the user's emotional journey"""
        
        narratives = {
            EmotionalState.OVERWHELMED: 
                "You're carrying a heavy load right now. It's okay to feel overwhelmed - "
                "it shows how much you care about your business. Let's tackle one thing at a time.",
            
            EmotionalState.STRESSED:
                "I can see the pressure is building. Stress is your body's way of saying "
                "it's time to recalibrate. You've handled challenges before, and you'll handle this too.",
            
            EmotionalState.THRIVING:
                "You're in an amazing flow! Your positive energy is creating momentum that will "
                "carry you far. This is what success feels like - savor it!",
            
            EmotionalState.BALANCED:
                "You're maintaining a healthy rhythm. This balance you've found is the foundation "
                "of sustainable success. Keep nurturing it.",
            
            EmotionalState.RECOVERING:
                "I see you're bouncing back - that takes real strength. Recovery isn't just about "
                "getting back to baseline; it's about growing stronger from the experience.",
            
            EmotionalState.ENERGIZED:
                "Your energy is contagious! This is the perfect time to tackle those big goals. "
                "Ride this wave while staying mindful of sustainable pace.",
            
            EmotionalState.FRUSTRATED:
                "Frustration often comes right before breakthrough. What feels stuck now is actually "
                "energy building for forward movement. Let's channel it productively."
        }
        
        return narratives.get(
            profile.current_state,
            "You're navigating your unique path. I'm here to support you every step of the way."
        )
    
    def create_supportive_message(
        self,
        profile: EmotionalProfile,
        intelligence: Dict[str, Any]
    ) -> str:
        """Create a supportive message based on context"""
        
        # Check if there are urgent business matters
        urgent_signals = 0
        if 'primary_signals' in intelligence:
            urgent_signals = sum(
                1 for signal in intelligence['primary_signals']
                if signal.get('requires_immediate_attention', False)
            )
        
        # Balance business urgency with emotional support
        if urgent_signals > 0 and profile.stress_level > 7:
            return (
                "I see there are urgent matters needing attention, and I also notice you're "
                "under significant stress. Let's address the most critical item first, "
                "then make sure you get some rest."
            )
        elif urgent_signals > 0:
            return (
                "There are some important items for your attention. You're handling things well - "
                "let's work through these together."
            )
        elif profile.stress_level > 7:
            return (
                "Your well-being is just as important as your business. Take a moment to breathe. "
                "The work will still be here, and you'll handle it better when refreshed."
            )
        else:
            return (
                "Everything's under control. You're doing great work maintaining this steady pace. "
                "Keep taking care of yourself along the way."
            )
    
    def identify_care_opportunities(
        self,
        profile: EmotionalProfile,
        intelligence: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify opportunities to show care and support"""
        
        opportunities = []
        
        # Check for late work patterns
        for signal in profile.recent_signals:
            if signal.indicator.value == 'late_night_work' and not signal.is_positive:
                opportunities.append({
                    'type': 'boundary_setting',
                    'message': 'Consider setting a work cutoff time',
                    'action': 'schedule_reminder',
                    'caring_note': 'Your rest directly impacts tomorrow\'s success'
                })
            
            elif signal.indicator.value == 'positive_momentum' and signal.is_positive:
                opportunities.append({
                    'type': 'celebration',
                    'message': 'Your consistency is paying off!',
                    'action': 'view_achievements',
                    'caring_note': 'Take a moment to appreciate how far you\'ve come'
                })
        
        # Check for financial stress
        if profile.stress_level > 6 and any(
            s.indicator.value == 'cash_flow_stress' 
            for s in profile.recent_signals
        ):
            opportunities.append({
                'type': 'practical_support',
                'message': 'Let\'s tackle cash flow together',
                'action': 'cash_flow_analysis',
                'caring_note': 'Financial stress is temporary - we\'ll find solutions'
            })
        
        return opportunities[:2]  # Limit to avoid overwhelming
    
    def get_well_being_status(self, profile: EmotionalProfile) -> str:
        """Get overall well-being status"""
        
        if profile.stress_level <= 3 and profile.resilience_score >= 70:
            return 'excellent'
        elif profile.stress_level <= 5 and profile.resilience_score >= 50:
            return 'good'
        elif profile.stress_level <= 7:
            return 'moderate'
        else:
            return 'needs_attention'
    
    def calculate_empathy_level(self, profile: EmotionalProfile) -> float:
        """Calculate appropriate empathy level (0-1)"""
        
        # Higher empathy for higher stress
        base_empathy = min(profile.stress_level / 10, 1.0)
        
        # Adjust based on state
        state_multipliers = {
            EmotionalState.OVERWHELMED: 1.2,
            EmotionalState.STRESSED: 1.1,
            EmotionalState.BURNT_OUT: 1.3,
            EmotionalState.FRUSTRATED: 1.1,
            EmotionalState.THRIVING: 0.8,  # Less needed when thriving
            EmotionalState.BALANCED: 0.9
        }
        
        multiplier = state_multipliers.get(profile.current_state, 1.0)
        
        return min(base_empathy * multiplier, 1.0)
    
    def get_appropriate_tone(self, profile: EmotionalProfile) -> str:
        """Determine appropriate communication tone"""
        
        tone_map = {
            EmotionalState.OVERWHELMED: 'gentle_supportive',
            EmotionalState.STRESSED: 'calm_reassuring',
            EmotionalState.THRIVING: 'enthusiastic_encouraging',
            EmotionalState.BALANCED: 'professional_friendly',
            EmotionalState.RECOVERING: 'patient_encouraging',
            EmotionalState.ENERGIZED: 'energetic_motivating',
            EmotionalState.FRUSTRATED: 'understanding_helpful',
            EmotionalState.BURNT_OUT: 'deeply_caring'
        }
        
        return tone_map.get(profile.current_state, 'professional_friendly')
    
    def get_appropriate_urgency(self, profile: EmotionalProfile) -> str:
        """Determine appropriate urgency level"""
        
        # Reduce urgency when stressed to avoid adding pressure
        if profile.stress_level > 7:
            return 'gentle'
        elif profile.stress_level > 5:
            return 'moderate'
        else:
            return 'normal'
    
    def get_support_level(self, profile: EmotionalProfile) -> str:
        """Determine level of support to offer"""
        
        if profile.stress_level > 8:
            return 'high_support'
        elif profile.stress_level > 6:
            return 'moderate_support'
        elif profile.stress_level > 4:
            return 'light_support'
        else:
            return 'minimal_support'
    
    def get_wellness_priority(self, profile: EmotionalProfile) -> str:
        """Determine wellness support priority"""
        
        if profile.stress_level > 8 or profile.current_state == EmotionalState.OVERWHELMED:
            return 'urgent'
        elif profile.stress_level > 6:
            return 'high'
        elif profile.stress_level > 4:
            return 'medium'
        else:
            return 'low'
    
    def get_contextual_wellness_tips(self, profile: EmotionalProfile) -> List[str]:
        """Get contextual wellness tips based on current state"""
        
        tips = []
        
        # Time-based tips
        hour = datetime.now().hour
        if hour >= 22 or hour < 6:
            tips.append("It's late - consider wrapping up for better tomorrow")
        elif hour == 12:
            tips.append("Lunch break = productivity boost")
        elif hour == 15:
            tips.append("3 PM slump? Perfect time for a quick walk")
        
        # State-based tips
        if profile.current_state == EmotionalState.OVERWHELMED:
            tips.extend([
                "Break big tasks into 15-minute chunks",
                "Delegate one thing today",
                "Perfect is the enemy of done"
            ])
        elif profile.current_state == EmotionalState.THRIVING:
            tips.extend([
                "Document what's working for future you",
                "Share your energy with your team",
                "Set a new inspiring goal"
            ])
        
        return tips[:2]  # Return top 2 most relevant
    
    def calculate_emotional_connection(self, profile: EmotionalProfile) -> float:
        """Calculate strength of emotional connection (0-1)"""
        
        # Factors that strengthen connection:
        # - Consistent positive interactions
        # - Successfully managing stress together
        # - Celebrating achievements
        # - Working through challenges
        
        connection_score = 0.5  # Base score
        
        # Positive signals strengthen connection
        positive_signals = sum(1 for s in profile.recent_signals if s.is_positive)
        connection_score += positive_signals * 0.05
        
        # High resilience shows we're working well together
        connection_score += (profile.resilience_score / 100) * 0.2
        
        # Moderate stress that's well-managed strengthens bond
        if 3 <= profile.stress_level <= 6:
            connection_score += 0.1
        
        return min(connection_score, 1.0)