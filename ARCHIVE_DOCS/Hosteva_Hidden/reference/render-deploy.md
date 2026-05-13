# Skill: Render Deployment Pre-Flight Audit

## Context
Before any code is pushed to the `main` branch for Render deployment, the Release Manager (Heimdall) MUST execute this pre-flight checklist to prevent 502/503 boot crashes.

## Mandatory Checklist
1. **Port Binding:** Inspect the `Dockerfile`. The `CMD` instruction MUST be in shell form and utilize the dynamic `$PORT` environment variable:
   `CMD gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000}`
2. **Database Driver:** Inspect `requirements.txt`. It MUST utilize `psycopg[binary]` (v3). It MUST NOT contain the legacy `psycopg2-binary` package to prevent dynamic linking crashes on `slim` containers.
3. **Connection String Prefix:** Inspect `app/database.py`. It MUST contain the intercept logic to rewrite Render's injected `postgresql://` string to the modern driver requirement: `postgresql+psycopg://`.
4. **Global Database Initialization:** Inspect `app/main.py`. There MUST NOT be any synchronous database calls (e.g., `CREATE EXTENSION`, `Base.metadata.create_all()`) executing in the global namespace. These operations block Gunicorn workers and cause timeouts.
5. **Dependency Linting:** Execute `scripts/run_linter.sh` to ensure all imported dependencies (e.g., Pydantic email validators) are actively resolved.

Failure to verify all 5 checkpoints constitutes an Orchestrator Protocol Violation.
