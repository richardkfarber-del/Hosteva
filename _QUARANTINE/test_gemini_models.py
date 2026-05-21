import os
import requests
from dotenv import load_dotenv

load_dotenv('/home/rdogen/OpenClaw_Factory/projects/Hosteva/.env')
api_key = os.environ.get('GOOGLE_API_KEY', '')

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)
print([m['name'] for m in response.json().get('models', [])])
