<thinking>
The task requires creating an Agile ticket for updating the Dockerfile in the Hosteva project based on the technical implementation details provided in Phase 1.
</thinking>

```markdown
# User Story

## Acceptance Criteria
Given a user is building the FastAPI application using the Dockerfile,
When the Dockerfile is updated according to the specified technical implementation details,
Then the application should build successfully without dropping any static files.

# Technical Spike

## Acceptance Criteria
- The base image is set to Python 3.12-slim.
- `uv` is installed via pip.
- The working directory is set to `/workspace`.
- `pyproject.toml` and `uv.lock` are copied into the container.
- `uv pip install --system .` runs to install dependencies.
- The `app/` directory is copied into `/workspace/app/`.
- The final command is `CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:$PORT"]`.

# Bug

## Expected Behavior
The Dockerfile should be updated to build the FastAPI application correctly without dropping any static files.
```

> CURRENT_FOCUS_TARGET: Update Dockerfile for Hosteva Project