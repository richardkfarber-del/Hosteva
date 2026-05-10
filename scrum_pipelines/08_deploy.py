#!/usr/bin/env python3
import json, os, sys
from gb_config import run_single_agent, local_config

print("======================================================")
print("  [PHASE 8] DEPLOYMENT & INFRASTRUCTURE")
print("======================================================")
print("-> AGENT-27-RELEASE (Heimdall) & Rocket bound to deployment_infrastructure_skill.md")

state_path = os.environ.get("SWARM_STATE_FILE", "../swarm_state.json")
try:
    with open(state_path, "r") as f:
        state = json.load(f)
except FileNotFoundError:
    state = {}

print("-> Executing GraphBit Node...")
result = run_single_agent("Deploy", "Heimdall", "deployment_infrastructure_skill.md", local_config, state)
print("\n>>> [PHASE 8 OUTPUT]:\n", result)
print(">>> [ORCHESTRATOR]: Phase 8 Complete.")
sys.exit(0)
