--- ARCHITECTURE NOTES (Iron Man) ---
The Dockerfile must be rewritten exactly as defined in the Phase 1 artifact to properly build the FastAPI application without dropping the static files.

### Technical Implementation Details
1. The base image should be Python 3.12-slim.
2. Install `uv` via pip.
3. Set the working directory to `/workspace`.
4. Copy `pyproject.toml` and `uv.lock` into the container.
5. Run `uv pip install --system .` to install the dependencies.
6. Copy the `app/` directory into `/workspace/app/`.
7. The final command must be: `CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:$PORT"]`

--- DATABASE NOTES (Vision) ---
N/A - No impact on my domain

--- BACKEND NOTES (Hulk) ---
N/A - No impact on my domain

--- SECURITY NOTES (Black Panther) ---
N/A - No impact on my domain

--- FRONTEND NOTES (Wasp) ---
N/A - No impact on my domain