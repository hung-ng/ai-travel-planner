"""
Tests for AI Service
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.unit
@pytest.mark.service
class TestChatService:
    """Tests for ChatService"""

    @pytest.mark.asyncio
    async def test_chat_completion(self, mock_openai_response):
        """Test chat completion"""
        with patch('openai.OpenAI') as mock_openai:
            # Setup mock
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_openai_response
            mock_openai.return_value = mock_client

            from app.services.ai.chat import ChatService
            service = ChatService()

            messages = [
                {"role": "user", "content": "Hello"}
            ]

            response = await service.get_completion(messages)

            assert isinstance(response, str)
            assert len(response) > 0
            assert response == "This is a test response from the AI assistant."

    @pytest.mark.asyncio
    async def test_chat_completion_with_temperature(self, mock_openai_response):
        """Test chat completion with custom temperature"""
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_openai_response
            mock_openai.return_value = mock_client

            from app.services.ai.chat import ChatService
            service = ChatService()

            messages = [{"role": "user", "content": "Be creative"}]

            # Test with custom temperature
            response = await service.get_completion(messages, temperature=0.9, max_tokens=100)

            assert isinstance(response, str)
            assert len(response) > 0

            # Verify temperature was passed to OpenAI
            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]['temperature'] == 0.9
            assert call_args[1]['max_tokens'] == 100

    @pytest.mark.asyncio
    async def test_chat_completion_error_handling(self):
        """Test error handling in chat completion"""
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai.return_value = mock_client

            from app.services.ai.chat import ChatService
            service = ChatService()

            messages = [{"role": "user", "content": "Hello"}]

            # Should raise exception
            with pytest.raises(Exception) as exc_info:
                await service.get_completion(messages)

            assert "API Error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_empty_messages(self, mock_openai_response):
        """Test with empty messages list"""
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_openai_response
            mock_openai.return_value = mock_client

            from app.services.ai.chat import ChatService
            service = ChatService()

            # Should handle empty messages (OpenAI will handle validation)
            response = await service.get_completion([])

            assert isinstance(response, str)


@pytest.mark.unit
@pytest.mark.service
class TestEmbeddingService:
    """Tests for EmbeddingService"""

    @pytest.mark.asyncio
    async def test_get_embedding(self, mock_embedding_response):
        """Test getting embeddings"""
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_client.embeddings.create.return_value = mock_embedding_response
            mock_openai.return_value = mock_client

            from app.services.ai.embeddings import EmbeddingService
            service = EmbeddingService()

            text = "Paris is a beautiful city"
            embedding = await service.get_embedding(text)

            assert isinstance(embedding, list)
            assert len(embedding) == 1536  # text-embedding-3-small dimension
            assert all(isinstance(x, float) for x in embedding)

    @pytest.mark.asyncio
    async def test_get_embeddings_batch(self, mock_embedding_response):
        """Test batch embedding generation"""
        with patch('openai.OpenAI') as mock_openai:
            # Setup mock for batch
            mock_batch_response = MagicMock()
            mock_batch_response.data = [
                MagicMock(embedding=[0.1] * 1536),
                MagicMock(embedding=[0.2] * 1536),
                MagicMock(embedding=[0.3] * 1536)
            ]

            mock_client = MagicMock()
            mock_client.embeddings.create.return_value = mock_batch_response
            mock_openai.return_value = mock_client

            from app.services.ai.embeddings import EmbeddingService
            service = EmbeddingService()

            texts = ["Paris", "London", "Tokyo"]
            embeddings = await service.get_embeddings_batch(texts)

            assert isinstance(embeddings, list)
            assert len(embeddings) == 3
            assert all(len(emb) == 1536 for emb in embeddings)

    @pytest.mark.asyncio
    async def test_embedding_error_handling(self):
        """Test error handling in embedding generation"""
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_client.embeddings.create.side_effect = Exception("Embedding API Error")
            mock_openai.return_value = mock_openai

            from app.services.ai.embeddings import EmbeddingService
            service = EmbeddingService()

            # Should raise exception
            with pytest.raises(Exception) as exc_info:
                await service.get_embedding("test")

            assert "Embedding API Error" in str(exc_info.value)
