from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.models.conversation import Conversation
from app.models.trip import Trip
from app.services.conversation import conversation_service
from app.services.context import context_manager

router = APIRouter()

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest, db: Session = Depends(get_db)):
    """Send a message in a conversation"""
    
    # Get trip first (to get user_id)
    trip = db.query(Trip).filter(Trip.id == request.trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Verify user owns this trip
    if trip.user_id != request.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get or create conversation
    conversation = db.query(Conversation).filter(
        Conversation.trip_id == request.trip_id
    ).first()
    
    if not conversation:
        conversation = Conversation(
            trip_id=request.trip_id,
            user_id=request.user_id,
            messages=[],
            context={},
            summary=None,
            message_count=0,
            last_summarized_index=0
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Get trip context
    trip = db.query(Trip).filter(Trip.id == request.trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    trip_context = {
        "destination": trip.destination,
        "start_date": trip.start_date.isoformat() if trip.start_date else None,
        "end_date": trip.end_date.isoformat() if trip.end_date else None,
        "budget": trip.budget,
        "status": trip.status
    }
    
    # Process message
    ai_response, updated_context, updated_summary = await conversation_service.process_message(
        user_message=request.message,
        conversation_history=conversation.messages or [],
        conversation_summary=conversation.summary,
        conversation_context=conversation.context or {},
        trip_context=trip_context
    )
    
    # Add new messages
    new_messages = [
        {"role": "user", "content": request.message},
        {"role": "assistant", "content": ai_response}
    ]
    conversation.messages = (conversation.messages or []) + new_messages
    
    # Update context
    conversation.context = updated_context
    conversation.message_count = len(conversation.messages)
    
    # Check if we should summarize with correct index
    should_summarize = await context_manager.should_summarize(
        message_count=conversation.message_count,
        last_summarized_index=conversation.last_summarized_index
    )
    
    if should_summarize:
        print(f"\n[SUMMARIZATION] Threshold reached! Creating summary...")
        print(f"[SUMMARIZATION] Total messages: {conversation.message_count}")
        print(f"[SUMMARIZATION] Last summarized at: {conversation.last_summarized_index}")
        
        # Create/update summary
        updated_summary = await context_manager.create_summary(
            messages=conversation.messages,
            existing_summary=conversation.summary
        )
        
        conversation.summary = updated_summary
        conversation.last_summarized_index = conversation.message_count
        
        print(f"[SUMMARIZATION] ✅ Summary created: {updated_summary[:100]}...")
    
    db.commit()
    
    return ChatResponse(
        message=ai_response,
        conversation_id=conversation.id
    )