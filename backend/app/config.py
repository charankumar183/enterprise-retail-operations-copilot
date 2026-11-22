import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise AI Retail Operations & Supply Chain Assistant"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "retail-enterprise-copilot-secret-key-2026-secure-token"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database (PostgreSQL default per PDF, with MySQL support)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/retail_copilot_db")
    
    # Vector Database
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    VECTOR_DB_COLLECTION: str = "retail_enterprise_knowledge"
    
    # Embeddings & RAG Configuration
    DEFAULT_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    COMPARISON_EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    PARENT_CHUNK_SIZE: int = 1500
    CHILD_CHUNK_SIZE: int = 350
    TOP_K_RETRIEVAL: int = 5
    HYBRID_ALPHA: float = 0.6  # 0.6 vector, 0.4 BM25
    RERANK_TOP_K: int = 3
    
    # LLM Settings
    LLM_PROVIDER: str = "auto"  # "gemini", "openai", or "fallback"
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # Paths
    DOCS_DIRECTORY: str = "./data/enterprise_docs"
    SYNTHETIC_DATA_DIRECTORY: str = "./data/synthetic_sql"
    REPORTS_DIRECTORY: str = "./data/reports"

    model_config = ConfigDict(env_file=".env", extra="allow")

settings = Settings()

# Ensure directories exist
os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
os.makedirs(settings.DOCS_DIRECTORY, exist_ok=True)
os.makedirs(settings.SYNTHETIC_DATA_DIRECTORY, exist_ok=True)
os.makedirs(settings.REPORTS_DIRECTORY, exist_ok=True)
