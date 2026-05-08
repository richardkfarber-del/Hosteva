import re

path = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/app/main.py'
with open(path, 'r') as f:
    content = f.read()

# Fix the syntax error on line 104
new_content = re.sub(r'"google_maps_"api_key": "os\.g[^)]+\("GOOGLE_MAPS_API_KEY", ""\)', '"google_maps_api_key": os.getenv("GOOGLE_MAPS_API_KEY", "")', content)

with open(path, 'w') as f:
    f.write(new_content)

print('Syntax error fixed')
