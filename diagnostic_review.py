import os
import requests
import json
from dotenv import load_dotenv

load_dotenv('/home/rdogen/OpenClaw_Factory/projects/Hosteva/.env')
api_key = os.getenv('GOOGLE_API_KEY')

if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env")
    exit(1)

def ask_gemini(system_prompt, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"Error: {response.status_code} - {response.text}"

files_to_read = [
    'scrum_master.py',
    'scrum_pipelines/gb_config.py',
    'scrum_pipelines/05_execution.py',
    'scrum_pipelines/rocket_failsafe.py',
    'Dockerfile',
    'pyproject.toml'
]
context = ""
for f in files_to_read:
    try:
        with open(f'/home/rdogen/OpenClaw_Factory/projects/Hosteva/{f}', 'r') as file:
            context += f"\n--- {f} ---\n{file.read()}\n"
    except Exception as e:
        pass

agents = {
    "Shuri": "You are Shuri, Head of R&D. Research testing frameworks (like Behave/Hypothesis) to prevent the swarm from hallucinating passing tests.",
    "Rocket_Raccoon": "You are Rocket Raccoon, Diagnostics Specialist. Review failsafes, strike counters, and error handling in this pipeline.",
    "Agent_Phil_Coulson": "You are Phil Coulson, Scrum Master. Review the PR review phase, context passing, and overall agile process."
}

outputs = {}
for name, sys_prompt in agents.items():
    print(f"Running {name}...")
    res = ask_gemini(sys_prompt, f"Here is the project codebase to review:\n{context}")
    outputs[name] = res
    with open(f'/home/rdogen/OpenClaw_Factory/projects/Hosteva/{name}_report.md', 'w') as f:
        f.write(res)

print("Synthesizing master report...")
synth_prompt = "You are the Director. Synthesize the following agent reports into a MASTER_DIAGNOSTIC_REPORT.md outlining actionable upgrades for Sprint 2, focusing on free tools like Claude Code CLI, Behave, etc.\n\n"
for name in ["Vision", "Iron_Man", "Shuri", "Rocket_Raccoon", "Agent_Phil_Coulson"]:
    try:
        with open(f'/home/rdogen/OpenClaw_Factory/projects/Hosteva/{name}_report.md', 'r') as f:
            synth_prompt += f"\n--- {name}'s Report ---\n{f.read()}\n"
    except:
        pass

master_res = ask_gemini("You are an executive summarizer.", synth_prompt)
with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/MASTER_DIAGNOSTIC_REPORT.md', 'w') as f:
    f.write(master_res)

print("Diagnostic Review Complete.")
