"""Data fetchers for RAG system"""
import requests
import time
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)




class GooglePlacesFetcher:
    """Fetch POIs from Google Places API"""

    BASE_URL = "https://maps.googleapis.com/maps/api/place"

    def __init__(self, api_key: str, rate_limit_rpm: int = 100):
        """
        Initialize Google Places fetcher

        Get API key: https://console.cloud.google.com/apis/credentials
        Free tier: $200 credit per month
        """
        self.api_key = api_key
        self.rate_limit = rate_limit_rpm
        self.last_request_time = 0

    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_request_time
        min_interval = 60.0 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()

    def search_places(self, query: str, location: Dict = None) -> List[Dict]:
        """
        Search for places

        Args:
            query: Search query (e.g., "tourist attractions in Paris")
            location: Optional dict with lat/lng
        """
        self._rate_limit()

        url = f"{self.BASE_URL}/textsearch/json"
        params = {
            "query": query,
            "key": self.api_key
        }

        if location:
            params["location"] = f"{location['lat']},{location['lng']}"
            params["radius"] = 5000

        try:
            logger.info(f"Fetching Google Places for: {query}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "OK":
                results = data.get("results", [])
                logger.info(f"✅ Found {len(results)} places from Google")
                return results
            else:
                logger.warning(f"Google Places API error: {data.get('status')}")
                return []

        except Exception as e:
            logger.error(f"Error fetching Google Places: {e}")
            return []


class FoursquareFetcher:
    """Fetch POIs from Foursquare Places API"""

    BASE_URL = "https://api.foursquare.com/v3/places"

    def __init__(self, api_key: str, rate_limit_rpm: int = 50):
        """
        Initialize Foursquare fetcher

        Get API key: https://foursquare.com/developers/signup
        Free tier: 50,000 calls/month
        """
        self.api_key = api_key
        self.rate_limit = rate_limit_rpm
        self.last_request_time = 0
        self.headers = {
            "Authorization": api_key,
            "Accept": "application/json"
        }

    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        min_interval = 60.0 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()

    def search_places(self, lat: float, lon: float, categories: str = None, limit: int = 50) -> List[Dict]:
        """
        Search for places near location

        Args:
            lat: Latitude
            lon: Longitude
            categories: Category IDs (e.g., "16000" for landmarks)
            limit: Max results
        """
        self._rate_limit()

        url = f"{self.BASE_URL}/search"
        params = {
            "ll": f"{lat},{lon}",
            "limit": limit,
            "radius": 5000
        }

        if categories:
            params["categories"] = categories

        try:
            logger.info(f"Fetching Foursquare places at {lat}, {lon}")
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            logger.info(f"✅ Found {len(results)} places from Foursquare")
            return results

        except Exception as e:
            logger.error(f"Error fetching Foursquare places: {e}")
            return []




class WikidataFetcher:
    """Fetch structured data from Wikidata"""

    BASE_URL = "https://www.wikidata.org/w/api.php"
    SPARQL_URL = "https://query.wikidata.org/sparql"

    def __init__(self, rate_limit_rpm: int = 100):
        """
        Initialize Wikidata fetcher

        No API key required - free to use
        """
        self.rate_limit = rate_limit_rpm
        self.last_request_time = 0
        self.headers = {
            "User-Agent": "AI-Travel-Planner/1.0 (Educational Project)"
        }

    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        min_interval = 60.0 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()

    def get_city_attractions(self, city_name: str) -> List[Dict]:
        """
        Get tourist attractions for a city using SPARQL query
        """
        self._rate_limit()

        # SPARQL query to find tourist attractions in the city
        query = f"""
        SELECT ?attraction ?attractionLabel ?description WHERE {{
          ?attraction wdt:P31/wdt:P279* wd:Q570116;  # tourist attraction
                      wdt:P131* ?city.
          ?city rdfs:label "{city_name}"@en.
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
          OPTIONAL {{ ?attraction schema:description ?description. FILTER(LANG(?description) = "en") }}
        }}
        LIMIT 50
        """

        try:
            logger.info(f"Fetching Wikidata attractions for: {city_name}")
            response = requests.get(
                self.SPARQL_URL,
                headers=self.headers,
                params={"query": query, "format": "json"},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            results = data.get("results", {}).get("bindings", [])
            logger.info(f"✅ Found {len(results)} attractions from Wikidata")
            return results

        except Exception as e:
            logger.error(f"Error fetching Wikidata attractions: {e}")
            return []




class OverpassOSMFetcher:
    """Fetch POIs from OpenStreetMap using Overpass API"""

    BASE_URL = "https://overpass-api.de/api/interpreter"

    def __init__(self, rate_limit_rpm: int = 30):
        """
        Initialize Overpass API fetcher

        No API key required - free to use
        Rate limit: Be conservative, shared public instance
        """
        self.rate_limit = rate_limit_rpm
        self.last_request_time = 0

    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        min_interval = 60.0 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()

    def fetch_pois(self, lat: float, lon: float, radius: int = 5000, tags: List[str] = None) -> List[Dict]:
        """
        Fetch POIs from OSM

        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius in meters
            tags: OSM tags to search (e.g., ["tourism", "historic"])
        """
        self._rate_limit()

        if tags is None:
            tags = ["tourism", "historic", "attraction"]

        # Build Overpass QL query
        tag_filters = "|".join(tags)
        query = f"""
        [out:json][timeout:25];
        (
          node[{tag_filters}](around:{radius},{lat},{lon});
          way[{tag_filters}](around:{radius},{lat},{lon});
        );
        out body;
        """

        try:
            logger.info(f"Fetching OSM POIs at {lat}, {lon} with tags: {tags}")
            response = requests.post(
                self.BASE_URL,
                data={"data": query},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            elements = data.get("elements", [])
            logger.info(f"✅ Found {len(elements)} POIs from OSM")
            return elements

        except Exception as e:
            logger.error(f"Error fetching OSM POIs: {e}")
            return []




class AmadeusFetcher:
    """Fetch travel data from Amadeus API"""

    BASE_URL = "https://test.api.amadeus.com/v1"  # Test environment
    # For production: https://api.amadeus.com/v1

    def __init__(self, api_key: str, api_secret: str, rate_limit_rpm: int = 50):
        """
        Initialize Amadeus fetcher

        Get API credentials: https://developers.amadeus.com/register
        Free tier: Test environment with limited data
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.rate_limit = rate_limit_rpm
        self.last_request_time = 0
        self.access_token = None
        self.token_expiry = 0

    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        min_interval = 60.0 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()

    def _get_access_token(self) -> str:
        """Get OAuth access token"""
        if self.access_token and time.time() < self.token_expiry:
            return self.access_token

        url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret
        }

        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            token_data = response.json()

            self.access_token = token_data["access_token"]
            self.token_expiry = time.time() + token_data["expires_in"] - 60  # Refresh 1min early

            return self.access_token

        except Exception as e:
            logger.error(f"Error getting Amadeus token: {e}")
            return None

    def get_points_of_interest(self, lat: float, lon: float, radius: int = 5) -> List[Dict]:
        """
        Get points of interest near location

        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius in km
        """
        self._rate_limit()

        token = self._get_access_token()
        if not token:
            return []

        url = f"{self.BASE_URL}/shopping/activities"
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "latitude": lat,
            "longitude": lon,
            "radius": radius
        }

        try:
            logger.info(f"Fetching Amadeus POIs at {lat}, {lon}")
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = data.get("data", [])
            logger.info(f"✅ Found {len(results)} POIs from Amadeus")
            return results

        except Exception as e:
            logger.error(f"Error fetching Amadeus POIs: {e}")
            return []

