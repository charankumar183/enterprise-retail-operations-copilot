import os
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.database import get_db
from backend.app.schemas.report import ReportRequest, ReportResponse
from backend.app.services.report_generator import ReportGeneratorService

router = APIRouter(prefix="/reports", tags=["Business Report Generation"])

@router.post("/generate", response_model=ReportResponse)
def generate_report(req: ReportRequest, db: Session = Depends(get_db)):
    """
    Generate business operational reports:
    - daily_store_ops (e.g. Store 105)
    - replenishment_checklist (e.g. Store 210)
    - delayed_purchase_orders (e.g. Supplier XYZ)
    """
    svc = ReportGeneratorService(db)
    target = req.target_id or "STORE-105"

    if req.report_type in ["daily_store_ops", "daily_operations"]:
        res = svc.generate_store_daily_report(target)
    elif req.report_type in ["replenishment_checklist", "replenishment"]:
        res = svc.generate_replenishment_checklist(target)
    elif req.report_type in ["delayed_purchase_orders", "delayed_pos"]:
        res = svc.generate_delayed_po_report(target if target != "STORE-105" else None)
    else:
        res = svc.generate_store_daily_report(target)

    return res

@router.get("/download/{report_id}")
def download_report_file(report_id: str):
    """Download generated operational report as JSON document."""
    file_path = os.path.join(settings.REPORTS_DIRECTORY, f"{report_id}.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    return FileResponse(
        path=file_path,
        filename=f"{report_id}.json",
        media_type="application/json"
    )
