# Enterprise Retail Copilot: OpenAPI / REST API Documentation

Base URL: `http://localhost:8000/api/v1`
Interactive Swagger Documentation: `http://localhost:8000/docs`
ReDoc Documentation: `http://localhost:8000/redoc`

---

## 1. Authentication & RBAC

### POST `/auth/login`
Authenticates an enterprise user using OAuth2 password flow and returns a signed JWT token.
- **Request (Form Data):** `username`, `password`
- **Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "role": "Store Manager",
  "username": "manager"
}
```

### POST `/auth/json-login`
JSON payload equivalent for frontend convenience.
- **Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

### GET `/auth/me`
Retrieves authenticated user profile.
- **Header:** `Authorization: Bearer <token>`
- **Response:**
```json
{
  "username": "manager",
  "email": "manager105@enterprise-retail.com",
  "full_name": "Marcus Vance",
  "role": "Store Manager",
  "id": 2,
  "is_active": true
}
```

---

## 2. AI Copilot & Agentic RAG

### POST `/chat`
Primary conversational agentic endpoint with intent detection, routing, and source citations.
- **Request Body:**
```json
{
  "query": "What are the standard receiving procedures for warehouse operations?",
  "conversation_id": "session_abc123",
  "filter_category": "Household Cleaning",
  "filter_store": "STORE-105",
  "filter_warehouse": "WH-001",
  "filter_doc_type": "Warehouse Manuals"
}
```
- **Response (200 OK):**
```json
{
  "query": "What are the standard receiving procedures for warehouse operations?",
  "detected_intent": "RAG Search",
  "route_taken": "RAG Search",
  "response": "### Standard Receiving Procedures for Warehouse Operations...",
  "citations": [
    {
      "document_name": "Warehouse_Receiving_Standard_Operating_Procedure.txt",
      "section_reference": "Section 1: Pre-Dock Arrival & Verification",
      "page_number": 1,
      "confidence_score": 0.94,
      "snippet": "Carrier driver must surrender physical Bill of Lading..."
    }
  ],
  "sql_query": null,
  "sql_results": null,
  "expanded_queries": [
    "warehouse receiving SOP",
    "standard receiving procedures",
    "inbound freight inspection"
  ],
  "retrieval_time_ms": 32.5,
  "response_latency_ms": 48.2,
  "conversation_id": "session_abc123",
  "query_id": 14
}
```

### GET `/chat/history/{session_id}`
Returns conversation memory turns for the given multi-turn session.

---

## 3. Product Catalog

### GET `/products`
Search and filter product master records.
- **Query Parameters:** `search`, `category`, `department`
- **Response:**
```json
[
  {
    "id": 1,
    "product_id": "P100",
    "name": "UltraClean Dishwasher Pods 60-Pack",
    "category": "Household Cleaning",
    "department": "Home Care",
    "brand": "Apex Clean",
    "unit_price": 18.99,
    "cost_price": 9.50,
    "supplier_id": "SUP-XYZ",
    "min_reorder_level": 120,
    "lead_time_days": 10
  }
]
```

### GET `/products/{product_id}`
Returns details for a single product.

---

## 4. Inventory Operations

### GET `/inventory/overview`
Retrieves executive inventory health overview, SKU counts, low-stock counts, and location distribution.

### GET `/inventory/lookup/{product_id}`
Queries inventory availability across all regional warehouses and retail stores for the given product.

---

## 5. Document Management & Ingestion

### GET `/documents`
Lists all ingested documents, versions, formats, and total vector chunks.

### POST `/documents/upload`
Uploads and indexes enterprise documents (PDF, DOCX, TXT, CSV, Excel).
- **Form Data:** `file` (multipart), `doc_type`, `department`, `version`, `category`

### PUT `/documents/{doc_id}`
Updates metadata or bumps document version.

### DELETE `/documents/{doc_id}`
Deletes document and purges all chunks from ChromaDB and relational tables.

---

## 6. Business Reports

### POST `/reports/generate`
Generates operations reports (Daily Store Ops, Replenishment Checklist, Delayed POs).
- **Request Body:**
```json
{
  "report_type": "daily_store_ops",
  "target_id": "STORE-105"
}
```

### GET `/reports/download/{report_id}`
Downloads the generated operational report JSON document.

---

## 7. Auditing & Model Benchmarking

### POST `/feedback`
Submits user rating (1-5) and feedback on copilot responses.

### GET `/feedback/audit-logs`
Returns execution traces, SQL queries, intent routes, and response latencies.

### GET `/evaluation/benchmark`
Executes automated comparative benchmarking between `sentence-transformers/all-MiniLM-L6-v2` and `BAAI/bge-small-en-v1.5`.
