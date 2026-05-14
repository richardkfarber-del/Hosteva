import sys
import os
import json
import re
import subprocess

def main():
    print("\n======================================================")
    print("  [PHASE 5] CORE EXECUTION (AIDER)")
    print("======================================================")
    
    # Resolve paths
    project_root = os.path.dirname(os.path.dirname(__file__))
    state_path = os.environ.get("SWARM_STATE_FILE", "/home/rdogen/OpenClaw_Factory/projects/Hosteva/swarm_state.json")
    venv_aider = os.path.join(project_root, "venv", "bin", "aider")
    
    # Fallback to global aider if venv aider doesn't exist
    aider_bin = venv_aider if os.path.exists(venv_aider) else "aider"

    try:
        with open(state_path, "r") as f:
            state = json.load(f)
    except FileNotFoundError:
        state = {}

    # Load Phase 3 & 4 Artifacts
    phase_3_artifact_path = os.path.join(project_root, state.get("phase_3_artifact", "03_groomed_ticket_artifact.md"))
    try:
        with open(phase_3_artifact_path, "r") as f:
            groomed_ticket = f.read()
    except FileNotFoundError:
        groomed_ticket = ""

    phase_4_artifact_path = os.path.join(project_root, state.get("phase_4_artifact", "04_qa_tests_artifact.md"))
    try:
        with open(phase_4_artifact_path, "r") as f:
            qa_tests = f.read()
    except FileNotFoundError:
        qa_tests = ""

    input_context = state.get("input", "")
    
    # Dynamically extract file path from groomed ticket
    match = re.search(r"## File to check\s+([^\n]+)", groomed_ticket)
    target_file = match.group(1).strip() if match else None

    if not target_file:
        print("[!] Error: Could not extract target file from groomed ticket.")
        sys.exit(1)
        
    print(f"-> Target file dynamically identified: {target_file}")
    print("-> AGENT-05 (Iron Man) bound to Aider CLI")
    print("-> Model locked: ollama/qwen2.5-coder:7b")
    
    prompt = f"Please fix the following issue based on the groomed ticket:\n\n{groomed_ticket}\n\nQA Test Context:\n{qa_tests}\n\nEnsure you fix the syntax error."
    
    cmd = [
        aider_bin,
        "--model", "ollama/qwen2.5-coder:7b",
        "--message", prompt,
        "--no-auto-commits",
        "--yes", # Auto-confirm prompts
        target_file
    ]
    
    print(f"-> Executing Aider...")
    try:
        # Run Aider, streaming output
        subprocess.run(cmd, check=True)
        print("\n>>> [ORCHESTRATOR]: Phase 5 Complete. Implementation executed via Aider.")
    except subprocess.CalledProcessError as e:
        print(f"\n>>> [ORCHESTRATOR]: Aider execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
