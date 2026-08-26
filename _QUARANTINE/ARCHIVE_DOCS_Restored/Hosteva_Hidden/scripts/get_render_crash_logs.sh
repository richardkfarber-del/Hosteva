#!/bin/bash
if [ -z "$RENDER_API_KEY" ] || [ -z "$RENDER_SERVICE_ID" ]; then
  echo "Error: RENDER_API_KEY or RENDER_SERVICE_ID environment variables are missing."
  exit 1
fi
deploy_id=$(curl -s -H "Authorization: Bearer $RENDER_API_KEY" "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys?limit=1" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
curl -s -H "Authorization: Bearer $RENDER_API_KEY" "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys/$deploy_id/logs" | grep -o '"text":"[^"]*' | cut -d'"' -f4 | tail -n 40
