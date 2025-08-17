"""
CORA AI Routes - API endpoints for intelligent CORA conversations
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Dict, Optional, List
from services.cora_ai_service import CORAAIService
from sqlalchemy.orm import Session
from dependencies.database import get_db
from dependencies.auth_hybrid import get_current_user_hybrid

router = APIRouter(prefix="/api/cora-ai", tags=["CORA AI"])

# Initialize AI service
ai_service = CORAAIService()

class ChatMessage(BaseModel):
    message: str
    business_context: Optional[Dict] = None
    personality_state: Optional[Dict] = None

class ChatResponse(BaseModel):
    response: str
    personality_state: Dict
    conversation_summary: Dict

class ConversationHistory(BaseModel):
    messages: List[Dict]
    summary: Dict

@router.post("/chat", response_model=ChatResponse)
async def chat_with_cora(
    chat_message: ChatMessage,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Chat with CORA using AI integration
    """
    try:
        # Try to enhance with user context (optional auth via cookie or header)
        try:
            user = await get_current_user_hybrid(request)
        except Exception:
            user = None

        if user is not None:
            response = await ai_service.generate_enhanced_response(
                user_message=chat_message.message,
                user=user,
                db=db,
                business_context=chat_message.business_context,
                personality_state=chat_message.personality_state,
            )
        else:
            # Fallback to basic response for unauthenticated users
            response = await ai_service.generate_response(
                user_message=chat_message.message,
                business_context=chat_message.business_context,
                personality_state=chat_message.personality_state,
            )
        
        # Get updated personality state (simplified for now)
        personality_state = chat_message.personality_state or {
            "relationship_level": 1,
            "mood": "neutral",
            "trust_score": 75
        }
        
        # Update relationship level based on interaction
        if chat_message.message.lower() in ['how are you', 'feeling', 'mood']:
            personality_state["relationship_level"] = min(5, personality_state.get("relationship_level", 1) + 1)
        
        # Get conversation summary
        conversation_summary = ai_service.get_conversation_summary()
        
        return ChatResponse(
            response=response,
            personality_state=personality_state,
            conversation_summary=conversation_summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Service Error: {str(e)}")

@router.get("/conversation-history", response_model=ConversationHistory)
async def get_conversation_history():
    """
    Get CORA's conversation history
    """
    try:
        return ConversationHistory(
            messages=ai_service.conversation_history,
            summary=ai_service.get_conversation_summary()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving conversation history: {str(e)}")

@router.post("/reset-conversation")
async def reset_conversation():
    """
    Reset CORA's conversation history
    """
    try:
        ai_service.conversation_history = []
        return {"message": "Conversation history reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting conversation: {str(e)}")

@router.get("/health")
async def ai_service_health():
    """
    Check CORA AI service health
    """
    try:
        # Test AI service with a simple message
        test_response = await ai_service.generate_response(
            user_message="Hello",
            business_context={"profit_score": 85},
            personality_state={"relationship_level": 1, "mood": "neutral"}
        )
        
        return {
            "status": "healthy",
            "ai_service": "operational",
            "test_response": test_response[:50] + "..." if len(test_response) > 50 else test_response
        }
    except Exception as e:
        return {
            "status": "degraded",
            "ai_service": "error",
            "error": str(e)
        } 