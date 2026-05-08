#!/bin/bash
ERRORS=$(tail -n 50 /home/rdogen/OpenClaw_Factory/projects/Hosteva/swarm_terminal.log /home/rdogen/OpenClaw_Factory/projects/Hosteva/daily_ledger.md 2>/dev/null | grep -iE 'halt|rocket|vram_ceiling|error|traceback')
if [ -n "$ERRORS" ]; then
    echo "⚠️ SWARM HALT/ERROR DETECTED:"
    echo "$ERRORS"
fi
