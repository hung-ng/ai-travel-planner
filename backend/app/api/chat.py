from fastapi import APIRouter, Depends, WebSocket
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.conversation import conversation_service
from app.models.conversation import Conversation
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest, db: Session = Depends(get_db)):
    """Send a chat message"""
    
    # Get conversation
    conversation = db.query(Conversation).filter(
        Conversation.trip_id == request.trip_id
    ).first()
    
    if not conversation:
        conversation = Conversation(
            trip_id=request.trip_id,
            user_id=request.user_id,
            messages=[]
        )
        db.add(conversation)
    
    # Process message
    response = await conversation_service.process_message(
        user_message=request.message,
        conversation_history=conversation.messages,
        trip_context=conversation.context
    )
    
    # Update conversation
    conversation.messages.append({"role": "user", "content": request.message})
    conversation.messages.append({"role": "assistant", "content": response})
    db.commit()
    
    return ChatResponse(message=response, conversation_id=conversation.id)

@router.websocket("/ws/{trip_id}")
async def websocket_endpoint(websocket: WebSocket, trip_id: int):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            # Process and send response
            response = await conversation_service.process_message(
                user_message=data,
                conversation_history=[],
                trip_context={}
            )
            await websocket.send_text(response)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()