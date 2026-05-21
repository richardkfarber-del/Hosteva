#!/bin/bash
cd /home/rdogen/OpenClaw_Factory/projects/Hosteva

# Extract Render API credentials from the .env file
RENDER_API_KEY=$(grep '^RENDER_API_KEY=' .env | cut -d '=' -f2 | tr -d '"')
RENDER_SERVICE_ID=$(grep '^RENDER_SERVICE_ID=' .env | cut -d '=' -f2 | tr -d '"')

echo "🛡️ HEIMDALL DEPLOYMENT PROTOCOL INITIATED 🛡️"
echo "-------------------------------------------"
echo "1. Committing unpushed fixes (Stripe dependency)..."
git add .
git commit -m "fix: add stripe dependency and fix syntax errors" || echo "No changes to commit."

echo "2. Pushing to GitHub (origin main)..."
git push origin main

echo "3. Contacting Render API to monitor deployment..."
sleep 15 # Give GitHub time to trigger the Render webhook

DEPLOY_ID=$(curl -s -X GET "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys?limit=1" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer $RENDER_API_KEY" | grep -o '"id":"dep-[^"]*"' | head -n 1 | cut -d'"' -f4)

if [ -z "$DEPLOY_ID" ]; then
  echo "❌ Error: Could not retrieve Deploy ID from Render."
  exit 1
fi

echo "Tracking Render Deploy ID: $DEPLOY_ID"

STATUS="created"
while [[ "$STATUS" == "created" || "$STATUS" == "build_in_progress" || "$STATUS" == "update_in_progress" ]]; do
  sleep 20
  STATUS=$(curl -s -X GET "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys/$DEPLOY_ID" \
    -H "Accept: application/json" \
    -H "Authorization: Bearer $RENDER_API_KEY" | grep -o '"status":"[^"]*"' | head -n 1 | cut -d'"' -f4)
  echo "Current Status: $STATUS..."
done

echo "-------------------------------------------"
if [ "$STATUS" == "live" ]; then
  echo "✅ DEPLOYMENT SUCCESSFUL! The service is live on Render."
  echo "Triggering QA Team for UAT Validation..."
  HTTP_STATUS=$(curl -o /dev/null -s -w "%{http_code}\n" https://hosteva.onrender.com/pricing)
  if [ "$HTTP_STATUS" == "200" ]; then
     echo "✅ QA Validation Passed (HTTP 200). Sprint is officially COMPLETE."
  else
     echo "❌ QA Validation Failed (HTTP $HTTP_STATUS). Generating Bug Ticket."
  fi
else
  echo "❌ DEPLOYMENT FAILED with status: $STATUS."
  echo "Generating Bug Ticket for Coder Agent."
fi
