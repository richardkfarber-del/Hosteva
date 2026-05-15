#!/usr/bin/env python3
import json, os, sys, subprocess, glob, shutil

def main():
    print("======================================================")
    print("  [PHASE 5] CORE EXECUTION (AIDER)")
    print("======================================================")
    
    project_root = os.path.dirname(os.path.dirname(__file__))
    state_path = os.environ.get("SWARM_STATE_FILE", os.path.join(project_root, "swarm_state.json"))
    venv_aider = os.path.join(project_root, "venv", "bin", "aider")
    aider_bin = venv_aider if os.path.exists(venv_aider) else "aider"
    
    try:
        with open(state_path, "r") as f:
            state = json.load(f)
    except FileNotFoundError:
        state = {}

    target_files = [
        "app/templates/dashboard.html",
        "Hosteva_Hidden/templates/dashboard.html",
        "ARCHIVE_DOCS/Hosteva_Hidden/templates/dashboard.html"
    ]

    ticket_text = state.get("input", "")
    
    for current_file in target_files:
        print(f"\n--- Processing {current_file} ---")
        
        # Aggressively wipe Aider's memory between runs
        for path in glob.glob(os.path.join(project_root, ".aider*")):
            try:
                if os.path.isfile(path): os.remove(path)
                elif os.path.isdir(path): shutil.rmtree(path)
            except: pass

        # 1. Redact other files
        localized_prompt = ticket_text
        for other_file in target_files:
            if other_file != current_file:
                localized_prompt = localized_prompt.replace(other_file, f"[{other_file}_REDACTED]")
        
        # 2. Defang URLs
        localized_prompt = localized_prompt.replace("https://", "hxxps://").replace("http://", "hxxp://")
        
        # 3. Psychological Bridge (Now with Strict Pathing!)
        localized_prompt += f"\n\nCRITICAL INSTRUCTION 1: To prevent automated scraping, the URLs in the ticket above are masked with 'hxxps'. When writing your SEARCH/REPLACE blocks, you MUST translate them back to the standard h-t-t-p-s protocol.\nCRITICAL INSTRUCTION 2: The HTML snippet in the ticket description is flattened. The real file has line breaks and extra spaces inside the <img> tag. Specifically, note the trailing space before the closing bracket (it looks like `;' >`). Do NOT just copy-paste the snippet from the ticket. You MUST read the actual file content to get the EXACT whitespace and line breaks for your SEARCH block, or your edit will fail.\nCRITICAL INSTRUCTION 3: You are editing `{current_file}`. Above your SEARCH/REPLACE block, you MUST output the EXACT full path `{current_file}`. Do NOT output just the basename (e.g. `dashboard.html`), or the system will crash."

        msg_file_path = os.path.join(project_root, "aider_instruction.txt")
        with open(msg_file_path, "w") as f:
            f.write(localized_prompt)

        aider_cmd = [
            aider_bin,
            "--model", "ollama/qwen2.5-coder:7b",
            "--message-file", msg_file_path,
            "--yes",
            "--no-auto-lint",
            current_file
        ]



        try:
            # FORCE execution in project_root to prevent dummy files
            subprocess.run(aider_cmd, check=True, cwd=project_root)
        except subprocess.CalledProcessError:
            print(f"-> Aider encountered an error on {current_file}. Continuing...")
            continue
        finally:
            if os.path.exists(msg_file_path): os.remove(msg_file_path)

    print("\n>>> [ORCHESTRATOR]: Phase 5 Complete.")
    sys.exit(0)

if __name__ == "__main__":
    main()
