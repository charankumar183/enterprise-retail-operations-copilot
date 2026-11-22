import re
import time
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.services.vector_store import VectorStoreService
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.hybrid_retriever import HybridRetrieverService
from backend.app.models.document import DocumentChunk, DocumentRecord

class AdvancedRAGPipeline:
    def __init__(
        self,
        vector_store: VectorStoreService,
        embedding_service: EmbeddingService,
        hybrid_retriever: HybridRetrieverService
    ):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.hybrid_retriever = hybrid_retriever
        self.conversation_memory: Dict[str, List[Dict[str, str]]] = {}

    # 5.3 Query Expansion
    def expand_query(self, query: str) -> List[str]:
        """
        Rewrites a user query into multiple relevant search variations for broad recall.
        Example: "Product out of stock" -> ["Inventory shortage", "Stock availability", "Replenishment issue", ...]
        """
        variations = [query]
        q_lower = query.lower()

        expansion_rules = [
            (
                r"\b(out of stock|stockout|oos|no stock)\b",
                [
                    "inventory shortage",
                    "stock availability",
                    "replenishment issue",
                    "warehouse stock level",
                    "inventory allocation"
                ]
            ),
            (
                r"\b(receiving|dock|unloading|inbound)\b",
                [
                    "warehouse receiving SOP",
                    "standard receiving procedures",
                    "inbound freight inspection",
                    "dock delivery verification checklist",
                    "warehouse goods intake protocol"
                ]
            ),
            (
                r"\b(promotion|promo|discount|markdown)\b",
                [
                    "promotional campaign policy",
                    "discount approval guideline",
                    "merchandising promotion calendar",
                    "markdown pricing threshold"
                ]
            ),
            (
                r"\b(supplier|vendor|lead time|po delay)\b",
                [
                    "vendor service level agreement",
                    "supplier lead time compliance",
                    "purchase order delayed shipment clause",
                    "procurement penalty terms"
                ]
            ),
            (
                r"\b(return|refund|defective|damaged)\b",
                [
                    "store customer return policy",
                    "defective merchandise return procedure",
                    "restocking fee guideline",
                    "damaged product disposal protocol"
                ]
            ),
            (
                r"\b(store operations|opening checklist|closing checklist|daily routine)\b",
                [
                    "store standard operating procedure",
                    "daily store operations checklist",
                    "shift handover protocol",
                    "store inventory reconciliation"
                ]
            )
        ]

        for pattern, terms in expansion_rules:
            if re.search(pattern, q_lower):
                variations.extend(terms)

        # De-duplicate while preserving order
        seen = set()
        unique_expansions = []
        for v in variations:
            if v.lower() not in seen:
                seen.add(v.lower())
                unique_expansions.append(v)

        return unique_expansions[:5]

    # 5.10 Conversation Memory & Context-Aware Query Reformulation
    def add_to_memory(self, session_id: str, role: str, content: str):
        if session_id not in self.conversation_memory:
            self.conversation_memory[session_id] = []
        self.conversation_memory[session_id].append({"role": role, "content": content})
        # Keep last 10 messages
        if len(self.conversation_memory[session_id]) > 10:
            self.conversation_memory[session_id] = self.conversation_memory[session_id][-10:]

    def reformulate_with_memory(self, session_id: str, current_query: str) -> str:
        """Resolves pronouns like 'it', 'they', 'that product' using conversation memory."""
        history = self.conversation_memory.get(session_id, [])
        if not history:
            return current_query

        # Check for coreference indicators
        pronouns = ["it", "this", "that", "its", "they", "them", "these", "the vendor", "the store", "the product"]
        words = set(re.findall(r'\b\w+\b', current_query.lower()))
        needs_context = any(p in words for p in pronouns) or len(words) <= 3

        if needs_context:
            # Find subject from last 2 user/assistant messages
            last_context = " ".join([m["content"] for m in history[-2:]])
            prod_entities = re.findall(r'\b(?:P\d+|Product [A-Za-z0-9_-]+|PROD-[A-Za-z0-9_-]+)\b', last_context, re.IGNORECASE)
            other_entities = re.findall(r'\b(?:Store \d+|WH-\w+|SUP-\w+)\b', last_context, re.IGNORECASE)
            contextual_subject = prod_entities[-1] if prod_entities else (other_entities[-1] if other_entities else None)
            if contextual_subject:
                return f"{current_query} regarding {contextual_subject}"

        return current_query

    # 5.4 Multi-Query Retrieval
    def multi_query_retrieve(
        self,
        queries: List[str],
        top_k: int = 5,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes hybrid search across all expanded queries and fuses/deduplicates results.
        """
        all_candidates: Dict[str, Dict[str, Any]] = {}

        for q in queries:
            results = self.hybrid_retriever.hybrid_search(
                query=q,
                n_results=top_k,
                where_filter=where_filter
            )
            for item in results:
                cid = item["id"]
                if cid not in all_candidates:
                    all_candidates[cid] = item
                else:
                    # Update score if higher match found
                    if item.get("score", 0) > all_candidates[cid].get("score", 0):
                        all_candidates[cid] = item

        deduped = list(all_candidates.values())
        deduped.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        return deduped

    # 5.5 Parent-Child Retrieval Resolution
    def resolve_parent_chunks(
        self,
        retrieved_child_chunks: List[Dict[str, Any]],
        db: Session
    ) -> List[Dict[str, Any]]:
        """
        Given retrieved child chunks, fetches their complete parent sections for full business context.
        """
        parent_resolved = []
        seen_parent_ids = set()

        for chunk in retrieved_child_chunks:
            meta = chunk.get("metadata", {})
            parent_id = meta.get("parent_id")

            if parent_id and parent_id not in seen_parent_ids:
                seen_parent_ids.add(parent_id)
                # Fetch parent chunk from SQL
                parent_record = db.query(DocumentChunk).filter(DocumentChunk.chunk_id == parent_id).first()
                if parent_record:
                    parent_resolved.append({
                        "id": parent_id,
                        "child_id": chunk["id"],
                        "document": parent_record.content, # Return full parent context
                        "child_snippet": chunk.get("document", ""),
                        "metadata": {
                            **meta,
                            "section_title": parent_record.section_title,
                            "page_number": parent_record.page_number
                        },
                        "score": chunk.get("score", 0.5)
                    })
                else:
                    parent_resolved.append(chunk)
            elif not parent_id:
                parent_resolved.append(chunk)

        return parent_resolved

    # 5.8 Re-ranking
    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Re-ranks retrieved documents by cross-matching key semantic tokens and proximity.
        """
        if not candidates:
            return []

        q_terms = set(re.findall(r'\b\w+\b', query.lower()))

        for item in candidates:
            doc_text = item.get("document", "").lower()
            doc_title = item.get("metadata", {}).get("section_title", "").lower()
            doc_terms = set(re.findall(r'\b\w+\b', doc_text))
            title_terms = set(re.findall(r'\b\w+\b', doc_title))

            # Overlap in content
            content_overlap = len(q_terms.intersection(doc_terms)) / (len(q_terms) + 1e-9)
            # Boost if terms appear in heading/title
            title_overlap = len(q_terms.intersection(title_terms)) / (len(q_terms) + 1e-9)
            
            orig_score = item.get("score", 0.5)
            # Reranked score calculation
            rerank_score = (0.5 * orig_score) + (0.35 * content_overlap) + (0.15 * title_overlap)
            item["rerank_score"] = round(rerank_score, 4)
            item["confidence_score"] = min(0.98, max(0.40, round(rerank_score * 1.15, 2)))

        candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
        return candidates[:top_k]

    # 5.9 Context Compression
    def compress_context(self, documents: List[Dict[str, Any]], query: str, max_chars: int = 2500) -> List[Dict[str, Any]]:
        """
        Removes irrelevant sentences while preserving critical business rules, procedures, numbers, and dates.
        """
        compressed = []
        q_terms = set(re.findall(r'\b\w+\b', query.lower()))

        for doc in documents:
            text = doc.get("document", "")
            sentences = re.split(r'(?<=[.!?])\s+', text)
            kept_sentences = []

            for sent in sentences:
                s_lower = sent.lower()
                s_terms = set(re.findall(r'\b\w+\b', s_lower))
                # Keep if sentence contains query terms, digits, or policy keywords
                has_term = len(q_terms.intersection(s_terms)) > 0
                has_metric = bool(re.search(r'\d+', sent))
                has_policy_kw = any(kw in s_lower for kw in ["must", "required", "policy", "procedure", "sop", "within", "step", "threshold", "percent", "%", "approved"])
                
                if has_term or has_metric or has_policy_kw:
                    kept_sentences.append(sent)

            compressed_text = " ".join(kept_sentences) if kept_sentences else text[:500]
            if len(compressed_text) > max_chars:
                compressed_text = compressed_text[:max_chars] + "..."

            doc_copy = dict(doc)
            doc_copy["compressed_content"] = compressed_text
            compressed.append(doc_copy)

        return compressed

    # Complete End-to-End Advanced RAG Retrieve Pipeline
    def retrieve(
        self,
        query: str,
        session_id: str,
        db: Session,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 3
    ) -> Tuple[List[Dict[str, Any]], List[str], float]:
        """
        Full orchestration of 5.1 through 5.10:
        Memory Reformulation -> Query Expansion -> Multi-Query Retrieval -> 
        Parent-Child Resolution -> Re-ranking -> Context Compression.
        """
        t0 = time.time()
        # 1. Context-aware memory
        effective_query = self.reformulate_with_memory(session_id, query)

        # 2. Query expansion
        expanded_queries = self.expand_query(effective_query)

        # 3. Multi-query hybrid retrieval with metadata filtering (5.6 & 5.7)
        where_filter = {}
        if filters:
            for k, v in filters.items():
                if v:
                    where_filter[k] = v

        child_candidates = self.multi_query_retrieve(
            queries=expanded_queries,
            top_k=8,
            where_filter=where_filter if where_filter else None
        )

        # 4. Parent-Child retrieval resolution (5.5)
        parent_docs = self.resolve_parent_chunks(child_candidates, db)

        # 5. Re-ranking (5.8)
        reranked = self.rerank(effective_query, parent_docs, top_k=top_k)

        # 6. Context compression (5.9)
        compressed = self.compress_context(reranked, effective_query)

        latency_ms = (time.time() - t0) * 1000.0
        return compressed, expanded_queries, round(latency_ms, 2)
