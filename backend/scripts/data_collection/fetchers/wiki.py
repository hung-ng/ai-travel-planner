"""Data fetchers for RAG system"""
import requests
import time
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)




class WikipediaFetcher:
    """Fetch data from Wikipedia API"""
    
    BASE_URL = "https://en.wikipedia.org/w/api.php"
    
    def __init__(self, rate_limit_rpm: int = 200):
        self.rate_limit = rate_limit_rpm
        self.last_request_time = 0
        
        # User-Agent is REQUIRED by Wikipedia API
        self.headers = {
            'User-Agent': 'AI-Travel-Planner/1.0 (Educational Project; Python/requests)'
        }
        
    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_request_time
        min_interval = 60.0 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()
    
    def search_articles(self, query: str, limit: int = 10) -> List[str]:
        """
        Search Wikipedia for articles matching query

        Returns list of article titles
        """
        self._rate_limit()

        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
            "srprop": "snippet"
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            results = data.get("query", {}).get("search", [])
            titles = [result["title"] for result in results]

            logger.info(f"Found {len(titles)} articles for query: '{query}'")
            return titles

        except Exception as e:
            logger.error(f"Error searching Wikipedia for '{query}': {e}")
            return []

    def fetch_article(self, city_name: str) -> Optional[Dict]:
        """Fetch Wikipedia article for a city"""
        self._rate_limit()

        params = {
            "action": "query",
            "format": "json",
            "titles": city_name,
            "prop": "extracts|info",
            "explaintext": True,
            "exintro": False,  # Get full article, not just intro
            "redirects": 1
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            pages = data.get("query", {}).get("pages", {})
            page = next(iter(pages.values()))

            if "missing" in page:
                logger.warning(f"Wikipedia article not found for: {city_name}")
                return None

            return {
                "title": page.get("title"),
                "url": f"https://en.wikipedia.org/wiki/{page.get('title', '').replace(' ', '_')}",
                "extract": page.get("extract"),
            }

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching Wikipedia for {city_name}: {e}")
            logger.error(f"Status code: {e.response.status_code}")
            if e.response.status_code == 403:
                logger.error("Wikipedia is blocking requests. This is usually due to:")
                logger.error("  1. Missing or invalid User-Agent header")
                logger.error("  2. Too many requests (rate limiting)")
                logger.error("  3. IP address blocked")
            return None
        except Exception as e:
            logger.error(f"Error fetching Wikipedia article for {city_name}: {e}")
            return None

    def fetch_multiple_articles(self, city_name: str) -> List[Dict]:
        """
        Fetch multiple related articles for a city

        Fetches:
        1. Main city article
        2. Top attractions (from search)
        3. Transportation article
        """
        articles = []

        # 1. Main city article
        logger.info(f"Fetching main article for {city_name}...")
        main_article = self.fetch_article(city_name)
        if main_article:
            articles.append(main_article)

        # 2. Search for attractions
        logger.info(f"Searching for attractions in {city_name}...")
        attraction_queries = [
            f"{city_name} attractions",
            f"{city_name} landmarks",
            f"museums in {city_name}",
        ]

        found_titles = set()
        for query in attraction_queries:
            titles = self.search_articles(query, limit=5)
            # Filter to avoid duplicates and the main city article
            for title in titles:
                if title not in found_titles and title != city_name:
                    found_titles.add(title)
                    if len(found_titles) >= 5:  # Limit to top 5 attractions
                        break
            if len(found_titles) >= 5:
                break

        # Fetch the attraction articles
        for title in list(found_titles)[:5]:
            logger.info(f"Fetching article: {title}")
            article = self.fetch_article(title)
            if article:
                articles.append(article)

        # 3. Try to fetch transportation article
        transport_title = f"{city_name} Metro"
        if city_name not in ["Singapore", "Dubai"]:  # Some cities don't have metro
            logger.info(f"Fetching transportation article...")
            transport_article = self.fetch_article(transport_title)
            if transport_article:
                articles.append(transport_article)

        logger.info(f"✅ Fetched {len(articles)} Wikipedia articles for {city_name}")
        return articles


class WikivoyageFetcher:
    """Fetch data from Wikivoyage API"""
    
    BASE_URL = "https://en.wikivoyage.org/w/api.php"
    
    def __init__(self, rate_limit_rpm: int = 200):
        self.rate_limit = rate_limit_rpm
        self.last_request_time = 0
        
        # User-Agent is REQUIRED
        self.headers = {
            'User-Agent': 'AI-Travel-Planner/1.0 (Educational Project; Python/requests)'
        }
        
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
            "exintro": False,  # Get full guide
            "redirects": 1
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                headers=self.headers,
                timeout=30
            )
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

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching Wikivoyage for {city_name}: {e}")
            logger.error(f"Status code: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Error fetching Wikivoyage for {city_name}: {e}")
            return None

    def fetch_multiple_guides(self, city_name: str) -> List[Dict]:
        """
        Fetch multiple Wikivoyage guides for a city

        Fetches:
        1. Main city guide
        2. District/neighborhood guides (e.g., "Paris/Montmartre")
        3. Topic guides (e.g., "Paris/Get around")
        """
        guides = []

        # 1. Main city guide
        logger.info(f"Fetching main Wikivoyage guide for {city_name}...")
        main_guide = self.fetch_guide(city_name)
        if main_guide:
            guides.append(main_guide)

        # 2. Common district naming patterns for Wikivoyage
        # Wikivoyage uses format: "CityName/DistrictName"
        common_districts = {
            "Paris": ["Montmartre", "Le Marais", "Latin Quarter", "Champs-Élysées"],
            "London": ["Westminster", "City of London", "Camden", "Kensington"],
            "Rome": ["Centro Storico", "Trastevere", "Vatican"],
            "Barcelona": ["Gothic Quarter", "Eixample", "Gràcia"],
            "Amsterdam": ["Centrum", "Jordaan", "De Pijp"],
            "Tokyo": ["Shinjuku", "Shibuya", "Asakusa", "Ginza"],
            "New York": ["Manhattan", "Brooklyn", "Queens"],
            "Berlin": ["Mitte", "Kreuzberg", "Charlottenburg"],
        }

        districts = common_districts.get(city_name, [])
        for district in districts[:3]:  # Limit to 3 districts
            district_title = f"{city_name}/{district}"
            logger.info(f"Fetching district guide: {district_title}")
            district_guide = self.fetch_guide(district_title)
            if district_guide:
                guides.append(district_guide)

        # 3. Topic guides (common across all cities)
        topics = ["Get around", "Eat", "Sleep", "See"]
        for topic in topics[:2]:  # Limit to 2 topics
            topic_title = f"{city_name}/{topic}"
            logger.info(f"Fetching topic guide: {topic_title}")
            topic_guide = self.fetch_guide(topic_title)
            if topic_guide:
                guides.append(topic_guide)

        logger.info(f"✅ Fetched {len(guides)} Wikivoyage guides for {city_name}")
        return guides



