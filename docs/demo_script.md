# Suggested 10–15 minute demonstration recording script

**This document is a recording plan; it is not a recorded video.** Use Windows screen recorder (Snipping Tool, OBS or Teams) to capture the live deployed app.

- **0:00–1:30**: Introduce retail business problems, multiple sources, objective and synthetic dataset.
- **1:30–3:00**: Architecture diagram: React → FastAPI RBAC → intent router → RAG / SQL / reports; PostgreSQL and ChromaDB.
- **3:00–4:30**: Login with role, Dashboard live SQL statistics and low-stock alerts.
- **4:30–6:00**: Query inventory for P100, supplier and delayed purchase orders.
- **6:00–8:30**: Ask warehouse receiving policy question. Expand source citations with name, section, PDF page and retrieval score.
- **8:30–9:30**: Query stockout cause for P100. Explain SQL+evidence path and clarify model-mode label.
- **9:30–10:30**: Upload and index a sample document. Demonstrate update via reindex, then delete only a disposable uploaded file.
- **10:30–11:30**: Generate daily operations report and download PDF.
- **11:30–12:30**: Run evaluation and explain actual Precision@5/Recall@5, embedding comparison script.
- **12:30–13:30**: Admin audit trail, permissions, Swagger.
- **13:30–15:00**: Deployment URL (if actually deployed), caveats and business-impact measurement plan.

Record the entire live session and deliver an MP4 file as the separate capstone artifact. Avoid calling data or metrics real enterprise records.
