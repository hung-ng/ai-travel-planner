"""
Main context manager - orchestrates context extraction, formatting, and summarization
"""
from typing import List, Dict, Optional
from app.services.ai import chat_service
from .extractor import context_extractor
from .formatter import context_formatter


class ContextManager:
    """
    Manages conversation context efficiently

    Strategy:
    1. Keep last N messages in full
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

        Args:
            messages: Full conversation history
            summary: Existing conversation summary
            context: Extracted context dictionary

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
            context_str = context_formatter.format_context(context)
            if context_str:
                context_parts.append(f"Known information: {context_str}")

        context_description = "\n\n".join(context_parts)

        return recent_messages, context_description

    def extract_context(self, messages: List[Dict]) -> Dict:
        """
        Extract key facts from messages

        Args:
            messages: List of conversation messages

        Returns:
            Dictionary of extracted context
        """
        return context_extractor.extract_context(messages)

    async def should_summarize(self, message_count: int, last_summarized_index: int) -> bool:
        """
        Check if we should create/update summary

        Args:
            message_count: Total number of messages
            last_summarized_index: Index when last summarized

        Returns:
            True if summarization threshold is reached
        """
        unsummarized_count = message_count - last_summarized_index
        return unsummarized_count >= self.summarize_threshold

    async def create_summary(self, messages: List[Dict], existing_summary: Optional[str] = None) -> str:
        """
        Create or update conversation summary

        Uses AI to summarize old messages

        Args:
            messages: All conversation messages
            existing_summary: Previous summary if any

        Returns:
            Updated summary
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

        summary = await chat_service.get_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200
        )

        return summary.strip()


# Singleton instance
context_manager = ContextManager(window_size=10, summarize_threshold=15)
