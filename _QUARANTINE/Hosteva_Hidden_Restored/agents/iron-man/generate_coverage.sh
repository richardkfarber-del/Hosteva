#!/bin/bash
# FEAT-019: Automated Test Coverage Generation (TDD Benchmark)

echo "Starting Automated Test Coverage Generation..."
source venv/bin/activate || true
pip install pytest pytest-cov httpx > /dev/null 2>&1

export PYTHONPATH=.
pytest --cov=app --cov-report=html --cov-report=term tests/
