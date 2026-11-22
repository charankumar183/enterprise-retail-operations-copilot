from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class ReportRequest(BaseModel):
    report_type: str # "daily_store_ops", "inventory_replenishment", "delayed_purchase_orders", "sales_analytics", "product_returns"
    target_id: Optional[str] = None # e.g. "STORE-105", "SUP-XYZ", "P100"
    date_range: Optional[str] = "today" # "today", "last_7_days", "this_month"

class ReportResponse(BaseModel):
    report_id: str
    title: str
    report_type: str
    target_id: Optional[str] = None
    generated_at: datetime
    summary: str
    key_metrics: Dict[str, Any]
    detailed_data: List[Dict[str, Any]]
    recommendations: List[str]
    download_url: str

class FeedbackCreate(BaseModel):
    query_id: Optional[int] = None
    rating: int # 1 to 5
    comment: Optional[str] = None
