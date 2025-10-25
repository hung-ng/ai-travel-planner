"""Data fetchers for RAG system"""
import requests
import time
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)




class WeatherAPIFetcher:
    """Fetch climate and weather data"""

    BASE_URL = "http://api.weatherapi.com/v1"

    def __init__(self, api_key: str, rate_limit_rpm: int = 100):
        """
        Initialize WeatherAPI fetcher

        Get API key: https://www.weatherapi.com/signup.aspx
        Free tier: 1M calls/month
        """
        self.api_key = api_key
        self.rate_limit = rate_limit_rpm
        self.last_request_time = 0

    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        min_interval = 60.0 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()

    def get_climate_data(self, city_name: str) -> Optional[Dict]:
        """
        Get climate averages for a city

        Returns monthly averages useful for travel planning
        """
        self._rate_limit()

        url = f"{self.BASE_URL}/current.json"
        params = {
            "key": self.api_key,
            "q": city_name,
            "aqi": "no"
        }

        try:
            logger.info(f"Fetching weather data for: {city_name}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            logger.info(f"✅ Got weather data for {city_name}")
            return data

        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return None



