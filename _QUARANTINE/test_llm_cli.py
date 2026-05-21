import os
import subprocess
from dotenv import load_dotenv

load_dotenv('.env')
google_key = os.getenv('GOOGLE_API_KEY')
os.environ['LLM_GEMINI_KEY'] = google_key

print("=== LLM Models ===")
result = subprocess.run(['.venv/bin/llm', 'models'], capture_output=True, text=True)
print(result.stdout)
