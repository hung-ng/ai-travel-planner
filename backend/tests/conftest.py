import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path

# Set test environment variables BEFORE importing app modules
os.environ.setdefault("OPENAI_API_KEY", "test-key-12345")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("CHROMA_URL", "http://localhost:8001")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import Base

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_db_engine():
    """Create test database engine"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine) -> Generator[Session, None, None]:
    """Create test database session"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db_engine
    )
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function", autouse=True)
def mock_openai_client():
    """Mock OpenAI client for all tests"""
    with patch('openai.OpenAI') as mock_openai:
        # Mock chat completion
        mock_chat_response = MagicMock()
        mock_chat_response.choices = [MagicMock()]
        mock_chat_response.choices[0].message.content = "This is a test AI response about Paris travel."
        mock_chat_response.usage.prompt_tokens = 100
        mock_chat_response.usage.completion_tokens = 50
        mock_chat_response.usage.total_tokens = 150
        
        # Mock embedding
        mock_embedding_response = MagicMock()
        mock_embedding_response.data = [MagicMock()]
        mock_embedding_response.data[0].embedding = [0.1] * 1536
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_chat_response
        mock_client.embeddings.create.return_value = mock_embedding_response
        
        mock_openai.return_value = mock_client
        yield mock_client


@pytest.fixture(scope="function")
def mock_chromadb():
    """Mock ChromaDB (use explicitly when needed, not autouse to avoid conflicts)"""
    
    class MockCollection:
        def __init__(self):
            self._documents = {}
        
        def add(self, documents=None, metadatas=None, ids=None, embeddings=None, **kwargs):
            """Mock add documents"""
            if ids:
                for i, doc_id in enumerate(ids):
                    self._documents[doc_id] = {
                        'document': documents[i] if documents else '',
                        'metadata': metadatas[i] if metadatas else {},
                        'embedding': embeddings[i] if embeddings else []
                    }
        
        def query(self, query_embeddings=None, n_results=5, where=None, **kwargs):
            """Mock query"""
            return {
                'documents': [[
                    'Paris is the capital of France, known for the Eiffel Tower.',
                    'The Louvre Museum houses the Mona Lisa.',
                    'French cuisine includes croissants and wine.',
                    'Best time to visit Paris is April-June.',
                    'Paris has an excellent metro system.'
                ][:n_results]],
                'metadatas': [[
                    {'city': 'Paris', 'category': 'overview', 'source': 'wikipedia'},
                    {'city': 'Paris', 'category': 'attractions', 'source': 'wikipedia'},
                    {'city': 'Paris', 'category': 'food', 'source': 'yelp'},
                    {'city': 'Paris', 'category': 'planning', 'source': 'wikivoyage'},
                    {'city': 'Paris', 'category': 'transportation', 'source': 'wikivoyage'}
                ][:n_results]],
                'distances': [[0.2, 0.3, 0.35, 0.4, 0.45][:n_results]],
                'ids': [['doc1', 'doc2', 'doc3', 'doc4', 'doc5'][:n_results]]
            }
        
        def count(self):
            """Mock count"""
            return len(self._documents)
    
    class MockChromaClient:
        def __init__(self):
            self.collections = {}
        
        def get_or_create_collection(self, name=None, metadata=None, **kwargs):
            if name not in self.collections:
                self.collections[name] = MockCollection()
            return self.collections[name]
    
    with patch('chromadb.HttpClient') as mock_http, \
         patch('chromadb.PersistentClient') as mock_persistent:
        
        mock_client = MockChromaClient()
        mock_http.return_value = mock_client
        mock_persistent.return_value = mock_client
        
        yield mock_client


@pytest.fixture(scope="function")
def client(test_db_session) -> Generator[TestClient, None, None]:
    """Create test client with overridden database"""
    
    # Import app here to use mocked dependencies
    from main import app
    from app.database import get_db
    
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_trip_data():
    """Sample trip data for database models (uses datetime objects)"""
    now = datetime.now()
    return {
        "user_id": 1,
        "destination": "Paris",
        "start_date": now + timedelta(days=30),
        "end_date": now + timedelta(days=35),
        "budget": 2000,
        "preferences": {"interests": ["art", "food"]}
    }


@pytest.fixture
def sample_trip_api_data():
    """Sample trip data for API requests (uses ISO strings)"""
    now = datetime.now()
    return {
        "user_id": 1,
        "destination": "Paris",
        "start_date": (now + timedelta(days=30)).isoformat(),
        "end_date": (now + timedelta(days=35)).isoformat(),
        "budget": 2000,
        "preferences": {"interests": ["art", "food"]}
    }


@pytest.fixture
def sample_trip(test_db_session, sample_trip_data):
    """Create a sample trip in the database"""
    from app.models.trip import Trip
    trip = Trip(**sample_trip_data)
    test_db_session.add(trip)
    test_db_session.commit()
    test_db_session.refresh(trip)
    return trip


@pytest.fixture
def sample_conversation_data():
    """Sample conversation data"""
    return {
        "trip_id": 1,
        "user_id": 1,  # ADDED
        "messages": [
            {"role": "user", "content": "I want to visit Paris"},
            {"role": "assistant", "content": "Great choice! What's your budget?"}
        ]
    }


@pytest.fixture
def sample_conversation(test_db_session, sample_trip, sample_conversation_data):
    """Create a sample conversation in the database"""
    from app.models.conversation import Conversation
    conversation = Conversation(
        trip_id=sample_trip.id,
        user_id=sample_conversation_data["user_id"],
        messages=sample_conversation_data["messages"],
        context={},
        summary=None,
        message_count=len(sample_conversation_data["messages"]),
        last_summarized_index=0
    )
    test_db_session.add(conversation)
    test_db_session.commit()
    test_db_session.refresh(conversation)
    return conversation


# Additional fixtures for specific test needs
@pytest.fixture
def mock_openai_response():
    """Mock OpenAI response structure for tests that need it"""
    class MockChoice:
        def __init__(self):
            self.message = type('Message', (), {
                'content': 'This is a test response from the AI assistant.'
            })()
    
    class MockUsage:
        prompt_tokens = 100
        completion_tokens = 50
        total_tokens = 150
    
    class MockResponse:
        def __init__(self):
            self.choices = [MockChoice()]
            self.usage = MockUsage()
    
    return MockResponse()


@pytest.fixture
def mock_embedding_response():
    """Mock embedding response structure for tests that need it"""
    class MockEmbeddingData:
        embedding = [0.1] * 1536
    
    class MockEmbeddingResponse:
        data = [MockEmbeddingData()]
    
    return MockEmbeddingResponse()


@pytest.fixture
def mock_rag_results():
    """Mock RAG search results"""
    return {
        'documents': [[
            'Paris is the capital of France.',
            'The Louvre Museum is famous.',
            'French cuisine is renowned.'
        ]],
        'metadatas': [[
            {'city': 'Paris', 'category': 'overview'},
            {'city': 'Paris', 'category': 'attractions'},
            {'city': 'Paris', 'category': 'food'}
        ]],
        'distances': [[0.2, 0.3, 0.4]]
    }


@pytest.fixture
def mock_ai_service(mocker):
    """Mock AI service at service level"""
    # Mock chat service
    mock_chat = mocker.patch('app.services.ai.chat_service.get_completion')
    mock_chat.return_value = "This is a mocked AI response about your travel plans."

    # Mock embedding service
    mock_embedding = mocker.patch('app.services.ai.embedding_service.get_embedding')
    mock_embedding.return_value = [0.1] * 1536

    return mock_chat


@pytest.fixture
def mock_rag_service(mocker):
    """Mock RAG service at service level"""
    mock = mocker.patch('app.services.rag.retrieval_service.search')
    mock.return_value = {
        'documents': [['Paris is a beautiful city with rich history', 'The Eiffel Tower is iconic', 'French cuisine is world-renowned']],
        'metadatas': [[{'city': 'Paris', 'source': 'wikipedia'}, {'city': 'Paris', 'source': 'wikivoyage'}, {'city': 'Paris', 'source': 'yelp'}]],
        'distances': [[0.2, 0.3, 0.4]]
    }
    return mock


@pytest.fixture
def mock_rag_empty_results(mock_chromadb):
    """Override RAG to return empty results"""
    for collection in mock_chromadb.collections.values():
        original_query = collection.query
        collection.query = lambda **kwargs: {
            'documents': [[]],
            'metadatas': [[]],
            'distances': [[]],
            'ids': [[]]
        }
    yield
    # Restore
    for collection in mock_chromadb.collections.values():
        collection.query = original_query


@pytest.fixture
def mock_openai_error(mock_openai_client):
    """Mock OpenAI to raise an error"""
    mock_openai_client.chat.completions.create.side_effect = Exception("OpenAI API Error")
    yield
    # Reset
    mock_openai_client.chat.completions.create.side_effect = None
