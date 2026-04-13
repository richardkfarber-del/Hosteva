#!/bin/bash
# Wrapper to allow piping to lobster
# Usage: echo "..." | ./lobster.sh
#    or: ./lobster.sh <file>

# Use exec to ensure signals and file descriptors are properly handled by the python process
exec python3 "$(dirname "$0")/lobster_interceptor.py" "$@"
