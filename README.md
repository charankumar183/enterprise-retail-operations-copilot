# Enterprise AI Retail Operations & Supply Chain Copilot (Advanced RAG)

**Academic capstone implementation matching the 9-page training PDF.** A real React frontend, FastAPI service, PostgreSQL enterprise dataset, ChromaDB-based advanced RAG, intent-driven SQL analytics, role-based authentication, synthetic documentation, PDF reporting, evaluation scripts and Docker.

> All documents and transaction records are **SYNTHETIC DEMONSTRATION DATA**. This is an educational reference implementation, **not** an independently audited production application. Real public deployment, a GitHub remote, the demonstration video, and measured business-impact claims require user-supplied accounts/evidence and cannot be included as completed actions in a ZIP.

## Fastest start — Windows 11 with Docker Desktop

1. Open **Docker Desktop** and confirm its engine is running (`docker info`).
2. Extract ZIP, open the `retail-operations-copilot` directory in VS Code.
3. In PowerShell, from the project root, run: `powershell -ExecutionPolicy Bypass -File .\start-windows.ps1`
4. Wait until `docker compose ps` shows services running. The first build downloads Python/npm dependencies and indexing downloads an embedding model; it can take time on the first run.
5. Open **http://localhost:5173** and **http://localhost:8000/docs**.
6. Sign in as `admin@demo.retail` / `RetailDemo2026!`. Six demo roles are seeded. **Change passwords and JWT/database secrets before public exposure.**
7. In **Knowledge library**, monitor the automatic indexing status. If indexing failed due to model connectivity, review `docker compose logs backend` and click **Index bundled sample documents** to retry.

### Quick diagnostics

```powershell
docker info
docker compose ps
docker compose logs --tail=100 backend
docker compose logs --tail=100 frontend
docker compose down
```

Stop: `powershell -ExecutionPolicy Bypass -File .\stop-windows.ps1`.

If PowerShell reports Docker daemon inaccessible, start Docker Desktop and verify WSL 2 / Linux containers are enabled.

## API and LLM mode

- **Backend**: http://localhost:8000
- **Interactive Swagger**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173
- If `OPENAI_API_KEY` is unset, SQL queries run normally and document questions return **extractive evidence only**, not fabricated generative answers. For LLM-generated answers, edit `.env`, set `OPENAI_API_KEY`, then run `docker compose up -d --force-recreate backend`.
- Model `sentence-transformers/all-MiniLM-L6-v2` is downloaded and embedded **locally**. The RAG engine does not use OpenAI embeddings by default; select another embedding in `.env` and reindex documents.
- Configure `ENABLE_CROSS_ENCODER=true` to run the cross-encoder model for document reranking (more resources/download time); otherwise reciprocal rank fusion and relevance sorting are active.

## Demo roles

| Role | Email | Password |
| --- | --- | --- |
| Administrator | `admin@demo.retail` | `RetailDemo2026!` |
| Store Manager | `store_manager@demo.retail` | `RetailDemo2026!` |
| Supply Chain Analyst | `supply_chain_analyst@demo.retail` | `RetailDemo2026!` |
| Inventory Planner | `inventory_planner@demo.retail` | `RetailDemo2026!` |
| Category Manager | `category_manager@demo.retail` | `RetailDemo2026!` |
| Procurement Manager | `procurement_manager@demo.retail` | `RetailDemo2026!` |

Registration is restricted to administrators (to prevent public role escalation). Admins can change role assignments using Swagger `/api/admin/users/{id}/role`. Document ingestion is reserved for Administrator and Procurement Manager; deletion is Admin-only. All business data endpoints require JWT.

## Advanced RAG feature matrix

| Feature in trainer PDF | Implementation |
| --- | --- |
| PDF/DOCX/TXT/CSV/Excel loading | `backend/app/rag.py:text_pages` |
| Recursive/metadata chunking; overlap | `split_parents`, `make_chunks`, `.env` chunk params |
| Query expansion | `expand_query` (business synonyms + lexical rewrites) |
| Multi-query retrieval | `retrieve`, original/expanded variants |
| Parent–child retrieval | Small vector child; full original parent section saved as metadata |
| Metadata filtering | Department, document type, region, version (backend API) |
| Hybrid search | Chroma semantic search + in-memory BM25 via `rank_bm25` |
| Re-ranking | RRF ranking; optional true cross-encoder rerank |
| Context compression | Query-focused sentence selection |
| Conversation memory | Per-user session history from PostgreSQL |
| Agentic RAG without LangGraph | Intent routing `rag/sql/report` in `analytics.py`, `main.py` |
| SQL analytics | ORM-backed, parameterized/read-only queries on inventory, sales, orders, returns, suppliers, complaints, forecasts |
| Source citations | Indexed name, section, original page (or explicitly unavailable), retrieval ranking score |
| Embedding comparison | `app.embedding_benchmark`, two models on shared corpus/questions |
| Source-backed PDF reports | `app.reporting:make_pdf` |
| Evaluation and logging | `/api/evaluation/run`, `app/evaluation.py`, SQL audit logs |

**Limitations:** The confidence indicator is an uncalibrated retrieval relevance signal rather than a verified probability. Non-PDF page numbers cannot reliably be obtained from file formats without page layouts, so they are labeled *unavailable*. Embedding comparison must be explicitly executed to report actual metrics. Advanced features should be validated on your target machine before describing the system as production ready.

## Explore and demonstrate

1. **Dashboard**: SQL-sourced inventory alerts and sales value.
2. **Catalog / Inventory**: Search `P100`, note low-stock locations.
3. **AI Copilot**: Ask `Why is Product P100 frequently going out of stock?` (SQL + policy evidence if indexed).
4. Ask `What is the standard warehouse receiving procedure?` (Advanced RAG citations).
5. Ask `Which products have the highest return rate?` (SQL analytics).
6. **Knowledge library**: Upload a new document with metadata, reindex, or delete.
7. **Reports**: Generate a PDF on `Store 105`; download and inspect evidence.
8. **Evaluation**: Run 30 labeled questions; observe measured Precision@5 and Recall@5.
9. **Admin**: Show audit logs and role restrictions.

## Development, tests and optional local Python workflow

Docker is the recommended way to get PostgreSQL and the entire system running in one command. For local development (without Docker for backend):

```powershell
# Keep PostgreSQL available from Docker or a local PostgreSQL installation.
docker compose up -d db
cd backend
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Set DATABASE_URL for localhost, then start:
$env:DATABASE_URL='postgresql+psycopg://retail:local_demo_change_this@localhost:5432/retail'
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Separate PowerShell tab: `cd frontend; npm install; npm run dev`.

Backend tests: from `backend`, activate virtual environment, run `pytest -q`. Unit tests use an isolated in-memory SQLite test database, **not** the production application database. Frontend production build: `cd frontend; npm run build`. Model-dependent retrieval integration/evaluation needs embedding download and an indexed document corpus. LLM-dependent tests need OpenAI API key and must not be mislabeled as tests run in mocked/extractive mode.

Embedding comparison:

```powershell
# Inside backend container, with both embedding models downloadable:
docker compose exec backend python -m app.embedding_benchmark
```

Writes `outputs/reports/embedding_comparison.json` and CSV with actual scores.

## Files of interest

- `backend/app`: all API, auth, SQL model, RAG, reporting, evaluation source
- `frontend/src`: functioning React UI (live REST calls)
- `data/sample_documents`: 18 synthetic retail documents of varied formats
- `data/structured`: 15 synthetic CSV snapshots corresponding to the structured SQL entities
- `data/evaluation/test_questions.json`: 30 labeled retrieval questions
- `data/metadata/document_manifest.json`: source metadata
- `docs/`: architectural, evaluation, setup and cloud deployment documentation
- `presentation/`: training presentation deck
- `docs/demo_script.md`: 10–15 minute demonstration recording script (recording itself cannot be generated without a running app/capture)

See `docs/SETUP_GUIDE.md`, `docs/ARCHITECTURE.md`, `docs/TECHNICAL_DOCUMENTATION.md`, `docs/VALIDATION_REPORT.md` and `docs/CLOUD_DEPLOYMENT.md` for more.
