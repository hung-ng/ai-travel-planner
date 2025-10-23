from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from app.database import Base

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    messages = Column(JSON, default=list)
    context = Column(JSON, default=dict)
    summary = Column(Text, nullable=True)
    message_count = Column(Integer, default=0)
    last_summarized_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())