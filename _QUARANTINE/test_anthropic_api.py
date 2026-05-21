import os
import requests
from dotenv import load_dotenv

load_dotenv('/home/rdogen/OpenClaw_Factory/projects/Hosteva/.env')
api_key = os.environ.get('ANTHROPIC_API_KEY', '')

url = "https://api.anthropic.com/v1/messages"
headers = {
    'x-api-key': api_key,
    'anthropic-version': '2023-06-01',
    'content-type': 'application/json'
}
data = {
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 10,
    "messages": [{"role": "user", "content": "Hi"}]
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code)
