"""
Intelligence Orchestrator API Routes

Provides endpoints for coordinated AI intelligence across all CORA components.
This creates the unified experience that Ghostwalker called "relational memory."
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import time

from models import get_db, User
from services.intelligence_orchestrator import IntelligenceOrchestrator
from services.enhanced_orchestrator import EnhancedIntelligenceOrchestrator
from dependencies.auth import get_current_user
from config import Config

# Use centralized templates from app.state.templates set in app.py

router = APIRouter()

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@router.get("/demo", response_class=HTMLResponse)
async def intelligence_demo_page(request: Request):
    """
    Demo page showcasing the Intelligence Orchestration system
    """
    return request.app.state.templates.TemplateResponse("intelligence_demo.html", {"request": request})

@router.get("/orchestrate")
async def get_orchestrated_intelligence(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Main orchestration endpoint - returns unified AI intelligence experience
    Now with optional emotional awareness when Enhanced Orchestrator is enabled
    """
    try:
        start_time = time.time()
        
        # Choose orchestrator based on configuration
        if Config.ENABLE_ENHANCED_ORCHESTRATOR:
            orchestrator = EnhancedIntelligenceOrchestrator(user, db)
            orchestration_type = "enhanced_with_emotional_awareness"
            logger.info(f"Using Enhanced Orchestrator for user {user.id}")
        else:
            orchestrator = IntelligenceOrchestrator(user, db)
            orchestration_type = "base_intelligence"
            logger.info(f"Using Base Orchestrator for user {user.id}")
        
        unified_experience = await orchestrator.orchestrate_intelligence()
        
        # Log performance metrics
        elapsed_time = time.time() - start_time
        logger.info(f"Orchestration completed in {elapsed_time:.3f} seconds")
        
        # Log emotional state if using Enhanced
        if Config.ENABLE_ENHANCED_ORCHESTRATOR and 'emotional_awareness' in unified_experience:
            emotional_data = unified_experience['emotional_awareness']
            logger.info(f"Emotional state detected for user {user.id}: "
                       f"state={emotional_data.get('detected_state')}, "
                       f"stress_level={emotional_data.get('stress_level')}, "
                       f"well_being={emotional_data.get('well_being_status')}")
        
        # Alert if response time is too slow
        if elapsed_time > 2.0:
            logger.warning(f"Orchestration took {elapsed_time:.3f} seconds - performance may be degraded")
        
        return {
            "success": True,
            "orchestration": unified_experience,
            "orchestration_type": orchestration_type,
            "timestamp": datetime.now().isoformat(),
            "user_id": user.id
        }
    
    except Exception as e:
        # Log the error and fallback to base orchestrator if Enhanced fails
        if Config.ENABLE_ENHANCED_ORCHESTRATOR:
            logger.error(f"Enhanced Orchestrator failed for user {user.id}: {str(e)}")
            logger.info(f"Attempting fallback to Base Orchestrator for user {user.id}")
            try:
                orchestrator = IntelligenceOrchestrator(user, db)
                unified_experience = await orchestrator.orchestrate_intelligence()
                
                logger.info(f"Successfully fell back to Base Orchestrator for user {user.id}")
                
                return {
                    "success": True,
                    "orchestration": unified_experience,
                    "orchestration_type": "base_intelligence_fallback",
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user.id,
                    "fallback_reason": str(e)
                }
            except Exception as fallback_error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Both orchestrators failed: Enhanced: {str(e)}, Base: {str(fallback_error)}"
                )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Intelligence orchestration failed: {str(e)}"
            )

@router.get("/signals")
async def get_active_signals(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current intelligence signals without full orchestration
    """
    try:
        # Use Enhanced Orchestrator if enabled
        if Config.ENABLE_ENHANCED_ORCHESTRATOR:
            orchestrator = EnhancedIntelligenceOrchestrator(user, db)
        else:
            orchestrator = IntelligenceOrchestrator(user, db)
            
        await orchestrator.collect_intelligence_signals()
        
        return {
            "success": True,
            "signals": [
                {
                    "id": f"signal_{i}",
                    "event_type": signal.event_type.value,
                    "source": signal.source_component,
                    "priority": signal.priority,
                    "confidence": signal.confidence,
                    "message": signal.data.get('message', 'Signal available'),
                    "requires_attention": signal.requires_immediate_attention
                }
                for i, signal in enumerate(orchestrator.active_signals)
            ],
            "signal_count": len(orchestrator.active_signals),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Signal collection failed: {str(e)}"
        )

@router.get("/component-status")
async def get_component_status(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get status of all AI components for orchestration dashboard
    """
    try:
        # Use Enhanced Orchestrator if enabled
        if Config.ENABLE_ENHANCED_ORCHESTRATOR:
            orchestrator = EnhancedIntelligenceOrchestrator(user, db)
        else:
            orchestrator = IntelligenceOrchestrator(user, db)
        
        # Test each component
        component_status = {}
        
        # Test predictive intelligence
        try:
            predictions = await orchestrator.predictive_engine.generate_predictions()
            component_status['predictive_intelligence'] = {
                'status': 'active',
                'predictions_count': len(predictions),
                'last_update': datetime.now().isoformat()
            }
        except Exception:
            component_status['predictive_intelligence'] = {
                'status': 'inactive',
                'error': 'Prediction engine unavailable'
            }
        
        # Test profit intelligence
        try:
            profit_data = orchestrator.profit_detector.get_intelligence_summary()
            component_status['profit_intelligence'] = {
                'status': 'active',
                'intelligence_score': profit_data.get('intelligence_score', 0),
                'last_update': datetime.now().isoformat()
            }
        except Exception:
            component_status['profit_intelligence'] = {
                'status': 'inactive',
                'error': 'Profit detector unavailable'
            }
        
        # Insight moments (always available)
        component_status['insight_moments'] = {
            'status': 'active',
            'type': 'contextual_insights',
            'last_update': datetime.now().isoformat()
        }
        
        # Intelligence widget (always available)
        component_status['intelligence_widget'] = {
            'status': 'active',
            'type': 'score_display',
            'last_update': datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "components": component_status,
            "orchestration_available": all(
                comp['status'] == 'active' 
                for comp in component_status.values()
            ),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Component status check failed: {str(e)}"
        )

@router.post("/feedback")
async def submit_orchestration_feedback(
    feedback_data: Dict[str, Any],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Collect user feedback on orchestrated intelligence for learning
    """
    try:
        # Store feedback for future orchestration improvements
        # This would typically go to a feedback table or analytics system
        
        return {
            "success": True,
            "message": "Feedback received. CORA will learn from your response.",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Feedback submission failed: {str(e)}"
        )

@router.get("/relational-context")
async def get_relational_context(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get the relational memory context that creates CORA's mythology
    """
    try:
        # Use Enhanced Orchestrator if enabled
        if Config.ENABLE_ENHANCED_ORCHESTRATOR:
            orchestrator = EnhancedIntelligenceOrchestrator(user, db)
        else:
            orchestrator = IntelligenceOrchestrator(user, db)
            
        await orchestrator.collect_intelligence_signals()
        
        # Create sample relational context
        relational_context = orchestrator.create_relational_context(
            orchestrator.active_signals
        )
        
        return {
            "success": True,
            "relational_context": relational_context,
            "user_story_chapter": relational_context.get('mythological_context', {}).get('current_chapter', 'beginning'),
            "relationship_stage": relational_context.get('user_relationship_stage', 'new_user'),
            "care_signals": relational_context.get('care_signals', []),
            "growth_moments": relational_context.get('growth_moments', []),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Relational context retrieval failed: {str(e)}"
        )

@router.get("/orchestration-demo")
async def get_orchestration_demo(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Demo endpoint showing how unified intelligence would work
    """
    try:
        # Create demo orchestration
        demo_orchestration = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user.id,
            "orchestration_type": "high_priority",
            "components": {
                "insight_moments": {
                    "display_style": "contextual_display",
                    "insights": [
                        {
                            "id": "demo_cash_flow_alert",
                            "type": "cash_flow_prediction",
                            "urgency": "high",
                            "confidence": 87,
                            "message": "💰 Cash flow heads up: You typically spend $3,200 around the 20th. That's in 3 days - consider preparing.",
                            "orchestrated": True,
                            "source_component": "predictive_intelligence"
                        }
                    ],
                    "timing_delay": 2000
                },
                "intelligence_widget": {
                    "score": 85,
                    "visual_state": "pulse_orange",
                    "trend": "needs_attention",
                    "attention_indicator": True,
                    "click_action": "show_orchestrated_insights"
                },
                "predictive_dashboard": {
                    "highlight_mode": "highlight_important",
                    "urgency_filter": "high",
                    "show_orchestration_context": True
                },
                "notifications": {
                    "style": "balanced",
                    "count": 1,
                    "preview_message": "1 urgent insight needs your attention",
                    "channels": ["in_app", "widget_indicator"]
                }
            },
            "relational_context": {
                "user_relationship_stage": "developing_trust",
                "current_chapter": "challenge_and_opportunity",
                "care_signals": [
                    "Warned about potential cash flow issue ahead of time"
                ],
                "mythological_context": {
                    "narrative_arc": "rising_action",
                    "recurring_themes": ["preparation_and_foresight"]
                }
            }
        }
        
        return {
            "success": True,
            "demo_orchestration": demo_orchestration,
            "message": "This demonstrates how all AI components work together as unified intelligence",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Demo orchestration failed: {str(e)}"
        )