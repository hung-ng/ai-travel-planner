"""
Main script to collect and process RAG data
"""
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.data_collection.config import config
from scripts.data_collection.processors import DataProcessor
from scripts.data_collection.embeddings import EmbeddingsGenerator
from scripts.data_collection.storage import VectorStore

# Import all fetchers from consolidated module
from scripts.data_collection.fetchers import (
    # Wiki sources
    WikipediaFetcher, WikivoyageFetcher,
    # Geographic & country data
    RESTCountriesFetcher, GeoNamesFetcher, OpenTripMapFetcher,
    # POI & places
    GooglePlacesFetcher, FoursquareFetcher, AmadeusFetcher,
    WikidataFetcher, OverpassOSMFetcher,
    # Restaurants
    YelpFetcher, ZomatoFetcher,
    # Weather
    WeatherAPIFetcher,
    # Web scrapers
    LonelyPlanetScraper, RickStevesScraper, AtlasObscuraScraper,
    CultureTripScraper, city_to_slug
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ProgressTracker:
    """Track progress of data collection"""
    
    def __init__(self, progress_file: str):
        """
        Initialize progress tracker
        
        Args:
            progress_file: Path to JSON file for storing progress
        """
        self.progress_file = progress_file
        self.progress = self._load_progress()
    
    def _load_progress(self) -> Dict:
        """Load progress from file"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading progress file: {e}")
                return {"completed_cities": [], "last_updated": None}
        return {"completed_cities": [], "last_updated": None}
    
    def _save_progress(self):
        """Save progress to file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
            
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving progress: {e}")
    
    def is_completed(self, city: str) -> bool:
        """Check if city has been processed"""
        return city in self.progress.get("completed_cities", [])
    
    def mark_completed(self, city: str):
        """Mark city as completed"""
        if "completed_cities" not in self.progress:
            self.progress["completed_cities"] = []
        
        if city not in self.progress["completed_cities"]:
            self.progress["completed_cities"].append(city)
        
        self.progress["last_updated"] = datetime.now().isoformat()
        self._save_progress()
        
        logger.info(f"✅ Marked {city} as completed")
    
    def get_stats(self) -> Dict:
        """Get progress statistics"""
        return {
            "completed_count": len(self.progress.get("completed_cities", [])),
            "completed_cities": self.progress.get("completed_cities", []),
            "last_updated": self.progress.get("last_updated")
        }


class RAGDataCollector:
    """Main data collector"""
    
    def __init__(self):
        """Initialize RAG data collector"""
        
        # Log API configuration status
        logger.info("\n" + "\n".join(config.get_api_status()))
        
        # Initialize core components (always available)
        logger.info("Initializing core components...")
        self.wikipedia = WikipediaFetcher(config.wikipedia_rpm)
        self.wikivoyage = WikivoyageFetcher(config.wikivoyage_rpm)
        self.rest_countries = RESTCountriesFetcher()
        
        # Initialize processing components
        logger.info("Initializing processing components...")
        self.processor = DataProcessor(
            chunk_size_words=config.chunk_size_words,
            overlap_words=config.overlap_words
        )
        self.embeddings = EmbeddingsGenerator(
            api_key=config.openai_api_key,
            model=config.embedding_model,
            batch_size=config.embedding_batch_size
        )
        self.vector_store = VectorStore(
            chroma_url=config.chroma_url,
            collection_name=config.collection_name
        )
        
        # Initialize progress tracker
        logger.info(f"Initializing progress tracker at: {config.progress_file}")
        self.progress = ProgressTracker(progress_file=config.progress_file)
        
        # Initialize optional fetchers
        self.opentripmap = None
        if config.has_opentripmap():
            logger.info("🗺️  Initializing OpenTripMap fetcher...")
            self.opentripmap = OpenTripMapFetcher(
                api_key=config.opentripmap_api_key,
                rate_limit_rpm=config.opentripmap_rpm
            )
        else:
            logger.warning("⚠️  OpenTripMap disabled: No API key")
            logger.info("   Get free key: https://opentripmap.io/product")
        
        self.yelp = None
        if config.has_yelp():
            logger.info("🍽️  Initializing Yelp fetcher...")
            self.yelp = YelpFetcher(
                api_key=config.yelp_api_key,
                rate_limit_rpm=config.yelp_rpm
            )
        else:
            logger.warning("⚠️  Yelp disabled: No API key")
            logger.info("   Get free key: https://www.yelp.com/developers")

        # Initialize Phase 2 fetchers (optional, based on available API keys)
        self._init_phase2_fetchers()

        # Create directories
        os.makedirs(config.raw_data_path, exist_ok=True)
        os.makedirs(config.processed_data_path, exist_ok=True)

        logger.info("\n✅ RAG Data Collector initialized successfully\n")

    def _init_phase2_fetchers(self):
        """Initialize additional data sources (all optional based on API keys)"""
        logger.info("\n🚀 Initializing additional data sources...")

        # Google Places
        self.google_places = None
        if config.has_google_places():
            logger.info("📍 Initializing Google Places...")
            self.google_places = GooglePlacesFetcher(
                api_key=config.google_places_api_key,
                rate_limit_rpm=config.google_places_rpm
            )

        # Foursquare
        self.foursquare = None
        if config.has_foursquare():
            logger.info("📍 Initializing Foursquare...")
            self.foursquare = FoursquareFetcher(
                api_key=config.foursquare_api_key,
                rate_limit_rpm=config.foursquare_rpm
            )

        # GeoNames
        self.geonames = None
        if config.has_geonames():
            logger.info("🌍 Initializing GeoNames...")
            self.geonames = GeoNamesFetcher(
                username=config.geonames_username,
                rate_limit_rpm=config.geonames_rpm
            )

        # WeatherAPI
        self.weather_api = None
        if config.has_weather_api():
            logger.info("🌤️  Initializing WeatherAPI...")
            self.weather_api = WeatherAPIFetcher(
                api_key=config.weather_api_key,
                rate_limit_rpm=config.weather_api_rpm
            )

        # Zomato
        self.zomato = None
        if config.has_zomato():
            logger.info("🍽️  Initializing Zomato...")
            self.zomato = ZomatoFetcher(
                api_key=config.zomato_api_key,
                rate_limit_rpm=config.zomato_rpm
            )

        # Amadeus
        self.amadeus = None
        if config.has_amadeus():
            logger.info("✈️  Initializing Amadeus...")
            self.amadeus = AmadeusFetcher(
                api_key=config.amadeus_api_key,
                api_secret=config.amadeus_api_secret,
                rate_limit_rpm=config.amadeus_rpm
            )

        # Always available (no API key required)
        logger.info("🔓 Initializing free data sources...")
        self.wikidata = WikidataFetcher(rate_limit_rpm=config.wikidata_rpm)
        self.osm = OverpassOSMFetcher(rate_limit_rpm=config.overpass_osm_rpm)

        # Web scrapers (use conservatively)
        logger.info("🕷️  Initializing web scrapers...")
        self.lonely_planet = LonelyPlanetScraper(rate_limit_rpm=config.web_scraper_rpm)
        self.rick_steves = RickStevesScraper(rate_limit_rpm=config.web_scraper_rpm)
        self.atlas_obscura = AtlasObscuraScraper(rate_limit_rpm=config.web_scraper_rpm)
        self.culture_trip = CultureTripScraper(rate_limit_rpm=config.web_scraper_rpm)

        logger.info("✅ Phase 2 sources initialized\n")
    
    def collect_city_data(self, city: str, country: str) -> List[Dict]:
        """Collect all data for a city"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Collecting data for: {city}, {country}")
        logger.info(f"{'='*60}")

        all_chunks = []

        # 1. Wikipedia - FETCH MULTIPLE ARTICLES
        logger.info("📖 Fetching Wikipedia articles (main + attractions + transport)...")
        wiki_articles = self.wikipedia.fetch_multiple_articles(city)
        if wiki_articles:
            for article in wiki_articles:
                chunks = self.processor.process_wikipedia_article(article, city, country)
                all_chunks.extend(chunks)
            logger.info(f"✅ Wikipedia: {len(all_chunks)} chunks from {len(wiki_articles)} articles")
        else:
            logger.warning(f"⚠️  Wikipedia: No articles found")

        # 2. Wikivoyage - FETCH MULTIPLE GUIDES
        logger.info("🗺️  Fetching Wikivoyage guides (main + districts + topics)...")
        wikivoyage_guides = self.wikivoyage.fetch_multiple_guides(city)
        wikivoyage_chunk_count = 0
        if wikivoyage_guides:
            for guide in wikivoyage_guides:
                chunks = self.processor.process_wikivoyage_guide(guide, city, country)
                all_chunks.extend(chunks)
                wikivoyage_chunk_count += len(chunks)
            logger.info(f"✅ Wikivoyage: {wikivoyage_chunk_count} chunks from {len(wikivoyage_guides)} guides")
        else:
            logger.warning(f"⚠️  Wikivoyage: No guides found")
        
        # 3. OpenTripMap POIs
        if self.opentripmap:
            logger.info("📍 Fetching OpenTripMap POIs...")
            coords = self.opentripmap.geocode(city)
            if coords:
                # Fetch POIs without kinds filter (free tier limitation)
                # Free tier works better without category filtering
                pois = self.opentripmap.fetch_pois(
                    coords["lat"],
                    coords["lon"],
                    radius=5000
                )
                if pois:
                    chunks = self.processor.process_poi_data(pois, city, country)
                    all_chunks.extend(chunks)
                    logger.info(f"✅ OpenTripMap: {len(chunks)} chunks from {len(pois)} POIs")
                else:
                    logger.warning(f"⚠️  OpenTripMap: No POIs found")
            else:
                logger.warning(f"⚠️  OpenTripMap: Could not geocode {city}")
        
        # 4. Yelp restaurants
        if self.yelp:
            logger.info("🍽️  Fetching Yelp restaurants...")
            restaurants = self.yelp.search_restaurants(f"{city}, {country}", limit=50)
            if restaurants:
                chunks = self.processor.process_restaurant_data(restaurants, city, country)
                all_chunks.extend(chunks)
                logger.info(f"✅ Yelp: {len(chunks)} chunks from {len(restaurants)} restaurants")
            else:
                logger.warning(f"⚠️  Yelp: No restaurants found")

        # 5. REST Countries - Country information
        logger.info("🌍 Fetching country information...")
        country_data = self.rest_countries.fetch_country(country)
        if country_data:
            chunks = self.processor.process_country_data(country_data, city, country)
            all_chunks.extend(chunks)
            logger.info(f"✅ REST Countries: {len(chunks)} chunks")
        else:
            logger.warning(f"⚠️  REST Countries: No data found for {country}")

        # Additional data sources (optional based on API keys)
        self._collect_additional_data(city, country, all_chunks)

        logger.info(f"\n📊 Total chunks for {city}: {len(all_chunks)}")

        return all_chunks

    def _collect_additional_data(self, city: str, country: str, all_chunks: List[Dict]):
        """Collect data from additional sources (optional based on API keys)"""
        logger.info("\n🚀 Fetching additional data sources...")

        # Get coordinates for location-based APIs
        coords = None

        # 1. Google Places
        if self.google_places:
            logger.info("📍 Fetching Google Places...")
            try:
                places = self.google_places.search_places(f"tourist attractions in {city}")
                if places:
                    chunks = self.processor.process_google_places(places, city, country)
                    all_chunks.extend(chunks)
                    logger.info(f"✅ Google Places: {len(chunks)} chunks from {len(places)} places")
            except Exception as e:
                logger.error(f"❌ Google Places error: {e}")

        # 2. Foursquare
        if self.foursquare:
            logger.info("📍 Fetching Foursquare places...")
            try:
                # Try to get coords if we don't have them
                if not coords and self.geonames:
                    geo_data = self.geonames.search_city(city)
                    if geo_data and geo_data.get('lat'):
                        coords = {"lat": float(geo_data['lat']), "lon": float(geo_data['lng'])}

                if coords:
                    places = self.foursquare.search_places(
                        coords['lat'],
                        coords['lon'],
                        limit=50
                    )
                    if places:
                        chunks = self.processor.process_foursquare_places(places, city, country)
                        all_chunks.extend(chunks)
                        logger.info(f"✅ Foursquare: {len(chunks)} chunks from {len(places)} places")
            except Exception as e:
                logger.error(f"❌ Foursquare error: {e}")

        # 3. GeoNames - Geographic info
        if self.geonames:
            logger.info("🌍 Fetching GeoNames data...")
            try:
                geo_data = self.geonames.search_city(city)
                if geo_data:
                    # Save coords for other APIs
                    if not coords and geo_data.get('lat'):
                        coords = {"lat": float(geo_data['lat']), "lon": float(geo_data['lng'])}

                    chunks = self.processor.process_geonames_data(geo_data, city, country)
                    all_chunks.extend(chunks)
                    logger.info(f"✅ GeoNames: {len(chunks)} chunks")
            except Exception as e:
                logger.error(f"❌ GeoNames error: {e}")

        # 4. Wikidata - Structured attractions
        if hasattr(self, 'wikidata') and self.wikidata:
            logger.info("📚 Fetching Wikidata attractions...")
            try:
                attractions = self.wikidata.get_city_attractions(city)
                if attractions:
                    chunks = self.processor.process_wikidata_attractions(attractions, city, country)
                    all_chunks.extend(chunks)
                    logger.info(f"✅ Wikidata: {len(chunks)} chunks from {len(attractions)} attractions")
            except Exception as e:
                logger.error(f"❌ Wikidata error: {e}")

        # 5. OpenStreetMap - Community POIs
        if hasattr(self, 'osm') and self.osm:
            logger.info("🗺️  Fetching OpenStreetMap POIs...")
            try:
                if coords:
                    pois = self.osm.fetch_pois(coords['lat'], coords['lon'], radius=5000)
                    if pois:
                        chunks = self.processor.process_osm_pois(pois, city, country)
                        all_chunks.extend(chunks)
                        logger.info(f"✅ OpenStreetMap: {len(chunks)} chunks from {len(pois)} POIs")
            except Exception as e:
                logger.error(f"❌ OpenStreetMap error: {e}")

        # 6. WeatherAPI - Climate info
        if self.weather_api:
            logger.info("🌤️  Fetching weather data...")
            try:
                weather_data = self.weather_api.get_climate_data(city)
                if weather_data:
                    chunks = self.processor.process_weather_data(weather_data, city, country)
                    all_chunks.extend(chunks)
                    logger.info(f"✅ WeatherAPI: {len(chunks)} chunks")
            except Exception as e:
                logger.error(f"❌ WeatherAPI error: {e}")

        # 7. Zomato - Alternative restaurant data
        if self.zomato:
            logger.info("🍽️  Fetching Zomato restaurants...")
            try:
                restaurants = self.zomato.search_restaurants(city, limit=20)
                if restaurants:
                    # Reuse Yelp processor for restaurant data
                    chunks = self.processor.process_restaurant_data(restaurants, city, country)
                    all_chunks.extend(chunks)
                    logger.info(f"✅ Zomato: {len(chunks)} chunks from {len(restaurants)} restaurants")
            except Exception as e:
                logger.error(f"❌ Zomato error: {e}")

        # 8. Amadeus - Activities
        if self.amadeus:
            logger.info("✈️  Fetching Amadeus activities...")
            try:
                if coords:
                    activities = self.amadeus.get_points_of_interest(coords['lat'], coords['lon'])
                    if activities:
                        # Process as Google Places format (similar structure)
                        chunks = self.processor.process_google_places(activities, city, country)
                        all_chunks.extend(chunks)
                        logger.info(f"✅ Amadeus: {len(chunks)} chunks from {len(activities)} activities")
            except Exception as e:
                logger.error(f"❌ Amadeus error: {e}")

        # 9. Web Scrapers (use conservatively)
        self._collect_scraped_data(city, country, all_chunks)

    def _collect_scraped_data(self, city: str, country: str, all_chunks: List[Dict]):
        """Collect data from web scrapers"""
        logger.info("\n🕷️  Fetching web-scraped content...")

        # Generate slugs for different sites
        slugs = city_to_slug(city, country)

        # Lonely Planet
        if hasattr(self, 'lonely_planet') and self.lonely_planet:
            try:
                logger.info(f"📖 Scraping Lonely Planet for {city}...")
                lp_data = self.lonely_planet.scrape_city_guide(
                    slugs['lonely_planet']['city'],
                    slugs['lonely_planet']['country']
                )
                if lp_data:
                    chunks = self.processor.process_scraped_content(lp_data, city, country)
                    all_chunks.extend(chunks)
                    logger.info(f"✅ Lonely Planet: {len(chunks)} chunks")
            except Exception as e:
                logger.error(f"❌ Lonely Planet error: {e}")

        # Rick Steves
        if hasattr(self, 'rick_steves') and self.rick_steves:
            try:
                logger.info(f"📖 Scraping Rick Steves for {city}...")
                rs_data = self.rick_steves.scrape_destination(
                    slugs['rick_steves']['destination']
                )
                if rs_data:
                    chunks = self.processor.process_scraped_content(rs_data, city, country)
                    all_chunks.extend(chunks)
                    logger.info(f"✅ Rick Steves: {len(chunks)} chunks")
            except Exception as e:
                logger.error(f"❌ Rick Steves error: {e}")

        # Atlas Obscura
        if hasattr(self, 'atlas_obscura') and self.atlas_obscura:
            try:
                logger.info(f"🗿 Scraping Atlas Obscura for {city}...")
                ao_attractions = self.atlas_obscura.scrape_city_attractions(
                    slugs['atlas_obscura']['city']
                )
                if ao_attractions:
                    chunks = self.processor.process_scraped_attractions(ao_attractions, city, country)
                    all_chunks.extend(chunks)
                    logger.info(f"✅ Atlas Obscura: {len(chunks)} chunks from {len(ao_attractions)} attractions")
            except Exception as e:
                logger.error(f"❌ Atlas Obscura error: {e}")

        # Culture Trip
        if hasattr(self, 'culture_trip') and self.culture_trip:
            try:
                logger.info(f"🎨 Scraping Culture Trip for {city}...")
                ct_articles = self.culture_trip.search_city_articles(city)
                if ct_articles:
                    # Process as scraped attractions
                    chunks = self.processor.process_scraped_attractions(ct_articles, city, country)
                    all_chunks.extend(chunks)
                    logger.info(f"✅ Culture Trip: {len(chunks)} chunks from {len(ct_articles)} articles")
            except Exception as e:
                logger.error(f"❌ Culture Trip error: {e}")
    
    def process_and_store(self, chunks: List[Dict]) -> bool:
        """Generate embeddings and store chunks"""
        if not chunks:
            logger.warning("No chunks to process")
            return False
        
        logger.info(f"\n🔢 Generating embeddings for {len(chunks)} chunks...")
        
        # Extract texts
        texts = [chunk["text"] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embeddings.generate_embeddings(texts)
        
        # Count successful embeddings
        successful = sum(1 for e in embeddings if e is not None)
        logger.info(f"✅ Generated {successful}/{len(chunks)} embeddings")
        
        if successful == 0:
            logger.error("❌ No embeddings generated")
            return False
        
        # Store in vector database
        logger.info(f"\n💾 Storing in vector database...")
        success = self.vector_store.add_documents(chunks, embeddings)
        
        if success:
            logger.info(f"✅ Successfully stored documents")
        else:
            logger.error(f"❌ Failed to store documents")
        
        return success
    
    def collect_all_cities(self, cities: List[str] = None, skip_completed: bool = True):
        """Collect data for all cities"""
        if cities is None:
            cities = config.priority_cities
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 Starting data collection for {len(cities)} cities")
        logger.info(f"{'='*60}")
        logger.info(f"Skip completed: {skip_completed}")
        
        # Show progress
        stats = self.progress.get_stats()
        logger.info(f"📊 Progress: {stats['completed_count']} cities completed")
        if stats['completed_cities']:
            logger.info(f"   Completed: {', '.join(stats['completed_cities'][:5])}" +
                       (f" ... and {len(stats['completed_cities']) - 5} more" 
                        if len(stats['completed_cities']) > 5 else ""))
        
        successful = 0
        failed = 0
        skipped = 0
        
        for i, city in enumerate(cities, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing city {i}/{len(cities)}: {city}")
            logger.info(f"{'='*60}")
            
            # Check if already completed
            if skip_completed and self.progress.is_completed(city):
                logger.info(f"⏭️  Skipping {city} (already completed)")
                skipped += 1
                continue
            
            try:
                # Infer country
                country = self._infer_country(city)
                
                # Collect data
                chunks = self.collect_city_data(city, country)
                
                if chunks:
                    # Process and store
                    success = self.process_and_store(chunks)
                    
                    if success:
                        self.progress.mark_completed(city)
                        successful += 1
                        logger.info(f"✅ {city} completed successfully")
                    else:
                        failed += 1
                        logger.error(f"❌ {city} failed to store")
                else:
                    failed += 1
                    logger.error(f"❌ {city} - no data collected")
                
            except Exception as e:
                failed += 1
                logger.error(f"❌ Error processing {city}: {e}", exc_info=True)
        
        # Final summary
        logger.info(f"\n{'='*60}")
        logger.info(f"COLLECTION COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"✅ Successful: {successful}")
        logger.info(f"❌ Failed: {failed}")
        logger.info(f"⏭️  Skipped: {skipped}")
        logger.info(f"📊 Total: {successful + failed + skipped}")
        
        # Show vector store stats
        stats = self.vector_store.get_collection_stats()
        logger.info(f"\n📚 Vector Store Stats:")
        logger.info(f"   Collection: {stats.get('collection_name')}")
        logger.info(f"   Documents: {stats.get('document_count', 0):,}")
    
    def _infer_country(self, city: str) -> str:
        """Infer country from city name"""
        # City to country mapping
        country_mapping = {
            # Europe
            "Paris": "France",
            "London": "United Kingdom",
            "Rome": "Italy",
            "Barcelona": "Spain",
            "Amsterdam": "Netherlands",
            "Prague": "Czech Republic",
            "Vienna": "Austria",
            "Berlin": "Germany",
            "Munich": "Germany",
            "Venice": "Italy",
            "Florence": "Italy",
            "Athens": "Greece",
            "Dublin": "Ireland",
            "Edinburgh": "United Kingdom",
            "Lisbon": "Portugal",
            "Madrid": "Spain",
            "Copenhagen": "Denmark",
            "Stockholm": "Sweden",
            "Budapest": "Hungary",
            "Krakow": "Poland",
            
            # Asia
            "Tokyo": "Japan",
            "Bangkok": "Thailand",
            "Singapore": "Singapore",
            "Hong Kong": "Hong Kong",
            "Seoul": "South Korea",
            "Dubai": "United Arab Emirates",
            "Bali": "Indonesia",
            "Kyoto": "Japan",
            "Shanghai": "China",
            "Beijing": "China",
            "Taipei": "Taiwan",
            "Hanoi": "Vietnam",
            "Ho Chi Minh City": "Vietnam",
            "Kuala Lumpur": "Malaysia",
            "Manila": "Philippines",
            
            # Americas
            "New York": "United States",
            "Los Angeles": "United States",
            "San Francisco": "United States",
            "Miami": "United States",
            "Las Vegas": "United States",
            "Mexico City": "Mexico",
            "Cancun": "Mexico",
            "Rio de Janeiro": "Brazil",
            "Buenos Aires": "Argentina",
            "Vancouver": "Canada",
            
            # Oceania & Others
            "Sydney": "Australia",
            "Melbourne": "Australia",
            "Auckland": "New Zealand",
            "Istanbul": "Turkey",
            "Cairo": "Egypt",
            "Cape Town": "South Africa",
            "Marrakech": "Morocco",
            "Tel Aviv": "Israel",
            "Jerusalem": "Israel",
            "Mumbai": "India"
        }
        
        return country_mapping.get(city, "Unknown")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Collect RAG data for travel planning")
    parser.add_argument("--cities", nargs="+", help="Specific cities to process")
    parser.add_argument("--count", type=int, help="Number of cities to process")
    parser.add_argument("--skip-completed", action="store_true", default=True,
                       help="Skip already completed cities")
    parser.add_argument("--force", action="store_true", help="Force reprocess all cities")
    
    args = parser.parse_args()
    
    # Initialize collector
    try:
        collector = RAGDataCollector()
    except Exception as e:
        logger.error(f"Failed to initialize collector: {e}")
        logger.error("Make sure all services are running:")
        logger.error("  docker-compose -f docker-compose.backend.yml up -d")
        sys.exit(1)
    
    # Determine which cities to process
    cities = args.cities
    if not cities:
        cities = config.priority_cities
        if args.count:
            cities = cities[:args.count]
    
    skip_completed = args.skip_completed and not args.force
    
    # Start collection
    try:
        collector.collect_all_cities(cities, skip_completed=skip_completed)
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Interrupted by user")
        logger.info("Progress has been saved. Run again to continue.")
    except Exception as e:
        logger.error(f"\n\n❌ Collection failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()