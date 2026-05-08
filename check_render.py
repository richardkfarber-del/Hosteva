import os
import time
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get('RENDER_API_KEY')
SERVICE_ID = os.environ.get('RENDER_SERVICE_ID')

if not API_KEY or not SERVICE_ID:
    print("Error: RENDER_API_KEY or RENDER_SERVICE_ID missing in .env")
    exit(1)

url = f"https://api.render.com/v1/services/{SERVICE_ID}/deploys"
req = urllib.request.Request(url, headers={
    'Accept': 'application/json',
    'Authorization': f'Bearer {API_KEY}'
})

print("Waiting 15 seconds for GitHub webhook to trigger Render build...")
time.sleep(15)

print("Polling Render API for deployment status...")
for _ in range(40):
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                if data:
                    latest = data[0]['deploy']
                    status = latest['status']
                    print(f"Current Render Status: {status}")
                    if status == 'live':
                        print("Deployment successful!")
                        exit(0)
                    elif status in ['build_failed', 'update_failed', 'canceled']:
                        print(f"Deployment failed with status: {status}")
                        exit(1)
    except Exception as e:
        print(f"API polling error: {e}")
    time.sleep(30)

print("Deployment timed out.")
exit(1)
