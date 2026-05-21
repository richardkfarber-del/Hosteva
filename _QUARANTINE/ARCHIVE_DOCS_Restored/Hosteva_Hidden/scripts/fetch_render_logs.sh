#!/bin/bash
if [ -z "$RENDER_API_KEY" ] || [ -z "$RENDER_SERVICE_ID" ]; then
  echo "Error: RENDER_API_KEY or RENDER_SERVICE_ID environment variables are missing."
  exit 1
fi
curl -s --request GET \
     --url "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys?limit=1" \
     --header "Accept: application/json" \
     --header "Authorization: Bearer $RENDER_API_KEY" > /tmp/last_deploy.json
deploy_id=$(grep -o '"id":"[^"]*' /tmp/last_deploy.json | head -1 | cut -d'"' -f4)

if [ -z "$deploy_id" ]; then
  echo "Error: Could not find deploy ID."
  exit 1
fi

curl -s --request GET \
     --url "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys/$deploy_id" \
     --header "Accept: application/json" \
     --header "Authorization: Bearer $RENDER_API_KEY" > /tmp/deploy_status.json
status=$(grep -o '"status":"[^"]*' /tmp/deploy_status.json | head -1 | cut -d'"' -f4)

echo "Latest Deployment ($deploy_id) Status: $status"
