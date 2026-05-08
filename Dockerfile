# syntax=docker/dockerfile:1
FROM python:3.12-slim AS builder

# Inject uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Configure uv behavior
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create virtual environment explicitly
RUN uv venv /opt/venv

# Install dependencies using cache mounts
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-install-project --no-dev && \
    find /opt/venv -name "*.so" -exec strip {} \; || true && \
    rm -rf /opt/venv/lib/python*/site-packages/numpy/core/tests || true


# Final runtime stage
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

RUN useradd -m -u 1000 hosteva_user

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --chown=hosteva_user:hosteva_user . /app

USER hosteva_user

CMD gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000}
