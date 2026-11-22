from fastapi import APIRouter
from backend.app.schemas.evaluation import EvaluationComparisonReport
from backend.app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/evaluation", tags=["RAG Performance Evaluation"])

@router.get("/benchmark", response_model=EvaluationComparisonReport)
@router.post("/benchmark", response_model=EvaluationComparisonReport)
@router.get("/run", response_model=EvaluationComparisonReport)
@router.post("/run", response_model=EvaluationComparisonReport)
def run_model_benchmark():
    """
    Executes automated benchmark evaluation:
    - Precision@3, Recall@3, Accuracy, Latency, Hallucination Rate, MRR
    - Compares Sentence Transformers (all-MiniLM-L6-v2) vs BAAI BGE (bge-small-en-v1.5)
    """
    return EvaluationService.run_benchmark_evaluation()
