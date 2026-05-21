#!/usr/bin/env python3
import json, os, sys
import sys; sys.path.append("/home/rdogen/OpenClaw_Factory/projects/Hosteva"); from gb_config import run_single_agent, local_config

print("======================================================")
print("  [PHASE 11] MEMORY CONSOLIDATION")
print("======================================================")
print("-> AGENT-02-DREAMSTATE (Wanda) & Winter Soldier running consolidation.")

state_path = os.environ.get("SWARM_STATE_FILE", "/home/rdogen/OpenClaw_Factory/projects/Hosteva/swarm_state.json")
try:
    with open(state_path, "r") as f:
        state = json.load(f)
except FileNotFoundError:
    state = {}

print("-> Executing GraphBit Node...")
result = run_single_agent("Memory", "Wanda", "memory_consolidation_skill.md", local_config, state)
print("\n>>> [PHASE 11 OUTPUT]:\n", result)
print(">>> [ORCHESTRATOR]: Phase 11 Complete.")
sys.exit(0)
