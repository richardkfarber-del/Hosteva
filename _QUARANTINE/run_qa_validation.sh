#!/bin/bash
cd /home/rdogen/OpenClaw_Factory/projects/Hosteva
export PYTHONPATH=/home/rdogen/OpenClaw_Factory/projects/Hosteva
./venv/bin/pytest tests/
echo "--- HTTP RESPONSE ---"
curl -sI https://hosteva.onrender.com/pricing
