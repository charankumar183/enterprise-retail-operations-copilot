# 10–15 Minute Demonstration Video Script: Enterprise AI Retail Operations Copilot

**Target Audience:** Project Evaluators, Enterprise Leadership, Retail Operations Executives  
**Video Length:** 12–14 Minutes  
**Demonstrator:** Senior AI Architect / Full-Stack Engineer

---

## Part 1: Introduction & Architecture Overview (00:00 - 02:30)
- **Visual:** Open browser to `http://localhost:8000/`. Show the clean, professional dashboard and top bar.
- **Narrator Script:**
  > *"Welcome to the demonstration of our Enterprise AI Retail Operations & Supply Chain Assistant using Advanced RAG. Large retail enterprises manage millions of items across thousands of stores and warehouses, generating vast amounts of unstructured policies, vendor contracts, and SOPs, while running transactional sales and inventory in relational databases.*
  > *Our copilot unifies both knowledge worlds into an auditable, high-precision AI assistant. It implements all 10 mandatory Advanced RAG features — including parent-child chunking, multi-query retrieval, hybrid vector-BM25 search, re-ranking, and conversational memory — orchestrated through an agentic intent router without LangGraph."*

---

## Part 2: Role-Based Access Control & User Personas (02:30 - 04:00)
- **Visual:** Click on the top-right role selector dropdown. Demonstrate switching between **Store Manager**, **Supply Chain Analyst**, and **Procurement Manager**.
- **Narrator Script:**
  > *"The platform enforces enterprise Role-Based Access Control using JWT Bearer tokens across six distinct enterprise personas: Store Manager, Supply Chain Analyst, Inventory Planner, Category Manager, Procurement Manager, and Administrator.*
  > *Notice how switching roles dynamically updates the user's operational scope, permissions, and contextual audit footprint."*

---

## Part 3: Live Advanced RAG Demonstration with Provenance Citations (04:00 - 07:00)
- **Visual:** In the AI Chat tab, click the suggested chip: *"What are the standard receiving procedures for warehouse operations?"*
- **Narrator Script:**
  > *"Let's test an unstructured policy search. The agentic router detects a 'RAG Search' intent. The query is expanded with domain synonyms, retrieved through hybrid ChromaDB and BM25 search, resolved from child chunk to full parent section, reranked, and compressed.*
  > *In under 60 milliseconds, the copilot returns the complete receiving protocol: BOL verification, physical bolt seal inspection, UCC-128 barcode scanning, and 2-hour GRN system posting.*
  > *Crucially, notice the audit-grade source citation pill: it cites 'Warehouse_Receiving_Standard_Operating_Procedure.txt', Section 1, Page 1, with a 94% confidence score. No hallucination, fully traceable."*

- **Visual:** Ask: *"Compare Promotion Policy Version 3 with Version 5."*
- **Narrator Script:**
  > *"Here, the copilot performs multi-document comparative synthesis across historical promotion policy versions. It creates a structured comparison table showing the reduction of discretionary store markdowns from 25% down to 15%, the strict ban on stackable coupons in Version 5, and the shift in vendor co-op advertising cost-sharing from 50/50 to 70/30."*

---

## Part 4: SQL Analytics & Hybrid Root-Cause Stockout Analysis (07:00 - 09:30)
- **Visual:** Click chip: *"Show inventory availability for Product X across all warehouses."*
- **Narrator Script:**
  > *"Now watch our Agentic Router dynamically pivot from document search to real-time SQL Analytics. The query is routed to the SQL Analytics Engine, executing a join across our Product Master, Inventories, and Warehouse tables.*
  > *We see live availability for Product X: 1,250 units in WH-CENTRAL, 680 in WH-002, 420 in WH-001, and 310 in WH-WEST.*
  > *Next, let's ask our key hybrid question: 'Why is Product P100 frequently going out of stock?'*
  > *The system activates our Combined Analytics & RAG route: it queries the SQL database to find that Store 105 has only 4 units remaining and that Supplier Apex (SUP-XYZ) has 3 delayed purchase orders. Simultaneously, it retrieves Section 3.2 of the Inventory Replenishment Policy, directing the planner to execute an emergency cross-dock from WH-CENTRAL and raise safety stock to 2.5x."*

---

## Part 5: Operational Dashboards & Automated Report Generation (09:30 - 11:30)
- **Visual:** Navigate to the **Inventory Dashboard** tab. Show the live Chart.js warehouse distribution bar chart and stockout donut chart.
- **Visual:** Navigate to the **Operations Reports** tab. Select *"Daily Store Operations Report"* for `STORE-105` and click *"Generate Report"*.
- **Narrator Script:**
  > *"In the Operations Reports tab, store managers can generate audit-ready daily reports in one click. Here is Store 105: gross sales of $28,450 against its target, transaction count, low-stock SKU count, and management directives.*
  > *We can download the complete report as a structured JSON file immediately using the download button."*

---

## Part 6: Document Ingestion, Benchmarks & Conclusion (11:30 - 13:30)
- **Visual:** Go to the **Document Ingestion** tab. Show the 12 ingested documents across PDF, DOCX, TXT, CSV, and Excel.
- **Visual:** Go to the **Admin & Benchmarks** tab. Show the live audit logs and click *"Run Benchmark Evaluation"*.
- **Narrator Script:**
  > *"In the Admin tab, we see the empirical benchmark comparing sentence-transformers/all-MiniLM-L6-v2 and BAAI/bge-small-en-v1.5. Both achieved 100% recall on ground-truth queries, with BGE delivering sub-millisecond retrieval latency.*
  > *Our platform is fully tested with 13 automated pytest tests, Dockerized with Nginx, and ready for production cloud deployment.*
  > *Thank you for watching the demonstration."*
