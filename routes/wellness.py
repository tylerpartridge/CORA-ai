"""
Emotional Wellness API Routes

Provides endpoints for emotional intelligence, stress detection, and wellness support.
Part of CORA's empathetic AI system that cares about contractor well-being.

Created by: Opus
Date: 2025-08-03
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from pydantic import BaseModel

from dependencies.auth import get_current_user
from models import User, get_db
from services.emotional_intelligence import (
    EmotionalIntelligenceEngine,
    EmotionalProfile,
    EmotionalState,
    StressIndicator
)
from services.intelligence_orchestrator import IntelligenceOrchestrator
from utils.api_response import APIResponse, ErrorCodes

# Create router
router = APIRouter(
    prefix="/api/wellness",
    tags=["wellness"],
    responses={404: {"description": "Not found"}},
)


# Request/Response Models
class WellnessCheckResponse(BaseModel):
    profile: Dict[str, Any]
    check_in: Optional[Dict[str, Any]]
    support_available: bool
    last_check: Optional[datetime]


class WellnessInteractionRequest(BaseModel):
    action: str
    timestamp: datetime
    context: Optional[Dict[str, Any]] = None


class QuickActionRequest(BaseModel):
    action_type: str  # breathing, break, chat
    duration: Optional[int] = None  # For break timer


# Wellness Check Endpoint
@router.get("/check", response_model=WellnessCheckResponse)
async def check_emotional_wellness(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze current emotional state and well-being
    """
    try:
        # Initialize emotional intelligence engine
        emotional_engine = EmotionalIntelligenceEngine(current_user, db)
        
        # Analyze current state
        profile = await emotional_engine.analyze_emotional_state()
        
        # Convert profile to dict for response
        profile_dict = {
            'current_state': profile.current_state.value,
            'confidence': profile.confidence,
            'stress_level': profile.stress_level,
            'resilience_score': profile.resilience_score,
            'recent_signals': [
                {
                    'indicator': signal.indicator.value,
                    'intensity': signal.intensity,
                    'is_positive': signal.is_positive,
                    'context': signal.context
                }
                for signal in profile.recent_signals[:5]  # Top 5 signals
            ],
            'support_recommendations': profile.support_recommendations[:3],  # Top 3 recommendations
            'well_being_trends': profile.well_being_trends
        }
        
        # Generate check-in if needed
        check_in = None
        if profile.stress_level > 6 or datetime.now().hour in [9, 14, 18]:
            check_in = await emotional_engine.generate_wellness_check_in()
        
        return WellnessCheckResponse(
            profile=profile_dict,
            check_in=check_in,
            support_available=profile.stress_level > 5,
            last_check=datetime.now()
        )
        
    except Exception as e:
        print(f"Wellness check error: {str(e)}")
        # Return neutral state on error
        return WellnessCheckResponse(
            profile={
                'current_state': EmotionalState.BALANCED.value,
                'confidence': 0.5,
                'stress_level': 5.0,
                'resilience_score': 50,
                'recent_signals': [],
                'support_recommendations': [],
                'well_being_trends': {}
            },
            check_in=None,
            support_available=False,
            last_check=None
        )


# Record Emotional State (compat shim for frontend expectation)
class EmotionalStateUpdate(BaseModel):
    state: str
    level: float | int | None = None
    context: Optional[Dict[str, Any]] = None


@router.post("/emotional-state")
async def update_emotional_state(
    request: EmotionalStateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Store/acknowledge user's emotional state.
    Minimal persistence for now; integrates with orchestrator over time.
    """
    try:
        # Best-effort persistence if a preferences table exists
        try:
            from models import UserPreference
            key = "emotional_state"
            value = {
                "state": request.state,
                "level": request.level,
                "context": request.context or {},
            }
            pref = db.query(UserPreference).filter(
                UserPreference.user_email == current_user.email,
                UserPreference.key == key
            ).first()
            if pref:
                pref.value = json.dumps(value)
            else:
                pref = UserPreference(
                    user_email=current_user.email,
                    key=key,
                    value=json.dumps(value)
                )
                db.add(pref)
            db.commit()
        except Exception:
            # Non-fatal; continue without DB persistence
            db.rollback()
        return {"status": "success", "message": "Emotional state recorded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to record emotional state")

# Enhanced Intelligence Orchestration with Emotion
@router.get("/orchestrated-intelligence")
async def get_emotionally_aware_intelligence(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get orchestrated intelligence enhanced with emotional awareness
    """
    try:
        # Initialize both engines
        orchestrator = IntelligenceOrchestrator(current_user, db)
        emotional_engine = EmotionalIntelligenceEngine(current_user, db)
        
        # Get base orchestration
        base_orchestration = await orchestrator.orchestrate_intelligence()
        
        # Get emotional profile
        emotional_profile = await emotional_engine.analyze_emotional_state()
        
        # Enhance with emotional intelligence
        enhanced_response = {
            **base_orchestration,
            'emotional_context': {
                'current_state': emotional_profile.current_state.value,
                'stress_level': emotional_profile.stress_level,
                'confidence': emotional_profile.confidence,
                'support_needed': emotional_profile.stress_level > 6,
                'empathetic_message': emotional_engine.create_empathetic_responses(
                    emotional_profile
                )[0] if emotional_profile.support_recommendations else None
            }
        }
        
        # Adjust components based on emotional state
        if emotional_profile.stress_level > 7:
            # Simplify when overwhelmed
            if 'components' in enhanced_response:
                if 'insight_moments' in enhanced_response['components']:
                    enhanced_response['components']['insight_moments']['display_style'] = 'gentle_display'
                    # Show fewer insights when stressed
                    insights = enhanced_response['components']['insight_moments'].get('insights', [])
                    enhanced_response['components']['insight_moments']['insights'] = insights[:1]
        
        # Add wellness component if stress is detected
        if emotional_profile.stress_level > 5:
            enhanced_response['wellness_support'] = {
                'available': True,
                'priority': 'high' if emotional_profile.stress_level > 7 else 'medium',
                'quick_actions': [
                    {'type': 'breathing', 'label': 'Breathing Exercise', 'icon': '🧘'},
                    {'type': 'break', 'label': 'Take a Break', 'icon': '☕'},
                    {'type': 'chat', 'label': 'Talk to CORA', 'icon': '💬'}
                ],
                'message': emotional_profile.support_recommendations[0]['message'] 
                    if emotional_profile.support_recommendations else 
                    "I'm here if you need support."
            }
        
        return enhanced_response
        
    except Exception as e:
        print(f"Enhanced orchestration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate emotionally aware intelligence")


# Track Wellness Interactions
@router.post("/interaction")
async def track_wellness_interaction(
    request: WellnessInteractionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Track user interactions with wellness features for learning
    """
    try:
        # In a real implementation, this would save to a wellness_interactions table
        # For now, we'll just acknowledge the interaction
        
        interaction_data = {
            'user_id': current_user.id,
            'action': request.action,
            'timestamp': request.timestamp,
            'context': request.context or {}
        }
        
        # Log interaction for learning
        print(f"Wellness interaction: {interaction_data}")
        
        # Special handling for certain actions
        response = {'status': 'tracked', 'action': request.action}
        
        if request.action == 'late_night_acknowledged':
            response['message'] = "Rest well! Your business needs you at your best."
        elif request.action == 'check_in_opened':
            response['message'] = "Taking time for self-care is smart business."
        elif request.action.startswith('quick_action_'):
            response['message'] = "Great choice! Small breaks lead to big productivity."
        
        return response
        
    except Exception as e:
        print(f"Interaction tracking error: {str(e)}")
        return APIResponse.error(
            message="Failed to track interaction",
            error_code=ErrorCodes.INTERNAL_ERROR,
            details={"original_error": str(e)}
        )


# Get Personalized Support
@router.get("/support/{support_type}")
async def get_personalized_support(
    support_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized support content based on current emotional state
    """
    try:
        # Initialize emotional engine
        emotional_engine = EmotionalIntelligenceEngine(current_user, db)
        
        # Get current profile
        profile = await emotional_engine.analyze_emotional_state()
        
        # Generate support based on type and state
        if support_type == 'breathing':
            return {
                'type': 'breathing_exercise',
                'duration': 5 if profile.stress_level > 7 else 3,  # Longer for higher stress
                'pattern': {
                    'inhale': 4,
                    'hold': 4,
                    'exhale': 6,
                    'rest': 2
                },
                'guidance': [
                    "Find a comfortable position",
                    "Close your eyes if you'd like",
                    "Follow the rhythm at your own pace",
                    "It's okay if your mind wanders - gently bring it back"
                ],
                'message': "This breathing pattern activates your parasympathetic nervous system, reducing stress hormones."
            }
            
        elif support_type == 'break':
            # Suggest break duration based on stress
            if profile.stress_level > 8:
                duration = 20
                activities = [
                    "Step outside for fresh air",
                    "Do some light stretching",
                    "Call someone you care about",
                    "Listen to calming music"
                ]
            elif profile.stress_level > 5:
                duration = 15
                activities = [
                    "Take a short walk",
                    "Make a healthy snack",
                    "Do 5 minutes of stretching",
                    "Practice gratitude"
                ]
            else:
                duration = 10
                activities = [
                    "Stretch at your desk",
                    "Get a glass of water",
                    "Look out the window",
                    "Take deep breaths"
                ]
            
            return {
                'type': 'break_suggestion',
                'duration': duration,
                'activities': activities,
                'message': f"A {duration}-minute break will help you return refreshed and focused."
            }
            
        elif support_type == 'affirmations':
            # Provide state-specific affirmations
            affirmations = {
                EmotionalState.OVERWHELMED: [
                    "You've handled difficult times before, and you'll handle this too.",
                    "It's okay to feel overwhelmed - it means you care deeply.",
                    "One step at a time is still progress.",
                    "Your worth isn't measured by your productivity."
                ],
                EmotionalState.STRESSED: [
                    "Stress is temporary, but your strength is permanent.",
                    "You're doing better than you think you are.",
                    "It's okay to ask for help - strong people delegate.",
                    "This challenge is making you stronger."
                ],
                EmotionalState.THRIVING: [
                    "Your hard work is paying off - celebrate it!",
                    "Success looks good on you!",
                    "You're inspiring others with your progress.",
                    "Keep riding this wave of momentum!"
                ],
                EmotionalState.BALANCED: [
                    "Balance is a skill, and you're mastering it.",
                    "Steady progress wins the race.",
                    "You're building something sustainable.",
                    "Your consistency is your superpower."
                ]
            }
            
            state_affirmations = affirmations.get(
                profile.current_state, 
                ["You're doing great.", "Keep going.", "You've got this."]
            )
            
            return {
                'type': 'affirmations',
                'affirmations': state_affirmations,
                'state': profile.current_state.value,
                'message': "Read these whenever you need a reminder of your strength."
            }
            
        elif support_type == 'tips':
            # Provide practical tips based on stress indicators
            tips = []
            
            for signal in profile.recent_signals[:3]:
                if signal.indicator == StressIndicator.LATE_NIGHT_WORK:
                    tips.extend([
                        "Set a 'work shutdown' alarm for 9 PM",
                        "Create a relaxing evening routine",
                        "Keep work devices out of the bedroom"
                    ])
                elif signal.indicator == StressIndicator.WEEKEND_WORK:
                    tips.extend([
                        "Block out 'no work' time on weekends",
                        "Plan enjoyable weekend activities in advance",
                        "Remember: Rest is productive"
                    ])
                elif signal.indicator == StressIndicator.CASH_FLOW_STRESS:
                    tips.extend([
                        "Review CORA's cash flow predictions daily",
                        "Set up automatic payment reminders",
                        "Focus on collecting outstanding invoices"
                    ])
            
            # Remove duplicates
            tips = list(set(tips))[:5]
            
            return {
                'type': 'practical_tips',
                'tips': tips if tips else [
                    "Take regular breaks every 90 minutes",
                    "Stay hydrated throughout the day",
                    "Celebrate small wins",
                    "Set realistic daily goals",
                    "End each day by noting 3 accomplishments"
                ],
                'message': "Small changes can make a big difference in your well-being."
            }
            
        else:
            raise HTTPException(status_code=404, detail=f"Support type '{support_type}' not found")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Support generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate support content")


# Wellness History
@router.get("/history")
async def get_wellness_history(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get wellness history and trends
    """
    try:
        # In a real implementation, this would query historical wellness data
        # For now, return a sample response
        
        return {
            'period': f'last_{days}_days',
            'average_stress_level': 5.2,
            'stress_trend': 'decreasing',
            'most_common_state': 'balanced',
            'positive_days': 4,
            'challenging_days': 3,
            'wellness_score': 72,  # Out of 100
            'improvements': [
                'Taking more regular breaks',
                'Better work-hour boundaries'
            ],
            'areas_for_growth': [
                'Weekend work patterns',
                'Late night sessions'
            ],
            'message': 'Your wellness is trending in the right direction. Keep it up!'
        }
        
    except Exception as e:
        print(f"Wellness history error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve wellness history")


# Emergency Support
@router.post("/emergency-support")
async def request_emergency_support(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Provide immediate support for high-stress situations
    """
    try:
        return {
            'type': 'emergency_support',
            'immediate_actions': [
                {
                    'step': 1,
                    'action': 'Take 3 deep breaths',
                    'instruction': 'Breathe in for 4, hold for 4, out for 6'
                },
                {
                    'step': 2,
                    'action': 'Ground yourself',
                    'instruction': 'Name 5 things you can see, 4 you can touch, 3 you can hear'
                },
                {
                    'step': 3,
                    'action': 'Step away',
                    'instruction': 'Take a 5-minute break from whatever you\'re doing'
                }
            ],
            'support_message': "You're not alone. This feeling will pass. Focus on one breath at a time.",
            'resources': [
                {
                    'type': 'video',
                    'title': '5-Minute Calm Down',
                    'url': '/wellness/resources/calm-down'
                },
                {
                    'type': 'audio',
                    'title': 'Guided Breathing',
                    'url': '/wellness/resources/breathing-audio'
                }
            ],
            'follow_up': 'CORA will check in with you in 30 minutes.'
        }
        
    except Exception as e:
        print(f"Emergency support error: {str(e)}")
        # Always return something for emergency support
        return {
            'type': 'emergency_support',
            'immediate_actions': [
                {
                    'step': 1,
                    'action': 'Breathe deeply',
                    'instruction': 'Take slow, deep breaths'
                }
            ],
            'support_message': "Take a moment to breathe. You've got this.",
            'resources': [],
            'follow_up': 'We\'re here for you.'
        }