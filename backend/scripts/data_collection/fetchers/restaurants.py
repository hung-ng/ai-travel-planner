"""Data fetchers for RAG system"""
import requests
import time
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)




class YelpFetcher:
    """Fetch restaurant data from Yelp API"""
    
    BASE_URL = "https://api.yelp.com/v3"
    
    def __init__(self, api_key: str, rate_limit_rpm: int = 10):
        self.api_key = api_key
        self.rate_limit = rate_limit_rpm
        self.last_request_time = 0
        self.headers = {"Authorization": f"Bearer {api_key}"}
        
    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        min_interval = 60.0 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()
    
    def search_restaurants(self, location: str, limit: int = 50) -> List[Dict]:
        """Search for restaurants in a location"""
        if not self.api_key:
            logger.warning("Yelp API key not configured")
            return []
        
        self._rate_limit()
        
        url = f"{self.BASE_URL}/businesses/search"
        params = {
            "location": location,
            "categories": "restaurants",
            "limit": min(limit, 50),  # Yelp max is 50
            "sort_by": "rating"
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            businesses = []
            for biz in data.get("businesses", []):
                businesses.append({
                    "name": biz.get("name"),
                    "rating": biz.get("rating"),
                    "review_count": biz.get("review_count"),
                    "price": biz.get("price"),
                    "categories": [cat["title"] for cat in biz.get("categories", [])],
                    "location": biz.get("location", {}).get("display_address", []),
                    "url": biz.get("url")
                })
            
            logger.info(f"Found {len(businesses)} restaurants")
            return businesses
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching Yelp data for {location}: {e}")
            logger.error(f"Status code: {e.response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Error fetching Yelp data for {location}: {e}")
            return []




class ZomatoFetcher:
    """Fetch restaurant data from Zomato API"""

    BASE_URL = "https://developers.zomato.com/api/v2.1"

    def __init__(self, api_key: str, rate_limit_rpm: int = 100):
        """
        Initialize Zomato fetcher

        Get API key: https://developers.zomato.com/api
        Note: Zomato API may have limited access - check availability
        """
        self.api_key = api_key
        self.rate_limit = rate_limit_rpm
        self.last_request_time = 0
        self.headers = {
            "user-key": api_key,
            "Accept": "application/json"
        }

    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        min_interval = 60.0 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()

    def search_restaurants(self, city_name: str, limit: int = 20) -> List[Dict]:
        """Search for restaurants in a city"""
        self._rate_limit()

        # First, get city ID
        city_url = f"{self.BASE_URL}/cities"
        city_params = {"q": city_name}

        try:
            logger.info(f"Fetching Zomato restaurants for: {city_name}")

            # Get city ID
            response = requests.get(city_url, headers=self.headers, params=city_params, timeout=10)
            response.raise_for_status()
            city_data = response.json()

            cities = city_data.get("location_suggestions", [])
            if not cities:
                logger.warning(f"City not found in Zomato: {city_name}")
                return []

            city_id = cities[0]["id"]

            # Search restaurants
            search_url = f"{self.BASE_URL}/search"
            search_params = {
                "entity_id": city_id,
                "entity_type": "city",
                "count": limit,
                "sort": "rating"
            }

            response = requests.get(search_url, headers=self.headers, params=search_params, timeout=10)
            response.raise_for_status()
            data = response.json()

            restaurants = data.get("restaurants", [])
            logger.info(f"✅ Found {len(restaurants)} restaurants from Zomato")
            return restaurants

        except Exception as e:
            logger.error(f"Error fetching Zomato restaurants: {e}")
            return []



