import os
import requests
import concurrent.futures
from dotenv import load_dotenv

env_path = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/.env'
load_dotenv(env_path)
api_key = os.getenv('GOOGLE_API_KEY')

def read_file(path):
    try:
        with open(path, 'r') as f: return f.read()
    except:
        return ""

context = f"""
[V3 Architecture]
{read_file('/home/rdogen/OpenClaw_Factory/projects/Hosteva/V3_WORKFLOW_MASTER_ARCHITECTURE.md')}

[Scrum Master Orchestrator]
{read_file('/home/rdogen/OpenClaw_Factory/projects/Hosteva/scrum_master.py')}

[Agent 05 Execution Pipeline]
{read_file('/home/rdogen/OpenClaw_Factory/projects/Hosteva/scrum_pipelines/05_execution.py')}
"""

agents = {
    "Vision": "Review the Python and GraphBit flows, the V3 architecture documentation, and error logs provided in the context. Identify structural bugs, anti-patterns, and data-drop points. Recommend free tools or fixes.",
    "Iron Man": "Review the execution environment and tool bindings. Research adding Claude Code or similar free tools for coding tasks. Recommend specific free tools or upgrades to give agents actual coding capabilities.",
    "Shuri": "Research and recommend new capabilities, skills, or MCPs to prevent hallucinations and improve efficiency. Focus on free tools and testing frameworks.",
    "Rocket Raccoon": "Audit the strike counter and kickback loops. Recommend a fix to ensure you are only engaged after the SAME agent fails twice, and suggest diagnostic skills/MCPs you need to do your job properly.",
    "Agent Phil Coulson": "Review the PR process and Captain America's involvement. Why is he hallucinating rejections? Suggest how to ensure agents get the right context and diffs during the PR phase."
}

url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent?key={api_key}'

def fetch_agent(name, prompt):
    print(f"Engaging {name}...")
    payload = {
        "contents": [{"parts": [{"text": f"System Prompt: You are {name}.\n\nContext:\n{context}\n\nTask: {prompt}\n\nProvide your specific findings and actionable recommendations based ONLY on the provided context and your expertise. Do not hallucinate files that are not in the context."}]}],
        "generationConfig": {"temperature": 0.2}
    }
    resp = requests.post(url, json=payload)
    if resp.status_code == 200:
        text = resp.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No output')
        return f"## {name}\n{text}\n\n"
    else:
        return f"## {name}\nAPI Error: {resp.text}\n\n"

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/MASTER_DIAGNOSTIC_REPORT.md', 'w') as f:
    f.write("# MASTER DIAGNOSTIC REPORT (VERIFIED RUN)\n\n")

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(fetch_agent, name, prompt): name for name, prompt in agents.items()}
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/MASTER_DIAGNOSTIC_REPORT.md', 'a') as f:
            f.write(result)
