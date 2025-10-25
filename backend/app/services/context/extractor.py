"""
Entity extraction from conversation messages

Extracts key information like destination, duration, budget, interests, etc.
"""
import re
from typing import List, Dict, Optional


class ContextExtractor:
    """Extract structured information from conversation messages"""

    # Common city names for better extraction
    KNOWN_CITIES = {
        # Europe
        "paris", "london", "rome", "barcelona", "amsterdam", "prague", "vienna",
        "berlin", "munich", "venice", "florence", "athens", "dublin", "edinburgh",
        "lisbon", "madrid", "copenhagen", "stockholm", "budapest", "krakow",
        # Asia
        "tokyo", "bangkok", "singapore", "hong kong", "seoul", "dubai", "bali",
        "kyoto", "shanghai", "beijing", "taipei", "hanoi", "ho chi minh city",
        "kuala lumpur", "manila", "istanbul", "jerusalem", "tel aviv", "mumbai",
        # Americas
        "new york", "los angeles", "san francisco", "miami", "las vegas",
        "mexico city", "cancun", "rio de janeiro", "buenos aires", "vancouver",
        "toronto", "montreal", "chicago", "boston", "seattle", "washington",
        # Oceania & Others
        "sydney", "melbourne", "auckland", "cairo", "cape town", "marrakech"
    }

    def extract_context(self, messages: List[Dict]) -> Dict:
        """
        Extract key facts from messages with improved entity extraction

        PRIORITY ORDER to avoid conflicts:
        1. Destination (most important)
        2. Duration (BEFORE budget to avoid "5 days" → budget confusion)
        3. Budget (only with explicit context)
        4. Interests
        5. Travel style

        Args:
            messages: List of conversation messages

        Returns:
            Dictionary of extracted context
        """
        context = {}

        # Combine all user messages
        all_user_messages = [msg["content"] for msg in messages if msg["role"] == "user"]
        user_text_lower = " ".join(all_user_messages).lower()

        # PRIORITY 1: Extract destination (case-insensitive now!)
        destination = self._extract_destination(all_user_messages)
        if destination:
            context["destination"] = destination

        # PRIORITY 2: Extract duration (BEFORE budget check)
        duration = self._extract_duration(user_text_lower)
        if duration:
            context["duration_days"] = duration

        # PRIORITY 3: Extract budget (only with clear context)
        budget = self._extract_budget(user_text_lower)
        if budget:
            context["budget"] = budget

        # PRIORITY 4: Extract interests
        interests = self._extract_interests(user_text_lower)
        if interests:
            context["interests"] = interests

        # PRIORITY 5: Extract travel style
        travel_style = self._extract_travel_style(user_text_lower)
        if travel_style:
            context["travel_style"] = travel_style

        return context

    def _extract_destination(self, messages: List[str]) -> Optional[str]:
        """
        Extract destination with robust, case-insensitive matching

        Strategy:
        1. Try verb-based patterns (most reliable)
        2. Try preposition patterns (in, to, at)
        3. Try known city names (fallback)
        """

        # Combine all messages for better context
        full_text = " ".join(messages)

        # STRATEGY 1: Verb-based extraction (most reliable)
        destination = self._extract_with_verbs(full_text)
        if destination:
            return destination

        # STRATEGY 2: Preposition-based extraction
        destination = self._extract_with_prepositions(full_text)
        if destination:
            return destination

        # STRATEGY 3: Known city detection (fallback)
        destination = self._extract_known_cities(full_text)
        if destination:
            return destination

        return None

    def _extract_with_verbs(self, text: str) -> Optional[str]:
        """Extract destination using verb patterns"""
        # Comprehensive verb patterns - case insensitive
        verb_patterns = [
            # Going/visiting patterns
            r"(?:visit|visiting|visited)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"(?:go|going|went)\s+to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"(?:travel|traveling|travelled)\s+to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"(?:trip|vacation|holiday)\s+(?:to|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",

            # Planning patterns
            r"(?:plan|planning|planned)\s+(?:a\s+)?(?:trip|visit)\s+to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"(?:plan|planning|planned)\s+to\s+(?:visit|go\s+to|travel\s+to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",

            # Want/exploring patterns
            r"(?:want|wanting|wanted)\s+to\s+(?:visit|see|explore|go\s+to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"(?:explore|exploring|explored)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"(?:see|seeing|saw)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",

            # Destination-specific patterns
            r"(?:destination|headed|heading)\s+(?:is|to|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"(?:fly|flying|flew)\s+to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        ]

        for pattern in verb_patterns:
            # Case insensitive search
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                destination = match.group(1).strip()

                # Capitalize properly
                destination = self._capitalize_city(destination)

                if self._is_valid_destination(destination):
                    return destination

        return None

    def _extract_with_prepositions(self, text: str) -> Optional[str]:
        """Extract destination using preposition patterns"""
        prep_patterns = [
            r"(?:in|at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:for|during|with|and|or|,|\.|\?|!|$)",
            r"(?:to|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:for|and|or|,|\.|\?|!|$)",
        ]

        for pattern in prep_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                destination = match.group(1).strip()
                destination = self._capitalize_city(destination)

                if self._is_valid_destination(destination):
                    return destination

        return None

    def _extract_known_cities(self, text: str) -> Optional[str]:
        """Extract by matching against known city names"""
        text_lower = text.lower()

        # Sort by length (longest first) to match "New York" before "York"
        sorted_cities = sorted(self.KNOWN_CITIES, key=len, reverse=True)

        for city in sorted_cities:
            # Check if city is mentioned (with word boundaries)
            pattern = r'\b' + re.escape(city) + r'\b'
            if re.search(pattern, text_lower):
                # Return properly capitalized
                return self._capitalize_city(city)

        return None

    def _capitalize_city(self, city: str) -> str:
        """Properly capitalize city names"""
        # Handle special cases
        special_cases = {
            "new york": "New York",
            "los angeles": "Los Angeles",
            "san francisco": "San Francisco",
            "las vegas": "Las Vegas",
            "hong kong": "Hong Kong",
            "ho chi minh city": "Ho Chi Minh City",
            "kuala lumpur": "Kuala Lumpur",
            "mexico city": "Mexico City",
            "rio de janeiro": "Rio de Janeiro",
            "buenos aires": "Buenos Aires",
            "cape town": "Cape Town",
            "tel aviv": "Tel Aviv",
        }

        city_lower = city.lower()
        if city_lower in special_cases:
            return special_cases[city_lower]

        # Default: title case
        return city.title()

    def _is_valid_destination(self, destination: str) -> bool:
        """Check if extracted destination is valid"""
        if not destination or len(destination) < 3:
            return False

        # Filter out common words that aren't cities
        stop_words = [
            "the", "a", "an", "and", "or", "for", "with", "about",
            "june", "july", "august", "september", "october", "november",
            "december", "january", "february", "march", "april", "may",
            "days", "weeks", "months", "day", "week", "month",
            "trip", "vacation", "holiday", "travel", "visit"
        ]

        if destination.lower() in stop_words:
            return False

        # Check if it's a known city (most reliable)
        if destination.lower() in self.KNOWN_CITIES:
            return True

        # Accept if it looks like a proper name (starts with capital)
        if destination[0].isupper():
            return True

        return False

    def _extract_duration(self, text: str) -> Optional[int]:
        """
        Extract trip duration in days
        CRITICAL: Must have explicit "day" or "week" context to avoid false positives
        """
        # Pattern: "5 days", "for 5 days", "5-day trip"
        duration_patterns = [
            r"(?:for\s+)?(\d+)\s*days?(?:\s+trip)?",
            r"(\d+)-day",
            r"(?:for\s+)?(one|two|three|four|five|six|seven|eight|nine|ten)\s*days?",
            r"(?:for\s+)?a\s+week(?:\s+trip)?",
            r"(?:for\s+)?(\d+)\s*weeks?",
        ]

        word_to_num = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
        }

        for pattern in duration_patterns:
            match = re.search(pattern, text)
            if match:
                value = match.group(1) if match.lastindex >= 1 else None

                # "a week" pattern
                if "week" in pattern and not value:
                    return 7

                # "N weeks" pattern
                if "weeks?" in pattern and value and value.isdigit():
                    return int(value) * 7

                # Number of days
                if value:
                    if value.isdigit():
                        return int(value)
                    elif value in word_to_num:
                        return word_to_num[value]

        return None

    def _extract_budget(self, text: str) -> Optional[int]:
        """
        Extract budget amount
        CRITICAL: Only extract if there's clear budget context to avoid false positives
        """
        # MUST have budget context words to avoid extracting random numbers
        budget_indicators = ["budget", "spend", "cost", "price", "afford",
                            "expensive", "cheap", "dollar", "euro", "$", "€"]

        has_budget_context = any(indicator in text for indicator in budget_indicators)

        if not has_budget_context:
            return None

        # Now look for amounts with budget context
        budget_patterns = [
            r"\$\s*([\d,]+)",  # $2000
            r"([\d,]+)\s*(?:dollars|usd)",  # 2000 dollars
            r"([\d,]+)\s*(?:euros|eur)",  # 2000 euros
            r"budget.*?(?:of|is|around)?\s*\$?\s*([\d,]+)",  # budget of 2000
            r"spend.*?(?:about|around)?\s*\$?\s*([\d,]+)",  # spend about 2000
        ]

        for pattern in budget_patterns:
            match = re.search(pattern, text)
            if match:
                budget_str = match.group(1).replace(",", "")
                try:
                    budget = int(budget_str)
                    # Sanity check: budget should be reasonable (100-100000)
                    if 100 <= budget <= 100000:
                        return budget
                except ValueError:
                    continue

        return None

    def _extract_interests(self, text: str) -> List[str]:
        """Extract interests/preferences"""
        interest_keywords = {
            "museums": ["museum", "museums", "art", "gallery", "galleries"],
            "food": ["food", "restaurant", "restaurants", "eating", "cuisine", "dining", "foodie"],
            "history": ["history", "historical", "castle", "monument", "heritage"],
            "nature": ["nature", "hiking", "park", "parks", "beach", "outdoor"],
            "nightlife": ["nightlife", "club", "clubs", "bar", "bars", "party"],
            "shopping": ["shopping", "shop", "shops", "mall", "market", "markets"],
            "culture": ["culture", "cultural", "local", "traditional"],
            "adventure": ["adventure", "activities", "sports"],
            "relaxation": ["relax", "spa", "peaceful"],
            "architecture": ["architecture", "buildings", "monuments"],
        }

        interests = []
        for interest, keywords in interest_keywords.items():
            if any(keyword in text for keyword in keywords):
                interests.append(interest)

        return interests

    def _extract_travel_style(self, text: str) -> Optional[str]:
        """Extract travel style"""
        if any(word in text for word in ["budget", "cheap", "affordable", "backpack"]):
            return "budget"
        elif any(word in text for word in ["luxury", "upscale", "premium", "5-star", "high-end"]):
            return "luxury"
        elif any(word in text for word in ["mid-range", "moderate", "comfortable"]):
            return "mid-range"

        return None


# Singleton instance
context_extractor = ContextExtractor()
