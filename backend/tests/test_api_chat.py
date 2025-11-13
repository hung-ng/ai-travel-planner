"""
Tests for Chat API endpoints
"""
import pytest


@pytest.mark.api
class TestChatAPI:
    """Tests for /api/chat endpoints"""
    
    def test_send_message(self, client, sample_trip, mock_ai_service, mock_rag_service):
        """Test POST /api/chat/message"""
        message_data = {
            "message": "I want to visit Paris for 5 days",
            "trip_id": sample_trip.id,
            "user_id": 1
        }
        
        response = client.post("/api/chat/message", json=message_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "conversation_id" in data
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0
    
    def test_send_message_creates_conversation(self, client, sample_trip, test_db_session,
                                               mock_ai_service, mock_rag_service):
        """Test that sending message creates conversation"""
        from app.models.conversation import Conversation
        
        # Verify no conversations exist
        conv_count_before = test_db_session.query(Conversation).count()
        assert conv_count_before == 0
        
        message_data = {
            "message": "Hello",
            "trip_id": sample_trip.id,
            "user_id": 1
        }
        
        response = client.post("/api/chat/message", json=message_data)
        assert response.status_code == 200
        
        # Verify conversation was created
        conv_count_after = test_db_session.query(Conversation).count()
        assert conv_count_after == 1
    
    def test_send_message_to_existing_conversation(self, client, sample_trip, 
                                                    sample_conversation, test_db_session,
                                                    mock_ai_service, mock_rag_service):
        """Test continuing existing conversation"""
        initial_message_count = len(sample_conversation.messages)
        
        message_data = {
            "message": "Tell me more about museums",
            "trip_id": sample_trip.id,
            "user_id": 1
        }
        
        response = client.post("/api/chat/message", json=message_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == sample_conversation.id
        
        # Refresh conversation
        test_db_session.refresh(sample_conversation)
        
        # Should have 2 new messages (user + assistant)
        assert len(sample_conversation.messages) == initial_message_count + 2
    
    def test_send_message_invalid_trip(self, client, mock_ai_service, mock_rag_service):
        """Test sending message to non-existent trip"""
        message_data = {
            "message": "Hello",
            "trip_id": 99999,
            "user_id": 1
        }
        
        response = client.post("/api/chat/message", json=message_data)
        
        assert response.status_code == 404
        assert "trip" in response.json()["detail"].lower()
    
    def test_send_empty_message(self, client, sample_trip, mock_ai_service, mock_rag_service):
        """Test sending empty message"""
        message_data = {
            "message": "",
            "trip_id": sample_trip.id,
            "user_id": 1
        }
        
        response = client.post("/api/chat/message", json=message_data)
        
        # Should handle gracefully (either 400 or process it)
        assert response.status_code in [200, 400, 422]
    
    @pytest.mark.skip(reason="GET /api/chat/history endpoint not implemented yet")
    def test_get_conversation_history(self, client, sample_conversation):
        """Test GET /api/chat/history/{conversation_id}"""
        # This endpoint doesn't exist yet, so test is skipped
        # When implemented, it should return:
        # {
        #     "conversation_id": int,
        #     "messages": List[Dict],
        #     "context": Dict,
        #     "summary": Optional[str]
        # }
        pass
    
    def test_get_nonexistent_conversation(self, client):
        """Test getting non-existent conversation"""
        response = client.get("/api/chat/history/99999")
        
        assert response.status_code == 404


@pytest.mark.api
@pytest.mark.slow
class TestChatAPIIntegration:
    """Integration tests for chat API (slower, more realistic)"""
    
    @pytest.mark.integration
    def test_full_conversation_flow(self, client, sample_trip, test_db_session, mock_ai_service, mock_rag_service):
        """Test a complete conversation flow"""
        from app.models.conversation import Conversation

        # First message
        response1 = client.post("/api/chat/message", json={
            "message": "I want to visit Paris",
            "trip_id": sample_trip.id,
            "user_id": 1
        })
        assert response1.status_code == 200
        data1 = response1.json()
        conv_id = data1["conversation_id"]
        assert "message" in data1
        assert isinstance(conv_id, int)

        # Second message (same conversation)
        response2 = client.post("/api/chat/message", json={
            "message": "What's the best time to visit?",
            "trip_id": sample_trip.id,
            "user_id": 1
        })
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["conversation_id"] == conv_id  # Same conversation
        assert "message" in data2

        # Third message
        response3 = client.post("/api/chat/message", json={
            "message": "Tell me about museums",
            "trip_id": sample_trip.id,
            "user_id": 1
        })
        assert response3.status_code == 200
        data3 = response3.json()
        assert data3["conversation_id"] == conv_id  # Still same conversation

        # Verify conversation in database has all messages
        conversation = test_db_session.query(Conversation).filter(
            Conversation.id == conv_id
        ).first()
        assert conversation is not None
        # Should have 6 messages (3 user + 3 assistant)
        assert len(conversation.messages) == 6
        assert conversation.messages[0]["role"] == "user"
        assert conversation.messages[0]["content"] == "I want to visit Paris"
        assert conversation.messages[1]["role"] == "assistant"
        assert conversation.messages[5]["role"] == "assistant"