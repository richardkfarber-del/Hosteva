#!/usr/bin/env python3
import json, os, sys
import sys; sys.path.append("/home/rdogen/OpenClaw_Factory/projects/Hosteva"); from gb_config import run_single_agent, local_config

print("======================================================")
print("  [PHASE 13] CONSOLIDATION & MARKETING")
print("======================================================")
print("-> AGENT-24-MARKETING (Star-Lord) bound to marketing_campaign_synthesis_skill.md")

state_path = os.environ.get("SWARM_STATE_FILE", "/home/rdogen/OpenClaw_Factory/projects/Hosteva/swarm_state.json")
try:
    with open(state_path, "r") as f:
        state = json.load(f)
except FileNotFoundError:
    state = {}

print("-> Executing GraphBit Node...")
result = run_single_agent("Consolidation", "Star-Lord", "marketing_campaign_synthesis_skill.md", local_config, state)
print("\n>>> [PHASE 13 OUTPUT]:\n", result)
print(">>> [ORCHESTRATOR]: Phase 13 Complete.")
sys.exit(0)
