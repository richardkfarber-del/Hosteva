#!/bin/bash
# Mock Email Webhook Listener (Spider-Man Automation)
QUEUE="/tmp/email_queue.json"
LOG="/home/rdogen/agents/IronMan/sent_emails.log"

if [ -f "$QUEUE" ]; then
    while IFS= read -r line; do
        if [ -n "$line" ]; then
            echo "[$(date)] SENT EMAIL Payload: $line" >> "$LOG"
        fi
    done < "$QUEUE"
    
    # Mark processed by deleting
    rm "$QUEUE"
    echo "Webhook processed emails and cleared queue."
else
    echo "No emails in queue."
fi
