from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas.report import FeedbackCreate
from backend.app.models.audit import Feedback, AuditLog

router = APIRouter(prefix="/feedback", tags=["User Feedback & Auditing"])

@router.post("")
def submit_feedback(fb: FeedbackCreate, db: Session = Depends(get_db)):
    """Submit rating (1-5) and user comments for AI response quality monitoring."""
    item = Feedback(
        query_id=fb.query_id,
        rating=fb.rating,
        comment=fb.comment
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"status": "success", "feedback_id": item.id, "message": "Thank you for rating the copilot response."}

@router.get("/audit-logs")
def get_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve system operational logs (Queries, Latency, Routes, SQL queries)."""
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return logs
