import os
import requests
from dotenv import load_dotenv

load_dotenv('/home/rdogen/OpenClaw_Factory/projects/Hosteva/.env')
api_key = os.getenv('GOOGLE_API_KEY')

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

docs = ['PIPELINE_ARCHITECTURE.md', 'V3_WORKFLOW_MASTER_ARCHITECTURE.md', 'V3_GRAPHBIT_IMPLEMENTATION_PLAN.md', 'MCP_INFRASTRUCTURE_PLAN.md', 'TOOLS.md', 'AGENTS.md']
doc_context = ""
for d in docs:
    try:
        with open(f'/home/rdogen/OpenClaw_Factory/projects/Hosteva/{d}', 'r') as f:
            doc_context += f"\n--- {d} ---\n{f.read()}\n"
    except:
        pass

reports_context = ""
agents_list = ["Vision", "Iron_Man", "Shuri", "Rocket_Raccoon", "Agent_Phil_Coulson"]
for a in agents_list:
    try:
        with open(f'/home/rdogen/OpenClaw_Factory/projects/Hosteva/{a}_report.md', 'r') as f:
            reports_context += f"\n--- {a}\'s Initial Report ---\n{f.read()}\n"
    except:
        pass

cross_review_prompt = f"""
Here are the system documentations:
{doc_context}

Here are the initial diagnostic reports from the team:
{reports_context}

Your task:
1. Review the other agents' recommendations. Confirm if you agree with them considering our current setup, infrastructure, and cost (we must use free tools).
2. Review the system documentations provided. You MUST explicitly confirm that these system documentations (workflow, skills, MCPs, etc.) are rock solid with no room for improvement.
"""

agents = {
    "Shuri": "You are Shuri. Focus on testing and R&D agreement.",
    "Rocket_Raccoon": "You are Rocket Raccoon. Focus on failsafe agreement.",
    "Agent_Phil_Coulson": "You are Phil Coulson. Focus on process agreement."
}

cross_reviews = {}
for name, sys_prompt in agents.items():
    print(f"Running cross-review for {name}...")
    res = ask_gemini(sys_prompt, cross_review_prompt)
    cross_reviews[name] = res
    with open(f'/home/rdogen/OpenClaw_Factory/projects/Hosteva/{name}_cross_review.md', 'w') as f:
        f.write(res)

print("Synthesizing consolidated path forward...")
synth_prompt = "You are the Director. Synthesize the following cross-reviews into a CONSOLIDATED_PATH_FORWARD.md. Ensure it explicitly states that the system documentations are rock solid with no room for improvement, and outlines the agreed-upon free tools and path forward.\n\n"
for name in ["Vision", "Iron_Man", "Shuri", "Rocket_Raccoon", "Agent_Phil_Coulson"]:
    try:
        with open(f'/home/rdogen/OpenClaw_Factory/projects/Hosteva/{name}_cross_review.md', 'r') as f:
            synth_prompt += f"\n--- {name}'s Cross Review ---\n{f.read()}\n"
    except:
        pass

master_res = ask_gemini("You are an executive summarizer.", synth_prompt)
with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/CONSOLIDATED_PATH_FORWARD.md', 'w') as f:
    f.write(master_res)

print("Cross Review Complete.")
