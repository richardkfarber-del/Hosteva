#!/bin/bash
export PYTHONPATH=/home/rdogen/OpenClaw_Factory/projects/Hosteva
nohup /home/rdogen/OpenClaw_Factory/projects/Hosteva/venv/bin/python /home/rdogen/OpenClaw_Factory/projects/Hosteva/trigger_heimdall.py > /home/rdogen/OpenClaw_Factory/projects/Hosteva/heimdall_bg.log 2>&1 &
echo "Heimdall process detached and running in background."
