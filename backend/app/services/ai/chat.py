"""
Chat completion service using OpenAI
"""
from openai import OpenAI
from typing import List, Dict
from app.config import settings


class ChatService:
    """Handle chat completions with OpenAI"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def get_completion(
        self,
        messages: List[Dict],
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """
        Get chat completion from OpenAI

        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            temperature: 0.0 (deterministic) to 1.0 (creative)
            max_tokens: Maximum tokens in response

        Returns:
            Assistant's response text
        """
        # Use defaults from settings if not specified
        if temperature is None:
            temperature = settings.OPENAI_TEMPERATURE
        if max_tokens is None:
            max_tokens = settings.OPENAI_MAX_TOKENS

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"[CHAT] ❌ Error getting completion: {e}")
            raise


# Singleton instance
chat_service = ChatService()
