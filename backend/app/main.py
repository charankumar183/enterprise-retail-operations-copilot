import os
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.app.config import settings
from backend.app.database import SessionLocal, engine
from backend.app.api.v1 import api_router
from backend.app.services.seeding_service import SeedingService
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vector_store import VectorStoreService
from backend.app.services.hybrid_retriever import HybridRetrieverService

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Enterprise AI Retail Operations & Supply Chain Assistant using Advanced RAG without LangGraph.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Latency and Audit Logging Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000.0
    response.headers["X-Process-Time-Ms"] = str(round(process_time, 2))
    return response

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(api_router, prefix="/api")

# Initialize and Seed on Startup
@app.on_event("startup")
def on_startup():
    print("=" * 60)
    print(f"Starting {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}")
    print("=" * 60)
    
    # 1. Initialize Relational Schema
    SeedingService.init_database()
    
    db = SessionLocal()
    try:
        # 2. Seed Users and 14 Relational Tables
        SeedingService.seed_users(db)
        SeedingService.seed_structured_data(db)
        
        # 3. Create 12 Enterprise Unstructured Documents
        SeedingService.generate_unstructured_documents()
        
        # 4. Parse, Chunk, Embed & Index Documents
        emb_svc = EmbeddingService()
        v_store = VectorStoreService()
        hybrid_ret = HybridRetrieverService(v_store, emb_svc)
        SeedingService.index_all_documents(db, emb_svc, v_store, hybrid_ret)
        
        print("Application startup and database initialization complete!")
    finally:
        db.close()

# Health check
@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "database": "connected"
    }

# Serve Frontend static directory if present
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
frontend_dir = os.path.join(project_root, "frontend")
if not os.path.exists(frontend_dir):
    frontend_dir = os.path.join(os.getcwd(), "frontend")
if not os.path.exists(frontend_dir):
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend_index():
        index_file = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Retail Copilot API is running. Visit /docs for Swagger."}
