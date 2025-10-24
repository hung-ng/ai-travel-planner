"""
Configuration for RAG data collection
"""
from dataclasses import dataclass
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class DataCollectionConfig:
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    embedding_model: str = "text-embedding-3-small"
    embedding_batch_size: int = 100
    
    # ChromaDB
    chroma_url: str = os.getenv("CHROMA_URL", "http://localhost:8001")
    collection_name: str = "travel_knowledge"
    
    # Data collection
    priority_cities: List[str] = None
    chunk_size_words: int = 800  # Target ~800 words per chunk
    overlap_words: int = 100      # 100 word overlap between chunks
    
    # API rate limits (requests per minute)
    wikipedia_rpm: int = 200
    yelp_rpm: int = 10
    opentripmap_rpm: int = 50
    
    # Storage paths
    raw_data_path: str = "data/raw"
    processed_data_path: str = "data/processed"
    progress_file: str = "data/progress.json"
    
    # Yelp API (optional)
    yelp_api_key: str = os.getenv("YELP_API_KEY", "")
    
    # OpenTripMap API
    opentripmap_api_key: str = os.getenv("OPENTRIPMAP_API_KEY", "")
    
    def __post_init__(self):
        if self.priority_cities is None:
            # Top 50 tourist destinations
            self.priority_cities = [
                # Europe
                "Paris", "London", "Rome", "Barcelona", "Amsterdam",
                "Prague", "Vienna", "Berlin", "Munich", "Venice",
                "Florence", "Athens", "Dublin", "Edinburgh", "Lisbon",
                "Madrid", "Copenhagen", "Stockholm", "Budapest", "Krakow",
                # Asia
                "Tokyo", "Bangkok", "Singapore", "Hong Kong", "Seoul",
                "Dubai", "Bali", "Kyoto", "Shanghai", "Beijing",
                # Americas
                "New York", "Los Angeles", "San Francisco", "Miami", "Las Vegas",
                "Mexico City", "Cancun", "Rio de Janeiro", "Buenos Aires", "Vancouver",
                # Oceania & Others
                "Sydney", "Melbourne", "Auckland", "Istanbul", "Cairo",
                "Cape Town", "Marrakech", "Tel Aviv", "Jerusalem", "Mumbai"
            ]

config = DataCollectionConfig()