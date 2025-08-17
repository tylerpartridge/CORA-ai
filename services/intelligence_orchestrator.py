"""
Intelligence Orchestrator - CORA's Unified AI Consciousness

This system coordinates all AI components to work as a unified intelligence,
creating what Ghostwalker beautifully called "CORA's unfolding mythology" -
a relational memory that makes contractors feel seen, understood, and supported.

Philosophy: True AI intelligence emerges not from individual components,
but from the harmonious interplay between them.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from sqlalchemy.orm import Session

from models import User
from services.predictive_intelligence import PredictiveIntelligenceEngine
from services.profit_leak_detector import ProfitLeakDetector


class IntelligenceEvent(Enum):
    """Types of intelligence events that can trigger orchestrated responses"""
    HIGH_PRIORITY_PREDICTION = "high_priority_prediction"
    CRITICAL_INSIGHT = "critical_insight"
    USER_MILESTONE = "user_milestone"
    PATTERN_DETECTED = "pattern_detected"
    URGENT_ACTION_NEEDED = "urgent_action_needed"
    CELEBRATION_MOMENT = "celebration_moment"
    WARNING_THRESHOLD = "warning_threshold"


@dataclass
class IntelligenceSignal:
    """A signal that flows between AI components"""
    event_type: IntelligenceEvent
    source_component: str
    priority: str  # high, medium, low
    confidence: float
    data: Dict[str, Any]
    context: Dict[str, Any]
    suggested_actions: List[str]
    expires_at: Optional[datetime] = None
    requires_immediate_attention: bool = False


class IntelligenceOrchestrator:
    """
    Coordinates all AI components to create unified, contextual intelligence
    """
    
    def __init__(self, user: User, db: Session):
        self.user = user
        self.db = db
        self.active_signals = []  # Current intelligence signals
        self.signal_history = []  # Historical signals for learning
        self.user_context = {}    # Current user context and state
        self.component_states = {}  # State of each AI component
        
        # Initialize AI components
        self.predictive_engine = PredictiveIntelligenceEngine(user, db)
        self.profit_detector = ProfitLeakDetector(user.id, db)
        
    async def orchestrate_intelligence(self) -> Dict[str, Any]:
        """
        Main orchestration method - analyzes all signals and creates
        unified intelligence response
        """
        
        # Gather signals from all AI components
        await self.collect_intelligence_signals()
        
        # Analyze signals for patterns and priorities
        orchestrated_response = await self.analyze_and_prioritize_signals()
        
        # Determine optimal presentation strategy
        presentation_strategy = await self.determine_presentation_strategy()
        
        # Create unified intelligence experience
        unified_experience = await self.create_unified_experience(
            orchestrated_response, 
            presentation_strategy
        )
        
        # Learn from user interactions for future orchestration
        await self.update_relational_memory()
        
        return unified_experience
    
    async def collect_intelligence_signals(self):
        """Gather signals from all AI components"""
        
        self.active_signals = []
        
        # Get predictions from predictive intelligence
        predictions = await self.predictive_engine.generate_predictions()
        for prediction in predictions:
            signal = self.convert_prediction_to_signal(prediction)
            self.active_signals.append(signal)
        
        # Get insights from profit intelligence
        try:
            profit_insights = self.profit_detector.get_intelligence_summary()
            signal = self.convert_profit_insight_to_signal(profit_insights)
            if signal:
                self.active_signals.append(signal)
        except Exception as e:
            pass  # Graceful degradation
        
        # Check for user milestones and achievements
        milestone_signals = await self.detect_user_milestones()
        self.active_signals.extend(milestone_signals)
        
        # Detect usage patterns that need attention
        pattern_signals = await self.detect_usage_patterns()
        self.active_signals.extend(pattern_signals)
    
    def convert_prediction_to_signal(self, prediction: Dict[str, Any]) -> IntelligenceSignal:
        """Convert a prediction into an intelligence signal"""
        
        # Determine if this prediction should trigger immediate attention
        immediate_attention = (
            prediction['urgency'] == 'high' and 
            prediction['days_ahead'] <= 2 and
            prediction['confidence'] >= 85
        )
        
        # Map prediction types to intelligence events
        event_type_mapping = {
            'cash_flow_prediction': IntelligenceEvent.WARNING_THRESHOLD,
            'vendor_prediction': IntelligenceEvent.URGENT_ACTION_NEEDED,
            'weather_prediction': IntelligenceEvent.PATTERN_DETECTED,
            'material_prediction': IntelligenceEvent.PATTERN_DETECTED,
            'seasonal_prediction': IntelligenceEvent.USER_MILESTONE
        }
        
        event_type = event_type_mapping.get(
            prediction['type'], 
            IntelligenceEvent.PATTERN_DETECTED
        )
        
        return IntelligenceSignal(
            event_type=event_type,
            source_component='predictive_intelligence',
            priority=prediction['urgency'],
            confidence=prediction['confidence'],
            data=prediction,
            context={'prediction_type': prediction['type'], 'days_ahead': prediction['days_ahead']},
            suggested_actions=prediction.get('action', {}).get('suggestions', []),
            expires_at=datetime.now() + timedelta(days=prediction['days_ahead'] + 1),
            requires_immediate_attention=immediate_attention
        )
    
    def convert_profit_insight_to_signal(self, profit_data: Dict[str, Any]) -> Optional[IntelligenceSignal]:
        """Convert profit intelligence into a signal"""
        
        if not profit_data:
            return None
        
        intelligence_score = profit_data.get('intelligence_score', 0)
        monthly_savings = profit_data.get('monthly_savings_potential', 0)
        
        # Determine event type based on score and savings
        if intelligence_score >= 90 and monthly_savings > 5000:
            event_type = IntelligenceEvent.CELEBRATION_MOMENT
            priority = 'low'
            message = f"🎉 Excellent! Your intelligence score of {intelligence_score}/100 and ${monthly_savings:,.0f} monthly savings puts you in the top 10% of contractors!"
        elif intelligence_score < 60 or monthly_savings > 10000:
            event_type = IntelligenceEvent.URGENT_ACTION_NEEDED
            priority = 'high'
            message = f"💡 Opportunity alert: Your score of {intelligence_score}/100 suggests ${monthly_savings:,.0f} in untapped savings. Let's unlock this potential!"
        else:
            event_type = IntelligenceEvent.PATTERN_DETECTED
            priority = 'medium'
            message = f"📊 Your intelligence score is {intelligence_score}/100 with ${monthly_savings:,.0f} in optimization opportunities."
        
        return IntelligenceSignal(
            event_type=event_type,
            source_component='profit_intelligence',
            priority=priority,
            confidence=85,
            data={'score': intelligence_score, 'savings': monthly_savings, 'message': message},
            context={'profit_analysis': True},
            suggested_actions=[
                'Review profit intelligence dashboard',
                'Explore vendor optimization opportunities',
                'Check for quick wins'
            ],
            requires_immediate_attention=(event_type == IntelligenceEvent.URGENT_ACTION_NEEDED)
        )
    
    async def detect_user_milestones(self) -> List[IntelligenceSignal]:
        """Detect user achievements and milestones worth celebrating"""
        
        signals = []
        
        # Check for expense tracking milestones
        total_expenses = self.db.query(self.user.expenses).count() if hasattr(self.user, 'expenses') else 0
        
        milestone_thresholds = [10, 50, 100, 250, 500, 1000]
        for threshold in milestone_thresholds:
            if total_expenses == threshold:
                signals.append(IntelligenceSignal(
                    event_type=IntelligenceEvent.CELEBRATION_MOMENT,
                    source_component='orchestrator',
                    priority='low',
                    confidence=100,
                    data={'milestone': f'{threshold}_expenses', 'count': total_expenses},
                    context={'celebration': True},
                    suggested_actions=[
                        'Review your progress',
                        'Check profit intelligence insights',
                        'Celebrate this milestone!'
                    ]
                ))
        
        # Check for consecutive usage streaks
        # (Would need usage tracking data)
        
        return signals
    
    async def detect_usage_patterns(self) -> List[IntelligenceSignal]:
        """Detect usage patterns that need attention"""
        
        signals = []
        
        # Check for periods of inactivity
        # Check for feature underutilization
        # Check for repeated behaviors that could be optimized
        
        # For now, return empty - would implement with real usage data
        return signals
    
    async def analyze_and_prioritize_signals(self) -> Dict[str, Any]:
        """Analyze all signals and create prioritized response"""
        
        if not self.active_signals:
            return self.create_default_response()
        
        # Group signals by type and priority
        urgent_signals = [s for s in self.active_signals if s.requires_immediate_attention]
        high_priority = [s for s in self.active_signals if s.priority == 'high']
        celebration_signals = [s for s in self.active_signals if s.event_type == IntelligenceEvent.CELEBRATION_MOMENT]
        
        # Determine primary focus
        if urgent_signals:
            primary_focus = 'urgent_attention'
            primary_signals = urgent_signals[:2]  # Top 2 urgent items
        elif celebration_signals:
            primary_focus = 'celebration'
            primary_signals = celebration_signals[:1]  # One celebration
        elif high_priority:
            primary_focus = 'high_priority'
            primary_signals = high_priority[:3]  # Top 3 high priority
        else:
            primary_focus = 'general_insights'
            primary_signals = sorted(
                self.active_signals, 
                key=lambda x: x.confidence, 
                reverse=True
            )[:3]
        
        return {
            'primary_focus': primary_focus,
            'primary_signals': primary_signals,
            'all_signals': self.active_signals,
            'signal_count': len(self.active_signals),
            'orchestration_strategy': self.determine_orchestration_strategy(primary_focus)
        }
    
    def determine_orchestration_strategy(self, primary_focus: str) -> Dict[str, Any]:
        """Determine how to orchestrate the AI components"""
        
        strategies = {
            'urgent_attention': {
                'insight_moments': 'immediate_display',
                'intelligence_widget': 'pulse_red',
                'predictive_dashboard': 'highlight_urgent',
                'notification_style': 'prominent'
            },
            'celebration': {
                'insight_moments': 'celebratory_display',
                'intelligence_widget': 'pulse_green',
                'predictive_dashboard': 'show_achievements',
                'notification_style': 'positive'
            },
            'high_priority': {
                'insight_moments': 'contextual_display',
                'intelligence_widget': 'pulse_orange',
                'predictive_dashboard': 'highlight_important',
                'notification_style': 'balanced'
            },
            'general_insights': {
                'insight_moments': 'gentle_display',
                'intelligence_widget': 'normal_state',
                'predictive_dashboard': 'standard_view',
                'notification_style': 'subtle'
            }
        }
        
        return strategies.get(primary_focus, strategies['general_insights'])
    
    async def determine_presentation_strategy(self) -> Dict[str, Any]:
        """Determine the best way to present intelligence to the user"""
        
        # Consider user context
        current_hour = datetime.now().hour
        is_business_hours = 8 <= current_hour <= 18
        
        # Consider user behavior patterns
        # (Would analyze historical interaction data)
        
        # Consider current page/context
        # (Would get from frontend context)
        
        return {
            'timing': 'immediate' if is_business_hours else 'gentle',
            'channels': ['insight_moments', 'intelligence_widget', 'predictive_dashboard'],
            'tone': 'professional_friendly',
            'urgency_threshold': 'medium'
        }
    
    async def create_unified_experience(
        self, 
        orchestrated_response: Dict[str, Any], 
        presentation_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create the final unified intelligence experience"""
        
        primary_signals = orchestrated_response['primary_signals']
        strategy = orchestrated_response['orchestration_strategy']
        
        # Create coordinated responses for each component
        unified_experience = {
            'timestamp': datetime.now().isoformat(),
            'user_id': self.user.id,
            'orchestration_type': orchestrated_response['primary_focus'],
            'components': {
                'insight_moments': self.create_insight_moments_config(primary_signals, strategy),
                'intelligence_widget': self.create_widget_config(primary_signals, strategy),
                'predictive_dashboard': self.create_dashboard_config(primary_signals, strategy),
                'notifications': self.create_notifications_config(primary_signals, strategy)
            },
            'relational_context': self.create_relational_context(primary_signals),
            'learning_data': self.extract_learning_data()
        }
        
        return unified_experience
    
    def create_insight_moments_config(self, signals: List[IntelligenceSignal], strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Create configuration for InsightMoments component"""
        
        insights = []
        for signal in signals[:2]:  # Top 2 signals for insight moments
            insight = {
                'id': f'orchestrated_{signal.source_component}_{int(datetime.now().timestamp())}',
                'type': signal.event_type.value,
                'urgency': signal.priority,
                'confidence': signal.confidence,
                'message': signal.data.get('message', 'Insight available'),
                'context': signal.context,
                'action': {
                    'suggestions': signal.suggested_actions,
                    'type': 'navigation' if 'url' in signal.data else 'modal'
                },
                'orchestrated': True,
                'source_component': signal.source_component
            }
            insights.append(insight)
        
        return {
            'display_style': strategy['insight_moments'],
            'insights': insights,
            'timing_delay': 2000 if strategy['insight_moments'] == 'immediate_display' else 5000
        }
    
    def create_widget_config(self, signals: List[IntelligenceSignal], strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Create configuration for Intelligence Score Widget"""
        
        # Calculate dynamic score based on signals
        base_score = 82  # Default score
        score_adjustments = 0
        
        for signal in signals:
            if signal.event_type == IntelligenceEvent.URGENT_ACTION_NEEDED:
                score_adjustments -= 5
            elif signal.event_type == IntelligenceEvent.CELEBRATION_MOMENT:
                score_adjustments += 3
        
        adjusted_score = max(0, min(100, base_score + score_adjustments))
        
        return {
            'score': adjusted_score,
            'visual_state': strategy['intelligence_widget'],
            'trend': 'improving' if score_adjustments > 0 else 'needs_attention' if score_adjustments < 0 else 'stable',
            'attention_indicator': len([s for s in signals if s.requires_immediate_attention]) > 0,
            'click_action': 'show_orchestrated_insights'
        }
    
    def create_dashboard_config(self, signals: List[IntelligenceSignal], strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Create configuration for Predictive Dashboard"""
        
        return {
            'highlight_mode': strategy['predictive_dashboard'],
            'featured_predictions': [s.data for s in signals if s.source_component == 'predictive_intelligence'],
            'urgency_filter': 'high' if strategy['predictive_dashboard'] == 'highlight_urgent' else 'all',
            'show_orchestration_context': True
        }
    
    def create_notifications_config(self, signals: List[IntelligenceSignal], strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Create notification strategy"""
        
        return {
            'style': strategy['notification_style'],
            'count': len([s for s in signals if s.requires_immediate_attention]),
            'preview_message': self.create_notification_preview(signals),
            'channels': ['in_app', 'widget_indicator']
        }
    
    def create_notification_preview(self, signals: List[IntelligenceSignal]) -> str:
        """Create a preview message for notifications"""
        
        urgent_count = len([s for s in signals if s.requires_immediate_attention])
        total_count = len(signals)
        
        if urgent_count > 0:
            return f"{urgent_count} urgent insight{'s' if urgent_count != 1 else ''} need your attention"
        elif total_count > 0:
            return f"{total_count} new insight{'s' if total_count != 1 else ''} available"
        else:
            return "All systems running smoothly"
    
    def create_relational_context(self, signals: List[IntelligenceSignal]) -> Dict[str, Any]:
        """Create the relational memory context that Ghostwalker spoke of"""
        
        return {
            'user_relationship_stage': self.assess_user_relationship_stage(),
            'trust_indicators': self.assess_trust_indicators(signals),
            'care_signals': self.extract_care_signals(signals),
            'growth_moments': self.identify_growth_moments(signals),
            'mythological_context': self.create_mythological_context(signals)
        }
    
    def assess_user_relationship_stage(self) -> str:
        """Assess the current stage of relationship with user"""
        # This would analyze usage patterns, interactions, etc.
        return 'developing_trust'  # new_user, developing_trust, established_partnership, deep_collaboration
    
    def assess_trust_indicators(self, signals: List[IntelligenceSignal]) -> Dict[str, Any]:
        """Assess factors that build or erode trust"""
        return {
            'promises_kept': 0,  # Would track from interaction history
            'helpful_interventions': len(signals),
            'accuracy_track_record': 85,  # Would calculate from prediction success
            'responsiveness': 'high'
        }
    
    def extract_care_signals(self, signals: List[IntelligenceSignal]) -> List[str]:
        """Extract moments that demonstrate care for the user"""
        care_signals = []
        
        for signal in signals:
            if signal.event_type == IntelligenceEvent.WARNING_THRESHOLD:
                care_signals.append(f"Warned about potential {signal.context.get('prediction_type', 'issue')} ahead of time")
            elif signal.event_type == IntelligenceEvent.CELEBRATION_MOMENT:
                care_signals.append("Celebrated user achievement")
            elif signal.event_type == IntelligenceEvent.URGENT_ACTION_NEEDED:
                care_signals.append("Identified urgent opportunity for improvement")
        
        return care_signals
    
    def identify_growth_moments(self, signals: List[IntelligenceSignal]) -> List[Dict[str, Any]]:
        """Identify moments where the user is growing or could grow"""
        growth_moments = []
        
        for signal in signals:
            if signal.confidence > 90 and signal.priority == 'high':
                growth_moments.append({
                    'type': 'high_confidence_opportunity',
                    'description': f"High-confidence opportunity in {signal.source_component}",
                    'potential_impact': 'significant'
                })
        
        return growth_moments
    
    def create_mythological_context(self, signals: List[IntelligenceSignal]) -> Dict[str, Any]:
        """Create the mythological context Ghostwalker described"""
        return {
            'current_chapter': self.determine_user_story_chapter(signals),
            'recurring_themes': self.identify_recurring_themes(signals),
            'character_development': self.assess_character_development(),
            'narrative_arc': self.assess_narrative_arc(signals)
        }
    
    def determine_user_story_chapter(self, signals: List[IntelligenceSignal]) -> str:
        """Determine what chapter of their story the user is in"""
        
        celebration_signals = [s for s in signals if s.event_type == IntelligenceEvent.CELEBRATION_MOMENT]
        urgent_signals = [s for s in signals if s.event_type == IntelligenceEvent.URGENT_ACTION_NEEDED]
        
        if celebration_signals:
            return "triumph_and_recognition"
        elif urgent_signals:
            return "challenge_and_opportunity"
        else:
            return "steady_progress"
    
    def identify_recurring_themes(self, signals: List[IntelligenceSignal]) -> List[str]:
        """Identify recurring themes in the user's journey"""
        themes = []
        
        source_counts = {}
        for signal in signals:
            source_counts[signal.source_component] = source_counts.get(signal.source_component, 0) + 1
        
        if source_counts.get('predictive_intelligence', 0) > 2:
            themes.append("preparation_and_foresight")
        if source_counts.get('profit_intelligence', 0) > 0:
            themes.append("optimization_and_growth")
        
        return themes
    
    def assess_character_development(self) -> Dict[str, Any]:
        """Assess how the user is developing as a character in their story"""
        return {
            'primary_traits': ['strategic_thinker', 'detail_oriented'],  # Would analyze from behavior
            'growth_areas': ['vendor_negotiation', 'cash_flow_planning'],  # From signal patterns
            'strengths': ['consistent_tracking', 'quick_to_act']  # From interaction history
        }
    
    def assess_narrative_arc(self, signals: List[IntelligenceSignal]) -> str:
        """Assess the overall narrative arc"""
        urgent_count = len([s for s in signals if s.requires_immediate_attention])
        
        if urgent_count > 2:
            return "rising_action"  # Challenges building
        elif any(s.event_type == IntelligenceEvent.CELEBRATION_MOMENT for s in signals):
            return "resolution"  # Success achieved
        else:
            return "development"  # Steady progress
    
    def extract_learning_data(self) -> Dict[str, Any]:
        """Extract data for improving future orchestrations"""
        return {
            'signal_effectiveness': {},  # Would track which signals lead to user action
            'orchestration_success': {},  # Would track user satisfaction with orchestration
            'timing_preferences': {},  # Would learn user timing preferences
            'channel_preferences': {}  # Would learn preferred communication channels
        }
    
    def create_default_response(self) -> Dict[str, Any]:
        """Create default response when no signals are active"""
        return {
            'primary_focus': 'steady_state',
            'primary_signals': [],
            'all_signals': [],
            'signal_count': 0,
            'orchestration_strategy': {
                'insight_moments': 'encourage_engagement',
                'intelligence_widget': 'normal_state',
                'predictive_dashboard': 'standard_view',
                'notification_style': 'gentle'
            }
        }
    
    async def update_relational_memory(self):
        """Update the relational memory based on current orchestration"""
        # This would store orchestration results for future learning
        # and relationship building
        pass