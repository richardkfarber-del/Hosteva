#!/usr/bin/env python3
import json, os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import sys; sys.path.append("/home/rdogen/OpenClaw_Factory/projects/Hosteva"); from gb_config import run_single_agent, local_config
from swarm_tools import run_shell_command, read_file, content_search, submit_phase_plan

print("======================================================")
print("  [PHASE 6] LOGIC & PULL REQUEST REVIEW")
print("======================================================")
print("-> AGENT-06-LOGIC (Captain America) bound exclusively to pr_review_skill.md")

project_root = os.path.dirname(os.path.dirname(__file__))
state_path = os.environ.get("SWARM_STATE_FILE", os.path.join(project_root, "swarm_state.json"))

try:
    with open(state_path, "r") as f:
        state = json.load(f)
except FileNotFoundError:
    state = {}

allowed_tools = [run_shell_command, read_file, content_search, submit_phase_plan]

# Fix CWD so git commands work flawlessly
os.chdir(project_root)

# PR Review Directive
pr_directive = """

CRITICAL PR REVIEW DIRECTIVE:
1. You are the PR Reviewer. Do NOT try to fix the bug yourself.
2. The execution agent just finished writing the code and committed it to Git.
3. You MUST use `run_shell_command` to execute `git diff HEAD~1 HEAD` to see the exact code changes that were just made.
4. DO NOT use hallucinated absolute paths like `/app/...`. You are already in the project root.
5. Verify the changes match the Expected Behavior in the bug ticket based ONLY on the git diff.
6. Call `submit_phase_plan` to output your final approval or rejection with your notes. Do not search the codebase manually.
7. If approved, include exactly: "### 🟢 [PR APPROVED]"
8. If rejected, include exactly: "### 🔴 [PR REJECTED]" and detail the issues.
"""

state["input"] = state.get("input", "") + pr_directive

print("-> Executing GraphBit Node...")
result = run_single_agent("reviewer", "Captain America", "pr_review_skill.md", local_config, state, allowed_tools)
print("\n>>> [PHASE 6 OUTPUT]:\n", result)

if result and "[PR REJECTED]" in result:
    print("\n>>> [ORCHESTRATOR]: 🔴 PR Rejected. Routing back to Phase 1.")
    sprint_history = state.get("sprint_history", [])
    sprint_history.append(f"PR Review Phase Failed: {result.strip()}")
    state["sprint_history"] = sprint_history
    
    history_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(sprint_history)])
    state["input"] = f"SPRINT CONTEXT & NEW BUG REPORT:\n\nSprint History:\n{history_text}\n\nAction Required:\nGenerate a new Bug Ticket based on the latest failure to unblock the sprint."
    state["current_phase"] = "01_intake"
    
    with open(state_path, "w") as f:
        json.dump(state, f, indent=4)
    sys.exit(1)
else:
    # Save artifact
    artifact_path = os.path.join(project_root, "06_review_artifact.md")
    with open(artifact_path, "w") as f:
        f.write(result if result else "No output.")
    print(f"-> Saved artifact to {artifact_path}")

    # Update state
    state["phase_6_artifact"] = "06_review_artifact.md"
    state["current_phase"] = "07_security"
    with open(state_path, "w") as f:
        json.dump(state, f, indent=4)
    print("-> Updated swarm_state.json")

    print(">>> [ORCHESTRATOR]: Phase 6 Complete. PR Review passed.")
    sys.exit(0)
