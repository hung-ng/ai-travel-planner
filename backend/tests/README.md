# Integration Tests

This directory contains integration tests for the AI Travel Planner backend API.

## Test Structure

```
tests/
├── conftest.py                      # Shared fixtures and test configuration
├── integration/
│   ├── test_chat_api.py            # Chat API endpoint tests
│   └── test_trips_api.py           # Trips API endpoint tests
└── fixtures/
    └── data.py                     # Test data fixtures (future)
```

## Setup

### Install Test Dependencies

```bash
cd backend
pip install -r requirements.txt
```

The following testing packages will be installed:
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Code coverage reporting
- `pytest-env` - Environment variable management
- `faker` - Test data generation

## Running Tests

### Run All Integration Tests

```bash
cd backend
pytest tests/integration/ -v
```

### Run Specific Test File

```bash
# Chat API tests
pytest tests/integration/test_chat_api.py -v

# Trips API tests
pytest tests/integration/test_trips_api.py -v
```

### Run Specific Test Class

```bash
pytest tests/integration/test_chat_api.py::TestChatMessageEndpoint -v
```

### Run Specific Test Method

```bash
pytest tests/integration/test_chat_api.py::TestChatMessageEndpoint::test_send_first_message_creates_conversation -v
```

### Run Tests with Coverage

```bash
pytest tests/integration/ -v --cov=app --cov-report=html
```

This will generate a coverage report in `htmlcov/index.html`.

### Run Only Integration Tests (by marker)

```bash
pytest -m integration -v
```

### Run Tests Excluding Slow Tests

```bash
pytest -m "not slow" -v
```

## Test Configuration

Tests are configured via `pytest.ini` in the backend directory:

- **Test Database**: Uses in-memory SQLite for fast, isolated tests
- **Environment Variables**: Test-specific values (see `pytest.ini`)
- **Markers**:
  - `@pytest.mark.integration` - Integration tests
  - `@pytest.mark.slow` - Tests that take longer to run

## Writing New Tests

### Integration Test Example

```python
import pytest
from fastapi import status

@pytest.mark.integration
class TestMyFeature:
    """Integration tests for my feature"""

    def test_feature_success(self, client, test_user_id, mock_openai_completion):
        """Test successful feature usage"""
        response = client.post(
            "/api/my-endpoint",
            json={"data": "test"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert "expected_field" in response.json()
```

## Available Fixtures

### Database Fixtures
- `db_engine` - Fresh database engine for each test
- `db_session` - Database session for test
- `client` - FastAPI test client with database override

### Data Fixtures
- `test_user_id` - Test user ID (integer: 1)
- `test_trip` - Pre-created trip with all fields
- `test_conversation` - Pre-created conversation with messages

### Mock Fixtures
- `mock_openai_completion` - Mocks OpenAI chat completions
- `mock_openai_embedding` - Mocks OpenAI embeddings
- `mock_chroma_search` - Mocks ChromaDB vector search

## Test Best Practices

1. **Use fixtures** - Leverage existing fixtures for common setup
2. **Test isolation** - Each test should be independent
3. **Clear names** - Test names should describe what they test
4. **Mock external services** - Use mocks for OpenAI, ChromaDB, etc.
5. **Assert thoroughly** - Verify both response and database state
6. **Use markers** - Mark slow tests with `@pytest.mark.slow`

## Continuous Integration

To run tests in CI/CD:

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests with coverage
pytest tests/integration/ -v --cov=app --cov-report=xml

# Tests will use in-memory SQLite (no external dependencies needed)
```

## Troubleshooting

### Import Errors

If you see import errors, ensure you're running pytest from the `backend` directory:

```bash
cd backend
pytest tests/integration/ -v
```

### Database Errors

Integration tests use in-memory SQLite, so no database setup is required. If you see database errors, check that all models are imported in `conftest.py`.

### Mock Not Working

Ensure you're using the correct mock fixtures in your test parameters:

```python
def test_my_feature(self, client, mock_openai_completion):
    # mock_openai_completion is automatically applied
    ...
```

## Future Enhancements

- [ ] Add tests for RAG service integration
- [ ] Add tests for context extraction service
- [ ] Add tests for conversation summarization
- [ ] Add end-to-end workflow tests
- [ ] Add performance/load tests
- [ ] Add API contract tests
