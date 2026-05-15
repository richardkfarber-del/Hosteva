#!/usr/bin/env python3
import json, os, sys

# Fix pathing so we can import gb_config
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_root)

from gb_config import run_single_agent, local_config
from swarm_tools import run_shell_command, read_file, content_search, submit_phase_plan

def main():
    print("======================================================")
    print("  [PHASE 7] SECURITY & COMPLIANCE GATES")
    print("======================================================")

    state_path = os.environ.get("SWARM_STATE_FILE", os.path.join(project_root, "swarm_state.json"))

    try:
        with open(state_path, "r") as f:
            state = json.load(f)
    except FileNotFoundError:
        state = {}

    allowed_tools = [run_shell_command, read_file, content_search, submit_phase_plan]
    
    # Fix CWD so git commands work flawlessly
    os.chdir(project_root)

    agents = [
        {"name": "Black Panther", "skill": "security_audit_skill.md", "type": "Security", "fail_flag": "### 🔴 [BREACH DETECTED]"},
        {"name": "Ultron", "skill": "security_audit_skill.md", "type": "Red Team", "fail_flag": "### 🔴 [BREACH DETECTED]"},
        {"name": "She-Hulk", "skill": "legal_compliance_audit_skill.md", "type": "Compliance", "fail_flag": "### 🔴 [COMPLIANCE VIOLATION]"}
    ]

    artifacts = []

    for agent in agents:
        print(f"\n-> Executing Gate: {agent['name']} ({agent['skill']})...")

        # ISOLATION: Give each agent a pristine copy of the state so they cannot see each other's work
        agent_state = state.copy()

        # SCORCHED EARTH DIRECTIVE
        directive = f"""

CRITICAL {agent['type'].upper()} DIRECTIVE:
1. You are auditing the code changes that were just made. 
2. You MUST use `run_shell_command` to execute `git diff HEAD~1 HEAD` to see the exact code changes.
3. DO NOT search the rest of the repository for unrelated issues. Base your audit ONLY on the git diff.
4. DO NOT hallucinate file paths (e.g., /app/workspace/... does not exist). 
5. DO NOT invent or assume file contents. If a tool fails, state that it failed.
6. Call `submit_phase_plan` to output your final decision.
"""
        agent_state["input"] = agent_state.get("input", "") + directive

        try:
            result = run_single_agent("auditor", agent["name"], agent["skill"], local_config, agent_state, allowed_tools)
        except Exception as e:
            print(f"\n[!] Agent {agent['name']} crashed: {e}")
            sys.exit(1)

        artifacts.append(f"=== {agent['name']} Audit ===\n{result}\n")

        if result and agent["fail_flag"] in result:
            print(f"\n>>> [ORCHESTRATOR]: {agent['name']} triggered a circuit breaker! Halting pipeline.")
            sys.exit(1)

    # All agents passed
    artifact_path = os.path.join(project_root, "07_security_artifact.md")
    with open(artifact_path, "w") as f:
        f.write("\n\n".join(artifacts))
    print(f"\n-> Saved artifact to {artifact_path}")

    state["phase_7_artifact"] = "07_security_artifact.md"
    state["current_phase"] = "08_deployment"
    with open(state_path, "w") as f:
        json.dump(state, f, indent=4)
    print("-> Updated swarm_state.json")

    print("\n>>> [ORCHESTRATOR]: Phase 7 Complete. All security and compliance gates passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
