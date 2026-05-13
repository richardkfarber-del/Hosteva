import os
import subprocess
from dotenv import load_dotenv

load_dotenv('.env')
google_key = os.getenv('GOOGLE_API_KEY')
os.environ['LLM_GEMINI_KEY'] = google_key

print("=== LLM Diagnostic Spike ===")
prompt = """
We are running the Hosteva project. We have a Python orchestrator (scrum_master.py) that manages a multi-agent pipeline.
Review the codebase architecture and identify any critical pathing or state-management issues. Keep it brief and focused on systemic risks.
"""
result = subprocess.run(['.venv/bin/llm', '-m', 'gemini-2.5-flash', prompt], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
