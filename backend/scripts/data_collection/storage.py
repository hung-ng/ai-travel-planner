"""
ChromaDB vector store operations (compatible with ChromaDB 0.5.x)
"""
import chromadb
from typing import List, Dict, Optional
import logging
from datetime import datetime
from urllib.parse import urlparse
import time
import hashlib

logger = logging.getLogger(__name__)


class VectorStore:
    """Manage ChromaDB vector store"""
    
    def __init__(self, chroma_url: str, collection_name: str = "travel_knowledge"):
        self.chroma_url = chroma_url
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        
        self._connect()
        self._init_collection()
    
    def _connect(self):
        """Connect to ChromaDB"""
        try:
            # Parse the URL
            parsed = urlparse(self.chroma_url)
            host = parsed.hostname or "localhost"
            port = parsed.port or 8001
            
            logger.info(f"Connecting to ChromaDB at {host}:{port}")
            
            # Create HTTP client (latest API)
            self.client = chromadb.HttpClient(
                host=host,
                port=port
            )
            
            # Test connection
            heartbeat = self.client.heartbeat()
            logger.info(f"✅ Connected to ChromaDB (heartbeat: {heartbeat})")
            
            # Get version info
            try:
                version_info = chromadb.__version__
                logger.info(f"ChromaDB client version: {version_info}")
            except:
                pass
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to ChromaDB")
            logger.error(f"URL: {self.chroma_url}")
            logger.error(f"Error: {e}")
            logger.error("\nTroubleshooting:")
            logger.error("1. Check if ChromaDB is running:")
            logger.error("   docker ps | grep chromadb")
            logger.error("2. Check ChromaDB logs:")
            logger.error("   docker logs travel_chromadb")
            logger.error("3. Test endpoint:")
            logger.error(f"   curl http://localhost:8001/api/v1/heartbeat")
            logger.error("4. Restart ChromaDB:")
            logger.error("   docker-compose -f docker-compose.backend.yml restart chromadb")
            raise ConnectionError(f"Cannot connect to ChromaDB: {e}")
    
    def _init_collection(self):
        """Initialize or get collection with COSINE distance"""
        try:
            logger.info(f"Initializing collection: {self.collection_name}")
            
            # CRITICAL: Use cosine distance for better similarity scores
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={
                    "description": "Travel knowledge base for RAG",
                    "hnsw:space": "cosine"  # ADD THIS LINE!
                }
            )
            
            # Get current count
            count = self.collection.count()
            logger.info(f"✅ Connected to collection '{self.collection_name}' ({count:,} documents)")
            logger.info(f"📊 Distance metric: cosine")
            
        except Exception as e:
            logger.error(f"❌ Error initializing collection: {e}")
            raise
    
    def add_documents(self, chunks: List[Dict], embeddings: List[List[float]]) -> bool:
        """Add documents to vector store"""
        if not chunks or not embeddings:
            logger.warning("No chunks or embeddings to add")
            return False
        
        if len(chunks) != len(embeddings):
            logger.error(f"Chunk count ({len(chunks)}) != embedding count ({len(embeddings)})")
            return False
        
        try:
            documents = []
            metadatas = []
            ids = []
            valid_embeddings = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                if embedding is None:
                    logger.warning(f"Skipping chunk {i} - no embedding")
                    continue

                # Generate content-based ID to prevent duplicates
                # Hash the text content to create a stable, unique ID
                city = chunk.get("city", "unknown")
                source = chunk.get("source", "unknown")
                text = chunk.get("text", "")

                # Create hash of the text content
                text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:12]

                # Combine city, source, and content hash for ID
                # This ensures same content = same ID = no duplicates!
                doc_id = f"{city}_{source}_{text_hash}"
                
                # Prepare document text
                documents.append(chunk["text"])
                
                # Prepare metadata (exclude text and embedding)
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
            total_batches = (len(documents) + batch_size - 1) // batch_size
            successful_batches = 0
            
            for i in range(0, len(documents), batch_size):
                batch_num = i // batch_size + 1
                batch_docs = documents[i:i+batch_size]
                batch_meta = metadatas[i:i+batch_size]
                batch_ids = ids[i:i+batch_size]
                batch_emb = valid_embeddings[i:i+batch_size]
                
                try:
                    self.collection.add(
                        documents=batch_docs,
                        metadatas=batch_meta,
                        ids=batch_ids,
                        embeddings=batch_emb
                    )
                    
                    successful_batches += 1
                    logger.info(f"✅ Batch {batch_num}/{total_batches}: {len(batch_docs)} docs")
                    
                    # Small delay between batches
                    if i + batch_size < len(documents):
                        time.sleep(0.1)
                        
                except Exception as batch_error:
                    logger.error(f"❌ Error in batch {batch_num}: {batch_error}")
                    continue
            
            logger.info(f"✅ Added {successful_batches}/{total_batches} batches successfully")
            return successful_batches > 0
            
        except Exception as e:
            logger.error(f"❌ Error adding documents: {e}")
            return False
    
    def get_collection_stats(self) -> Dict:
        """Get collection statistics"""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def search(self, query_embedding: List[float], n_results: int = 10, 
               filter_metadata: Optional[Dict] = None) -> Dict:
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
            logger.error(f"Error searching: {e}")
            return {}
    
    def test_connection(self) -> bool:
        """Test connection"""
        try:
            heartbeat = self.client.heartbeat()
            count = self.collection.count()
            logger.info(f"✅ Test passed (heartbeat: {heartbeat}, docs: {count:,})")
            return True
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            return False