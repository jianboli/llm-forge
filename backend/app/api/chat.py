# backend/app/api/chat.py
import logging
from fastapi import APIRouter, HTTPException, Depends
from ..models.chat import ChatRequest, ChatResponse
from ..services import chat_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("", response_model=ChatResponse)
async def handle_chat_message(request: ChatRequest):
    """Receives a chat message and returns the model's response."""
    logger.info(f"Received chat request for model: {request.model_id}")
    try:
        response_text = await chat_service.generate_response(
            model_id=request.model_id,
            prompt=request.message
        )
        return ChatResponse(response=response_text, model_id=request.model_id)
    except ValueError as ve:
         logger.warning(f"Value error in chat request: {ve}")
         raise HTTPException(status_code=404, detail=str(ve)) # e.g., model not found
    except RuntimeError as re:
         logger.error(f"Runtime error during chat generation: {re}", exc_info=True)
         raise HTTPException(status_code=500, detail=str(re)) # e.g., model loading failed
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")