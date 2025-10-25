"""
Configuration for RAG data collection
"""
from dataclasses import dataclass
from typing import List, Optional
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get the data collection package directory
DATA_COLLECTION_DIR = Path(__file__).parent
DATA_DIR = DATA_COLLECTION_DIR / "data"

@dataclass
class DataCollectionConfig:
    """Configuration for RAG data collection"""

    # ============================================
    # OpenAI Configuration (REQUIRED)
    # ============================================
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    embedding_model: str = "text-embedding-3-small"
    embedding_batch_size: int = 100

    # ============================================
    # ChromaDB Configuration
    # ============================================
    chroma_url: str = os.getenv("CHROMA_URL", "http://localhost:8001")
    collection_name: str = "travel_knowledge"

    # ============================================
    # Data Collection Settings
    # ============================================
    priority_cities: Optional[List[str]] = None
    chunk_size_words: int = 800      # 200-400 if need better match
    overlap_words: int = 100         # 50 if need better match

    # ============================================
    # External API Keys (OPTIONAL)
    # ============================================

    # OpenTripMap API
    # Sign up: https://opentripmap.io/product
    # Free tier: 1000 requests/day
    opentripmap_api_key: str = os.getenv("OPENTRIPMAP_API_KEY", "")

    # Yelp Fusion API
    # Sign up: https://www.yelp.com/developers
    # Free tier: 500 requests/day
    yelp_api_key: str = os.getenv("YELP_API_KEY", "")

    # ============================================
    # Phase 2: Additional API Keys (OPTIONAL)
    # ============================================

    # Google Places API
    # Sign up: https://console.cloud.google.com/apis/credentials
    # Free tier: $200 credit/month
    google_places_api_key: str = os.getenv("GOOGLE_PLACES_API_KEY", "")

    # Foursquare Places API
    # Sign up: https://foursquare.com/developers/signup
    # Free tier: 50,000 calls/month
    foursquare_api_key: str = os.getenv("FOURSQUARE_API_KEY", "")

    # GeoNames API
    # Sign up: http://www.geonames.org/login
    # Free tier: 20,000 credits/day
    geonames_username: str = os.getenv("GEONAMES_USERNAME", "")

    # WeatherAPI
    # Sign up: https://www.weatherapi.com/signup.aspx
    # Free tier: 1M calls/month
    weather_api_key: str = os.getenv("WEATHER_API_KEY", "")

    # Zomato API
    # Sign up: https://developers.zomato.com/api
    # Note: May have limited availability
    zomato_api_key: str = os.getenv("ZOMATO_API_KEY", "")

    # Amadeus Travel API
    # Sign up: https://developers.amadeus.com/register
    # Free tier: Test environment
    amadeus_api_key: str = os.getenv("AMADEUS_API_KEY", "")
    amadeus_api_secret: str = os.getenv("AMADEUS_API_SECRET", "")

    # ============================================
    # API Rate Limits (requests per minute)
    # ============================================
    wikipedia_rpm: int = 200          # Wikipedia is very generous
    wikivoyage_rpm: int = 200         # Same as Wikipedia
    opentripmap_rpm: int = 50         # Stay well under 1000/day limit
    yelp_rpm: int = 10                # Conservative to stay under 500/day

    # Phase 2 rate limits
    google_places_rpm: int = 100      # Generous free tier
    foursquare_rpm: int = 50          # 50K/month = ~1600/day
    geonames_rpm: int = 100           # 20K/day = ~800/hour
    weather_api_rpm: int = 100        # 1M/month is very generous
    zomato_rpm: int = 100             # If available
    amadeus_rpm: int = 50             # Test environment limits
    wikidata_rpm: int = 100           # Public SPARQL endpoint
    overpass_osm_rpm: int = 30        # Shared public instance - be conservative
    web_scraper_rpm: int = 10         # Very conservative for web scraping

    # ============================================
    # Storage Paths (relative to data_collection package)
    # ============================================
    raw_data_path: str = str(DATA_DIR / "raw")
    processed_data_path: str = str(DATA_DIR / "processed")
    progress_file: str = str(DATA_DIR / "progress.json")
    
    def __post_init__(self):
        """Validate configuration and set defaults"""
        
        # Validate OpenAI API key
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required! Set it in .env file or environment."
            )
        
        # Set default priority cities if not provided
        if self.priority_cities is None:
            self.priority_cities = self._get_default_cities()
        
        # Validate optional API keys
        self._validate_optional_apis()
    
    def _get_default_cities(self) -> List[str]:
        """Get default list of priority cities"""
        return [
            # Europe (20 cities)
            "Paris", "London", "Rome", "Barcelona", "Amsterdam",
            "Prague", "Vienna", "Berlin", "Munich", "Venice",
            "Florence", "Athens", "Dublin", "Edinburgh", "Lisbon",
            "Madrid", "Copenhagen", "Stockholm", "Budapest", "Krakow",
            
            # Asia (15 cities)
            "Tokyo", "Bangkok", "Singapore", "Hong Kong", "Seoul",
            "Dubai", "Bali", "Kyoto", "Shanghai", "Beijing",
            "Taipei", "Hanoi", "Ho Chi Minh City", "Kuala Lumpur", "Manila",
            
            # Americas (10 cities)
            "New York", "Los Angeles", "San Francisco", "Miami", "Las Vegas",
            "Mexico City", "Cancun", "Rio de Janeiro", "Buenos Aires", "Vancouver",
            
            # Oceania & Others (5 cities)
            "Sydney", "Melbourne", "Auckland", "Istanbul", "Cairo"
        ]
    
    def _validate_optional_apis(self):
        """Validate and log status of optional API keys"""
        apis_status = []

        # Phase 1 APIs
        if self.opentripmap_api_key:
            apis_status.append("✅ OpenTripMap API: Enabled")
        else:
            apis_status.append("⚠️  OpenTripMap API: Disabled (no API key)")

        if self.yelp_api_key:
            apis_status.append("✅ Yelp API: Enabled")
        else:
            apis_status.append("⚠️  Yelp API: Disabled (no API key)")

        # Phase 2 APIs
        if self.google_places_api_key:
            apis_status.append("✅ Google Places API: Enabled")
        else:
            apis_status.append("⚠️  Google Places API: Disabled (no API key)")

        if self.foursquare_api_key:
            apis_status.append("✅ Foursquare API: Enabled")
        else:
            apis_status.append("⚠️  Foursquare API: Disabled (no API key)")

        if self.geonames_username:
            apis_status.append("✅ GeoNames API: Enabled")
        else:
            apis_status.append("⚠️  GeoNames API: Disabled (no username)")

        if self.weather_api_key:
            apis_status.append("✅ Weather API: Enabled")
        else:
            apis_status.append("⚠️  Weather API: Disabled (no API key)")

        if self.zomato_api_key:
            apis_status.append("✅ Zomato API: Enabled")
        else:
            apis_status.append("⚠️  Zomato API: Disabled (no API key)")

        if self.amadeus_api_key and self.amadeus_api_secret:
            apis_status.append("✅ Amadeus API: Enabled")
        else:
            apis_status.append("⚠️  Amadeus API: Disabled (no API key/secret)")

        # Store status for logging
        self._api_status = apis_status
    
    def get_api_status(self) -> List[str]:
        """Get status of all APIs"""
        status = [
            "=" * 60,
            "API Configuration Status",
            "=" * 60,
            f"✅ OpenAI API: Configured ({self.embedding_model})",
            f"✅ ChromaDB: {self.chroma_url}",
        ]

        status.extend(self._api_status)

        status.extend([
            "",
            "Always Available (No API Key Required):",
            "✅ Wikipedia",
            "✅ Wikivoyage",
            "✅ REST Countries",
            "✅ Wikidata (SPARQL)",
            "✅ OpenStreetMap (Overpass API)",
            "✅ Web Scrapers (Lonely Planet, Rick Steves, Atlas Obscura, Culture Trip)",
            "=" * 60
        ])

        return status

    # Phase 1 API availability checks
    def has_opentripmap(self) -> bool:
        """Check if OpenTripMap API is configured"""
        return bool(self.opentripmap_api_key)

    def has_yelp(self) -> bool:
        """Check if Yelp API is configured"""
        return bool(self.yelp_api_key)

    # Phase 2 API availability checks
    def has_google_places(self) -> bool:
        """Check if Google Places API is configured"""
        return bool(self.google_places_api_key)

    def has_foursquare(self) -> bool:
        """Check if Foursquare API is configured"""
        return bool(self.foursquare_api_key)

    def has_geonames(self) -> bool:
        """Check if GeoNames API is configured"""
        return bool(self.geonames_username)

    def has_weather_api(self) -> bool:
        """Check if Weather API is configured"""
        return bool(self.weather_api_key)

    def has_zomato(self) -> bool:
        """Check if Zomato API is configured"""
        return bool(self.zomato_api_key)

    def has_amadeus(self) -> bool:
        """Check if Amadeus API is configured"""
        return bool(self.amadeus_api_key and self.amadeus_api_secret)

# Create singleton config instance
config = DataCollectionConfig()