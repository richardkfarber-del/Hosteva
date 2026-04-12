#!/bin/bash
echo "🛡️ Initializing Avengers Swarm..."

export $(grep -v '^#' .env | xargs)

export OPENCLAW_HOME="/home/rdogen/OpenClaw_Factory/projects/Hosteva/.openclaw"
export OPENCLAW_DATA="/home/rdogen/OpenClaw_Factory/projects/Hosteva/.openclaw/.openclaw"
export OPENCLAW_CONFIG_PATH="$OPENCLAW_DATA/openclaw.json"
export OPENCLAW_PLUGINS_DIR="/home/rdogen/OpenClaw_Factory/openclaw/dist/extensions"

echo "🚀 Helicarrier Launching on Native Port..."

NODE_OPTIONS="--dns-result-order=ipv4first" /usr/bin/node /home/rdogen/OpenClaw_Factory/openclaw/dist/index.js gateway
