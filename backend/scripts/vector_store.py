"""
ChromaDB vector store operations
"""
import chromadb
from typing import List, Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class VectorStore:
    """Manage ChromaDB vector store"""
    
    def __init__(self, chroma_url: str, collection_name: str = "travel_knowledge"):
        self.client = chromadb.HttpClient(host=chroma_url.replace("http://", "").replace(":8000", ""), port=8000)
        self.collection_name = collection_name
        self.collection = None
        
        self._init_collection()
    
    def _init_collection(self):
        """Initialize or get collection"""
        try:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Travel knowledge base for RAG"}
            )
            logger.info(f"Connected to collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error initializing collection: {e}")
            raise
    
    def add_documents(self, chunks: List[Dict], embeddings: List[List[float]]) -> bool:
        """Add documents to vector store"""
        if not chunks or not embeddings:
            logger.warning("No chunks or embeddings to add")
            return False
        
        if len(chunks) != len(embeddings):
            logger.error(f"Chunk count ({len(chunks)}) doesn't match embedding count ({len(embeddings)})")
            return False
        
        try:
            # Prepare data
            documents = []
            metadatas = []
            ids = []
            valid_embeddings = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                if embedding is None:
                    logger.warning(f"Skipping chunk {i} - no embedding")
                    continue
                
                # Generate unique ID
                city = chunk.get("city", "unknown")
                source = chunk.get("source", "unknown")
                topic = chunk.get("topic", "general")
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                doc_id = f"{city}_{source}_{topic}_{i}_{timestamp}"
                
                # Prepare document
                documents.append(chunk["text"])
                
                # Prepare metadata (remove text and embedding)
                metadata = {k: v for k, v in chunk.items() if k not in ["text", "embedding"]}
                metadata["added_at"] = datetime.now().isoformat()
                
                # Convert all values to strings (ChromaDB requirement)
                metadata = {k: str(v) for k, v in metadata.items()}
                
                metadatas.append(metadata)
                ids.append(doc_id)
                valid_embeddings.append(embedding)
            
            if not documents:
                logger.warning("No valid documents to add")
                return False
            
            # Add to ChromaDB in batches
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i+batch_size]
                batch_meta = metadatas[i:i+batch_size]
                batch_ids = ids[i:i+batch_size]
                batch_emb = valid_embeddings[i:i+batch_size]
                
                self.collection.add(
                    documents=batch_docs,
                    metadatas=batch_meta,
                    ids=batch_ids,
                    embeddings=batch_emb
                )
                
                logger.info(f"Added batch {i//batch_size + 1}: {len(batch_docs)} documents")
            
            logger.info(f"Successfully added {len(documents)} documents to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            return False
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
    
    def search(self, query_embedding: List[float], n_results: int = 10, 
               filter_metadata: Dict = None) -> Dict:
        """Search the vector store"""
        try:
            query_params = {
                "query_embeddings": [query_embedding],
                "n_results": n_results
            }
            
            if filter_metadata:
                query_params["where"] = filter_metadata
            
            results = self.collection.query(**query_params)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return {}