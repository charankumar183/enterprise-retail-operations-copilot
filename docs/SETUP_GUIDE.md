# Windows 11 Setup Guide — PowerShell 5.1

This guide was tailored for the reported machine: **Python 3.10.11**, **Node 22.17.0**, **npm 10.9.2**, **Git 2.50.1**, **Docker 29.8.0**, **Compose v5.5.1**. The detected versions are suitable for the chosen development workflow; this does **not** confirm that Docker Desktop's engine is actually running or that dependencies have been downloaded.

## Recommended: Docker Desktop / one PowerShell command

1. Run Docker Desktop. In Settings, enable Linux containers and WSL 2 backend when prompted.
2. Extract the ZIP to a short path such as `C:\Projects\retail-operations-copilot`.
3. Open PowerShell (not the Python interpreter), `cd C:\Projects\retail-operations-copilot`.
4. Run `docker info` and ensure it returns server information.
5. `powershell -ExecutionPolicy Bypass -File .\start-windows.ps1`.
6. Watch logs: `docker compose logs -f backend`.
7. Open http://localhost:5173. Swagger at http://localhost:8000/docs.
8. Log in using the administrator demo credentials shown in README. Never use these public credentials for a real deployment.
9. Wait for background indexing to complete. It first downloads a model and then indexes 18 bundled documents. The UI shows indexing status and errors.
10. For true generative AI, edit `.env` and add `OPENAI_API_KEY=...`; rerun `docker compose up -d --force-recreate backend`. No key is necessary for SQL analytics or extractive retrieval.

**When to create a virtual environment?** Not needed with Docker. Docker isolates Python packages. Only create one if running `uvicorn` directly on Windows.

## If ports are unavailable

`netstat -ano | findstr :5173` or `netstat -ano | findstr :8000`. Shut down conflicting applications or change exposed ports in `docker-compose.yml` and frontend `VITE_API_URL` as appropriate.

## If backend reports database connection errors

`docker compose ps` and `docker compose logs db`. The backend waits for PostgreSQL readiness. Do not change the hostname `db` in `DATABASE_URL` inside Docker.

## If AI fails after indexing

Check `docker compose logs backend`. Initial model download needs internet and adequate RAM. API is intentionally error-transparent. No model or key → use SQL dashboards until setup is completed. Optional cross-encoder is off by default to reduce load.

## If Docker engine is unavailable

Verify Docker Desktop is open, `wsl --status` returns valid output and Windows virtualization is enabled. Start with `docker info`, not just `docker --version` (the latter only tests CLI installation).

## Tests

`docker compose exec backend pytest -q` and `cd frontend; npm install; npm run build`. Retrieval metrics from `/api/evaluation/run` are live and computed only after indexing. No fabricated performance numbers or 80–90% business-impact improvements are reported.
