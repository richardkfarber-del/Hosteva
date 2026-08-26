import os
import requests
from dotenv import load_dotenv

load_dotenv('/home/rdogen/OpenClaw_Factory/projects/Hosteva/.env')
api_key = os.environ.get('GOOGLE_API_KEY', '')

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
headers = {'Content-Type': 'application/json'}
data = {"contents":[{"parts":[{"text":"Test"}]}]}

response = requests.post(url, headers=headers, json=data)
print(response.json())
