#!/bin/bash

cd /home/rdogen/OpenClaw_Factory/projects/Hosteva

echo "🚀 IGNITING MODULAR ASSEMBLY LINE..."

/home/rdogen/OpenClaw_Factory/projects/Hosteva/venv/bin/python event_driven_swarm.py
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo "💥 UNKNOWN CRASH in event_driven_swarm.py! Exit code: $exit_code. Halting."
    exit 1
fi

echo "✅ FULL SPRINT PIPELINE COMPLETE."
