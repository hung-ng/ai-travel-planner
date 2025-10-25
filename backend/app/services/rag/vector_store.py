"""
ChromaDB vector store client

Manages connection and operations with the ChromaDB vector database.
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
from urllib.parse import urlparse
from app.config import settings


class VectorStore:
    """ChromaDB client for vector storage and retrieval"""

    def __init__(self, collection_name: str = "travel_knowledge"):
        """
        Initialize ChromaDB client

        Args:
            collection_name: Name of the collection to use
        """
        self.collection_name = collection_name
        self._connect()
        self._init_collection()

    def _connect(self):
        """Connect to ChromaDB"""
        parsed_url = urlparse(settings.CHROMA_URL)
        host = parsed_url.hostname or "localhost"
        port = parsed_url.port or 8001

        print(f"[VECTOR_STORE] Connecting to ChromaDB at {host}:{port}")

        try:
            self.client = chromadb.HttpClient(
                host=host,
                port=port,
                settings=ChromaSettings(anonymized_telemetry=False),
            )

            self.client.heartbeat()
            print(f"[VECTOR_STORE] ✅ Successfully connected to ChromaDB")

        except Exception as e:
            print(f"[VECTOR_STORE] ⚠️  Could not connect to ChromaDB via HTTP: {e}")
            print(f"[VECTOR_STORE] Falling back to local persistent storage")

            self.client = chromadb.PersistentClient(
                path="./chroma_db",
                settings=ChromaSettings(anonymized_telemetry=False)
            )

    def _init_collection(self):
        """Initialize or get the collection with COSINE distance"""
        try:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={
                    "description": "Travel information for RAG",
                    "hnsw:space": "cosine"  # CRITICAL: Use cosine distance for embeddings
                }
            )

            count = self.collection.count()
            print(f"[VECTOR_STORE] ✅ Collection '{self.collection_name}' ready ({count:,} documents)")
            print(f"[VECTOR_STORE] 📊 Distance metric: cosine")

        except Exception as e:
            print(f"[VECTOR_STORE] ❌ Error creating collection: {e}")
            raise

    async def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict],
        ids: List[str]
    ):
        """
        Add documents to vector DB

        Args:
            documents: List of document texts
            metadatas: List of metadata dicts
            ids: List of document IDs

        Note: This method expects embeddings to be generated elsewhere
        (e.g., during bulk data collection) for efficiency
        """
        print(f"[VECTOR_STORE] Adding {len(documents)} documents to vector DB")

        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"[VECTOR_STORE] ✅ Successfully stored {len(documents)} documents")
        except Exception as e:
            print(f"[VECTOR_STORE] ❌ Error adding documents: {e}")
            raise

    async def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 10,
        filter_metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Query the vector store with embeddings

        Args:
            query_embeddings: List of embedding vectors
            n_results: Number of results to return
            filter_metadata: Optional metadata filters (e.g., {"city": "Paris"})

        Returns:
            Dictionary with documents, metadatas, distances, and ids
        """
        try:
            query_params = {
                "query_embeddings": query_embeddings,
                "n_results": n_results
            }

            if filter_metadata:
                query_params["where"] = filter_metadata

            results = self.collection.query(**query_params)
            return results

        except Exception as e:
            print(f"[VECTOR_STORE] ❌ Error during query: {e}")
            raise

    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "total_documents": count,
            }
        except Exception as e:
            print(f"[VECTOR_STORE] ❌ Error getting stats: {e}")
            return {}


# Singleton instance
vector_store = VectorStore()
