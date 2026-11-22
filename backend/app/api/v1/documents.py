import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models.document import DocumentRecord, DocumentChunk
from backend.app.schemas.document import DocumentUploadResponse, DocumentRecordOut, DocumentUpdate
from backend.app.services.document_parser import DocumentParserService
from backend.app.services.chunking_service import ChunkingService
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vector_store import VectorStoreService
from backend.app.services.hybrid_retriever import HybridRetrieverService
from backend.app.services.auth_service import require_roles, get_current_user
from backend.app.models.auth import User

router = APIRouter(prefix="/documents", tags=["Document Management & Ingestion"])

@router.get("", response_model=List[DocumentRecordOut])
def list_documents(db: Session = Depends(get_db)):
    """List all managed enterprise retail documents with version, category, and chunk counts."""
    return db.query(DocumentRecord).order_by(DocumentRecord.created_at.desc()).all()

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: Optional[str] = Form("Store SOPs"),
    department: Optional[str] = Form("Operations"),
    product_category: Optional[str] = Form("General"),
    store: Optional[str] = Form(""),
    warehouse: Optional[str] = Form(""),
    supplier: Optional[str] = Form(""),
    region: Optional[str] = Form("National"),
    version: Optional[str] = Form("1.0"),
    db: Session = Depends(get_db)
):
    """
    Ingest enterprise document (PDF, DOCX, TXT, CSV, Excel).
    Executes automatic parsing, metadata tagging, chunking, embedding, and indexing.
    """
    allowed_exts = [".pdf", ".docx", ".doc", ".txt", ".csv", ".xlsx", ".xls"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{ext}'. Supported: PDF, DOCX, TXT, CSV, Excel."
        )

    # Save to documents directory
    os.makedirs(settings.DOCS_DIRECTORY, exist_ok=True)
    file_path = os.path.join(settings.DOCS_DIRECTORY, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)

    # Check for existing document version
    existing = db.query(DocumentRecord).filter(DocumentRecord.filename == file.filename).first()
    if existing:
        db.query(DocumentChunk).filter(DocumentChunk.doc_id == existing.id).delete()
        doc_record = existing
        doc_record.version = version
        doc_record.doc_type = doc_type
        doc_record.department = department
        doc_record.file_size_bytes = file_size
        doc_record.status = "reindexing"
    else:
        doc_record = DocumentRecord(
            filename=file.filename,
            file_type=ext.replace(".", ""),
            doc_type=doc_type,
            department=department,
            product_category=product_category,
            store=store,
            warehouse=warehouse,
            supplier=supplier,
            region=region,
            version=version,
            file_path=file_path,
            file_size_bytes=file_size,
            status="parsing"
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)

    # Parse document
    sections = DocumentParserService.parse_file(file_path)
    
    # Chunking
    chunker = ChunkingService()
    meta_dict = {
        "doc_id": doc_record.id,
        "filename": doc_record.filename,
        "file_type": doc_record.file_type,
        "doc_type": doc_record.doc_type,
        "department": doc_record.department or "",
        "store": doc_record.store or "",
        "warehouse": doc_record.warehouse or "",
        "supplier": doc_record.supplier or "",
        "region": doc_record.region or "",
        "product_category": doc_record.product_category or "",
        "version": doc_record.version or "1.0"
    }

    parent_chunks, child_chunks = chunker.create_parent_child_chunks(
        doc_id=doc_record.id,
        sections=sections,
        doc_metadata=meta_dict
    )

    # Save parent chunks to SQL
    for p in parent_chunks:
        db_chunk = DocumentChunk(
            doc_id=doc_record.id,
            chunk_id=p.chunk_id,
            parent_chunk_id=None,
            is_parent=True,
            chunk_index=int(p.chunk_id.split("_")[-1]),
            section_title=p.section_title,
            page_number=p.page_number,
            content=p.content,
            metadata_json=str(p.metadata)
        )
        db.add(db_chunk)

    # Embed and index child chunks
    emb_svc = EmbeddingService()
    v_store = VectorStoreService()
    hybrid_retriever = HybridRetrieverService(v_store, emb_svc)

    child_texts = [c.content for c in child_chunks]
    child_ids = [c.chunk_id for c in child_chunks]
    child_metas = [c.metadata for c in child_chunks]

    embeddings = emb_svc.embed_documents(child_texts)

    all_bm25 = []
    for c in child_chunks:
        db_chunk = DocumentChunk(
            doc_id=doc_record.id,
            chunk_id=c.chunk_id,
            parent_chunk_id=c.parent_chunk_id,
            is_parent=False,
            chunk_index=int(c.chunk_id.split("_")[-1]),
            section_title=c.section_title,
            page_number=c.page_number,
            content=c.content,
            metadata_json=str(c.metadata)
        )
        db.add(db_chunk)
        all_bm25.append({"chunk_id": c.chunk_id, "text": c.content, "metadata": c.metadata})

    v_store.add_documents(
        ids=child_ids,
        embeddings=embeddings,
        metadatas=child_metas,
        documents=child_texts
    )

    total_chunks = len(parent_chunks) + len(child_chunks)
    doc_record.total_chunks = total_chunks
    doc_record.status = "indexed"
    db.commit()

    return DocumentUploadResponse(
        id=doc_record.id,
        filename=doc_record.filename,
        file_type=doc_record.file_type,
        doc_type=doc_record.doc_type,
        version=doc_record.version,
        total_chunks=total_chunks,
        status="indexed",
        message=f"Document '{file.filename}' parsed and indexed successfully ({total_chunks} chunks)."
    )

@router.put("/{doc_id}", response_model=DocumentRecordOut)
def update_document_metadata(doc_id: int, update_data: DocumentUpdate, db: Session = Depends(get_db)):
    """Update document version and metadata categorization."""
    doc = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if update_data.doc_type:
        doc.doc_type = update_data.doc_type
    if update_data.version:
        doc.version = update_data.version
    if update_data.department:
        doc.department = update_data.department
    if update_data.product_category:
        doc.product_category = update_data.product_category
    if update_data.store:
        doc.store = update_data.store
    if update_data.warehouse:
        doc.warehouse = update_data.warehouse
    if update_data.supplier:
        doc.supplier = update_data.supplier

    db.commit()
    db.refresh(doc)
    return doc

@router.delete("/{doc_id}")
def delete_document(
    doc_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator"]))
):
    """Deletes document and purges all associated chunks from vector database and SQL."""
    doc = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Remove from vector store
    v_store = VectorStoreService()
    v_store.delete_document_chunks(doc.id)

    # Remove physical file if exists
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    # Remove chunks and record from SQL
    db.query(DocumentChunk).filter(DocumentChunk.doc_id == doc.id).delete()
    db.delete(doc)
    db.commit()

    return {"message": f"Document ID {doc_id} ('{doc.filename}') deleted successfully."}
