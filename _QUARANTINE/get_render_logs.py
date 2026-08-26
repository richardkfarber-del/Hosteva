import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get('RENDER_API_KEY')
SERVICE_ID = os.environ.get('RENDER_SERVICE_ID')

url = f"https://api.render.com/v1/services/{SERVICE_ID}/deploys"
req = urllib.request.Request(url, headers={'Accept': 'application/json', 'Authorization': f'Bearer {API_KEY}'})

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        if data:
            latest_deploy = data[0]['deploy']
            deploy_id = latest_deploy['id']
            print(f"Latest Deploy ID: {deploy_id}, Status: {latest_deploy['status']}")
            print(json.dumps(latest_deploy, indent=2))
except Exception as e:
    print(f"Error fetching deploy: {e}")