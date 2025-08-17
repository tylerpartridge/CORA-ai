"""
Predictive Intelligence API

Serves proactive predictions and anticipatory insights to help contractors
stay ahead of their business needs.

Philosophy: True AI partnership means anticipating needs, not just responding.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

from dependencies.auth_hybrid import get_current_user_hybrid
from dependencies.database import get_db
from models.user import User
from services.predictive_intelligence import PredictiveIntelligenceEngine
from models import PredictionFeedback

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/predictions")
async def get_predictions(
    days_ahead: Optional[int] = Query(7, description="How many days ahead to predict"),
    prediction_types: Optional[str] = Query(None, description="Comma-separated list of prediction types to include"),
    current_user: User = Depends(get_current_user_hybrid),
    db: Session = Depends(get_db)
):
    """Get predictive insights for the current user"""
    
    try:
        engine = PredictiveIntelligenceEngine(current_user, db)
        predictions = await engine.generate_predictions()
        
        # Filter by prediction types if specified
        if prediction_types:
            type_filter = [t.strip() for t in prediction_types.split(',')]
            predictions = [p for p in predictions if p['type'] in type_filter]
        
        # Filter by time horizon
        predictions = [p for p in predictions if p['days_ahead'] <= days_ahead]
        
        return JSONResponse({
            'status': 'success',
            'predictions': predictions,
            'generated_at': datetime.now().isoformat(),
            'days_ahead': days_ahead,
            'user_id': current_user.id
        })
        
    except Exception as e:
        logger.error(f"Error generating predictions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate predictions")

@router.get("/predictions/{prediction_type}")
async def get_predictions_by_type(
    prediction_type: str,
    current_user: User = Depends(get_current_user_hybrid),
    db: Session = Depends(get_db)
):
    """Get predictions of a specific type"""
    
    try:
        engine = PredictiveIntelligenceEngine(current_user, db)
        all_predictions = await engine.generate_predictions()
        
        # Filter by type
        filtered_predictions = [p for p in all_predictions if p['type'] == prediction_type]
        
        return JSONResponse({
            'status': 'success',
            'predictions': filtered_predictions,
            'prediction_type': prediction_type,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating {prediction_type} predictions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate {prediction_type} predictions")

@router.post("/predictions/{prediction_id}/acknowledge")
async def acknowledge_prediction(
    prediction_id: str,
    action_taken: Optional[str] = None,
    current_user: User = Depends(get_current_user_hybrid),
    db: Session = Depends(get_db)
):
    """Mark a prediction as acknowledged/acted upon"""
    
    try:
        # Store acknowledgment in database for learning
        # This helps the ML improve predictions over time
        
        feedback = PredictionFeedback(
            user_id=current_user.id,
            prediction_id=prediction_id,
            action_taken=action_taken
        )
        db.add(feedback)
        db.commit()
        return JSONResponse({
            'status': 'success',
            'prediction_id': prediction_id,
            'acknowledged_at': datetime.now().isoformat(),
            'action_taken': action_taken,
            'message': 'Prediction acknowledged'
        })
        
    except Exception as e:
        logger.error(f"Error acknowledging prediction {prediction_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to acknowledge prediction")

@router.get("/patterns")
async def get_user_patterns(
    current_user: User = Depends(get_current_user_hybrid),
    db: Session = Depends(get_db)
):
    """Get analyzed patterns for the current user"""
    
    try:
        engine = PredictiveIntelligenceEngine(current_user, db)
        await engine.analyze_user_patterns()
        
        return JSONResponse({
            'status': 'success',
            'patterns': engine.patterns,
            'analyzed_at': datetime.now().isoformat(),
            'user_id': current_user.id
        })
        
    except Exception as e:
        logger.error(f"Error analyzing user patterns: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze patterns")

@router.get("/forecast/cash-flow")
async def get_cash_flow_forecast(
    days_ahead: Optional[int] = Query(30, description="Days ahead to forecast"),
    current_user: User = Depends(get_current_user_hybrid),
    db: Session = Depends(get_db)
):
    """Get detailed cash flow forecast"""
    
    try:
        engine = PredictiveIntelligenceEngine(current_user, db)
        await engine.analyze_user_patterns()
        
        cash_flow_predictions = await engine.predict_cash_flow_needs()
        
        return JSONResponse({
            'status': 'success',
            'forecast': cash_flow_predictions,
            'days_ahead': days_ahead,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating cash flow forecast: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate cash flow forecast")

@router.get("/forecast/materials")
async def get_material_forecast(
    current_user: User = Depends(get_current_user_hybrid),
    db: Session = Depends(get_db)
):
    """Get material needs forecast"""
    
    try:
        engine = PredictiveIntelligenceEngine(current_user, db)
        await engine.analyze_user_patterns()
        
        material_predictions = await engine.predict_material_needs()
        
        return JSONResponse({
            'status': 'success',
            'forecast': material_predictions,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating material forecast: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate material forecast")

@router.get("/forecast/weather")
async def get_weather_impact_forecast(
    current_user: User = Depends(get_current_user_hybrid),
    db: Session = Depends(get_db)
):
    """Get weather impact predictions"""
    
    try:
        engine = PredictiveIntelligenceEngine(current_user, db)
        weather_predictions = await engine.predict_weather_impacts()
        
        return JSONResponse({
            'status': 'success',
            'forecast': weather_predictions,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating weather forecast: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate weather forecast")