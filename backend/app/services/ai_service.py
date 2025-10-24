from openai import OpenAI
from app.config import settings

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.embedding_model = settings.OPENAI_EMBEDDING_MODEL
    
    async def chat_completion(
        self, 
        messages: list, 
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        Get completion from OpenAI
        
        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            temperature: 0.0 (deterministic) to 1.0 (creative)
            max_tokens: Maximum tokens in response
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    async def get_embedding(self, text: str):
        """Get embedding for RAG"""
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding

ai_service = AIService()