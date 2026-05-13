#!/usr/bin/env python3
import json, os, sys
import sys; sys.path.append("/home/rdogen/OpenClaw_Factory/projects/Hosteva"); from gb_config import run_single_agent, local_config

print("======================================================")
print("  [PHASE 12] EXECUTIVE ROUTING")
print("======================================================")
print("-> AGENT-01-DIRECTOR (Nick Fury) & Coulson bound to team_communication_skill.md")

state_path = os.environ.get("SWARM_STATE_FILE", "../swarm_state.json")
try:
    with open(state_path, "r") as f:
        state = json.load(f)
except FileNotFoundError:
    state = {}

print("-> Executing GraphBit Node...")
result = run_single_agent("Executive", "Nick Fury", "team_communication_skill.md", local_config, state)
print("\n>>> [PHASE 12 OUTPUT]:\n", result)
print(">>> [ORCHESTRATOR]: Phase 12 Complete.")
sys.exit(0)
