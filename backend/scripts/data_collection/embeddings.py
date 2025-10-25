"""
Generate embeddings using OpenAI
"""
from openai import OpenAI
from typing import List, Dict
import time
import logging

logger = logging.getLogger(__name__)


class EmbeddingsGenerator:
    """Generate embeddings using OpenAI API"""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small", batch_size: int = 100):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.batch_size = batch_size
        
        logger.info(f"Initialized EmbeddingsGenerator with model: {model}")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            try:
                logger.info(f"Generating embeddings for batch {i//self.batch_size + 1} "
                          f"({len(batch)} texts)")
                
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                
                # Extract embeddings
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                # Log usage
                usage = response.usage
                cost = (usage.total_tokens / 1_000_000) * 0.020  # $0.020 per 1M tokens
                logger.info(f"Batch complete. Tokens: {usage.total_tokens:,}, "
                          f"Cost: ${cost:.6f}")
                
                # Small delay to respect rate limits
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error generating embeddings for batch {i//self.batch_size + 1}: {e}")
                # Add None for failed embeddings
                all_embeddings.extend([None] * len(batch))
        
        return all_embeddings
    
    def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=[text]
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None