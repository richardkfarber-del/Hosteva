#!/usr/bin/env python3
import json, os, sys
import sys; sys.path.append("/home/rdogen/OpenClaw_Factory/projects/Hosteva"); from gb_config import run_single_agent, local_config

print("======================================================")
print("  [PHASE 9] USER ACCEPTANCE TESTING")
print("======================================================")
print("-> AGENT-04-FRONTEND (Spider-Man) & Wasp bound to ui_ux_specification_skill.md")

state_path = os.environ.get("SWARM_STATE_FILE", "../swarm_state.json")
try:
    with open(state_path, "r") as f:
        state = json.load(f)
except FileNotFoundError:
    state = {}

print("-> Executing GraphBit Node...")
result = run_single_agent("UAT", "Spider-Man", "ui_ux_specification_skill.md", local_config, state)
print("\n>>> [PHASE 9 OUTPUT]:\n", result)
print(">>> [ORCHESTRATOR]: Phase 9 Complete.")
sys.exit(0)
