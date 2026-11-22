from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.database import get_db
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.agentic_router import AgenticRouterService
from backend.app.services.advanced_rag import AdvancedRAGPipeline
from backend.app.services.vector_store import VectorStoreService
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.hybrid_retriever import HybridRetrieverService
from backend.app.services.hybrid_retriever import HybridRetrieverService
from backend.app.services.auth_service import get_optional_current_user
from backend.app.models.auth import User

router = APIRouter(prefix="/chat", tags=["AI Copilot & Agentic RAG"])

# Singleton services cache
_embedding_service = None
_vector_store = None
_hybrid_retriever = None
_rag_pipeline = None

def get_rag_pipeline(db: Session = Depends(get_db)) -> AdvancedRAGPipeline:
    global _embedding_service, _vector_store, _hybrid_retriever, _rag_pipeline
    if _rag_pipeline is None:
        _embedding_service = EmbeddingService()
        _vector_store = VectorStoreService()
        _hybrid_retriever = HybridRetrieverService(_vector_store, _embedding_service)
        _rag_pipeline = AdvancedRAGPipeline(_vector_store, _embedding_service, _hybrid_retriever)
    return _rag_pipeline

@router.post("", response_model=ChatResponse)
def handle_chat_message(
    chat_req: ChatRequest,
    db: Session = Depends(get_db),
    rag_pipe: AdvancedRAGPipeline = Depends(get_rag_pipeline),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Primary Agentic RAG Endpoint:
    - User Query
    - Intent Detection Layer (RAG Search, SQL Analytics, Report Generator, Combined)
    - Dynamic Routing without LangGraph
    - Source Citations with Document Name, Section, Page Number, and Confidence Score.
    """
    # Build metadata filters dict from request
    filters = {}
    if chat_req.filter_category:
        filters["product_category"] = chat_req.filter_category
    if chat_req.filter_store:
        filters["store"] = chat_req.filter_store
    if chat_req.filter_warehouse:
        filters["warehouse"] = chat_req.filter_warehouse
    if chat_req.filter_supplier:
        filters["supplier"] = chat_req.filter_supplier
    if chat_req.filter_department:
        filters["department"] = chat_req.filter_department
    if chat_req.filter_region:
        filters["region"] = chat_req.filter_region
    if chat_req.filter_doc_type:
        filters["doc_type"] = chat_req.filter_doc_type
    if chat_req.filter_promotion:
        filters["promotion_campaign"] = chat_req.filter_promotion

    agent_router = AgenticRouterService(rag_pipe, db)
    
    user_info = {
        "username": current_user.username if current_user else "manager",
        "role": current_user.role if current_user else "Store Manager",
        "id": current_user.id if current_user else None
    }
    
    response = agent_router.process_query(
        query=chat_req.query,
        session_id=chat_req.conversation_id or "default_session",
        filters=filters if filters else None,
        user_info=user_info
    )
    return response

@router.get("/history/{session_id}")
def get_chat_history(session_id: str, rag_pipe: AdvancedRAGPipeline = Depends(get_rag_pipeline)):
    """Retrieve multi-turn conversation memory for the given session."""
    history = rag_pipe.conversation_memory.get(session_id, [])
    return {"session_id": session_id, "messages": history}
