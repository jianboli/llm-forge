# backend/app/models/chat.py
from pydantic import BaseModel

class ChatRequest(BaseModel):
    model_id: str
    message: str
    # Add history later if needed: history: list[dict[str, str]] = []

class ChatResponse(BaseModel):
    response: str
    model_id: str

class ModelInfo(BaseModel):
    id: str
    name: str
    # type: str = "local" # Add later if mixing local/API