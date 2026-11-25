from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str = 'postgresql+psycopg://retail:retail_local_only@localhost:5432/retail'
    jwt_secret: str = 'CHANGE_ME_BEFORE_DEPLOYMENT'
    openai_api_key: str = ''
    openai_model: str = 'gpt-4o-mini'
    demo_mode: bool = True
    data_dir: str = str(BASE / 'data')
    uploads_dir: str = str(BASE / 'outputs' / 'uploads')
    reports_dir: str = str(BASE / 'outputs' / 'reports')
    chroma_dir: str = str(BASE / 'outputs' / 'chroma')
    embedding_model: str = 'sentence-transformers/all-MiniLM-L6-v2'
    comparison_embedding_model: str = 'intfloat/e5-small-v2'
    reranker_model: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
    enable_cross_encoder: bool = False
    chunk_size: int = 700
    chunk_overlap: int = 100
    max_upload_mb: int = 20
    cors_origins: str = 'http://localhost:5173,http://127.0.0.1:5173'

settings = Settings()
for folder in (settings.uploads_dir,settings.reports_dir,settings.chroma_dir):
    Path(folder).mkdir(parents=True,exist_ok=True)
