"""
Tests for RAG/Retrieval Service
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock


@pytest.mark.unit
@pytest.mark.service
class TestRetrievalService:
    """Tests for RetrievalService"""

    @pytest.mark.asyncio
    async def test_search(self):
        """Test RAG search"""
        with patch('chromadb.HttpClient') as mock_chroma, \
             patch('app.services.ai.embedding_service.get_embedding') as mock_embedding:

            # Setup embedding mock
            mock_embedding.return_value = [0.1] * 1536

            # Setup ChromaDB mock
            mock_collection = MagicMock()
            mock_collection.query.return_value = {
                'documents': [['Test document about Paris']],
                'metadatas': [[{'city': 'Paris', 'source': 'wikipedia'}]],
                'distances': [[0.3]],  # 0.3 distance = 0.7 similarity
                'ids': [['doc1']]
            }

            mock_client = MagicMock()
            mock_client.get_or_create_collection.return_value = mock_collection
            mock_chroma.return_value = mock_client

            from app.services.rag.retrieval import RetrievalService
            service = RetrievalService(similarity_threshold=0.5)

            results = await service.search("test query", n_results=5)

            assert 'documents' in results
            assert 'metadatas' in results
            assert len(results['documents'][0]) > 0

    @pytest.mark.asyncio
    async def test_add_documents(self):
        """Test adding documents to RAG - using vector_store directly"""
        with patch('chromadb.HttpClient') as mock_chroma:

            # Setup ChromaDB mock
            mock_collection = MagicMock()
            mock_client = MagicMock()
            mock_client.get_or_create_collection.return_value = mock_collection
            mock_client.heartbeat.return_value = 12345
            mock_chroma.return_value = mock_client

            from app.services.rag.vector_store import VectorStore
            vector_store = VectorStore()

            documents = ["Test document 1", "Test document 2"]
            metadatas = [{"city": "Paris"}, {"city": "London"}]
            ids = ["doc1", "doc2"]

            # Call add_documents
            await vector_store.add_documents(documents, metadatas, ids)

            # Verify collection.add was called
            mock_collection.add.assert_called_once()
            call_args = mock_collection.add.call_args
            assert call_args[1]['documents'] == documents
            assert call_args[1]['metadatas'] == metadatas
            assert call_args[1]['ids'] == ids

    @pytest.mark.asyncio
    async def test_search_with_filter(self):
        """Test RAG search with metadata filter"""
        with patch('chromadb.HttpClient') as mock_chroma, \
             patch('app.services.ai.embedding_service.get_embedding') as mock_embedding:

            # Setup embedding mock
            mock_embedding.return_value = [0.2] * 1536

            # Setup ChromaDB mock
            mock_collection = MagicMock()
            mock_collection.query.return_value = {
                'documents': [['Paris restaurant document']],
                'metadatas': [[{'city': 'Paris', 'category': 'food'}]],
                'distances': [[0.2]],  # 0.2 distance = 0.8 similarity
                'ids': [['doc2']]
            }

            mock_client = MagicMock()
            mock_client.get_or_create_collection.return_value = mock_collection
            mock_chroma.return_value = mock_client

            from app.services.rag.retrieval import RetrievalService
            service = RetrievalService()

            # Search with filter
            results = await service.search(
                "restaurants",
                n_results=5,
                filter_metadata={"city": "Paris", "category": "food"}
            )

            assert results is not None
            # Verify filter was applied
            call_args = mock_collection.query.call_args
            assert 'where' in call_args[1]
            assert call_args[1]['where'] == {"city": "Paris", "category": "food"}

    @pytest.mark.asyncio
    async def test_empty_search_results(self):
        """Test handling empty search results"""
        with patch('chromadb.HttpClient') as mock_chroma, \
             patch('app.services.ai.embedding_service.get_embedding') as mock_embedding:

            # Setup embedding mock
            mock_embedding.return_value = [0.5] * 1536

            # Setup ChromaDB mock
            mock_collection = MagicMock()
            mock_collection.query.return_value = {
                'documents': [[]],
                'metadatas': [[]],
                'distances': [[]],
                'ids': [[]]
            }

            mock_client = MagicMock()
            mock_client.get_or_create_collection.return_value = mock_collection
            mock_chroma.return_value = mock_client

            from app.services.rag.retrieval import RetrievalService
            service = RetrievalService()

            results = await service.search("nonexistent query")

            assert results['documents'] == [[]]
            assert results['metadatas'] == [[]]

    @pytest.mark.asyncio
    async def test_similarity_threshold_filtering(self):
        """Test that similarity threshold filters out low-quality results"""
        with patch('chromadb.HttpClient') as mock_chroma, \
             patch('app.services.ai.embedding_service.get_embedding') as mock_embedding:

            # Setup embedding mock
            mock_embedding.return_value = [0.3] * 1536

            # Setup ChromaDB mock with mixed quality results
            mock_collection = MagicMock()
            mock_collection.query.return_value = {
                'documents': [['High quality doc', 'Low quality doc', 'Another high quality']],
                'metadatas': [[{'city': 'Paris'}, {'city': 'Paris'}, {'city': 'Paris'}]],
                'distances': [[0.2, 0.9, 0.3]],  # 0.8, 0.1, 0.7 similarity
                'ids': [['doc1', 'doc2', 'doc3']]
            }

            mock_client = MagicMock()
            mock_client.get_or_create_collection.return_value = mock_collection
            mock_chroma.return_value = mock_client

            from app.services.rag.retrieval import RetrievalService
            service = RetrievalService(similarity_threshold=0.6)  # Filter out < 0.6

            results = await service.search("test", n_results=10)

            # Should only return 2 documents (0.8 and 0.7 similarity, not 0.1)
            assert len(results['documents'][0]) == 2
            assert results['documents'][0] == ['High quality doc', 'Another high quality']
