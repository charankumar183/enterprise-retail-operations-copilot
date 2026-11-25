# Architecture — Retail Operations Copilot

## Agentic architecture (no LangGraph)

```mermaid
flowchart TD
    U[Store Manager / Retail User] --> F[React Operations Portal]
    F --> A[FastAPI JWT & RBAC]
    A --> R{Intent Detection / Route}
    R -->|Policies & manuals| Q[Advanced RAG Pipeline]
    R -->|Inventory / sales / POs| S[SQL Analytics]
    R -->|Operational reports| G[Report Generator]
    Q --> X[Query expansion + multiple queries]
    X --> H[Hybrid Search: BM25 + Chroma Vector]
    H --> Y[Rank Fusion + Optional Cross Encoder]
    Y --> P[Parent Context + Compression]
    P --> L[Grounded LLM / Extractive Answer]
    S --> DB[(PostgreSQL Retail Data)]
    G --> S
    G --> Q
    G --> PDF[ReportLab PDF]
    L --> C[Document Citations & Score]
    A --> LOG[(Audit Logs / Chat History)]
    A --> DOC[Document Upload & Versioning]
    DOC --> ING[PDF DOCX TXT CSV Excel Parsing]
    ING --> SPLIT[Metadata / Recursive Chunks]
    SPLIT --> E[Sentence Transformer Embeddings]
    E --> V[(ChromaDB Persistent Index)]
    V --> H
    C --> F
    S --> F
    PDF --> F
```

## Data stores

- PostgreSQL: products, stores, warehouses, inventory, sales, purchase orders, suppliers, customers, promotions, shipments, returns, pricing history, demand forecast, employees, complaints, users, chat, feedback, audit, report metadata.
- ChromaDB: child-chunk vectors plus document name, page, section, and original parent context.
- Persistent file storage: uploads, synthetic sample documents, PDF reports, embedding caches, generated retrieval evaluations.

## Security model

JWT tokens provide user identity and backend-enforced roles. All retail data APIs require authorization. Admin-only operations cover user creation, source deletion and evaluations. The LLM is never allowed to execute arbitrary generated SQL; deterministic SQLAlchemy queries are used for each recognized analytic intent. Documents are untrusted; their text is evidence and not executable instructions.

## Limitations

The system uses bounded RRF ranking and optional cross-encoder reranking. Confidence shown is a relative retrieval score, not model-based certainty. Automatic metadata is derived from upload choices and source formatting; no unsupported page numbers are invented. Public hosting needs proper TLS, secrets, backups, rate limiting, access policies and a cloud account.
