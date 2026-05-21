import os

root_env_path = '/home/rdogen/OpenClaw_Factory/.env'
project_env_path = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/.env'

api_key = None
with open(root_env_path, 'r') as f:
    for line in f:
        if line.startswith('GEMINI_API_KEY='):
            api_key = line.strip().split('=', 1)[1]
            break

if api_key:
    with open(project_env_path, 'a') as f:
        f.write(f'\nGOOGLE_API_KEY={api_key}\n')
    print('Key successfully migrated.')
else:
    print('Key not found in root .env.')
