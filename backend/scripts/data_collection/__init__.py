"""
Data collection package for RAG system

Logical organization of modules:
- config: Configuration and settings
- fetchers: All data source fetchers (APIs + web scrapers)
- processors: Text processing and chunking
- embeddings: Embedding generation
- storage: Vector database operations
- collector: Main orchestrator
"""

from .config import config, DataCollectionConfig
from .processors import DataProcessor, TextCleaner, TextChunker
from .embeddings import EmbeddingsGenerator
from .storage import VectorStore

# Import common fetchers for convenience
from .fetchers import (
    WikipediaFetcher,
    WikivoyageFetcher,
    OpenTripMapFetcher,
    YelpFetcher,
    RESTCountriesFetcher,
    GooglePlacesFetcher,
    FoursquareFetcher,
    GeoNamesFetcher,
    WikidataFetcher,
    OverpassOSMFetcher,
    WeatherAPIFetcher,
    ZomatoFetcher,
    AmadeusFetcher,
)

__all__ = [
    # Configuration
    'config',
    'DataCollectionConfig',

    # Processors
    'DataProcessor',
    'TextCleaner',
    'TextChunker',

    # Embeddings & Storage
    'EmbeddingsGenerator',
    'VectorStore',

    # Common Fetchers
    'WikipediaFetcher',
    'WikivoyageFetcher',
    'OpenTripMapFetcher',
    'YelpFetcher',
    'RESTCountriesFetcher',
    'GooglePlacesFetcher',
    'FoursquareFetcher',
    'GeoNamesFetcher',
    'WikidataFetcher',
    'OverpassOSMFetcher',
    'WeatherAPIFetcher',
    'ZomatoFetcher',
    'AmadeusFetcher',
]
