#!/bin/bash
TARGET="/home/rdogen/OpenClaw_Factory/projects/Hosteva/Dockerfile"
echo "Verifying Dockerfile for CHORE-025..."
grep -q "FROM python:3.12-slim AS builder" "$TARGET" && echo "[OK] Builder stage found" || echo "[FAIL] Builder stage missing"
grep -q "COPY --from=ghcr.io/astral-sh/uv" "$TARGET" && echo "[OK] uv binary injection found" || echo "[FAIL] uv binary injection missing"
grep -q "ENV UV_COMPILE_BYTECODE=1" "$TARGET" && echo "[OK] UV_COMPILE_BYTECODE found" || echo "[FAIL] UV_COMPILE_BYTECODE missing"
grep -q "uv venv /opt/venv" "$TARGET" && echo "[OK] venv creation found" || echo "[FAIL] venv creation missing"
grep -q "\-\-mount=type=cache" "$TARGET" && echo "[OK] cache mounts found" || echo "[FAIL] cache mounts missing"
