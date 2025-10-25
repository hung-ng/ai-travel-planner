"""Web scrapers for travel content"""
import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import Dict, List, Optional
from urllib.parse import quote, urljoin

logger = logging.getLogger(__name__)




class LonelyPlanetScraper:
    """
    Scrape travel guides from Lonely Planet

    Note: Check robots.txt and terms of service
    URL pattern: https://www.lonelyplanet.com/[country]/[city]
    """

    BASE_URL = "https://www.lonelyplanet.com"

    def __init__(self, rate_limit_rpm: int = 10):
        """
        Initialize Lonely Planet scraper

        Conservative rate limiting to respect the site
        """
        self.rate_limit = rate_limit_rpm
        self.last_request_time = 0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_request_time
        min_interval = 60.0 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()

    def scrape_city_guide(self, city_slug: str, country_slug: str) -> Optional[Dict]:
        """
        Scrape city guide

        Args:
            city_slug: URL slug for city (e.g., "paris")
            country_slug: URL slug for country (e.g., "france")
        """
        self._rate_limit()

        url = f"{self.BASE_URL}/{country_slug}/{city_slug}"

        try:
            logger.info(f"Scraping Lonely Planet: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title_elem = soup.find('h1')
            title = title_elem.get_text(strip=True) if title_elem else None

            # Extract introduction
            intro_elem = soup.find('div', class_='intro')
            intro = intro_elem.get_text(strip=True) if intro_elem else None

            # Extract main content sections
            sections = []
            content_divs = soup.find_all('div', class_=['content', 'article-body'])

            for div in content_divs:
                text = div.get_text(strip=True, separator='\n')
                if text and len(text) > 100:  # Only meaningful content
                    sections.append(text)

            if sections or intro:
                logger.info(f"✅ Scraped Lonely Planet guide for {city_slug}")
                return {
                    "source": "lonely_planet",
                    "title": title,
                    "intro": intro,
                    "sections": sections,
                    "url": url
                }
            else:
                logger.warning(f"No content found for {city_slug}")
                return None

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Lonely Planet guide not found: {url}")
            else:
                logger.error(f"HTTP error scraping Lonely Planet: {e}")
            return None
        except Exception as e:
            logger.error(f"Error scraping Lonely Planet: {e}")
            return None


class RickStevesScraper:
    """
    Scrape travel guides from Rick Steves

    Note: Check robots.txt and terms of service
    URL pattern: https://www.ricksteves.com/europe/[city]
    """

    BASE_URL = "https://www.ricksteves.com"

    def __init__(self, rate_limit_rpm: int = 10):
        self.rate_limit = rate_limit_rpm
        self.last_request_time = 0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        min_interval = 60.0 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()

    def scrape_destination(self, destination_slug: str, region: str = "europe") -> Optional[Dict]:
        """
        Scrape destination guide

        Args:
            destination_slug: URL slug (e.g., "paris", "rome")
            region: Geographic region (default: "europe")
        """
        self._rate_limit()

        url = f"{self.BASE_URL}/{region}/{destination_slug}"

        try:
            logger.info(f"Scraping Rick Steves: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title_elem = soup.find('h1')
            title = title_elem.get_text(strip=True) if title_elem else None

            # Extract main content
            sections = []

            # Look for article or main content areas
            article = soup.find('article') or soup.find('div', class_='content')

            if article:
                # Extract paragraphs
                paragraphs = article.find_all('p')
                text_blocks = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50]
                sections.extend(text_blocks)

            if sections:
                logger.info(f"✅ Scraped Rick Steves guide for {destination_slug}")
                return {
                    "source": "rick_steves",
                    "title": title,
                    "sections": sections,
                    "url": url
                }
            else:
                logger.warning(f"No content found for {destination_slug}")
                return None

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Rick Steves guide not found: {url}")
            else:
                logger.error(f"HTTP error scraping Rick Steves: {e}")
            return None
        except Exception as e:
            logger.error(f"Error scraping Rick Steves: {e}")
            return None


class AtlasObscuraScraper:
    """
    Scrape unusual attractions from Atlas Obscura

    Note: Check robots.txt and terms of service
    URL pattern: https://www.atlasobscura.com/things-to-do/[city]
    """

    BASE_URL = "https://www.atlasobscura.com"

    def __init__(self, rate_limit_rpm: int = 10):
        self.rate_limit = rate_limit_rpm
        self.last_request_time = 0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        min_interval = 60.0 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()

    def scrape_city_attractions(self, city_slug: str) -> List[Dict]:
        """
        Scrape unusual attractions for a city

        Args:
            city_slug: URL slug (e.g., "paris-france", "rome-italy")
        """
        self._rate_limit()

        url = f"{self.BASE_URL}/things-to-do/{city_slug}"

        try:
            logger.info(f"Scraping Atlas Obscura: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            attractions = []

            # Find attraction cards/listings
            # Note: Structure may vary, adjust selectors as needed
            items = soup.find_all(['div', 'article'], class_=lambda c: c and ('item' in c or 'place' in c or 'card' in c))

            for item in items[:20]:  # Limit to 20 attractions
                title_elem = item.find(['h3', 'h2', 'a'])
                desc_elem = item.find('p')

                if title_elem:
                    title = title_elem.get_text(strip=True)
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    link = title_elem.get('href') if title_elem.name == 'a' else None

                    if link and not link.startswith('http'):
                        link = urljoin(self.BASE_URL, link)

                    attractions.append({
                        "name": title,
                        "description": description,
                        "url": link,
                        "source": "atlas_obscura"
                    })

            if attractions:
                logger.info(f"✅ Scraped {len(attractions)} attractions from Atlas Obscura")
            else:
                logger.warning(f"No attractions found for {city_slug}")

            return attractions

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Atlas Obscura page not found: {url}")
            else:
                logger.error(f"HTTP error scraping Atlas Obscura: {e}")
            return []
        except Exception as e:
            logger.error(f"Error scraping Atlas Obscura: {e}")
            return []


class CultureTripScraper:
    """
    Scrape travel content from Culture Trip

    Note: Check robots.txt and terms of service
    URL pattern: https://theculturetrip.com/[region]/[country]/articles/[topic]
    """

    BASE_URL = "https://theculturetrip.com"

    def __init__(self, rate_limit_rpm: int = 10):
        self.rate_limit = rate_limit_rpm
        self.last_request_time = 0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        min_interval = 60.0 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()

    def search_city_articles(self, city_name: str) -> List[Dict]:
        """
        Search for articles about a city

        Args:
            city_name: City name for search
        """
        self._rate_limit()

        # Use search endpoint
        search_url = f"{self.BASE_URL}/search"
        params = {"q": city_name}

        try:
            logger.info(f"Scraping Culture Trip articles for: {city_name}")
            response = requests.get(search_url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            articles = []

            # Find article links
            # Note: Structure may vary, adjust selectors as needed
            links = soup.find_all('a', class_=lambda c: c and ('article' in c.lower() if c else False))[:10]

            for link in links:
                title = link.get_text(strip=True)
                href = link.get('href')

                if href and title:
                    if not href.startswith('http'):
                        href = urljoin(self.BASE_URL, href)

                    articles.append({
                        "title": title,
                        "url": href,
                        "source": "culture_trip"
                    })

            if articles:
                logger.info(f"✅ Found {len(articles)} Culture Trip articles")
            else:
                logger.warning(f"No Culture Trip articles found for {city_name}")

            return articles

        except Exception as e:
            logger.error(f"Error scraping Culture Trip: {e}")
            return []


class TripadvisorScraper:
    """
    Scrape attraction info from Tripadvisor

    Note: Tripadvisor has strict anti-scraping measures
    - Check robots.txt and terms of service
    - May require additional measures (proxies, etc.)
    - Consider using official API if available
    - For educational purposes only
    """

    BASE_URL = "https://www.tripadvisor.com"

    def __init__(self, rate_limit_rpm: int = 5):
        """Very conservative rate limiting"""
        self.rate_limit = rate_limit_rpm
        self.last_request_time = 0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }

    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        min_interval = 60.0 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()

    def search_attractions(self, city_name: str, country_code: str = None) -> List[Dict]:
        """
        Search for top attractions

        Args:
            city_name: City name
            country_code: Optional country code

        Note: This is a basic implementation. Tripadvisor may block or rate-limit.
        """
        self._rate_limit()

        # Build search query
        query = f"things to do in {city_name}"
        search_url = f"{self.BASE_URL}/Search"
        params = {"q": query}

        try:
            logger.info(f"Scraping Tripadvisor for: {city_name}")
            logger.warning("⚠️  Tripadvisor has anti-scraping measures. Use with caution.")

            response = requests.get(search_url, headers=self.headers, params=params, timeout=15)

            # Check for blocking
            if response.status_code == 403:
                logger.error("❌ Tripadvisor blocked the request (403 Forbidden)")
                return []

            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # This is a simplified example - actual structure varies
            attractions = []

            # Note: Selectors need to be updated based on current Tripadvisor HTML structure
            items = soup.find_all('div', class_=lambda c: c and 'attraction' in c.lower() if c else False)

            for item in items[:15]:
                name_elem = item.find(['h3', 'h2', 'a'])
                if name_elem:
                    name = name_elem.get_text(strip=True)
                    attractions.append({
                        "name": name,
                        "source": "tripadvisor"
                    })

            if attractions:
                logger.info(f"✅ Scraped {len(attractions)} Tripadvisor attractions")
            else:
                logger.warning("No Tripadvisor data extracted (may be blocked or structure changed)")

            return attractions

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error scraping Tripadvisor: {e}")
            return []
        except Exception as e:
            logger.error(f"Error scraping Tripadvisor: {e}")
            return []


# Helper functions for generating URL slugs

def city_to_slug(city_name: str, country_name: str = None) -> Dict[str, str]:
    """
    Convert city/country names to URL slugs for different sites

    Returns dict with slugs for different services
    """
    city_lower = city_name.lower().replace(" ", "-")
    country_lower = country_name.lower().replace(" ", "-") if country_name else ""

    # Site-specific slug mappings
    slug_map = {
        "lonely_planet": {
            "city": city_lower,
            "country": country_lower
        },
        "rick_steves": {
            "destination": city_lower
        },
        "atlas_obscura": {
            "city": f"{city_lower}-{country_lower}" if country_name else city_lower
        }
    }

    return slug_map

def city_to_slug(city_name: str, country_name: str = None) -> Dict[str, str]:
    """
    Convert city/country names to URL slugs for different sites

    Returns dict with slugs for different services
    """
    city_lower = city_name.lower().replace(" ", "-")
    country_lower = country_name.lower().replace(" ", "-") if country_name else ""

    # Site-specific slug mappings
    slug_map = {
        "lonely_planet": {
            "city": city_lower,
            "country": country_lower
        },
        "rick_steves": {
            "destination": city_lower
        },
        "atlas_obscura": {
            "city": f"{city_lower}-{country_lower}" if country_name else city_lower
        }
    }

    return slug_map