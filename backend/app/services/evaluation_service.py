import time
from typing import List, Dict, Any
from backend.app.schemas.evaluation import ModelEvaluationMetric, EvaluationComparisonReport
from backend.app.services.embedding_service import EmbeddingModelBenchmark, EmbeddingService

# Benchmark dataset based on real enterprise retail operational scenarios
BENCHMARK_EVAL_DATASET = [
    {
        "query": "What are the standard receiving procedures for warehouse operations?",
        "target_doc_id": "doc_wh_receiving",
        "expected_terms": ["dock arrival", "bol", "seal inspection", "barcode scanning", "grn"]
    },
    {
        "query": "Why is Product P100 frequently going out of stock?",
        "target_doc_id": "doc_inv_replenish",
        "expected_terms": ["stockout", "reorder threshold", "lead time", "supplier delay"]
    },
    {
        "query": "Compare Promotion Policy Version 3 with Version 5.",
        "target_doc_id": "doc_promo_v5",
        "expected_terms": ["version 5", "version 3", "discount", "stackable coupon"]
    },
    {
        "query": "What are the delivery lead times and delayed penalty clauses for Supplier XYZ?",
        "target_doc_id": "doc_vendor_xyz",
        "expected_terms": ["lead time", "10 business days", "penalty", "1.5%"]
    },
    {
        "query": "Summarize customer complaints related to Product Y essential oil diffuser.",
        "target_doc_id": "doc_cust_service",
        "expected_terms": ["leakage", "reservoir", "mist", "defective"]
    },
    {
        "query": "What is the procedure for morning store opening routine and cash registers?",
        "target_doc_id": "doc_store_sop",
        "expected_terms": ["opening float", "safety walkthrough", "replenishment scan"]
    },
    {
        "query": "What are the dual sourcing procurement guidelines for Tier-1 retail SKUs?",
        "target_doc_id": "doc_proc_guideline",
        "expected_terms": ["dual sourcing", "tier-1", "35%", "reliability score"]
    },
    {
        "query": "How are electronic shelf labels synchronized during corporate price changes?",
        "target_doc_id": "doc_pricing_guide",
        "expected_terms": ["electronic shelf label", "esl", "synchronize", "pos registers"]
    }
]

BENCHMARK_CORPUS = [
    {
        "id": "doc_wh_receiving",
        "text": "Standard Operating Procedure: Inbound Freight & Warehouse Receiving Protocol. Driver presents BOL and PO Number. Supervisors inspect high-security bolt seal. UCC-128 barcode scanning and GRN posting within 2 hours."
    },
    {
        "id": "doc_inv_replenish",
        "text": "Enterprise Inventory Policy: Replenishment Thresholds & Stockout Escalation. Stores maintain 14 days of forward demand. High-velocity SKUs like P100 trigger reorder at 45 units. Root causes include supplier delay and demand spikes."
    },
    {
        "id": "doc_promo_v5",
        "text": "Promotion Governance Policy: Version 5. Maximum store discount is 15%. Discounts 16-35% require Category Director. Stackable coupons disallowed. Vendor co-op funding set at 70% vs 50% in legacy Version 3."
    },
    {
        "id": "doc_vendor_xyz",
        "text": "Master Procurement Agreement with Apex Consumer Goods (SUP-XYZ). Contracted lead time is 10 business days. Late delivery penalty is 1.5% per business day up to 15%."
    },
    {
        "id": "doc_cust_service",
        "text": "Customer Service Quality Manual: Quality Defect Handling for Product Y diffuser. Reservoir base leakage and broken misting. Immediate refund or replacement under Code QA-DEFECT without shelf restock."
    },
    {
        "id": "doc_store_sop",
        "text": "Store Operations Manual: Morning Store Opening Routine. Perimeter security walkthrough, cash drawer register floats $300, out of stock scanning across grocery and home care."
    },
    {
        "id": "doc_proc_guideline",
        "text": "Strategic Sourcing & Procurement: Dual Sourcing Mandate for Tier-1 SKUs. Secondary active suppliers must support at least 35% of volume. Suppliers with reliability under 85% placed on probation."
    },
    {
        "id": "doc_pricing_guide",
        "text": "Enterprise Retail Pricing Policy: Everyday Low Price. Corporate price changes effective at 00:01. Electronic shelf labels (ESLs) synchronize within 4 minutes."
    }
]

class EvaluationService:
    @staticmethod
    def run_benchmark_evaluation(models: List[str] = None) -> EvaluationComparisonReport:
        if not models:
            models = ["sentence-transformers/all-MiniLM-L6-v2", "BAAI/bge-small-en-v1.5"]

        raw_metrics = EmbeddingModelBenchmark.compare_models(
            test_queries=BENCHMARK_EVAL_DATASET,
            corpus=BENCHMARK_CORPUS,
            model_names=models
        )

        metric_objs = [ModelEvaluationMetric(**m) for m in raw_metrics]
        
        # Determine winning model based on F1 / accuracy and latency balance
        best_model = max(metric_objs, key=lambda m: (m.response_accuracy * 0.7 + (1.0 / (m.avg_latency_ms + 1.0)) * 0.3))

        summary = (
            f"Comprehensive evaluation benchmarked {len(metric_objs)} embedding models across {len(BENCHMARK_EVAL_DATASET)} "
            f"retail enterprise operational queries. Model '{best_model.model_name}' achieved top overall performance "
            f"with {best_model.retrieval_precision * 100:.1f}% Precision@3, {best_model.retrieval_recall * 100:.1f}% Recall@3, "
            f"{best_model.avg_latency_ms:.1f}ms average query latency, and a low hallucination rate of {best_model.hallucination_rate * 100:.1f}%."
        )

        return EvaluationComparisonReport(
            models=metric_objs,
            benchmark_dataset_size=len(BENCHMARK_EVAL_DATASET),
            summary_findings=summary,
            winner_model=best_model.model_name
        )
