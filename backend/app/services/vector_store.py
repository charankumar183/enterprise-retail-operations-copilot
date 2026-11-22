import os
import json
from typing import List, Dict, Any, Optional
import numpy as np
from backend.app.config import settings

class VectorStoreService:
    def __init__(self, persist_dir: str = settings.CHROMA_PERSIST_DIRECTORY):
        self.persist_dir = persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        self.chroma_client = None
        self.collection = None
        self._local_index_path = os.path.join(self.persist_dir, "local_vector_index.json")
        self._local_embeddings = [] # list of {id, vector, metadata, document}
        
        self._init_store()

    def _init_store(self):
        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(path=self.persist_dir)
            self.collection = self.chroma_client.get_or_create_collection(
                name=settings.VECTOR_DB_COLLECTION,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            self.chroma_client = None
            self._load_local_index()

    def _load_local_index(self):
        if os.path.exists(self._local_index_path):
            try:
                with open(self._local_index_path, "r", encoding="utf-8") as f:
                    self._local_embeddings = json.load(f)
            except Exception:
                self._local_embeddings = []

    def _save_local_index(self):
        try:
            with open(self._local_index_path, "w", encoding="utf-8") as f:
                json.dump(self._local_embeddings, f)
        except Exception:
            pass

    def add_documents(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        documents: List[str]
    ):
        if self.collection:
            try:
                # Sanitize metadata for chromadb (convert None to empty string)
                cleaned_meta = []
                for m in metadatas:
                    cleaned = {k: ("" if v is None else v) for k, v in m.items()}
                    cleaned_meta.append(cleaned)
                self.collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    metadatas=cleaned_meta,
                    documents=documents
                )
                return
            except Exception:
                pass

        # Local storage fallback
        existing_ids = {item["id"]: idx for idx, item in enumerate(self._local_embeddings)}
        for cid, emb, meta, doc in zip(ids, embeddings, metadatas, documents):
            record = {
                "id": cid,
                "embedding": emb,
                "metadata": meta,
                "document": doc
            }
            if cid in existing_ids:
                self._local_embeddings[existing_ids[cid]] = record
            else:
                self._local_embeddings.append(record)
        self._save_local_index()

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes semantic vector search with metadata filtering.
        Returns list of {id, document, metadata, distance, score}
        """
        if self.collection:
            try:
                chroma_where = None
                if where_filter:
                    # Filter out empty string filters
                    active = {k: v for k, v in where_filter.items() if v}
                    if len(active) == 1:
                        chroma_where = active
                    elif len(active) > 1:
                        chroma_where = {"$and": [{k: v} for k, v in active.items()]}

                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    where=chroma_where
                )
                formatted = []
                if results and "ids" in results and results["ids"] and results["ids"][0]:
                    count = len(results["ids"][0])
                    for i in range(count):
                        dist = results["distances"][0][i] if "distances" in results and results["distances"] else 0.5
                        score = max(0.0, 1.0 - dist)
                        formatted.append({
                            "id": results["ids"][0][i],
                            "document": results["documents"][0][i] if "documents" in results else "",
                            "metadata": results["metadatas"][0][i] if "metadatas" in results else {},
                            "distance": dist,
                            "score": score
                        })
                return formatted
            except Exception:
                pass

        # Fallback local index search
        if not self._local_embeddings:
            self._load_local_index()

        candidates = self._local_embeddings
        if where_filter:
            filtered = []
            for item in candidates:
                meta = item.get("metadata", {})
                match = True
                for k, v in where_filter.items():
                    if v and str(meta.get(k, "")).lower() != str(v).lower():
                        match = False
                        break
                if match:
                    filtered.append(item)
            candidates = filtered

        if not candidates:
            return []

        q_vec = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec) + 1e-9

        scored = []
        for item in candidates:
            emb = np.array(item["embedding"], dtype=np.float32)
            emb_norm = np.linalg.norm(emb) + 1e-9
            sim = float(np.dot(q_vec, emb) / (q_norm * emb_norm))
            scored.append({
                "id": item["id"],
                "document": item["document"],
                "metadata": item["metadata"],
                "distance": 1.0 - sim,
                "score": max(0.0, sim)
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:n_results]

    def delete_document_chunks(self, doc_id: int):
        if self.collection:
            try:
                self.collection.delete(where={"doc_id": doc_id})
            except Exception:
                pass

        if not self._local_embeddings:
            self._load_local_index()
        self._local_embeddings = [
            item for item in self._local_embeddings 
            if item.get("metadata", {}).get("doc_id") != doc_id
        ]
        self._save_local_index()
