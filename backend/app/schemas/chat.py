from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SourceCitation(BaseModel):
    document_name: str
    section_reference: str
    page_number: int
    confidence_score: float
    snippet: Optional[str] = None

class Message(BaseModel):
    role: str # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = "default_session"
    history: Optional[List[Message]] = []
    # Metadata filters (Mandatory per PDF)
    filter_category: Optional[str] = None
    filter_store: Optional[str] = None
    filter_warehouse: Optional[str] = None
    filter_supplier: Optional[str] = None
    filter_department: Optional[str] = None
    filter_region: Optional[str] = None
    filter_doc_type: Optional[str] = None
    filter_date: Optional[str] = None
    filter_promotion: Optional[str] = None

class ChatResponse(BaseModel):
    query: str
    detected_intent: str # RAG Search, SQL Analytics, Report Generator
    route_taken: str
    response: str
    citations: List[SourceCitation] = []
    sql_query: Optional[str] = None
    sql_results: Optional[List[Dict[str, Any]]] = None
    expanded_queries: Optional[List[str]] = []
    retrieval_time_ms: float = 0.0
    response_latency_ms: float = 0.0
    conversation_id: str
    query_id: Optional[int] = None
