"""
Fetchers package - All data source fetchers organized by category

Structure:
- base: Common utilities
- wiki: Wikipedia & Wikivoyage
- geographic: REST Countries, GeoNames, OpenTripMap
- places: Google Places, Foursquare, Wikidata, OSM, Amadeus
- restaurants: Yelp, Zomato
- weather: WeatherAPI
- scrapers: Web scrapers for travel sites
"""

# Import all fetchers for convenient access
from .wiki import WikipediaFetcher, WikivoyageFetcher
from .geographic import RESTCountriesFetcher, GeoNamesFetcher, OpenTripMapFetcher
from .places import GooglePlacesFetcher, FoursquareFetcher, WikidataFetcher, OverpassOSMFetcher, AmadeusFetcher
from .restaurants import YelpFetcher, ZomatoFetcher
from .weather import WeatherAPIFetcher
from .scrapers import (
    LonelyPlanetScraper, RickStevesScraper, AtlasObscuraScraper,
    CultureTripScraper, TripadvisorScraper, city_to_slug
)

__all__ = [
    # Wiki
    'WikipediaFetcher', 'WikivoyageFetcher',
    # Geographic
    'RESTCountriesFetcher', 'GeoNamesFetcher', 'OpenTripMapFetcher',
    # Places
    'GooglePlacesFetcher', 'FoursquareFetcher', 'WikidataFetcher',
    'OverpassOSMFetcher', 'AmadeusFetcher',
    # Restaurants
    'YelpFetcher', 'ZomatoFetcher',
    # Weather
    'WeatherAPIFetcher',
    # Scrapers
    'LonelyPlanetScraper', 'RickStevesScraper', 'AtlasObscuraScraper',
    'CultureTripScraper', 'TripadvisorScraper', 'city_to_slug'
]
