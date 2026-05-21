import os
import requests
from dotenv import load_dotenv
load_dotenv('/home/rdogen/OpenClaw_Factory/projects/Hosteva/.env')
api_key = os.getenv('GOOGLE_API_KEY')
url = f'https://generativelanguage.googleapis.com/v1beta/models?key={api_key}'
resp = requests.get(url)
for m in resp.json().get('models', []):
    if 'gemini' in m['name']:
        print(m['name'])
