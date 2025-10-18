from openai import OpenAI
from app.config import settings

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def chat_completion(self, messages: list, temperature: float = 0.7):
        """Get completion from OpenAI"""
        response = self.client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    async def get_embedding(self, text: str):
        """Get embedding for RAG"""
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding

ai_service = AIService()