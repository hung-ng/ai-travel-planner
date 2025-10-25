"""
Embedding generation service using OpenAI

This service is shared across the application for consistent embeddings.
"""
from openai import OpenAI
from typing import List
from app.config import settings


class EmbeddingService:
    """Generate embeddings using OpenAI API"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_EMBEDDING_MODEL

    async def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Text to embed

        Returns:
            1536-dimensional embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )

            embedding = response.data[0].embedding

            # Verify dimension (should be 1536 for text-embedding-3-small)
            if len(embedding) != 1536:
                print(f"[EMBEDDINGS] ⚠️  Unexpected dimension: {len(embedding)}")

            return embedding

        except Exception as e:
            print(f"[EMBEDDINGS] ❌ Error generating embedding: {e}")
            raise

    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )

            embeddings = [item.embedding for item in response.data]
            return embeddings

        except Exception as e:
            print(f"[EMBEDDINGS] ❌ Error generating batch embeddings: {e}")
            raise


# Singleton instance
embedding_service = EmbeddingService()
