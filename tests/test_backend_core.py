import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal, engine, Base
from backend.app.services.seeding_service import SeedingService
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vector_store import VectorStoreService
from backend.app.services.hybrid_retriever import HybridRetrieverService
from backend.app.services.advanced_rag import AdvancedRAGPipeline
from backend.app.services.agentic_router import AgenticRouterService
from backend.app.services.evaluation_service import EvaluationService

def run_all_tests():
    print("\n" + "="*70)
    print("STEP 1: INITIALIZE DATABASE AND SEED ENTERPRISE DATA")
    print("="*70)
    SeedingService.init_database()
    db = SessionLocal()
    
    SeedingService.seed_users(db)
    SeedingService.seed_structured_data(db)
    SeedingService.generate_unstructured_documents()
    
    emb_svc = EmbeddingService()
    v_store = VectorStoreService()
    hybrid_ret = HybridRetrieverService(v_store, emb_svc)
    SeedingService.index_all_documents(db, emb_svc, v_store, hybrid_ret)
    
    rag_pipeline = AdvancedRAGPipeline(v_store, emb_svc, hybrid_ret)
    router = AgenticRouterService(rag_pipeline, db)

    test_queries = [
        "What are the standard receiving procedures for warehouse operations?",
        "Show inventory availability for Product X across all warehouses.",
        "Why is Product P100 frequently going out of stock?",
        "Which vendor supplies Product ABC?",
        "Compare Promotion Policy Version 3 with Version 5.",
        "Generate a replenishment checklist for Store 210.",
        "Which products have the highest return rate this month?",
        "Summarize customer complaints related to Product Y.",
        "Show all delayed purchase orders for Supplier XYZ.",
        "Generate a daily operations report for Store 105."
    ]

    print("\n" + "="*70)
    print("STEP 2: TEST AGENTIC RAG & BENCHMARK QUESTIONS FROM PDF")
    print("="*70)
    for idx, q in enumerate(test_queries, 1):
        print(f"\n[Test {idx}/10] Query: '{q}'")
        res = router.process_query(q, session_id="test_suite_session")
        print(f"  -> Detected Intent: {res.detected_intent}")
        print(f"  -> Route Taken:     {res.route_taken}")
        print(f"  -> Citations:       {len(res.citations)} source citations")
        for c in res.citations[:2]:
            print(f"     * [{c.document_name} | {c.section_reference} (p.{c.page_number})] Confidence: {c.confidence_score}")
        if res.sql_query:
            print(f"  -> Executed SQL:    {res.sql_query}")
        print(f"  -> Latency:         {res.response_latency_ms} ms")
        print(f"  -> Response Preview: {res.response[:120]}...")

    print("\n" + "="*70)
    print("STEP 3: TEST EMBEDDING MODEL COMPARISON & PERFORMANCE EVALUATION")
    print("="*70)
    report = EvaluationService.run_benchmark_evaluation()
    print(f"Total Benchmark Queries: {report.benchmark_dataset_size}")
    print(f"Winner Model:           {report.winner_model}")
    for m in report.models:
        print(f"  * Model: {m.model_name}")
        print(f"    - Precision@3:       {m.retrieval_precision:.4f}")
        print(f"    - Recall@3:          {m.retrieval_recall:.4f}")
        print(f"    - Response Accuracy: {m.response_accuracy:.4f}")
        print(f"    - Avg Latency:       {m.avg_latency_ms:.2f} ms")
        print(f"    - Hallucination:     {m.hallucination_rate:.4f}")
        print(f"    - MRR:               {m.mrr:.4f}")

    db.close()
    print("\n" + "="*70)
    print("ALL CORE BACKEND, ADVANCED RAG & SQL ANALYTICS TESTS PASSED!")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_all_tests()
