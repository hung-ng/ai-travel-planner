"""
Tests for database models
"""
import pytest
from datetime import datetime
from app.models.trip import Trip
from app.models.conversation import Conversation


@pytest.mark.unit
@pytest.mark.database
class TestTripModel:
    """Tests for Trip model"""
    
    def test_create_trip(self, test_db_session, sample_trip_data):
        """Test creating a trip"""
        trip = Trip(**sample_trip_data)
        test_db_session.add(trip)
        test_db_session.commit()
        test_db_session.refresh(trip)
        
        assert trip.id is not None
        assert trip.user_id == sample_trip_data["user_id"]
        assert trip.destination == sample_trip_data["destination"]
        assert trip.budget == sample_trip_data["budget"]
        assert trip.status == "gathering"
        assert trip.created_at is not None
    
    def test_trip_status_default(self, test_db_session):
        """Test default trip status"""
        trip = Trip(
            user_id=1,
            destination="Tokyo",
            start_date=datetime.now(),
            end_date=datetime.now()
        )
        test_db_session.add(trip)
        test_db_session.commit()
        
        assert trip.status == "gathering"
    
    def test_trip_preferences_json(self, test_db_session):
        """Test JSON preferences field"""
        preferences = {
            "interests": ["food", "history"],
            "travel_style": "moderate",
            "dietary_restrictions": ["vegetarian"]
        }
        
        trip = Trip(
            user_id=1,
            destination="Rome",
            start_date=datetime.now(),
            end_date=datetime.now(),
            preferences=preferences
        )
        test_db_session.add(trip)
        test_db_session.commit()
        test_db_session.refresh(trip)
        
        assert trip.preferences == preferences
        assert isinstance(trip.preferences, dict)
    
    def test_trip_itinerary_json(self, test_db_session, sample_trip):
        """Test JSON itinerary field"""
        itinerary = {
            "day_1": ["Eiffel Tower", "Louvre"],
            "day_2": ["Notre-Dame", "Montmartre"]
        }
        
        sample_trip.itinerary = itinerary
        sample_trip.status = "GATHERING"
        test_db_session.commit()
        test_db_session.refresh(sample_trip)
        
        assert sample_trip.itinerary == itinerary
        assert sample_trip.status == "gathering"
        
    def test_trip_null_budget(self, test_db_session):
        """Test trip with null budget"""
        trip = Trip(
            user_id=1,
            destination="Bangkok",
            start_date=datetime.now(),
            end_date=datetime.now(),
            budget=None
        )
        test_db_session.add(trip)
        test_db_session.commit()
        
        assert trip.budget is None
    
    def test_query_trips_by_user(self, test_db_session):
        """Test querying trips by user"""
        # Create multiple trips
        trip1 = Trip(user_id=1, destination="Paris", start_date=datetime.now(), end_date=datetime.now())
        trip2 = Trip(user_id=1, destination="London", start_date=datetime.now(), end_date=datetime.now())
        trip3 = Trip(user_id=2, destination="Tokyo", start_date=datetime.now(), end_date=datetime.now())
        
        test_db_session.add_all([trip1, trip2, trip3])
        test_db_session.commit()
        
        user1_trips = test_db_session.query(Trip).filter(Trip.user_id == 1).all()
        
        assert len(user1_trips) == 2
        assert all(trip.user_id == 1 for trip in user1_trips)


@pytest.mark.unit
@pytest.mark.database
class TestConversationModel:
    """Tests for Conversation model"""
    
    def test_create_conversation(self, test_db_session, sample_trip):
        """Test creating a conversation"""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        conversation = Conversation(
            trip_id=sample_trip.id,
            user_id=1,  # FIXED: Added user_id
            messages=messages
        )
        test_db_session.add(conversation)
        test_db_session.commit()
        test_db_session.refresh(conversation)
        
        assert conversation.id is not None
        assert conversation.trip_id == sample_trip.id
        assert len(conversation.messages) == 2
        assert conversation.created_at is not None


    def test_empty_conversation(self, test_db_session, sample_trip):
        """Test conversation with empty messages"""
        conversation = Conversation(
            trip_id=sample_trip.id,
            user_id=1,
            messages=[],
            context={},
            summary=None,
            message_count=0,
            last_summarized_index=0
        )
        test_db_session.add(conversation)
        test_db_session.commit()
        test_db_session.refresh(conversation)

        assert conversation.id is not None
        assert conversation.messages == []
        assert conversation.message_count == 0
    
    def test_conversation_messages_json(self, test_db_session, sample_conversation):
        """Test JSON messages field"""
        assert isinstance(sample_conversation.messages, list)
        assert all(isinstance(msg, dict) for msg in sample_conversation.messages)
        assert all('role' in msg and 'content' in msg for msg in sample_conversation.messages)
    
    def test_add_message_to_conversation(self, test_db_session, sample_conversation):
        """Test adding messages to existing conversation"""
        initial_count = len(sample_conversation.messages)
        new_message = {"role": "user", "content": "Tell me more"}

        # Append to messages list
        sample_conversation.messages = sample_conversation.messages + [new_message]
        sample_conversation.message_count = len(sample_conversation.messages)
        test_db_session.commit()
        test_db_session.refresh(sample_conversation)

        assert len(sample_conversation.messages) == initial_count + 1
        assert sample_conversation.messages[-1] == new_message
        assert sample_conversation.message_count == initial_count + 1
    
    def test_conversation_trip_relationship(self, test_db_session, sample_trip, sample_conversation):
        """Test relationship between conversation and trip"""
        # Query conversation through trip
        trip = test_db_session.query(Trip).filter(Trip.id == sample_trip.id).first()
        conversations = test_db_session.query(Conversation).filter(
            Conversation.trip_id == trip.id
        ).all()
        
        assert len(conversations) == 1
        assert conversations[0].id == sample_conversation.id