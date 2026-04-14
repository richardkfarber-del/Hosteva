# syntax=docker/dockerfile:1
FROM python:3.12-slim
WORKDIR /app/workspace/Hosteva

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt gunicorn "python-jose[cryptography]" passlib bcrypt

COPY . .
CMD gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000}