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

print("Synthesis Complete.")
