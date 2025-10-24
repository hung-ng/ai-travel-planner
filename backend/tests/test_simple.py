"""
Simple tests to verify setup
"""
import pytest


@pytest.mark.unit
def test_basic_math():
    """Most basic test possible"""
    assert 1 + 1 == 2


@pytest.mark.unit
def test_client_exists(client):
    """Test that test client works"""
    assert client is not None


@pytest.mark.unit
def test_health_endpoint(client):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.unit
def test_database_session(test_db_session):
    """Test database session works"""
    assert test_db_session is not None


@pytest.mark.unit
def test_sample_trip_fixture(sample_trip):
    """Test sample trip fixture"""
    assert sample_trip.id is not None
    assert sample_trip.destination == "Paris"


@pytest.mark.unit
def test_mocks_are_working(mock_openai_client, mock_chromadb):
    """Test that mocks are properly set up"""
    assert mock_openai_client is not None
    assert mock_chromadb is not None
    
    # Verify ChromaDB mock works
    collection = mock_chromadb.get_or_create_collection(name="test")
    assert collection is not None
    
    # Verify it returns mock data
    results = collection.query(query_embeddings=[[0.1] * 1536], n_results=3)
    assert 'documents' in results
    assert len(results['documents'][0]) == 3