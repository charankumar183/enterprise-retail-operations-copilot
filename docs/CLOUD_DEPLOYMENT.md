# Cloud Deployment Guide — required for final capstone submission

The training PDF requires **Docker + Nginx** and a publicly accessible application on **AWS, Azure or Google Cloud**. This ZIP contains Docker/Nginx definitions, but **a public URL cannot be provisioned without a cloud account, domain/TLS policy, budget approval and credentials.** Do not claim deployment is finished until verified.

## Example cloud target: AWS EC2

1. Provision an EC2 Linux instance with enough RAM/CPU for Sentence Transformers and ChromaDB, attach sufficient encrypted disk and allow inbound only 22 from admin IP and 443 publicly. Do **not** expose PostgreSQL port 5432 publicly.
2. Install Docker Engine and Docker Compose plugin on instance; upload the project through Git or a secure transfer.
3. Create a unique `.env` with strong `JWT_SECRET` and PostgreSQL password, and add an API key to server secrets if generative answers are required. Never commit `.env`.
4. Deploy `docker compose up --build -d`. Confirm `curl http://localhost:8000/health` and test real login, SQL, documents, PDF reports.
5. Replace local-only port exposure with a TLS-terminated reverse proxy at 443 (e.g., HTTPS Nginx plus certificate); proxy `/api` to FastAPI, `/` to the frontend. Set browser API URL to public HTTPS origin. Configure CORS to the actual site origin.
6. Use managed PostgreSQL or protect its volume with backups, configure persistent disk for indexes and uploads, use secret management, rotating logs, request limits, file scanning, monitoring, vulnerability scanning and non-demo user credentials.
7. Re-run smoke tests from an external network and record public URL. Evaluate retrieval quality and error logs.

The same approach can be adapted to **Azure VM / Container Apps** or **Google Compute Engine / Cloud Run** after evaluating persistent volumes, model memory and database constraints. A fully validated production deployment should implement TLS, HSTS, rate limiting and multi-tenant document authorization. Do not reuse demo credentials.

## Cloud acceptance evidence

- Public `https://...` URL reaches login.
- Authorized sign-in works, all protected APIs enforce roles.
- PostgreSQL, vector index, uploaded documents persist after restart.
- AI policy question cites real document/page; inventory question returns SQL-backed data.
- PDF download works; Swagger/OpenAPI is accessible under protected deployment policy.
- Measured evaluation report saved; demonstration video captures the flow.
