import os, requests
from dotenv import load_dotenv
load_dotenv('/home/rdogen/OpenClaw_Factory/projects/Hosteva/.env')
api_key = os.environ.get('RENDER_API_KEY')
headers = {'Authorization': f'Bearer {api_key}', 'Accept': 'application/json'}
url = 'https://api.render.com/v1/services/srv-d798m4chg0os73e3it70/deploys'
res = requests.get(url, headers=headers)
if res.status_code == 200:
    deploys = res.json()
    print('Latest status:', deploys[0]['deploy']['status'])
else:
    print('Error:', res.text)
