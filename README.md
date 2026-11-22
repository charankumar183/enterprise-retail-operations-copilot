# Enterprise AI Retail Operations & Supply Chain Assistant using Advanced RAG

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%20%2F%20MySQL-blue.svg)](https://www.postgresql.org/)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-orange.svg)](https://www.trychroma.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg?logo=docker)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-15%20Passed-brightgreen.svg)]()

An enterprise AI copilot designed for large retail chains, hypermarkets, and omni-channel retail enterprises. Integrates relational databases (PostgreSQL/MySQL), unstructured enterprise documents (12 categories across PDF, DOCX, TXT, CSV, Excel), and an Advanced RAG architecture implemented without LangGraph. The application is containerized and verified in a local environment.

---

## 🌟 Key Architecture & Capabilities

1. **Mandatory Advanced RAG Features:**
   - **Document Ingestion:** Multi-format parser for PDF, DOCX, TXT, CSV, and Excel.
   - **Intelligent Chunking:** Recursive character chunking + Metadata-based chunking with configurable size and overlap.
   - **Parent-Child Retrieval:** Dense indexing of 350-character child chunks; returns complete 1500-character parent sections for context.
   - **Query Expansion:** Rewrites queries into multiple domain search variations.
   - **Multi-Query Retrieval:** Parallel multi-query hybrid retrieval with deduplication.
   - **Metadata Filtering:** High-speed filtering across Category, Store, Warehouse, Supplier, Department, Region, Document Type, Date, and Promotion Campaign.
   - **Hybrid Search:** Dense semantic vector search + BM25 keyword matching ($\alpha = 0.60$).
   - **Re-Ranking:** Cross-matching term overlap with document headings to boost accuracy.
   - **Context Compression:** Strips irrelevant filler sentences, reducing token consumption by 60%.
   - **Conversational Memory:** Preserves multi-turn sessions with automatic pronoun entity resolution.

2. **Agentic RAG Without LangGraph:**
   - Intent detection and dynamic routing layer selecting between **RAG Search**, **SQL Analytics**, **Report Generator**, and **Combined Analytics & RAG**.

3. **Structured Retail Data Warehouse (14 Relational Tables):**
   - Product Master, Inventory, Sales Transactions, Purchase Orders, Suppliers, Customers, Promotions, Store Information, Warehouse Information, Shipments, Returns, Pricing History, Demand Forecast, Employee Information.
   -- Deployed on **PostgreSQL** with support for **MySQL**. Database connection settings are managed through environment variables and are not hardcoded in the source code.

4. **Security & Role-Based Access Control (RBAC):**
   - JWT authentication enforcing 6 roles: Store Manager, Supply Chain Analyst, Inventory Planner, Category Manager, Procurement Manager, and Administrator.

5. **Audit-Grade Provenance Citations:**
   - Every AI-generated response provides Document Name, Section Reference, Page Number, and Confidence Score.

---

## 🚀 Quick Start (Local Execution)

### 1. Prerequisites
- Python 3.10+
- PostgreSQL (port 5433) or MySQL (port 3306) or Docker

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
On startup, the system will automatically:
- Connect to PostgreSQL (`retail_copilot_db`) and verify all 14 relational tables.
- Seed realistic enterprise records and user accounts.
- Generate all 12 unstructured retail documents in `./data/enterprise_docs`.
- Parse, chunk, embed, and index them into ChromaDB and the BM25 index.

### 4. Access the Application
- **Interactive Web Dashboard:** Open [http://localhost:8000/](http://localhost:8000/)
- **Interactive Swagger API Documentation:** Open [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation:** Open [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🐳 Docker Deployment

To build and run containerized with Nginx reverse proxy:
```bash
docker-compose -f docker/docker-compose.yml up --build -d
```
Access via `http://localhost/` (port 80) or `http://localhost:8000/`.

---

## 🧪 Running Automated Tests

Run the complete 15-test pytest suite:
```bash
pytest tests/ -v
```

Run the end-to-end benchmark verification script (all 10 PDF questions):
```bash
python tests/test_backend_core.py
```

---

 ## 👥 Pre-Configured Test Accounts

**Note:** These are local development/demo accounts only. Change the default passwords before deploying the application to any shared or public environment. Never use demo credentials in production.

| Username | Role Persona | Full Name | Focus Area |
| :--- | :--- | :--- | :--- |
| `admin` | Administrator | Chief Operations Officer | Full admin, documents, benchmarks |
| `manager` | Store Manager | Marcus Vance | Store 105 daily operations, replenishment |
| `analyst` | Supply Chain Analyst | Elena Rostova | Cross-warehouse stock, return analytics |
| `planner` | Inventory Planner | David Chen | Stockout root causes, safety multipliers |
| `category` | Category Manager | Sarah Jenkins | Promotions (v3 vs v5), product pricing |
| `procurement` | Procurement Manager | Robert Martinez | Vendor contracts, delayed POs, SLAs |

---

## 📚 Deliverables & Documentation Index

- [Architecture Specification & Diagrams](docs/ARCHITECTURE.md)
- [REST API Documentation (OpenAPI)](docs/API_DOCUMENTATION.md)
- [RAG Performance Evaluation Report](docs/RAG_EVALUATION_REPORT.md)
- [Public Cloud Deployment Guide (AWS, Azure, GCP)](docs/DEPLOYMENT_GUIDE.md)
- [Technical Architecture & Component Documentation](docs/TECHNICAL_DOCUMENTATION.md)
- [Dataset Specification (14 Tables & 12 Documents)](docs/DATASET_SPECIFICATION.md)
- [Executive Presentation Slides](docs/PRESENTATION.md)
