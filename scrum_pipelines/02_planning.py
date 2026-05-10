#!/usr/bin/env python3
import json, os, sys
from gb_config import run_single_agent, local_config

print("======================================================")
print("  [PHASE 2] SPRINT PLANNING & ARCHITECTURE")
print("======================================================")
print("-> AGENT-10-DATA_ARCHITECT (Vision) & Kang bound to architecture_skill.md")
print("-> AGENT-18-COMPLIANCE (She-Hulk) bound to legal_compliance_audit_skill.md")
print("-> AGENT-04-FRONTEND (Spider-Man) bound to ui_ux_specification_skill.md")

state_path = os.environ.get("SWARM_STATE_FILE", os.path.join(os.path.dirname(os.path.dirname(__file__)), "swarm_state.json"))
try:
    with open(state_path, "r") as f:
        state = json.load(f)
except FileNotFoundError:
    state = {}

print("-> Executing GraphBit Node...")
result = run_single_agent("Planning", "Vision", "architecture_skill.md", local_config, state)
print("\n>>> [PHASE 2 OUTPUT]:\n", result)
print(">>> [ORCHESTRATOR]: Phase 2 Complete.")
sys.exit(0)
