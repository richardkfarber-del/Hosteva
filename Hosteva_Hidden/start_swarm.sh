#!/bin/bash
# --- HOSTOVA SWARM STABILITY PROTOCOL (MORNING WAKE-UP) ---

PROJECT_ROOT="/home/rdogen/OpenClaw_Factory/projects/Hosteva"
cd $PROJECT_ROOT

# 1. KILL GHOSTS: Stop all lingering background processes
echo "🛡️ Clearing the deck..."
pkill -9 -f openclaw
pkill -9 -f ollama

# 2. PATH GUARD: Ensure Fury's "Eyes" (/app/workspace) are correctly mapped
if [ ! -L "/app/workspace" ] || [ "$(readlink /app/workspace)" != "$PROJECT_ROOT" ]; then
    echo "👁️ Re-aligning workspace vision..."
    sudo mkdir -p /app
    sudo ln -sf $PROJECT_ROOT /app/workspace
fi

# 3. PLUGIN GUARD: Delete the duplicate OpenAI plugin that causes JSON leaks
rm -f /home/rdogen/OpenClaw_Factory/openclaw/extensions/openai/index.ts

# 4. IDENTITY GUARD: Force the 'main' agent to use the Nick Fury Soul
# This prevents the "Duplicate agentDir" crash permanently.
node -e '
const fs = require("fs");
const path = "./.openclaw/openclaw.json";
let config = JSON.parse(fs.readFileSync(path, "utf8"));
config.agents.list = config.agents.list.filter(a => a.id !== "nick_fury").map(agent => {
  if (agent.id === "main") {
    agent.agentDir = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/nick-fury";
    agent.workspace = "/home/rdogen/OpenClaw_Factory/projects/Hosteva";
  }
  return agent;
});
fs.writeFileSync(path, JSON.stringify(config, null, 2));
'

# 5. MEMORY PURGE: Wipe stuck conversation loops for a clean save-state
echo "🧠 Purging corrupted session cache..."
rm -rf ./.openclaw/agents/main/sessions/*
rm -f ./.openclaw/storage.sqlite

# 6. BACKEND START: Engage the Local GPU (Ollama)
echo "⚡ Engaging Local GPU (Ollama)..."
ollama serve > /dev/null 2>&1 &
sleep 5

# 7. ENGAGE HELICARRIER
echo "🚀 Swarm Online. Good morning, Secretary Farber."
./launch.sh
