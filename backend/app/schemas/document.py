from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    doc_type: str
    version: str
    total_chunks: int
    status: str
    message: str

class DocumentRecordOut(BaseModel):
    id: int
    filename: str
    file_type: str
    doc_type: str
    department: Optional[str] = None
    product_category: Optional[str] = None
    store: Optional[str] = None
    warehouse: Optional[str] = None
    supplier: Optional[str] = None
    region: Optional[str] = None
    promotion_campaign: Optional[str] = None
    version: str
    file_size_bytes: int
    total_chunks: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentUpdate(BaseModel):
    doc_type: Optional[str] = None
    version: Optional[str] = None
    department: Optional[str] = None
    product_category: Optional[str] = None
    store: Optional[str] = None
    warehouse: Optional[str] = None
    supplier: Optional[str] = None
