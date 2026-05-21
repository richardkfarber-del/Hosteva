#!/bin/bash
# Deterministic Hook: Run Unit Tests
echo "[HOOK] Executing unit tests..."
python -m pytest tests/ "$@"
