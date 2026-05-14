#!/usr/bin/env python3
import json, os, sys
import sys; sys.path.append("/home/rdogen/OpenClaw_Factory/projects/Hosteva"); from gb_config import run_single_agent, local_config

print("======================================================")
print("  [PHASE 1] INTAKE")
print("======================================================")
print("-> AGENT-07-PRODUCT (Hawkeye) bound to business_analysis_skill.md")
print("-> AGENT-20-RECON (Falcon) bound to market_recon_research_skill.md")

state_path = os.environ.get("SWARM_STATE_FILE", "/home/rdogen/OpenClaw_Factory/projects/Hosteva/swarm_state.json")
try:
    with open(state_path, "r") as f:
        state = json.load(f)
except FileNotFoundError:
    state = {}

print("-> Executing GraphBit Node...")
result = run_single_agent("Intake", "Hawkeye and Falcon", "business_analysis_skill.md", local_config, state)
print("\n>>> [PHASE 1 OUTPUT]:\n", result)
print(">>> [ORCHESTRATOR]: Phase 1 Complete.")
sys.exit(0)
