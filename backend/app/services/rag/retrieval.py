"""
RAG retrieval service

Handles semantic search, similarity filtering, and result ranking.
"""
from typing import List, Dict, Optional
from app.config import settings
from app.services.ai import embedding_service
from .vector_store import vector_store


class RetrievalService:
    """
    RAG retrieval with OpenAI embeddings and similarity threshold filtering

    Uses OpenAI's text-embedding-3-small model (1536 dimensions)
    to match the embeddings used during data collection
    """

    def __init__(self, similarity_threshold: float = None):
        """
        Initialize retrieval service

        Args:
            similarity_threshold: Minimum similarity score (0.0-1.0)
        """
        self.similarity_threshold = (
            similarity_threshold if similarity_threshold is not None
            else settings.RAG_SIMILARITY_THRESHOLD
        )

        print(f"[RETRIEVAL] Using OpenAI embeddings: {settings.OPENAI_EMBEDDING_MODEL}")
        print(f"[RETRIEVAL] Similarity threshold: {self.similarity_threshold:.2f}")

    async def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None,
        similarity_threshold: Optional[float] = None,
    ) -> Dict:
        """
        Search for relevant documents using OpenAI embeddings

        Args:
            query: Search query text
            n_results: Number of results to return (after filtering)
            filter_metadata: Optional metadata filters (e.g., {"city": "Paris"})
            similarity_threshold: Minimum similarity score (0.0-1.0)

        Returns:
            Dictionary with documents, metadatas, distances, and ids
        """
        threshold = (
            similarity_threshold
            if similarity_threshold is not None
            else self.similarity_threshold
        )

        print(f"[RETRIEVAL] 🔍 Searching for: '{query[:50]}...'")
        if filter_metadata:
            print(f"[RETRIEVAL] 🔧 Filters: {filter_metadata}")
        print(f"[RETRIEVAL] 📊 Threshold: {threshold:.2f}")

        try:
            # Generate embedding for query using OpenAI
            print(f"[RETRIEVAL] 🤖 Generating OpenAI embedding for query...")
            query_embedding = await embedding_service.get_embedding(query)
            print(f"[RETRIEVAL] ✅ Embedding generated ({len(query_embedding)} dimensions)")

            # Query more results than needed to account for filtering
            query_n = n_results * 2

            # Query vector store
            results = await vector_store.query(
                query_embeddings=[query_embedding],
                n_results=query_n,
                filter_metadata=filter_metadata
            )

            # Filter by similarity threshold
            filtered_results = self._filter_by_similarity(results, threshold, n_results)

            # Log results
            if filtered_results and filtered_results["documents"][0]:
                doc_count = len(filtered_results["documents"][0])
                print(
                    f"[RETRIEVAL] ✅ Returned {doc_count} documents (above {threshold:.2f} threshold)"
                )

                # Show top results
                for i, doc in enumerate(filtered_results["documents"][0][:3]):
                    if filtered_results.get("distances"):
                        similarity = self._distance_to_similarity(
                            filtered_results["distances"][0][i]
                        )
                        print(
                            f"[RETRIEVAL]   {i+1}. Similarity: {similarity:.3f} - {doc[:80]}..."
                        )
            else:
                print(f"[RETRIEVAL] ⚠️  No documents found above {threshold:.2f} threshold")

            return filtered_results

        except Exception as e:
            print(f"[RETRIEVAL] ❌ Error during search: {e}")
            import traceback
            traceback.print_exc()
            return {
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
                "ids": [[]],
            }

    def _distance_to_similarity(self, distance: float) -> float:
        """
        Convert cosine distance to similarity score (0.0-1.0)

        ChromaDB with cosine distance returns: distance = 1 - cosine_similarity
        Therefore: similarity = 1 - distance

        Range:
        - distance = 0.0 → similarity = 1.0 (identical)
        - distance = 0.5 → similarity = 0.5 (moderately similar)
        - distance = 1.0 → similarity = 0.0 (orthogonal)
        """
        return 1.0 - distance

    def _similarity_to_distance(self, similarity: float) -> float:
        """
        Convert similarity score to cosine distance

        Inverse of _distance_to_similarity
        """
        return 1.0 - similarity

    def _filter_by_similarity(
        self, results: Dict, threshold: float, max_results: int
    ) -> Dict:
        """
        Filter results by similarity threshold and limit to max_results

        ChromaDB returns results sorted by distance (lower = more similar)
        We filter out results below the similarity threshold

        Args:
            results: Raw results from vector store
            threshold: Minimum similarity score
            max_results: Maximum number of results to return

        Returns:
            Filtered results dictionary
        """
        if not results or not results.get("documents") or not results["documents"][0]:
            return {
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
                "ids": [[]],
            }

        # Extract results
        documents = results["documents"][0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        # Filter by threshold
        filtered_docs = []
        filtered_metas = []
        filtered_dists = []
        filtered_ids = []

        filtered_count = 0

        for i, distance in enumerate(distances):
            similarity = self._distance_to_similarity(distance)

            if similarity >= threshold:
                filtered_docs.append(documents[i])
                filtered_metas.append(metadatas[i] if i < len(metadatas) else {})
                filtered_dists.append(distance)
                filtered_ids.append(ids[i] if i < len(ids) else f"doc_{i}")

                # Stop when we have enough results
                if len(filtered_docs) >= max_results:
                    break
            else:
                filtered_count += 1

        if filtered_count > 0:
            print(f"[RETRIEVAL] 🔍 Filtered out {filtered_count} low-similarity documents")

        return {
            "documents": [filtered_docs],
            "metadatas": [filtered_metas],
            "distances": [filtered_dists],
            "ids": [filtered_ids],
        }

    def get_stats(self) -> Dict:
        """Get retrieval service statistics"""
        store_stats = vector_store.get_collection_stats()
        return {
            **store_stats,
            "similarity_threshold": self.similarity_threshold,
            "embedding_model": settings.OPENAI_EMBEDDING_MODEL,
            "embedding_dimensions": 1536
        }


# Singleton instance
retrieval_service = RetrievalService()
