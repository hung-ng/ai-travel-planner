import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict
from urllib.parse import urlparse
from app.config import settings

class RAGService:
    def __init__(self):
        """Initialize ChromaDB client"""
        # Parse the CHROMA_URL
        parsed_url = urlparse(settings.CHROMA_URL)
        host = parsed_url.hostname or "localhost"
        port = parsed_url.port or 8001
        
        print(f"[RAG] Connecting to ChromaDB at {host}:{port}")
        
        try:
            # Use the newer PersistentClient for HTTP connections
            self.client = chromadb.HttpClient(
                host=host,
                port=port,
                settings=ChromaSettings(
                    anonymized_telemetry=False
                )
            )
            
            # Test connection
            self.client.heartbeat()
            print(f"[RAG] Successfully connected to ChromaDB")
            
        except Exception as e:
            print(f"[RAG] Warning: Could not connect to ChromaDB via HTTP: {e}")
            print(f"[RAG] Falling back to local persistent storage")
            
            # Fallback to local storage
            self.client = chromadb.PersistentClient(
                path="./chroma_db",
                settings=ChromaSettings(
                    anonymized_telemetry=False
                )
            )
        
        # Get or create collection
        try:
            self.collection = self.client.get_or_create_collection(
                name="travel_knowledge",
                metadata={"description": "Travel information for RAG"}
            )
            print(f"[RAG] Collection 'travel_knowledge' ready")
            
        except Exception as e:
            print(f"[RAG] Error creating collection: {e}")
            raise
    
    async def add_documents(
        self, 
        documents: List[str],
        metadatas: List[Dict],
        ids: List[str]
    ):
        """Add travel knowledge to the vector database"""
        
        print(f"[RAG] Adding {len(documents)} documents to vector DB")
        
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"[RAG] Successfully stored {len(documents)} documents")
        except Exception as e:
            print(f"[RAG] Error adding documents: {e}")
            raise
    
    async def search(
        self, 
        query: str, 
        n_results: int = 5,
        filter_metadata: Dict = None
    ):
        """Search for similar documents using semantic similarity"""
        
        print(f"[RAG] Searching for: '{query}'")
        
        try:
            query_params = {
                "query_texts": [query],
                "n_results": n_results
            }
            
            if filter_metadata:
                query_params["where"] = filter_metadata
            
            results = self.collection.query(**query_params)
            
            if results and results['documents']:
                print(f"[RAG] Found {len(results['documents'][0])} relevant documents")
                for i, doc in enumerate(results['documents'][0][:3]):
                    distance = results['distances'][0][i] if results.get('distances') else 0
                    similarity = 1 - distance
                    print(f"[RAG]   {i+1}. (similarity: {similarity:.2f}) {doc[:80]}...")
            
            return results
            
        except Exception as e:
            print(f"[RAG] Error during search: {e}")
            # Return empty results
            return {
                'documents': [[]],
                'metadatas': [[]],
                'distances': [[]]
            }

# Create singleton instance
rag_service = RAGService()