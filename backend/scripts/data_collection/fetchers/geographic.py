"""Data fetchers for RAG system"""
import requests
import time
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)




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

class GeoNamesFetcher:
    """Fetch geographic data from GeoNames API"""

    BASE_URL = "http://api.geonames.org"

    def __init__(self, username: str, rate_limit_rpm: int = 100):
        """
        Initialize GeoNames fetcher

        Get username: http://www.geonames.org/login
        Free tier: 20,000 credits/day
        """
        self.username = username
        self.rate_limit = rate_limit_rpm
        self.last_request_time = 0

    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        min_interval = 60.0 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()

    def search_city(self, city_name: str) -> Optional[Dict]:
        """Get detailed city information"""
        self._rate_limit()

        url = f"{self.BASE_URL}/searchJSON"
        params = {
            "q": city_name,
            "maxRows": 1,
            "username": self.username,
            "featureClass": "P"  # Cities
        }

        try:
            logger.info(f"Fetching GeoNames data for: {city_name}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = data.get("geonames", [])
            if results:
                logger.info(f"✅ Found GeoNames data for {city_name}")
                return results[0]
            else:
                logger.warning(f"No GeoNames data for {city_name}")
                return None

        except Exception as e:
            logger.error(f"Error fetching GeoNames data: {e}")
            return None




class OpenTripMapFetcher:
    """Fetch POIs from OpenTripMap API"""
    
    BASE_URL = "https://api.opentripmap.com/0.1/en/places"
    
    # Fallback coordinates for major cities (when geocoding fails)
    CITY_COORDINATES = {
        "Paris": {"lat": 48.8566, "lon": 2.3522, "country": "France"},
        "London": {"lat": 51.5074, "lon": -0.1278, "country": "United Kingdom"},
        "Rome": {"lat": 41.9028, "lon": 12.4964, "country": "Italy"},
        "Barcelona": {"lat": 41.3851, "lon": 2.1734, "country": "Spain"},
        "Amsterdam": {"lat": 52.3676, "lon": 4.9041, "country": "Netherlands"},
        "Prague": {"lat": 50.0755, "lon": 14.4378, "country": "Czech Republic"},
        "Vienna": {"lat": 48.2082, "lon": 16.3738, "country": "Austria"},
        "Berlin": {"lat": 52.5200, "lon": 13.4050, "country": "Germany"},
        "Munich": {"lat": 48.1351, "lon": 11.5820, "country": "Germany"},
        "Venice": {"lat": 45.4408, "lon": 12.3155, "country": "Italy"},
        "Florence": {"lat": 43.7696, "lon": 11.2558, "country": "Italy"},
        "Athens": {"lat": 37.9838, "lon": 23.7275, "country": "Greece"},
        "Dublin": {"lat": 53.3498, "lon": -6.2603, "country": "Ireland"},
        "Edinburgh": {"lat": 55.9533, "lon": -3.1883, "country": "United Kingdom"},
        "Lisbon": {"lat": 38.7223, "lon": -9.1393, "country": "Portugal"},
        "Madrid": {"lat": 40.4168, "lon": -3.7038, "country": "Spain"},
        "Copenhagen": {"lat": 55.6761, "lon": 12.5683, "country": "Denmark"},
        "Stockholm": {"lat": 59.3293, "lon": 18.0686, "country": "Sweden"},
        "Budapest": {"lat": 47.4979, "lon": 19.0402, "country": "Hungary"},
        "Krakow": {"lat": 50.0647, "lon": 19.9450, "country": "Poland"},
        "Tokyo": {"lat": 35.6762, "lon": 139.6503, "country": "Japan"},
        "Bangkok": {"lat": 13.7563, "lon": 100.5018, "country": "Thailand"},
        "Singapore": {"lat": 1.3521, "lon": 103.8198, "country": "Singapore"},
        "Hong Kong": {"lat": 22.3193, "lon": 114.1694, "country": "Hong Kong"},
        "Seoul": {"lat": 37.5665, "lon": 126.9780, "country": "South Korea"},
        "Dubai": {"lat": 25.2048, "lon": 55.2708, "country": "United Arab Emirates"},
        "Bali": {"lat": -8.4095, "lon": 115.1889, "country": "Indonesia"},
        "Kyoto": {"lat": 35.0116, "lon": 135.7681, "country": "Japan"},
        "Shanghai": {"lat": 31.2304, "lon": 121.4737, "country": "China"},
        "Beijing": {"lat": 39.9042, "lon": 116.4074, "country": "China"},
        "Taipei": {"lat": 25.0330, "lon": 121.5654, "country": "Taiwan"},
        "Hanoi": {"lat": 21.0285, "lon": 105.8542, "country": "Vietnam"},
        "Ho Chi Minh City": {"lat": 10.8231, "lon": 106.6297, "country": "Vietnam"},
        "Kuala Lumpur": {"lat": 3.1390, "lon": 101.6869, "country": "Malaysia"},
        "Manila": {"lat": 14.5995, "lon": 120.9842, "country": "Philippines"},
        "New York": {"lat": 40.7128, "lon": -74.0060, "country": "United States"},
        "Los Angeles": {"lat": 34.0522, "lon": -118.2437, "country": "United States"},
        "San Francisco": {"lat": 37.7749, "lon": -122.4194, "country": "United States"},
        "Miami": {"lat": 25.7617, "lon": -80.1918, "country": "United States"},
        "Las Vegas": {"lat": 36.1699, "lon": -115.1398, "country": "United States"},
        "Mexico City": {"lat": 19.4326, "lon": -99.1332, "country": "Mexico"},
        "Cancun": {"lat": 21.1619, "lon": -86.8515, "country": "Mexico"},
        "Rio de Janeiro": {"lat": -22.9068, "lon": -43.1729, "country": "Brazil"},
        "Buenos Aires": {"lat": -34.6037, "lon": -58.3816, "country": "Argentina"},
        "Vancouver": {"lat": 49.2827, "lon": -123.1207, "country": "Canada"},
        "Sydney": {"lat": -33.8688, "lon": 151.2093, "country": "Australia"},
        "Melbourne": {"lat": -37.8136, "lon": 144.9631, "country": "Australia"},
        "Auckland": {"lat": -36.8485, "lon": 174.7633, "country": "New Zealand"},
        "Istanbul": {"lat": 41.0082, "lon": 28.9784, "country": "Turkey"},
        "Cairo": {"lat": 30.0444, "lon": 31.2357, "country": "Egypt"},
    }
    
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
        """Get coordinates for a city (with fallback)"""
        
        # First try fallback database
        if city_name in self.CITY_COORDINATES:
            coords = self.CITY_COORDINATES[city_name]
            logger.info(f"Using fallback coordinates for {city_name}: {coords['lat']}, {coords['lon']}")
            return {
                "lat": coords["lat"],
                "lon": coords["lon"],
                "country": coords["country"],
                "name": city_name
            }
        
        # Try API if not in fallback database
        self._rate_limit()
        
        url = f"{self.BASE_URL}/geoname"
        params = {
            "name": city_name,
            "apikey": self.api_key
        }
        
        try:
            logger.info(f"Attempting to geocode {city_name} via API...")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Debug: log the response
            logger.debug(f"Geocode response for {city_name}: {data}")
            
            if not data:
                logger.warning(f"Empty response from OpenTripMap geocoding for {city_name}")
                return None
            
            # Check if we got valid coordinates
            if "lat" not in data or "lon" not in data:
                logger.warning(f"No coordinates in response for {city_name}")
                logger.debug(f"Response data: {data}")
                return None
            
            logger.info(f"API geocoded {city_name}: {data.get('lat')}, {data.get('lon')}")
            
            return {
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "country": data.get("country"),
                "name": data.get("name", city_name)
            }
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error geocoding {city_name}: {e}")
            logger.error(f"Response: {e.response.text[:200]}")
            return None
        except Exception as e:
            logger.error(f"Error geocoding {city_name}: {e}")
            return None
    
    def fetch_pois(self, lat: float, lon: float, radius: int = 5000,
                    kinds: str = None) -> List[Dict]:
        """
        Fetch points of interest

        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius in meters (default 5000m = 5km)
            kinds: Category filter (default None = all categories)
                   Examples: "museums", "theatres", "restaurants", "historic"
                   Full list: https://opentripmap.io/catalog
        """
        self._rate_limit()

        url = f"{self.BASE_URL}/radius"

        params = {
            "lat": lat,
            "lon": lon,
            "radius": radius,
            "limit": 100,
            "apikey": self.api_key
        }

        # Only add kinds filter if specified (free tier works better without it)
        if kinds:
            params["kinds"] = kinds
        
        try:
            logger.info(f"Fetching POIs at {lat}, {lon} with radius {radius}m, kinds: {kinds}")
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Debug: log response type
            logger.debug(f"POI response type: {type(data)}")
            
            # Handle different response formats
            features = []
            if isinstance(data, list):
                features = data
            elif isinstance(data, dict):
                features = data.get("features", [])
            
            if not features:
                logger.warning(f"No POIs found at {lat}, {lon}")
                return []
            
            pois = []
            
            for feature in features:
                if isinstance(feature, dict):
                    # GeoJSON format
                    if "properties" in feature:
                        props = feature.get("properties", {})
                        coords = feature.get("geometry", {}).get("coordinates", [])
                        
                        poi_name = props.get("name")
                        if poi_name:  # Only add POIs with names
                            pois.append({
                                "name": poi_name,
                                "kinds": props.get("kinds", "").split(","),
                                "xid": props.get("xid"),
                                "lon": coords[0] if len(coords) > 0 else None,
                                "lat": coords[1] if len(coords) > 1 else None
                            })
                    # Simple format
                    else:
                        poi_name = feature.get("name")
                        if poi_name:  # Only add POIs with names
                            pois.append({
                                "name": poi_name,
                                "kinds": feature.get("kinds", "").split(","),
                                "xid": feature.get("xid"),
                                "lon": feature.get("point", {}).get("lon"),
                                "lat": feature.get("point", {}).get("lat")
                            })
            
            logger.info(f"Found {len(pois)} POIs with names")
            return pois
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching POIs: {e}")
            logger.error(f"Status code: {e.response.status_code}")
            logger.error(f"Response: {e.response.text[:200]}")
            return []
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



