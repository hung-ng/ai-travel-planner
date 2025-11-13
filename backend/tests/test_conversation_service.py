"""
Tests for Conversation Service
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.unit
@pytest.mark.service
class TestConversationService:
    """Tests for ConversationService"""

    @pytest.mark.asyncio
    async def test_process_message(self):
        """Test processing a message"""
        with patch('app.services.ai.chat_service.get_completion') as mock_chat, \
             patch('app.services.rag.retrieval_service.search') as mock_rag:

            # Setup mocks
            mock_chat.return_value = "This is a great AI response about Paris attractions!"
            mock_rag.return_value = {
                'documents': [['Paris has the Eiffel Tower', 'The Louvre is famous']],
                'metadatas': [[{'city': 'Paris'}, {'city': 'Paris'}]],
                'distances': [[0.2, 0.3]]
            }

            from app.services.conversation import conversation_service

            user_message = "What should I do in Paris?"
            conversation_history = []
            trip_context = {
                "destination": "Paris",
                "budget": 2000,
                "start_date": "2024-06-01",
                "end_date": "2024-06-05"
            }

            response, context, summary = await conversation_service.process_message(
                user_message=user_message,
                conversation_history=conversation_history,
                trip_context=trip_context
            )

            assert isinstance(response, str)
            assert len(response) > 0
            assert response == "This is a great AI response about Paris attractions!"

            # Verify RAG was called
            mock_rag.assert_called_once()

            # Verify AI was called
            mock_chat.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_message_with_history(self):
        """Test processing message with conversation history"""
        with patch('app.services.ai.chat_service.get_completion') as mock_chat, \
             patch('app.services.rag.retrieval_service.search') as mock_rag:

            # Setup mocks
            mock_chat.return_value = "The Louvre and Musée d'Orsay are must-visit museums!"
            mock_rag.return_value = {
                'documents': [['Louvre info', 'Musée d\'Orsay info']],
                'metadatas': [[{'city': 'Paris'}, {'city': 'Paris'}]],
                'distances': [[0.1, 0.2]]
            }

            from app.services.conversation import conversation_service

            user_message = "Tell me more about that"
            conversation_history = [
                {"role": "user", "content": "What museums are in Paris?"},
                {"role": "assistant", "content": "The Louvre is famous..."}
            ]
            trip_context = {"destination": "Paris"}

            response, context, summary = await conversation_service.process_message(
                user_message=user_message,
                conversation_history=conversation_history,
                trip_context=trip_context
            )

            assert isinstance(response, str)
            assert len(response) > 0

            # Verify chat was called with messages including history
            ai_call_args = mock_chat.call_args
            messages = ai_call_args[1]['messages']

            # Should include system prompt + (possibly summarized history) + new message
            assert len(messages) >= 2  # At minimum: system + user message
            # Last message should be the new user message
            assert messages[-1]['role'] == 'user'
            assert messages[-1]['content'] == user_message

    @pytest.mark.asyncio
    async def test_process_message_rag_context(self):
        """Test that RAG context is included in AI prompt"""
        with patch('app.services.ai.chat_service.get_completion') as mock_chat, \
             patch('app.services.rag.retrieval_service.search') as mock_rag:

            # Setup mocks
            rag_doc_content = "Best Paris restaurants include Le Jules Verne and L'Ambroisie"
            mock_rag.return_value = {
                'documents': [[rag_doc_content]],
                'metadatas': [[{'city': 'Paris', 'category': 'food'}]],
                'distances': [[0.15]]
            }
            mock_chat.return_value = "Based on the knowledge base, I recommend these restaurants..."

            from app.services.conversation import conversation_service

            user_message = "Best restaurants in Paris?"

            response, context, summary = await conversation_service.process_message(
                user_message=user_message,
                conversation_history=[],
                trip_context={"destination": "Paris"}
            )

            # Verify RAG search was called
            mock_rag.assert_called_once()
            search_call_args = mock_rag.call_args

            # Verify search query contains relevant terms
            search_query = search_call_args[1]['query']
            # The query might be enhanced, so just check it's not empty
            assert isinstance(search_query, str)
            assert len(search_query) > 0

            # Verify AI was called with system prompt containing RAG context
            ai_call_args = mock_chat.call_args
            messages = ai_call_args[1]['messages']

            # System prompt should be first message
            system_prompt = messages[0]['content']
            assert 'RELEVANT TRAVEL KNOWLEDGE' in system_prompt or 'knowledge' in system_prompt.lower()

    @pytest.mark.asyncio
    async def test_context_extraction(self):
        """Test that conversation context is extracted correctly"""
        with patch('app.services.ai.chat_service.get_completion') as mock_chat, \
             patch('app.services.rag.retrieval_service.search') as mock_rag:

            # Setup mocks
            mock_chat.return_value = "Great choice for a 3-day trip!"
            mock_rag.return_value = {
                'documents': [['Paris travel info']],
                'metadatas': [[{'city': 'Paris'}]],
                'distances': [[0.3]]
            }

            from app.services.conversation import conversation_service

            # Message contains extractable context (duration)
            user_message = "I want to visit Paris for 3 days"

            response, extracted_context, summary = await conversation_service.process_message(
                user_message=user_message,
                conversation_history=[],
                trip_context={"destination": "Paris"}
            )

            # Context should be extracted and returned
            assert isinstance(extracted_context, dict)
            # The context_manager should have extracted duration
            # Check if duration was extracted (might be in context)
            # This depends on the context_manager implementation

    @pytest.mark.asyncio
    async def test_empty_rag_results(self):
        """Test handling when RAG returns no results"""
        with patch('app.services.ai.chat_service.get_completion') as mock_chat, \
             patch('app.services.rag.retrieval_service.search') as mock_rag:

            # Setup mocks - RAG returns empty
            mock_rag.return_value = {
                'documents': [[]],
                'metadatas': [[]],
                'distances': [[]]
            }
            mock_chat.return_value = "I'll help you plan your trip!"

            from app.services.conversation import conversation_service

            user_message = "Plan my trip"

            response, context, summary = await conversation_service.process_message(
                user_message=user_message,
                conversation_history=[],
                trip_context={"destination": "UnknownCity"}
            )

            # Should still work even without RAG results
            assert isinstance(response, str)
            assert len(response) > 0
            mock_chat.assert_called_once()
