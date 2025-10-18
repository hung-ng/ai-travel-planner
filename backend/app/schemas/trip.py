from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class TripCreate(BaseModel):
    user_id: int
    destination: str
    start_date: datetime
    end_date: datetime
    budget: Optional[int] = None
    preferences: Optional[Dict[str, Any]] = None

class TripResponse(BaseModel):
    id: int
    user_id: int
    destination: str
    start_date: datetime
    end_date: datetime
    budget: Optional[int]
    status: str
    itinerary: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True