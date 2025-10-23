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
        Extract key facts from messages
        
        Simple rule-based extraction (no AI needed!)
        """
        context = {}
        
        # Combine all user messages
        user_text = " ".join([
            msg["content"] 
            for msg in messages 
            if msg["role"] == "user"
        ]).lower()
        
        # Extract destination (simple pattern matching)
        destination_patterns = [
            r"(?:visit|go to|trip to|travel to|going to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
            r"(?:in|at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        ]
        
        for pattern in destination_patterns:
            matches = re.findall(pattern, " ".join([msg["content"] for msg in messages if msg["role"] == "user"]))
            if matches:
                context["destination"] = matches[0]
                break
        
        # Extract budget
        budget_patterns = [
            r"\$?\s*(\d+(?:,\d+)?)\s*(?:dollars|usd|\$)",
            r"budget.*?\$?\s*(\d+(?:,\d+)?)",
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, user_text)
            if match:
                budget_str = match.group(1).replace(",", "")
                context["budget"] = int(budget_str)
                break
        
        # Extract dates/duration
        duration_patterns = [
            r"(\d+)\s*(?:days?|nights?)",
            r"for\s+(\d+)\s+days?",
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, user_text)
            if match:
                context["duration_days"] = int(match.group(1))
                break
        
        # Extract interests (keywords)
        interest_keywords = {
            "art": ["art", "museum", "gallery", "painting"],
            "food": ["food", "restaurant", "eating", "cuisine", "dining"],
            "history": ["history", "historical", "castle", "monument"],
            "nature": ["nature", "hiking", "park", "beach", "outdoor"],
            "nightlife": ["nightlife", "club", "bar", "party"],
            "shopping": ["shopping", "shop", "mall", "market"],
            "culture": ["culture", "cultural", "local", "traditional"],
        }
        
        interests = []
        for interest, keywords in interest_keywords.items():
            if any(keyword in user_text for keyword in keywords):
                interests.append(interest)
        
        if interests:
            context["interests"] = interests
        
        # Extract travel style
        if any(word in user_text for word in ["budget", "cheap", "affordable", "backpack"]):
            context["travel_style"] = "budget"
        elif any(word in user_text for word in ["luxury", "upscale", "premium", "5-star"]):
            context["travel_style"] = "luxury"
        else:
            context["travel_style"] = "mid-range"
        
        return context
    
    def _format_context(self, context: Dict) -> str:
        """Format context dict into readable string"""
        parts = []
        
        if "destination" in context:
            parts.append(f"Destination: {context['destination']}")
        
        if "budget" in context:
            parts.append(f"Budget: ${context['budget']:,}")
        
        if "duration_days" in context:
            parts.append(f"Duration: {context['duration_days']} days")
        
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