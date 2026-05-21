#!/bin/bash
# Pre-commit Linter Hook
set -e

echo "Initiating Swarm Code Audit (ruff)..."
python3 -m ruff check .

echo "Initiating Gherkin Linter (Third-Person Perspective Check)..."
if [ -x "./node_modules/.bin/gherkin-lint" ]; then
    # gherkin-lint automatically finds all .feature files in the project
    ./node_modules/.bin/gherkin-lint
    echo "Gherkin Linter Passed."
else
    echo "Warning: gherkin-lint not installed or not executable. Skipping."
fi

echo "Audit Complete."
