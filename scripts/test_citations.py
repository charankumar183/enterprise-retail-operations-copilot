import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.app.database import SessionLocal
from backend.app.services.vector_store import VectorStoreService
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.hybrid_retriever import HybridRetrieverService
from backend.app.services.advanced_rag import AdvancedRAGPipeline

db = SessionLocal()
emb = EmbeddingService()
vs = VectorStoreService()
hr = HybridRetrieverService(vs, emb)
rag = AdvancedRAGPipeline(vs, emb, hr)

queries = [
    "Show inventory availability for Product X across all warehouses.",
    "Which vendor supplies Product ABC?",
    "Generate a replenishment checklist for Store 210.",
    "Which products have the highest return rate this month?",
    "Show all delayed purchase orders for Supplier XYZ.",
    "Generate a daily operations report for Store 105."
]

for q in queries:
    docs, _, _ = rag.retrieve(query=q, session_id="test_sess", db=db, top_k=2)
    print(f"Q: '{q}'")
    for d in docs:
        m = d.get("metadata", {})
        print(f"  -> {m.get('filename')} | {m.get('section_title')} | Score: {d.get('confidence_score')}")

db.close()
