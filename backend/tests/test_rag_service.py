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
        # Need to patch both ChromaDB, embedding service, AND vector_store singleton
        with patch('chromadb.HttpClient') as mock_chroma, \
             patch('app.services.rag.retrieval.embedding_service') as mock_embedding, \
             patch('app.services.rag.retrieval.vector_store') as mock_vs:

            # Setup embedding mock - return value, not coroutine
            mock_embedding.get_embedding = AsyncMock(return_value=[0.1] * 1536)

            # Setup vector_store singleton mock
            mock_vs.query = AsyncMock(return_value={
                'documents': [['Test document about Paris']],
                'metadatas': [[{'city': 'Paris', 'source': 'wikipedia'}]],
                'distances': [[0.3]],  # 0.3 distance = 0.7 similarity
                'ids': [['doc1']]
            })

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
            mock_collection.count.return_value = 0

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
            call_kwargs = mock_collection.add.call_args.kwargs
            assert call_kwargs['documents'] == documents
            assert call_kwargs['metadatas'] == metadatas
            assert call_kwargs['ids'] == ids

    @pytest.mark.asyncio
    async def test_search_with_filter(self):
        """Test RAG search with metadata filter"""
        with patch('chromadb.HttpClient') as mock_chroma, \
             patch('app.services.rag.retrieval.embedding_service') as mock_embedding, \
             patch('app.services.rag.retrieval.vector_store') as mock_vs:

            # Setup embedding mock
            mock_embedding.get_embedding = AsyncMock(return_value=[0.2] * 1536)

            # Setup vector_store singleton mock
            mock_vs.query = AsyncMock(return_value={
                'documents': [['Paris restaurant document']],
                'metadatas': [[{'city': 'Paris', 'category': 'food'}]],
                'distances': [[0.2]],  # 0.2 distance = 0.8 similarity
                'ids': [['doc2']]
            })

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
            assert len(results['documents'][0]) > 0

            # Verify filter was applied - check that vector_store.query was called
            mock_vs.query.assert_called_once()
            # Access kwargs properly
            if mock_vs.query.call_args:
                call_kwargs = mock_vs.query.call_args[1]  # kwargs are in index 1
                assert 'filter_metadata' in call_kwargs or 'where' in call_kwargs

    @pytest.mark.asyncio
    async def test_empty_search_results(self):
        """Test handling empty search results"""
        # Need to patch vector_store singleton as well
        with patch('chromadb.HttpClient') as mock_chroma, \
             patch('app.services.rag.retrieval.embedding_service') as mock_embedding, \
             patch('app.services.rag.retrieval.vector_store') as mock_vs:

            # Setup embedding mock
            mock_embedding.get_embedding = AsyncMock(return_value=[0.5] * 1536)

            # Setup vector_store mock to return empty results
            mock_vs.query = AsyncMock(return_value={
                'documents': [[]],
                'metadatas': [[]],
                'distances': [[]],
                'ids': [[]]
            })

            # Setup ChromaDB mock - return empty results
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
        # Need to patch vector_store singleton as well
        with patch('chromadb.HttpClient') as mock_chroma, \
             patch('app.services.rag.retrieval.embedding_service') as mock_embedding, \
             patch('app.services.rag.retrieval.vector_store') as mock_vs:

            # Setup embedding mock
            mock_embedding.get_embedding = AsyncMock(return_value=[0.3] * 1536)

            # Setup vector_store mock to return mixed quality results
            mock_vs.query = AsyncMock(return_value={
                'documents': [['High quality doc', 'Low quality doc', 'Another high quality']],
                'metadatas': [[{'city': 'Paris'}, {'city': 'Paris'}, {'city': 'Paris'}]],
                'distances': [[0.2, 0.9, 0.3]],  # 0.8, 0.1, 0.7 similarity
                'ids': [['doc1', 'doc2', 'doc3']]
            })

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

    @pytest.mark.asyncio
    async def test_search_error_handling(self):
        """Test that search handles errors gracefully"""
        with patch('chromadb.HttpClient') as mock_chroma, \
             patch('app.services.rag.retrieval.embedding_service') as mock_embedding:

            # Setup embedding to raise error
            mock_embedding.get_embedding = AsyncMock(side_effect=Exception("Embedding failed"))

            mock_client = MagicMock()
            mock_chroma.return_value = mock_client

            from app.services.rag.retrieval import RetrievalService
            service = RetrievalService()

            # Should return empty results on error (service catches exception)
            results = await service.search("test query")

            # Service returns empty structure on error
            assert results['documents'] == [[]]
            assert results['metadatas'] == [[]]
            assert results['distances'] == [[]]

    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test getting retrieval service statistics"""
        with patch('chromadb.HttpClient') as mock_chroma:
            mock_collection = MagicMock()
            mock_collection.count.return_value = 1000

            mock_client = MagicMock()
            mock_client.get_or_create_collection.return_value = mock_collection
            mock_client.heartbeat.return_value = 12345
            mock_chroma.return_value = mock_client

            from app.services.rag.retrieval import RetrievalService
            service = RetrievalService(similarity_threshold=0.5)

            stats = service.get_stats()

            assert 'similarity_threshold' in stats
            assert stats['similarity_threshold'] == 0.5
            assert 'embedding_model' in stats
            assert 'embedding_dimensions' in stats
            assert stats['embedding_dimensions'] == 1536
