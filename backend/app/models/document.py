from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base

class DocumentRecord(Base):
    __tablename__ = "document_records"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    file_type = Column(String(50), nullable=False) # pdf, docx, txt, csv, excel
    doc_type = Column(String(100), nullable=False, index=True) 
    # e.g. "Store SOPs", "Warehouse Manuals", "Inventory Policies", "Pricing Guidelines", "Promotion Documents",
    # "Vendor Contracts", "Product Catalogs", "Customer Service Manuals", "Logistics SOPs", "Procurement Guidelines",
    # "Merchandising Documents", "Supply Chain Reports"
    department = Column(String(100), nullable=True, index=True)
    product_category = Column(String(100), nullable=True, index=True)
    store = Column(String(100), nullable=True, index=True)
    warehouse = Column(String(100), nullable=True, index=True)
    supplier = Column(String(100), nullable=True, index=True)
    region = Column(String(100), nullable=True, index=True)
    promotion_campaign = Column(String(100), nullable=True, index=True)
    version = Column(String(50), default="1.0") # e.g. "Version 3", "Version 5"
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    uploaded_by = Column(String(100), default="Administrator")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(50), default="indexed") # uploaded, parsing, indexed, error, archived

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, ForeignKey("document_records.id"), index=True, nullable=False)
    chunk_id = Column(String(100), unique=True, index=True, nullable=False) # doc_{id}_chunk_{index}
    parent_chunk_id = Column(String(100), index=True, nullable=True) # for parent-child retrieval
    is_parent = Column(Boolean, default=False)
    chunk_index = Column(Integer, nullable=False)
    section_title = Column(String(255), default="General Section")
    page_number = Column(Integer, default=1)
    content = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=True) # JSON serialized filters: store, warehouse, supplier, etc.

    document = relationship("DocumentRecord", back_populates="chunks")
