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
sys.path.append(str(Path(__file__).parent.parent))

from scripts.config import config
from scripts.data_fetchers import (
    WikipediaFetcher, WikivoyageFetcher, OpenTripMapFetcher,
    YelpFetcher, RESTCountriesFetcher
)
from scripts.data_processors import DataProcessor
from scripts.embeddings_generator import EmbeddingsGenerator
from scripts.vector_store import VectorStore

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
        self.progress_file = progress_file
        self.progress = self._load_progress()
    
    def _load_progress(self) -> Dict:
        """Load progress from file"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {"completed_cities": [], "last_updated": None}
    
    def _save_progress(self):
        """Save progress to file"""
        os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
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
        # Initialize components
        self.wikipedia = WikipediaFetcher(config.wikipedia_rpm)
        self.wikivoyage = WikivoyageFetcher(config.wikipedia_rpm)
        self.processor = DataProcessor(config.chunk_size_words, config.overlap_words)
        self.embeddings = EmbeddingsGenerator(config.openai_api_key, config.embedding_model)
        self.vector_store = VectorStore(config.chroma_url, config.collection_name)
        self.progress = ProgressTracker(config.progress_file)
        
        # Optional fetchers
        self.opentripmap = None
        if config.opentripmap_api_key:
            self.opentripmap = OpenTripMapFetcher(config.opentripmap_api_key, config.opentripmap_rpm)
        
        self.yelp = None
        if config.yelp_api_key:
            self.yelp = YelpFetcher(config.yelp_api_key, config.yelp_rpm)
        
        self.rest_countries = RESTCountriesFetcher()
        
        # Create directories
        os.makedirs(config.raw_data_path, exist_ok=True)
        os.makedirs(config.processed_data_path, exist_ok=True)
        
        logger.info("RAG Data Collector initialized")
    
    def collect_city_data(self, city: str, country: str) -> List[Dict]:
        """Collect all data for a city"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Collecting data for: {city}, {country}")
        logger.info(f"{'='*60}")
        
        all_chunks = []
        
        # 1. Wikipedia
        logger.info("Fetching Wikipedia article...")
        wiki_data = self.wikipedia.fetch_article(city)
        if wiki_data:
            chunks = self.processor.process_wikipedia_article(wiki_data, city, country)
            all_chunks.extend(chunks)
            logger.info(f"✅ Wikipedia: {len(chunks)} chunks")
        else:
            logger.warning(f"⚠️  Wikipedia: No data")
        
        # 2. Wikivoyage
        logger.info("Fetching Wikivoyage guide...")
        wikivoyage_data = self.wikivoyage.fetch_guide(city)
        if wikivoyage_data:
            chunks = self.processor.process_wikivoyage_guide(wikivoyage_data, city, country)
            all_chunks.extend(chunks)
            logger.info(f"✅ Wikivoyage: {len(chunks)} chunks")
        else:
            logger.warning(f"⚠️  Wikivoyage: No data")
        
        # 3. OpenTripMap POIs
        if self.opentripmap:
            logger.info("Fetching OpenTripMap POIs...")
            coords = self.opentripmap.geocode(city)
            if coords:
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
            logger.info("Fetching Yelp restaurants...")
            restaurants = self.yelp.search_restaurants(f"{city}, {country}", limit=50)
            if restaurants:
                chunks = self.processor.process_restaurant_data(restaurants, city, country)
                all_chunks.extend(chunks)
                logger.info(f"✅ Yelp: {len(chunks)} chunks from {len(restaurants)} restaurants")
            else:
                logger.warning(f"⚠️  Yelp: No restaurants found")
        
        logger.info(f"\n📊 Total chunks for {city}: {len(all_chunks)}")
        
        return all_chunks
    
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
        
        # Store in vector database
        logger.info(f"\n💾 Storing in vector database...")
        success = self.vector_store.add_documents(chunks, embeddings)
        
        if success:
            logger.info(f"✅ Successfully stored {successful} documents")
        else:
            logger.error(f"❌ Failed to store documents")
        
        return success
    
    def collect_all_cities(self, cities: List[str] = None, skip_completed: bool = True):
        """Collect data for all cities"""
        if cities is None:
            cities = config.priority_cities
        
        logger.info(f"\n🚀 Starting data collection for {len(cities)} cities")
        logger.info(f"Skip completed: {skip_completed}")
        
        # Show progress
        stats = self.progress.get_stats()
        logger.info(f"📊 Progress: {stats['completed_count']} cities completed")
        
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
                # Infer country (simple approach - improve this)
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
        logger.info(f"   Documents: {stats.get('document_count'):,}")
    
    def _infer_country(self, city: str) -> str:
        """Simple country inference - improve this with a proper mapping"""
        # This is a simplified version - you should use a proper city->country mapping
        country_mapping = {
            "Paris": "France",
            "London": "United Kingdom",
            "Rome": "Italy",
            "Barcelona": "Spain",
            "Amsterdam": "Netherlands",
            "Tokyo": "Japan",
            "New York": "United States",
            # Add more mappings...
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
    collector = RAGDataCollector()
    
    # Determine which cities to process
    cities = args.cities
    if not cities:
        cities = config.priority_cities
        if args.count:
            cities = cities[:args.count]
    
    skip_completed = args.skip_completed and not args.force
    
    # Start collection
    collector.collect_all_cities(cities, skip_completed=skip_completed)


if __name__ == "__main__":
    main()