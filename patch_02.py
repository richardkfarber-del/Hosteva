import re

path = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/run_02_ticket_creation.py'
with open(path, 'r') as f:
    content = f.read()

content = re.sub(r"api_key=os\.getenv\('GOOGLE_API_KEY', ''\)", "local_config = LlmConfig.ollama('llama3.1-orchestrator')", content)
content = re.sub(r"llm_config=LlmConfig\.gemini\(api_key, model='gemini-2\.5-pro'\)", "llm_config=local_config", content)

with open(path, 'w') as f:
    f.write(content)
