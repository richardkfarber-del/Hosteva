import sys

path = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/app/main.py'
with open(path, 'r') as f:
    content = f.read()

content = content.replace('"google_maps_"api_key": "os.getenv"("GOOGLE_MAPS_API_KEY", "")', '"google_maps_api_key": os.environ.get("GOOGLE_MAPS_API_KEY", "")')

with open(path, 'w') as f:
    f.write(content)
