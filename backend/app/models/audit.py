from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from datetime import datetime
from backend.app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True, nullable=True)
    username = Column(String(100), default="anonymous")
    user_role = Column(String(50), default="Store Manager")
    query_text = Column(Text, nullable=False)
    detected_intent = Column(String(100), nullable=False) # RAG Search, SQL Analytics, Report Generator
    route_taken = Column(String(100), nullable=False)
    sql_query = Column(Text, nullable=True)
    retrieved_documents = Column(Text, nullable=True) # JSON list of cited sources
    generated_response = Column(Text, nullable=True)
    retrieval_time_ms = Column(Float, default=0.0)
    response_latency_ms = Column(Float, default=0.0)
    status_code = Column(Integer, default=200)
    api_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True, nullable=True)
    query_id = Column(Integer, ForeignKey("audit_logs.id"), nullable=True)
    rating = Column(Integer, nullable=False) # 1 to 5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
