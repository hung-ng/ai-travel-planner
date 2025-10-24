"""
Manage conversation context efficiently
"""
from typing import List, Dict, Optional
from app.services.ai_service import ai_service
import re


class ContextManager:
    """
    Manages conversation context efficiently
    
    Strategy:
    1. Keep last 10 messages in full
    2. Summarize older messages
    3. Extract and track key facts
    4. Only send relevant context to AI
    """
    
    def __init__(self, window_size: int = 10, summarize_threshold: int = 15):
        """
        Args:
            window_size: Number of recent messages to keep in full
            summarize_threshold: Summarize when message count exceeds this
        """
        self.window_size = window_size
        self.summarize_threshold = summarize_threshold
    
    def get_context_for_ai(
        self, 
        messages: List[Dict], 
        summary: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> tuple[List[Dict], str]:
        """
        Get optimized context for AI
        
        Returns:
            (recent_messages, context_description)
        """
        # Take only recent messages
        recent_messages = messages[-self.window_size:]
        
        # Build context description
        context_parts = []
        
        # Add summary if exists
        if summary:
            context_parts.append(f"Previous conversation summary: {summary}")
        
        # Add extracted context
        if context:
            context_str = self._format_context(context)
            if context_str:
                context_parts.append(f"Known information: {context_str}")
        
        context_description = "\n\n".join(context_parts)
        
        return recent_messages, context_description
    
    def extract_context(self, messages: List[Dict]) -> Dict:
        """
        Extract key facts from messages with improved entity extraction
        
        PRIORITY ORDER to avoid conflicts:
        1. Destination (most important)
        2. Duration (BEFORE budget to avoid "5 days" → budget confusion)
        3. Budget (only with explicit context)
        4. Interests
        5. Travel style
        """
        context = {}
        
        # Combine all user messages
        all_user_messages = [msg["content"] for msg in messages if msg["role"] == "user"]
        user_text_lower = " ".join(all_user_messages).lower()
        
        # PRIORITY 1: Extract destination (case-sensitive)
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
        """Extract destination with case-sensitive matching"""
        destination_patterns = [
            r"(?:visit|go to|going to|trip to|travel to|traveling to)\s+([A-Z][a-zA-Z\s]+?)(?:\s+for|\s+in|\s|,|\.|$)",
            r"(?:plan.*?to|planning to)\s+(?:visit|go to)\s+([A-Z][a-zA-Z\s]+?)(?:\s|,|\.|$)",
            r"(?:in|at)\s+([A-Z][a-zA-Z\s]+?)(?:\s+for|\s+in|,|\.|$)",
        ]
        
        # Search in original case-sensitive messages
        for message in messages:
            for pattern in destination_patterns:
                match = re.search(pattern, message)
                if match:
                    destination = match.group(1).strip()
                    
                    # Filter out common words and time-related words
                    stop_words = ["the", "a", "an", "for", "june", "july", "august", "september", 
                                 "october", "november", "december", "january", "february", "march",
                                 "april", "may", "days", "weeks", "months", "Day", "Days", "Week"]
                    
                    if destination.lower() not in [w.lower() for w in stop_words] and len(destination) > 2:
                        return destination
        
        return None
    
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
    
    def _format_context(self, context: Dict) -> str:
        """Format context dict into readable string"""
        parts = []
        
        if "destination" in context:
            parts.append(f"Destination: {context['destination']}")
        
        if "duration_days" in context:
            parts.append(f"Duration: {context['duration_days']} days")
        
        if "budget" in context:
            parts.append(f"Budget: ${context['budget']:,}")
        
        if "interests" in context:
            parts.append(f"Interests: {', '.join(context['interests'])}")
        
        if "travel_style" in context:
            parts.append(f"Travel style: {context['travel_style']}")
        
        return "; ".join(parts)
    
    async def should_summarize(self, message_count: int, last_summarized_index: int) -> bool:
        """Check if we should create/update summary"""
        unsummarized_count = message_count - last_summarized_index
        return unsummarized_count >= self.summarize_threshold
    
    async def create_summary(self, messages: List[Dict], existing_summary: Optional[str] = None) -> str:
        """
        Create or update conversation summary
        
        Uses AI to summarize old messages
        """
        if len(messages) <= self.window_size:
            return existing_summary or ""
        
        messages_to_summarize = messages[:-self.window_size]
        
        conversation_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in messages_to_summarize
        ])
        
        prompt = f"""Summarize this travel planning conversation into 2-3 concise sentences. Focus on key facts: destination, dates, budget, preferences, and any decisions made.

Conversation:
{conversation_text}

Previous summary (if any):
{existing_summary or 'None'}

Concise summary:"""
        
        summary = await ai_service.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200
        )
        
        return summary.strip()


context_manager = ContextManager(window_size=10, summarize_threshold=15)