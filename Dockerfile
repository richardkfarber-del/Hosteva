# syntax=docker/dockerfile:1
FROM python:3.12-slim AS builder

# Inject uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Configure uv behavior
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build

# Copy project manifests and required files for metadata generation
COPY pyproject.toml uv.lock README.md ./
COPY app ./app

# Create virtual environment and install dependencies
RUN uv sync --no-dev

# Final runtime stage
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

RUN useradd -m -u 1000 hosteva_user

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --chown=hosteva_user:hosteva_user . /app

USER hosteva_user

CMD /opt/venv/bin/gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000}
