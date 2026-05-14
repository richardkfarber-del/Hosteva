import sys
import os
import re
import subprocess
import glob
import shutil

def main():
    print('\n======================================================')
    print('  [PHASE 5] CORE EXECUTION (AIDER)')
    print('======================================================')
    
    project_root = '/home/rdogen/OpenClaw_Factory/projects/Hosteva'
    phase_3_artifact_path = os.path.join(project_root, '03_groomed_ticket_artifact.md')
    
    if not os.path.exists(phase_3_artifact_path):
        print(f"[!] Error: Artifact not found at {phase_3_artifact_path}")
        sys.exit(1)
        
    with open(phase_3_artifact_path, 'r') as f:
        ticket_content = f.read()
        
    # Extract target files
    target_files = re.findall(r'- (\./\S+)', ticket_content)
    if not target_files:
        print("[!] Error: Could not extract target file from groomed ticket.")
        sys.exit(1)
        
    print(f"-> Target files dynamically identified: {', '.join(target_files)}")
    print("-> AGENT-05 (Iron Man) bound to Aider CLI")
    print("-> Model locked: ollama/qwen2.5-coder:7b")

    venv_aider = os.path.join(project_root, 'venv', 'bin', 'aider')
    aider_bin = venv_aider if os.path.exists(venv_aider) else 'aider'

    for current_file in target_files:
        print(f"\n--- Processing {current_file} ---")
        
        # 1. Programmatic Memory Wipe
        for path in glob.glob(os.path.join(project_root, ".aider*")):
            try:
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
            except Exception as e:
                pass
        
        # 2. Dynamic Prompt Redaction
        localized_prompt = ticket_content
        for other_file in target_files:
            if other_file != current_file:
                localized_prompt = localized_prompt.replace(other_file, f"[{other_file}_REDACTED]")
                
        # 3. Defang URLs
        localized_prompt = localized_prompt.replace("https://", "hxxps://").replace("http://", "hxxp://")
        
        # 4. Psychological Bridge
        bridge_instruction = "\n\nCRITICAL INSTRUCTION: To prevent automated web scraping, the URLs in the ticket above have been masked with 'hxxps://'. However, the actual HTML files on your disk still contain 'https://'. When you write your SEARCH/REPLACE blocks, you MUST translate 'hxxps://' back to 'https://' so your exact-match succeeds. You are modifying only the target file specified."
        localized_prompt += bridge_instruction

        # Write localized prompt to temp file
        msg_file_path = os.path.join(project_root, "temp_aider_msg.txt")
        with open(msg_file_path, "w") as f:
            f.write(localized_prompt)

        # 5. Fault-Tolerant Loop & Absolute Pathing
        abs_file_path = os.path.join(project_root, current_file.lstrip('./'))
        
        aider_command = [
            aider_bin,
            "--model", "ollama/qwen2.5-coder:7b",
            "--edit-format", "diff",
            "--message-file", msg_file_path,
            "--yes",
            abs_file_path
        ]
        
        try:
            subprocess.run(aider_command, cwd=project_root, check=True)
        except subprocess.CalledProcessError as e:
            print(f"-> Aider encountered an error or couldn't match the search block in {current_file}. Continuing to next file...")
            continue
            
    # Cleanup temp file
    if os.path.exists(msg_file_path):
        os.remove(msg_file_path)

if __name__ == '__main__':
    main()
