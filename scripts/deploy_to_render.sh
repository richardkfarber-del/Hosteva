#!/bin/bash
set -e

TICKET_ID=$1
if [ -z "$TICKET_ID" ]; then
    echo "Error: Ticket ID required."
    exit 1
fi

echo "--- Starting physical deployment for $TICKET_ID ---"

# Load env vars
source /home/rdogen/OpenClaw_Factory/projects/Hosteva/.env

cd /home/rdogen/OpenClaw_Factory/projects/Hosteva

# Check if there are changes to commit
if [[ `git status --porcelain` ]]; then
    git add .
    git commit -m "feat: deploy $TICKET_ID (automated swarm push)"
    git push origin main
    echo "Git push successful. Hash: $(git rev-parse HEAD)"
else
    echo "No git changes to commit. Proceeding to trigger Render..."
fi

# Trigger Render Deployment
echo "Triggering Render API for service $RENDER_SERVICE_ID..."
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys" \
     -H "Authorization: Bearer $RENDER_API_KEY" \
     -H "Accept: application/json" \
     -d '{"clearCache": "do_not_clear"}')

STATUS_CODE=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d':' -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

if [ "$STATUS_CODE" -eq 201 ] || [ "$STATUS_CODE" -eq 200 ]; then
    echo "Render webhook triggered successfully!"
    echo "Response: $BODY"
    echo "DEPLOYMENT_VERIFIED"
else
    echo "Render webhook failed with status $STATUS_CODE"
    echo "Response: $BODY"
    exit 1
fi
