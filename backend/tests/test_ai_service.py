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
    async def test_chat_completion(self):
        """Test chat completion"""
        # Create fresh mock to avoid autouse fixture interference
        with patch('app.services.ai.chat.OpenAI') as mock_openai_class:
            # Setup mock response
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "This is a test response from the AI assistant."

            # Setup mock client
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client

            from app.services.ai.chat import ChatService
            service = ChatService()

            messages = [{"role": "user", "content": "Hello"}]
            response = await service.get_completion(messages)

            assert isinstance(response, str)
            assert len(response) > 0
            assert response == "This is a test response from the AI assistant."

    @pytest.mark.asyncio
    async def test_chat_completion_with_temperature(self):
        """Test chat completion with custom temperature"""
        with patch('app.services.ai.chat.OpenAI') as mock_openai_class:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Creative response!"

            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client

            from app.services.ai.chat import ChatService
            service = ChatService()

            messages = [{"role": "user", "content": "Be creative"}]

            # Test with custom temperature
            response = await service.get_completion(messages, temperature=0.9, max_tokens=100)

            assert isinstance(response, str)
            assert len(response) > 0

            # Verify temperature was passed to OpenAI
            mock_client.chat.completions.create.assert_called_once()
            call_kwargs = mock_client.chat.completions.create.call_args.kwargs
            assert call_kwargs['temperature'] == 0.9
            assert call_kwargs['max_tokens'] == 100

    @pytest.mark.asyncio
    async def test_chat_completion_error_handling(self):
        """Test error handling in chat completion"""
        with patch('app.services.ai.chat.OpenAI') as mock_openai_class:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai_class.return_value = mock_client

            from app.services.ai.chat import ChatService
            service = ChatService()

            messages = [{"role": "user", "content": "Hello"}]

            # Should raise exception (service doesn't catch it)
            with pytest.raises(Exception) as exc_info:
                await service.get_completion(messages)

            assert "API Error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_empty_messages(self):
        """Test with empty messages list - OpenAI will validate"""
        with patch('app.services.ai.chat.OpenAI') as mock_openai_class:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Response"

            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client

            from app.services.ai.chat import ChatService
            service = ChatService()

            # Service will pass empty list to OpenAI (which would reject it in real use)
            response = await service.get_completion([])

            assert isinstance(response, str)


@pytest.mark.unit
@pytest.mark.service
class TestEmbeddingService:
    """Tests for EmbeddingService"""

    @pytest.mark.asyncio
    async def test_get_embedding(self):
        """Test getting embeddings"""
        with patch('app.services.ai.embeddings.OpenAI') as mock_openai_class:
            # Setup mock embedding response
            mock_response = MagicMock()
            mock_embedding_data = MagicMock()
            mock_embedding_data.embedding = [0.1] * 1536
            mock_response.data = [mock_embedding_data]

            mock_client = MagicMock()
            mock_client.embeddings.create.return_value = mock_response
            mock_openai_class.return_value = mock_client

            from app.services.ai.embeddings import EmbeddingService
            service = EmbeddingService()

            text = "Paris is a beautiful city"
            embedding = await service.get_embedding(text)

            assert isinstance(embedding, list)
            assert len(embedding) == 1536  # text-embedding-3-small dimension
            # Check first few values are floats
            assert isinstance(embedding[0], float)
            assert embedding[0] == 0.1

    @pytest.mark.asyncio
    async def test_get_embeddings_batch(self):
        """Test batch embedding generation"""
        with patch('app.services.ai.embeddings.OpenAI') as mock_openai_class:
            # Setup mock for batch
            mock_response = MagicMock()
            mock_response.data = [
                MagicMock(embedding=[0.1] * 1536),
                MagicMock(embedding=[0.2] * 1536),
                MagicMock(embedding=[0.3] * 1536)
            ]

            mock_client = MagicMock()
            mock_client.embeddings.create.return_value = mock_response
            mock_openai_class.return_value = mock_client

            from app.services.ai.embeddings import EmbeddingService
            service = EmbeddingService()

            texts = ["Paris", "London", "Tokyo"]
            embeddings = await service.get_embeddings_batch(texts)

            assert isinstance(embeddings, list)
            assert len(embeddings) == 3
            assert all(len(emb) == 1536 for emb in embeddings)
            assert embeddings[0][0] == 0.1
            assert embeddings[1][0] == 0.2
            assert embeddings[2][0] == 0.3

    @pytest.mark.asyncio
    async def test_embedding_error_handling(self):
        """Test error handling in embedding generation"""
        with patch('app.services.ai.embeddings.OpenAI') as mock_openai_class:
            mock_client = MagicMock()
            mock_client.embeddings.create.side_effect = Exception("Embedding API Error")
            mock_openai_class.return_value = mock_client

            from app.services.ai.embeddings import EmbeddingService
            service = EmbeddingService()

            # Should raise exception
            with pytest.raises(Exception) as exc_info:
                await service.get_embedding("test")

            assert "Embedding API Error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_embedding_dimension_validation(self):
        """Test that embedding dimension is validated"""
        with patch('app.services.ai.embeddings.OpenAI') as mock_openai_class:
            # Return wrong dimension
            mock_response = MagicMock()
            mock_embedding_data = MagicMock()
            mock_embedding_data.embedding = [0.1] * 512  # Wrong dimension!
            mock_response.data = [mock_embedding_data]

            mock_client = MagicMock()
            mock_client.embeddings.create.return_value = mock_response
            mock_openai_class.return_value = mock_client

            from app.services.ai.embeddings import EmbeddingService
            service = EmbeddingService()

            # Should still return the embedding (service logs warning but doesn't fail)
            embedding = await service.get_embedding("test")

            # Service returns what OpenAI gave, even if wrong dimension
            assert len(embedding) == 512
