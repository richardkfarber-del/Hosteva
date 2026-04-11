#!/bin/bash
LEDGER_FILE="/home/rdogen/OpenClaw_Factory/projects/Hosteva/daily_ledger.md"

if [ -z "$1" ]; then
    echo "Error: No QA report provided."
    exit 1
fi

echo -e "\n$1" >> "$LEDGER_FILE"
echo "Ledger updated successfully."