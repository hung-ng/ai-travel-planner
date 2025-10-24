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