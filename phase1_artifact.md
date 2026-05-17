# Ticket Summary
The Render deployment is failing because the Dockerfile is dropping static files and missing dependencies.

# Root Cause Hypothesis
The `Dockerfile` uses `uv pip install --system .` which drops `app/templates/` and `app/static/` during the build because they are not packaged by `pyproject.toml`. Hardcoded `pip install` commands also missed critical dependencies like `sqlalchemy` and `redis`.

# Spike Research & Vanguard Consensus
**Shuri (Platform Engineering):** "We don't need to package Hosteva; we just need to run it. The best practice is to copy `pyproject.toml` and `uv.lock`, run `uv pip install --system .` to install dependencies, and then copy the entire `app/` directory into the container *after* the dependencies are installed so the static files are not lost."

**Iron Man (CTO - Architecture):**
Here is the bulletproof architecture:
1. Install `uv`.
2. Copy `pyproject.toml` and `uv.lock`.
3. Run `uv pip install --system .` to install ALL dependencies into the system.
4. **CRITICAL STEP:** Copy the entire `app/` directory into `/workspace/app/`.
5. Run `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`.

# Acceptance Criteria
1. Open `Dockerfile`.
2. DO NOT hardcode any pip packages.
3. Use `uv` to install dependencies directly from `pyproject.toml`.
4. Ensure the `app/` directory (including `templates` and `static`) is explicitly copied into the container's working directory.
5. Set the CMD to run Gunicorn with the Uvicorn worker class.