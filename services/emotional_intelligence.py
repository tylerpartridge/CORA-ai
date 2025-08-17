"""
Emotional Intelligence System - CORA's Empathetic Understanding

This system adds emotional awareness to CORA, allowing it to detect and respond
to contractor stress, burnout, and well-being. Construction is a high-stress 
industry where mental health often goes unaddressed. CORA can be more than a 
profit tracker - it can be a supportive partner.

Philosophy: True intelligence includes emotional awareness. By understanding 
not just WHAT contractors are doing but HOW they're feeling, CORA can provide
support when it's needed most.

Created by: Opus
Date: 2025-08-03
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from sqlalchemy.orm import Session
import numpy as np
from collections import defaultdict

from models import User, Expense


class EmotionalState(Enum):
    """Emotional states CORA can detect"""
    THRIVING = "thriving"
    BALANCED = "balanced"
    STRESSED = "stressed"
    OVERWHELMED = "overwhelmed"
    BURNT_OUT = "burnt_out"
    RECOVERING = "recovering"
    ENERGIZED = "energized"
    FRUSTRATED = "frustrated"


class StressIndicator(Enum):
    """Indicators that suggest stress or well-being issues"""
    LATE_NIGHT_WORK = "late_night_work"
    WEEKEND_WORK = "weekend_work"
    RAPID_EXPENSE_ENTRY = "rapid_expense_entry"
    EXPENSE_DELETION_SPREE = "expense_deletion_spree"
    LONG_WORK_STREAK = "long_work_streak"
    IRREGULAR_PATTERNS = "irregular_patterns"
    CASH_FLOW_STRESS = "cash_flow_stress"
    MISSED_MILESTONES = "missed_milestones"
    POSITIVE_MOMENTUM = "positive_momentum"
    REGULAR_BREAKS = "regular_breaks"


@dataclass
class EmotionalSignal:
    """A signal indicating emotional state or well-being"""
    indicator: StressIndicator
    intensity: float  # 0-1, where 1 is highest intensity
    timestamp: datetime
    context: Dict[str, Any]
    suggested_support: List[str]
    is_positive: bool


@dataclass
class EmotionalProfile:
    """Complete emotional profile of a contractor"""
    current_state: EmotionalState
    confidence: float
    stress_level: float  # 0-10 scale
    resilience_score: float  # 0-100
    recent_signals: List[EmotionalSignal]
    support_recommendations: List[Dict[str, Any]]
    well_being_trends: Dict[str, Any]


class EmotionalIntelligenceEngine:
    """
    Detects and responds to contractor emotional states and well-being
    """
    
    def __init__(self, user: User, db: Session):
        self.user = user
        self.db = db
        self.emotional_history = []
        self.signal_buffer = []
        self.baseline_patterns = {}
        
    async def analyze_emotional_state(self) -> EmotionalProfile:
        """
        Main analysis method - detects current emotional state and well-being
        """
        
        # Collect emotional signals from various sources
        signals = await self.collect_emotional_signals()
        
        # Analyze patterns for stress indicators
        stress_analysis = self.analyze_stress_patterns(signals)
        
        # Determine current emotional state
        current_state = self.determine_emotional_state(signals, stress_analysis)
        
        # Calculate well-being metrics
        well_being_metrics = self.calculate_well_being_metrics(signals)
        
        # Generate support recommendations
        support_recommendations = self.generate_support_recommendations(
            current_state, 
            stress_analysis,
            well_being_metrics
        )
        
        # Build complete emotional profile
        profile = EmotionalProfile(
            current_state=current_state['state'],
            confidence=current_state['confidence'],
            stress_level=stress_analysis['stress_level'],
            resilience_score=well_being_metrics['resilience_score'],
            recent_signals=signals[-10:],  # Last 10 signals
            support_recommendations=support_recommendations,
            well_being_trends=well_being_metrics['trends']
        )
        
        # Store for learning
        self.emotional_history.append({
            'timestamp': datetime.now(),
            'profile': profile
        })
        
        return profile
    
    async def collect_emotional_signals(self) -> List[EmotionalSignal]:
        """Collect signals from user behavior patterns"""
        
        signals = []
        
        # Check work hour patterns
        work_hour_signals = await self.analyze_work_hours()
        signals.extend(work_hour_signals)
        
        # Check expense entry patterns
        expense_signals = await self.analyze_expense_patterns()
        signals.extend(expense_signals)
        
        # Check financial stress indicators
        financial_signals = await self.analyze_financial_stress()
        signals.extend(financial_signals)
        
        # Check achievement and momentum
        momentum_signals = await self.analyze_positive_momentum()
        signals.extend(momentum_signals)
        
        # Check interaction patterns
        interaction_signals = await self.analyze_interaction_patterns()
        signals.extend(interaction_signals)
        
        return sorted(signals, key=lambda x: x.timestamp, reverse=True)
    
    async def analyze_work_hours(self) -> List[EmotionalSignal]:
        """Analyze when contractor is working - late nights, weekends, etc."""
        
        signals = []
        
        # Get recent expense entries to understand work patterns
        recent_expenses = self.db.query(Expense).filter(
            Expense.user_id == self.user.id,
            Expense.created_at >= datetime.now() - timedelta(days=7)
        ).all()
        
        if not recent_expenses:
            return signals
        
        # Group by hour and day
        hour_counts = defaultdict(int)
        weekend_work = 0
        late_night_work = 0
        
        for expense in recent_expenses:
            hour = expense.created_at.hour
            hour_counts[hour] += 1
            
            # Check for late night work (10 PM - 4 AM)
            if hour >= 22 or hour < 4:
                late_night_work += 1
            
            # Check for weekend work
            if expense.created_at.weekday() >= 5:  # Saturday = 5, Sunday = 6
                weekend_work += 1
        
        # Generate signals based on patterns
        if late_night_work > 5:
            signals.append(EmotionalSignal(
                indicator=StressIndicator.LATE_NIGHT_WORK,
                intensity=min(late_night_work / 10, 1.0),
                timestamp=datetime.now(),
                context={
                    'count': late_night_work,
                    'message': f"You've been working late {late_night_work} times this week"
                },
                suggested_support=[
                    "Consider setting work boundaries",
                    "Late night work affects next-day productivity",
                    "Your health is your wealth"
                ],
                is_positive=False
            ))
        
        if weekend_work > 3:
            signals.append(EmotionalSignal(
                indicator=StressIndicator.WEEKEND_WORK,
                intensity=min(weekend_work / 7, 1.0),
                timestamp=datetime.now(),
                context={
                    'count': weekend_work,
                    'message': "You've been working most weekends"
                },
                suggested_support=[
                    "Everyone needs rest, even contractors",
                    "Schedule some downtime this weekend",
                    "Burnout costs more than a day off"
                ],
                is_positive=False
            ))
        
        return signals
    
    async def analyze_expense_patterns(self) -> List[EmotionalSignal]:
        """Analyze how expenses are being entered - rushed, deleted, etc."""
        
        signals = []
        
        # Check for rapid entry (stress dumping)
        recent_expenses = self.db.query(Expense).filter(
            Expense.user_id == self.user.id,
            Expense.created_at >= datetime.now() - timedelta(hours=2)
        ).order_by(Expense.created_at).all()
        
        if len(recent_expenses) > 10:
            # Calculate time between entries
            entry_gaps = []
            for i in range(1, len(recent_expenses)):
                gap = (recent_expenses[i].created_at - recent_expenses[i-1].created_at).total_seconds()
                entry_gaps.append(gap)
            
            avg_gap = np.mean(entry_gaps) if entry_gaps else 0
            
            if avg_gap < 30:  # Less than 30 seconds between entries
                signals.append(EmotionalSignal(
                    indicator=StressIndicator.RAPID_EXPENSE_ENTRY,
                    intensity=0.7,
                    timestamp=datetime.now(),
                    context={
                        'entry_count': len(recent_expenses),
                        'avg_seconds': avg_gap,
                        'message': "Rapid expense entry detected - feeling overwhelmed?"
                    },
                    suggested_support=[
                        "Take a breath - accuracy matters more than speed",
                        "Would you like help organizing these expenses?",
                        "Consider using voice entry to reduce stress"
                    ],
                    is_positive=False
                ))
        
        # Check for deletion patterns (frustration indicator)
        # This would need a deletion tracking table in real implementation
        
        return signals
    
    async def analyze_financial_stress(self) -> List[EmotionalSignal]:
        """Detect financial stress from cash flow and expense patterns"""
        
        signals = []
        
        # Get recent financial data
        expenses_30d = self.db.query(Expense).filter(
            Expense.user_id == self.user.id,
            Expense.created_at >= datetime.now() - timedelta(days=30)
        ).all()
        
        if not expenses_30d:
            return signals
        
        # Calculate cash flow stress
        total_expenses = sum(e.amount for e in expenses_30d)
        expense_variance = np.var([e.amount for e in expenses_30d]) if len(expenses_30d) > 1 else 0
        
        # High variance in expenses can indicate financial uncertainty
        if expense_variance > 10000:  # High variance threshold
            signals.append(EmotionalSignal(
                indicator=StressIndicator.CASH_FLOW_STRESS,
                intensity=0.8,
                timestamp=datetime.now(),
                context={
                    'variance': expense_variance,
                    'total_expenses': total_expenses,
                    'message': "Your expenses are fluctuating significantly"
                },
                suggested_support=[
                    "Cash flow uncertainty is stressful - let's create stability",
                    "Consider setting up emergency fund targets",
                    "CORA can help predict upcoming expenses"
                ],
                is_positive=False
            ))
        
        return signals
    
    async def analyze_positive_momentum(self) -> List[EmotionalSignal]:
        """Detect positive patterns and achievements"""
        
        signals = []
        
        # Check for consistent tracking (positive habit)
        daily_entries = defaultdict(int)
        expenses_7d = self.db.query(Expense).filter(
            Expense.user_id == self.user.id,
            Expense.created_at >= datetime.now() - timedelta(days=7)
        ).all()
        
        for expense in expenses_7d:
            day_key = expense.created_at.date()
            daily_entries[day_key] += 1
        
        # If tracking every day, that's positive momentum
        if len(daily_entries) >= 6:
            signals.append(EmotionalSignal(
                indicator=StressIndicator.POSITIVE_MOMENTUM,
                intensity=0.8,
                timestamp=datetime.now(),
                context={
                    'streak_days': len(daily_entries),
                    'message': f"Great job! {len(daily_entries)} days of consistent tracking"
                },
                suggested_support=[
                    "Your consistency is building great financial habits",
                    "This momentum will pay off in better profit visibility",
                    "Keep it up - you're doing amazing!"
                ],
                is_positive=True
            ))
        
        # Check for regular break patterns (self-care)
        work_gaps = self.detect_break_patterns(expenses_7d)
        if work_gaps['taking_breaks']:
            signals.append(EmotionalSignal(
                indicator=StressIndicator.REGULAR_BREAKS,
                intensity=0.6,
                timestamp=datetime.now(),
                context={
                    'break_pattern': work_gaps,
                    'message': "Good work-life balance detected"
                },
                suggested_support=[
                    "Taking breaks is smart business",
                    "Well-rested contractors make better decisions",
                    "Your balance is admirable"
                ],
                is_positive=True
            ))
        
        return signals
    
    async def analyze_interaction_patterns(self) -> List[EmotionalSignal]:
        """Analyze how user interacts with CORA - rushed, careful, etc."""
        
        signals = []
        
        # This would analyze:
        # - Session duration patterns
        # - Feature usage patterns
        # - Error/retry patterns
        # - Help-seeking behavior
        
        # For now, return empty - would need interaction tracking
        return signals
    
    def detect_break_patterns(self, expenses: List[Expense]) -> Dict[str, Any]:
        """Detect if contractor is taking healthy breaks"""
        
        if not expenses:
            return {'taking_breaks': False}
        
        # Group expenses by day and hour
        work_patterns = defaultdict(set)
        for expense in expenses:
            day = expense.created_at.date()
            hour = expense.created_at.hour
            work_patterns[day].add(hour)
        
        # Check for days with reasonable work hours (not working all day)
        reasonable_days = 0
        for day, hours in work_patterns.items():
            if len(hours) < 10:  # Working less than 10 different hours
                reasonable_days += 1
        
        return {
            'taking_breaks': reasonable_days >= 4,
            'reasonable_days': reasonable_days,
            'total_days': len(work_patterns)
        }
    
    def analyze_stress_patterns(self, signals: List[EmotionalSignal]) -> Dict[str, Any]:
        """Analyze signals to determine overall stress patterns"""
        
        if not signals:
            return {
                'stress_level': 3.0,  # Neutral
                'primary_stressors': [],
                'stress_trajectory': 'stable'
            }
        
        # Calculate weighted stress level
        stress_score = 0
        positive_score = 0
        
        for signal in signals:
            if signal.is_positive:
                positive_score += signal.intensity * 2  # Positive signals count double
            else:
                stress_score += signal.intensity
        
        # Normalize to 0-10 scale
        net_stress = stress_score - positive_score
        stress_level = max(0, min(10, 5 + net_stress))
        
        # Identify primary stressors
        negative_signals = [s for s in signals if not s.is_positive]
        primary_stressors = []
        if negative_signals:
            # Group by indicator
            stressor_groups = defaultdict(list)
            for signal in negative_signals:
                stressor_groups[signal.indicator].append(signal)
            
            # Sort by total intensity
            sorted_stressors = sorted(
                stressor_groups.items(), 
                key=lambda x: sum(s.intensity for s in x[1]), 
                reverse=True
            )
            
            primary_stressors = [str(s[0].value) for s in sorted_stressors[:3]]
        
        # Determine trajectory
        if len(self.emotional_history) >= 2:
            previous_stress = self.emotional_history[-2]['profile'].stress_level
            if stress_level > previous_stress + 1:
                trajectory = 'increasing'
            elif stress_level < previous_stress - 1:
                trajectory = 'decreasing'
            else:
                trajectory = 'stable'
        else:
            trajectory = 'unknown'
        
        return {
            'stress_level': stress_level,
            'primary_stressors': primary_stressors,
            'stress_trajectory': trajectory,
            'positive_factors': sum(1 for s in signals if s.is_positive)
        }
    
    def determine_emotional_state(
        self, 
        signals: List[EmotionalSignal], 
        stress_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Determine the current emotional state based on signals and stress"""
        
        stress_level = stress_analysis['stress_level']
        positive_count = stress_analysis['positive_factors']
        trajectory = stress_analysis['stress_trajectory']
        
        # Decision logic for emotional state
        if stress_level >= 8:
            state = EmotionalState.OVERWHELMED
            confidence = 0.85
        elif stress_level >= 6:
            if trajectory == 'increasing':
                state = EmotionalState.STRESSED
                confidence = 0.8
            else:
                state = EmotionalState.STRESSED
                confidence = 0.7
        elif stress_level <= 3 and positive_count >= 2:
            state = EmotionalState.THRIVING
            confidence = 0.9
        elif stress_level <= 4:
            if positive_count >= 1:
                state = EmotionalState.ENERGIZED
                confidence = 0.8
            else:
                state = EmotionalState.BALANCED
                confidence = 0.75
        elif trajectory == 'decreasing':
            state = EmotionalState.RECOVERING
            confidence = 0.7
        else:
            state = EmotionalState.BALANCED
            confidence = 0.6
        
        return {
            'state': state,
            'confidence': confidence,
            'reasoning': self.explain_state_determination(state, signals)
        }
    
    def explain_state_determination(
        self, 
        state: EmotionalState, 
        signals: List[EmotionalSignal]
    ) -> str:
        """Provide human-readable explanation for the state determination"""
        
        explanations = {
            EmotionalState.THRIVING: "You're in a great rhythm with consistent tracking and positive momentum",
            EmotionalState.BALANCED: "You're maintaining steady progress with manageable stress levels",
            EmotionalState.STRESSED: "Several stress indicators suggest you're under pressure",
            EmotionalState.OVERWHELMED: "Multiple high-stress patterns indicate you need support",
            EmotionalState.BURNT_OUT: "Extended stress patterns suggest burnout risk",
            EmotionalState.RECOVERING: "You're showing improvement from previous stress levels",
            EmotionalState.ENERGIZED: "Positive momentum and good habits are energizing your business"
        }
        
        return explanations.get(state, "Analyzing your current state")
    
    def calculate_well_being_metrics(self, signals: List[EmotionalSignal]) -> Dict[str, Any]:
        """Calculate comprehensive well-being metrics"""
        
        # Calculate resilience score (0-100)
        positive_signals = [s for s in signals if s.is_positive]
        negative_signals = [s for s in signals if not s.is_positive]
        
        if not signals:
            resilience_score = 50  # Neutral
        else:
            # Resilience = ability to maintain positive patterns despite stress
            positive_strength = sum(s.intensity for s in positive_signals)
            negative_strength = sum(s.intensity for s in negative_signals)
            
            if negative_strength > 0:
                resilience_ratio = positive_strength / (positive_strength + negative_strength)
            else:
                resilience_ratio = 1.0
            
            resilience_score = int(resilience_ratio * 100)
        
        # Calculate trends
        trends = {
            'work_life_balance': self.calculate_work_life_trend(signals),
            'financial_stability': self.calculate_financial_trend(signals),
            'consistency': self.calculate_consistency_trend(signals),
            'overall_trajectory': 'improving' if resilience_score > 60 else 'needs_attention'
        }
        
        return {
            'resilience_score': resilience_score,
            'trends': trends,
            'strengths': self.identify_strengths(positive_signals),
            'growth_areas': self.identify_growth_areas(negative_signals)
        }
    
    def calculate_work_life_trend(self, signals: List[EmotionalSignal]) -> str:
        """Analyze work-life balance trend"""
        
        work_stress_signals = [
            s for s in signals 
            if s.indicator in [
                StressIndicator.LATE_NIGHT_WORK, 
                StressIndicator.WEEKEND_WORK,
                StressIndicator.LONG_WORK_STREAK
            ]
        ]
        
        balance_signals = [
            s for s in signals 
            if s.indicator == StressIndicator.REGULAR_BREAKS
        ]
        
        if balance_signals and not work_stress_signals:
            return 'excellent'
        elif len(work_stress_signals) > len(balance_signals):
            return 'needs_improvement'
        else:
            return 'moderate'
    
    def calculate_financial_trend(self, signals: List[EmotionalSignal]) -> str:
        """Analyze financial stability trend"""
        
        financial_stress = any(
            s.indicator == StressIndicator.CASH_FLOW_STRESS 
            for s in signals
        )
        
        if financial_stress:
            return 'unstable'
        else:
            return 'stable'
    
    def calculate_consistency_trend(self, signals: List[EmotionalSignal]) -> str:
        """Analyze consistency and momentum trend"""
        
        momentum_signals = [
            s for s in signals 
            if s.indicator == StressIndicator.POSITIVE_MOMENTUM
        ]
        
        if momentum_signals:
            return 'strong'
        else:
            return 'developing'
    
    def identify_strengths(self, positive_signals: List[EmotionalSignal]) -> List[str]:
        """Identify contractor's strengths from positive signals"""
        
        strengths = []
        
        for signal in positive_signals:
            if signal.indicator == StressIndicator.POSITIVE_MOMENTUM:
                strengths.append("Consistent tracking habits")
            elif signal.indicator == StressIndicator.REGULAR_BREAKS:
                strengths.append("Good work-life boundaries")
        
        return list(set(strengths))  # Remove duplicates
    
    def identify_growth_areas(self, negative_signals: List[EmotionalSignal]) -> List[str]:
        """Identify areas for improvement from negative signals"""
        
        growth_areas = []
        
        for signal in negative_signals:
            if signal.indicator == StressIndicator.LATE_NIGHT_WORK:
                growth_areas.append("Setting work hour boundaries")
            elif signal.indicator == StressIndicator.CASH_FLOW_STRESS:
                growth_areas.append("Financial planning and stability")
            elif signal.indicator == StressIndicator.WEEKEND_WORK:
                growth_areas.append("Protecting personal time")
        
        return list(set(growth_areas))  # Remove duplicates
    
    def generate_support_recommendations(
        self,
        emotional_state: Dict[str, Any],
        stress_analysis: Dict[str, Any],
        well_being_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate personalized support recommendations"""
        
        recommendations = []
        state = emotional_state['state']
        stress_level = stress_analysis['stress_level']
        
        # State-specific recommendations
        if state == EmotionalState.OVERWHELMED:
            recommendations.extend([
                {
                    'type': 'immediate_support',
                    'priority': 'high',
                    'title': 'You seem overwhelmed - let\'s help',
                    'message': 'Running a business is tough. CORA is here to lighten the load.',
                    'actions': [
                        'Use voice entry to save time',
                        'Let CORA identify quick wins',
                        'Take a 15-minute break'
                    ],
                    'tone': 'empathetic'
                },
                {
                    'type': 'stress_reduction',
                    'priority': 'high',
                    'title': 'Simplify your workflow',
                    'message': 'Let\'s focus on what matters most right now.',
                    'actions': [
                        'Identify top 3 priorities',
                        'Delegate or delay non-critical tasks',
                        'Use CORA\'s automation features'
                    ],
                    'tone': 'supportive'
                }
            ])
        
        elif state == EmotionalState.STRESSED:
            recommendations.extend([
                {
                    'type': 'preventive_care',
                    'priority': 'medium',
                    'title': 'Stress is building - time for self-care',
                    'message': 'Your well-being directly impacts your business success.',
                    'actions': [
                        'Schedule regular breaks',
                        'Set work hour boundaries',
                        'Use predictive insights to reduce surprises'
                    ],
                    'tone': 'caring'
                }
            ])
        
        elif state == EmotionalState.THRIVING:
            recommendations.extend([
                {
                    'type': 'celebration',
                    'priority': 'low',
                    'title': 'You\'re crushing it! 🎉',
                    'message': 'Your positive momentum is inspiring.',
                    'actions': [
                        'Keep up the great habits',
                        'Share your success strategies',
                        'Set new growth goals'
                    ],
                    'tone': 'celebratory'
                }
            ])
        
        # Stress-specific recommendations
        if stress_level > 7:
            recommendations.append({
                'type': 'crisis_support',
                'priority': 'urgent',
                'title': 'High stress detected',
                'message': 'Remember: This is temporary. You\'ve overcome challenges before.',
                'actions': [
                    'Focus on one task at a time',
                    'Reach out to your support network',
                    'Consider professional business coaching'
                ],
                'tone': 'urgent_caring'
            })
        
        # Pattern-specific recommendations
        for stressor in stress_analysis['primary_stressors']:
            if stressor == 'late_night_work':
                recommendations.append({
                    'type': 'behavior_change',
                    'priority': 'medium',
                    'title': 'Protect your sleep',
                    'message': 'Late night work hurts tomorrow\'s productivity.',
                    'actions': [
                        'Set a work cutoff time',
                        'Use morning hours for complex tasks',
                        'Track how sleep affects your profits'
                    ],
                    'tone': 'educational'
                })
            
            elif stressor == 'cash_flow_stress':
                recommendations.append({
                    'type': 'financial_support',
                    'priority': 'high',
                    'title': 'Cash flow help available',
                    'message': 'CORA can predict and prevent cash crunches.',
                    'actions': [
                        'Review cash flow predictions',
                        'Set up payment reminders',
                        'Identify quick revenue opportunities'
                    ],
                    'tone': 'practical'
                })
        
        return recommendations
    
    def create_empathetic_responses(self, profile: EmotionalProfile) -> List[str]:
        """Create empathetic responses based on emotional profile"""
        
        responses = []
        
        state_responses = {
            EmotionalState.OVERWHELMED: [
                "I notice you've been putting in long hours. You're not alone in this.",
                "Running a business is overwhelming sometimes. Let's tackle one thing at a time.",
                "You're doing better than you think. Let CORA handle some of the load."
            ],
            EmotionalState.STRESSED: [
                "Stress is part of business, but it shouldn't consume you.",
                "You've handled tough times before. You've got this.",
                "Let's find ways to reduce the pressure together."
            ],
            EmotionalState.THRIVING: [
                "Your positive energy is contagious! Keep it up!",
                "You're in the zone - this momentum will take you far.",
                "Success looks good on you! What's your secret?"
            ],
            EmotionalState.BALANCED: [
                "Nice steady progress - consistency wins the race.",
                "You're managing well. Keep this balance.",
                "Solid work - you're building something sustainable."
            ],
            EmotionalState.RECOVERING: [
                "I see you're bouncing back. That's the entrepreneurial spirit!",
                "Recovery takes strength. You're showing it.",
                "Things are looking up - keep moving forward."
            ]
        }
        
        # Get responses for current state
        if profile.current_state in state_responses:
            responses.extend(state_responses[profile.current_state])
        
        # Add specific responses based on stress level
        if profile.stress_level > 8:
            responses.extend([
                "Remember to breathe. Even superheroes need breaks.",
                "Your health is your most important business asset.",
                "It's okay to ask for help. Strong contractors delegate."
            ])
        
        # Add encouraging responses for positive signals
        for signal in profile.recent_signals:
            if signal.is_positive and signal.indicator == StressIndicator.POSITIVE_MOMENTUM:
                responses.append(f"Love seeing your {signal.context.get('streak_days', 'consistent')} day streak!")
        
        return responses
    
    async def generate_wellness_check_in(self) -> Dict[str, Any]:
        """Generate a periodic wellness check-in"""
        
        profile = await self.analyze_emotional_state()
        
        check_in = {
            'type': 'wellness_check',
            'timestamp': datetime.now(),
            'greeting': self.get_contextual_greeting(),
            'observation': self.create_wellness_observation(profile),
            'question': self.create_check_in_question(profile),
            'quick_actions': self.suggest_quick_wellness_actions(profile),
            'tone': self.determine_check_in_tone(profile)
        }
        
        return check_in
    
    def get_contextual_greeting(self) -> str:
        """Get time-appropriate greeting"""
        
        hour = datetime.now().hour
        
        if hour < 12:
            return "Good morning! How are you starting your day?"
        elif hour < 17:
            return "Hey there! How's your afternoon going?"
        elif hour < 20:
            return "Evening! How was your day?"
        else:
            return "Still working? How are you holding up?"
    
    def create_wellness_observation(self, profile: EmotionalProfile) -> str:
        """Create an observation about user's wellness"""
        
        if profile.stress_level > 7:
            return "I've noticed you've been under a lot of pressure lately."
        elif profile.current_state == EmotionalState.THRIVING:
            return "You seem to be in a great flow lately!"
        elif any(s.indicator == StressIndicator.LATE_NIGHT_WORK for s in profile.recent_signals):
            return "I see you've been burning the midnight oil."
        else:
            return "Hope you're taking care of yourself."
    
    def create_check_in_question(self, profile: EmotionalProfile) -> str:
        """Create a check-in question based on profile"""
        
        questions = {
            EmotionalState.OVERWHELMED: "What's the biggest challenge you're facing right now?",
            EmotionalState.STRESSED: "What would help reduce your stress today?",
            EmotionalState.THRIVING: "What's working really well for you lately?",
            EmotionalState.BALANCED: "Anything I can help make easier for you?",
            EmotionalState.RECOVERING: "How are you feeling compared to last week?"
        }
        
        return questions.get(
            profile.current_state, 
            "How can CORA support you better?"
        )
    
    def suggest_quick_wellness_actions(self, profile: EmotionalProfile) -> List[Dict[str, str]]:
        """Suggest quick wellness actions"""
        
        actions = []
        
        if profile.stress_level > 6:
            actions.extend([
                {
                    'icon': '🧘',
                    'text': 'Take 5 deep breaths',
                    'action': 'wellness_breathing'
                },
                {
                    'icon': '☕',
                    'text': 'Quick break',
                    'action': 'start_break_timer'
                }
            ])
        
        if profile.current_state == EmotionalState.THRIVING:
            actions.extend([
                {
                    'icon': '🎯',
                    'text': 'Set new goal',
                    'action': 'goal_setting'
                },
                {
                    'icon': '📊',
                    'text': 'Review wins',
                    'action': 'show_achievements'
                }
            ])
        
        # Always include
        actions.append({
            'icon': '💬',
            'text': 'Just chat',
            'action': 'open_chat'
        })
        
        return actions[:3]  # Max 3 actions
    
    def determine_check_in_tone(self, profile: EmotionalProfile) -> str:
        """Determine appropriate tone for check-in"""
        
        if profile.stress_level > 7:
            return 'gentle_concerned'
        elif profile.current_state == EmotionalState.THRIVING:
            return 'upbeat_encouraging'
        else:
            return 'warm_supportive'


class EmotionalIntelligenceIntegration:
    """
    Integrates Emotional Intelligence with the existing Intelligence Orchestrator
    """
    
    def __init__(self, orchestrator, emotional_engine: EmotionalIntelligenceEngine):
        self.orchestrator = orchestrator
        self.emotional_engine = emotional_engine
    
    async def enhance_orchestration_with_emotion(
        self, 
        base_orchestration: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance the orchestrated response with emotional intelligence"""
        
        # Get emotional profile
        emotional_profile = await self.emotional_engine.analyze_emotional_state()
        
        # Add emotional context to orchestration
        base_orchestration['emotional_context'] = {
            'current_state': emotional_profile.current_state.value,
            'stress_level': emotional_profile.stress_level,
            'confidence': emotional_profile.confidence,
            'support_needed': emotional_profile.stress_level > 6
        }
        
        # Modify presentation based on emotional state
        if emotional_profile.stress_level > 7:
            # Reduce cognitive load when stressed
            base_orchestration['components']['insight_moments']['insights'] = \
                base_orchestration['components']['insight_moments']['insights'][:1]  # Show only 1
            base_orchestration['components']['insight_moments']['display_style'] = 'gentle_display'
        
        # Add emotional support recommendations
        if emotional_profile.support_recommendations:
            base_orchestration['emotional_support'] = {
                'recommendations': emotional_profile.support_recommendations[:2],  # Top 2
                'empathetic_message': self.emotional_engine.create_empathetic_responses(
                    emotional_profile
                )[0] if emotional_profile.support_recommendations else None
            }
        
        # Adjust tone based on emotional state
        base_orchestration['communication_tone'] = self.determine_communication_tone(
            emotional_profile
        )
        
        # Add wellness component if needed
        if emotional_profile.stress_level > 5 or datetime.now().hour in [9, 14, 18]:
            wellness_check = await self.emotional_engine.generate_wellness_check_in()
            base_orchestration['wellness_component'] = wellness_check
        
        return base_orchestration
    
    def determine_communication_tone(self, profile: EmotionalProfile) -> str:
        """Determine appropriate communication tone based on emotional state"""
        
        tone_mapping = {
            EmotionalState.OVERWHELMED: 'gentle_supportive',
            EmotionalState.STRESSED: 'calm_reassuring',
            EmotionalState.THRIVING: 'enthusiastic_encouraging',
            EmotionalState.BALANCED: 'professional_friendly',
            EmotionalState.RECOVERING: 'patient_encouraging',
            EmotionalState.ENERGIZED: 'energetic_motivating',
            EmotionalState.FRUSTRATED: 'understanding_helpful'
        }
        
        return tone_mapping.get(profile.current_state, 'professional_friendly')