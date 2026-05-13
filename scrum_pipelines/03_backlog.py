#!/usr/bin/env python3
import json, os, sys

# Add root directory to sys.path to import the correct V3 gb_config
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import sys; sys.path.append("/home/rdogen/OpenClaw_Factory/projects/Hosteva"); from gb_config import run_single_agent, local_config
from swarm_tools import read_file, write_file, content_search, submit_phase_plan

print("======================================================")
print("  [PHASE 3] BACKLOG GROOMING")
print("======================================================")
print("-> AGENT-07-PRODUCT (Hawkeye) bound to backlog_grooming_skill.md")

state_path = os.environ.get("SWARM_STATE_FILE", "/home/rdogen/OpenClaw_Factory/projects/Hosteva/swarm_state.json")
try:
    with open(state_path, "r") as f:
        state = json.load(f)
except FileNotFoundError:
    state = {}

# Equip Hawkeye with actual function objects, not strings
allowed_tools = [read_file, write_file, content_search, submit_phase_plan]

print("-> Executing GraphBit Node...")
result = run_single_agent("hawkeye", "Hawkeye", "backlog_grooming_skill.md", local_config, state, allowed_tools)
print("\n>>> [PHASE 3 OUTPUT]:\n", result)

# Save artifact
artifact_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "03_groomed_ticket_artifact.md")
with open(artifact_path, "w") as f:
    f.write(result if result else "No output.")
print(f"-> Saved artifact to {artifact_path}")

# Update state
state["phase_3_artifact"] = "03_groomed_ticket_artifact.md"
state["current_phase"] = "04_tdd"
with open(state_path, "w") as f:
    json.dump(state, f, indent=4)
print("-> Updated swarm_state.json")

print(">>> [ORCHESTRATOR]: Phase 3 Complete.")
sys.exit(0)
