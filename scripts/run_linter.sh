#!/bin/bash
# Pre-commit Linter Hook
echo "Initiating Swarm Code Audit (ruff)..."
python3 -m ruff check .
echo "Audit Complete."
