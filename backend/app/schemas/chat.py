from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    trip_id: int
    user_id: int

class ChatResponse(BaseModel):
    message: str
    conversation_id: int