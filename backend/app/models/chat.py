# backend/app/models/chat.py
from pydantic import BaseModel
from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    model_id: str
    message: str
    # Add history later if needed: history: list[dict[str, str]] = []

class ChatResponse(BaseModel):
    response: str
    model_id: str

class ModelInfo(BaseModel):
    id: str = Field(..., description="Unique identifier for the model")
    name: str = Field(..., description="User-friendly name for the model")
    source: Optional[str] = Field(None, description="Origin of the model (e.g., OpenAI, Hugging Face, Local)")
    deployed: bool = Field(..., description="Indicates if the model is actively deployed/available")

    class Config:
        orm_mode = True # If you load this from a DB model later