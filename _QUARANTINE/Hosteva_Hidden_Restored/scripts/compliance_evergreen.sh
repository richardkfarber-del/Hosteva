#!/bin/bash
# FEAT-020 Compliance Evergreen System Trigger
# This script is intended to be run by cron every Friday at 2:00 AM.
# It queues the 'update_ordinances' job into the Postgres-backed worker queue.

RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://localhost:8000/api/v1/queue/jobs" \
     -H "Content-Type: application/json" \
     -d '{"task_name": "update_ordinances", "payload": {}}')

if [ "$RESPONSE" -eq 200 ] || [ "$RESPONSE" -eq 201 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - SUCCESS: Evergreen compliance job queued (HTTP $RESPONSE)."
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: Failed to queue evergreen compliance job. HTTP status: $RESPONSE." >&2
    exit 1
fi
