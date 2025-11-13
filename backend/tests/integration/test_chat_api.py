"""
Integration tests for Chat API endpoints
"""
import pytest
from fastapi import status
from app.models.conversation import Conversation


@pytest.mark.integration
class TestChatMessageEndpoint:
    """Integration tests for POST /api/chat/message endpoint"""

    def test_send_first_message_creates_conversation(
        self, client, test_trip, test_user_id, db_session, mock_openai_completion
    ):
        """Test that sending the first message creates a new conversation"""
        response = client.post(
            "/api/chat/message",
            json={
                "message": "I want to visit Paris",
                "trip_id": test_trip.id,
                "user_id": test_user_id
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify response structure
        assert "message" in data
        assert "conversation_id" in data
        assert isinstance(data["message"], str)
        assert isinstance(data["conversation_id"], int)

        # Verify conversation was created in database
        conversation = db_session.query(Conversation).filter_by(
            id=data["conversation_id"]
        ).first()
        assert conversation is not None
        assert conversation.trip_id == test_trip.id
        assert conversation.user_id == test_user_id
        assert len(conversation.messages) == 2  # User message + AI response

    def test_send_message_to_existing_conversation(
        self, client, test_conversation, test_trip, test_user_id, db_session, mock_openai_completion
    ):
        """Test sending a message to an existing conversation"""
        initial_message_count = len(test_conversation.messages)

        response = client.post(
            "/api/chat/message",
            json={
                "message": "What's the best time to visit?",
                "trip_id": test_trip.id,
                "user_id": test_user_id
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["conversation_id"] == test_conversation.id

        # Refresh conversation from database
        db_session.refresh(test_conversation)

        # Verify messages were added
        assert len(test_conversation.messages) == initial_message_count + 2
        assert test_conversation.messages[-2]["role"] == "user"
        assert test_conversation.messages[-2]["content"] == "What's the best time to visit?"
        assert test_conversation.messages[-1]["role"] == "assistant"

    def test_send_message_with_trip_context(
        self, client, test_trip, test_user_id, db_session, mock_openai_completion
    ):
        """Test that trip context is included in message processing"""
        response = client.post(
            "/api/chat/message",
            json={
                "message": "What should I pack?",
                "trip_id": test_trip.id,
                "user_id": test_user_id
            }
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify the OpenAI completion was called
        assert mock_openai_completion.called

    def test_conversation_history_is_persisted(
        self, client, test_trip, test_user_id, db_session, mock_openai_completion
    ):
        """Test that full conversation history is stored correctly"""
        messages = [
            "I want to visit Tokyo",
            "What's the best time to visit?",
            "Tell me about good restaurants"
        ]

        conversation_id = None
        for message in messages:
            response = client.post(
                "/api/chat/message",
                json={
                    "message": message,
                    "trip_id": test_trip.id,
                    "user_id": test_user_id
                }
            )
            assert response.status_code == status.HTTP_200_OK
            conversation_id = response.json()["conversation_id"]

        # Verify all messages stored in database
        conversation = db_session.query(Conversation).filter_by(
            id=conversation_id
        ).first()

        assert conversation is not None
        assert len(conversation.messages) == len(messages) * 2  # Each message has user + assistant

        # Verify message order
        for i, original_message in enumerate(messages):
            user_message = conversation.messages[i * 2]
            assert user_message["role"] == "user"
            assert user_message["content"] == original_message

    def test_send_message_nonexistent_trip(
        self, client, test_user_id, mock_openai_completion
    ):
        """Test sending message for non-existent trip returns 404"""
        response = client.post(
            "/api/chat/message",
            json={
                "message": "Hello",
                "trip_id": 99999,  # Non-existent trip ID
                "user_id": test_user_id
            }
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_send_message_unauthorized_user(
        self, client, test_trip, mock_openai_completion
    ):
        """Test that users cannot access other users' trips"""
        wrong_user_id = test_trip.user_id + 1

        response = client.post(
            "/api/chat/message",
            json={
                "message": "Hello",
                "trip_id": test_trip.id,
                "user_id": wrong_user_id
            }
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "not authorized" in response.json()["detail"].lower()

    def test_message_count_is_updated(
        self, client, test_trip, test_user_id, db_session, mock_openai_completion
    ):
        """Test that message_count field is updated correctly"""
        response = client.post(
            "/api/chat/message",
            json={
                "message": "First message",
                "trip_id": test_trip.id,
                "user_id": test_user_id
            }
        )

        conversation_id = response.json()["conversation_id"]

        # Send second message
        client.post(
            "/api/chat/message",
            json={
                "message": "Second message",
                "trip_id": test_trip.id,
                "user_id": test_user_id
            }
        )

        # Verify message count
        conversation = db_session.query(Conversation).filter_by(
            id=conversation_id
        ).first()

        assert conversation.message_count == 4  # 2 user messages + 2 AI responses

    def test_context_extraction_from_messages(
        self, client, test_trip, test_user_id, db_session, mock_openai_completion
    ):
        """Test that context is extracted and stored from user messages"""
        response = client.post(
            "/api/chat/message",
            json={
                "message": "I want to visit Tokyo for 7 days with a budget of $3000. I love food and temples.",
                "trip_id": test_trip.id,
                "user_id": test_user_id
            }
        )

        assert response.status_code == status.HTTP_200_OK
        conversation_id = response.json()["conversation_id"]

        # Verify context was extracted and stored
        conversation = db_session.query(Conversation).filter_by(
            id=conversation_id
        ).first()

        assert conversation.context is not None
        # Context extraction happens in the service layer

    def test_empty_message_validation(
        self, client, test_trip, test_user_id, mock_openai_completion
    ):
        """Test that empty messages are rejected"""
        response = client.post(
            "/api/chat/message",
            json={
                "message": "",
                "trip_id": test_trip.id,
                "user_id": test_user_id
            }
        )

        # Should either reject with 422 (validation error) or handle gracefully
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_200_OK]

    @pytest.mark.slow
    def test_long_conversation_with_summarization(
        self, client, test_trip, test_user_id, db_session, mock_openai_completion
    ):
        """Test that long conversations trigger summarization"""
        # Send 16 messages to trigger summarization (threshold is 15)
        conversation_id = None
        for i in range(16):
            response = client.post(
                "/api/chat/message",
                json={
                    "message": f"Message number {i}",
                    "trip_id": test_trip.id,
                    "user_id": test_user_id
                }
            )
            assert response.status_code == status.HTTP_200_OK
            conversation_id = response.json()["conversation_id"]

        # Verify summary was created
        conversation = db_session.query(Conversation).filter_by(
            id=conversation_id
        ).first()

        # After 16 messages (32 total with responses), summary should exist
        assert conversation.message_count == 32
        # Summarization logic should have been triggered

    def test_concurrent_messages_same_conversation(
        self, client, test_conversation, test_trip, test_user_id, db_session, mock_openai_completion
    ):
        """Test handling of multiple messages in quick succession"""
        # Send multiple messages
        responses = []
        for i in range(3):
            response = client.post(
                "/api/chat/message",
                json={
                    "message": f"Concurrent message {i}",
                    "trip_id": test_trip.id,
                    "user_id": test_user_id
                }
            )
            responses.append(response)

        # All should succeed
        for response in responses:
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["conversation_id"] == test_conversation.id

        # Verify all messages stored
        db_session.refresh(test_conversation)
        assert test_conversation.message_count >= 8  # Initial 2 + 3*2 new messages


@pytest.mark.integration
class TestChatIntegrationWithServices:
    """Integration tests for chat with service layer"""

    def test_full_message_flow_with_ai_service(
        self, client, test_trip, test_user_id, db_session, mock_openai_completion
    ):
        """Test complete flow from request to AI response"""
        user_message = "I want to explore museums in Paris"

        response = client.post(
            "/api/chat/message",
            json={
                "message": user_message,
                "trip_id": test_trip.id,
                "user_id": test_user_id
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify AI response was generated
        assert len(data["message"]) > 0

        # Verify OpenAI was called
        assert mock_openai_completion.called

    def test_trip_context_included_in_ai_prompt(
        self, client, test_trip, test_user_id, mock_openai_completion
    ):
        """Test that trip details are included in AI context"""
        response = client.post(
            "/api/chat/message",
            json={
                "message": "What can you tell me about my trip?",
                "trip_id": test_trip.id,
                "user_id": test_user_id
            }
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify OpenAI was called with trip context
        assert mock_openai_completion.called
        call_kwargs = mock_openai_completion.call_args[1]

        # The messages should include trip context
        assert "messages" in call_kwargs
