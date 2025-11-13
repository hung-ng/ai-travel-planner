"""
End-to-end integration tests
"""
import pytest
from datetime import datetime, timedelta


@pytest.mark.integration
@pytest.mark.slow
class TestFullTripPlanningFlow:
    """Test complete trip planning flow"""
    
    def test_complete_trip_planning(self, client, test_db_session, mock_ai_service, mock_rag_service):
        """Test entire flow: create trip -> chat -> verify data"""
        from app.models.conversation import Conversation

        # Step 1: Create trip
        trip_data = {
            "user_id": 1,
            "destination": "Paris",
            "start_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=35)).isoformat(),
            "budget": 2500,
            "preferences": {"interests": ["art", "food"]}
        }

        create_response = client.post("/api/trips/", json=trip_data)
        assert create_response.status_code == 200
        trip = create_response.json()
        trip_id = trip["id"]
        assert trip["destination"] == "Paris"
        assert trip["budget"] == 2500
        assert trip["status"] == "gathering"

        # Step 2: Start conversation
        msg1 = client.post("/api/chat/message", json={
            "message": "I want to visit Paris for 5 days",
            "trip_id": trip_id,
            "user_id": 1
        })
        assert msg1.status_code == 200
        data1 = msg1.json()
        conv_id = data1["conversation_id"]
        assert "message" in data1
        assert isinstance(data1["message"], str)

        # Step 3: Continue conversation
        msg2 = client.post("/api/chat/message", json={
            "message": "I love art and food",
            "trip_id": trip_id,
            "user_id": 1
        })
        assert msg2.status_code == 200
        data2 = msg2.json()
        assert data2["conversation_id"] == conv_id  # Same conversation
        assert "message" in data2

        # Step 4: Another message
        msg3 = client.post("/api/chat/message", json={
            "message": "What museums should I visit?",
            "trip_id": trip_id,
            "user_id": 1
        })
        assert msg3.status_code == 200
        data3 = msg3.json()
        assert data3["conversation_id"] == conv_id

        # Step 5: Verify conversation in database
        conversation = test_db_session.query(Conversation).filter(
            Conversation.id == conv_id
        ).first()
        assert conversation is not None
        assert len(conversation.messages) == 6  # 3 user + 3 assistant
        assert conversation.trip_id == trip_id

        # Step 6: Get trip details
        trip_details = client.get(f"/api/trips/{trip_id}")
        assert trip_details.status_code == 200
        trip_data_retrieved = trip_details.json()
        assert trip_data_retrieved["id"] == trip_id
        assert trip_data_retrieved["destination"] == "Paris"
        assert trip_data_retrieved["budget"] == 2500
    
    def test_multiple_trips_same_user(self, client, mock_ai_service, mock_rag_service):
        """Test user with multiple trips"""
        user_id = 1
        
        # Create multiple trips
        paris_trip = client.post("/api/trips/", json={
            "user_id": user_id,
            "destination": "Paris",
            "start_date": datetime.now().isoformat(),
            "end_date": datetime.now().isoformat()
        })
        
        london_trip = client.post("/api/trips/", json={
            "user_id": user_id,
            "destination": "London",
            "start_date": datetime.now().isoformat(),
            "end_date": datetime.now().isoformat()
        })
        
        assert paris_trip.status_code == 200
        assert london_trip.status_code == 200
        
        # Get all trips
        all_trips = client.get("/api/trips/")
        assert all_trips.status_code == 200
        trips_list = all_trips.json()
        assert len(trips_list) >= 2
        
        # Chat on different trips
        paris_msg = client.post("/api/chat/message", json={
            "message": "Paris itinerary",
            "trip_id": paris_trip.json()["id"],
            "user_id": user_id
        })
        
        london_msg = client.post("/api/chat/message", json={
            "message": "London itinerary",
            "trip_id": london_trip.json()["id"],
            "user_id": user_id
        })
        
        assert paris_msg.status_code == 200
        assert london_msg.status_code == 200
        
        # Different conversation IDs
        assert paris_msg.json()["conversation_id"] != london_msg.json()["conversation_id"]


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling across the system"""
    
    def test_chat_with_invalid_trip(self, client, mock_ai_service, mock_rag_service):
        """Test chatting with non-existent trip"""
        response = client.post("/api/chat/message", json={
            "message": "Hello",
            "trip_id": 99999,
            "user_id": 1
        })
        
        assert response.status_code == 404
    
    def test_invalid_data_types(self, client):
        """Test API with invalid data types"""
        invalid_trip = {
            "user_id": "not_a_number",
            "destination": 12345,  # Should be string
            "start_date": "invalid_date"
        }
        
        response = client.post("/api/trips/", json=invalid_trip)
        assert response.status_code == 422