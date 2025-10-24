"""
Fetch data from various APIs
"""
import requests
import time
import json
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class WikipediaFetcher:
    """Fetch data from Wikipedia API"""
    
    BASE_URL = "https://en.wikipedia.org/w/api.php"
    
    def __init__(self, rate_limit_rpm: int = 200):
        self.rate_limit = rate_limit_rpm
        self.last_request_time = 0
        
    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_request_time
        min_interval = 60.0 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()
    
    def fetch_article(self, city_name: str) -> Optional[Dict]:
        """Fetch Wikipedia article for a city"""
        self._rate_limit()
        
        params = {
            "action": "query",
            "format": "json",
            "titles": city_name,
            "prop": "extracts|info|categories",
            "explaintext": True,
            "inprop": "url",
            "redirects": 1
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get("query", {}).get("pages", {})
            page = next(iter(pages.values()))
            
            if "missing" in page:
                logger.warning(f"Wikipedia article not found for: {city_name}")
                return None
            
            return {
                "title": page.get("title"),
                "url": page.get("fullurl"),
                "extract": page.get("extract"),
                "categories": [cat["title"] for cat in page.get("categories", [])]
            }
            
        except Exception as e:
            logger.error(f"Error fetching Wikipedia article for {city_name}: {e}")
            return None
    
    def fetch_article_sections(self, city_name: str) -> Optional[Dict]:
        """Fetch Wikipedia article with sections"""
        self._rate_limit()
        
        params = {
            "action": "parse",
            "format": "json",
            "page": city_name,
            "prop": "sections|text",
            "redirects": 1
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                logger.warning(f"Wikipedia sections not found for: {city_name}")
                return None
            
            parse_data = data.get("parse", {})
            
            return {
                "title": parse_data.get("title"),
                "sections": parse_data.get("sections", []),
                "text": parse_data.get("text", {}).get("*", "")
            }
            
        except Exception as e:
            logger.error(f"Error fetching sections for {city_name}: {e}")
            return None


class WikivoyageFetcher:
    """Fetch data from Wikivoyage API"""
    
    BASE_URL = "https://en.wikivoyage.org/w/api.php"
    
    def __init__(self, rate_limit_rpm: int = 200):
        self.rate_limit = rate_limit_rpm
        self.last_request_time = 0
        
    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        min_interval = 60.0 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()
    
    def fetch_guide(self, city_name: str) -> Optional[Dict]:
        """Fetch Wikivoyage travel guide"""
        self._rate_limit()
        
        params = {
            "action": "query",
            "format": "json",
            "titles": city_name,
            "prop": "extracts",
            "explaintext": True,
            "redirects": 1
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get("query", {}).get("pages", {})
            page = next(iter(pages.values()))
            
            if "missing" in page:
                logger.warning(f"Wikivoyage guide not found for: {city_name}")
                return None
            
            return {
                "title": page.get("title"),
                "content": page.get("extract")
            }
            
        except Exception as e:
            logger.error(f"Error fetching Wikivoyage for {city_name}: {e}")
            return None


class OpenTripMapFetcher:
    """Fetch POIs from OpenTripMap API"""
    
    BASE_URL = "https://api.opentripmap.com/0.1/en/places"
    
    def __init__(self, api_key: str, rate_limit_rpm: int = 50):
        self.api_key = api_key
        self.rate_limit = rate_limit_rpm
        self.last_request_time = 0
        
    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        min_interval = 60.0 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()
    
    def geocode(self, city_name: str) -> Optional[Dict]:
        """Get coordinates for a city"""
        self._rate_limit()
        
        url = f"{self.BASE_URL}/geoname"
        params = {
            "name": city_name,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "country": data.get("country"),
                "name": data.get("name")
            }
            
        except Exception as e:
            logger.error(f"Error geocoding {city_name}: {e}")
            return None
    
    def fetch_pois(self, lat: float, lon: float, radius: int = 5000, 
                    kinds: str = "museums,attractions,tourist_facilities") -> List[Dict]:
        """Fetch points of interest"""
        self._rate_limit()
        
        url = f"{self.BASE_URL}/radius"
        params = {
            "radius": radius,
            "lon": lon,
            "lat": lat,
            "kinds": kinds,
            "limit": 100,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            features = data.get("features", [])
            pois = []
            
            for feature in features:
                props = feature.get("properties", {})
                coords = feature.get("geometry", {}).get("coordinates", [])
                
                pois.append({
                    "name": props.get("name"),
                    "kinds": props.get("kinds", "").split(","),
                    "xid": props.get("xid"),
                    "lon": coords[0] if len(coords) > 0 else None,
                    "lat": coords[1] if len(coords) > 1 else None
                })
            
            return pois
            
        except Exception as e:
            logger.error(f"Error fetching POIs: {e}")
            return []
    
    def fetch_poi_details(self, xid: str) -> Optional[Dict]:
        """Fetch detailed information for a POI"""
        self._rate_limit()
        
        url = f"{self.BASE_URL}/xid/{xid}"
        params = {"apikey": self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching POI details for {xid}: {e}")
            return None


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
            "limit": limit,
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
            
            return businesses
            
        except Exception as e:
            logger.error(f"Error fetching Yelp data for {location}: {e}")
            return []


class RESTCountriesFetcher:
    """Fetch country data from REST Countries API"""
    
    BASE_URL = "https://restcountries.com/v3.1"
    
    def fetch_country(self, country_name: str) -> Optional[Dict]:
        """Fetch country information"""
        url = f"{self.BASE_URL}/name/{country_name}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data:
                country = data[0]
                return {
                    "name": country.get("name", {}).get("common"),
                    "capital": country.get("capital", [None])[0],
                    "region": country.get("region"),
                    "subregion": country.get("subregion"),
                    "population": country.get("population"),
                    "area": country.get("area"),
                    "languages": list(country.get("languages", {}).values()),
                    "currencies": list(country.get("currencies", {}).keys()),
                    "timezones": country.get("timezones", [])
                }
            
        except Exception as e:
            logger.error(f"Error fetching country data for {country_name}: {e}")
            return None