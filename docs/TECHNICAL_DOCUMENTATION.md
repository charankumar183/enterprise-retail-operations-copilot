# Technical Documentation: Enterprise AI Retail Operations Copilot

## 1. System Components & Module Organization

```
ML PROJECT_3/
├── backend/
│   ├── app/
│   │   ├── main.py                    # Application entrypoint & startup orchestrator
│   │   ├── config.py                  # Pydantic Settings & environment variables
│   │   ├── database.py                # SQLAlchemy engine & session factory
│   │   ├── models/                    # Relational data schema (14 tables + auth + docs + audit)
│   │   ├── schemas/                   # Pydantic request/response validation schemas
│   │   ├── services/
│   │   │   ├── auth_service.py        # Password hashing, JWT creation & RBAC enforcement
│   │   │   ├── seeding_service.py     # Automatic database schema creation & synthetic data seeder
│   │   │   ├── document_parser.py     # Multi-format parser (PDF, DOCX, TXT, CSV, Excel)
│   │   │   ├── chunking_service.py    # Recursive chunking & parent-child hierarchical splits
│   │   │   ├── embedding_service.py   # Embedding models (Sentence Transformers & BGE) & benchmarks
│   │   │   ├── vector_store.py        # ChromaDB persistent client with local index fallback
│   │   │   ├── hybrid_retriever.py    # Dense vector + BM25 keyword reciprocal fusion
│   │   │   ├── advanced_rag.py        # 10 mandatory Advanced RAG pipeline features
│   │   │   ├── agentic_router.py      # Non-LangGraph intent classifier & dynamic router
│   │   │   ├── sql_analytics.py       # Parameterized SQL analytics & stockout root-cause analyzer
│   │   │   ├── report_generator.py    # Daily store ops & replenishment checklist generator
│   │   │   └── evaluation_service.py  # Precision, Recall, Accuracy, Latency, Hallucination benchmarking
│   │   └── api/
│   │       └── v1/                    # REST API routers (auth, chat, products, inventory, docs, reports, feedback, eval)
├── frontend/                          # Enterprise single-page application (HTML, CSS, JS, Chart.js)
├── docker/                            # Dockerfile, docker-compose.yml, nginx.conf
├── docs/                              # Comprehensive technical documentation & deliverables
├── tests/                             # Automated pytest test suites (13 unit & integration tests)
├── requirements.txt                   # Production dependency manifest
└── README.md                          # Quickstart guide & repository index
```

---

## 2. Advanced RAG Implementation Details

### Hierarchical Parent-Child Retrieval
In retail operations, retrieving a tiny paragraph without the surrounding context leads to loss of critical policy criteria (such as approval thresholds or penalty schedules).
- **Chunking Pipeline:**
  1. The document is split into **Parent Chunks** ($1500$ characters) representing cohesive business sections.
  2. Each Parent Chunk is subdivided into **Child Chunks** ($350$ characters, $100$ character overlap).
  3. Child chunks are embedded into ChromaDB with dense embeddings and indexed into the BM25 inverted index.
  4. At search time, the hybrid retriever identifies the most relevant child chunks, and the pipeline fetches the complete parent chunk from the relational database.

### Hybrid Retrieval & Reciprocal Fusion
Vector similarity struggles with precise SKU numbers or exact store IDs, while keyword matching fails on paraphrased policy questions. Fusing both yields optimal results:
$$\text{Score} = 0.60 \cdot \text{VectorScore} + 0.40 \cdot \text{BM25Score}$$

### Agentic Routing Without LangGraph
Routing decisions are evaluated via an intent classifier that inspects semantic indicators, query verbs, and referenced entities:
- **`Report Generator`:** Queries requesting daily summaries or replenishment checklists.
- **`SQL Analytics`:** Queries requesting live warehouse stock, supplier lookup, return rates, or delayed purchase orders.
- **`Combined Analytics & RAG`:** Queries investigating root causes of stockouts, combining SQL queries with policy citations.
- **`RAG Search`:** Policy interpretation, SOP guidance, and contract clause lookup.

---

## 3. Security & Role-Based Access Control

- **Token Standard:** JWT Bearer (HMAC SHA-256)
- **Token Expiry:** Configurable (default 24 hours)
- **Pre-seeded Accounts:**
  - `admin` (Role: Administrator, Password: `admin123`)
  - `manager` (Role: Store Manager, Password: `admin123`)
  - `analyst` (Role: Supply Chain Analyst, Password: `admin123`)
  - `planner` (Role: Inventory Planner, Password: `admin123`)
  - `category` (Role: Category Manager, Password: `admin123`)
  - `procurement` (Role: Procurement Manager, Password: `admin123`)
