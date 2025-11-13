# AI Travel Planner

An intelligent travel planning assistant powered by **Retrieval Augmented Generation (RAG)** that provides personalized travel recommendations through natural conversation.

## Features

- **Conversational AI**: Natural language interaction for travel planning
- **Smart RAG System**: Retrieves relevant information from 14+ curated travel data sources
- **Context-Aware**: Remembers your preferences, budget, and interests throughout the conversation
- **Comprehensive Knowledge**: Data from Wikipedia, Wikivoyage, OpenStreetMap, Yelp, and more
- **Trip Management**: Create and manage complete travel itineraries
- **Real-time Recommendations**: Get instant suggestions for attractions, restaurants, and activities

## Tech Stack

### Backend
- **FastAPI** - Modern, high-performance Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **ChromaDB** - Vector database for semantic search
- **OpenAI** - GPT-4.1-nano for chat, text-embedding-3-small for embeddings
- **PostgreSQL** - Relational database for trips and conversations
- **Redis** - Caching layer (optional)

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API communication

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker and Docker Compose
- OpenAI API key

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-travel-planner
```

### 2. Set Up Environment Variables

**Backend** - Create `backend/.env`:
```bash
# Required
OPENAI_API_KEY=sk-your-openai-api-key
DATABASE_URL=postgresql://admin:password123@localhost:5432/travel_planner
CHROMA_URL=http://localhost:8001
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here

# Optional - defaults shown
OPENAI_MODEL=gpt-4.1-nano
CONTEXT_WINDOW_SIZE=10
CONTEXT_SUMMARIZE_THRESHOLD=15
RAG_TOP_K=10
RAG_SIMILARITY_THRESHOLD=0.5
```

**Frontend** - Create `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start Infrastructure Services

```bash
# Start PostgreSQL, ChromaDB, and Redis
docker-compose -f docker-compose.backend.yml up -d

# Verify services are running
docker ps
```

### 4. Initialize Database

```bash
cd backend
python scripts/init_db.py
```

### 5. Collect Travel Data (RAG)

This step populates the vector database with travel information. It requires an OpenAI API key for generating embeddings.

```bash
cd backend

# Collect data for first 10 cities from priority list
python -m scripts.data_collection.collector --count 10

# Or collect specific cities
python -m scripts.data_collection.collector --cities "Paris" "London" "Tokyo"

# Resume interrupted collection
python -m scripts.data_collection.collector --skip-completed
```

**Note**: Data collection can take 5-15 minutes per city depending on API availability. Progress is saved to `progress.json`.

### 6. Start Backend Server

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn main:app --reload --port 8000
```

Backend will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 7. Start Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at http://localhost:3000

## Usage

1. Navigate to http://localhost:3000
2. Click "Start Planning Now" to begin a conversation
3. Tell the AI about your travel plans:
   - "I'm planning a trip to Paris for 5 days"
   - "What are the best museums in Paris?"
   - "I'm interested in food and history"
   - "My budget is $2000"
4. The AI will provide personalized recommendations based on your preferences

## Architecture

### How RAG Works

```
User Query
    ↓
Context Extraction (destination, interests, budget, etc.)
    ↓
Query Enhancement ("restaurants" → "restaurants in Paris focusing on food")
    ↓
Embedding Generation (OpenAI text-embedding-3-small)
    ↓
Vector Search (ChromaDB with cosine similarity)
    ↓
Similarity Filtering (threshold: 0.5)
    ↓
Top 10 Relevant Documents
    ↓
AI Response Generation (GPT-4.1-nano with RAG context)
    ↓
Personalized Recommendation
```

### Context Management

The system uses intelligent context windowing:
- **Recent Messages**: Last 10 messages kept in full
- **Conversation Summary**: Older messages automatically summarized when count exceeds 15
- **Extracted Context**: Key facts (destination, budget, interests) tracked throughout
- **RAG Context**: Relevant documents fetched per query

This approach maintains conversation coherence while optimizing token usage and API costs.

### Data Sources

The RAG system aggregates information from 14+ sources:

**Always Available (no API key required):**
- Wikipedia - General city information, history, culture
- Wikivoyage - Travel guides, practical tips
- REST Countries - Country facts, currencies, languages
- Wikidata - Structured attraction data
- OpenStreetMap - Points of interest, geographic data
- Web Scrapers - Lonely Planet, Rick Steves, Atlas Obscura, Culture Trip

**Optional (API key required):**
- OpenTripMap - Tourist attractions
- Yelp - Restaurants, ratings, reviews
- Google Places - Attractions, business information
- Foursquare - Venues and recommendations
- GeoNames - Geographic database
- WeatherAPI - Climate information
- Zomato - Restaurant data
- Amadeus - Travel activities and bookings

## Development

### Project Structure

```
ai-travel-planner/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   │   ├── ai/           # OpenAI integration
│   │   │   ├── rag/          # Vector search
│   │   │   └── context/      # Context management
│   │   ├── config.py         # Configuration
│   │   └── database.py       # Database setup
│   ├── scripts/
│   │   ├── init_db.py        # Database initialization
│   │   └── data_collection/  # RAG data pipeline
│   └── tests/                # Test suite
├── frontend/
│   └── src/
│       ├── app/              # Next.js pages
│       ├── components/       # React components
│       ├── lib/              # API client
│       └── types/            # TypeScript types
└── docker-compose.backend.yml
```

### Running Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest -m unit           # Unit tests
pytest -m integration    # Integration tests
pytest -m api            # API tests
pytest -m service        # Service tests

# Run specific test file
pytest tests/test_api_chat.py

# Run single test
pytest tests/test_api_chat.py::test_send_message
```

Test coverage report will be available at `backend/htmlcov/index.html`.

### Linting

```bash
# Frontend
cd frontend
npm run lint
```

### Database Management

```bash
# Reset database (development only)
cd backend
python scripts/init_db.py

# The project uses Alembic for migrations
# Migration files would be in backend/alembic/versions/
```

## API Documentation

Interactive API documentation is available at http://localhost:8000/docs when the backend is running.

### Key Endpoints

**Chat:**
- `POST /api/chat/message` - Send a message and get AI response
- `POST /api/chat/conversations` - Create new conversation
- `GET /api/chat/conversations/{id}` - Get conversation history

**Trips:**
- `POST /api/trips/` - Create new trip
- `GET /api/trips/{id}` - Get trip details
- `PUT /api/trips/{id}` - Update trip
- `GET /api/trips/` - List user's trips

**Health:**
- `GET /health` - Health check endpoint

## Configuration Options

### Backend Settings (backend/.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Required | OpenAI API key |
| `OPENAI_MODEL` | gpt-4.1-nano | Chat completion model |
| `OPENAI_TEMPERATURE` | 0.7 | Response randomness (0-1) |
| `OPENAI_MAX_TOKENS` | 2000 | Max tokens per response |
| `OPENAI_EMBEDDING_MODEL` | text-embedding-3-small | Embedding model |
| `CONTEXT_WINDOW_SIZE` | 10 | Number of recent messages to keep |
| `CONTEXT_SUMMARIZE_THRESHOLD` | 15 | Messages before summarization |
| `RAG_TOP_K` | 10 | Number of documents to retrieve |
| `RAG_SIMILARITY_THRESHOLD` | 0.5 | Minimum similarity score (0-1) |
| `DATABASE_URL` | Required | PostgreSQL connection string |
| `CHROMA_URL` | Required | ChromaDB URL |
| `REDIS_URL` | Optional | Redis connection string |
| `SECRET_KEY` | Required | JWT signing key |
