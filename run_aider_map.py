import os
import subprocess
from dotenv import load_dotenv

load_dotenv('.env')
google_key = os.getenv('GOOGLE_API_KEY')
os.environ['GEMINI_API_KEY'] = google_key

prompt = """
Please analyze the current repository structure, the Python orchestrator scripts (like scrum_master.py and the scrum_pipelines directory), and the configuration files.
Generate a comprehensive architectural map of this repository. 
Save it to a file named REPO_MAP.md in the root directory.
This map will be used by all agents going forward to understand the full project context.
"""

print("=== Running Aider Architect Mode ===")
# Run without --architect to avoid the multi-step prompt that might hang, just use direct edit
result = subprocess.run(
    ['.venv/bin/aider', '--model', 'gemini/gemini-2.5-flash', '--message', prompt, '--yes'], 
    capture_output=True, 
    text=True
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
