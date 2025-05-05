# backend/app/api/models.py
from fastapi import APIRouter, HTTPException
from typing import List
from ..core.config import AVAILABLE_MODELS
from ..models.chat import ModelInfo # Reusing ModelInfo from chat models

router = APIRouter()

@router.get("", response_model=List[ModelInfo])
async def get_available_models():
    """Returns a list of currently configured models."""
    # Convert the config dict list to ModelInfo objects
    return [ModelInfo(id=m["id"], name=m["name"]) for m in AVAILABLE_MODELS]