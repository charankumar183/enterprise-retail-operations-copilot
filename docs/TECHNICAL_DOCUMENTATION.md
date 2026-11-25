# Technical Documentation

## Objective

Build a production-oriented academic demonstration that can search enterprise retail knowledge, query SQL inventory and sales data, create supply-chain reports, and cite its sources.

## Implementation map

- `models.py`: product master, inventory, sales transactions, POs, suppliers, customers, promotions, store info, warehouse info, shipments, returns, pricing history, demand forecast, employees, complaints, user/auth, reports, audit logging.
- `seed.py`: reproducible seed of 120 products, five stores, four warehouses, suppliers, orders, sales, returns and forecasts. Changes persist in PostgreSQL volume.
- `auth.py`: JWT verification, Argon2 password hashing, role dependencies.
- `rag.py`: multi-format parsing, metadata-aware section parents, RecursiveCharacterTextSplitter with configured overlap, Sentence Transformers embeddings, ChromaDB storage, lexical BM25 plus semantic hybrid, query expansion and multi-query merging via RRF, parent–child context, optional cross-encoder, context compression, cited answer generation, per-user conversation memory in SQL.
- `analytics.py`: deterministic intent routing and SQLAlchemy analytics; never executes arbitrary text-to-SQL generated from prompts.
- `reporting.py`: generated report PDF with evidence list, page and section values as available.
- `evaluation.py`: retrieval precision/recall/latency against 30 labeled questions. Do not report hallucination/answer-accuracy metrics without explicit judging.
- `embedding_benchmark.py`: quantitative comparison of two embeddings with equal corpus and question sets.
- `main.py`: documented REST endpoints; Swagger enabled by FastAPI.
- `frontend/src/main.jsx`: responsive React portal, real API requests, JWT, chat, inventory, product search, document management, reports, evaluation, administration.

## Deployment topology

Docker Compose runs: PostgreSQL on an internal network, FastAPI published on port 8000, frontend built using Node 22 and served from Nginx on port 5173. Named PostgreSQL volume and bound `outputs` directory persist data across restarts. Public cloud requires additional infrastructure work detailed in `CLOUD_DEPLOYMENT.md`.

## Source citation semantics

AI answers provide a reference to file name, section, original PDF page where known, plus the RRF retrieval rank score. This score is not a calibrated confidence probability. Non-page-based file formats correctly display `N/A` for page reference. Answers with insufficient evidence are explicitly limited rather than invented.

## Performance and impact

Do not claim a verified 80–90% search-time reduction until actual baseline timing data is collected. Sample evaluation measures retrieval relevance, not real-world productivity outcomes. Use `data/evaluation/test_questions.json` as reproducible evidence labels; report all test conditions and question counts.
