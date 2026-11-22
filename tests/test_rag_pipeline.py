import pytest
from backend.app.services.chunking_service import ChunkingService
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vector_store import VectorStoreService
from backend.app.services.hybrid_retriever import HybridRetrieverService
from backend.app.services.advanced_rag import AdvancedRAGPipeline

def test_recursive_character_chunking():
    chunker = ChunkingService(chunk_size=100, chunk_overlap=20)
    text = "Enterprise retail operations generate massive data across thousands of stores and warehouses. Inventory planning and replenishment SOPs guide daily operations."
    chunks = chunker.recursive_character_chunk(text, max_size=100, overlap=20)
    assert len(chunks) >= 2
    for c in chunks:
        assert len(c) <= 150 # within tolerance

def test_metadata_based_chunking():
    chunker = ChunkingService(chunk_size=200, chunk_overlap=20)
    text = "## Section 1: Receiving Dock Check-in\nCheck driver BOL and PO number.\n\n## Section 2: Seal Inspection\nInspect high-security bolt seal."
    meta = {"doc_type": "Warehouse Manuals", "department": "Logistics"}
    chunks = chunker.metadata_based_chunk(text, meta)
    assert len(chunks) >= 2
    assert chunks[0].section_title.startswith("Section 1")
    assert chunks[0].metadata["department"] == "Logistics"

def test_query_expansion():
    rag = AdvancedRAGPipeline(None, None, None)
    exp = rag.expand_query("Product out of stock")
    assert len(exp) >= 2
    assert any("inventory shortage" in s.lower() or "stock availability" in s.lower() for s in exp)

def test_conversational_memory_followup():
    rag = AdvancedRAGPipeline(None, None, None)
    session = "sess_memory_test"
    rag.add_to_memory(session, "user", "What is the replenishment status for Product P100?")
    rag.add_to_memory(session, "assistant", "Product P100 has 4 units on hand in Store 105.")
    
    # Follow-up query with pronoun
    reformulated = rag.reformulate_with_memory(session, "Why is it delayed?")
    assert "P100" in reformulated
