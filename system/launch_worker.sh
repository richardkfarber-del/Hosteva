#!/bin/bash
pkill -f "system/swarm_worker.py"
export REDIS_URL="redis://localhost:6379/0"
export PYTHONPATH="/home/rdogen/OpenClaw_Factory/projects/Hosteva"
export OPENCLAW_GATEWAY_TOKEN="hosteva_director_2026"
export OPENCLAW_GATEWAY_URL="http://127.0.0.1:18789/v1/chat/completions"
python3 /home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py
