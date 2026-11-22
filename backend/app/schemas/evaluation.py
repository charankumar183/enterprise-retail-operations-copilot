from pydantic import BaseModel
from typing import List, Dict, Any

class ModelEvaluationMetric(BaseModel):
    model_name: str
    retrieval_precision: float
    retrieval_recall: float
    response_accuracy: float
    avg_latency_ms: float
    hallucination_rate: float
    mrr: float # Mean Reciprocal Rank
    total_eval_queries: int

class EvaluationComparisonReport(BaseModel):
    models: List[ModelEvaluationMetric]
    benchmark_dataset_size: int
    summary_findings: str
    winner_model: str
