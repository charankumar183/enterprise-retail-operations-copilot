import re
import math
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
from backend.app.config import settings
from backend.app.services.vector_store import VectorStoreService
from backend.app.services.embedding_service import EmbeddingService

class HybridRetrieverService:
    def __init__(
        self,
        vector_store: VectorStoreService,
        embedding_service: EmbeddingService,
        alpha: float = settings.HYBRID_ALPHA
    ):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.alpha = alpha  # weight for vector search; (1 - alpha) for BM25
        self.corpus_chunks: List[Dict[str, Any]] = [] # list of {chunk_id, text, metadata}
        self.bm25_model = None
        self.tokenized_corpus = []

    def index_for_bm25(self, chunks: List[Dict[str, Any]]):
        """Index all chunks for BM25 keyword search."""
        self.corpus_chunks = chunks
        self.tokenized_corpus = [
            self._tokenize(c["text"]) for c in chunks
        ]
        if self.tokenized_corpus:
            self.bm25_model = BM25Okapi(self.tokenized_corpus)

    def _tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens if tokens else [""]

    def bm25_search(
        self,
        query: str,
        n_results: int = 10,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Keyword search using BM25 with metadata filtering."""
        if not self.bm25_model or not self.corpus_chunks:
            return []

        tokens = self._tokenize(query)
        scores = self.bm25_model.get_scores(tokens)
        max_score = max(scores) if len(scores) > 0 and max(scores) > 0 else 1.0

        results = []
        for idx, score in enumerate(scores):
            chunk = self.corpus_chunks[idx]
            meta = chunk.get("metadata", {})

            # Apply metadata filter
            if where_filter:
                match = True
                for k, v in where_filter.items():
                    if v and str(meta.get(k, "")).lower() != str(v).lower():
                        match = False
                        break
                if not match:
                    continue

            norm_score = float(score / max_score)
            results.append({
                "id": chunk.get("chunk_id", str(idx)),
                "document": chunk.get("text", ""),
                "metadata": meta,
                "score": norm_score,
                "bm25_score": float(score)
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:n_results]

    def hybrid_search(
        self,
        query: str,
        n_results: int = 5,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes hybrid search combining Semantic Vector Search and BM25 Keyword Search.
        Score = alpha * Semantic_Score + (1 - alpha) * BM25_Score.
        """
        # 1. Semantic Search
        q_emb = self.embedding_service.embed_query(query)
        vector_results = self.vector_store.query(
            query_embedding=q_emb,
            n_results=n_results * 2,
            where_filter=where_filter
        )

        # 2. BM25 Search
        bm25_results = self.bm25_search(
            query=query,
            n_results=n_results * 2,
            where_filter=where_filter
        )

        # Combine results by chunk ID
        combined_map: Dict[str, Dict[str, Any]] = {}

        for item in vector_results:
            cid = item["id"]
            combined_map[cid] = {
                "id": cid,
                "document": item["document"],
                "metadata": item["metadata"],
                "vector_score": item["score"],
                "bm25_score": 0.0,
            }

        for item in bm25_results:
            cid = item["id"]
            if cid in combined_map:
                combined_map[cid]["bm25_score"] = item["score"]
            else:
                combined_map[cid] = {
                    "id": cid,
                    "document": item["document"],
                    "metadata": item["metadata"],
                    "vector_score": 0.0,
                    "bm25_score": item["score"],
                }

        # Calculate weighted hybrid score
        fused_list = []
        for cid, data in combined_map.items():
            hybrid_score = (self.alpha * data["vector_score"]) + ((1.0 - self.alpha) * data["bm25_score"])
            data["hybrid_score"] = round(hybrid_score, 4)
            data["score"] = data["hybrid_score"]
            fused_list.append(data)

        # Rank by hybrid score descending
        fused_list.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return fused_list[:n_results]
