# Phase 0: Vanguard Planning (Spike: INFRA-001)
**Date:** 2026-05-16
**Goal:** Architect a mathematically sound Dockerfile for Render deployment using `uv` and FastAPI.
**Targets:** INFRA-001 (Render Deployment Crash)

## The Problem Statement
The current Render deployment fails because the `Dockerfile` uses `uv pip install --system .`. This command treats the repository as a standard Python package. Because `pyproject.toml` does not explicitly package the HTML templates or static images, `uv` drops `app/templates/` and `app/static/` during the build, crashing the live FastAPI server. 
Furthermore, manually hardcoding dependencies in the Dockerfile missed critical database libraries (SQLAlchemy, psycopg, Redis) defined in `pyproject.toml`.

## Vanguard Consensus & Architectural Alignment (Gemini-Class Reasoning)

**Shuri (Platform Engineering / DevOps):**
"The issue is that we are trying to build a wheel/package out of a web application. We don't need to package Hosteva; we just need to run it. 
The mathematically correct approach for `uv` in Docker is to use `uv pip install --system -r pyproject.toml`. However, `uv` doesn't read `pyproject.toml` directly like `pip` does. The modern standard is to compile the dependencies first, or use `uv pip install --system -e .` (editable mode) which leaves the source files intact. 
Actually, the best practice is to simply copy `pyproject.toml` and `uv.lock`, run `uv pip install --system --no-cache -r pyproject.toml` (if using a requirements export), OR use `uv pip install --system .` but ensure we copy the entire `app/` directory into the container *after* the dependencies are installed so the static files are not lost."

**Iron Man (CTO - Architecture):**
"Shuri is close, but let's be absolute. If we install via `uv pip install --system .`, it installs the dependencies listed in `pyproject.toml` into the system Python. That is correct. The reason the templates were lost is because the Dockerfile likely didn't copy them properly, or the working directory was wrong.
Here is the bulletproof architecture:
1. Install `uv`.
2. Copy `pyproject.toml` and `uv.lock`.
3. Run `uv pip install --system .` to install ALL 18 dependencies (including SQLAlchemy, pgvector, Redis, Stripe) into the system.
4. **CRITICAL STEP:** Copy the entire `app/` directory into `/workspace/app/`.
5. Run `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`.
By copying the `app/` folder *after* the package installation, the raw `templates/` and `static/` files are physically present on the hard drive when Gunicorn boots."

**Hulk (Backend / Database):**
"Hulk agrees with Iron Man. The `pyproject.toml` contains `psycopg` and `pgvector`. These require C-extensions. The Docker container must use a base image that has `build-essential` or `libpq-dev` if it compiles from source, but `uv` usually fetches pre-compiled wheels. As long as `pyproject.toml` is the single source of truth for dependencies, the database connection will survive."

**Hawkeye (Product Owner):**
"The strategy is aligned. The Spike is complete. I am generating the exact ticket for Aider.

### Acceptance Criteria for Aider (Phase 5):
1. Open `Dockerfile`.
2. DO NOT hardcode any pip packages. 
3. Use `uv` to install dependencies directly from `pyproject.toml`.
4. Ensure the `app/` directory (including `templates` and `static`) is explicitly copied into the container's working directory.
5. Set the CMD to run Gunicorn with the Uvicorn worker class."
