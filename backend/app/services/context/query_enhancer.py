"""
Query enhancement for better document retrieval

Simple 2-tier approach:
- Tier 1 (Always): Append destination if not already in query
- Tier 2 (Often): Append top 1-2 interests if available

Duration, budget, and travel style are passed to AI via system prompt, not RAG query.
"""
from typing import Dict, Optional, List


class QueryEnhancer:
    """Enhance search queries with conversation context"""

    def enhance_query(self, query: str, context: Optional[Dict] = None) -> str:
        """
        Enhance a search query with extracted context

        Strategy:
        1. Always add destination (if exists and not already mentioned)
        2. Add top 1-2 interests (if exist)
        3. Skip duration, budget, travel_style (better for system prompt)

        Examples:
        - "What should I see?" + {destination: "Paris", interests: ["museums"]}
          → "What should I see in Paris focusing on museums"

        - "Best restaurants?" + {destination: "Tokyo", interests: ["food", "culture"]}
          → "Best restaurants in Tokyo"

        - "Tell me about museums" + {destination: "Rome"}
          → "Tell me about museums in Rome"

        Args:
            query: Original user query
            context: Extracted conversation context

        Returns:
            Enhanced query string
        """
        if not context:
            return query

        query_lower = query.lower()
        enhanced_parts = [query]

        # TIER 1: Add destination (if exists and not already in query)
        destination = context.get("destination")
        if destination:
            # Simple check: is destination already mentioned?
            if destination.lower() not in query_lower:
                enhanced_parts.append(f"in {destination}")

        # TIER 2: Add top 1-2 interests (if exist and relevant)
        interests = context.get("interests", [])
        if interests and self._should_add_interests(query_lower):
            # Only use top 2 interests to avoid over-constraining
            interest_str = " and ".join(interests[:2])
            enhanced_parts.append(f"focusing on {interest_str}")

        # Join and clean up
        enhanced_query = " ".join(enhanced_parts)
        enhanced_query = self._clean_query(enhanced_query)

        return enhanced_query

    def _should_add_interests(self, query: str) -> bool:
        """
        Check if query would benefit from interest context

        Add interests for:
        - Vague queries: "what should I do?", "any suggestions?"
        - Activity queries: "what to see?", "things to do?"
        - Planning queries: "help me plan", "create itinerary"

        Skip interests for:
        - Very specific: "Eiffel Tower hours?", "metro ticket price?"
        - Factual: "how to get to", "what time does", "how much"
        """
        # Questions that benefit from interests
        benefit_patterns = [
            "what should", "what can", "where should", "where can",
            "any suggestions", "what else", "tell me more",
            "things to do", "what to see", "what to do",
            "activities", "attractions", "places to visit",
            "help me plan", "itinerary", "recommendations"
        ]

        # Very specific questions that don't need interests
        skip_patterns = [
            "what time", "how much", "how far", "how long",
            "how to get", "when does", "where is",
            "is it open", "is there", "ticket", "price"
        ]

        # Skip if it's a specific factual question
        if any(pattern in query for pattern in skip_patterns):
            return False

        # Add if it matches benefit patterns or is vague
        if any(pattern in query for pattern in benefit_patterns):
            return True

        # Default: add interests for short/vague queries
        word_count = len(query.split())
        return word_count <= 5  # Short queries are usually vague

    def _clean_query(self, query: str) -> str:
        """Clean up enhanced query"""
        # Remove multiple spaces
        query = " ".join(query.split())

        # Fix punctuation issues
        query = query.replace("? in", " in")
        query = query.replace("? focusing", " focusing")
        query = query.replace(". in", " in")
        query = query.replace(". focusing", " focusing")

        return query.strip()

    def create_contextual_filter(self, context: Optional[Dict] = None) -> Optional[Dict]:
        """
        Create metadata filter for RAG search based on context

        Args:
            context: Extracted conversation context

        Returns:
            ChromaDB metadata filter or None
        """
        if not context:
            return None

        filters = {}

        # Filter by destination if available
        destination = context.get("destination")
        if destination:
            filters["city"] = destination

        # Only return filter if we have criteria
        return filters if filters else None

    def get_context_for_prompt(self, context: Optional[Dict] = None) -> str:
        """
        Format context for AI system prompt (not for RAG query)

        This includes duration, budget, travel_style that we DON'T put in RAG query.

        Args:
            context: Extracted conversation context

        Returns:
            Formatted context string for system prompt
        """
        if not context:
            return ""

        parts = []

        # Duration
        duration = context.get("duration_days")
        if duration:
            parts.append(f"Trip duration: {duration} days")

        # Budget
        budget = context.get("budget")
        if budget:
            parts.append(f"Budget: ${budget:,}")

        # Travel style
        travel_style = context.get("travel_style")
        if travel_style:
            parts.append(f"Travel style: {travel_style}")

        return "; ".join(parts) if parts else ""


# Singleton instance
query_enhancer = QueryEnhancer()
