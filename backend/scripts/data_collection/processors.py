"""
Process and chunk raw data
"""
import re
from typing import List, Dict
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class TextCleaner:
    """Clean and normalize text"""
    
    @staticmethod
    def clean_html(html_text: str) -> str:
        """Remove HTML tags and clean text"""
        if not html_text:
            return ""
        
        soup = BeautifulSoup(html_text, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        text = soup.get_text()
        
        # Clean up whitespace
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize plain text"""
        if not text:
            return ""
        
        # Remove multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove excessive whitespace
        text = re.sub(r' +', ' ', text)
        
        # Remove citation markers like [1], [citation needed]
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'\[citation needed\]', '', text)
        
        # Remove wiki markup remnants
        text = re.sub(r'\{\{.*?\}\}', '', text)
        
        return text.strip()
    
    @staticmethod
    def extract_sections(text: str) -> Dict[str, str]:
        """Extract sections from text based on headers"""
        sections = {}
        current_section = "introduction"
        current_text = []
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a header (all caps or ends with ==)
            if line.isupper() or (line.startswith('==') and line.endswith('==')):
                # Save previous section
                if current_text:
                    sections[current_section] = '\n'.join(current_text).strip()
                
                # Start new section
                current_section = line.replace('=', '').strip().lower()
                current_text = []
            else:
                current_text.append(line)
        
        # Save last section
        if current_text:
            sections[current_section] = '\n'.join(current_text).strip()
        
        return sections


class TextChunker:
    """Chunk text into smaller pieces"""
    
    def __init__(self, chunk_size_words: int = 800, overlap_words: int = 100):
        self.chunk_size = chunk_size_words
        self.overlap = overlap_words
    
    def count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    def chunk_by_paragraphs(self, text: str, topic: str = "general") -> List[Dict]:
        """Chunk text by paragraphs, respecting chunk size"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for para in paragraphs:
            para_word_count = self.count_words(para)
            
            # If single paragraph is too large, split it
            if para_word_count > self.chunk_size:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append({
                        "text": '\n\n'.join(current_chunk),
                        "word_count": current_word_count,
                        "topic": topic
                    })
                    current_chunk = []
                    current_word_count = 0
                
                # Split large paragraph into sentences
                sentences = re.split(r'[.!?]+\s+', para)
                temp_chunk = []
                temp_count = 0
                
                for sent in sentences:
                    sent_words = self.count_words(sent)
                    
                    if temp_count + sent_words > self.chunk_size and temp_chunk:
                        chunks.append({
                            "text": '. '.join(temp_chunk) + '.',
                            "word_count": temp_count,
                            "topic": topic
                        })
                        
                        # Keep overlap
                        overlap_sents = []
                        overlap_count = 0
                        for s in reversed(temp_chunk):
                            s_words = self.count_words(s)
                            if overlap_count + s_words <= self.overlap:
                                overlap_sents.insert(0, s)
                                overlap_count += s_words
                            else:
                                break
                        
                        temp_chunk = overlap_sents
                        temp_count = overlap_count
                    
                    temp_chunk.append(sent)
                    temp_count += sent_words
                
                if temp_chunk:
                    chunks.append({
                        "text": '. '.join(temp_chunk) + '.',
                        "word_count": temp_count,
                        "topic": topic
                    })
                
            elif current_word_count + para_word_count > self.chunk_size and current_chunk:
                # Current chunk is full, save it
                chunks.append({
                    "text": '\n\n'.join(current_chunk),
                    "word_count": current_word_count,
                    "topic": topic
                })
                
                # Start new chunk with overlap
                overlap_text = '\n\n'.join(current_chunk[-2:])  # Last 2 paragraphs
                overlap_count = self.count_words(overlap_text)
                
                if overlap_count <= self.overlap:
                    current_chunk = current_chunk[-2:]
                    current_word_count = overlap_count
                else:
                    current_chunk = []
                    current_word_count = 0
                
                current_chunk.append(para)
                current_word_count += para_word_count
            
            else:
                # Add to current chunk
                current_chunk.append(para)
                current_word_count += para_word_count
        
        # Save final chunk
        if current_chunk:
            chunks.append({
                "text": '\n\n'.join(current_chunk),
                "word_count": current_word_count,
                "topic": topic
            })
        
        return chunks
    
    def chunk_by_topics(self, sections: Dict[str, str]) -> List[Dict]:
        """Chunk text by topics/sections"""
        chunks = []
        
        # Topic-based chunking (better for travel content)
        topic_mapping = {
            "introduction": "overview",
            "history": "culture",
            "geography": "overview",
            "climate": "planning",
            "get in": "transportation",
            "get around": "transportation",
            "see": "attractions",
            "do": "activities",
            "eat": "food",
            "drink": "food",
            "sleep": "accommodation",
            "stay safe": "practical",
            "practical information": "practical",
            "museums": "attractions",
            "attractions": "attractions",
            "culture": "culture",
            "neighborhoods": "neighborhoods"
        }
        
        for section_name, content in sections.items():
            # Determine category
            category = "general"
            for key, value in topic_mapping.items():
                if key in section_name.lower():
                    category = value
                    break
            
            # Chunk this section
            section_chunks = self.chunk_by_paragraphs(content, topic=section_name)
            
            # Add category to chunks
            for chunk in section_chunks:
                chunk["category"] = category
                chunks.append(chunk)
        
        return chunks


class DataProcessor:
    """Main data processor"""
    
    def __init__(self, chunk_size_words: int = 800, overlap_words: int = 100):
        self.cleaner = TextCleaner()
        self.chunker = TextChunker(chunk_size_words, overlap_words)
    
    def process_wikipedia_article(self, article_data: Dict, city: str, country: str) -> List[Dict]:
        """Process Wikipedia article into chunks"""
        if not article_data:
            return []
        
        # Clean text
        text = article_data.get("extract", "")
        clean_text = self.cleaner.clean_text(text)
        
        # Extract sections
        sections = self.cleaner.extract_sections(clean_text)
        
        # Chunk by topics
        chunks = self.chunker.chunk_by_topics(sections)
        
        # Add metadata
        for chunk in chunks:
            chunk["source"] = "wikipedia"
            chunk["source_url"] = article_data.get("url", "")
            chunk["city"] = city
            chunk["country"] = country
            chunk["reliability_score"] = 9
        
        return chunks
    
    def process_wikivoyage_guide(self, guide_data: Dict, city: str, country: str) -> List[Dict]:
        """Process Wikivoyage guide into chunks"""
        if not guide_data:
            return []
        
        text = guide_data.get("content", "")
        clean_text = self.cleaner.clean_text(text)
        
        sections = self.cleaner.extract_sections(clean_text)
        chunks = self.chunker.chunk_by_topics(sections)
        
        for chunk in chunks:
            chunk["source"] = "wikivoyage"
            chunk["city"] = city
            chunk["country"] = country
            chunk["reliability_score"] = 8
        
        return chunks
    
    def process_poi_data(self, pois: List[Dict], city: str, country: str) -> List[Dict]:
        """Process POI data into chunks"""
        chunks = []
        
        # Group POIs by kind
        poi_groups = {}
        for poi in pois:
            if not poi.get("name"):
                continue
            
            kinds = poi.get("kinds", ["general"])
            primary_kind = kinds[0] if kinds else "general"
            
            if primary_kind not in poi_groups:
                poi_groups[primary_kind] = []
            
            poi_groups[primary_kind].append(poi)
        
        # Create chunks per group
        for kind, poi_list in poi_groups.items():
            if len(poi_list) < 3:
                continue  # Skip small groups
            
            # Create text description
            text_parts = [f"Points of interest in {city} - {kind.replace('_', ' ').title()}:\n"]
            
            for poi in poi_list[:20]:  # Limit to top 20
                name = poi.get("name", "Unknown")
                text_parts.append(f"• {name}")
            
            text = '\n'.join(text_parts)
            
            chunks.append({
                "text": text,
                "word_count": len(text.split()),
                "topic": f"poi_{kind}",
                "category": "attractions",
                "source": "opentripmap",
                "city": city,
                "country": country,
                "poi_count": len(poi_list),
                "reliability_score": 7
            })
        
        return chunks
    
    def process_restaurant_data(self, restaurants: List[Dict], city: str, country: str) -> List[Dict]:
        """Process restaurant data into chunks"""
        if not restaurants:
            return []
        
        # Sort by rating and review count
        sorted_restaurants = sorted(
            restaurants,
            key=lambda x: (x.get("rating", 0), x.get("review_count", 0)),
            reverse=True
        )
        
        # Create chunks by price range
        price_ranges = {"$": [], "$$": [], "$$$": [], "$$$$": []}
        no_price = []
        
        for restaurant in sorted_restaurants:
            price = restaurant.get("price", "")
            if price in price_ranges:
                price_ranges[price].append(restaurant)
            else:
                no_price.append(restaurant)
        
        chunks = []
        
        for price, rest_list in price_ranges.items():
            if not rest_list:
                continue
            
            # Create text
            price_label = {
                "$": "Budget",
                "$$": "Mid-range",
                "$$$": "Upscale",
                "$$$$": "Fine Dining"
            }.get(price, "Restaurants")
            
            text_parts = [f"{price_label} restaurants in {city}:\n"]
            
            for rest in rest_list[:15]:  # Top 15 per category
                name = rest.get("name", "")
                rating = rest.get("rating", 0)
                review_count = rest.get("review_count", 0)
                categories = ", ".join(rest.get("categories", [])[:2])
                
                text_parts.append(
                    f"• {name} ({rating}⭐, {review_count} reviews) - {categories}"
                )
            
            text = '\n'.join(text_parts)
            
            chunks.append({
                "text": text,
                "word_count": len(text.split()),
                "topic": f"restaurants_{price}",
                "category": "food",
                "subcategory": "restaurants",
                "source": "yelp",
                "city": city,
                "country": country,
                "price_range": price,
                "restaurant_count": len(rest_list),
                "reliability_score": 8
            })

        return chunks

    # ============================================
    # Phase 2: Additional Data Processors
    # ============================================

    def process_country_data(self, country_data: Dict, city: str, country: str) -> List[Dict]:
        """Process REST Countries data into chunks"""
        if not country_data:
            return []

        # Create comprehensive country information text
        text_parts = [f"Country Information: {country_data.get('name', country)}\n"]

        if country_data.get('capital'):
            text_parts.append(f"Capital: {country_data['capital']}")

        if country_data.get('region'):
            text_parts.append(f"Region: {country_data['region']}")
            if country_data.get('subregion'):
                text_parts.append(f"Subregion: {country_data['subregion']}")

        if country_data.get('population'):
            pop = f"{country_data['population']:,}"
            text_parts.append(f"Population: {pop}")

        if country_data.get('area'):
            area = f"{country_data['area']:,}"
            text_parts.append(f"Area: {area} km²")

        if country_data.get('languages'):
            langs = ", ".join(country_data['languages'])
            text_parts.append(f"Languages: {langs}")

        if country_data.get('currencies'):
            curr = ", ".join(country_data['currencies'])
            text_parts.append(f"Currencies: {curr}")

        if country_data.get('timezones'):
            tz = ", ".join(country_data['timezones'])
            text_parts.append(f"Timezones: {tz}")

        text = '\n'.join(text_parts)

        return [{
            "text": text,
            "word_count": len(text.split()),
            "topic": "country_info",
            "category": "general",
            "subcategory": "country_facts",
            "source": "rest_countries",
            "city": city,
            "country": country,
            "reliability_score": 10
        }]

    def process_google_places(self, places: List[Dict], city: str, country: str) -> List[Dict]:
        """Process Google Places data into chunks"""
        if not places:
            return []

        chunks = []

        for place in places[:30]:  # Top 30 places
            name = place.get('name', '')
            rating = place.get('rating', 0)
            types = ', '.join(place.get('types', [])[:3])
            address = place.get('formatted_address', '')

            text_parts = [f"{name}"]

            if rating:
                text_parts.append(f"Rating: {rating}⭐")

            if types:
                text_parts.append(f"Type: {types}")

            if address:
                text_parts.append(f"Address: {address}")

            text = '\n'.join(text_parts)

            chunks.append({
                "text": text,
                "word_count": len(text.split()),
                "topic": "google_place",
                "category": "attractions",
                "subcategory": "poi",
                "source": "google_places",
                "city": city,
                "country": country,
                "rating": rating,
                "reliability_score": 9
            })

        return chunks

    def process_foursquare_places(self, places: List[Dict], city: str, country: str) -> List[Dict]:
        """Process Foursquare Places data into chunks"""
        if not places:
            return []

        chunks = []

        for place in places[:30]:
            name = place.get('name', '')
            categories = place.get('categories', [])
            cat_names = ', '.join([c.get('name', '') for c in categories[:2]])
            location = place.get('location', {})
            address = location.get('formatted_address', '')

            text_parts = [f"{name}"]

            if cat_names:
                text_parts.append(f"Category: {cat_names}")

            if address:
                text_parts.append(f"Location: {address}")

            text = '\n'.join(text_parts)

            chunks.append({
                "text": text,
                "word_count": len(text.split()),
                "topic": "foursquare_place",
                "category": "attractions",
                "subcategory": "poi",
                "source": "foursquare",
                "city": city,
                "country": country,
                "reliability_score": 8
            })

        return chunks

    def process_geonames_data(self, geo_data: Dict, city: str, country: str) -> List[Dict]:
        """Process GeoNames data into chunks"""
        if not geo_data:
            return []

        text_parts = [f"Geographic Information: {geo_data.get('name', city)}"]

        if geo_data.get('population'):
            text_parts.append(f"Population: {geo_data['population']:,}")

        if geo_data.get('timezone'):
            tz_info = geo_data['timezone']
            text_parts.append(f"Timezone: {tz_info.get('timeZoneId', '')}")

        if geo_data.get('elevation'):
            text_parts.append(f"Elevation: {geo_data['elevation']}m")

        text = '\n'.join(text_parts)

        return [{
            "text": text,
            "word_count": len(text.split()),
            "topic": "geography",
            "category": "general",
            "subcategory": "geographic_info",
            "source": "geonames",
            "city": city,
            "country": country,
            "reliability_score": 9
        }]

    def process_wikidata_attractions(self, attractions: List[Dict], city: str, country: str) -> List[Dict]:
        """Process Wikidata attractions into chunks"""
        if not attractions:
            return []

        text_parts = [f"Notable Attractions in {city}:\n"]

        for attr in attractions[:20]:
            name = attr.get('attractionLabel', {}).get('value', '')
            desc = attr.get('description', {}).get('value', '')

            if name:
                if desc:
                    text_parts.append(f"• {name}: {desc}")
                else:
                    text_parts.append(f"• {name}")

        text = '\n'.join(text_parts)

        return [{
            "text": text,
            "word_count": len(text.split()),
            "topic": "attractions",
            "category": "attractions",
            "subcategory": "notable_sites",
            "source": "wikidata",
            "city": city,
            "country": country,
            "reliability_score": 9
        }]

    def process_osm_pois(self, pois: List[Dict], city: str, country: str) -> List[Dict]:
        """Process OpenStreetMap POIs into chunks"""
        if not pois:
            return []

        # Group by type
        by_type = {}
        for poi in pois:
            tags = poi.get('tags', {})
            poi_type = tags.get('tourism') or tags.get('historic') or tags.get('amenity') or 'other'

            if poi_type not in by_type:
                by_type[poi_type] = []

            by_type[poi_type].append(poi)

        chunks = []

        for poi_type, items in by_type.items():
            if len(items) < 3:  # Skip small groups
                continue

            text_parts = [f"{poi_type.title()} in {city}:\n"]

            for item in items[:15]:
                tags = item.get('tags', {})
                name = tags.get('name', '')

                if name:
                    text_parts.append(f"• {name}")

            if len(text_parts) > 1:  # Has content besides header
                text = '\n'.join(text_parts)

                chunks.append({
                    "text": text,
                    "word_count": len(text.split()),
                    "topic": f"osm_{poi_type}",
                    "category": "attractions",
                    "subcategory": poi_type,
                    "source": "openstreetmap",
                    "city": city,
                    "country": country,
                    "poi_count": len(items),
                    "reliability_score": 8
                })

        return chunks

    def process_weather_data(self, weather_data: Dict, city: str, country: str) -> List[Dict]:
        """Process weather/climate data into chunks"""
        if not weather_data:
            return []

        location = weather_data.get('location', {})
        current = weather_data.get('current', {})

        text_parts = [f"Climate Information for {city}"]

        if location.get('localtime'):
            text_parts.append(f"Local Time: {location['localtime']}")

        if current.get('temp_c'):
            text_parts.append(f"Temperature: {current['temp_c']}°C / {current.get('temp_f', '')}°F")

        if current.get('condition'):
            text_parts.append(f"Current Conditions: {current['condition'].get('text', '')}")

        if current.get('humidity'):
            text_parts.append(f"Humidity: {current['humidity']}%")

        text = '\n'.join(text_parts)

        return [{
            "text": text,
            "word_count": len(text.split()),
            "topic": "weather",
            "category": "practical",
            "subcategory": "climate",
            "source": "weather_api",
            "city": city,
            "country": country,
            "reliability_score": 8
        }]

    def process_scraped_content(self, scraped_data: Dict, city: str, country: str) -> List[Dict]:
        """Process web-scraped content into chunks"""
        if not scraped_data:
            return []

        source = scraped_data.get('source', 'web_scraper')
        chunks = []

        # Process introduction
        if scraped_data.get('intro'):
            intro_text = scraped_data['intro']
            if len(intro_text.split()) > 50:  # Meaningful content
                chunks.append({
                    "text": intro_text,
                    "word_count": len(intro_text.split()),
                    "topic": f"{source}_intro",
                    "category": "guide",
                    "subcategory": "introduction",
                    "source": source,
                    "city": city,
                    "country": country,
                    "url": scraped_data.get('url'),
                    "reliability_score": 7
                })

        # Process sections
        if scraped_data.get('sections'):
            for i, section in enumerate(scraped_data['sections']):
                # Split long sections
                section_chunks = self._chunk_text(section, self.chunk_size, self.overlap)

                for chunk in section_chunks:
                    if len(chunk.split()) > 50:
                        chunks.append({
                            "text": chunk,
                            "word_count": len(chunk.split()),
                            "topic": f"{source}_section_{i}",
                            "category": "guide",
                            "subcategory": "content",
                            "source": source,
                            "city": city,
                            "country": country,
                            "url": scraped_data.get('url'),
                            "reliability_score": 7
                        })

        return chunks

    def process_scraped_attractions(self, attractions: List[Dict], city: str, country: str) -> List[Dict]:
        """Process scraped attraction lists (e.g., Atlas Obscura)"""
        if not attractions:
            return []

        source = attractions[0].get('source', 'web_scraper') if attractions else 'web_scraper'

        text_parts = [f"Unique Attractions in {city}:\n"]

        for attr in attractions[:20]:
            name = attr.get('name', '')
            desc = attr.get('description', '')

            if name:
                if desc and len(desc) > 20:
                    text_parts.append(f"• {name}: {desc}")
                else:
                    text_parts.append(f"• {name}")

        text = '\n'.join(text_parts)

        return [{
            "text": text,
            "word_count": len(text.split()),
            "topic": f"{source}_attractions",
            "category": "attractions",
            "subcategory": "unique_places",
            "source": source,
            "city": city,
            "country": country,
            "reliability_score": 7
        }]