from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum
from sqlalchemy.sql import func
import enum
from app.database import Base

class TripStatus(str, enum.Enum):
    GATHERING = "gathering"
    GENERATING = "generating"
    REVIEWING = "reviewing"
    FINALIZED = "finalized"
    ARCHIVED = "archived"

class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    destination = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    budget = Column(Integer, nullable=True)
    status = Column(Enum(TripStatus), default=TripStatus.GATHERING)
    itinerary = Column(JSON, nullable=True)
    preferences = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())