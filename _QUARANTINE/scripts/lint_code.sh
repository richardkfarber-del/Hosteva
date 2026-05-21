#!/bin/bash
# Deterministic Hook: Lint Code
echo "[HOOK] Executing code linters..."
flake8 app/ tests/ || echo "[HOOK] Linting issues detected."
