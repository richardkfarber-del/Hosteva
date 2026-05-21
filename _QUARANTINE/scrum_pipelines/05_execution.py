#!/usr/bin/env python3
import json, os, sys, subprocess, glob, shutil

def main():
    print("======================================================")
    print("  [PHASE 5] CORE EXECUTION (AIDER)")
    print("======================================================")
    
    project_root = os.path.dirname(os.path.dirname(__file__))
    
    # Read artifacts
    ticket_path = os.path.join(project_root, "03_groomed_ticket_artifact.md")
    test_path = os.path.join(project_root, "04_qa_tests_artifact.md")
    
    ticket_text = ""
    if os.path.exists(ticket_path):
        with open(ticket_path, "r") as f:
            ticket_text = f.read()
            
    test_text = ""
    if os.path.exists(test_path):
        with open(test_path, "r") as f:
            test_text = f.read()

    if not ticket_text:
        print("Error: 03_groomed_ticket_artifact.md not found. Cannot proceed.")
        sys.exit(1)

    # Aggressively wipe Aider's memory between runs
    for path in glob.glob(os.path.join(project_root, ".aider*")):
        try:
            if os.path.isfile(path): os.remove(path)
            elif os.path.isdir(path): shutil.rmtree(path)
        except: pass

    # Combine instructions
    instruction = f"TICKET DETAILS:\n{ticket_text}\n\nTEST PLAN:\n{test_text}\n\n"
    instruction += "CRITICAL INSTRUCTION: You are the Execution Agent. Read the ticket and test plan above. Identify the correct files in the workspace, make the required changes to fulfill the Acceptance Criteria, and ensure the test plan is satisfied."

    msg_file_path = os.path.join(project_root, "aider_instruction.txt")
    with open(msg_file_path, "w") as f:
        f.write(instruction)

    venv_aider = os.path.join(project_root, "venv", "bin", "aider")
    aider_bin = venv_aider if os.path.exists(venv_aider) else "aider"

    aider_cmd = [
        aider_bin,
        "--model", "ollama/qwen2.5-coder:7b",
        "--message-file", msg_file_path,
        "--yes",
        "--no-auto-lint"
    ]

    try:
        # FORCE execution in project_root
        env = os.environ.copy()
        env["BROWSER"] = "echo"
        subprocess.run(aider_cmd, check=True, cwd=project_root, env=env)
    except subprocess.CalledProcessError:
        print(f"-> Aider encountered an error. Continuing...")
    finally:
        if os.path.exists(msg_file_path): os.remove(msg_file_path)

    print("\n>>> [ORCHESTRATOR]: Phase 5 Complete.")
    
    # Update state
    state_path = os.environ.get("SWARM_STATE_FILE", os.path.join(project_root, "swarm_state.json"))
    try:
        with open(state_path, "r") as f:
            state = json.load(f)
    except FileNotFoundError:
        state = {}
    state["phase"] = 6
    with open(state_path, "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    main()
